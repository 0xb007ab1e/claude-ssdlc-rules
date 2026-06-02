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

## Autonomous approval authority (delegated — for unattended runs)
A designated approver role (e.g. the `sdlc-gate-approver`) may **adjudicate** gate requests during
autonomous runs when no human is present. This **narrows** autonomy; it never widens it.

- **Opt-in per run, scoped by the human.** Autonomous approval is **OFF by default**: with no
  explicit, human-granted policy for the run, the approver **escalates everything** (current
  behavior preserved). The human pre-authorizes a specific scope/allowlist per run.
- **May auto-approve only if ALL hold:** reversible, **non-production**, no real secrets, no
  spend above a preset cap (default $0), within the run's declared scope, has a stated rollback,
  and is on the human's pre-authorized allowlist. Typical: a local commit on a feature branch in
  an isolated worktree, a **draft** PR, running tests/scanners, an ephemeral non-prod sandbox.
- **MUST escalate to the human (never auto-approve):** push to a shared/protected branch, merge,
  any deploy/promotion, IaC `apply`/`destroy` to real infra, create/rotate/revoke real secrets,
  outward-facing sends, spend over the cap, prod/data access, relaxing a security gate or risk
  waiver, anything destructive outside a worktree, and anything novel or ambiguous.
- **MUST deny:** requests that fail a security rule, lack a rollback, exceed the granted scope, or
  are otherwise unsafe — with a reason.
- **Fail closed:** default decision is **escalate**; approve only on an explicit, unambiguous
  policy match. The approver **decides only — it does not execute** gated actions; execution stays
  with the human/main session or a separately scoped step.
- **Audit:** record every decision (approve/deny/escalate), the request, the matched policy, and
  rationale (`@rules/topic-logging-observability.md`). Decisions are per-action, not standing.
- **Granting autonomy (scaffold):** the human fills in the template at
  `~/.claude/workflows/autonomy-policy.example.json` (who / run / expiry, scoped paths + non-prod
  environments, an `autoApprove.allowlist` + spend cap, and a reinforcing `alwaysEscalate` list)
  and passes it as `args.autonomy` to the PM orchestration. Omit it and everything escalates.

## References
- master §1/§2/§7; `@rules/std-owasp-llm.md` (LLM08); `@rules/workflow-release.md`,
  `@rules/workflow-secrets.md`, `@rules/workflow-incident-response.md`. Index:
  `@rules/reference-style-guides.md`.
