# Runbook: Deploy / Release

> Copy to `docs/runbooks/deploy.md` and fill in `<...>`. Rules: `@rules/workflow-release.md`.

## When to use
- Promoting a tagged, gate-passing build to an environment (staging → prod).

## Prerequisites & access
- Green CI on the release commit (all gates — `@rules/workflow-cicd.md`); signed artifact +
  SBOM exist. Deploy role/credentials (least privilege, OIDC). Change/approval recorded.

## Steps
1. Confirm the release tag + artifact digest: `<cmd>` → matches the intended commit.
2. Verify DB migrations are backward-compatible and already applied (or apply now):
   `<migrate cmd>` → no long locks (`@rules/topic-database.md`).
3. Trigger the deploy of the **promoted artifact** (build once, promote — no rebuild): `<cmd>`.
4. Roll out progressively (canary/blue-green): `<cmd>`; watch SLOs/error budget
   (`@rules/topic-reliability.md`) for `<N>` minutes.
5. Flip feature flags as planned (default off/safe) — `@rules/topic-config-environments.md`.

## Verification
- Health/readiness green; smoke tests pass: `<cmd>`. Error rate + latency within budget; no
  new error classes in logs (`@rules/topic-logging-observability.md`).

## Rollback / abort
- If canary regresses: halt rollout and follow `runbooks/rollback.md`.

## Escalation
- Page `<on-call>`; notify `<stakeholders>` on `<channel>`.

## Related
- `runbooks/rollback.md`, `runbooks/scaling.md`; `@rules/workflow-release.md`.

---
_Last validated: <date>. Owner: <team>._
