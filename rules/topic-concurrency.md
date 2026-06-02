# Topic: Concurrency & Thread Safety

Concurrency bugs are nondeterministic, hard to test, and a security risk (races/TOCTOU).
Default to designs that avoid shared mutable state. Pairs with `@rules/topic-reliability.md`
(timeouts/backpressure), `@rules/topic-resource-management.md` (goroutine/task leaks,
cancellation), and the `lang-*` concurrency idioms.

## Design to avoid the problem
- **Prefer no shared mutable state:** immutable data, message passing/channels/actors, or
  confining state to one owner beats locks. Pure functions parallelize safely.
- **Share by communicating, not communicating by sharing.** If you must share, make it immutable
  or guard it explicitly.
- Concurrency (structure) ≠ parallelism (execution) — design for correctness first.

## Race conditions
- **Data races** (unsynchronized access with ≥1 writer) are undefined behavior in many languages
  — eliminate them; run a **race detector / sanitizer** in CI (`-race`, TSan).
- **Race conditions / atomicity violations:** "check-then-act" and "read-modify-write" must be
  atomic — use locks, atomics, transactions, or compare-and-swap. A correct-looking sequence of
  individually-safe operations can still be wrong.
- **TOCTOU (time-of-check to time-of-use)** is a *security* bug: re-validating then acting on a
  resource that can change between (files, permissions, balances) enables privilege/abuse. Use
  atomic operations (open-then-fstat, `O_CREAT|O_EXCL`, DB row locks / conditional updates,
  idempotency keys) instead of check-then-use (`@rules/std-cwe.md`, `@rules/topic-database.md`).

## Locks & coordination
- **Least locking:** hold locks for the shortest scope; never do I/O or call out (esp. callbacks)
  while holding a lock.
- **Deadlock avoidance:** acquire multiple locks in a **consistent global order**; prefer
  trylock-with-timeout; avoid nested locks. Watch for **livelock** and lock convoys.
- Prefer higher-level primitives (concurrent collections, atomics, semaphores, immutable
  snapshots) over hand-rolled locking. Beware **reentrancy** and non-reentrant locks.
- Protect every access to shared state — a single unguarded read can corrupt.

## Async / structured concurrency
- Use **structured concurrency** (scoped tasks/coroutines) so work is bounded, cancellable, and
  errors propagate; always pass cancellation (context/token) and **timeouts**
  (`@rules/topic-reliability.md`). No fire-and-forget tasks that outlive their scope
  (`@rules/topic-resource-management.md` leaks).
- **Never block the async event loop / async context** with sync I/O or CPU-bound work — offload
  to a worker/thread pool. Don't mix blocking and async carelessly (deadlocks).
- Bound concurrency with pools/semaphores; size pools to the real bottleneck; backpressure over
  unbounded queues.

## Verify
- Run race/thread sanitizers in CI; write stress/concurrency tests and, where valuable,
  property/deterministic-schedule tests; assume tests won't catch every interleaving — favor
  designs that are correct by construction (`@rules/topic-testing.md`).

## References
- *Java Concurrency in Practice* (Goetz); Go Memory Model (go.dev/ref/mem); Rust `Send`/`Sync`
  ("fearless concurrency"); *The Art of Multiprocessor Programming*. Index: `@rules/reference-style-guides.md`.
