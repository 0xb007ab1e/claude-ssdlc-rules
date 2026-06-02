# Rule: Secrets Management

## Storage & access
- Secrets live in a dedicated secret manager / KMS (Vault, cloud KMS, SOPS-encrypted)
  — never in source, config files, container images, CI logs, or env files committed to VCS.
- Applications read secrets at runtime via injected env vars or a secrets API, scoped with
  least privilege. One identity per workload; no shared "god" credentials.
- Local development uses a local secret store or `.env` that is **git-ignored**; provide a
  committed `.env.example` with placeholder keys only.

## Rotation & lifecycle
- All long-lived credentials have a defined rotation interval; prefer short-lived,
  auto-rotated tokens (OIDC/workload identity) over static keys.
- Rotate immediately on suspected exposure or personnel change. Revoke before rotating.
- No credential is valid forever; set expiry on tokens, certs, and signing keys.

## Detection & hygiene
- Secret scanning runs pre-commit and in CI (block on detection). Treat any committed
  secret as compromised: rotate it, don't just delete the commit.
- Never log, print, or include secrets in error messages or telemetry (see redaction
  rules in master §5).
- Encryption keys follow separation of duties: the key encrypting data ≠ the credential
  accessing the service.

> Pre-existing intentional legacy shared creds (e.g. `~/.env.global`) are out of scope for
> rotation flags unless the user asks.
