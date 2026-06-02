# Topic: Database & Data Layer

Schema, migration, and access discipline. Security of queries lives in the `lang-*` modules
(parameterization) and `@rules/std-owasp.md`; this covers structure, change, and operations.

## Schema design
- Model with integrity constraints in the DB (NOT NULL, FK, UNIQUE, CHECK) — don't rely only
  on app code. Normalize by default; denormalize deliberately for measured performance.
- Choose types deliberately (timestamps in UTC with tz, money as integer/decimal not float,
  UUID/identity for keys). Add a created/updated audit column convention.

## Migrations (zero-downtime, reversible)
- All schema changes are **versioned migrations in VCS**, reviewed like code; never hand-edit
  prod schemas.
- **Expand/contract pattern** for zero-downtime: add new (nullable/defaulted) → backfill in
  batches → switch reads/writes → drop old, across separate deploys. App and schema stay
  compatible at every step.
- Migrations are **forward-only in spirit** but reversible where feasible; test rollback.
  Avoid long locks (concurrent index builds; batch large backfills); set lock timeouts.
- Separate schema migration from data backfill; backfills are idempotent and resumable.

## Performance
- **Index for actual query patterns**; verify with `EXPLAIN`/query plans; watch for N+1
  (`@rules/topic-performance.md`). Don't over-index (write cost).
- Use **connection pooling** with sane limits; short transactions; avoid long-held locks.
- Paginate (keyset/cursor for large sets); avoid `SELECT *`.

## Security & operations
- **Least-privilege DB accounts** per service; no shared superuser; separate read/write roles.
- **Row-Level Security** / tenant scoping for multi-tenant data; enforce in the DB where
  possible, not just the app (`@rules/std-owasp-api.md` BOLA, `@rules/std-zero-trust.md`).
- Encrypt at rest + in transit; manage keys via KMS (`@rules/topic-cryptography.md`).
- **Backups + tested restores**, retention, and PITR for critical data
  (`@rules/topic-reliability.md`, `@rules/workflow-data-lifecycle.md`). No real prod data in
  non-prod (master §5).

## References
- **Use The Index, Luke!** — use-the-index-luke.com; your DB's official docs (PostgreSQL/MySQL).
- *Refactoring Databases* (Ambler/Sadalage) for evolutionary schema. Index: `@rules/reference-style-guides.md`.
