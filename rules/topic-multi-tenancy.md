# Topic: Multi-Tenancy

For SaaS serving multiple customers (tenants) from shared infrastructure. **Tenant isolation
is a security boundary** — a cross-tenant data leak is a critical incident. Builds on master §5,
`@rules/topic-database.md`, and `@rules/std-zero-trust.md`.

## Isolation models (choose deliberately, document it)
- **Silo** (per-tenant DB/instance) — strongest isolation, highest cost/ops; for high-compliance
  or large tenants.
- **Pool** (shared schema, `tenant_id` column) — efficient, but isolation depends entirely on
  query discipline — highest leak risk.
- **Bridge** (shared DB, schema/table per tenant) — middle ground.
- Often hybrid: pool by default, silo for premium/regulated tenants. Record each tenant's tier.

## Enforce isolation (defense in depth)
- **Every query is tenant-scoped.** Never rely on the app remembering to add `WHERE tenant_id` —
  enforce in the DB with **Row-Level Security**, a scoped connection/role, or a repository layer
  that injects the tenant filter centrally. App-only scoping is one bug away from a breach.
- **Tenant context** is derived server-side from the authenticated principal — **never** from a
  client-supplied tenant ID (that's BOLA — `@rules/std-owasp-api.md`). Propagate it through the
  request and every downstream call/event (`@rules/topic-event-driven.md`).
- **Test for cross-tenant access** explicitly: attempt tenant A's IDs as tenant B in the security
  suite (`@rules/topic-testing.md`). This is a required negative test.

## Data, keys & caching
- **Per-tenant encryption keys** for restricted data where required (crypto-shredding enables
  per-tenant deletion — `@rules/topic-cryptography.md`, `@rules/workflow-data-lifecycle.md`).
- **Cache keys include the tenant** — never serve one tenant's cached data to another
  (`@rules/topic-caching.md`). Same for search indexes and rate-limit buckets.
- **Logs/metrics carry tenant ID** (for support/billing) but still redact PII
  (`@rules/topic-logging-observability.md`).

## Operations
- **Noisy-neighbor protection:** per-tenant quotas, rate limits, and resource caps so one tenant
  can't degrade others (`@rules/topic-reliability.md`).
- Per-tenant observability (usage, errors, SLOs) for support and billing; tenant lifecycle:
  onboarding, suspension, **offboarding with full data export + deletion** (`@rules/std-privacy.md`).
- Migrations and deploys must be tenant-safe (no partial cross-tenant states).

## References
- AWS SaaS Lens (Well-Architected) / *Designing Multi-Tenant SaaS* guidance.
  Index: `@rules/reference-style-guides.md`.
