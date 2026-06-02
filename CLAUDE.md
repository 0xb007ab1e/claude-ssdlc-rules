# Master Ruleset — Secure Software Development Lifecycle (SSDLC)

This file applies to **every** project for this user. Claude Code loads it automatically
on top of any project-local `CLAUDE.md`. It defines SSDLC at an **abstract level**;
granular rules live in `~/.claude/rules/*.md` and are pulled into each project's own
`CLAUDE.md` via `@import` (see "Composition" below).

**Conflict resolution:** the more specific file wins — project `CLAUDE.md` > subdirectory
`CLAUDE.md` > this master. A project may relax a default here only by stating so
explicitly and giving a reason; it may never relax the *non-negotiable mandates*.

---

## 1. Non-negotiable mandates (apply everywhere)
- **Git identity:** commit with the GitHub noreply email
  `134006168+0xb007ab1e@users.noreply.github.com`. Never the private address.
- **Documentation:** every public class/function carries a doc comment, and the project has a
  doc system that renders them to browsable, cross-linked pages. Docs are part of "done," not an
  afterthought. **Proportionality:** the requirement is *current, complete source docs + a
  configured generator* (rustdoc/godoc/TSDoc/pdoc/mkdocstrings, etc.) — committing generated HTML
  is optional and usually *not* desired (build it in CI / publish on release). Scale prose depth
  to project size: a small tool needs docstrings + README; a large system adds architecture/ADRs
  (`@rules/topic-documentation.md`).
- **Parallel-edit atomicity:** never let more than one parallel runner/agent touch the
  same file in the same batch. Serialize items that share a file.
- **No secrets in code or VCS.** Secrets come from a vault/KMS or injected env at runtime.
- **Security gates are merge-blocking.** A change that fails SAST/SCA/secret-scan/tests
  is not "done" and must not merge.
- **Verify generated & third-party code.** AI-generated, copied, or dependency code is
  reviewed and tested like any other — never trusted blindly. Confirm it compiles, passes
  the gates, and contains no insecure patterns or hallucinated/typosquatted dependencies
  before it lands.

---

## 2. Design & architecture principles
- **SOLID** — Single-responsibility, Open/closed, Liskov substitution, Interface
  segregation, Dependency inversion. Apply pragmatically; cite the principle when a
  refactor is motivated by it.
- **Separation of concerns & high cohesion / low coupling.** Business logic must not
  depend on transport, framework, or persistence details (ports & adapters / hexagonal).
- **Least privilege & secure-by-default.** Every component, credential, and config starts
  with the minimum rights and the safe default; opt *in* to power, never opt out of safety.
- **Fail closed.** On error or ambiguity, deny/abort rather than proceed insecurely.
- **Defense in depth.** Never rely on a single control; assume any one layer can fail.
- **Complete mediation.** Validate/authorize on every access, server-side, every time —
  never trust client-side checks or cached authorization.
- **Minimize attack surface.** Fewer endpoints, dependencies, and privileges; remove dead
  code and unused features.
- **Idempotency & explicitness** over hidden side effects; prefer pure functions and
  immutable data where practical.
- **12-Factor** for services: config in env, stateless processes, logs as event streams,
  dev/prod parity.
- **Structure & wiring:** isolate pure business logic from I/O (functional core / imperative
  shell, ports & adapters) — `@rules/topic-architecture-patterns.md`; depend on abstractions and
  inject them — `@rules/topic-dependency-injection.md`; recognize and refactor smells —
  `@rules/topic-anti-patterns.md`.

---

## 3. Secure SDLC phases (what's required in each)
1. **Requirements** — capture security & privacy requirements and data classification
   alongside functional ones. Identify regulated data (PII/PHI/cardholder) up front.
2. **Design** — threat-model new services/significant changes (STRIDE) before coding;
   document trust boundaries and mitigations. See `@rules/workflow-threat-model.md`.
3. **Implementation** — follow language + standard rule modules; secure defaults; input
   validation and output encoding at every boundary.
4. **Verification** — testing gates in §4; SAST/DAST/SCA; security review of the diff.
5. **Release** — signed artifacts, SBOM, provenance; reproducible builds where feasible.
   See `@rules/std-supplychain.md` and `@rules/workflow-cicd.md`.
6. **Operate & respond** — monitoring, secret rotation, vulnerability & patch SLAs.
   See `@rules/workflow-vuln-mgmt.md`.

---

## 4. Testing mandates (definition of "done")
- **Coverage gate (CI-enforced):** **100% on critical paths** (authentication,
  authorization, cryptography, payments, data handling), **≥90% line and ≥90% branch**
  elsewhere. Coverage may not regress on a PR.
  - *Enforcement note:* a single repo-wide `--cov-fail-under=90` (or equivalent) is the
    baseline; the **100%-critical** part needs more than one number — designate the critical
    modules/paths and enforce per-path (separate higher-threshold check / per-package or
    per-file fail-under / coverage groups). If a project has **no** critical paths, say so
    (the 90% baseline applies) — don't claim 100%-critical vacuously. See `@rules/topic-testing.md`.
