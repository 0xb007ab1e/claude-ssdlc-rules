# Topic: Accessibility (a11y)

Target **WCAG 2.2 Level AA** for user-facing web/mobile UIs. Accessibility is an acceptance
criterion, not a retrofit. Pairs with `@rules/topic-web-frontend.md` and `@rules/std-owasp-masvs.md`.

## POUR principles (WCAG)
- **Perceivable:** text alternatives (`alt`) for non-text content; captions/transcripts for
  media; don't convey meaning by color alone; minimum contrast 4.5:1 (3:1 large text).
- **Operable:** full **keyboard** operability; visible focus indicators; no keyboard traps;
  skip-links; targets large enough; no content that flashes > 3×/sec (seizure risk); users
  can pause/stop motion.
- **Understandable:** clear labels and instructions; consistent navigation; programmatic
  error identification with suggestions; predictable behavior; set page `lang`.
- **Robust:** valid, **semantic HTML** first (`<button>`, `<nav>`, `<main>`, headings in
  order); ARIA only to fill gaps, never to replace semantics ("no ARIA is better than bad
  ARIA"); proper roles/states/`aria-label`s; associate form labels with inputs.

## Implementation
- Semantic structure + landmarks; logical heading hierarchy; one `<h1>` per page.
- Manage focus on route changes / modal open-close; trap focus within modals; restore on close.
- Announce dynamic updates via live regions; don't rely on hover/pointer only.
- Respect user preferences: `prefers-reduced-motion`, `prefers-color-scheme`, zoom/reflow to 400%.

## Testing (gates)
- Automated checks in CI (axe-core / Lighthouse / pa11y) — but automation catches ~30–40%.
- **Manual** keyboard-only pass and screen-reader pass (NVDA/VoiceOver) for key flows.
- Include a11y assertions in E2E tests for critical journeys (master §4).

## References
- **WCAG 2.2** — w3.org/TR/WCAG22; **WAI-ARIA Authoring Practices (APG)** — w3.org/WAI/ARIA/apg.
- **WebAIM** — webaim.org; **The A11Y Project checklist** — a11yproject.com.
- Index: `@rules/reference-style-guides.md`.
