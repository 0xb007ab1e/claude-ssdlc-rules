# Topic: Repository Docs Currency

Living docs are updated **in the same PR** as the change — never "docs later." Complements
`@rules/topic-documentation.md` (doc standards, generators, ADRs, runbooks) with the freshness
mandate that makes those docs trustworthy.

## Update per change
- A change to behavior, features, config, or the public API updates, in the **same PR** as the
  change, as applicable: the **README**, the **`docs/`** pages (including an **FAQ** and the
  generated API-site source), and the **CHANGELOG**. Stale docs are a defect, not a follow-up.
- Keep an **FAQ** for user-facing projects and update it as questions recur; keep the README
  quickstart runnable.
- Keep ADRs and runbooks current where they exist (`@rules/topic-documentation.md`,
  `@rules/workflow-runbooks.md`); diagrams-as-code and examples update with the code they describe
  (broken examples/links fail the doc build).

## Enforcement
- Where the SDLC is gated, enforce as an acceptance check (e.g. a reviewer criterion "docs not
  updated with the change"); otherwise a required review-checklist item
  (`@rules/workflow-code-review.md`).
- "Docs updated for new/changed public symbols and behavior" is part of the Definition of Done
  (master §8).

## References
- `@rules/topic-documentation.md` (standards, generators, Diátaxis), `@rules/workflow-code-review.md`.
  Index: `@rules/reference-style-guides.md`.
