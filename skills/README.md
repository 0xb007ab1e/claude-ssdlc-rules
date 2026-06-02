# SDLC Agent Org

Role-based agents layered on the SSDLC ruleset (`~/.claude/rules`). Each role is a **skill**
(`~/.claude/skills/sdlc-*/SKILL.md`, user-invocable as `/sdlc-*`) and most are also a spawnable
**subagent** (`~/.claude/agents/sdlc-*.md`). Roles *reference* the rules — they don't duplicate them.

## Org chart
```
                                  Human (you)
                                      │
                        /sdlc-project-manager   (coordinator · main context)
                                      │   delegates 1:N in parallel, worktree-isolated
              ┌───────────────────────┼────────────────────────┐
   /sdlc-software-architect   /sdlc-infra-architect      /sdlc-release-manager
     (absorbs bootstrap)              │                    (prepares; ship = gated)
        ┌──────┬───────┬──────┐       │
     backend frontend security qa   sre-engineer
     engineer engineer engineer engineer

  Cross-cutting / oversight / advisory (consultable by any role or the human):
   /sdlc-reviewer            verify gate (security & quality) — advisory, read-only
   /sdlc-red-team            decision devil's advocate — consensus before proceed, else escalate
   /sdlc-sme                 sourced domain expert — advisory, read-only
   /sdlc-gate-approver       decides on gated actions (opt-in autonomy) — never executes
    sdlc-gate-executor       executes ONLY the approved reversible class (agent-only)
   /sdlc-incident-commander  runs incident response — reports to the human
```

## Roles
| Command (skill) | Agent def | Group | Reports to | Delegates to | Isolation | Gated? |
|---|---|---|---|---|---|---|
| `/sdlc-project-manager` | — (main ctx) | Coordinator | human | architects (1:N ∥) | — | enforces; never auto-approves |
| `/sdlc-software-architect` | ✓ | Architect (T1) | PM | backend/frontend/security/qa eng | worktree | yes |
| `/sdlc-infra-architect` | ✓ | Architect (T1) | PM | sre-engineer | worktree | yes |
| `/sdlc-release-manager` | ✓ | Manager (T1) | PM | sre-engineer | — | yes (+disallowedTools) |
| `/sdlc-backend-engineer` | ✓ | Engineer (T2, leaf) | software-arch | — | worktree | yes |
| `/sdlc-frontend-engineer` | ✓ | Engineer (T2, leaf) | software-arch | — | worktree | yes |
| `/sdlc-security-engineer` | ✓ | Engineer (T2, leaf) | software-arch | — | worktree | yes |
| `/sdlc-qa-engineer` | ✓ | Engineer (T2, leaf) | software-arch | — | worktree | yes |
| `/sdlc-sre-engineer` | ✓ | Engineer (T2, leaf) | infra-arch | — | worktree | yes |
| `/sdlc-reviewer` | ✓ | Oversight | software-arch | — | — | advisory/read-only |
| `/sdlc-red-team` | ✓ | Oversight | parent-of-decision | — | — | advisory/read-only |
| `/sdlc-sme` | ✓ | Advisory | requester | — | — | advisory/read-only |
| `/sdlc-gate-approver` | ✓ | Oversight | human | — | — | decides only |
| _(none)_ `sdlc-gate-executor` | ✓ | Execution authority | — | — | — | executes approved class (hook+denylist) |
| `/sdlc-incident-commander` | ✓ | Command | human | responders (main ctx) | — | yes (prod/secrets) |

T1 = tier 1, T2 = tier 2. "∥" = parallel.

## Delegation model
- **One level only.** A subagent **cannot** spawn subagents (platform limit; `Agent` tool withheld
  from worker agent defs). Whoever holds the **main context** does the spawning. A delegated role
  that needs its own team **returns a "needs N engineers" request** to its coordinator.
- **Parallel + isolated.** Architects/engineers run in their own **git worktrees**
  (`isolation: worktree`) on **disjoint files** (batch-atomicity); no two workers touch one file.
- Each worker agent **preloads its skill** (`skills:` frontmatter) — skill = role spec, agent = the
  spawnable, worktree-isolated, non-delegating wrapper.

## Gated actions & autonomy (`~/.claude/rules/workflow-gated-actions.md`)
- Roles act autonomously on **reversible/local** work; they **stop at gates** (commit, push, deploy,
  destructive, secrets, outward-facing, prod/data, waivers) and return a **gate request**.
- **Approver decides, executor executes, neither is the requester** (separation of duties). The
  `sdlc-gate-approver` approves only the human-pre-authorized reversible/non-prod/in-scope class and
  **escalates the rest**; `sdlc-gate-executor` then runs only the approved actions, backstopped by
  `disallowedTools` **and** a fail-closed PreToolUse hook (`~/.claude/hooks/gate-executor-guard.py`).
- **Autonomy is opt-in per run:** fill in `~/.claude/workflows/autonomy-policy.example.json` and pass
  it as `args.autonomy`. Omit it → **everything escalates to the human** (default-safe).

## PM orchestration workflow (`~/.claude/workflows/sdlc-pm-orchestration.js`)
`Plan → Challenge (red-team) → Architect (∥ worktrees) → Integrate → Review → Adjudicate → Execute →
Gate Review`. Budget-capped to the turn's `+Nk` target. A red-team **no-consensus** halts before
building; a reviewer **block** suppresses autonomous execution; escalations/denials are never executed.

## How to invoke
- **Single role:** `/sdlc-sme <topic>`, `/sdlc-reviewer <diff>`, `/sdlc-software-architect <task>`, …
- **Full delivery:** `/sdlc-project-manager <goal>` (Direct mode for simple work; Workflow mode for
  ≥2 parallel workstreams — add `args.autonomy` to enable the approved-class auto-execution).
- **SDLC flow:** bootstrap → build (architects+engineers) → verify (reviewer + threat model) →
  release (release-manager) → operate (incident-commander). Advisory: SME (expertise), Red Team (challenge).

See `~/.claude/rules/README.md` for the rule catalog and `~/.claude/CLAUDE.md` for the master ruleset.
