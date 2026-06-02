# Template: Python Web Service — project CLAUDE.md

Copy this to a new project's root `CLAUDE.md` and fill in the project specifics. It inherits
`~/.claude/CLAUDE.md` (master SSDLC) automatically; the `@import` lines pull in the granular
modules for this stack.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-python.md
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
# @~/.claude/rules/topic-api-consumption.md  # if it calls third-party APIs
# @~/.claude/rules/topic-notifications.md    # if it sends email/SMS/push
# @~/.claude/rules/topic-cryptography.md # if it does crypto beyond TLS/hashing
# @~/.claude/rules/std-pci.md            # only if it touches cardholder data
# @~/.claude/rules/std-soc2.md           # if under SOC 2 scope

## Stack
- Framework: <FastAPI / Django / Flask>
- Data store: <Postgres / ...>; ORM: <SQLAlchemy / Django ORM>
- Runtime: <container / serverless>

## Project-specific rules
- Data classification: <what sensitive data, if any, this service handles>
- Public API contract lives in: <path/to/openapi.yaml>
- <any deviations from defaults, with justification>
```
