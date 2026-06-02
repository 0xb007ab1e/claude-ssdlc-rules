# Template: Batch Job / Cron Worker — project CLAUDE.md

For scheduled or queue-triggered background jobs (cron, workers, scheduled tasks). Copy to
the project's root `CLAUDE.md`. Inherits the master automatically.

```markdown
# <JobName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-python.md            # or lang-go / lang-typescript
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-reliability.md      # retries, idempotency, timeouts are essential
@~/.claude/rules/topic-database.md
@~/.claude/rules/topic-event-driven.md     # if queue/event triggered
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/topic-config-environments.md
@~/.claude/rules/std-privacy.md            # if it processes personal data
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-data-lifecycle.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md

## Stack
- Trigger: <cron / queue / scheduler (Airflow/Temporal/K8s CronJob)>; data: <...>

## Project-specific rules
- **Idempotent & resumable:** safe to run twice (schedulers double-fire); checkpoint progress;
  process in bounded batches; resume from last checkpoint on failure (`@rules/topic-reliability.md`).
- **Single-run guard:** prevent overlapping runs (locking) if a run can exceed its interval.
- **Bounded & observable:** set timeouts and resource limits; emit start/finish/duration/
  records-processed metrics and structured logs with a run ID; **alert on failure AND on
  silent non-execution** (a job that didn't run is an incident too).
- **Least privilege:** scoped credentials for exactly the data/resources it touches; secrets
  at runtime (`@rules/workflow-secrets.md`).
- **Graceful shutdown:** handle SIGTERM — finish or checkpoint the current batch, don't corrupt
  state. Partial-failure handling with dead-letter/retry, never silent drops.
```
