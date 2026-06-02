# Topic: Performance & Efficiency

Make performance a budget and a test, not an afterthought. Measure before optimizing —
**no guessing**.

## Budgets & measurement
- Set **performance budgets** for critical paths: API latency (p50/p95/p99), throughput,
  and for web UIs the **Core Web Vitals** (LCP, INP, CLS) and bundle size. Enforce in CI.
- Profile to find real hotspots before optimizing; optimize the measured bottleneck, not the
  guessed one. Track regressions against the budget.
- Define and test against expected + peak load (see load testing below).

## Common server-side issues
- **N+1 queries** — batch/eager-load; watch ORM lazy loading. Index for query patterns
  (`@rules/topic-database.md`).
- **Pagination** all list endpoints (cursor-based for large/realtime sets); never return
  unbounded result sets (also a DoS control — `@rules/std-owasp-api.md`).
- **Caching** for expensive/hot reads (`@rules/topic-caching.md`); avoid recomputation.
- Async/non-blocking IO; connection pooling; avoid blocking the event loop / holding threads.
- Stream large payloads instead of buffering whole; compress responses (gzip/brotli).
- Avoid premature micro-optimization that hurts readability; choose the right algorithm/data
  structure first (complexity beats constants).

## Client-side (web)
- Code-split and lazy-load; tree-shake; minimize and compress assets; defer non-critical JS.
- Optimize images (modern formats, responsive sizes); preload critical resources; cache
  static assets with long TTLs + content hashing.
- Minimize main-thread work and layout thrash; budget third-party scripts.

## Verification
- Load, soak, and spike tests for services; track Web Vitals in CI (Lighthouse) and in the
  field (RUM). Performance assertions on critical paths feed master §4.

## References
- **web.dev / Core Web Vitals** — web.dev/vitals; **Brendan Gregg** (systems performance) — brendangregg.com.
- *High Performance Browser Networking* (Grigorik). Index: `@rules/reference-style-guides.md`.
