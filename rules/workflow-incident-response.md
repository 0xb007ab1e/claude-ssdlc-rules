# Rule: Incident Response

For security incidents and major outages. Promoted from `@rules/workflow-vuln-mgmt.md`
(which handles routine vulnerability remediation); this is the response when something is
actively wrong.

## Severity levels
- **SEV1 — Critical:** active breach, data loss/exposure, or full outage of a critical
  service. All-hands, immediate, exec/customer comms.
- **SEV2 — High:** significant degradation or contained security incident; urgent, business-hours+.
- **SEV3 — Moderate:** minor/partial impact with a workaround; normal working hours.
- Declare early; it's cheaper to downgrade than to under-respond. Anyone can declare.

## Lifecycle (NIST 800-61 aligned)
1. **Prepare** — runbooks (`@rules/topic-documentation.md`), on-call rotation, contacts,
   access, and tooling ready *before* an incident. Practice with drills/game-days.
2. **Detect & analyze** — alerts/monitoring (`@rules/topic-logging-observability.md`) trigger;
   assess scope, severity, and impact; start an incident timeline immediately. Map observed
   adversary behavior to **`@rules/std-mitre-attack.md`** techniques for shared vocabulary and
   to anticipate next moves.
3. **Contain** — stop the bleeding: isolate affected systems, revoke/rotate exposed
   credentials (`@rules/workflow-secrets.md`), block the vector. Short-term then long-term
   containment. **Preserve evidence/logs** before wiping.
4. **Eradicate** — remove the root cause (malware, vulnerable component, misconfig).
5. **Recover** — restore from known-good (`@rules/topic-reliability.md` backups), verify
   integrity, monitor closely for recurrence before declaring resolved.
6. **Post-incident** — see below.

## Roles & comms
- Assign an **Incident Commander** (coordinates, decides), comms lead, and ops/responders.
  IC is not necessarily the most senior — it's whoever runs the response.
- Communicate on a defined channel; update stakeholders at a set cadence. Honor breach-
  notification duties and timelines (`@rules/std-privacy.md` — GDPR 72h; PCI/regulatory).

## Post-mortem (blameless)
- Within a few days: timeline, root cause(s), impact, what worked/didn't, and **tracked,
  time-bound action items** with owners. Focus on systems and process, not individuals.
- Feed findings back into prevention (detection gaps, missing tests, controls) and update
  runbooks. Share learnings.
