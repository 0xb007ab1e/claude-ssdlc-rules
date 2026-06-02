# Runbook: <Title>

> Copy to `docs/runbooks/<name>.md` in the project and fill in. Keep it executable by someone
> who didn't write it. See `@rules/workflow-runbooks.md` for the rules.

## When to use
- Trigger / symptoms / the alert that points here. When NOT to use this runbook.

## Severity / impact
- Expected blast radius and urgency; link to severity taxonomy (master §7).

## Prerequisites & access
- Roles/permissions, tools, VPN, credentials needed (least privilege). Where to get access.

## Steps
1. `command --here`  → expected output / what success looks like.
2. Decision point: if X, go to step 3; if Y, go to Rollback.
3. ...

## Verification
- How to confirm the procedure worked (health checks, metrics, a test request).

## Rollback / abort
- How to safely back out if a step fails or makes things worse.

## Escalation
- Who to page and when; comms channel; stakeholders to notify.

## Related
- Links to related runbooks and rule modules.

---
_Last validated: <date> (drill/incident). Owner: <team>._
