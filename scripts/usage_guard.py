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
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

CLAUDE_HOME = Path.home() / ".claude"
GUARD_DIR = CLAUDE_HOME / "usage-guard"
STATE_FILE = GUARD_DIR / "state.json"
SETTINGS_FILE = CLAUDE_HOME / "settings.json"

WARN = float(os.environ.get("CLAUDE_USAGE_WARN", "80"))
STOP = float(os.environ.get("CLAUDE_USAGE_STOP", "95"))
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
# Usage reading (reuses claude_usage as a library) — ALL windows
# --------------------------------------------------------------------------- #
def read_windows(timeout: float = 8.0) -> list[dict]:
    """Return all active usage windows ``[{name, utilization, resets_at}, ...]``.

    Reads live from the browser (no copy) and falls through credential
    candidates on auth failure. Raises :class:`RuntimeError` if usage cannot be
    read (caller fails open).
    """
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
        raise RuntimeError(f"all credentials rejected ({last})")
    except cu.UsageError as exc:  # candidate resolution failed
        raise RuntimeError(str(exc)) from exc


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
    except RuntimeError as exc:
        state["read_error"] = str(exc)
    state["fetched_at"] = _now()  # don't hammer on persistent failure
    _save_state(state)
    return state


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


def classify(util: float | None) -> str:
    """Return 'ok' | 'warn' | 'stop' for a utilization value."""
    if util is None:
        return "ok"
    if util >= STOP:
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

    level = classify(max_util)

    if level == "warn":
        if _now() - state.get("notified_at", 0) > NOTIFY_EVERY:
            state["notified_at"] = _now()
            _save_state(state)
            notify("Claude usage approaching limit",
                   f"warn {WARN:.0f}% crossed — {offenders(windows, WARN)}.")
        return 0

    if level == "stop":
        if not state.get("blocked_since"):
            state["blocked_since"] = _now()
            ckpt = checkpoint(reason=f"stop: {offenders(windows, STOP)}")
            state["block_checkpoint"] = str(ckpt)
            _save_state(state)
            notify("Claude usage: STOP — budget exhausted",
                   f"stop {STOP:.0f}% crossed — {offenders(windows, STOP)}. "
                   "Blocking new tool calls. Checkpoint saved.")
        if tool_name in allow_set():
            return 0  # read-only tool: keep the session usable
        sys.stderr.write(
            f"BLOCKED by usage-guard: {offenders(windows, STOP)} (>= stop {STOP:.0f}%). "
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
    print(f"overall: {max_util:.1f}% [{classify(max_util).upper()}] worst={worst}  "
          f"(warn {WARN:.0f} / stop {STOP:.0f}, applied to every window)")
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
def main(argv: list[str] | None = None) -> int:
    """Dispatch the subcommand. Returns a process exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "status"
    if cmd == "gate":
        return gate(argv[1:])
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
    print(f"unknown command '{cmd}'. Use: status|refresh|gate|checkpoint|resume|install|uninstall",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
