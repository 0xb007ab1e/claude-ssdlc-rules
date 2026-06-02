# Topic: Webhooks

For sending and receiving HTTP callbacks. Both directions have specific security and
reliability requirements. Pairs with `@rules/std-owasp-api.md`, `@rules/topic-reliability.md`,
`@rules/topic-event-driven.md`.

## Receiving webhooks (you are the endpoint)
- **Verify authenticity** of every inbound webhook: HMAC signature over the raw body with a
  shared secret (constant-time compare — `@rules/topic-cryptography.md`), or mTLS/OAuth per the
  provider. Reject unsigned/invalid. Never trust the payload's claimed identity alone.
- **Use the raw body** for signature verification (parsing/re-serializing changes bytes and
  breaks the HMAC). Verify *before* processing.
- **Replay protection:** include and check a timestamp (reject stale, e.g. >5 min) and/or a
  nonce/event-ID; dedupe by event ID — providers retry, so handlers must be **idempotent**
  (`@rules/topic-event-driven.md`).
- **Treat the payload as untrusted input** — validate against a schema; don't let it drive
  SSRF/injection (`@rules/std-cwe.md`, `@rules/std-owasp-api.md` API10).
- **Respond fast (2xx) then process async:** ack quickly, enqueue the work; long processing in
  the handler causes provider timeouts + retries. Bound handler time.
- Scope the endpoint: rate-limit, size-limit, and authenticate; one secret per provider, rotatable.

## Sending webhooks (you are the source)
- **Sign outbound payloads** (HMAC over body) so receivers can verify; document the scheme,
  include a timestamp, and support **secret rotation** (overlap window — `@rules/workflow-secrets.md`).
- **Retry with exponential backoff + jitter** on non-2xx/timeout, capped; after max attempts,
  dead-letter and alert. Make deliveries idempotent (stable event ID) so receiver retries are safe.
- **SSRF defense:** customer-supplied callback URLs are an SSRF vector — allow-list schemes
  (https only), block internal/metadata IPs and private ranges, resolve+validate the host, and
  don't follow redirects to internal targets (`@rules/std-owasp-api.md` API7/SSRF).
- Provide delivery logs/status and a replay mechanism; let customers rotate their endpoint secret.
- Send the minimum data (or just an ID to fetch) — avoid pushing sensitive data to external URLs
  (master §5).

## References
- Provider webhook security docs (e.g. Stripe/GitHub) as reference implementations.
  Index: `@rules/reference-style-guides.md`.
