# Topic: Anti-Patterns & Code Smells

A recognition catalog for review and refactoring. A smell isn't always a bug — it's a **prompt
to look closer**. Use it in `@rules/workflow-code-review.md`; the positive counterparts live in
`@rules/topic-defensive-programming.md`, `@rules/topic-architecture-patterns.md`, and
`@rules/topic-dependency-injection.md`.

## Design / structure smells
- **God object/class**, **Big Ball of Mud**, spaghetti code — too many responsibilities / no
  boundaries. Split by responsibility (SRP), apply architecture patterns.
- **Anemic domain model** — data bags with all logic elsewhere; put behavior with the data it
  guards.
- **Feature envy / inappropriate intimacy** — a class fixated on another's internals; move the
  behavior or fix encapsulation.
- **Shotgun surgery / divergent change** — one change touches many files, or one file changes for
  many reasons; realign module boundaries (cohesion).
- **Circular dependencies**, **leaky abstraction** — break cycles; don't let implementation
  details bleed through an interface.

## Function-level smells
- **Long method**, **long parameter list**, **deep nesting** → extract, use guard clauses, group
  params into types (`@rules/topic-defensive-programming.md`).
- **Boolean/flag parameter** ("boolean trap") — split into two intent-revealing functions.
- **Primitive obsession / stringly-typed** — wrap domain concepts in types (make illegal states
  unrepresentable).
- **Magic numbers/strings** — name them (`@rules/topic-defensive-programming.md`).

## Duplication & abstraction
- **Copy-paste / WET** — violates DRY; extract shared logic. **But** beware the opposite:
  **premature/incidental abstraction** and over-DRYing unrelated code (prefer "a little copying
  over a little dependency" / AHA — avoid wrong abstractions).

## Coupling & global state
- **Service Locator**, **Singleton abuse / global mutable state** — hidden dependencies and
  concurrency hazards; prefer DI (`@rules/topic-dependency-injection.md`, `@rules/topic-concurrency.md`).
- **Hard-coded config/dependencies** — inject them (`@rules/topic-config-environments.md`).

## Process / decision anti-patterns
- **Premature optimization** (measure first — `@rules/topic-performance.md`), **golden hammer**
  (one tool for everything), **cargo-cult** (copying without understanding), **NIH / reinventing
  the wheel**, **bikeshedding**.
- **Lava flow / dead code** — remove unused code (minimize attack surface, master §2);
  **comments as deodorant** — fix the code, don't explain bad code.

## Async / concurrency smells
- **Callback hell**, **sync-over-async** (blocking on async → deadlock), **fire-and-forget**
  tasks that outlive scope (`@rules/topic-concurrency.md`, `@rules/topic-resource-management.md`).

## Security anti-patterns (never do)
- Rolling your own crypto, **security by obscurity**, hard-coded secrets, **blocklist-only**
  (deny-list) validation instead of allow-list, trusting client-side checks
  (`@rules/std-owasp-proactive.md`, `@rules/topic-cryptography.md`, `@rules/workflow-secrets.md`).

## Refactoring
- Refactor under a **green test safety net** (`@rules/topic-testing.md`); make small, behavior-
  preserving steps; address the smell only when it impedes the current change (don't gold-plate).

## References
- *Refactoring* (Fowler — smells catalog) — refactoring.com/catalog; *AntiPatterns* (Brown et al.);
  "The Wrong Abstraction" (Sandi Metz). Index: `@rules/reference-style-guides.md`.
