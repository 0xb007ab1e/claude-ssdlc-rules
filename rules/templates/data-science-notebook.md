# Template: Data Science / Notebook Project — project CLAUDE.md

For analysis/experimentation projects (Jupyter, R, exploratory ML). Copy to the project's
root `CLAUDE.md`. Inherits the master automatically. (For production training pipelines use
`templates/ml-training-pipeline.md`; for batch data movement use `templates/data-pipeline.md`.)

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-python.md            # or R
@~/.claude/rules/std-privacy.md            # analysis data frequently contains PII
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-data-lifecycle.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md

## Stack
- Env: <Jupyter / VS Code / Colab>; libs: <pandas / numpy / scikit-learn / ...>

## Project-specific rules
- **No secrets/credentials in notebooks** — they get committed with output; load from env/
  secret store (`@rules/workflow-secrets.md`). **Clear cell outputs before commit** (outputs
  can leak data, tokens, and PII) — use a pre-commit hook (e.g. nbstripout).
- **No real personal data in shared notebooks:** classify, minimize, and pseudonymize
  (`@rules/std-privacy.md`, master §5); document data source + access basis.
- **Reproducibility:** pin dependencies (lockfile/`requirements.txt` + versions); set random
  seeds; record data snapshot/version. A result others can't reproduce isn't done.
- **Promote out of notebooks:** refactor reusable logic into tested modules
  (`@rules/lang-python.md` + master §4) before it becomes production; notebooks are for
  exploration, not pipelines.
- Treat input datasets as untrusted (parsing, formulas, deserialization — `@rules/std-cwe.md`).
- Retention/deletion of datasets per `@rules/workflow-data-lifecycle.md`.
```
