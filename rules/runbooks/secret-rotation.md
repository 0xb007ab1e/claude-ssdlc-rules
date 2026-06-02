# Runbook: Secret Rotation

> Copy to `docs/runbooks/secret-rotation.md` and fill in `<...>`.
> Rules: `@rules/workflow-secrets.md`, `@rules/topic-cryptography.md`.

## When to use
- Scheduled rotation, suspected/confirmed exposure (treat any committed secret as
  compromised), or personnel/role change.

## Prerequisites & access
- Access to the secret manager/KMS; ability to deploy/restart consumers; list of every
  consumer of the secret (find via the secret manager's access audit).

## Steps (zero-downtime: add-new-before-revoke-old)
1. **Generate** the new credential/key in the secret manager: `<cmd>`. Strong, unique.
2. **Add** it alongside the old one (dual-valid period) — provision both so consumers accept
   either: `<cmd>`.
3. **Roll out** the new value to all consumers (deploy/restart or hot-reload): `<cmd>`.
4. Verify every consumer is using the new credential (logs/metrics).
5. **Revoke** the old credential: `<cmd>`. (For a confirmed compromise, revoke FIRST and
   accept brief downtime over continued exposure.)

## Verification
- All consumers authenticate with the new secret; the old one is rejected; no auth-error spike
  (`@rules/topic-logging-observability.md`).

## Rollback / abort
- If a consumer breaks, the old secret is still valid during the dual-valid window — re-point
  and investigate before revoking.

## Escalation
- For a confirmed exposure, run this under `runbooks/incident-response.md`; page security.

## Related
- `runbooks/incident-response.md`; `@rules/workflow-secrets.md`, `@rules/topic-cryptography.md`.

---
_Last validated: <date>. Owner: <team>._
