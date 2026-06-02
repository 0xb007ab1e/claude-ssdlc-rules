# Rule: Gated Actions (human-in-the-loop)

Defines which automated/agent actions run **autonomously** vs. require **explicit human
approval** (a *gate*). Operationalizes master §1 ("commit/push/outward actions only when asked;
confirm hard-to-reverse"), §2 (fail closed, least privilege, complete mediation), and
`@rules/std-owasp-llm.md` LLM08 (excessive agency) for SDLC agents and any delegation.

## Principle
- Agents act **autonomously on reversible, local, non-production work** and **stop at a gate**
  before anything high-impact, irreversible, outward-facing, or production-touching.
- **Default deny / fail closed:** on silence, ambiguity, or uncertainty about whether an action
  is gated, treat it as gated and ask. Least autonomy needed for the task.

## Gated — require explicit, per-action human approval
- **Version control:** commit, push, tag, create remotes/PRs, merge to a protected branch,
  force-push, history rewrite (`@rules/workflow-git.md`).
- **Deploy / release:** any deploy or artifact promotion to a shared or production environment
  (`@rules/workflow-release.md`).
- **Destructive:** deleting files/resources outside an isolated worktree, DB schema/data
  migrations against real data, IaC `apply`/`destroy` to real infra, dropping resources.
- **Secrets:** create/rotate/revoke real credentials; read production secret stores
  (`@rules/workflow-secrets.md`).
- **Outward-facing:** send email/SMS/push/notifications; call paid or external APIs at scale;
  publish packages; create external accounts/resources.
- **Spend / data:** actions that incur cost; touching, exporting, or copying production data.
- **Governance:** relaxing or skipping a security gate, accepting a risk waiver, granting access.

## Autonomous — no gate (do freely, then report)
- Read/inspect/search; plan, design, threat-model.
- Scaffold and write/edit code, tests, docs **in a fresh repo or an isolated worktree**.
- Run tests, linters, formatters, type-checkers, build, and scanners locally.
- Produce diffs, proposals, and PR *drafts* (not opened) for review.

## Gate protocol
- Present: the **exact action**, **why**, **blast radius/severity** (master §7), and the
  **rollback**. Wait for explicit approval. Approval is **per-action and non-transferable** —
  approving one push is not standing approval for the next.
- **Log** gate requests and decisions (`@rules/topic-logging-observability.md`).

## Delegation interaction (coordinators ↔ subagents)
- A subagent that reaches a gate **stops and returns a gate request** to its coordinator; it
  never self-approves.
- **Coordinators never auto-approve** — they aggregate and **surface gate requests up to the
  human**. Only the human clears a gate.
- Subagents run with least privilege: their tool allowlist should **exclude gated tools where
  possible** (e.g. omit `Agent` to forbid sub-spawning); don't put gated operations in a skill's
  or agent's `allowed-tools`, so the permission layer still prompts. Gating is enforced by
  **policy + permissions together**, not policy alone.

## References
- master §1/§2/§7; `@rules/std-owasp-llm.md` (LLM08); `@rules/workflow-release.md`,
  `@rules/workflow-secrets.md`, `@rules/workflow-incident-response.md`. Index:
  `@rules/reference-style-guides.md`.
