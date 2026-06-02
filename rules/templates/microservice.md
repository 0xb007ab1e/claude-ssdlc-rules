# Template: Microservice / Event-Driven Service — project CLAUDE.md

For a service in a distributed system (sync API and/or async messaging). Copy to the
project's root `CLAUDE.md`. Inherits the master automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-go.md                # or lang-java / lang-python / lang-csharp
@~/.claude/rules/std-owasp.md
@~/.claude/rules/std-owasp-api.md          # sync API surface
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-api-design.md       # contracts & versioning
@~/.claude/rules/topic-event-driven.md     # queues/streams, idempotent consumers, DLQs
@~/.claude/rules/topic-authn-authz.md
@~/.claude/rules/topic-reliability.md      # timeouts, retries, circuit-breakers, SLOs
@~/.claude/rules/topic-database.md
@~/.claude/rules/topic-logging-observability.md  # correlation IDs across services
@~/.claude/rules/topic-config-environments.md
@~/.claude/rules/std-zero-trust.md         # mTLS, per-request authZ between services
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-threat-model.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-multi-tenancy.md # if multi-tenant
# @~/.claude/rules/topic-webhooks.md      # if integrating via webhooks
# @~/.claude/rules/topic-nosql.md         # if using a non-relational store
# @~/.claude/rules/topic-api-consumption.md  # if it calls other/3rd-party services

## Stack
- Transport: <REST / gRPC>; messaging: <Kafka / SQS / NATS>; data store: <... (own its data)>
- Runtime: <containers / K8s — see @~/.claude/rules/topic-container-k8s.md>

## Project-specific rules
- **Owns its data:** no shared databases across services; integrate via API/events only.
- **Service identity + mTLS** between services; per-request authZ, not network trust
  (`@rules/std-zero-trust.md`).
- Versioned API + event contracts; backward-compatible changes; consumer-driven contract
  tests (master §4).
- Idempotent handlers; bounded resources; graceful shutdown/draining; health & readiness probes.
- Propagate a correlation/trace ID through every call and message for end-to-end tracing.
```
