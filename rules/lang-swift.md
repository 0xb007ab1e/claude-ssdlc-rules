# Rule: Swift (iOS/macOS)

## Project setup
- Pin the Swift/Xcode toolchain; Swift Package Manager with a committed `Package.resolved`.
- CI runs SwiftFormat + SwiftLint (zero violations) and tests. Enable strict concurrency checking.

## Style & safety
- **Embrace optionals** — avoid force-unwrap (`!`) and `try!`/`as!` on untrusted/fallible paths;
  use `guard let`/`if let`, `??`, and typed `throws`. Force-unwrap only where the invariant is
  truly guaranteed.
- Prefer **value types** (`struct`/`enum`) and immutability (`let`); reference types only when
  identity/sharing is needed. Model state with enums + associated values (make illegal states
  unrepresentable).
- Use `Result`/`throws` for errors (`@rules/topic-error-handling.md`); avoid silent `try?` that
  discards errors.
- **Concurrency:** use `async/await` + actors (`Sendable`) for shared mutable state; avoid data
  races (the compiler's strict concurrency catches many); never block the main thread with IO.
  See `@rules/topic-concurrency.md`.
- Doc comments (`///`, DocC) on public APIs (feeds `docs/` mandate); enforce with SwiftLint
  `missing_docs`.

## Secure coding (mobile context — `@rules/std-owasp-masvs.md`)
- Secrets/keys in **Keychain** (with appropriate accessibility), never `UserDefaults`/plist/source.
- Networking over TLS with validation (`URLSession`); consider certificate pinning; ATS on
  (no arbitrary cleartext). Validate all input, IPC, deep links, and URL-scheme params.
- Use `CryptoKit`/Keychain for crypto; `SystemRandomNumberGenerator`/`SecRandomCopyBytes` for
  randomness — never `arc4random`-as-security shortcuts or custom crypto (`@rules/topic-cryptography.md`).
- No sensitive data in logs, screenshots, pasteboard, or backups; protect data-at-rest with
  file protection classes.

## Resource management
- **Cleanup:** `defer` for scope-exit cleanup and `deinit` for owned resources; avoid retain
  cycles with `weak`/`unowned` (esp. closures/delegates); cancel `Task`s. See
  `@rules/topic-resource-management.md`.

## Testing
- XCTest / Swift Testing; isolate tests; mock network/clock; UI tests for critical flows.
  Coverage and contract requirements per master §4 (`@rules/topic-testing.md`).

## References & style guides
- **Swift API Design Guidelines** — swift.org/documentation/api-design-guidelines.
- **Apple Human Interface Guidelines** — developer.apple.com/design (for UI).
- **SwiftLint** rule reference. Index: `@rules/reference-style-guides.md`.
