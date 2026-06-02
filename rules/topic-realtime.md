# Topic: Real-Time / Streaming Connections

For WebSocket, Server-Sent Events (SSE), long-polling, and gRPC streaming. Persistent
connections change the security and scaling model vs. request/response. Pairs with
`@rules/topic-authn-authz.md`, `@rules/topic-reliability.md`.

## Authentication & authorization
- **Authenticate at connect** and **re-check authorization per message/subscription** — a
  long-lived connection can outlive a token's validity or a permission change. Enforce token
  expiry on the open connection (disconnect/re-auth on expiry).
- WebSocket: don't rely on cookies alone (CSRF/cross-origin risk) — validate `Origin` and use a
  token in the handshake. Authorize each channel/topic a client subscribes to (tenant scope —
  `@rules/topic-multi-tenancy.md`).
- Use **WSS/HTTPS** always (`@rules/topic-cryptography.md`).

## Validation & abuse
- **Validate every inbound message** as untrusted (schema, size) — the connection is open, so
  the attack surface is continuous (`@rules/std-cwe.md`).
- **Rate-limit per connection and per message type**; cap message size, subscriptions, and
  connections per user/IP/tenant to prevent resource exhaustion (`@rules/std-owasp-api.md` API4).
- Authenticated connection ≠ trusted content — still encode/sanitize anything echoed to other
  clients (stored XSS via chat/presence — `@rules/topic-web-frontend.md`).

## Reliability & scale
- **Backpressure:** bound per-connection send buffers; drop/coalesce or slow producers when a
  client can't keep up — never grow buffers unboundedly (`@rules/topic-reliability.md`).
- **Reconnection:** clients reconnect with backoff + jitter; support resume (last-event-ID for
  SSE, sequence numbers) so no messages are silently lost. Assume connections drop constantly.
- **Heartbeats / ping-pong** to detect dead connections and reclaim resources; idle timeouts.
- **Horizontal scale:** connections are stateful — use a shared pub/sub backplane (Redis/NATS) to
  fan out across instances; sticky sessions or a connection-routing layer. Plan graceful drain on
  deploy (`@rules/workflow-release.md`) so reconnects rebalance.
- Prefer SSE for one-way server→client streams (simpler, HTTP-native); WebSocket for bidirectional.

## References
- MDN WebSocket/SSE; RFC 6455 (WebSocket); WHATWG SSE. Index: `@rules/reference-style-guides.md`.
