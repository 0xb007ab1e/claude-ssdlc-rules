# Runbook: Backup & Restore

> Copy to `docs/runbooks/backup-restore.md` and fill in `<...>`.
> Rules: `@rules/workflow-data-lifecycle.md`, `@rules/topic-reliability.md`.

## When to use
- Data loss/corruption, recovery during an incident, or a **scheduled restore drill** (do this
  regularly — an untested backup is not a backup).

## Prerequisites & access
- Backup location + decryption key access (least privilege); target environment to restore
  into (prefer an isolated/non-prod target for drills). Know the RPO/RTO targets.

## Steps
1. Identify the correct backup (point-in-time): `<list cmd>` → pick timestamp `<...>`.
2. Verify backup integrity/checksum before restoring: `<cmd>`.
3. Restore into the target: `<restore cmd>`. For PITR, replay to `<timestamp>`.
4. Run migrations/compatibility checks if restoring an older schema: `<cmd>`.

## Verification
- Row counts / checksums / spot-check critical records match expectations; app connects and
  passes smoke tests. Record actual RTO achieved vs. target.

## Rollback / abort
- Restores target an isolated instance first; only cut over once verified. Keep the current
  (damaged) state snapshotted before overwriting, in case forensics are needed.

## Escalation
- Page `<DBA/on-call>`; for data-loss incidents, link to `runbooks/incident-response.md`.

## Related
- `runbooks/rollback.md`, `runbooks/incident-response.md`; `@rules/workflow-data-lifecycle.md`.

---
_Last validated: <date> (restore drill). Owner: <team>._
