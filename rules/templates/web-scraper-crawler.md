# Template: Web Scraper / Crawler — project CLAUDE.md

For data-extraction services (crawlers, scrapers, extraction pipelines). Copy to the
project's root `CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-python.md            # or lang-typescript / lang-go
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-owasp-llm.md          # if using LLMs for extraction/parsing
# @~/.claude/rules/topic-token-optimization.md  # if LLM-based extraction (cost at scale)
@~/.claude/rules/topic-reliability.md      # retries/backoff/circuit-breakers are core here
@~/.claude/rules/topic-event-driven.md     # if queue-driven crawl frontier
@~/.claude/rules/topic-database.md
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/std-privacy.md            # scraped data may contain personal data
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-data-lifecycle.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-nosql.md         # if storing to a document/KV store

## Stack
- Fetch/render: <httpx / Playwright / headless Chromium>; queue: <...>; store: <...>

## Project-specific rules
- **Legality & politeness:** honor robots.txt and site ToS; respect rate limits and crawl
  delay; identify with an honest User-Agent + contact; obtain authorization for gated/
  authenticated targets. Document the legal basis for each source.
- **Resilience (core):** per-host rate limiting + backoff/jitter; circuit-break failing
  hosts; bounded concurrency; idempotent, resumable jobs; checkpoint the frontier.
- **Anti-bot handling** stays within ToS/authorization; throttle rather than evade where
  evasion would breach terms.
- **Data quality / self-healing (the moat):** selectors/extractors are versioned and
  monitored; on layout drift, detect and flag rather than silently emit wrong data. Track a
  **Silent Corruption Rate** (undetected-wrong outputs) as a first-class SLO; schema-validate
  every extracted record; quarantine + alert on anomalies before they reach customers.
- **Provenance:** record source URL, fetch timestamp, and extractor version per record.
- **Privacy:** classify scraped data; redact/minimize PII; honor retention/deletion
  (`@rules/workflow-data-lifecycle.md`); never store credentials of target sites in code.
```
