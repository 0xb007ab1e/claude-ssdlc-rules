# Topic: Authentication & Authorization

Concrete patterns for proving identity (authN) and enforcing permissions (authZ).
Complements `@rules/std-owasp.md` (#1, #7) and `@rules/std-owasp-proactive.md` (#6, #7).

## Authentication
- **Don't build your own** identity provider. Use OAuth 2.0 / OIDC via a vetted IdP
  (Auth0/Okta/Cognito/Keycloak) or a maintained library. Use **Authorization Code + PKCE**
  for web/native/SPA; never the implicit or password grants.
- **Passwords** (when unavoidable): hash with argon2id (preferred) or bcrypt/scrypt — never
  fast hashes (MD5/SHA). Enforce length over complexity; check against breach corpora; no
  forced periodic rotation; no silent truncation.
- **MFA** for privileged and remote access; prefer WebAuthn/passkeys or TOTP over SMS.
- **Rate-limit and lock-out** auth endpoints; use generic error messages (no
  "user not found" vs "wrong password"); add timing-safe comparisons.

## Sessions & tokens
- **Server-side sessions:** opaque, high-entropy IDs; `Secure`, `HttpOnly`, `SameSite`
  cookies; rotate on privilege change; idle + absolute timeouts; invalidate on logout.
- **JWTs:** verify signature with a pinned algorithm (reject `alg:none`; don't accept
  attacker-chosen alg); validate `iss`/`aud`/`exp`/`nbf`; keep them short-lived; store
  access tokens in memory (not localStorage). Use refresh-token rotation with reuse
  detection. JWTs can't be revoked — keep TTL small or maintain a denylist for critical ops.
- Never put secrets/PII in token payloads (they're readable).

## Authorization
- **Deny by default; enforce server-side on every request** — never trust client-side checks
  or hidden UI as a control.
- Check **object ownership / tenant scope** on every access (prevent IDOR/BOLA — see
  `@rules/std-owasp-api.md`).
- Choose a model and apply it consistently: **RBAC** (roles→permissions) for coarse control,
  **ABAC/ReBAC** (attributes/relationships) for fine-grained/multi-tenant. Centralize policy
  (e.g. a policy engine like OPA/Cedar) rather than scattering `if` checks.
- Least privilege everywhere; separate duties for sensitive actions; re-authenticate
  ("step-up") for high-risk operations.
- Log authZ decisions for auditing (redacted — see `@rules/topic-logging-observability.md`).

## References
- **OAuth 2.0 Security BCP** (RFC 9700), **OAuth for Native Apps** (RFC 8252) + **PKCE** (RFC 7636),
  **OpenID Connect Core**.
- **NIST SP 800-63** (Digital Identity); **OWASP Authentication / Session Management / JWT Cheat Sheets**.
- Index: `@rules/reference-style-guides.md`.
