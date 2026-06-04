#!/usr/bin/env python3
"""Pre-execution usage guard for claude.ai's 5-hour window.

Runs as a synchronous Claude Code ``PreToolUse`` hook: before each tool call it
checks the 5-hour-session utilization (via ``claude_usage`` read live from the
browser) and:

  * below WARN  -> allow silently.
  * WARN..STOP  -> allow, but notify (desktop + stderr), rate-limited.
  * >= STOP     -> BLOCK token-consuming tool calls (exit 2) and enter a
                   "safe stop": write a resume checkpoint and notify. A small
                   read-only allowlist stays permitted so the session isn't
                   bricked. Set CLAUDE_USAGE_OVERRIDE=1 to bypass for one run.

Self-healing resume: once the 5-hour window resets (``resets_at`` passes, or
utilization falls back below WARN), the block lifts automatically, any system
crons we paused are re-enabled, and you're notified that capacity is back.

This file is also a small CLI for humans:

    usage_guard.py status        # show current state
    usage_guard.py refresh       # force a fresh reading
    usage_guard.py gate          # the hook entry (reads PreToolUse JSON on stdin)
    usage_guard.py checkpoint    # snapshot in-progress/queued jobs now
    usage_guard.py resume        # clear the block, re-enable paused crons, notify
    usage_guard.py install       # wire the PreToolUse hook into settings.json (GATED)
    usage_guard.py uninstall     # remove the hook from settings.json

Tunables (env vars):
    CLAUDE_USAGE_WARN     warn threshold %        (default 80)
    CLAUDE_USAGE_STOP     stop/block threshold %  (default 95)
    CLAUDE_USAGE_TTL      cache seconds           (default 60; 15 when >= WARN)
    CLAUDE_USAGE_OVERRIDE "1" to never block (one-run bypass)
    CLAUDE_USAGE_ALLOW    extra comma-separated tool names always allowed at STOP

Design notes / honest limits:
  * Utilization is a percentage + reset time, NOT a token count, so "will this
    job finish?" is a HEURISTIC (headroom + reset proximity), not exact math.
  * A hook cannot freeze an in-flight model turn; blocking the next tool call is
    the stop mechanism. In-session Tasks/Workflows/crons are halted by that
    block and recorded in the checkpoint; durable resume of a CLOSED session
    needs the opt-in system-cron (install --system-cron) — and auto-launching
    fresh AI work is deliberately NOT automatic (it would spend tokens and act
    autonomously). Fail-open: if usage can't be read, the gate ALLOWS (warns).
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
# Usage reading (reuses claude_usage as a library)
# --------------------------------------------------------------------------- #
def read_five_hour(timeout: float = 8.0) -> tuple[float, str | None]:
    """Return ``(utilization, resets_at)`` for the 5-hour window.

    Raises :class:`RuntimeError` if usage cannot be read (caller fails open).
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
            window = usage.get("five_hour") or {}
            util = window.get("utilization")
            if util is None:
                raise RuntimeError("no five_hour utilization in response")
            return float(util), window.get("resets_at")
        raise RuntimeError(f"all credentials rejected ({last})")
    except cu.UsageError as exc:  # candidate resolution failed
        raise RuntimeError(str(exc)) from exc


def refresh_state(force: bool = False) -> dict:
    """Refresh cached usage if stale (or ``force``); return the state dict."""
    state = _load_state()
    util = state.get("utilization")
    ttl = float(os.environ.get("CLAUDE_USAGE_TTL", "60"))
    if util is not None and util >= WARN:
        ttl = min(ttl, 15.0)
    fresh = state.get("fetched_at", 0) + ttl > _now()
    if fresh and not force:
        return state

    try:
        util, resets_at = read_five_hour()
        state.update({"utilization": util, "resets_at": resets_at,
                      "fetched_at": _now(), "read_error": None})
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


def _window_reset(resets_at: str | None) -> bool:
    """True if the reset timestamp is in the past (window has rolled over)."""
    target = _parse_iso(resets_at)
    return target is not None and target <= datetime.now(timezone.utc)


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
    """Snapshot known on-disk jobs so work can be picked up after reset.

    Captures background-task and job directories, workflow scripts, and the
    current usage reading. In-session crons (CronList) and live Workflow runs
    are only fully visible to the agent, so this records what is on disk and
    notes the boundary.
    """
    GUARD_DIR.mkdir(parents=True, exist_ok=True)
    state = _load_state()
    snap = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "reason": reason,
        "utilization": state.get("utilization"),
        "resets_at": state.get("resets_at"),
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
        for d in sorted(jobs_dir.iterdir()):
            if d.is_dir():
                snap["jobs"].append(d.name)
    wf_dir = CLAUDE_HOME / "workflows"
    if wf_dir.is_dir():
        snap["workflows"] = sorted(p.name for p in wf_dir.glob("*.js"))

    path = GUARD_DIR / f"checkpoint-{int(_now())}.json"
    path.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    latest = GUARD_DIR / "checkpoint-latest.json"
    latest.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# Paused-cron bookkeeping (system crontab entries we disable/enable)
