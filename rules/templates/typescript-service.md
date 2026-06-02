# Template: TypeScript/Node Service — project CLAUDE.md

Copy to a new project's root `CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-typescript.md
@~/.claude/rules/std-owasp.md
@~/.claude/rules/std-owasp-api.md
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-authn-authz.md
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/std-privacy.md          # if it handles personal data
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-threat-model.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-multi-tenancy.md # if multi-tenant SaaS
# @~/.claude/rules/topic-webhooks.md      # if sending/receiving webhooks
# @~/.claude/rules/topic-realtime.md      # if WebSocket/SSE
# @~/.claude/rules/topic-cryptography.md # if it does crypto beyond TLS/hashing
# @~/.claude/rules/std-soc2.md           # if under SOC 2 scope

## Stack
- Runtime: Node <LTS>; module system: ESM
- Framework: <Express / Fastify / NestJS / Next.js API>
- Data store: <...>; query layer: <Prisma / Drizzle / ...>
- Validation: <zod / valibot>

## Project-specific rules
- Data classification: <sensitive data handled, if any>
- API contract: <path/to/openapi.yaml or tRPC router>
- <deviations from defaults, with justification>
```
