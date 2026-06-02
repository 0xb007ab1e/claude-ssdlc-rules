# Template: Data Pipeline / ETL — project CLAUDE.md

For batch/stream data processing (ETL/ELT, Spark/Beam/dbt, Airflow/Dagster). Copy to the
project's root `CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-python.md            # or lang-scala / lang-java
@~/.claude/rules/std-privacy.md            # pipelines often move PII at scale
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-iac-cloud.md
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-nosql.md         # if reading/writing non-relational stores

## Stack
- Orchestrator: <Airflow / Dagster / Prefect>; engine: <Spark / Beam / dbt / SQL>
- Sources/sinks: <...>; storage/warehouse: <...>

## Project-specific rules
- **Data classification drives handling:** tag PII/PHI/restricted at the schema level;
  encrypt in transit/at rest; least-privilege access to each dataset (master §5).
- **Redaction/anonymization** before data leaves its trust zone or lands in analytics/logs;
  no real personal data in non-prod (pseudonymize/synthesize).
- **Data quality + integrity:** schema validation and quality checks as pipeline gates;
  idempotent, replayable steps; track lineage and provenance.
- Parameterize all queries; treat source data as untrusted input.
- Retention and deletion enforced per `@rules/std-privacy.md`; document data flows in the
  threat model for new pipelines (`@rules/workflow-threat-model.md`).
```
