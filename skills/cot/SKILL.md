---
name: cot
description: >-
  Out-of-band, isolated execution and safety tooling for the terminal. Use when a shell
  command is blocked by Claude Code's own sandbox/permissions or needs capability the session
  lacks — network access, secrets/credentials, a full toolchain, or root/sudo — by delegating
  it to a provisioned out-of-band session (cot exec). Also: run a command in an egress
  allowlist (cot netjail), recoverably delete instead of rm (cot trash), scrub secrets/PII
  from output (cot redact), pre-check pip/npm/curl|sh installs for typosquats and pipe-to-shell
  (cot vet), snapshot→diff→revert a workspace (cot capsule), make an ephemeral isolated git
  worktree (cot worktree), or run as root inside a throwaway container (--session root-box).
---

# cot — out-of-band execution & safety toolkit

`cot` runs *restricted* commands out of band, in isolated/provisioned environments, and
provides safety utilities. It is terminal-confined and on `PATH` as `cot` (or `python -m cot`).
Every action is audited to `~/.claude/cot/audit.jsonl`.

## When to reach for it

| Situation | Use |
|---|---|
| A command is blocked by the sandbox / a deny rule, or needs network, secrets, a toolchain, or **sudo/root** | `cot exec --session <name> '<shell command>'` (async; result returns via the Stop hook or `cot result <id> --wait`) |
| Need network but only to specific hosts | `cot netjail run --allow github.com -- git fetch` |
| About to `rm` something | `cot trash put <paths>` → `cot trash restore <batch>` |
| Output may contain secrets/PII | `… | cot redact` |
| About to `pip/npm install` or `curl … | sh` | `cot vet '<command>'` (exit 2 = high risk) |
| Risky batch of edits you might want to undo | `cot capsule snapshot` → … → `cot capsule diff/restore/commit` |
| Want an isolated branch/checkout for edits | `cot worktree new` |
| Need root, but isolated from the host | `cot exec --session root-box '<command>'` (root in a throwaway container) |
| A human must approve a gated action | `cot approve request --action … --reason …` (human runs `cot approve grant <id>`) |

## Delegated execution (the core)

```bash
cot exec --session default 'npm install && npm test'   # queues a job, returns a job id
cot result <job-id> --wait                              # or it returns via the Stop hook
cot jobs                                                # queued / running / done
```

**Requires the daemon** (`cotd`) to be running to process jobs:
`systemctl --user status cotd` — if not active, `cot daemon run &` or `make install-daemon`.

Sessions are defined in `~/.claude/cot/sessions.toml` (or the bundled default). Ready-made:
`default` (your host env), `root-box` (root in an isolated container), `sudo-box`,
`container` (project mounted), `clean` (minimal env). Profiles can inject **secrets** from
references (`env:`/`file:`/`cmd:` — never values in config) and set resource limits / a gVisor
runtime.

## Notes
- `cot exec` takes the command as ONE shell string (full pipes/`&&`/redirection/`$VAR`).
- It does **not** perform gated actions itself; it's the mechanism to run the *reversible,
  non-prod, isolated* class safely. Push/deploy/destructive-on-host still need human approval.
- `cot <tool> --help` documents each tool; `cot sandbox doctor` / `cot netjail doctor` report
  available isolation backends.
