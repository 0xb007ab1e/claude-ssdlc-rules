# Topic: Numeric, Money & Time Correctness

Consolidates numeric and temporal correctness that's otherwise scattered (`@rules/topic-database.md`,
`@rules/topic-api-design.md`, `@rules/topic-i18n.md`, `@rules/std-cwe.md`). These bugs are silent,
costly, and often security/financial.

## Money & decimals
- **Never use binary floating point (`float`/`double`) for money** — it can't represent 0.10
  exactly. Use a **decimal type** (BigDecimal, `decimal`, `Decimal`) or store **integer minor
  units** (cents) with explicit currency.
- Always pair an amount with its **ISO 4217 currency code**; never assume symbol or decimal
  places (JPY has 0, most have 2, some 3). Don't mix currencies in arithmetic.
- **Rounding is a decision:** choose the mode (banker's/half-even vs half-up) deliberately and
  consistently; round only at the boundary (display/settlement), compute at full precision.
  Document it. Beware accumulation error in sums.

## Floating point (when you do use it)
- Don't `==` compare floats — use a tolerance/epsilon. Beware NaN/Inf propagation, catastrophic
  cancellation, and order-dependence of summation. Validate/clamp inputs.

## Integer correctness
- **Guard integer overflow/underflow** on untrusted or unbounded arithmetic (esp. sizes,
  indices, allocations, counters) — use checked/saturating ops or wider types; overflow before an
  allocation is a classic vuln (`@rules/std-cwe.md` CWE-190, `@rules/lang-cpp.md`, `@rules/lang-rust.md`).
- Mind signedness, truncation on narrowing casts, and division-by-zero / `INT_MIN/-1`.

## Units & quantities
- Make units explicit (and ideally type-encoded — `Meters`, `Millis`, `Bytes`) so you can't add
  seconds to milliseconds or dollars to euros (Mars Climate Orbiter). Convert at boundaries.

## Time & clocks
- **Store and compute in UTC**; convert to local only for display (`@rules/topic-i18n.md`).
  Persist with offset/zone where wall-clock intent matters (future appointments need the zone, not
  just an instant).
- **Wall clock vs monotonic:** use a **monotonic** clock for durations/timeouts/elapsed (wall
  clocks jump backward via NTP/DST); use wall clock for timestamps.
- Handle DST transitions, leap seconds/years, and clock skew across machines (don't assume ordered
  timestamps in distributed systems — use logical clocks/sequence where ordering matters,
  `@rules/topic-event-driven.md`).
- Inject the clock (don't call `now()` directly) so time is testable and freezable
  (`@rules/topic-testing.md`).

## References
- IEEE 754; ISO 4217 (currency); ISO 8601 / RFC 3339 (time); *falsehoods programmers believe
  about time*. Index: `@rules/reference-style-guides.md`.