- **End-to-end suite** covering primary user journeys; must pass before release.
- **Regression test for every bug:** reproduce the defect with a failing test *first*,
  then fix until green.
- **Security tests:** negative/abuse-path tests, authz-bypass attempts, fuzzing for
  parsers/decoders, and dependency + container scans run as gates.
- **Mutation testing** to validate test quality on critical modules; **contract tests**
  for every service boundary / public API.
- Tests are deterministic and hermetic — no reliance on network, wall-clock, or shared
  mutable state. No production data in tests.
- **Test strategy, the pyramid, test-data management, and property/mutation/contract patterns:**
  `@rules/topic-testing.md` (language specifics live in the `lang-*` modules).

---

## 5. Data protection (encryption / redaction / isolation)
- **In transit:** TLS 1.2+ (prefer 1.3) for all network traffic, including internal
  service-to-service. No plaintext protocols.
- **At rest:** AES-256 (or equivalent) for stored sensitive data; full-disk encryption is
  not sufficient on its own for regulated data.
- **Key management:** keys live in a KMS/HSM, never in code/config; enforce rotation and
  separation of duties. See `@rules/workflow-secrets.md`.
- **Data classification** (public / internal / confidential / restricted) drives handling;
  label data and let the label dictate encryption, retention, and access rules.
- **Redaction by default:** PII/PHI/secrets are scrubbed from logs, traces, metrics, and
  error reports. Logging sensitive fields requires an explicit allow-list and justification.
- **Isolation:** least-privilege data access; tenant/environment isolation (logical at
  minimum, physical when required by classification); **never copy production data into
  non-production** without irreversible anonymization.
- **Minimize & expire:** collect the least data needed; define and enforce retention.

---

## 6. Composition — how projects inherit & apply granular rules
Application is **native `@import`**: a project's root `CLAUDE.md` imports only the modules
relevant to its stack. When scaffolding a project, generate its `CLAUDE.md` from the
matching template in `~/.claude/rules/templates/` and follow `@rules/workflow-bootstrap.md`.

**Import lean.** Every imported module is loaded into context *every session* — importing the
whole catalog is both noise and token cost (counter to `@rules/topic-token-optimization.md`).
Pull in only what genuinely applies: a simple library/CLI needs ~6–10 modules; a rich
multi-tenant service legitimately needs ~15–20 (the worked example in `rules/examples/` imports
18 ≈ 10K tokens of always-on context). The discipline is **deliberate selection and pruning**,
not a hard cap — start from the template's set, add a module when a real need appears, remove
ones that don't fit. Breadth lives in this catalog; a project's `CLAUDE.md` is a focused
selection, never a copy of it.

Example — a Python web service handling personal data:
```
# <ProjectName> — project rules (inherits ~/.claude/CLAUDE.md automatically)
@~/.claude/rules/lang-python.md
@~/.claude/rules/std-owasp.md
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-privacy.md
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-threat-model.md

## Project-specific rules
- <anything unique to this project>
```

### Universal workflow modules (loaded globally here)
@rules/workflow-git.md
@rules/workflow-secrets.md

### Module catalog (import per project as needed)
**Languages:** `lang-python` · `lang-typescript` · `lang-go` · `lang-rust` · `lang-java`
· `lang-csharp` · `lang-cpp` · `lang-shell` · `lang-ruby` · `lang-php` · `lang-swift`
· `lang-kotlin` · `lang-scala` · `lang-sql`
**Standards:** `std-owasp` (Top 10 + ASVS) · `std-owasp-api` (API Top 10)
· `std-owasp-llm` (LLM Top 10) · `std-owasp-proactive` · `std-cwe` (Top 25)
· `std-nist` (SSDF 800-218 + 800-53) · `std-cis` · `std-pci` · `std-supplychain` (SLSA)
· `std-iso27001` · `std-soc2` · `std-privacy` (GDPR/HIPAA/CCPA) · `std-zero-trust` (800-207)
· `std-owasp-masvs` (mobile) · `std-samm` · `std-fedramp` · `std-hitrust` · `std-csa-ccm`
· `std-mitre-attack`
**Topics:** `topic-authn-authz` · `topic-cryptography` · `topic-logging-observability`
· `topic-iac-cloud` · `topic-container-k8s` · `topic-web-frontend` · `topic-reliability`
· `topic-accessibility` · `topic-performance` · `topic-caching` · `topic-database`
· `topic-i18n` · `topic-api-design` · `topic-event-driven` · `topic-config-environments`
· `topic-documentation` · `topic-testing` · `topic-error-handling` · `topic-multi-tenancy`
· `topic-webhooks` · `topic-realtime` · `topic-nosql` · `topic-model-serving`
· `topic-license-compliance` · `topic-resource-management` · `topic-defensive-programming`
· `topic-concurrency` · `topic-state-management` · `topic-numeric-correctness`
· `topic-dependency-injection` · `topic-architecture-patterns` · `topic-anti-patterns`
· `topic-token-optimization` · `topic-api-consumption` · `topic-notifications`
· `topic-migration` · `topic-local-dev`
**Workflows:** `workflow-git` · `workflow-cicd` · `workflow-threat-model`
· `workflow-secrets` · `workflow-vuln-mgmt` · `workflow-cve-management` · `workflow-code-review`
· `workflow-release` · `workflow-incident-response` · `workflow-data-lifecycle`
· `workflow-runbooks` · `workflow-bootstrap`
**Templates:** `templates/python-web-service` · `templates/typescript-service`
· `templates/cli-tool` · `templates/library` · `templates/ai-llm-service`
· `templates/web-frontend-spa` · `templates/serverless-function` · `templates/data-pipeline`
· `templates/infrastructure-repo` · `templates/generic` · `templates/web-scraper-crawler`
· `templates/ml-training-pipeline` · `templates/mobile-app` · `templates/microservice`
· `templates/browser-extension` · `templates/desktop-app` · `templates/monorepo`
· `templates/batch-job` · `templates/static-site` · `templates/api-gateway`
· `templates/data-science-notebook` · `templates/embedded-firmware`
**Reference:** `reference-style-guides` (industry style/design/security guide index, cited
per-module).
**Runbooks:** `runbooks/` — copy-ready operational runbooks (deploy, rollback,
incident-response, backup-restore, on-call, scaling, secret-rotation, dependency-patch);
mandated and indexed by `workflow-runbooks`.

