# Standard: OWASP Proactive Controls

Positive, "do this" secure-coding patterns — the complement to the Top 10's "avoid this."

1. **Define security requirements** — derive from ASVS; capture per feature up front.
2. **Leverage security frameworks & libraries** — use vetted, maintained libraries for auth,
   crypto, validation; keep them patched. Never hand-roll security primitives.
3. **Secure database access** — parameterized queries, least-privilege DB accounts,
   secure configuration, encrypted connections.
4. **Encode and escape data** — context-aware output encoding (HTML, JS, URL, SQL) at the
   point of use to neutralize injection/XSS.
5. **Validate all inputs** — positive (allow-list) validation, server-side, with strong
   typing/schemas; treat all external input as hostile.
6. **Implement digital identity** — appropriate authentication levels (MFA), secure session
   management, and password handling (argon2/bcrypt, breach-check, no arbitrary rotation).
7. **Enforce access controls** — deny by default, server-side, least privilege, RBAC/ABAC;
   check ownership on every object access.
8. **Protect data everywhere** — classify, encrypt in transit/at rest, manage keys, minimize
   and redact (ties to master §5).
9. **Implement security logging & monitoring** — log security-relevant events with PII
   redaction; make logs actionable and alert on anomalies.
10. **Handle errors & exceptions securely** — fail closed; never leak stack traces, secrets,
    or internal detail to clients; log the detail server-side.
