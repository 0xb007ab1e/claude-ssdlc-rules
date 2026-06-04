# scripts/

Small, portable helper scripts for this `~/.claude` setup.

## `claude_usage.py` — claude.ai usage monitor

Reads the same JSON the [claude.ai usage page](https://claude.ai/settings/usage)
shows — session (5-hour) and weekly (7-day) limit utilization — from the command
line, by calling claude.ai's internal usage endpoint with your authenticated
`sessionKey` cookie.

- **Portable:** Python 3.8+ standard library only for the core. No `pip install`.
- **No HTML scraping:** hits the JSON endpoint the page itself uses
  (`/api/organizations/{uuid}/usage`).
- **Live creds, no copy:** the `sessionKey` is read **live from your browser at
  request time** and used in memory only — never copied to disk, so a rotated
  cookie is always current. If the cookie in hand fails auth, the next valid
  candidate (another profile/browser, or a freshly rotated value) is tried
  automatically.

> ⚠️ claude.ai's internal endpoints are **undocumented** and may change or break
> without notice. This is a convenience monitor, not a supported API.

### Quick start

Just log into claude.ai in a browser, then run it — credentials are found for
you, live:

```bash
python3 ~/.claude/scripts/claude_usage.py            # one-shot table
python3 ~/.claude/scripts/claude_usage.py --json     # machine-readable
python3 ~/.claude/scripts/claude_usage.py --watch 60 # live dashboard (re-reads creds each tick)
python3 ~/.claude/scripts/claude_usage.py --threshold 80   # exit 2 if any window ≥ 80% (alerting)
```

Example output (`creds <source>` shows which browser/profile was used):

```
claude.ai usage  (org 1a2b3c4d..., creds brave:Default)  2026-06-04 14:02:11
  five_hour         [########----------------]  34.0%   resets in   3h 20m  (2026-06-04 17:00)
  seven_day         [##################------]  72.0%   resets in  2d 14h   (2026-06-07 04:00)
  seven_day_sonnet  [------------------------]   0.0%   resets in  2d 14h   (2026-06-07 04:00)
```

### Where credentials come from

Resolution order — the first that yields a candidate wins:

1. `--session-key-file PATH` — read the sessionKey from a file you manage.
2. `CLAUDE_COOKIE` env — a full `Cookie:` header string (advanced; lets you add
   `cf_clearance` for a Cloudflare challenge).
3. `CLAUDE_SESSION_KEY` env — just the sessionKey value.
4. **live browser read (default)** — every installed browser logged into
   claude.ai becomes a candidate; tried in order, first valid one used.
   `--browser NAME` narrows to one.

The live read uses `extract_session_key.py` (below). The only thing written to
disk is a throwaway temp copy of the *locked cookie database* (deleted
immediately) — never the credential itself.

> The explicit sources (1–3) are deliberate overrides: if you set one and it's
> invalid, the tool reports the failure rather than silently falling back to the
> browser. Leave them unset for the always-current live-browser default.

### Options

| Flag | Purpose |
|---|---|
| `--json` | Emit raw + parsed JSON (`org_id`, `source`, `raw`, `windows`). |
| `--watch SECONDS` | Poll repeatedly (floored at 5s) until `Ctrl-C`; re-reads creds live each tick. |
| `--threshold PCT` | Exit code **2** if any window's utilization ≥ `PCT`. |
| `--browser NAME` | Restrict the live read to one browser (`auto` by default). |
| `--org-id UUID` | Skip org auto-discovery (or set `CLAUDE_ORG_ID`). |
| `--session-key-file PATH` | Read the sessionKey from a file instead of a browser. |
| `--timeout SECONDS` | Per-request timeout (default 15). |

Exit codes: `0` ok · `1` config/auth/network error · `2` threshold exceeded.

## `extract_session_key.py` — locate the sessionKey

Used as a **library** by the monitor (`iter_candidates()`), and runnable on its
own to see where your cookie lives. It finds the claude.ai `sessionKey` across:

- **Firefox / LibreWolf** — plaintext `cookies.sqlite` (stdlib only).
- **Chrome / Chromium / Brave / Edge / Vivaldi** — decrypts the Linux
  `v10` (password `peanuts`) and `v11` (keyring "Safe Storage") AES-128-CBC
  scheme, handling the Chromium ≥ M114 32-byte domain-hash prefix. Decryption
  uses the `cryptography` package if present, else the `openssl` CLI.

```bash
python3 ~/.claude/scripts/extract_session_key.py            # report locations, NO copy
python3 ~/.claude/scripts/extract_session_key.py --stdout   # print the value (credential!)
python3 ~/.claude/scripts/extract_session_key.py --out FILE # write a (stale-prone) copy, opt-in
```

By default it makes **no copy** — it just reports which browsers/profiles hold a
valid cookie. Notes:

- `v11`/keyring cookies need the `secretstorage` pip package or the `secret-tool`
  CLI, with an unlocked keyring.
- macOS/Windows Chromium keyrings aren't handled — use Firefox there, or
  `CLAUDE_SESSION_KEY`.

## Headless / cron

No browser at runtime? Provide the key via env (rotate it yourself):

```bash
# Warn (non-zero exit) when any limit crosses 80%
*/30 * * * * CLAUDE_SESSION_KEY='sk-ant-sid01-...' \
  python3 ~/.claude/scripts/claude_usage.py --threshold 80 >/dev/null \
  || notify-send "Claude usage high"
```

Get a value manually from a logged-in browser: **DevTools → Application/Storage →
Cookies → `https://claude.ai` → `sessionKey`**. Treat it like a password.

## Troubleshooting

- **`all credential candidates were rejected`** — the cookie(s) expired; open
  claude.ai in your browser to refresh the session, then re-run.
- **`got a non-JSON response (likely a login/challenge page)`** — same cause, or
  a Cloudflare challenge: pass a full cookie (incl. `cf_clearance`) via
  `CLAUDE_COOKIE`.
- **`No AES backend available`** (Chromium decrypt) — install the `cryptography`
  pip package or the `openssl` CLI.

## `usage_guard.py` — pre-execution budget gate (all limit windows)

A synchronous Claude Code **`PreToolUse` hook** that, *before each tool call*,
checks utilization across **every** limit window the endpoint returns (5-hour
session, 7-day weekly, per-model weekly, …) and acts on the **worst** one,
naming the offending window(s) and their reset times:

- **< 80% (warn):** allow silently.
- **any window 80–95%:** allow, but **notify** (desktop via `notify-send` +
  stderr), naming the window(s) over warn; rate-limited to once per 10 min.
- **any window ≥ 95% (stop):** **block** token-consuming tool calls (exit 2) and
  enter a **safe stop** — write a resume checkpoint and notify, naming the
  window(s) over stop. A small read-only allowlist (`Read`, `Grep`, `Glob`,
  `TaskList`, …) stays permitted so the session isn't bricked.
  `CLAUDE_USAGE_OVERRIDE=1` bypasses for one run.
- **self-heal:** once the worst window falls back below warn (it reset), the
  block lifts automatically and you're notified. (A *weekly* window over stop
  keeps the block until that window resets — days, not hours — so the message
  says which window and when; override is always available.)

