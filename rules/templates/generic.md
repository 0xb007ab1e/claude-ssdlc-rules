# Template: Generic / Blank Starter — project CLAUDE.md

A minimal starting point when no specific template fits. Copy to the project's root
`CLAUDE.md`, then add the language + standard + workflow modules that apply. Inherits the
master SSDLC ruleset automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
# --- Language (pick one or more) ---
@~/.claude/rules/lang-<python|typescript|go|rust|java|csharp|cpp|shell|ruby|php>.md

# --- Always sensible for code projects ---
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/topic-testing.md
@~/.claude/rules/topic-error-handling.md
@~/.claude/rules/topic-defensive-programming.md
@~/.claude/rules/topic-anti-patterns.md

# --- Add as relevant ---
# @~/.claude/rules/std-owasp.md             # web/app surface
# @~/.claude/rules/std-owasp-api.md         # exposes an API
# @~/.claude/rules/std-owasp-llm.md         # uses LLMs/agents
# @~/.claude/rules/topic-authn-authz.md     # has auth
# @~/.claude/rules/topic-cryptography.md    # does crypto
# @~/.claude/rules/topic-logging-observability.md
# @~/.claude/rules/topic-web-frontend.md    # browser UI
# @~/.claude/rules/topic-iac-cloud.md       # ships infra
# @~/.claude/rules/std-privacy.md           # handles personal data
# @~/.claude/rules/std-pci.md               # handles cardholder data
# @~/.claude/rules/std-soc2.md / std-iso27001.md / std-nist.md  # compliance context
# @~/.claude/rules/workflow-threat-model.md # new service / significant design
# @~/.claude/rules/topic-multi-tenancy.md   # multi-tenant SaaS
# @~/.claude/rules/topic-webhooks.md        # sends/receives webhooks
# @~/.claude/rules/topic-realtime.md        # WebSocket/SSE/streaming
# @~/.claude/rules/topic-nosql.md           # non-relational data store
# @~/.claude/rules/topic-model-serving.md   # serves ML models
# @~/.claude/rules/topic-token-optimization.md  # calls LLM APIs (cost/latency)
# @~/.claude/rules/topic-license-compliance.md  # OSS license obligations (esp. distributed code)
# @~/.claude/rules/topic-resource-management.md  # disposal/leaks/shutdown; esp. native/long-running
# @~/.claude/rules/topic-concurrency.md      # threads/async/shared state
# @~/.claude/rules/topic-state-management.md # stateful lifecycle / state machines
# @~/.claude/rules/topic-numeric-correctness.md  # money, floats, overflow, time/clocks
# @~/.claude/rules/topic-dependency-injection.md   # IoC / injecting collaborators
# @~/.claude/rules/topic-architecture-patterns.md  # functional core, hexagonal/clean layering
# @~/.claude/rules/topic-api-consumption.md   # calls third-party APIs
# @~/.claude/rules/topic-notifications.md      # sends email/SMS/push
# @~/.claude/rules/topic-migration.md          # replacing/modernizing a legacy system
# @~/.claude/rules/topic-local-dev.md          # team project — reproducible local setup
# --- Deployable services should also add: workflow-release, workflow-incident-response,
#     workflow-runbooks ---

## Project-specific rules
- Data classification: <what sensitive data, if any>
- <anything unique to this project; deviations from defaults with justification>
```

> See `~/.claude/rules/README.md` for the full module catalog.