See `~/.claude/rules/README.md` for the full index and authoring conventions.

---

## 7. Severity & risk taxonomy (shared vocabulary)
Rate security findings and bugs consistently; this drives remediation SLAs
(`@rules/workflow-vuln-mgmt.md`) and gate decisions.

- **Critical** — CVSS ≥ 9.0, or actively exploited, or full compromise / mass data loss.
  Fix/mitigate in **24–72h**; blocks release.
- **High** — CVSS 7.0–8.9; significant exposure (authz bypass, sensitive data exposure).
  Fix in **7 days**; blocks merge of the affected change.
- **Medium** — CVSS 4.0–6.9; limited or conditional impact. Fix in **30 days**.
- **Low** — CVSS < 4.0; minimal impact / defense-in-depth. Next maintenance window.
- **Informational** — hardening suggestions, no direct risk.

Risk = likelihood × impact. When uncertain, **rate up**, not down. Any accepted risk is
documented, owned, and time-boxed (no permanent ignores).

---

## 8. Definition of "Done" (consolidated checklist)
A change is done only when **all** of these hold (the granular rules expand each):

- [ ] Meets the security & functional requirements; data classified and handled per §5.
- [ ] Design threat-modeled if it adds/changes a trust boundary (`@rules/workflow-threat-model.md`).
- [ ] Code follows the applicable language + standard modules; secure-by-default.
- [ ] Tests pass and meet the §4 gates (100% critical / ≥90% line+branch; no regression;
      E2E + security/abuse tests; new regression test for any bug fixed).
- [ ] Lint/format/type-check clean; CI security gates green (SAST/DAST/SCA/secret/IaC/image —
      `@rules/workflow-cicd.md`).
- [ ] No secrets committed; sensitive data redacted from logs/telemetry.
- [ ] Docs updated — `docs/` pages for new/changed classes & functions (mandate §1).
- [ ] Reviewed via PR (`@rules/workflow-git.md`); security-focused review if security-relevant.
- [ ] Dependencies vetted/pinned; SBOM/provenance for releases (`@rules/std-supplychain.md`).
- [ ] Generated/third-party code verified, not trusted blindly (mandate §1).

---

## 9. Glossary (shared terms used across modules)
- **Trust boundary** — any point where data or control crosses between zones of different
  privilege, ownership, or trust (e.g. internet→service, service→service, tenant→tenant,
  user-input→parser). Every boundary requires authentication, authorization, and input
  validation. Identified during threat modeling (`@rules/workflow-threat-model.md`).
- **Fail closed / fail safe** — on error or ambiguity, deny and stop in a safe state rather
  than proceeding (`@rules/topic-error-handling.md`).
- **Least privilege** — every identity/component/credential gets the minimum access needed,
  for the minimum time.
- **Defense in depth** — multiple independent controls so no single failure is catastrophic.
- **Data classification** — public / internal / confidential / restricted; the label drives
  encryption, access, logging, redaction, and retention (§5).
- **SLI / SLO / error budget** — service-level indicator/objective and the allowance for
  unreliability that gates change vs. hardening (`@rules/topic-reliability.md`).
- **SBOM** — Software Bill of Materials; the component inventory used for CVE impact analysis
  (`@rules/std-supplychain.md`, `@rules/workflow-cve-management.md`).
- **VEX** — Vulnerability Exploitability eXchange; a statement of whether a CVE actually
  affects you (`@rules/workflow-cve-management.md`).
- **Idempotency** — an operation safely repeatable with the same effect; required for retries
  and at-least-once delivery (`@rules/topic-reliability.md`, `@rules/topic-event-driven.md`).
- **Tenant** — an isolated customer/account in shared infrastructure
  (`@rules/topic-multi-tenancy.md`).
