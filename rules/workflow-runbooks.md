# Rule: Runbooks

Every production service maintains operational **runbooks** — step-by-step procedures for
routine operations and failure scenarios, written so someone *other* than the author can
execute them under pressure. Runbooks are part of "done" for a service (master §1, §8).

## Requirements
- Live in the repo under `docs/runbooks/` (versioned, reviewed like code —
  `@rules/topic-documentation.md`); linked from alerts and the service README.
- **Tested:** validated in a drill/game-day, not just written. An untested runbook is a
  hypothesis. Review/refresh after each incident and on significant change.
- **Actionable:** exact commands, expected output, decision points, and rollback at each step;
  no "figure it out." Include prerequisites, access needed, and escalation contacts.
- **Automate the toil:** prefer a script/tool the runbook invokes over manual steps; the
  runbook explains when and why, the tool does the how. Aim to make runbooks obsolete by
  automating their content.

## Standard set (copy from `~/.claude/rules/runbooks/`)
Every service should have, at minimum:
- **deploy** — release/promote a version (`@rules/workflow-release.md`).
- **rollback** — revert a bad release safely, incl. DB considerations (`@rules/topic-database.md`).
- **incident-response** — triage/contain/recover (`@rules/workflow-incident-response.md`).
- **backup-restore** — restore data from backup; verify integrity (`@rules/workflow-data-lifecycle.md`).
- **on-call** — alert response, escalation, comms, handoff.
- **scaling** — scale up/down/out; handle load spikes (`@rules/topic-reliability.md`).
- **secret-rotation** — rotate keys/credentials with zero downtime (`@rules/workflow-secrets.md`).
- **dependency-patch** — patch a vulnerable dependency/CVE (`@rules/workflow-cve-management.md`).

Add service-specific runbooks for known failure modes surfaced by threat modeling and
post-mortems (`@rules/workflow-threat-model.md`, `@rules/workflow-incident-response.md`).

## Structure (see `runbooks/_TEMPLATE.md`)
Title · When to use (trigger/symptoms) · Prerequisites/access · Steps (with commands +
expected output) · Verification · Rollback/abort · Escalation contacts · Related runbooks.
