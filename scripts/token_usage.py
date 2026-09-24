"""Token-first usage reader — reuse Claude Code's own OAuth credential.

The consistent alternative to scraping browser cookies: Claude Code stores an OAuth token in
``~/.claude/.credentials.json`` (``claudeAiOauth``) and keeps it fresh (access ~1h, refresh
~1 month). The CLI reads usage from ``GET https://api.anthropic.com/api/oauth/usage`` with an
``Authorization: Bearer`` header — no browser, no org lookup, same JSON shape as the cookie path.

This module fetches that and returns the same ``[{name, utilization, resets_at}, ...]`` windows
(parsed by :func:`claude_usage.extract_windows`). It **never writes** the credential file — on an
expired/absent token or any HTTP/network failure it raises :class:`TokenUnavailable`, so the caller
falls back to the browser-cookie reader.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

CREDENTIALS = Path.home() / ".claude" / ".credentials.json"
USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
EXPIRY_SKEW_S = 60.0  # treat a token expiring within this as already expired


class TokenUnavailable(Exception):
    """The OAuth token path can't serve — caller should fall back to the cookie reader."""


def load_token() -> dict | None:
    """Return the ``claudeAiOauth`` credential block, or ``None`` if absent/unreadable."""
    try:
        return json.loads(CREDENTIALS.read_text(encoding="utf-8")).get("claudeAiOauth")
    except (OSError, json.JSONDecodeError, AttributeError):
        return None


def is_expired(cred: dict, now: float | None = None, skew_s: float = EXPIRY_SKEW_S) -> bool:
    """True if the access token is expired (or within ``skew_s`` of expiring). ``expiresAt`` is ms."""
    exp = cred.get("expiresAt")
    if not isinstance(exp, (int, float)):
        return True
    now = time.time() if now is None else now
    return (exp / 1000.0) <= (now + skew_s)


def _get_json(url: str, token: str, timeout: float) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "carterm-usage-guard",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # 401/403 → token no good (expired/revoked) → fall back; others surface too.
        raise TokenUnavailable(f"HTTP {exc.code} from oauth usage") from exc
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise TokenUnavailable(f"oauth usage read failed: {exc}") from exc


def fetch_usage_windows(timeout: float = 8.0) -> list[dict]:
    """Fetch usage via the OAuth token. Raises :class:`TokenUnavailable` on any problem.

    Returns the same ``[{name, utilization, resets_at}, ...]`` shape as the cookie reader
    (parsed by ``claude_usage.extract_windows``).
    """
    cred = load_token()
    if not cred:
        raise TokenUnavailable("no oauth credential in ~/.claude/.credentials.json")
    if is_expired(cred):
        raise TokenUnavailable("oauth access token expired")
    token = cred.get("accessToken")
    if not token:
        raise TokenUnavailable("oauth credential missing accessToken")

    data = _get_json(USAGE_URL, token, timeout)

    import claude_usage as cu  # reuse the shared window parser

    windows = cu.extract_windows(data)
    if not windows:
        raise TokenUnavailable("no usage windows in oauth response")
    return windows
