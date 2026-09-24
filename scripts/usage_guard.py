#!/usr/bin/env python3
"""Pre-execution usage guard for claude.ai limit windows.

Runs as a synchronous Claude Code ``PreToolUse`` hook: before each tool call it
checks utilization across **all** limit windows the usage endpoint returns
(5-hour session, 7-day weekly, per-model weekly, etc. — read live from the
browser via ``claude_usage``) and acts on the **worst** one:

  * below WARN  -> allow silently.
  * WARN..STOP  -> allow, but notify (desktop + stderr), naming the window(s)
                   that crossed WARN and when each resets. Rate-limited.
  * >= STOP     -> BLOCK token-consuming tool calls (exit 2) and enter a
                   "safe stop": write a resume checkpoint and notify, naming the
                   window(s) over STOP. A small read-only allowlist stays
                   permitted. Set CLAUDE_USAGE_OVERRIDE=1 to bypass one run.

Note a weekly window over STOP keeps the block until that window resets (days),
not just hours — the notification/stderr say which window and when, and override
is always available.

Self-healing resume: once the worst window falls back below WARN (its window
reset), the block lifts automatically and you're notified capacity is back.

CLI:
    usage_guard.py status        # show every window + overall state
    usage_guard.py refresh       # force a fresh reading
    usage_guard.py gate          # the hook entry (reads PreToolUse JSON on stdin)
    usage_guard.py checkpoint    # snapshot in-progress/queued jobs now
    usage_guard.py resume        # clear the block, notify
    usage_guard.py install       # wire the PreToolUse hook into settings.json (GATED)
    usage_guard.py uninstall     # remove the hook from settings.json

Tunables (env vars):
    CLAUDE_USAGE_WARN     warn threshold %  applied to every window (default 80)
    CLAUDE_USAGE_STOP     stop threshold %  applied to every window (default 95)
    CLAUDE_USAGE_TTL      cache seconds     (default 60; 15 when any window >= WARN)
    CLAUDE_USAGE_OVERRIDE "1" to never block (one-run bypass)
    CLAUDE_USAGE_ALLOW    extra comma-separated tool names always allowed at STOP

Honest limits:
  * Utilization is a percentage + reset time, NOT a token count, so "will this
    job finish?" is a HEURISTIC (the threshold), not exact math.
  * A hook cannot freeze an in-flight model turn; blocking the next tool call is
    the stop mechanism. In-session Tasks/Workflows/crons are halted by the block
    and recorded in the checkpoint; durable resume of a CLOSED session is
    best-effort. Fail-open: if usage can't be read, the gate ALLOWS (warns).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import scheduler as sched  # noqa: E402  (needs _HERE on sys.path; ships alongside this file)

CLAUDE_HOME = Path.home() / ".claude"
GUARD_DIR = CLAUDE_HOME / "usage-guard"
STATE_FILE = GUARD_DIR / "state.json"
SETTINGS_FILE = CLAUDE_HOME / "settings.json"

WARN = float(os.environ.get("CLAUDE_USAGE_WARN", "80"))
STOP = float(os.environ.get("CLAUDE_USAGE_STOP", "95"))  # cold-start / fallback STOP

# Adaptive STOP buffer: learn the safety margin from observed overshoot, clamped hard.
STOP_CEIL = float(os.environ.get("CLAUDE_USAGE_STOP_CEIL", "98"))    # never gate above this
STOP_FLOOR = float(os.environ.get("CLAUDE_USAGE_STOP_FLOOR", "90"))  # never below this
OVERSHOOT_Q = float(os.environ.get("CLAUDE_USAGE_OVERSHOOT_Q", "0.95"))
STOP_SAFETY = float(os.environ.get("CLAUDE_USAGE_STOP_SAFETY", "1.0"))
OVERSHOOT_LOG = GUARD_DIR / "overshoot.jsonl"  # audit trail of learned overshoot
OVERSHOOT_LOG_MAX = 500
NOTIFY_EVERY = 600  # seconds between repeated WARN notifications

# Low-cost, read-only tools still allowed while STOPped so you can inspect and
# checkpoint without un-sticking the budget. Augment via CLAUDE_USAGE_ALLOW.
DEFAULT_ALLOW = {
    "Read", "Grep", "Glob", "TodoWrite", "TaskList", "TaskGet", "TaskOutput",
    "CronList", "BashOutput", "ExitPlanMode",
}


# --------------------------------------------------------------------------- #
# State persistence
# --------------------------------------------------------------------------- #
def _load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(state: dict) -> None:
    GUARD_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.replace(tmp, STATE_FILE)


def _now() -> float:
    return time.time()


# --------------------------------------------------------------------------- #
# Usage reading — ALL windows. Token-first (Claude Code's own OAuth credential),
# falling back to the browser-cookie reader. Env CLAUDE_USAGE_NO_TOKEN=1 skips the token path.
# --------------------------------------------------------------------------- #
def read_windows(timeout: float = 8.0) -> list[dict]:
    """Return all active usage windows ``[{name, utilization, resets_at}, ...]``.

    Prefers Claude Code's OAuth token (``~/.claude/.credentials.json`` →
    ``api.anthropic.com/api/oauth/usage``) — consistent, no browser. On an expired/absent token
    or any HTTP/network failure, falls back to the browser-cookie reader. Raises
    :class:`RuntimeError` only if *both* paths fail (caller then fails open).
    """
    token_err = None
    if os.environ.get("CLAUDE_USAGE_NO_TOKEN") != "1":
        try:
            import token_usage
            return token_usage.fetch_usage_windows(timeout)
        except Exception as exc:  # TokenUnavailable or import issue → try cookies
            token_err = exc

    import claude_usage as cu

    try:
        candidates = cu.candidate_cookies(None, "auto")
        last = None
        for _label, cookie in candidates:
            try:
                org = cu.discover_org_id(cookie, timeout)
                usage = cu.fetch_usage(cookie, org, timeout)
            except cu.UsageError as exc:
                last = exc
                if exc.auth:
                    continue
                raise RuntimeError(str(exc)) from exc
            windows = cu.extract_windows(usage)
            if not windows:
                raise RuntimeError("no usage windows in response")
            return windows
        raise RuntimeError(f"all credentials rejected ({last}); token: {token_err}")
    except cu.UsageError as exc:  # candidate resolution failed
        raise RuntimeError(f"{exc}; token: {token_err}") from exc


def _max_util(windows: list[dict]) -> tuple[float | None, str | None, str | None]:
    """Return ``(max_utilization, window_name, resets_at)`` across windows."""
    numeric = [w for w in windows if isinstance(w.get("utilization"), (int, float))]
    if not numeric:
        return None, None, None
    worst = max(numeric, key=lambda w: w["utilization"])
    return float(worst["utilization"]), worst.get("name"), worst.get("resets_at")


def refresh_state(force: bool = False) -> dict:
    """Refresh cached usage if stale (or ``force``); return the state dict."""
    state = _load_state()
    cur_max, _, _ = _max_util(state.get("windows") or [])
    ttl = float(os.environ.get("CLAUDE_USAGE_TTL", "60"))
    if cur_max is not None and cur_max >= WARN:
        ttl = min(ttl, 15.0)
    fresh = state.get("fetched_at", 0) + ttl > _now()
    if fresh and not force:
        return state

    try:
        state["windows"] = read_windows()
        state["read_error"] = None
        _record_sample(state)  # feed the burn-rate history on each fresh read
    except RuntimeError as exc:
        state["read_error"] = str(exc)
    state["fetched_at"] = _now()  # don't hammer on persistent failure
    _save_state(state)
    return state


# Keep the last N (t, worst_util) samples so the scheduler can project a burn rate.
HISTORY_MAX = 30


def _record_sample(state: dict) -> None:
    """Append a ``(t, worst_util)`` sample; log any upward jump for the overshoot audit."""
    worst, _, _ = _max_util(state.get("windows") or [])
    if worst is None:
        return
    hist = state.get("history") or []
    prev = hist[-1]["util"] if hist else None
    hist.append({"t": _now(), "util": float(worst)})
    state["history"] = hist[-HISTORY_MAX:]
    if prev is not None and worst > prev:
        _log_overshoot(float(prev), float(worst), effective_stop(state))


def _history_samples(state: dict) -> list["sched.Sample"]:
    """The stored history as scheduler ``Sample`` objects (oldest→newest)."""
    out = []
    for h in state.get("history") or []:
        try:
            out.append(sched.Sample(float(h["t"]), float(h["util"])))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def effective_stop(state: dict) -> float:
    """The **adaptive** STOP threshold: ``100 - overshoot_q - safety``, clamped to
    ``[STOP_FLOOR, STOP_CEIL]``; the fixed ``STOP`` on cold start. Learns the buffer from the
    observed per-read overshoot but can never exceed the hard ceiling."""
    ov = sched.quantile(sched.overshoot_deltas(_history_samples(state)), OVERSHOOT_Q)
    return sched.adaptive_stop(ov, ceiling=STOP_CEIL, floor=STOP_FLOOR,
                               safety=STOP_SAFETY, default=STOP)


def _log_overshoot(from_util: float, to_util: float, eff_stop: float) -> None:
    """Append one overshoot observation to the bounded JSONL audit log (best-effort)."""
    rec = {
        "t": datetime.now().astimezone().isoformat(timespec="seconds"),
        "from": round(from_util, 2), "to": round(to_util, 2),
        "delta": round(to_util - from_util, 2), "eff_stop": round(eff_stop, 2),
        "crossed_stop": to_util >= eff_stop,
    }
    try:
        GUARD_DIR.mkdir(parents=True, exist_ok=True)
        old = OVERSHOOT_LOG.read_text(encoding="utf-8").splitlines() if OVERSHOOT_LOG.exists() else []
        lines = old[-(OVERSHOOT_LOG_MAX - 1):] + [json.dumps(rec)]
        OVERSHOOT_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _when(resets_at: str | None) -> str:
    """Human local time for a reset timestamp."""
    dt = _parse_iso(resets_at)
    return dt.astimezone().strftime("%b %d %H:%M") if dt else "?"


def offenders(windows: list[dict], threshold: float) -> str:
    """Summarize windows at/above ``threshold`` as 'name pct% (resets when)'."""
    parts = []
    for w in sorted(windows, key=lambda w: -(w.get("utilization") or 0)):
        u = w.get("utilization")
        if isinstance(u, (int, float)) and u >= threshold:
            parts.append(f"{w['name']} {u:.0f}% (resets {_when(w.get('resets_at'))})")
    return "; ".join(parts)


def notify(title: str, body: str) -> None:
    """Best-effort desktop notification; always also prints to stderr."""
    print(f"[usage-guard] {title}: {body}", file=sys.stderr)
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", title, body], timeout=5,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (OSError, subprocess.SubprocessError):
            pass


def classify(util: float | None, stop: float | None = None) -> str:
    """Return 'ok' | 'warn' | 'stop' for a utilization value against ``stop`` (default fixed STOP)."""
    if util is None:
        return "ok"
    s = STOP if stop is None else stop
    if util >= s:
        return "stop"
    if util >= WARN:
        return "warn"
    return "ok"


def allow_set() -> set[str]:
    extra = os.environ.get("CLAUDE_USAGE_ALLOW", "")
    return DEFAULT_ALLOW | {t.strip() for t in extra.split(",") if t.strip()}


# --------------------------------------------------------------------------- #
# Job checkpoint (best-effort snapshot of on-disk job state)
# --------------------------------------------------------------------------- #
def checkpoint(reason: str = "manual") -> Path:
    """Snapshot known on-disk jobs + the full window readout for resume."""
    GUARD_DIR.mkdir(parents=True, exist_ok=True)
    state = _load_state()
    snap = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "reason": reason,
        "windows": state.get("windows") or [],
        "tasks": [], "jobs": [], "workflows": [],
        "note": "In-session crons (CronList) and live Workflow runs must be "
                "captured by the agent; on-disk state recorded below.",
    }
    tasks_dir = CLAUDE_HOME / "tasks"
    if tasks_dir.is_dir():
        for d in sorted(tasks_dir.iterdir()):
            if d.is_dir():
                snap["tasks"].append({
                    "id": d.name,
                    "locked": (d / ".lock").exists(),
                    "mtime": datetime.fromtimestamp(d.stat().st_mtime).isoformat(timespec="seconds"),
                })
    jobs_dir = CLAUDE_HOME / "jobs"
    if jobs_dir.is_dir():
        snap["jobs"] = sorted(d.name for d in jobs_dir.iterdir() if d.is_dir())
    wf_dir = CLAUDE_HOME / "workflows"
    if wf_dir.is_dir():
        snap["workflows"] = sorted(p.name for p in wf_dir.glob("*.js"))

    path = GUARD_DIR / f"checkpoint-{int(_now())}.json"
    path.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    (GUARD_DIR / "checkpoint-latest.json").write_text(json.dumps(snap, indent=2), encoding="utf-8")
    return path


def resume(triggered_by: str = "manual") -> None:
    """Lift the block and notify that capacity is back."""
    state = _load_state()
    was_blocked = bool(state.get("blocked_since"))
    state["blocked_since"] = None
    state["block_checkpoint"] = None
    _save_state(state)
    if was_blocked or triggered_by != "manual":
        notify("Claude usage: capacity restored",
               "A limit window reset below the warn level. Block lifted; "
               "paused work can resume.")


# --------------------------------------------------------------------------- #
# Budget-aware landing + resume (see DESIGN.md, scheduler.py)
# --------------------------------------------------------------------------- #
WORK_DIR = GUARD_DIR / "work"             # session-declared work markers
LEDGER_FILE = GUARD_DIR / "ledger.json"   # shared land/resume ledger (Q4: per-session + ledger)
WORK_TTL = 900.0                          # a declared estimate older than this is ignored


def session_id() -> str:
    """A stable key for the current session: env override, else the tmux pane, else ppid."""
    for var in ("CLAUDE_SESSION_ID", "CLAUDE_SESSION", "CJ_NAME"):
        v = os.environ.get(var)
        if v:
            return v
    pane = os.environ.get("TMUX_PANE")
    return pane.lstrip("%") if pane else f"pid-{os.getppid()}"


def tmux_target() -> str | None:
    """The tmux pane to resume into (this session's pane), or None if not in tmux."""
    return os.environ.get("TMUX_PANE")


def read_work_marker(session: str) -> dict | None:
    """A session's declared work estimate, if fresh: ``{remaining_est_min?, safe_to_land?, updated_at}``."""
    try:
        m = json.loads((WORK_DIR / f"{session}.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if _now() - float(m.get("updated_at", 0)) > WORK_TTL:
        return None
    return m


def declared_eta_seconds(marker: dict | None) -> float | None:
    """Remaining-work seconds from a marker (``remaining_est_min`` → s), or None."""
    if not marker:
        return None
    mins = marker.get("remaining_est_min")
    return float(mins) * 60.0 if isinstance(mins, (int, float)) else None


def _ledger() -> dict:
    try:
        return json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_ledger(led: dict) -> None:
    GUARD_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_FILE.write_text(json.dumps(led, indent=2), encoding="utf-8")


def schedule_resume(slot_epoch: float, target: str | None, session: str) -> bool:
    """Schedule ``claude --continue`` in ``target`` at ``slot_epoch``.

    Prefers ``at``; falls back to a transient ``systemd-run --user`` timer (no sudo / atd).
    Returns True if a job was submitted.
    """
    if not target:
        return False
    resume_argv = sched.resume_command(target)
    if shutil.which("at"):
        script = " ".join(shlex.quote(a) for a in resume_argv) + "\n"
        try:
            subprocess.run(sched.at_schedule_argv(slot_epoch), input=script, text=True, timeout=10,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except (OSError, subprocess.SubprocessError):
            pass
    if shutil.which("systemd-run"):
        argv = sched.systemd_run_argv(slot_epoch, sched.unit_name(session), resume_argv)
        try:
            subprocess.run(argv, timeout=10, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=True)
            return True
        except (OSError, subprocess.SubprocessError):
            pass
    return False


def land(session: str, worst_resets: str | None, reason: str) -> str:
    """Bring work to a safe landing slot: checkpoint, schedule the resume, record the ledger."""
    ckpt = checkpoint(reason=f"land: {reason}")
    reset_dt = _parse_iso(worst_resets)
    slot = sched.resume_epoch(reset_dt.timestamp()) if reset_dt else None
    target = tmux_target()
    scheduled = slot is not None and schedule_resume(slot, target, session)
    led = _ledger()
    led[session] = {
        "landed_at": _now(), "reason": reason, "checkpoint": str(ckpt),
        "resume_slot": slot, "scheduled": scheduled, "target": target,
    }
    _write_ledger(led)
    when = _when(worst_resets)
    msg = ("LANDING (budget): " + reason + ". Checkpointed; "
           + (f"resume scheduled ~{when} +60s." if scheduled
              else f"resume NOT auto-scheduled (need tmux + `at`); worst resets ~{when}."))
    notify("Claude usage: landing before the cap", msg)
    return msg


# --------------------------------------------------------------------------- #
# The gate (PreToolUse hook entry)
# --------------------------------------------------------------------------- #
def gate(argv: list[str]) -> int:
    """PreToolUse entry. Reads the hook JSON on stdin; returns 0 allow / 2 block."""
    tool_name = ""
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        if raw:
            tool_name = str(json.loads(raw).get("tool_name", ""))
    except (json.JSONDecodeError, ValueError):
        pass

    if os.environ.get("CLAUDE_USAGE_OVERRIDE") == "1":
        return 0

    state = refresh_state()
    windows = state.get("windows") or []
    max_util, worst_name, worst_resets = _max_util(windows)
    eff = effective_stop(state)  # adaptive STOP (learned overshoot buffer, hard-capped)

    # Self-heal: worst window fell back below WARN -> clear any block.
    if state.get("blocked_since") and (max_util is None or max_util < WARN):
        resume(triggered_by="self-heal")
        state = _load_state()

    # Fail open: no reading at all -> allow but warn once.
    if max_util is None:
        if state.get("read_error") and _now() - state.get("warn_no_read_at", 0) > NOTIFY_EVERY:
            state["warn_no_read_at"] = _now()
            _save_state(state)
            notify("Claude usage: check unavailable",
                   f"Could not read usage ({state['read_error']}); not gating.")
        return 0

    level = classify(max_util, eff)

    if level == "warn":
        # Budget-aware landing: project the burn and ask whether the pending work fits before
        # STOP. If not, land NOW (before the wall) + schedule a resume past the reset; else warn
        # and continue. Read-only tools always pass so the session can checkpoint while landed.
        session = session_id()
        if state.get("blocked_since"):
            verdict = "land"  # already landed this window; stay landed until it resets
        else:
            burn = sched.burn_rate(_history_samples(state))
            headroom = sched.seconds_to_stop(max_util, burn, eff)
            eta = declared_eta_seconds(read_work_marker(session))
            verdict = sched.decide(headroom, eta)

        if verdict == "land":
            if not state.get("blocked_since"):
                state["blocked_since"] = _now()
                land(session, worst_resets, f"warn {max_util:.0f}%")
                state["block_checkpoint"] = _ledger().get(session, {}).get("checkpoint")
                _save_state(state)
            if tool_name in allow_set():
                return 0  # read-only tool: keep the session usable while landed
            sys.stderr.write(
                f"LANDED by usage-guard (budget): worst {worst_name} {max_util:.0f}% — projected "
                f"to exceed STOP before the pending work finishes. Checkpointed; resume scheduled "
                f"past the reset (~{_when(worst_resets)} +60s). To proceed anyway, "
                f"CLAUDE_USAGE_OVERRIDE=1.\n"
            )
            return 2

        # Work still fits — warn (rate-limited) and continue.
        if _now() - state.get("notified_at", 0) > NOTIFY_EVERY:
            state["notified_at"] = _now()
            _save_state(state)
            notify("Claude usage approaching limit",
                   f"warn {WARN:.0f}% crossed — {offenders(windows, WARN)}; work still fits.")
        return 0

    if level == "stop":
        if not state.get("blocked_since"):
            state["blocked_since"] = _now()
            ckpt = checkpoint(reason=f"stop: {offenders(windows, eff)}")
            state["block_checkpoint"] = str(ckpt)
            _save_state(state)
            notify("Claude usage: STOP — budget exhausted",
                   f"stop {eff:.0f}% crossed — {offenders(windows, eff)}. "
                   "Blocking new tool calls. Checkpoint saved.")
        if tool_name in allow_set():
            return 0  # read-only tool: keep the session usable
        sys.stderr.write(
            f"BLOCKED by usage-guard: {offenders(windows, eff)} (>= adaptive stop {eff:.0f}%). "
            f"The block self-clears when the worst window ({worst_name}) resets "
            f"~{_when(worst_resets)}. Checkpoint: {state.get('block_checkpoint')}. "
            f"To proceed anyway, re-run with CLAUDE_USAGE_OVERRIDE=1.\n"
        )
        return 2

    return 0


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #
def _bar(pct: float, width: int = 20) -> str:
    pct = max(0.0, min(100.0, float(pct)))
    filled = int(round(pct / 100 * width))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def cmd_status() -> int:
    """Print every usage window and the overall guard state."""
    state = refresh_state(force=True)
    windows = state.get("windows") or []
    if not windows:
        print(f"usage-guard: no reading ({state.get('read_error')})")
        return 1
    max_util, worst, _ = _max_util(windows)
    eff = effective_stop(state)
    ov = sched.quantile(sched.overshoot_deltas(_history_samples(state)), OVERSHOOT_Q)
    ov_txt = f"{ov:.1f}%" if ov is not None else "n/a (cold)"
    print(f"overall: {max_util:.1f}% [{classify(max_util, eff).upper()}] worst={worst}  "
          f"(warn {WARN:.0f} / stop {eff:.1f} adaptive [{STOP_FLOOR:.0f}–{STOP_CEIL:.0f}], "
          f"applied to every window)")
    print(f"  adaptive-stop: {eff:.1f}%  (overshoot p{OVERSHOOT_Q*100:.0f}={ov_txt}, "
          f"safety {STOP_SAFETY:.1f}; audit {OVERSHOOT_LOG})")
    name_w = max(len(w["name"]) for w in windows)
    for w in sorted(windows, key=lambda w: -(w.get("utilization") or 0)):
        u = w.get("utilization")
        lvl = classify(u).upper() if isinstance(u, (int, float)) else "—"
        pct = float(u) if isinstance(u, (int, float)) else 0.0
        print(f"  {w['name']:<{name_w}}  {_bar(pct)} {pct:5.1f}%  [{lvl:<4}]  "
              f"resets {_when(w.get('resets_at'))}")
    if state.get("blocked_since"):
        since = datetime.fromtimestamp(state["blocked_since"]).strftime("%H:%M:%S")
        print(f"  BLOCKED since {since}; checkpoint {state.get('block_checkpoint')}")
    return 0


# --------------------------------------------------------------------------- #
# install / uninstall (settings.json wiring) -- GATED activation
# --------------------------------------------------------------------------- #
HOOK_TAG = "usage_guard.py gate"


def _hook_command() -> str:
    return f"{sys.executable} {(_HERE / 'usage_guard.py')} gate"


def cmd_install() -> int:
    """Wire the synchronous PreToolUse gate into ~/.claude/settings.json."""
    settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8")) if SETTINGS_FILE.exists() else {}
    hooks = settings.setdefault("hooks", {})
    pre = hooks.setdefault("PreToolUse", [])
    if any(HOOK_TAG in h.get("command", "")
           for entry in pre for h in entry.get("hooks", [])):
        print("usage-guard PreToolUse hook already installed.")
        return 0
    backup = SETTINGS_FILE.with_suffix(".json.usage-guard-bak")
    if SETTINGS_FILE.exists():
        shutil.copy2(SETTINGS_FILE, backup)
    pre.append({
        "matcher": "*",
        "hooks": [{"type": "command", "command": _hook_command(),
                   "async": False, "timeout": 15}],
    })
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    print(f"installed synchronous PreToolUse gate (backup: {backup}).\n"
          "Start a new Claude Code session (or /resume) for it to take effect.")
    return 0


def cmd_uninstall() -> int:
    """Remove the usage-guard PreToolUse hook from settings.json."""
    if not SETTINGS_FILE.exists():
        print("no settings.json.")
        return 0
    settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    pre = settings.get("hooks", {}).get("PreToolUse", [])
    kept = [e for e in pre
            if not any(HOOK_TAG in h.get("command", "") for h in e.get("hooks", []))]
    settings.setdefault("hooks", {})["PreToolUse"] = kept
    if not kept:
        settings["hooks"].pop("PreToolUse", None)
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    print("removed usage-guard PreToolUse hook.")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def cmd_declare(argv: list[str]) -> int:
    """Declare this session's remaining work so the fit-decision can use it (Q1 hybrid).

    Usage: ``declare <remaining_minutes> [--unsafe]``. Writes a fresh work marker for this
    session; ``--unsafe`` flags that it is NOT at a safe landing slot right now.
    """
    if not argv:
        print("usage: declare <remaining_minutes> [--unsafe]", file=sys.stderr)
        return 1
    try:
        mins = float(argv[0])
    except ValueError:
        print("remaining_minutes must be a number", file=sys.stderr)
        return 1
    safe = "--unsafe" not in argv
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    session = session_id()
    (WORK_DIR / f"{session}.json").write_text(
        json.dumps({"remaining_est_min": mins, "safe_to_land": safe, "updated_at": _now()}, indent=2),
        encoding="utf-8",
    )
    print(f"declared: session={session} remaining={mins:.0f}min safe_to_land={safe}")
    return 0


def cmd_statusline() -> int:
    """Cached-only status-line segment styled like the other addons: ``[GUARD] <detail>``.

    Renders on every status update, so it is **cached-only** (no network). Shows the two main
    windows (5h / 7d) color-coded by level, plus the adaptive STOP; or a LANDED state with the
    resume time. Reads the guard's cached state (kept fresh by the gate during activity).
    """
    # Tweakables (env): tag text/color, which windows to show (label:name,…), show the stop.
    tag_txt = os.environ.get("CLAUDE_USAGE_SL_TAG", "GUARD")
    tag_color = os.environ.get("CLAUDE_USAGE_SL_TAG_COLOR", "45")  # 256-color; matches [CAVEMAN] style
    win_spec = os.environ.get("CLAUDE_USAGE_SL_WINDOWS", "5h:five_hour,7d:seven_day")
    show_stop = os.environ.get("CLAUDE_USAGE_SL_SHOW_STOP", "1") != "0"
    tag = f"\033[1;38;5;{tag_color}m[{tag_txt}]\033[0m"

    state = _load_state()
    windows = state.get("windows") or []
    if not windows:
        sys.stdout.write(f"{tag} \033[2musage ?\033[0m")
        return 0
    eff = effective_stop(state)
    lvl_color = {"ok": "32", "warn": "33", "stop": "31"}  # green / yellow / red

    if state.get("blocked_since"):
        _, _, resets = _max_util(windows)
        sys.stdout.write(f"{tag} \033[31mLANDED\033[0m \033[2m↺ resume {_when(resets)}\033[0m")
        return 0

    by = {w.get("name"): w for w in windows}

    def seg(label: str, name: str) -> str | None:
        w = by.get(name)
        u = w.get("utilization") if w else None
        if not isinstance(u, (int, float)):
            return None
        return f"{label} \033[{lvl_color[classify(u, eff)]}m{u:.0f}%\033[0m"

    parts = []
    for spec in win_spec.split(","):
        label, _, name = spec.partition(":")
        s = seg(label.strip() or (name or spec).strip(), (name or label).strip())
        if s:
            parts.append(s)
    if not parts:  # unknown window names → fall back to the worst window
        mu, _, _ = _max_util(windows)
        parts = [f"\033[{lvl_color[classify(mu, eff)]}m{mu:.0f}%\033[0m"]
    if show_stop:
        parts.append(f"\033[2mstop {eff:.0f}%\033[0m")
    sys.stdout.write(f"{tag} " + " \033[2m·\033[0m ".join(parts))
    return 0


def cmd_ledger() -> int:
    """Print the shared land/resume ledger (which sessions landed + their resume slots)."""
    led = _ledger()
    if not led:
        print("ledger empty (no sessions landed).")
        return 0
    for sid, e in led.items():
        slot = e.get("resume_slot")
        when = (datetime.fromtimestamp(slot).astimezone().strftime("%b %d %H:%M")
                if isinstance(slot, (int, float)) else "?")
        print(f"{sid}: reason={e.get('reason')} scheduled={e.get('scheduled')} resume~{when} "
              f"ckpt={e.get('checkpoint')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Dispatch the subcommand. Returns a process exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "status"
    if cmd == "gate":
        return gate(argv[1:])
    if cmd == "declare":
        return cmd_declare(argv[1:])
    if cmd == "ledger":
        return cmd_ledger()
    if cmd == "statusline":
        return cmd_statusline()
    if cmd == "status":
        return cmd_status()
    if cmd == "refresh":
        refresh_state(force=True)
        return cmd_status()
    if cmd == "checkpoint":
        print(f"checkpoint written: {checkpoint(reason='manual')}")
        return 0
    if cmd == "resume":
        resume()
        return 0
    if cmd == "install":
        return cmd_install()
    if cmd == "uninstall":
        return cmd_uninstall()
    print("unknown command '" + cmd + "'. Use: "
          "status|refresh|gate|declare|ledger|statusline|checkpoint|resume|install|uninstall",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
