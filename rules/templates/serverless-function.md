# Template: Serverless Function — project CLAUDE.md

For FaaS (Lambda/Cloud Functions/Azure Functions/Workers). Copy to the project's root
`CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-typescript.md        # or lang-python / lang-go
@~/.claude/rules/topic-iac-cloud.md        # IAM least-privilege, deploy as code
@~/.claude/rules/std-owasp.md
@~/.claude/rules/std-owasp-api.md           # if HTTP-triggered
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-threat-model.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-webhooks.md      # if this is a webhook handler

## Stack
- Provider/runtime: <AWS Lambda / Cloud Functions / Workers>; trigger: <HTTP / queue / event>
- Deploy: <SAM / Serverless Framework / Terraform / CDK>

## Project-specific rules
- **Least-privilege execution role** scoped to exactly the resources this function uses; no
  wildcards. One role per function.
- Secrets from the cloud secret manager at runtime — never in env vars baked at deploy or in
  source (`@rules/workflow-secrets.md`).
- Validate every event payload as untrusted; set timeouts, memory, and concurrency limits to
  bound cost/DoS. Idempotent handlers (events can repeat).
- No long-lived state in the function; treat the filesystem as ephemeral.
- Structured logs to the platform sink with correlation IDs; redact PII.
```
