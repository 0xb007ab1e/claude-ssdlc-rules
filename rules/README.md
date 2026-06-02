# SSDLC Rules Catalog

Granular, composable rule modules for the Secure Software Development Lifecycle. The
**abstract** rules live in `~/.claude/CLAUDE.md` (the master, loaded for every project);
these modules are the **specifics**, pulled into each project via `@import`.

## How it fits together
```
~/.claude/CLAUDE.md          # master: abstract SSDLC, loaded everywhere
   ├─ @import workflow-git    # universal, imported globally by master
   └─ @import workflow-secrets
~/.claude/rules/*.md          # this catalog: imported per project as needed
<repo>/CLAUDE.md              # project: @imports the modules for its stack + project rules
<repo>/sub/CLAUDE.md          # optional: subtree-specific rules (loaded on demand)
```
Precedence on conflict: **project > subdirectory > master**. Mandates in the master are
non-negotiable and cannot be relaxed by a project.

## Applying modules to a project
Use the native `@import` syntax in the project's root `CLAUDE.md`. Start from a template:

| Project kind | Template |
|---|---|
| Python web service | `templates/python-web-service.md` |
| TypeScript/Node service | `templates/typescript-service.md` |
| CLI tool | `templates/cli-tool.md` |
| Library / SDK | `templates/library.md` |
| AI / LLM / agent service | `templates/ai-llm-service.md` |
| Web frontend / SPA | `templates/web-frontend-spa.md` |
| Serverless function | `templates/serverless-function.md` |
| Data pipeline / ETL | `templates/data-pipeline.md` |
| Infrastructure (IaC) repo | `templates/infrastructure-repo.md` |
| Web scraper / crawler | `templates/web-scraper-crawler.md` |
| ML training pipeline (MLOps) | `templates/ml-training-pipeline.md` |
| Mobile app | `templates/mobile-app.md` |
| Microservice / event-driven | `templates/microservice.md` |
| Browser extension | `templates/browser-extension.md` |
| Desktop app | `templates/desktop-app.md` |
| Monorepo | `templates/monorepo.md` |
| Batch job / cron worker | `templates/batch-job.md` |
| Static site / JAMstack | `templates/static-site.md` |
| API gateway / BFF | `templates/api-gateway.md` |
| Data science / notebook | `templates/data-science-notebook.md` |
| Embedded / firmware | `templates/embedded-firmware.md` |
| Anything else (blank starter) | `templates/generic.md` |

Import paths use `~` (e.g. `@~/.claude/rules/lang-python.md`). Imports nest up to 5 levels.

## Catalog

### Languages (`lang-*`)
| Module | Use for |
|---|---|
| `lang-python` | Python services, scripts, tooling |
| `lang-typescript` | Node/TypeScript services & frontends |
| `lang-go` | Go services & CLIs |
| `lang-rust` | Rust services, CLIs, libraries |
| `lang-java` | Java/Kotlin (JVM) apps |
| `lang-csharp` | C#/.NET apps |
| `lang-cpp` | C/C++ (memory-safety focused) |
| `lang-shell` | Bash/shell scripts |
| `lang-ruby` | Ruby / Rails |
| `lang-php` | PHP / Laravel / Symfony |
| `lang-swift` | Swift (iOS/macOS) |
| `lang-kotlin` | Kotlin (Android / JVM) |
| `lang-scala` | Scala (Spark / JVM backends) |
| `lang-sql` | SQL query style & anti-patterns |

