# Topic: API Design

Design conventions for public/internal APIs. Security is in `@rules/std-owasp-api.md`; this
is about contracts, consistency, and evolution.

## Contract-first
- Define the contract before implementing: **OpenAPI** (REST), **schema/SDL** (GraphQL), or
  **.proto** (gRPC). It's the source of truth; generate clients/servers/docs from it.
- Validate requests and responses against the contract at runtime.

## REST conventions
- Resource-oriented nouns, plural collections (`/orders/{id}`); correct HTTP methods
  (GET safe/idempotent, PUT/DELETE idempotent, POST for create/non-idempotent).
- Correct status codes (200/201/204, 400/401/403/404/409/422, 429, 5xx). Don't 200-with-error.
- **Pagination** on all collections (cursor/keyset preferred); filtering/sorting documented
  and bounded.
- **Idempotency keys** for non-idempotent POSTs so clients can safely retry
  (`@rules/topic-reliability.md`).
- Standardized **error format** — RFC 9457 (Problem Details): stable machine code + human
  message; never leak internals/stack traces (`@rules/std-owasp-proactive.md` #10).

## GraphQL specifics
- Depth/complexity/cost limits (DoS — `@rules/std-owasp-api.md` API4); avoid unbounded list
  fields; use pagination connections; object-level authZ on resolvers (BOLA).

## Versioning & evolution
- Version explicitly (URI `/v1` or header/media-type); **never break a published contract**
  without a new version. Additive changes only within a version.
- **Deprecation policy:** mark deprecated fields/endpoints, announce, set a sunset date
  (`Deprecation`/`Sunset` headers), maintain an API inventory (`@rules/std-owasp-api.md` API9).

## Consistency
- Consistent naming, casing, date format (ISO-8601 UTC), money (amount + currency code),
  pagination, and error shapes across all endpoints. Document everything (master §1 docs).

## References
- **Google API Design Guide / AIPs** — cloud.google.com/apis/design, aip.dev.
- **Microsoft REST API Guidelines** — github.com/microsoft/api-guidelines; **Zalando** guidelines.
- **RFC 9110** (HTTP), **RFC 9457** (Problem Details), **OpenAPI**, **AsyncAPI**. Index: `@rules/reference-style-guides.md`.
