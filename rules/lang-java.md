# Rule: Java / Kotlin (JVM)

## Project setup
- Use a supported LTS JDK. Reproducible builds via Maven/Gradle with a locked dependency
  set; commit the lockfile/dependency verification metadata.
- CI runs formatter (spotless/google-java-format), static analysis, and tests with zero
  high-severity findings.

## Style & types
- Prefer immutability (`final`, records, Kotlin `val`/data classes); avoid nullability bugs
  (Optional / Kotlin null-safety; annotate `@Nullable`/`@NonNull` for Java APIs).
- No swallowed exceptions; never catch `Throwable`/`Exception` and ignore. Use specific
  types; wrap with context. Close resources with try-with-resources/`use`.
- Javadoc/KDoc on every public type and method (feeds `docs/` mandate); enforce with Checkstyle
  `MissingJavadocMethod`/`MissingJavadocType` (detekt `UndocumentedPublic*` for Kotlin).

## Secure coding
- **Never deserialize untrusted data** with native Java serialization; prefer JSON with a
  safe mapper and explicit allow-listing. Disable XXE in all XML parsers.
- SQL via `PreparedStatement`/JPA parameters — never string concatenation.
- Validate input (Bean Validation / explicit checks); encode output to prevent XSS.
- Crypto via JCA with strong algorithms; `SecureRandom` only; never hardcode keys.
- Run SpotBugs + FindSecBugs (SAST) and OWASP Dependency-Check / SCA in CI; block on
  high/critical. Keep the framework (Spring, etc.) patched.

## Concurrency
- Prefer immutable objects and `java.util.concurrent` (executors, concurrent collections,
  atomics, `CompletableFuture`) over raw `synchronized`/`wait`/`notify`; minimize shared mutable
  state and document thread-safety; use virtual threads for I/O-bound work. See
  `@rules/topic-concurrency.md`.

## Testing
- JUnit 5; isolate tests (no shared static state); Testcontainers for integration;
  mock clock/network. Coverage, mutation (PIT), and contract requirements per master §4.

## References & style guides
- **Google Java Style Guide** — google.github.io/styleguide/javaguide.html; *Effective Java* (Bloch).
- **Kotlin coding conventions** — kotlinlang.org/docs/coding-conventions.html.
- **SEI CERT Oracle Java** secure coding. Index: `@rules/reference-style-guides.md`.
