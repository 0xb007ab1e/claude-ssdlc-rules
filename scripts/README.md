# scripts/

Small, portable helper scripts for this `~/.claude` setup.

## `claude_usage.py` — claude.ai usage monitor

Reads the same JSON the [claude.ai usage page](https://claude.ai/settings/usage)
shows — session (5-hour) and weekly (7-day) limit utilization — from the command
line, by calling claude.ai's internal usage endpoint with your authenticated
`sessionKey` cookie.

- **Portable:** Python 3.8+ standard library only. No `pip install`, no deps.
  Linux / macOS / Windows.
- **No HTML scraping:** hits the JSON endpoint the page itself uses
  (`/api/organizations/{uuid}/usage`).
- **Secret-safe:** the session key comes from an env var or a git-ignored file,
  never a CLI flag (which would leak into shell history / `ps`).

> ⚠️ claude.ai's internal endpoints are **undocumented** and may change or break
> without notice. This is a convenience monitor, not a supported API.

### 1. Get your session key

In a browser logged into claude.ai: **DevTools → Application/Storage → Cookies →
`https://claude.ai` → `sessionKey`**. The value looks like `sk-ant-sid01-…`.

### 2. Provide it (pick one)

```bash
# Option A — environment variable (good for a shell session / cron)
export CLAUDE_SESSION_KEY='sk-ant-sid01-...'

# Option B — git-ignored file (default location; recommended)
install -m 600 /dev/null ~/.claude/.claude_session_key
printf '%s' 'sk-ant-sid01-...' > ~/.claude/.claude_session_key
```

The file `~/.claude/.claude_session_key` is git-ignored (see `.gitignore`) so it
is never committed. Treat the session key like a password — it grants access to
your account.

### 3. Run

```bash
python3 ~/.claude/scripts/claude_usage.py            # one-shot table
python3 ~/.claude/scripts/claude_usage.py --json     # machine-readable
python3 ~/.claude/scripts/claude_usage.py --watch 60 # poll every 60s
```

Example output:

```
claude.ai usage  (org 1a2b3c4d...)  2026-06-04 14:02:11
  five_hour        [########----------------]  34.0%   resets in   3h 20m  (2026-06-04 17:00)
  seven_day        [##################------]  72.0%   resets in  2d 14h   (2026-06-07 04:00)
  seven_day_opus   [####--------------------]  18.0%   resets in  2d 14h   (2026-06-07 04:00)
```

### Options

| Flag | Purpose |
|---|---|
| `--json` | Emit raw + parsed JSON instead of the table. |
| `--watch SECONDS` | Poll repeatedly (floored at 5s) until `Ctrl-C`. |
| `--threshold PCT` | Exit code **2** if any window's utilization ≥ `PCT` (for alerting). |
| `--org-id UUID` | Skip org auto-discovery (or set `CLAUDE_ORG_ID`). |
| `--session-key-file PATH` | Read the sessionKey from a specific file. |
| `--timeout SECONDS` | Per-request timeout (default 15). |

Exit codes: `0` ok · `1` config/auth/network error · `2` threshold exceeded.

### Cron / alerting example

```bash
# Warn (non-zero exit) when any limit crosses 80%
*/30 * * * * CLAUDE_SESSION_KEY="$(cat ~/.claude/.claude_session_key)" \
  python3 ~/.claude/scripts/claude_usage.py --threshold 80 >/dev/null \
  || notify-send "Claude usage high"
```

### Troubleshooting

- **`Authentication failed (HTTP 401/403)`** — the sessionKey expired; get a
  fresh one. Persistent `403` can mean a Cloudflare challenge: pass a full cookie
  string (including `cf_clearance`) via `CLAUDE_COOKIE` instead of just the key.
- **`got an HTML challenge/login page`** — same cause; refresh the cookie.
