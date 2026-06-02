# Topic: Testing Strategy

Consolidates the test *strategy* behind the master §4 gates. The `lang-*` modules cover
framework specifics; this covers what to test, at what level, and how to keep tests trustworthy.

## The test pyramid (shape your suite)
- **Many unit tests** (fast, isolated, pure) → **fewer integration tests** (real DB/queue via
  Testcontainers, contracts between components) → **few E2E tests** (critical user journeys
  only). Avoid the "ice-cream cone" (mostly slow E2E) — it's flaky and slow.
- Push coverage down the pyramid: test logic at the unit level, wiring at integration, journeys at E2E.

## What to test
- **Behavior, not implementation** — tests assert observable outcomes so refactors don't break them.
- **Edge cases & boundaries:** nulls, empty, max/min, off-by-one, unicode, timezones, concurrency.
- **Negative / abuse paths** (security — master §4): invalid input, authz bypass attempts, malformed data.
- **Regression test for every bug:** reproduce with a failing test *first*, then fix (master §1).
- **Contract tests** for every service/API boundary (consumer-driven where possible).
- **Property-based tests** for pure logic, parsers, encoders, serializers.
- **Mutation testing** on critical modules to verify the tests actually catch faults (coverage ≠ quality).

## Coverage enforcement (the "how" behind master §4)
- A flat repo-wide `--cov-fail-under=90` (or equivalent: jacoco/istanbul/coverlet thresholds) is
  the **baseline**, and CI fails the build below it. Track **branch** coverage too, not just line.
- The **100%-on-critical-paths** rule can't be one number — implement it with **path-scoped
  enforcement:** a second check targeting the critical modules at 100% (per-file/per-package
  `fail_under`, coverage groups, or a dedicated job), or an explicit, reviewed list of critical
  modules. Decide which paths are critical (auth, authz, crypto, payments, data handling) at
  design time and document them.
- **No critical paths?** State that (e.g. a stateless utility) — the 90% baseline applies; don't
  assert 100%-critical vacuously. Coverage is a floor, not the goal — pair it with mutation
  testing so it isn't gamed.

## Verify the gate actually fails (don't trust a green negative test)
- When confirming a lint/security/coverage gate *catches* violations, prove it with a **known-bad
  input** and check the gate **fails** — a passing negative test often means the fixture was
  silently exempted, not that the rule works.
- **Watch for fixtures excluded by config/convention.** Example: validating ruff/pydocstyle `D`
  (docstring) rules with a probe file named `_probe.py` gives a **false pass** — a leading
  underscore marks the module *private*, which `D` exempts; use a **public-named** module. Same
  trap with `tests/**`, `*_test`, `examples/`, generated/`# noqa` lines, and per-file-ignore
  globs — confirm your bad fixture isn't on an ignore list.
- Generally: a guard you've never seen go red is unproven. Mutation testing (above) is the
  systematic form of this — it injects known-bad code to confirm tests fail.

## Test quality & hygiene
- **Deterministic & hermetic:** no real network, wall-clock, randomness, or shared mutable
  state. Inject clock/IO; seed RNG; freeze time. Flaky tests are bugs — quarantine then fix,
  never blanket-retry to green.
- **Isolated & parallel-safe:** each test sets up and tears down its own state; order-independent.
- **Fast feedback:** unit suite runs in seconds; gate slower suites in CI stages.
- **Readable:** arrange-act-assert; one logical assertion focus; descriptive names; test code is
  reviewed and maintained like production code.

## Test data
- **Synthetic / factories**, never production data (master §5). Builders/factories over fixtures
  for clarity. Anonymize if derived from real data.
- Reset state between tests; use ephemeral databases (Testcontainers) for integration.

## References
- *Practical Test Pyramid* (Fowler) — martinfowler.com; **Google Testing Blog / "Software
  Engineering at Google"** (testing chapters). Index: `@rules/reference-style-guides.md`.
