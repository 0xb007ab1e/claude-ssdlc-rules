# Topic: Error Handling

Consolidates the error-handling fragments across `@rules/std-owasp-proactive.md` (#10),
`@rules/topic-reliability.md`, and the `lang-*` modules. Errors are part of the contract —
design them, don't just throw.

## Principles
- **Fail closed / fail safe:** on error or ambiguity, deny and abort to a safe state — never
  proceed insecurely or with partial/garbage data (master §2).
- **Don't swallow errors:** no empty catch blocks, no ignored return codes. Handle, wrap with
  context, or propagate — never silently discard.
- **Errors are values / typed:** model expected failures explicitly (Result/Either, error enums,
  checked outcomes) rather than control-flow-by-exception for routine cases. Reserve
  exceptions/panics for truly exceptional, unrecoverable conditions.
- **Fail fast on programmer errors** (bad invariants, misconfig at startup — see
  `@rules/topic-config-environments.md`); **handle gracefully** for expected runtime errors
  (network, validation, not-found).

## Taxonomy (distinguish these)
- **User/client errors** (400-class): invalid input → clear, actionable message; the caller can fix it.
- **Auth errors** (401/403): generic messages — don't leak whether a resource exists or why
  (`@rules/topic-authn-authz.md`).
- **Transient/dependency errors** (5xx/timeout): retry with backoff if idempotent, else circuit-break
  (`@rules/topic-reliability.md`).
- **Programmer errors / bugs:** fail fast, alert, fix — don't try to recover from a broken invariant.

## Security & disclosure (master §5)
- **Never leak internals to clients:** no stack traces, SQL, file paths, secrets, or dependency
  versions in responses. Return a stable error code + safe message; log the detail server-side
  with a correlation ID (`@rules/topic-logging-observability.md`).
- Use a consistent error envelope (RFC 9457 Problem Details for APIs — `@rules/topic-api-design.md`).

## Practice
- Clean up resources on every path (RAII / try-with-resources / `defer` / `finally`) —
  lifecycle, leaks, and shutdown are owned by `@rules/topic-resource-management.md`.
- Preserve the original cause when wrapping (exception chaining / `%w`); don't flatten to a string.
- Make error handling testable and tested — negative-path tests (`@rules/topic-testing.md`).
- Distinguish retryable vs. terminal errors explicitly so callers/queues behave correctly
  (`@rules/topic-event-driven.md` DLQs).

## References
- *Release It!* (Nygard); language error-handling idioms in the `lang-*` modules.
  Index: `@rules/reference-style-guides.md`.
