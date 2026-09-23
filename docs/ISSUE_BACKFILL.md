# Backfilled Issue → Commit Mapping

All commits below predate the adoption of the issue-tracking rule
(`rules/workflow-issue-tracking.md`). Their tracking issues were filed
**retroactively** — labeled `backfilled`, closed as completed, each linked to its
delivering commit — as honest historical records. This is **not** a claim the work was
tracked at the time; signed history was never rewritten (`rules/workflow-git.md`).

Repo: [`0xb007ab1e/claude-ssdlc-rules`](https://github.com/0xb007ab1e/claude-ssdlc-rules)

| Issue | Commit | Subject |
|---|---|---|
| #5 | `6cd6c5f` | fix: @RTK.md import broken in CI (untracked by .gitignore allowlist) |
| #6 | `3b0daa8` | feat(rules): promote issue-tracking + docs-currency to global; catalog reverse-engineering |
| #7 | `faa1181` | rules: add knowledge-base + tailnet-dev-access universal modules |
| #8 | `446094e` | feat(scripts): usage guard monitors ALL limit windows, not just 5-hour |
| #9 | `d6073de` | feat(scripts): pre-execution usage guard (5h budget gate, inert) |
| #10 | `08b0025` | feat(scripts): use live browser creds, never a copy; auto-fallthrough on auth fail |
| #11 | `f902d97` | feat(scripts): auto-locate sessionKey from browser; live-verified |
| #12 | `a2f32ad` | feat(scripts): portable claude.ai usage monitor |
| #13 | `31a7e35` | fix(workflow): dry-run findings — pure-literal meta + graceful agent-load guard + prereqs |
| #14 | `4ad13de` | docs(skills): add SDLC agent org map (README) |
| #15 | `ee9ca37` | feat(skills): reviewer, release-manager, incident-commander roles |
| #16 | `5bb4289` | harden(gate-executor): fail-closed PreToolUse hook (hard boundary) |
| #17 | `2e7ad2d` | harden(gate-executor): command-level disallowedTools backstop |
| #18 | `5958ee4` | feat(skills): red-team (decision devil's advocate) + autonomous execution of approved class |
| #19 | `7ca7ea9` | feat(skills): add SME advisory role + scaffold opt-in autonomy policy |
| #20 | `ad89d6b` | feat(skills): engineering tier + gate-approver (autonomous gate adjudication) |
| #21 | `d2f496b` | feat(workflows): budgeted, gate-bounded PM orchestration workflow |
| #22 | `f0aeed0` | feat(skills): SDLC role org (PM + architects) with gated-action delegation |
| #23 | `96d896f` | fix(check-rules): resolve ~/.claude/ template imports against repo root |
| #24 | `bec44a0` | ci: add GitHub Action running check-rules.sh on push/PR |
| #25 | `d960ea3` | Add SSDLC ruleset: master + 78 modules, templates, runbooks |

_Generated during the issue-tracking backfill. 21 issues (#5–#25)._
