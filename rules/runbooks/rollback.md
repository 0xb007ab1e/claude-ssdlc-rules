# Runbook: Rollback

> Copy to `docs/runbooks/rollback.md` and fill in `<...>`. Rules: `@rules/workflow-release.md`.

## When to use
- A release caused an SLO regression, elevated errors, or a functional/security defect and
  forward-fix isn't fast enough.

## Severity / impact
- Usually SEV2+; rolling back is the bias when in doubt during an active regression.

## Prerequisites & access
- The previous known-good artifact digest is available; deploy role. Know whether the release
  included a DB migration (critical — see below).

## Steps
1. Stop the in-progress rollout / freeze further promotion: `<cmd>`.
2. **Check migrations:** if the release applied a DB change, confirm it was
   backward-compatible (expand/contract — `@rules/topic-database.md`). If so, app rollback is
   safe. If NOT reversible, do **not** naively roll back — escalate; forward-fix or restore
   per `runbooks/backup-restore.md`.
3. Redeploy the previous known-good artifact: `<cmd>` (or shift traffic back to blue/stable).
4. Disable the offending feature flag if the change was flag-gated (fastest path): `<cmd>`.

## Verification
- Health green; error rate + latency back within budget; the original symptom is gone.

## Rollback / abort
- If rollback itself fails, escalate to incident response (`runbooks/incident-response.md`).

## Escalation
- Page `<on-call>` / incident commander; notify `<stakeholders>`.

## Related
- `runbooks/deploy.md`, `runbooks/backup-restore.md`, `runbooks/incident-response.md`.

---
_Last validated: <date>. Owner: <team>._
