# Topic: Documentation Standards

The standards behind the master §1 docs mandate. Docs are part of "done"; treat them as code
(reviewed, versioned, kept current).

## Per-symbol API docs (the mandate)
- Every public class/function/method has a doc comment: purpose, parameters, return, errors/
  exceptions raised, side effects, and a usage example. Use the language's doc tool (docstrings,
  TSDoc, godoc, rustdoc, Javadoc, XML-doc — see the `lang-*` modules).
- **Generate HTML `docs/` pages** from these and cross-link them. Examples should compile/run
  (doctests where the language supports it). Doc build runs in CI; broken links fail.
- **Enforce the docstring mandate mechanically** — a linter rule fails the build on undocumented
  public symbols, so "every public symbol documented" is checked, not just asserted (master §1):

  | Language | Linter rule |
  |---|---|
  | Python | ruff `D` (pydocstyle) |
  | TypeScript/JS | eslint-plugin-jsdoc `require-jsdoc` + eslint-plugin-tsdoc |
  | Go | `revive` `exported` rule / staticcheck ST1000 (via golangci-lint) |
  | Rust | `#![warn(missing_docs)]` (deny in CI) |
  | Java/Kotlin | Checkstyle `MissingJavadoc*` / detekt `UndocumentedPublic*` |
  | C# | `<GenerateDocumentationFile>` + treat CS1591 as error |
  | C/C++ | Doxygen `WARN_IF_UNDOCUMENTED=YES`, warnings as errors |
  | Ruby | RuboCop `Style/Documentation` |
  | PHP | phpcs `Squiz.Commenting.FunctionComment` |
  | Swift | SwiftLint `missing_docs` |
  | Scala | scalastyle `ScalaDocChecker` |

  Generated HTML need not be committed (build/publish in CI) — see master §1 proportionality.

## Repository docs
- **README** — what it is, quickstart (install/run/test), and where to go next. The front door.
- **Architecture Decision Records (ADRs)** — one short, immutable record per significant
  decision: context, decision, alternatives, consequences. Append, don't rewrite history.
- **Runbooks** — operational procedures: deploy, rollback, on-call response, common incidents
  (link from alerts — `@rules/workflow-incident-response.md`).
- **CHANGELOG** — human-readable, Keep-a-Changelog style, updated per release
  (`@rules/workflow-release.md`); driven by Conventional Commits where automated.
- **SECURITY.md** — vulnerability reporting + disclosure (`@rules/workflow-vuln-mgmt.md`).
- **CONTRIBUTING / threat model / data-flow** docs as applicable
  (`@rules/workflow-threat-model.md`).

## Quality
- Docs live in VCS beside the code and are updated **in the same PR** as the change — no
  "docs later." Stale docs are a defect.
- Diagrams as code (Mermaid/PlantUML) so they version and diff. Prefer concise, current, and
  accurate over exhaustive and rotting. Write for the reader's task, not the writer's model.

## References
- **Diátaxis** documentation framework — diataxis.fr; **Arc42** (architecture docs) — arc42.org.
- **ADRs** (Nygard) — adr.github.io; **Keep a Changelog** — keepachangelog.com; **C4 model** — c4model.com.
- Index: `@rules/reference-style-guides.md`.
