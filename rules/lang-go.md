# Rule: Go

## Project setup
- Use a supported Go release with modules; commit `go.sum`. Run `go mod verify`.
- Keep `go vet` and `golangci-lint` clean (zero issues) in CI.

## Style & idioms
- `gofmt`/`goimports` enforced. Idiomatic Go: small interfaces, accept interfaces/return
  structs, no premature abstraction.
- **Handle every error** explicitly; wrap with `%w` for context; never ignore returned
  errors (errcheck). No naked `panic` in libraries — return errors.
- Doc comments on every exported identifier (feeds `docs/` mandate); enforce with `revive`'s
  `exported` rule (or staticcheck ST1000) via golangci-lint.
- Guard goroutines: pass `context.Context` for cancellation/timeouts; avoid leaks; protect
  shared state (mutex/channels) and run the **race detector** in tests (`go test -race`).

## Secure coding
- SQL via `database/sql` placeholders or a query builder — never string-built queries.
- `os/exec` with explicit arg slices; never pass user input to a shell.
- Use `crypto/rand` (never `math/rand`) for security; standard `crypto` libs only.
- Validate and bound all input; set server timeouts (`ReadHeaderTimeout`, etc.) and body
  size limits; confine file paths to an allowed root.
- Run `govulncheck` and a SAST (e.g. gosec) in CI; block on high/critical.

## Resource management
- **Cleanup:** `defer` + `Close()` for files/connections (release on every path); use
  `context` cancellation and bounded lifetimes so goroutines don't leak. See
  `@rules/topic-resource-management.md`.

## Concurrency
- Share by communicating (channels) over shared memory; guard shared state with `sync`
  primitives/atomics; **always run `go test -race`** in CI; bound concurrency and propagate
  `context` for cancellation/timeouts. See `@rules/topic-concurrency.md`.

## Testing
- Table-driven tests; `t.Parallel()` where safe; `testdata/` for fixtures; `t.TempDir()`.
- Coverage, mutation, and contract requirements per master §4.

## References & style guides
- **Effective Go** — go.dev/doc/effective_go; **Go Code Review Comments** — go.dev/wiki/CodeReviewComments.
- **Google Go Style Guide** — google.github.io/styleguide/go.
- **Uber Go Style Guide** — github.com/uber-go/guide. Index: `@rules/reference-style-guides.md`.
