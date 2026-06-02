# Runbook: On-Call

> Copy to `docs/runbooks/on-call.md` and fill in `<...>`. Rules: `@rules/topic-reliability.md`.

## When to use
- You're the on-call engineer and received an alert, or you're starting/ending a shift.

## Prerequisites & access
- Paging tool access, dashboards, log access, incident channel, and this repo's runbooks.
  Ensure you can deploy/rollback before your shift starts.

## Responding to an alert
1. **Acknowledge** the page within `<SLA>` so it doesn't escalate.
2. Open the linked runbook/dashboard; assess severity and user impact.
3. **Mitigate first, diagnose later** — stop user pain (rollback, scale, failover, flag-off)
   before root-causing. Follow the specific runbook for the symptom.
4. If it's an incident (security or major outage), **declare** and follow
   `runbooks/incident-response.md` — don't solo a SEV1.
5. Keep a timeline of actions; communicate status on `<channel>` at a regular cadence.

## Verification
- Alert cleared; metrics back to normal; user impact resolved. Silence/snooze only with a
  follow-up task, never blindly.

## Escalation
- Can't resolve within `<time>` or out of depth → escalate to `<secondary on-call>` /
  `<eng lead>`. Escalating early is encouraged, not a failure.

## Shift handoff
- Document open issues, ongoing mitigations, noisy/flapping alerts, and pending follow-ups for
  the next on-call. File tickets for toil and alert-quality fixes.

## Related
- `runbooks/incident-response.md`, `runbooks/scaling.md`, `runbooks/rollback.md`.

---
_Last validated: <date>. Owner: <team>._
