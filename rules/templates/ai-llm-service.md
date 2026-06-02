# Template: AI / LLM / Agent Service — project CLAUDE.md

For services that call LLMs, do RAG, or run autonomous agents/tools. Copy to the project's
root `CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-python.md            # or lang-typescript
@~/.claude/rules/std-owasp-llm.md          # prompt injection, output handling, excessive agency
@~/.claude/rules/topic-token-optimization.md  # cost/latency: prompt caching, routing, context trim
@~/.claude/rules/std-owasp-api.md          # the service is an API
@~/.claude/rules/std-owasp.md
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-authn-authz.md
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/std-privacy.md            # if user data reaches prompts/context
@~/.claude/rules/std-supplychain.md        # model/dataset/plugin provenance
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-threat-model.md  # treat agent autonomy as privilege escalation
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-model-serving.md # if you host/serve your own models
# @~/.claude/rules/topic-multi-tenancy.md # if multi-tenant SaaS
# @~/.claude/rules/topic-realtime.md      # if streaming responses (SSE/WebSocket)

## Stack
- Model(s)/provider: <Anthropic Claude / ...>; SDK: <...>
- Pattern: <chat / RAG / tool-using agent>; vector store: <...>

## Project-specific rules
- **Trust boundary:** model output + tool/retrieved content are untrusted — validate before
  use; never eval/exec/render unsanitized output.
- **Agency limits:** tools are least-privilege with typed/validated params; human approval
  required for <list irreversible/destructive actions>.
- **Limits:** max input size, output tokens, agent steps, tool calls, and per-user cost budget.
- **Data:** no secrets/PII in prompts or logs; redact retrieved content; data classification
  for the retrieval index.
- **Prompt-injection testing** is part of the security test suite.
```
