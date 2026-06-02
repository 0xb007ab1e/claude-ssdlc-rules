# Rule: C# / .NET

## Project setup
- Target a supported .NET LTS. Enable `<Nullable>enable</Nullable>` and
  `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`. Central package management with
  pinned versions; commit the lockfile (`packages.lock.json`).
- CI runs `dotnet format` (verify), analyzers, and tests with zero high-severity findings.

## Style & types
- Honor nullable reference types; avoid `!` null-forgiving on untrusted paths.
- Prefer `async`/`await` end-to-end with `CancellationToken`; never `.Result`/`.Wait()`
  (deadlock/leak risk). Dispose via `using`/`await using`.
- No empty/blanket `catch`; catch specific exceptions and add context.
- XML-doc comments on every public type/member (feeds `docs/` mandate); enforce with
  `<GenerateDocumentationFile>` + treat CS1591 (missing XML comment) as error.

## Secure coding
- Parameterize SQL (Dapper/EF parameters); never concatenate. EF Core for data access.
- Validate input (DataAnnotations/FluentValidation); encode output (Razor auto-encodes —
  avoid `Html.Raw` with untrusted data). Configure security headers + CSP.
- **No `BinaryFormatter`** or insecure deserialization; disable XXE (`XmlResolver = null`).
- Crypto via `System.Security.Cryptography` with strong algorithms; `RandomNumberGenerator`
  for security (never `System.Random`). Use ASP.NET Core Data Protection for secrets at rest.
- Run a .NET SAST (e.g. Roslyn security analyzers, security-code-scan) and SCA
  (`dotnet list package --vulnerable` / OWASP Dependency-Check) in CI; block on high/critical.

## Concurrency
- `async`/`await` end-to-end with `CancellationToken`; never `.Result`/`.Wait()` (deadlock).
  Guard shared state with concurrent collections / `Interlocked` / `SemaphoreSlim`; prefer
  immutability; `ConfigureAwait(false)` in libraries. See `@rules/topic-concurrency.md`.

## Testing
- xUnit/NUnit; isolated tests; WebApplicationFactory/Testcontainers for integration; mock
  clock/network. Coverage, mutation (Stryker.NET), and contract requirements per master §4.

## References & style guides
- **Microsoft C# Coding Conventions** — learn.microsoft.com/dotnet/csharp/fundamentals/coding-style.
- **.NET Framework Design Guidelines** — learn.microsoft.com/dotnet/standard/design-guidelines.
- **.NET Runtime coding style** (dotnet/runtime). Index: `@rules/reference-style-guides.md`.
