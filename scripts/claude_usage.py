#!/usr/bin/env python3
"""Monitor claude.ai subscription usage from the command line.

Reads the same JSON the claude.ai usage page (https://claude.ai/settings/usage)
consumes, by calling claude.ai's internal usage endpoint with your authenticated
``sessionKey`` cookie:

    GET https://claude.ai/api/organizations                -> [{ "uuid": ... }]
    GET https://claude.ai/api/organizations/{uuid}/usage    -> usage windows

Each usage window (e.g. ``five_hour``, ``seven_day``, ``seven_day_opus``) carries
a ``utilization`` percentage and a ``resets_at`` ISO-8601 timestamp.

Portable: Python 3.8+ standard library only (no pip installs, no third-party
deps). Runs on Linux, macOS, and Windows.

Authentication
--------------
The script needs your claude.ai web ``sessionKey`` (value looks like
``sk-ant-sid01-...``). Get it from a logged-in browser:
DevTools -> Application/Storage -> Cookies -> https://claude.ai -> ``sessionKey``.

Provide it via one of (checked in this order); the secret is never accepted as a
plain CLI argument (that would leak into shell history / the process table):

  1. ``CLAUDE_COOKIE``      env var  - a full Cookie header string (advanced;
                                       lets you add e.g. ``cf_clearance`` if a
                                       Cloudflare challenge requires it).
  2. ``CLAUDE_SESSION_KEY`` env var  - just the sessionKey value.
  3. ``--session-key-file PATH``     - file containing only the sessionKey.
  4. ``~/.claude/.claude_session_key`` (default file, if present).

Exit codes: 0 = ok, 1 = config/auth/network error, 2 = a threshold was exceeded.

WARNING: claude.ai's internal endpoints are undocumented and can change or break
without notice. This is a convenience monitor, not a supported API.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://claude.ai/api"
DEFAULT_KEY_FILE = Path.home() / ".claude" / ".claude_session_key"
DEFAULT_TIMEOUT = 15.0
# A realistic browser User-Agent; the default urllib UA is often blocked by the
# Cloudflare layer in front of claude.ai.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class UsageError(Exception):
    """A user-facing error (config, auth, or network) that should exit non-zero."""


# --------------------------------------------------------------------------- #
# Credential resolution
# --------------------------------------------------------------------------- #
def resolve_cookie(session_key_file: str | None) -> str:
    """Return the ``Cookie`` header value to send with each request.

    Resolution order is documented in the module docstring. Raises
    :class:`UsageError` if no credential is found.

    :param session_key_file: optional explicit path to a file holding the
        sessionKey value; overrides the default key-file location.
    :returns: a Cookie header string (e.g. ``"sessionKey=sk-ant-sid01-..."``).
    """
    full_cookie = os.environ.get("CLAUDE_COOKIE", "").strip()
    if full_cookie:
        return full_cookie

    session_key = os.environ.get("CLAUDE_SESSION_KEY", "").strip()
    if not session_key:
        key_path = Path(session_key_file).expanduser() if session_key_file else DEFAULT_KEY_FILE
        if key_path.is_file():
            session_key = key_path.read_text(encoding="utf-8").strip()

    if not session_key:
        raise UsageError(
            "No claude.ai session key found.\n"
            "Set CLAUDE_SESSION_KEY, or write the sessionKey to "
            f"{DEFAULT_KEY_FILE} (chmod 600), or pass --session-key-file.\n"
            "Get the value from a logged-in browser: DevTools -> Cookies -> "
            "https://claude.ai -> sessionKey."
        )
    return f"sessionKey={session_key}"


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def http_get_json(url: str, cookie: str, timeout: float) -> object:
    """GET ``url`` with the session cookie and return parsed JSON.

    :raises UsageError: on auth failure, HTTP error, network error, or non-JSON
        response. The session key is never included in any error message.
    """
    request = urllib.request.Request(url, method="GET")
    request.add_header("Cookie", cookie)
    request.add_header("User-Agent", USER_AGENT)
    request.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise UsageError(
                f"Authentication failed (HTTP {exc.code}). Your sessionKey is "
                "likely expired or invalid - grab a fresh one from the browser. "
                "If you keep getting 403, a Cloudflare challenge may require "
                "passing a full cookie via CLAUDE_COOKIE (including cf_clearance)."
            ) from exc
        raise UsageError(f"HTTP {exc.code} from {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise UsageError(f"Network error contacting claude.ai: {exc.reason}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UsageError(
            f"Expected JSON from {url} but got something else "
            "(claude.ai may have returned an HTML challenge/login page)."
        ) from exc


def discover_org_id(cookie: str, timeout: float) -> str:
    """Return an organization UUID, preferring one with chat capability.

    :raises UsageError: if no organization is found.
    """
    data = http_get_json(f"{BASE_URL}/organizations", cookie, timeout)
    if not isinstance(data, list) or not data:
        raise UsageError("No organizations returned for this account.")

    def has_chat(org: dict) -> bool:
        caps = org.get("capabilities") or []
        return isinstance(caps, list) and "chat" in caps

    for org in data:
        if isinstance(org, dict) and org.get("uuid") and has_chat(org):
            return str(org["uuid"])
    for org in data:
        if isinstance(org, dict) and org.get("uuid"):
            return str(org["uuid"])
    raise UsageError("Could not find an organization uuid in the response.")


def fetch_usage(cookie: str, org_id: str, timeout: float) -> dict:
    """Fetch the raw usage JSON for ``org_id``."""
    data = http_get_json(f"{BASE_URL}/organizations/{org_id}/usage", cookie, timeout)
    if not isinstance(data, dict):
        raise UsageError("Unexpected usage response shape (expected an object).")
    return data


# --------------------------------------------------------------------------- #
# Parsing & rendering
# --------------------------------------------------------------------------- #
def extract_windows(usage: dict) -> list[dict]:
    """Pull usage windows out of the raw response, defensively.

    Returns a list of ``{name, utilization, resets_at}`` dicts for every
    top-level entry that looks like a usage window (a dict carrying a
    ``utilization`` field). This auto-adapts if claude.ai adds new windows.
    """
    windows = []
    for name, value in usage.items():
        # A real usage window is a dict carrying a numeric utilization. Skip
        # null/None utilization (e.g. inactive windows, or the extra_usage
        # credit-balance object when disabled).
        if isinstance(value, dict) and value.get("utilization") is not None:
            windows.append(
                {
                    "name": name,
                    "utilization": value.get("utilization"),
                    "resets_at": value.get("resets_at"),
                }
            )
    return windows


def _parse_iso(ts: str | None) -> datetime | None:
    """Parse an ISO-8601 timestamp (tolerating a trailing ``Z``)."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _humanize_delta(target: datetime | None) -> str:
    """Render time remaining until ``target`` as ``"3h 20m"`` (or ``"reset"``)."""
    if target is None:
        return "?"
    seconds = (target - datetime.now(timezone.utc)).total_seconds()
    if seconds <= 0:
        return "reset"
    days, rem = divmod(int(seconds), 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _bar(pct: float, width: int = 24) -> str:
    """Return a fixed-width ASCII utilization bar for ``pct`` (0-100)."""
    pct = max(0.0, min(100.0, float(pct)))
    filled = int(round(pct / 100 * width))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def render_text(windows: list[dict], org_id: str) -> str:
    """Render usage windows as a human-readable table."""
    if not windows:
        return "No usage windows found in the response."
    lines = [f"claude.ai usage  (org {org_id[:8]}...)  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
    name_w = max(len(w["name"]) for w in windows)
    for w in windows:
        try:
            pct = float(w["utilization"])
        except (TypeError, ValueError):
            pct = 0.0
        resets = _parse_iso(w["resets_at"])
        local = resets.astimezone().strftime("%Y-%m-%d %H:%M") if resets else "?"
        lines.append(
            f"  {w['name']:<{name_w}}  {_bar(pct)} {pct:5.1f}%   "
            f"resets in {_humanize_delta(resets):>7}  ({local})"
        )
    return "\n".join(lines)


def max_utilization(windows: list[dict]) -> float:
    """Return the highest utilization across all windows (0.0 if none)."""
    values = []
    for w in windows:
        try:
            values.append(float(w["utilization"]))
        except (TypeError, ValueError):
            continue
    return max(values) if values else 0.0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Monitor claude.ai subscription usage (session/weekly limits).",
        epilog="Auth: set CLAUDE_SESSION_KEY env var or ~/.claude/.claude_session_key file.",
    )
    parser.add_argument("--json", action="store_true", help="emit raw + parsed JSON instead of a table")
    parser.add_argument("--org-id", default=os.environ.get("CLAUDE_ORG_ID"),
                        help="organization uuid (default: auto-discover; or CLAUDE_ORG_ID)")
    parser.add_argument("--session-key-file", help="path to a file containing the sessionKey value")
    parser.add_argument("--from-browser", nargs="?", const="auto", metavar="BROWSER",
                        help="locate+copy the sessionKey from a local browser first "
                             "(runs extract_session_key.py; default 'auto')")
    parser.add_argument("--threshold", type=float, metavar="PCT",
                        help="exit code 2 if any window's utilization >= PCT")
    parser.add_argument("--watch", type=float, metavar="SECONDS",
                        help="poll repeatedly every SECONDS until interrupted")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"per-request timeout in seconds (default {DEFAULT_TIMEOUT})")
    return parser


