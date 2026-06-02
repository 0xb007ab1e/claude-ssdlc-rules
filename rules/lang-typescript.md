# Rule: TypeScript / Node.js

## Project setup
- Use a maintained LTS Node. Pin deps with a lockfile; commit it. Prefer ESM.
- `tsconfig.json` in **strict** mode (`strict`, `noUncheckedIndexedAccess`,
  `noImplicitOverride`, `exactOptionalPropertyTypes`). No implicit `any`.

## Style & types
- Lint with zero errors (eslint + type-aware rules); auto-format (prettier).
- Avoid `any` and non-null `!` assertions; model absence with unions/`unknown` + narrowing.
- Validate all external input (HTTP, env, files) at the boundary with a runtime schema
  validator (zod/valibot) — TypeScript types alone do not validate runtime data.
- TSDoc on every exported symbol (feeds `docs/` mandate); enforce with eslint-plugin-jsdoc
  (`require-jsdoc`) + eslint-plugin-tsdoc.

## Secure coding
- Prevent injection: parameterized DB queries/ORM; never build SQL/shell by concatenation.
- XSS: encode/escape on output; prefer frameworks' safe templating; avoid
  `dangerouslySetInnerHTML`/`innerHTML` with untrusted data. Set a strong CSP.
- Avoid `eval`, `Function()`, and `child_process` with interpolated input.
- Use `crypto` (Web Crypto / Node `crypto`) — never `Math.random()` for security.
- Set secure HTTP headers (helmet or equivalent), validate `Content-Type`, enforce
  size/timeout limits, and CSRF protection for cookie-based auth.
- Run `npm audit`/SCA and a JS/TS SAST (e.g. semgrep, eslint security plugins) in CI.
- Guard against prototype pollution and ReDoS (bounded regex; avoid catastrophic patterns).

## Resource management
- **Cleanup:** `try/finally` (or `using` / `Symbol.dispose`, TS 5.2+) to close handles/connections;
  **remove event listeners, clear timers, and abort fetches** (`AbortController`) on teardown to
  avoid leaks. See `@rules/topic-resource-management.md`.

## Concurrency
- Single-threaded event loop: no shared-memory data races within a thread, but **logical races
  still occur across `await`** (check-then-act / interleaved mutations) — re-validate after await
  and use locks/queues for critical sections. Parallelism is via Workers (message passing); don't
  block the loop with sync/CPU work. See `@rules/topic-concurrency.md`.

## Testing
- vitest/jest; no shared mutable module state; mock network/clock.
- Coverage, mutation, and contract requirements per master §4.

## References & style guides
- **Google TypeScript Style Guide** — google.github.io/styleguide/tsguide.html.
- **Airbnb JavaScript Style Guide** — github.com/airbnb/javascript; **MDN** — developer.mozilla.org.
- **typescript-eslint** recommended-type-checked rules. Index: `@rules/reference-style-guides.md`.
