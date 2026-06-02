# Rule: Rust

## Project setup
- Pin the toolchain (`rust-toolchain.toml`); commit `Cargo.lock` for binaries.
- CI runs `cargo fmt --check`, `cargo clippy -- -D warnings` (zero warnings), and tests.

## Style & safety
- **Avoid `unsafe`.** If unavoidable, isolate it, document the invariants it upholds, and
  justify why it's sound; cover it with tests and (ideally) Miri.
- No `.unwrap()`/`.expect()`/`panic!` on fallible paths in library/production code — return
  `Result`/`Option` and propagate with `?`. Reserve panics for true invariants.
- Model errors with an enum (thiserror) for libs; `anyhow` acceptable at app boundaries.
- Doc comments (`///`) on every public item, with examples that run under `cargo test`
  (feeds `docs/` mandate). Enforce with `#![warn(missing_docs)]` (deny in CI) on public APIs.

## Secure coding
- Validate/parse external input into typed values at the boundary (parse, don't validate).
- Crypto: use vetted crates (ring, rustls, RustCrypto); never hand-roll. Use a CSPRNG.
- Avoid integer overflow surprises: use checked/saturating ops on untrusted arithmetic;
  enable `overflow-checks` in release for sensitive code.
- Run `cargo audit` (RUSTSEC advisories) and `cargo deny` (licenses/bans/sources) in CI.

## Resource management
- **Cleanup:** ownership + `Drop` release resources deterministically at scope end (RAII);
  use guards/`drop()` for explicit/early release; prefer `zeroize` for secret buffers. See
  `@rules/topic-resource-management.md`.

## Concurrency
- "Fearless concurrency": `Send`/`Sync` + the borrow checker prevent data races at compile time.
  Share with `Arc<Mutex<_>>`/channels; in async, don't block the executor (use async I/O) and
  keep tasks structured/cancellable. See `@rules/topic-concurrency.md`.

## Testing
- Unit + integration tests; property-based tests (proptest) for parsers/encoders;
  fuzz targets (cargo-fuzz) for untrusted-input parsing.
- Coverage, mutation, and contract requirements per master §4.

## References & style guides
- **Rust API Guidelines** — rust-lang.github.io/api-guidelines.
- **Rust Style Guide** — doc.rust-lang.org/style-guide (enforced by rustfmt); **Clippy** lints.
- **The Rustonomicon** (unsafe code) — doc.rust-lang.org/nomicon. Index: `@rules/reference-style-guides.md`.
