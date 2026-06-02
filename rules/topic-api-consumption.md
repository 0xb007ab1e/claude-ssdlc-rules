# Topic: Consuming Third-Party APIs

Calling someone else's API robustly. Treat every upstream as **unreliable and untrusted**.
Complements `@rules/topic-reliability.md` (patterns), `@rules/std-owasp-api.md` (API10 unsafe
consumption), and `@rules/topic-webhooks.md` (the inbound direction).

## Resilience (upstreams fail)
- **Timeouts** on connect and read — never unbounded. **Retries** with exponential backoff +
  jitter, only for idempotent calls and retryable statuses (429/503/timeout); cap attempts.
- **Respect `429`/`Retry-After`** and documented rate limits; throttle proactively; bound your
  own concurrency against them.
- **Circuit-break** a failing dependency; **fall back** (cache, default, degraded mode) instead
  of cascading the failure (`@rules/topic-reliability.md`).
- Isolate each dependency (bulkhead) so one slow upstream can't exhaust your pools.

## Correctness (don't trust the shape)
- **Validate/parse responses against a schema** — treat upstream output as untrusted input
  (injection/SSRF via reflected data — `@rules/std-owasp-api.md` API10, `@rules/std-cwe.md`).
  Handle empty/partial/unexpected payloads explicitly (`@rules/topic-error-handling.md`).
- **Pin the API version**; consume **all pages** (cursor/continuation); monitor for **contract
  drift** and deprecation notices. Write a thin client/anti-corruption layer so upstream changes
  don't ripple through your domain (`@rules/topic-architecture-patterns.md`).
- **Idempotency keys** on writes so your retries don't double-charge/double-create.

## Caching & cost
- Cache responses where valid (TTL + conditional requests / `ETag`); avoid redundant calls
  (`@rules/topic-caching.md`). Mind per-call cost and quota budgets.

## Security
- Verify TLS; **don't follow redirects to internal/metadata addresses** (SSRF); allow-list hosts
  for any user-influenced URL. Store API credentials in the secret manager, least scope, rotate
  (`@rules/workflow-secrets.md`). Never log full request/response with secrets/PII (master §5).

## Observability
- Trace and meter outbound calls per dependency (latency, error rate, retry count); define an SLO
  and **alert on upstream degradation** (`@rules/topic-logging-observability.md`). Surface
  upstream incidents in your own status.

## References
- Provider API docs + status pages; *Release It!* (Nygard); `@rules/reference-style-guides.md`.
