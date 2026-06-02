# Runbook: Incident Response

> Copy to `docs/runbooks/incident-response.md` and fill in `<...>`.
> Rules: `@rules/workflow-incident-response.md`.

## When to use
- A security incident (suspected breach, active exploitation) or major outage. When in doubt,
  declare — it's cheaper to downgrade than to under-respond.

## Severity / impact
- Classify SEV1/2/3 (`@rules/workflow-incident-response.md`); set initial severity now, adjust later.

## Prerequisites & access
- Incident channel `<#channel>`; paging tool; access to logs/dashboards; break-glass creds
  location. Anyone may declare an incident.

## Steps
1. **Declare** + open the incident channel; assign **Incident Commander** and scribe. Start a
   timeline immediately.
2. **Assess** scope/impact from telemetry (`@rules/topic-logging-observability.md`); set severity.
3. **Contain:** isolate affected systems; **rotate exposed secrets** (`runbooks/secret-rotation.md`);
   block the vector. **Preserve logs/evidence before wiping.**
4. **Eradicate** root cause (patch — `runbooks/dependency-patch.md`; remove malware/misconfig).
5. **Recover:** restore from known-good (`runbooks/backup-restore.md`), verify integrity, monitor.
6. Honor **breach-notification** duties + timelines (`@rules/std-privacy.md` — GDPR 72h, etc.).

## Verification
- Symptom resolved; attacker access revoked; systems healthy; monitoring confirms no recurrence.

## Escalation
- IC pages `<security lead>` / `<eng lead>` / legal+comms for SEV1; cadence updates to stakeholders.

## Post-incident
- Blameless post-mortem within `<N>` days: timeline, root cause, tracked action items
  (`@rules/workflow-incident-response.md`). Update this runbook with lessons learned.

## Related
- `runbooks/secret-rotation.md`, `runbooks/backup-restore.md`, `runbooks/dependency-patch.md`.

---
_Last validated: <date>. Owner: <team>._