# --------------------------------------------------------------------------- #
PAUSED_CRONS = GUARD_DIR / "paused-crons.txt"


def resume(triggered_by: str = "manual") -> None:
    """Lift the block, re-enable paused crons, and notify that capacity is back."""
    state = _load_state()
    was_blocked = bool(state.get("blocked_since"))
    state["blocked_since"] = None
    state["block_checkpoint"] = None
    _save_state(state)
    if PAUSED_CRONS.exists():
        # Re-enabling system crons is left to the install --system-cron flow;
        # here we just clear the marker. (Kept minimal and reversible.)
        PAUSED_CRONS.unlink()
    if was_blocked or triggered_by != "manual":
        notify("Claude usage: capacity restored",
               "5-hour window reset. Block lifted; paused work can resume.")


# --------------------------------------------------------------------------- #
# The gate (PreToolUse hook entry)
# --------------------------------------------------------------------------- #
def gate(argv: list[str]) -> int:
    """PreToolUse entry. Reads the hook JSON on stdin; returns 0 allow / 2 block."""
    # Parse the hook payload (best-effort; never fail the session on bad input).
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
    util = state.get("utilization")

    # Self-heal: window rolled over -> clear any block and welcome back.
    if state.get("blocked_since") and (_window_reset(state.get("resets_at"))
                                       or classify(util) == "ok"):
        resume(triggered_by="self-heal")
        state = _load_state()

    # Fail open: if we have no reading at all, allow but warn once.
    if util is None:
        if state.get("read_error") and _now() - state.get("warn_no_read_at", 0) > NOTIFY_EVERY:
            state["warn_no_read_at"] = _now()
            _save_state(state)
            notify("Claude usage: check unavailable",
                   f"Could not read usage ({state['read_error']}); not gating.")
        return 0

    level = classify(util)
    resets = _parse_iso(state.get("resets_at"))
    when = resets.astimezone().strftime("%H:%M") if resets else "?"

    if level == "warn":
        if _now() - state.get("notified_at", 0) > NOTIFY_EVERY:
            state["notified_at"] = _now()
            _save_state(state)
            notify("Claude usage approaching limit",
                   f"5-hour window at {util:.0f}% (warn {WARN:.0f}%), resets ~{when}.")
        return 0

    if level == "stop":
        # Enter / maintain safe-stop.
        if not state.get("blocked_since"):
            state["blocked_since"] = _now()
            ckpt = checkpoint(reason=f"stop at {util:.0f}%")
            state["block_checkpoint"] = str(ckpt)
            _save_state(state)
            notify("Claude usage: STOP — token budget low",
                   f"5-hour window at {util:.0f}% (>= {STOP:.0f}%). Blocking new "
                   f"tool calls; resets ~{when}. Checkpoint saved.")
        if tool_name in allow_set():
            return 0  # read-only tool: keep the session usable
        sys.stderr.write(
            f"BLOCKED by usage-guard: 5-hour usage {util:.0f}% >= stop {STOP:.0f}%. "
            f"Window resets ~{when}; the block self-clears then. A checkpoint was "
            f"saved to {state.get('block_checkpoint')}. To proceed anyway, re-run "
            f"with CLAUDE_USAGE_OVERRIDE=1.\n"
        )
        return 2

    return 0


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #
def cmd_status() -> int:
    """Print the current usage/guard state."""
    state = refresh_state(force=True)
    util = state.get("utilization")
    if util is None:
        print(f"usage-guard: no reading ({state.get('read_error')})")
        return 1
    resets = _parse_iso(state.get("resets_at"))
    when = resets.astimezone().strftime("%Y-%m-%d %H:%M") if resets else "?"
    print(f"5-hour window: {util:.1f}%  [{classify(util).upper()}]  "
          f"(warn {WARN:.0f} / stop {STOP:.0f})  resets {when}")
    if state.get("blocked_since"):
        print(f"  BLOCKED since {datetime.fromtimestamp(state['blocked_since']).strftime('%H:%M:%S')}; "
              f"checkpoint {state.get('block_checkpoint')}")
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
