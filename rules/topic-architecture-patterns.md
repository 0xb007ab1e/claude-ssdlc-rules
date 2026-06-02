# Topic: Architecture Patterns

Structural patterns that keep business logic independent of I/O, frameworks, and persistence —
making code testable, changeable, and reasoned-about. Expands master §2 (SOLID, hexagonal).
Wire the pieces with `@rules/topic-dependency-injection.md`.

## The dependency rule
- **Dependencies point inward.** The domain/business core depends on nothing external; outer
  layers (UI, DB, frameworks, network) depend on the core, never the reverse. Source-code
  dependencies oppose the flow of control (achieved via DI + interfaces/ports).
- The core knows *nothing* about HTTP, SQL, the cloud, or the framework. You should be able to
  swap any of those without touching business logic.

## Functional core, imperative shell
- **Functional core:** pure, deterministic logic — decisions, calculations, state transitions —
  with **no I/O and no side effects**. Same inputs → same outputs.
- **Imperative shell:** a thin outer layer that does the I/O (read inputs, call the core, write
  results). Push side effects to the edges; keep decisions and actions separate.
- Payoff: the core is **trivially unit-testable without mocks** (`@rules/topic-testing.md`),
  easy to reason about, and **concurrency-safe** (pure = no shared mutable state, no races —
  `@rules/topic-concurrency.md`). State machines fit naturally in the core
  (`@rules/topic-state-management.md`).

## Ports & adapters (hexagonal) / Clean / Onion
- **Ports:** interfaces the core defines for what it needs (e.g. `OrderRepository`, `Clock`,
  `PaymentGateway`). **Adapters:** outer implementations (Postgres repo, system clock, Stripe
  client) injected at the composition root.
- **Layering** (Clean/Onion): entities → use cases → interface adapters → frameworks/drivers,
  obeying the dependency rule. Cross a boundary only through an interface.
- Lets you test the core against in-memory/fake adapters and swap infrastructure without churn.

## Apply proportionally
- Match ceremony to complexity — a small CLI or script doesn't need full hexagonal layering;
  a long-lived domain-rich service does. **Don't gold-plate** (`@rules/topic-anti-patterns.md`).
- Even when skipping layers, keep the instinct: isolate pure logic, push I/O to the edges,
  depend on abstractions for the things you'll test or swap.

## References
- *Clean Architecture* (Martin); Hexagonal Architecture (Cockburn); "Functional Core, Imperative
  Shell" (Gary Bernhardt); *Domain-Driven Design* (Evans). Index: `@rules/reference-style-guides.md`.
