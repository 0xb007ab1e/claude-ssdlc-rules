# Topic: Resource Management, Lifecycle & Memory Safety

Deterministic cleanup of everything a program acquires — memory, handles, connections,
goroutines/threads, listeners — plus memory-safety and secret-zeroization concerns. The
*principle* is referenced from `@rules/topic-error-handling.md` (cleanup on every path) and
`@rules/topic-reliability.md` (graceful shutdown); this is the consolidated home. Language
syntax lives in each `lang-*` module.

## Acquire/release discipline
- **Whoever acquires a resource is responsible for releasing it**, on every path including
  errors and early returns. Prefer scope-bound, automatic release over manual close.
- Bind a resource's lifetime to a scope/owner; avoid leaking handles into ambiguous ownership.
- **Per-language idiom** (always release deterministically, never rely on the GC/finalizer for
  non-memory resources):
  - C++ — **RAII** (destructors); smart pointers. Rust — **`Drop`** / ownership.
  - C# — **`using` / `await using`** (`IDisposable`/`IAsyncDisposable`). Java/Kotlin —
    **try-with-resources** / **`use {}`**.
  - Go — **`defer` + `Close()`**. Python — **`with`** (context managers). Swift — **`defer`** /
    `deinit`. Ruby — block form / **`ensure`**. PHP/JS/TS — **`finally`** (TS 5.2+ `using` /
    `Symbol.dispose`). Scala — **`Using`** / bracket. Shell — **`trap`** on EXIT.
- **Finalizers/GC are a backstop, not a strategy** — they run late/never and don't guarantee
  ordering; always release explicitly.

## Leak classes to watch (managed languages leak too)
- **Native memory** — buffers, off-heap allocations (see memory safety below).
- **OS handles** — files, sockets, DB connections: use **pools**, cap size, and return/close
  promptly; a leaked connection exhausts the pool and looks like an outage (`@rules/topic-database.md`).
- **Concurrency** — goroutines/threads/tasks/coroutines that never exit: always provide
  cancellation (`context`/`CancellationToken`/structured concurrency) and bounded lifetimes.
- **Subscriptions** — event listeners, observers, timers, watches, websocket handlers: unsubscribe
  on teardown (a top cause of frontend + long-running-service leaks — `@rules/topic-web-frontend.md`,
  `@rules/topic-realtime.md`).
- **Unbounded growth** — caches/maps/queues without eviction or backpressure
  (`@rules/topic-caching.md`, `@rules/topic-reliability.md`).

## Graceful shutdown
- On SIGTERM/stop: stop accepting new work, **drain** in-flight requests/messages, flush buffers,
  checkpoint, then close pools/connections within a timeout. Distinguish liveness vs. readiness
  (`@rules/topic-reliability.md`). Idempotent, resumable work survives abrupt kills
  (`@rules/topic-event-driven.md`).

## Memory safety
- **Prefer memory-safe languages** by default; reserve C/C++ (and `unsafe` Rust) for where
  they're truly needed, and isolate/justify it (`@rules/lang-cpp.md`, `@rules/lang-rust.md`).
- In unsafe contexts: bounds-check, guard integer overflow before allocation/arithmetic, no
  use-after-free/double-free (ownership), validate all sizes from untrusted input
  (`@rules/std-cwe.md` CWE-119/125/787/416/190/476).
- **Verify with tooling:** ASan/UBSan/TSan/Valgrind, `-fstack-protector`/`_FORTIFY_SOURCE`, Miri
  for Rust unsafe, and fuzzing for parsers (`@rules/topic-testing.md`).

## Secret zeroization (sensitive data in memory)
- **Minimize lifetime** of secrets/keys/plaintext in memory; wipe (`memzero`) as soon as done —
  don't wait for GC.
- **Language caveats:** in GC'd/immutable-string languages (Java/C#/Python/JS/Go) string copies
  may persist and can't be reliably wiped — hold secrets in **mutable byte arrays** and clear them
  (`Arrays.fill`, `bytearray`), use `SecureString`/dedicated APIs, or libs like libsodium
  `sodium_memzero` / Rust `zeroize` / Go `memguard`. Avoid logging or putting secrets in
  exceptions/heap dumps (`@rules/workflow-secrets.md`, `@rules/topic-cryptography.md`, master §5).
- Disable core dumps / swap for processes handling key material where feasible.

## Testing
- Leak-detection in CI where the platform supports it (ASan/LeakSanitizer, goroutine-leak checks,
  handle/connection assertions); soak tests to catch slow leaks (`@rules/topic-performance.md`,
  `@rules/topic-testing.md`).

## References
- C++ Core Guidelines (resource/lifetime), Rust ownership model, language `using`/`defer`/`with`
  docs; OWASP on clearing sensitive data. Index: `@rules/reference-style-guides.md`.
