# Topic: Spec-Driven Development (SDD)

Author a **machine-checkable spec before code**, then gate every phase transition against it. This is
the positive complement to the rest of the ruleset: the standards/lang modules check the *absence of
defects*; SDD adds the *contract of what the software must do* — the missing "what" that makes
autonomous generation verifiable. Pairs with `@rules/workflow-gated-actions.md`,
`@rules/topic-testing.md`, `@rules/workflow-threat-model.md`, `@rules/topic-api-design.md`.

## The spec is the source of truth
- Every feature starts from a **spec, not code**: an executable/verifiable statement of intent —
  acceptance criteria, interface contract (types/schema), properties/invariants, data classification,
  security/authz requirements, and the **oracle** for "correct" (reference output, invariant,
  differential). A prose PRD is **not** a spec; a spec is checkable.
- Artifacts live on disk, versioned and reviewed like code: per feature a `spec` (what), `plan`
  (design/approach), `tasks` (work items), each traceable forward to tests and gate results.
- Reference toolchain: **GitHub spec-kit** (`specify` CLI; `/speckit-constitution|specify|plan|tasks|
  implement|converge`; artifacts under `.specify/` — `memory/constitution.md`, per-feature
  `spec.md`/`plan.md`/`tasks.md` + `contracts/`). Any SDD tool qualifies if it emits reviewable
  spec/plan/tasks artifacts.

## Constitution = this ruleset (one source of truth)
- The SDD "constitution" (principles the agent must obey) is **generated from / points at** this
  ruleset (`~/.claude/CLAUDE.md` + imported modules) — never a second, divergent copy. The
  non-negotiable mandates (master §1) are constitution clauses. Regenerate on ruleset change; drift is
  a defect.

## Gate every phase transition (authoring ≠ the gate)
An SDD tool's own "done/converged" signal is an **LLM self-check — advisory, not authoritative.**
Each artifact transition is gated by the deterministic engine (`@rules/workflow-gated-actions.md`;
Lattice or equivalent), **fail-closed**:
- **spec → plan:** spec is complete + testable — acceptance criteria present, data classified
  (master §5), authz/abuse requirements stated, an oracle defined. Otherwise BLOCK.
- **plan → tasks:** design threat-modeled (`@rules/workflow-threat-model.md`); contracts + versioning
  defined (`@rules/topic-api-design.md`); no secrets in design (`@rules/workflow-secrets.md`).
- **tasks → implement:** every task traces to a spec acceptance id and names its test.
- **implement → done:** the applicable language/standard batteries + CI gates
  (`@rules/workflow-cicd.md`) **plus spec-conformance** — the spec's acceptance criteria run as tests
  and its properties as property/abuse tests (`@rules/topic-testing.md`, master §4). "Converged" only
  when the gate returns PASS, not when the author agent says so.
- Irreversible/outward actions (commit, PR, merge, deploy) stay human-gated regardless
  (`@rules/workflow-gated-actions.md`).

## Traceability (the evidence chain)
- Maintain **requirement → spec clause → task → test → gate verdict → artifact**. It is both the
  autonomous-correctness signal (did it build what was asked, provably?) and change-management
  evidence (`@rules/std-soc2.md`, `@rules/workflow-issue-tracking.md`). Record it, don't reconstruct it.

## Proportionality
- Full `spec → plan → tasks` for features and any trust-boundary change; a lighter spec (or the tool's
  bug/fix path) for small fixes. Match ceremony to risk — don't gold-plate (`@rules/topic-anti-patterns.md`).

## Supply chain & trust
- Pin the SDD tool as a **vetted dependency** (`@rules/std-supplychain.md`) — it is young and evolving.
- Generated specs/plans/tasks are **reviewable artifacts, not trusted output** (mandate §1: verify
  AI-generated code and content before it lands).

## References
- **GitHub spec-kit** — github.com/github/spec-kit (Spec-Driven Development).
- Contract-first: `@rules/topic-api-design.md`; design-by-contract / "parse, don't validate":
  `@rules/topic-defensive-programming.md`. Index: `@rules/reference-style-guides.md`.
