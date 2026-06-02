# Rule: Scala

Common for data engineering (Spark) and JVM backends. Complements `@rules/lang-java.md` for
JVM concerns.

## Project setup
- Pin the Scala version + sbt/Mill; commit the build/lock. CI runs scalafmt (check) + a linter
  (Scalafix/WartRemover) with zero issues, and tests. Enable `-Wunused`, `-Xfatal-warnings` for
  new code.

## Style & safety
- **Prefer immutability and pure functions:** `val` over `var`, immutable collections, no shared
  mutable state; isolate side effects (an effect type — Cats Effect/ZIO — or at minimum the edges).
- **Model effects/failures in types:** `Option`/`Either`/`Try`; avoid throwing for expected errors
  and avoid `.get`/`.head`/partial functions on untrusted data (`@rules/topic-error-handling.md`).
- Exhaustive pattern matching (enable warnings); avoid `null` (interop boundary only); avoid
  over-clever implicits — keep them explicit and documented.
- Scaladoc on public APIs (feeds `docs/` mandate; enforce with scalastyle `ScalaDocChecker`).
  Keep one consistent style (functional vs. imperative) per codebase.

## Secure coding
- Parameterize SQL (no string interpolation into queries); validate all input as untrusted
  (`@rules/std-cwe.md`, `@rules/std-owasp.md`). No insecure Java deserialization (`@rules/lang-java.md`).
- Crypto via vetted libs + `SecureRandom`; secrets from the secret manager (`@rules/workflow-secrets.md`).
- **Spark/data jobs:** treat source data as untrusted; partition deliberately; classify/redact PII
  in datasets and logs (`@rules/std-privacy.md`, `@rules/topic-logging-observability.md`).

## Resource management
- **Cleanup:** `scala.util.Using` / bracket patterns (or cats-effect `Resource` / ZIO scoped)
  so resources release on every path, including failures in effects. See
  `@rules/topic-resource-management.md`.

## Concurrency
- Prefer immutability + an effect system (cats-effect/ZIO) or `Future` with an explicit
  `ExecutionContext` over shared mutable state and raw threads; `synchronized` is a last resort.
  See `@rules/topic-concurrency.md`.

## Testing
- ScalaTest/MUnit; property-based tests (ScalaCheck) for pure logic; isolate IO; Testcontainers
  for integration. Coverage/contract requirements per master §4 (`@rules/topic-testing.md`).

## References & style guides
- **Scala Style Guide** — docs.scala-lang.org/style; **Databricks Scala Guide** (Spark) —
  github.com/databricks/scala-style-guide. Index: `@rules/reference-style-guides.md`.