### Standards (`std-*`)
| Module | Scope |
|---|---|
| `std-owasp` | OWASP Top 10 + ASVS — any web app |
| `std-owasp-api` | OWASP API Security Top 10 — REST/GraphQL/gRPC APIs |
| `std-owasp-llm` | OWASP Top 10 for LLM Apps — LLM/RAG/agent systems |
| `std-owasp-proactive` | OWASP Proactive Controls — positive secure-coding patterns |
| `std-cwe` | CWE Top 25 — weakness checklist for review/SAST |
| `std-nist` | NIST SSDF (800-218) + 800-53 control families |
| `std-cis` | CIS Benchmarks & Controls — runtime/infra hardening |
| `std-pci` | PCI DSS — only when handling cardholder data |
| `std-supplychain` | SLSA + SSDF PS — build/release integrity, SBOM, signing |
| `std-iso27001` | ISO/IEC 27001/27002 — ISMS / certification context |
| `std-soc2` | SOC 2 Trust Services Criteria — SaaS audit context |
| `std-privacy` | GDPR / HIPAA / CCPA — personal data handling |
| `std-zero-trust` | NIST 800-207 — never-trust/always-verify architecture |
| `std-owasp-masvs` | OWASP MASVS — mobile app security |
| `std-samm` | OWASP SAMM — maturity assessment of the SDLC |
| `std-fedramp` | FedRAMP / FISMA — US federal cloud authorization (niche) |
| `std-hitrust` | HITRUST CSF — healthcare certification framework (niche) |
| `std-csa-ccm` | CSA Cloud Controls Matrix — cloud assurance + vendor assessment |
| `std-mitre-attack` | MITRE ATT&CK — detection engineering / adversary TTP mapping |

### Topics (`topic-*`) — cross-cutting concerns
| Module | Scope |
|---|---|
| `topic-authn-authz` | OAuth2/OIDC, sessions, JWT, RBAC/ABAC, MFA |
| `topic-cryptography` | Concrete algorithms, key sizes, deprecations, FIPS, agility |
| `topic-logging-observability` | Structured logs, audit trails, metrics/traces, alerting |
| `topic-iac-cloud` | IaC scanning + cloud hardening (IAM, network, encryption) |
| `topic-container-k8s` | Container image + Kubernetes hardening |
| `topic-web-frontend` | CSP, SRI, CORS, cookies, client-side XSS/CSRF |
| `topic-reliability` | SRE: SLOs, retries/backoff, circuit-breakers, DR, chaos testing |
| `topic-accessibility` | WCAG 2.2 AA — semantic HTML, ARIA, keyboard, contrast |
| `topic-performance` | Budgets, profiling, N+1, pagination, load testing, Web Vitals |
| `topic-caching` | Strategy, TTLs, invalidation, stampede protection, safe caching |
| `topic-database` | Schema, zero-downtime migrations, indexing, RLS, backups |
| `topic-i18n` | Internationalization/localization — UTF-8, ICU, locale formatting |
| `topic-api-design` | REST/GraphQL conventions, versioning, pagination, error format |
| `topic-event-driven` | Queues/streams, event schemas, idempotent consumers, DLQs |
| `topic-config-environments` | 12-Factor config, env parity/isolation, feature flags |
| `topic-documentation` | Doc standards — API docs, ADRs, runbooks, changelogs |
| `topic-testing` | Test strategy — pyramid, test data, flakiness, property/mutation/contract |
| `topic-error-handling` | Fail-closed, error taxonomy, retries vs fail-fast, safe disclosure |
| `topic-multi-tenancy` | Tenant isolation models, per-tenant keys/cache, noisy-neighbor |
| `topic-webhooks` | Inbound/outbound webhooks — HMAC verify, replay/idempotency, SSRF |
| `topic-realtime` | WebSocket/SSE — connection auth, backpressure, reconnect, scale |
| `topic-nosql` | Document/KV/wide-column/graph/time-series modeling + NoSQL injection |
| `topic-model-serving` | ML inference infra — versioning, batching, rollout, drift |
| `topic-license-compliance` | OSS license obligations (copyleft/AGPL), attribution, scanning |
| `topic-resource-management` | Disposal/RAII per language, leak classes, graceful shutdown, secret zeroization, memory safety |
| `topic-defensive-programming` | Guard clauses, fail-fast, assertions/contracts, complexity, magic numbers, illegal-states |
| `topic-concurrency` | Data races, TOCTOU, deadlock, lock discipline, atomics, structured concurrency |
| `topic-state-management` | Explicit state machines, valid transitions, single source of truth |
| `topic-numeric-correctness` | Money/decimal, floating-point, integer overflow, units, time/clock correctness |
| `topic-dependency-injection` | IoC, constructor injection, composition root, lifetimes, no service-locator |
| `topic-architecture-patterns` | Dependency rule, functional core/imperative shell, hexagonal/clean/onion |
| `topic-anti-patterns` | Code-smell & anti-pattern catalog for review/refactor |
| `topic-token-optimization` | LLM token/cost reduction — prompt caching, routing, context trim, batching; when to apply |
| `topic-api-consumption` | Consuming third-party APIs — timeouts/retries/circuit-break, schema-validate, pagination, SSRF |
| `topic-notifications` | Email/SMS/push — deliverability (SPF/DKIM/DMARC), idempotent sends, consent, no PII |
| `topic-migration` | Legacy migration — strangler-fig, parallel-run, anti-corruption layer, safe data migration |
| `topic-local-dev` | Reproducible local setup — devcontainers, task runner, pre-commit hooks, safe defaults |

