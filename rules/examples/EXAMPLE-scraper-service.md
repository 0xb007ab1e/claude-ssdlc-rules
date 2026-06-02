# EXAMPLE (dogfood) — Multi-tenant LLM Scraper Service · project CLAUDE.md

> A worked example composing the ruleset for a real project (the scraping SaaS): a multi-tenant
> Python service that crawls target sites and uses an LLM to extract structured data. Not a
> template — a reference composition used to validate that the modules read coherently together.
> Started from `templates/web-scraper-crawler.md`, trimmed/added per `workflow-bootstrap.md`.

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-python.md
@~/.claude/rules/std-owasp-llm.md             # LLM extraction — injection, output handling
@~/.claude/rules/topic-token-optimization.md  # LLM cost at scale
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-reliability.md         # per-host backoff, circuit-break, idempotent jobs
@~/.claude/rules/topic-api-consumption.md     # target sites + LLM API are untrusted upstreams
@~/.claude/rules/topic-multi-tenancy.md       # SaaS tenant isolation
@~/.claude/rules/topic-database.md
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/std-privacy.md               # scraped data may contain PII
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/topic-testing.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-threat-model.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/workflow-cve-management.md

## Project-specific rules
- **Data classification:** scraped content = confidential (may contain PII); per-tenant isolation
  with tenant-scoped storage and cache keys.
- **Moat — Silent Corruption Rate:** extractor outputs are schema-validated and monitored for
  drift; on layout change, flag/quarantine rather than emit wrong data; SCR is a first-class SLO.
- **Legality:** honor robots.txt/ToS; per-host rate limits; honest User-Agent + contact.
- **Token spend:** prompt-cache the extraction system prompt; route simple pages to a small model;
  trim page HTML before the LLM — but never below the accuracy bar (correctness > tokens).
