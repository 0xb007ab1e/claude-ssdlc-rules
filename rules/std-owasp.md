# Standard: OWASP Top 10 + ASVS

Apply to any application, especially web/API services. Use the **Top 10** as the risk
checklist and **ASVS** as the verification depth.

## OWASP Top 10 — required controls
1. **Broken Access Control** — enforce authZ server-side on every request; deny by default;
   no IDOR (verify object ownership); no client-side-only checks.
2. **Cryptographic Failures** — encrypt sensitive data in transit/at rest; strong, current
   algorithms; no hardcoded keys (see master §5, `@rules/workflow-secrets.md`).
3. **Injection** — parameterize queries; validate input; encode output; safe APIs only.
4. **Insecure Design** — threat-model first (`@rules/workflow-threat-model.md`); secure
   patterns from `@rules/std-owasp-proactive.md`.
5. **Security Misconfiguration** — harden defaults, disable debug/verbose errors in prod,
   minimal surface, security headers (see `@rules/std-cis.md`).
6. **Vulnerable & Outdated Components** — SCA + patch SLAs (`@rules/workflow-vuln-mgmt.md`).
7. **Identification & Authentication Failures** — strong auth, MFA where appropriate,
   secure session management, rate-limit/lock-out, password hashing (argon2/bcrypt).
8. **Software & Data Integrity Failures** — verify integrity of deps/updates; signed
   artifacts; no insecure deserialization (see `@rules/std-supplychain.md`).
9. **Security Logging & Monitoring Failures** — log security events (with redaction),
   detect and alert; ensure tamper-resistant, retained logs.
10. **SSRF** — validate/allow-list outbound URLs; block internal metadata endpoints; no
    user-controlled fetch targets without an allow-list.

## ASVS — verification level
- Default target **ASVS Level 2** for applications handling sensitive data; **Level 3** for
  high-value/regulated systems; Level 1 only for low-risk public content.
- Use the relevant ASVS chapter as the acceptance checklist for each feature (auth, session,
  access control, validation, crypto, errors/logging, data protection, comms, config).
- Abuse/negative tests (master §4) should cover the ASVS requirements for the feature.