### Workflows (`workflow-*`)
| Module | Scope |
|---|---|
| `workflow-git` | Trunk-based branching, signed commits, mandatory PR review *(global)* |
| `workflow-secrets` | Secret storage, rotation, detection *(global)* |
| `workflow-cicd` | CI/CD security gates (SAST/DAST/SCA/secret-scan, SBOM, signing) |
| `workflow-threat-model` | STRIDE threat modeling at design time |
| `workflow-vuln-mgmt` | Vulnerability monitoring, remediation SLAs, disclosure |
| `workflow-cve-management` | CVE intel — CVSS/EPSS/KEV scoring, OSV/GHSA/NVD, VEX, SBOM impact |
| `workflow-code-review` | Security + quality review checklist (what reviewers check) |
| `workflow-release` | SemVer, changelog, canary/blue-green, rollback, feature-flag rollout |
| `workflow-incident-response` | Severity, containment, recovery, blameless post-mortems |
| `workflow-data-lifecycle` | Classification, retention/deletion, backups + restore drills |
| `workflow-runbooks` | Runbook mandate + standard set (indexes `runbooks/`) |
| `workflow-bootstrap` | Procedure to start a new project (template → CLAUDE.md → docs/CI/runbooks) |

*(global)* = imported by the master, so already active in every project.

### Reference & runbooks
- **`reference-style-guides`** (`reference-style-guides.md`) — consolidated index of industry style, design, security, and
  architecture guides (PEP 8, Effective Go, Google/Airbnb, OWASP cheat sheets, NIST, WCAG,
  Material/HIG/Fluent, 12-Factor, Google SRE, CVE sources, …). Each language/design module also
  carries its own "References & style guides" section pointing here.
- **`runbooks/`** — copy-ready operational runbook templates (`_TEMPLATE` + deploy, rollback,
  incident-response, backup-restore, on-call, scaling, secret-rotation, dependency-patch).
  Copy into a project's `docs/runbooks/`; mandated and indexed by `workflow-runbooks`.

## Authoring conventions
- One concern per file; keep modules tight and actionable (rules, not essays).
- Cite the canonical guide (`reference-style-guides.md`) behind a convention; add a per-module
  "References" section for language/design modules.
- Cross-reference other modules with `@rules/<name>.md` so relationships are explicit.
- Mandate the **control**, not a specific tool (tool-agnostic); name tools only as examples.
- When adding a module, list it in this README and, if broadly useful, in the master's
  module catalog (§6).
- To add a new project kind, drop a `templates/<kind>.md` and add it to the table above.
- After any change, run `./check-rules.sh` (imports resolve + catalog/README/runbook sync).

## Maintenance & review
These rules cite specifics that **drift** — tool/LTS versions, CVSS thresholds, OWASP/NIST/WCAG
versions, provider behaviors (e.g. the Anthropic prompt-cache TTL). Keep them honest:
- **Review cadence:** revisit the ruleset **quarterly** (or when a cited standard releases a major
  version). Update the drift-prone specifics and re-run `check-rules.sh`.
- **Drift-prone spots to check:** language `lang-*` LTS/toolchain versions; `workflow-vuln-mgmt`
  CVSS/SLA numbers; `std-*` standard versions (OWASP Top 10, ASVS, WCAG, NIST baselines);
  `topic-token-optimization` provider features; remediation SLAs (master §7).
- **Last reviewed:** 2026-06-02. (Update this date each review.)
- Optional automation: a scheduled agent can diff cited versions against upstream and open a
  review note — wire via the user's scheduled-agent infra if desired.

> This ruleset is a living standard, not a finished artifact. Prefer pruning stale/over-specific
> content over accreting more — breadth already exists; correctness and currency are the work.
