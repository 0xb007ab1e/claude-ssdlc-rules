# Standard: PCI DSS (Cardholder Data)

Apply **only** when the system stores, processes, or transmits cardholder data (CHD) or
sensitive authentication data (SAD). First goal: **reduce scope** — don't touch CHD if you
can avoid it.

## Scope reduction (do this first)
- Use a PCI-compliant payment provider with tokenization / hosted fields so raw PAN never
  enters your systems. Store tokens, not card numbers.
- **Never store SAD** after authorization (full track data, CVV/CVC, PIN) — ever.
- Segment any CHD environment (CDE) from the rest of the network; minimize systems in scope.

## Core requirements (when CHD is in scope)
- **Protect stored CHD:** render PAN unreadable (strong cryptography/tokenization); mask PAN
  on display (show at most first 6 / last 4). Manage keys per `@rules/workflow-secrets.md`.
- **Encrypt transmission** of CHD over open/public networks (TLS 1.2+).
- **Strong access control:** need-to-know, unique IDs, MFA for access to the CDE, least
  privilege; no shared/default accounts.
- **Logging & monitoring:** log all access to CHD and audit trails; protect and retain logs;
  monitor for anomalies (align with `@rules/std-owasp.md` #9).
- **Vulnerability management:** patch SLAs, quarterly scans / ASV scans, annual pen test;
  secure SDLC for CDE apps (this ruleset).
- **Secure development:** address OWASP-class flaws (`@rules/std-owasp.md`), code review,
  and change control for all CDE software.

> CHD is "restricted" data under master §5 classification — apply the strictest handling,
> redaction, and isolation rules.
