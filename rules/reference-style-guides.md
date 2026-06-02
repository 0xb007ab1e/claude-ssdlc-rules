# Reference: Industry Style, Design & Security Guides

Consolidated index of the authoritative external guides the rule modules build on. Each
language/design module also carries its own "References & style guides" section; this is the
single overview. Cite the relevant guide when justifying a convention.

## Language style guides
| Language | Canonical guides |
|---|---|
| Python | PEP 8 (peps.python.org/pep-0008), PEP 257 docstrings, PEP 484 typing; Google Python Style Guide (google.github.io/styleguide/pyguide.html) |
| TypeScript/JS | Google TS Style Guide (google.github.io/styleguide/tsguide.html), Airbnb JS Style Guide (github.com/airbnb/javascript), MDN JS |
| Go | Effective Go (go.dev/doc/effective_go), Go Code Review Comments (go.dev/wiki/CodeReviewComments), Google Go Style Guide (google.github.io/styleguide/go) |
| Rust | Rust API Guidelines (rust-lang.github.io/api-guidelines), Rust Style Guide (doc.rust-lang.org/style-guide), Clippy lints |
| Java/Kotlin | Google Java Style Guide (google.github.io/styleguide/javaguide.html), *Effective Java* (Bloch); Kotlin coding conventions (kotlinlang.org/docs/coding-conventions.html) |
| C# /.NET | Microsoft C# Coding Conventions + Framework Design Guidelines (learn.microsoft.com/dotnet/standard/design-guidelines) |
| C/C++ | C++ Core Guidelines (isocpp.github.io/CppCoreGuidelines), Google C++ Style Guide (google.github.io/styleguide/cppguide.html), CERT C/C++ Secure Coding (wiki.sei.cmu.edu) |
| Shell/Bash | Google Shell Style Guide (google.github.io/styleguide/shellguide.html), ShellCheck wiki |
| Ruby | Ruby Style Guide (rubystyle.guide), Rails guides (guides.rubyonrails.org) |
| PHP | PSR standards / PHP-FIG (php-fig.org), PHP The Right Way (phptherightway.com) |

## API & integration design
- **Google API Design Guide / AIPs** — cloud.google.com/apis/design, aip.dev
- **Microsoft REST API Guidelines** — github.com/microsoft/api-guidelines
- **Zalando RESTful API Guidelines** — opensource.zalando.com/restful-api-guidelines
- **RFC 9110** (HTTP semantics), **RFC 9457** (Problem Details for errors)
- **JSON:API** — jsonapi.org; **GraphQL** best practices — graphql.org/learn/best-practices
- **OpenAPI** — spec.openapis.org; **AsyncAPI** (event-driven) — asyncapi.com
- **CloudEvents** (event format) — cloudevents.io

## Security guides & cheat sheets
- **OWASP Cheat Sheet Series** — cheatsheetseries.owasp.org (auth, session, crypto storage,
  input validation, logging, etc.) — the practical companion to `std-owasp*`.
- **OWASP ASVS / API Top 10 / Top 10 / LLM Top 10 / MASVS / Proactive Controls / SAMM** —
  owasp.org. **CWE** — cwe.mitre.org. **MITRE ATT&CK / ATLAS** — attack.mitre.org, atlas.mitre.org.
- **NIST**: SSDF SP 800-218, SP 800-53, SP 800-207 (Zero Trust), SP 800-57/800-175B (key mgmt),
  SP 800-61 (incident handling) — csrc.nist.gov. **CIS Benchmarks/Controls** — cisecurity.org.
- **SLSA** — slsa.dev; **Sigstore** — sigstore.dev; **OpenSSF** — openssf.org.

## Architecture & design
- **The Twelve-Factor App** — 12factor.net
- **Domain-Driven Design** (Evans / Vernon); **Clean Architecture** / Hexagonal (Ports & Adapters)
- **C4 model** for architecture diagrams — c4model.com
- **Microsoft Azure Architecture Center / Well-Architected**; **AWS Well-Architected Framework**
- **Enterprise Integration Patterns** (Hohpe) — enterpriseintegrationpatterns.com (messaging)
- **Refactoring / code smells** (Fowler) — refactoring.com

## Reliability / SRE / operations
- **Google SRE books** — sre.google/books (SRE, SRE Workbook); SLO/error-budget practice.
- **Release It!** (Nygard) — resilience patterns (circuit breaker, bulkhead).
- **Keep a Changelog** — keepachangelog.com; **Semantic Versioning** — semver.org;
  **Conventional Commits** — conventionalcommits.org.
- **OpenTelemetry** — opentelemetry.io (logs/metrics/traces conventions).

## UI / UX design systems
- **Material Design 3** — m3.material.io (Android/web)
- **Apple Human Interface Guidelines** — developer.apple.com/design/human-interface-guidelines (iOS/macOS)
- **Microsoft Fluent / Fluent 2** — fluent2.microsoft.design (Windows/web)
- **WCAG 2.2** — w3.org/TR/WCAG22; **WAI-ARIA Authoring Practices (APG)** — w3.org/WAI/ARIA/apg
- **Refactoring UI** (Wathan/Schoger) — practical visual design for engineers
- **Nielsen's 10 Usability Heuristics** — nngroup.com

## Vulnerability & CVE sources
- **NVD** — nvd.nist.gov; **GitHub Advisories (GHSA)** — github.com/advisories;
  **OSV** — osv.dev; **CISA KEV** — cisa.gov/known-exploited-vulnerabilities-catalog;
  **EPSS** — first.org/epss; **CVSS** — first.org/cvss; **VEX/CSAF** — see `workflow-cve-management.md`.

> Modules cite these by name; treat the linked guide as the deeper "why" behind a rule. When a
> guide and a rule here conflict, the rule (and its security mandate) wins — note the deviation.
