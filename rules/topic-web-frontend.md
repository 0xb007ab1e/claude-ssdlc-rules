# Topic: Web Frontend / Browser Security

Client-side controls for browser apps (SPA/SSR). Complements `@rules/lang-typescript.md`,
`@rules/std-owasp.md`, and `@rules/topic-authn-authz.md`. Remember: the client is untrusted —
**all security decisions are also enforced server-side.**

## Headers & policy
- **Content Security Policy (CSP):** strict, nonce/hash-based; no `unsafe-inline`/`unsafe-eval`;
  restrict `script-src`, `connect-src`, `frame-ancestors`. This is the primary XSS backstop.
- `Strict-Transport-Security` (HSTS), `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`/`frame-ancestors` (clickjacking).
- **CORS:** explicit allow-list of origins; never reflect arbitrary `Origin`; never
  `Access-Control-Allow-Origin: *` with credentials.

## XSS & injection
- Prefer framework auto-escaping (React/Vue/Svelte); avoid `innerHTML`/`dangerouslySetInnerHTML`/
  `v-html` with untrusted data; sanitize with a vetted library (DOMPurify) if you must.
- Never build DOM/URLs/styles from untrusted input without encoding; avoid `javascript:` URLs.
- **Subresource Integrity (SRI)** on third-party scripts/styles; pin and minimize external deps.

## Auth & data on the client
- Cookies for session: `Secure`, `HttpOnly`, `SameSite=Lax/Strict`. **Don't store tokens in
  `localStorage`** (XSS-readable) — keep access tokens in memory; use the auth patterns in
  `@rules/topic-authn-authz.md`.
- **CSRF** protection for cookie-based auth (SameSite + anti-CSRF token for state-changing
  requests).
- No secrets/API keys in client bundles — anything shipped to the browser is public.
- Validate and bound all input client-side for UX, but re-validate server-side for security.

## Supply chain & build
- Audit npm deps (`@rules/std-supplychain.md`); lockfile committed; watch for malicious
  packages and typosquats. Strip source maps and debug info from production bundles.
- Guard against prototype pollution and ReDoS in client code.

## References & design systems
- **OWASP Cheat Sheets** (XSS, CSP, CSRF) — cheatsheetseries.owasp.org; **MDN** + **web.dev**.
- **UI design systems:** Material Design 3 (m3.material.io), Apple HIG, Microsoft Fluent;
  **Refactoring UI**; Nielsen usability heuristics (nngroup.com).
- Index: `@rules/reference-style-guides.md`.
