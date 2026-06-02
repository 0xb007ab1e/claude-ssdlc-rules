# Rule: Kotlin (Android / JVM)

Complements `@rules/lang-java.md` for JVM specifics; this covers Kotlin idioms and Android.

## Project setup
- Pin Kotlin + (for Android) AGP/SDK versions; Gradle with version catalogs + a lockfile.
- CI runs ktlint/detekt (zero issues) and tests. Treat compiler warnings as errors for new code.

## Style & safety
- **Null safety:** lean on the type system — avoid `!!` (not-null assertion) and unsafe casts on
  fallible/untrusted paths; use `?.`, `?:`, `let`/`requireNotNull` with intent.
- Prefer **immutability**: `val` over `var`, `data class`, read-only collections (`List` not
  `MutableList`) in APIs. Model state with sealed classes/enums (exhaustive `when`).
- **Coroutines:** structured concurrency (scope-bound); pass `CoroutineContext`/cancellation; never
  block threads with `runBlocking` in production; do IO on `Dispatchers.IO`. Avoid `GlobalScope`.
  Guard shared mutable state (`Mutex`/atomics/confinement). See `@rules/topic-concurrency.md`.
- Errors via `Result`/sealed types for expected failures; exceptions for exceptional
  (`@rules/topic-error-handling.md`). Use `use {}` for closeable resources.
- KDoc on public APIs (feeds `docs/` mandate); enforce with detekt
  `UndocumentedPublicClass`/`UndocumentedPublicFunction`/`UndocumentedPublicProperty`.

## Secure coding (Android — `@rules/std-owasp-masvs.md`)
- Secrets/keys in the **Android Keystore**, never source/`SharedPreferences`/resources; no secrets
  in the APK (it's decompilable). Use EncryptedSharedPreferences/Jetpack Security for at-rest.
- TLS with validation (consider pinning via Network Security Config); no cleartext traffic.
  Validate all input, IPC (Intents), deep links, and exported-component access.
- Least permissions; protect exported components; guard WebViews (no `addJavascriptInterface` to
  untrusted content). Crypto via Keystore/`SecureRandom` — never custom (`@rules/topic-cryptography.md`).

## Resource management
- **Cleanup:** `use {}` for `Closeable` (auto-close on every path); structured-concurrency
  scopes so coroutines are cancelled with their parent; cancel/clear listeners on teardown. See
  `@rules/topic-resource-management.md`.

## Testing
- JUnit5/Kotest + MockK; coroutine test dispatchers; Robolectric/instrumented for Android;
  Testcontainers for backend Kotlin. Coverage/mutation per master §4 (`@rules/topic-testing.md`).

## References & style guides
- **Kotlin coding conventions** — kotlinlang.org/docs/coding-conventions.html.
- **Android app architecture / Kotlin style** — developer.android.com; **Material Design 3**.
- **detekt** rule set. Index: `@rules/reference-style-guides.md`.
