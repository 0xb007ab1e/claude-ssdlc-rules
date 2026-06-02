# Topic: Notifications (Email / SMS / Push)

Sending transactional and (where consented) marketing messages reliably, deliverably, and
privately. Pairs with `@rules/topic-event-driven.md` (async send), `@rules/topic-api-consumption.md`
(the provider is an upstream), and `@rules/std-privacy.md` (consent).

## Deliverability (email)
- Authenticate your domain: **SPF, DKIM, and DMARC** (move DMARC toward enforcement). Use a
  reputable ESP or a warmed dedicated IP; monitor sender reputation.
- **Handle bounces and complaints** — suppress hard bounces and spam reports; keep lists clean.
  High bounce/complaint rates wreck deliverability.
- **One-click unsubscribe** + honor it immediately for anything non-transactional; comply with
  CAN-SPAM / CASL / GDPR. Separate transactional from marketing streams.

## Reliability & idempotency
- Send **asynchronously via a queue** with retries + DLQ (`@rules/topic-event-driven.md`); don't
  block the request path on the provider.
- **Idempotent sends:** dedupe by a stable message/event key so retries and at-least-once
  delivery don't double-notify (`@rules/topic-reliability.md`). Rate-limit per provider.
- Per-user **frequency caps**, quiet hours, batching/digest to avoid notification fatigue.

## Content & security
- **Templating:** localize (`@rules/topic-i18n.md`); **escape user-supplied content** in HTML
  emails/templates (template/HTML injection & XSS — `@rules/std-cwe.md`). Sign/scope links;
  avoid open-redirect in tracking links.
- **Minimize sensitive data over channels** — don't put secrets/PII/PHI in email/SMS bodies;
  prefer a link to the authenticated app (master §5). Verify recipient ownership to avoid
  sending data to the wrong address.
- Verify provider **delivery webhooks** (signatures — `@rules/topic-webhooks.md`).

## Preferences & consent
- Per-user channel preferences and **opt-in/opt-out**, persisted and enforced; record consent
  (`@rules/std-privacy.md`). Transactional vs. promotional handled distinctly.

## Observability
- Track sent / delivered / bounced / complained / opened; **alert on deliverability or
  bounce-rate regressions** (`@rules/topic-logging-observability.md`).

## References
- ESP deliverability guides; M3AAWG best practices; RFC 8058 (one-click unsubscribe).
  Index: `@rules/reference-style-guides.md`.