The thresholds (`CLAUDE_USAGE_WARN` / `CLAUDE_USAGE_STOP`) apply to every window.
`usage_guard.py status` prints all windows with a bar, level, and reset time.

Thresholds/behavior are env-tunable: `CLAUDE_USAGE_WARN` (80), `CLAUDE_USAGE_STOP`
(95), `CLAUDE_USAGE_TTL` (60s; 15s when ≥ warn), `CLAUDE_USAGE_ALLOW` (extra
always-allowed tools).

```bash
python3 ~/.claude/scripts/usage_guard.py status      # current state + level
python3 ~/.claude/scripts/usage_guard.py checkpoint  # snapshot jobs now
python3 ~/.claude/scripts/usage_guard.py install     # arm the PreToolUse hook (edits settings.json; backs it up)
python3 ~/.claude/scripts/usage_guard.py uninstall   # disarm
```

**Honest limits.** Utilization is a percentage + reset time, not a token count,
so "will this job finish?" is a heuristic (the threshold), not exact accounting.
A hook can't freeze an in-flight turn — blocking the *next* tool call is the stop
mechanism; in-session Tasks/Workflows/crons are halted by the block and recorded
in the checkpoint. Durable resume of a **closed** session needs a local
system-cron (opt-in), and auto-launching fresh AI work is intentionally manual
(it spends tokens and acts autonomously). If usage can't be read (expired cookie
/ Cloudflare), the gate **fails open** (allows + warns) so it never bricks your
tools.
