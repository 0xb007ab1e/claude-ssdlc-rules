# Template: API Gateway / BFF — project CLAUDE.md

For an edge gateway or Backend-for-Frontend that fronts internal services. Copy to the
project's root `CLAUDE.md`. Inherits the master automatically.

```markdown
# <GatewayName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-go.md                # or lang-typescript
@~/.claude/rules/std-owasp.md
@~/.claude/rules/std-owasp-api.md          # primary surface: it IS the API edge
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-api-design.md
@~/.claude/rules/topic-authn-authz.md      # central authN; token validation/exchange
@~/.claude/rules/topic-reliability.md      # timeouts, retries, circuit-breakers per upstream
@~/.claude/rules/topic-caching.md
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/std-zero-trust.md         # mTLS to upstreams; don't trust the network
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-threat-model.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-realtime.md      # if proxying WebSocket/SSE
# @~/.claude/rules/topic-webhooks.md      # if handling inbound webhooks

## Stack
- Gateway: <Kong / Envoy / APIM / custom>; upstreams: <list services>

## Project-specific rules
- **Single enforcement point, not the only one:** terminate TLS, authenticate, and rate-limit
  at the edge — but upstreams still authorize per-request (defense in depth — `@rules/std-zero-trust.md`).
- **Don't trust client input or upstream output:** validate requests against the contract;
  treat upstream responses as untrusted (`@rules/std-owasp-api.md` API10).
- Per-route **rate limits, quotas, timeouts, and circuit breakers**; fail fast and shed load
  (`@rules/topic-reliability.md`); never let one slow upstream stall the gateway.
- Strict CORS + security headers (`@rules/topic-web-frontend.md`); consistent error shape
  (RFC 9457); propagate a correlation/trace ID to every upstream.
- BFF tailors/aggregates responses per client — minimize exposed data; no sensitive field
  pass-through (`@rules/std-owasp-api.md` API3).
- Secrets/keys for upstream auth from the secret manager (`@rules/workflow-secrets.md`).
```
