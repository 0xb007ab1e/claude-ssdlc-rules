# Topic: Legacy Migration & Modernization

Replacing or re-platforming existing systems incrementally and safely — **never big-bang**.
Pairs with `@rules/topic-database.md` (schema/data), `@rules/workflow-release.md` (rollout),
and `@rules/topic-testing.md` (safety net).

## Strategy
- **Strangler fig:** route functionality from old to new incrementally behind a facade/router;
  the new system grows as the legacy one shrinks, until the old is decommissioned. Each step is
  small, shippable, and reversible.
- **Characterize before you change:** capture current behavior with characterization/golden
  tests around the legacy code first — your regression safety net (`@rules/topic-testing.md`).
- **Anti-corruption layer:** translate between old and new models so legacy concepts don't leak
  into the new design (`@rules/topic-architecture-patterns.md`).
- **Feature-flag** the cutover per slice so you can roll forward/back instantly
  (`@rules/topic-config-environments.md`, `@rules/workflow-release.md`).

## Parallel run (esp. correctness-sensitive)
- Run old and new **side by side on the same input and compare outputs** (shadow/dark launch)
  before cutting traffic over; investigate every divergence. For correctness-critical systems
  this is the gate (e.g. your scraper's Silent Corruption Rate —
  `@rules/templates/web-scraper-crawler.md`).

## Data migration
- **Expand/contract** schema changes for zero downtime (`@rules/topic-database.md`).
- Backfills are **idempotent, resumable, batched, and validated**; reconcile counts/checksums;
  keep a verified rollback. Use dual-write or CDC during the transition window; cut over only
  after parallel-run confidence.

## Decommission
- Remove legacy only after the new path is proven and traffic fully migrated; **archive/retain**
  legacy data per `@rules/workflow-data-lifecycle.md`; delete dead code (anti-pattern: lava flow).
- Security-review the new path (`@rules/workflow-threat-model.md`); monitor both systems and
  error budgets throughout (`@rules/topic-reliability.md`).

## References
- "StranglerFigApplication" (Fowler); *Working Effectively with Legacy Code* (Feathers).
  Index: `@rules/reference-style-guides.md`.
