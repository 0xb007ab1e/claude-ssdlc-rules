# Topic: Defensive Programming & Clean Control Flow

Write code that resists misuse and stays readable under change. Complements
`@rules/topic-error-handling.md` (what to do when things fail), `@rules/std-owasp-proactive.md`
(input validation), and the SOLID/architecture principles in master §2.

## Guard clauses & control flow
- **Guard clauses / early return:** validate preconditions at the top and return/throw early;
  keep the happy path un-indented at the bottom. Avoid the "arrow anti-pattern" (deep nested
  `if`/`else`). Handle errors and edge cases first.
- **Keep nesting shallow** (aim ≤ 2–3 levels); extract helpers instead of nesting. Cap
  cyclomatic/cognitive complexity per function (lint-enforced where the language supports it).
- **One level of abstraction per function**; small, single-purpose functions (SRP — master §2).
- Avoid `else` after a returning `if`; prefer early exits and flat, linear flow.

## Design by contract
- **Preconditions:** validate inputs at the boundary; reject bad arguments fast and loudly
  (fail fast — `@rules/topic-error-handling.md`). Distinguish *public* boundaries (validate
  untrusted input — `@rules/std-owasp-proactive.md`) from *internal* invariants (assertions).
- **Postconditions & invariants:** assert what must hold after an operation and what must always
  hold for a type. Use assertions for *programmer errors* (bugs), exceptions/Results for
  *expected runtime* failures — never use assertions for input validation or security checks
  (they may be compiled out).
- State invariants in code (assertions/checks) and in docs (`@rules/topic-documentation.md`).

## Make wrong code hard to write
- **Make illegal states unrepresentable:** use the type system (enums/sum types, newtypes,
  non-empty/non-null types, smart constructors) so invalid combinations don't compile. Prefer
  parsing untrusted input into a validated type once over re-checking everywhere ("parse, don't
  validate"). See `@rules/topic-state-management.md` for stateful flows.
- **Total functions:** handle every case (exhaustive matches); avoid partial operations
  (`head`/`!`/unchecked index) on untrusted data.
- **Immutability by default** (`const`/`val`/`final`/readonly); copy-on-share or defensive copies
  at boundaries so callers can't mutate your internals; favor pure functions.
- **Named constants over magic numbers/strings;** centralize and explain them. No unexplained
  literals in logic.
- **Principle of least astonishment:** predictable names, no hidden side effects, no surprising
  mutation; a function does what its name says and nothing more.

## Practice
- Validate, then trust within the boundary — don't scatter redundant re-checks (that hides where
  the real boundary is). Encapsulate invariants in the type/module that owns them.
- Defensive coverage is testable: assert edge cases and contract violations
  (`@rules/topic-testing.md`).

## References
- *Code Complete* (McConnell), *The Pragmatic Programmer*; "Parse, don't validate" (Alexis King);
  language lint rules for complexity. Index: `@rules/reference-style-guides.md`.
