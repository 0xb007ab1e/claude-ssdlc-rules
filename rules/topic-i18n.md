# Topic: Internationalization & Localization (i18n / l10n)

Build for multiple languages/regions from the start — retrofitting is expensive. Pairs with
`@rules/topic-accessibility.md`.

## Internationalization (i18n — make it translatable)
- **No hardcoded user-facing strings.** Externalize to resource/message catalogs keyed by ID;
  never concatenate sentence fragments (grammar/word-order differs per language).
- Support **pluralization** and gender via ICU MessageFormat (not `if count == 1`); pass
  named variables, not positional string-building.
- Design layouts for **text expansion** (~30–40% longer in some languages) and **RTL**
  (Arabic/Hebrew) — use logical CSS properties (`margin-inline-start`), `dir` attribute.
- Set page/document `lang`; use Unicode-aware libraries for the locale.

## Encoding & data
- **UTF-8 everywhere** — storage, transport, files, DB columns/collation. Normalize Unicode
  (NFC) on input; be careful with case-folding and length (code points vs. grapheme clusters).
- Guard against homoglyph/bidi spoofing in security-sensitive contexts (`@rules/std-cwe.md`).

## Localization (l10n — adapt to a locale)
- Format **dates, times, numbers, currency, units** via locale-aware libraries (Intl/ICU) —
  never manual formatting. Store timestamps in **UTC**; convert for display.
- Currency: store amount + ISO currency code; never assume a symbol or decimal places.
- Locale negotiation from `Accept-Language`/user preference with a sensible fallback chain.
- Collation/sorting and search are locale-dependent — use locale-aware comparison.

## Process
- Pseudo-localization in testing to catch hardcoded strings and layout breakage early.
- Keep translation catalogs in VCS; don't ship untranslated keys to users (fallback).

## References
- **Unicode CLDR / ICU** — cldr.unicode.org, icu.unicode.org; **W3C Internationalization** — w3.org/International.
- Platform `Intl` APIs / ICU MessageFormat. Index: `@rules/reference-style-guides.md`.
