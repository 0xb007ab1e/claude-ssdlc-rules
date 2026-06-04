#!/usr/bin/env python3
"""Monitor claude.ai subscription usage from the command line.

Reads the same JSON the claude.ai usage page (https://claude.ai/settings/usage)
consumes, by calling claude.ai's internal usage endpoint with your authenticated
``sessionKey`` cookie:

    GET https://claude.ai/api/organizations                -> [{ "uuid": ... }]
    GET https://claude.ai/api/organizations/{uuid}/usage    -> usage windows

Each usage window (e.g. ``five_hour``, ``seven_day``, ``seven_day_sonnet``)
carries a ``utilization`` percentage and a ``resets_at`` ISO-8601 timestamp.

Portable: Python 3.8+ standard library only for the core. Reading the cookie
live from a browser additionally uses the sibling ``extract_session_key.py``
(which itself needs only stdlib for Firefox, and ``cryptography`` or ``openssl``
for Chromium).

Credential sourcing (NO on-disk copy by default)
------------------------------------------------
The session ``sessionKey`` rotates. To always use a current one, the cookie is
read **live from your browser at request time** and used in memory only - it is
never copied to disk. If the cookie in hand fails authentication, the next valid
candidate (another profile/browser, or a freshly rotated value) is tried
automatically.

Resolution order (first that yields a candidate wins):
  1. ``--session-key-file PATH`` - read the sessionKey from a file you manage.
  2. ``CLAUDE_COOKIE``      env  - a full Cookie header string (advanced).
  3. ``CLAUDE_SESSION_KEY`` env  - just the sessionKey value.
  4. live browser read (default) - every installed browser logged into claude.ai
     becomes a candidate; ``--browser NAME`` narrows to one.

Exit codes: 0 = ok, 1 = config/auth/network error, 2 = a threshold was exceeded.

WARNING: claude.ai's internal endpoints are undocumented and can change or break
without notice. This is a convenience monitor, not a supported API.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://claude.ai/api"
DEFAULT_TIMEOUT = 15.0
# A realistic browser User-Agent; the default urllib UA is often blocked by the
# Cloudflare layer in front of claude.ai.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# The sibling extractor is imported lazily for the live-browser path.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


class UsageError(Exception):
    """A user-facing error (config, auth, or network) that exits non-zero.

    :param auth: True if the failure is a credential/authentication problem, so
        the caller can fall through to the next candidate cookie.
    """

    def __init__(self, message: str, *, auth: bool = False) -> None:
        super().__init__(message)
        self.auth = auth


# --------------------------------------------------------------------------- #
# Credential candidates (live, no copy)
# --------------------------------------------------------------------------- #
def candidate_cookies(session_key_file: str | None, browser: str) -> list[tuple[str, str]]:
    """Return ordered ``(label, cookie_header)`` candidates to try.

    Explicit sources (file/env) yield a single candidate. Otherwise every
    browser logged into claude.ai is read **live** (in memory) and each becomes
    a candidate, newest-usable first. Raises :class:`UsageError` if none found.

    :param session_key_file: explicit path to a file holding the sessionKey.
    :param browser: ``"auto"`` or a specific browser name for the live read.
    """
    file_path = session_key_file
    if file_path:
        value = Path(file_path).expanduser().read_text(encoding="utf-8").strip()
        if not value:
            raise UsageError(f"{file_path} is empty.")
        return [("file", f"sessionKey={value}")]

    full_cookie = os.environ.get("CLAUDE_COOKIE", "").strip()
    if full_cookie:
        return [("env:CLAUDE_COOKIE", full_cookie)]

    session_key = os.environ.get("CLAUDE_SESSION_KEY", "").strip()
    if session_key:
        return [("env:CLAUDE_SESSION_KEY", f"sessionKey={session_key}")]

    # Live browser read - the default. Held in memory only; never written.
    try:
        import extract_session_key as esk
    except Exception as exc:  # pragma: no cover - import-time environment issue
        raise UsageError(f"cannot import extract_session_key.py for live read: {exc}")

    try:
        found = esk.iter_candidates(browser, "claude.ai", "sessionKey")
    except esk.ExtractError as exc:
        raise UsageError(str(exc))

    if not found:
        raise UsageError(
            "No claude.ai sessionKey found in any local browser. Log into "
            "claude.ai in a supported browser, or set CLAUDE_SESSION_KEY / "
            "--session-key-file."
        )
    return [(label, f"sessionKey={value}") for label, value in found]


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def http_get_json(url: str, cookie: str, timeout: float) -> object:
    """GET ``url`` with the session cookie and return parsed JSON.

    :raises UsageError: on auth failure (``auth=True``), HTTP error, network
        error, or non-JSON response. The session key is never included in any
        error message.
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
            raise UsageError(f"authentication rejected (HTTP {exc.code})", auth=True) from exc
        raise UsageError(f"HTTP {exc.code} from {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise UsageError(f"Network error contacting claude.ai: {exc.reason}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        # claude.ai returned HTML (login/challenge) instead of JSON -> treat as
        # an auth problem so we fall through to the next candidate.
        raise UsageError("got a non-JSON response (likely a login/challenge page)", auth=True) from exc


def discover_org_id(cookie: str, timeout: float) -> str:
    """Return an organization UUID, preferring one with chat capability."""
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
    top-level entry that looks like an active usage window. Auto-adapts to new
    windows; entries with a null/None utilization (inactive windows, or the
    ``extra_usage`` credit-balance object when disabled) are skipped.
    """
    windows = []
    for name, value in usage.items():
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


def render_text(windows: list[dict], org_id: str, source: str) -> str:
    """Render usage windows as a human-readable table."""
    header = (f"claude.ai usage  (org {org_id[:8]}..., creds {source})  "
              f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if not windows:
        return header + "\n  No active usage windows found."
    lines = [header]
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
        description="Monitor claude.ai subscription usage (session/weekly limits). "
                    "Reads the sessionKey live from your browser by default - no copy.",
    )
    parser.add_argument("--json", action="store_true", help="emit raw + parsed JSON instead of a table")
    parser.add_argument("--org-id", default=os.environ.get("CLAUDE_ORG_ID"),
                        help="organization uuid (default: auto-discover; or CLAUDE_ORG_ID)")
    parser.add_argument("--browser", default="auto",
                        help="which browser to read the cookie from for the live read "
                             "(default 'auto' tries all)")
    parser.add_argument("--session-key-file", help="read the sessionKey from this file instead of a browser")
    parser.add_argument("--threshold", type=float, metavar="PCT",
                        help="exit code 2 if any window's utilization >= PCT")
    parser.add_argument("--watch", type=float, metavar="SECONDS",
                        help="poll repeatedly every SECONDS until interrupted (re-reads creds live each time)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"per-request timeout in seconds (default {DEFAULT_TIMEOUT})")
    return parser


def run_once(args: argparse.Namespace) -> int:
    """Fetch and report usage once, trying credential candidates in order.

    Re-resolves candidates on each call (so ``--watch`` always uses current
    cookies). Falls through to the next candidate on an auth failure. Returns
    the intended process exit code.
    """
    candidates = candidate_cookies(args.session_key_file, args.browser)
    last_auth_error: UsageError | None = None

    for label, cookie in candidates:
        try:
            org_id = args.org_id or discover_org_id(cookie, args.timeout)
            usage = fetch_usage(cookie, org_id, args.timeout)
        except UsageError as exc:
            if exc.auth:
                last_auth_error = exc
                if len(candidates) > 1:
                    print(f"note: creds from {label} {exc} - trying next", file=sys.stderr)
                continue
            raise

        windows = extract_windows(usage)
        if args.json:
            print(json.dumps({"org_id": org_id, "source": label, "raw": usage,
                              "windows": windows}, indent=2))
        else:
            print(render_text(windows, org_id, label))

        if args.threshold is not None and max_utilization(windows) >= args.threshold:
            if not args.json:
                print(f"  ! threshold {args.threshold:.0f}% reached or exceeded", file=sys.stderr)
            return 2
        return 0

    # Every candidate failed authentication.
    raise UsageError(
        "all credential candidates were rejected - log into claude.ai in your "
        "browser to refresh the session, or set a valid CLAUDE_SESSION_KEY.",
        auth=True,
    ) if last_auth_error else UsageError("no usable credentials found.")


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code (0 ok, 1 error, 2 threshold)."""
    args = build_parser().parse_args(argv)

    if args.watch is None:
        try:
            return run_once(args)
        except UsageError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    interval = max(5.0, args.watch)  # floor to avoid hammering the endpoint
    worst = 0
    try:
        while True:
            try:
                worst = max(worst, run_once(args))
            except UsageError as exc:
                print(f"error: {exc}", file=sys.stderr)
                worst = max(worst, 1)
            print("-" * 60)
            time.sleep(interval)
    except KeyboardInterrupt:
        return worst


if __name__ == "__main__":
    sys.exit(main())
