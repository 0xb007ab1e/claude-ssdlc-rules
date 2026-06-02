# Topic: State Management & State Machines

Model state explicitly so invalid states and transitions can't happen. Extends
"make illegal states unrepresentable" from `@rules/topic-defensive-programming.md`.

## Model state explicitly
- For anything with a lifecycle (orders, jobs, connections, workflows, sessions), define a
  **finite set of states** and the **allowed transitions** between them — a state machine — rather
  than a tangle of boolean flags. Combinations of booleans encode impossible states; one enum
  doesn't.
- **Make illegal states unrepresentable:** use sum types/enums with per-state data (a `Cancelled`
  state carries a reason; a `Draft` has no `shippedAt`). The type system rejects invalid shapes.
- **Reject invalid transitions** explicitly (return an error / no-op), don't silently allow them.
  Centralize transition logic in one place, not scattered `if`s across the codebase.

## Transitions
- Transitions are **explicit, total, and validated:** every (state, event) pair is handled
  (exhaustive), and disallowed ones fail loudly (`@rules/topic-error-handling.md`).
- **Idempotent / replay-safe transitions** where events can repeat (at-least-once delivery,
  retries, webhooks — `@rules/topic-event-driven.md`, `@rules/topic-webhooks.md`): re-applying
  the same transition is a safe no-op.
- **Concurrency:** guard transitions against races — use optimistic concurrency (version column),
  conditional updates, or locks so two actors can't both move state (`@rules/topic-concurrency.md`,
  `@rules/topic-database.md`).
- **Persist and audit** state + transitions where it matters (who/what/when — event sourcing or a
  status + history; `@rules/topic-logging-observability.md`).

## Client / UI state
- Keep a **single source of truth**; derive view state rather than duplicating it (avoid
  divergent copies). Prefer unidirectional data flow; make state changes explicit and traceable.
- Distinguish server state (cached/synced — `@rules/topic-caching.md`) from local UI state.

## Verify
- The valid-transition matrix is highly testable; assert that disallowed transitions are rejected
  and that transitions are idempotent (`@rules/topic-testing.md`).

## References
- Statecharts (Harel) / state-machine libraries (e.g. XState); event-sourcing patterns
  (`@rules/topic-event-driven.md`). Index: `@rules/reference-style-guides.md`.