def run_once(args: argparse.Namespace, cookie: str) -> int:
    """Fetch and report usage one time. Returns the intended process exit code."""
    org_id = args.org_id or discover_org_id(cookie, args.timeout)
    usage = fetch_usage(cookie, org_id, args.timeout)
    windows = extract_windows(usage)

    if args.json:
        print(json.dumps({"org_id": org_id, "raw": usage, "windows": windows}, indent=2))
    else:
        print(render_text(windows, org_id))

    if args.threshold is not None and max_utilization(windows) >= args.threshold:
        if not args.json:
            print(f"  ! threshold {args.threshold:.0f}% reached or exceeded", file=sys.stderr)
        return 2
    return 0


def refresh_key_from_browser(browser: str, out_path: str | None) -> None:
    """Run the sibling extractor to copy the sessionKey from a local browser.

    :raises UsageError: if the extractor is missing or fails.
    """
    extractor = Path(__file__).resolve().parent / "extract_session_key.py"
    if not extractor.is_file():
        raise UsageError(f"extractor not found at {extractor}")
    cmd = [sys.executable, str(extractor), "--browser", browser]
    if out_path:
        cmd += ["--out", out_path]
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise UsageError("could not extract a session key from the browser "
                         "(see the error above)")


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code (0 ok, 1 error, 2 threshold)."""
    args = build_parser().parse_args(argv)
    try:
        if args.from_browser:
            refresh_key_from_browser(args.from_browser, args.session_key_file)
        cookie = resolve_cookie(args.session_key_file)
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.watch is None:
        try:
            return run_once(args, cookie)
        except UsageError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    interval = max(5.0, args.watch)  # floor to avoid hammering the endpoint
    worst = 0
    try:
        while True:
            try:
                worst = max(worst, run_once(args, cookie))
            except UsageError as exc:
                print(f"error: {exc}", file=sys.stderr)
                worst = max(worst, 1)
            print("-" * 60)
            time.sleep(interval)
    except KeyboardInterrupt:
        return worst


if __name__ == "__main__":
    sys.exit(main())
