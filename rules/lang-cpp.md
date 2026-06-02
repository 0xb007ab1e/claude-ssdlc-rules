# Rule: C / C++

Memory-unsafe by default — most critical CVEs here are memory-safety bugs. Maximize
compiler/tooling help and prefer modern, safe constructs.

## Standard & build
- Target a modern standard (C++17/20+); `-std=` explicit. Treat warnings as errors:
  `-Wall -Wextra -Wpedantic -Werror`.
- Enable hardening flags: `-D_FORTIFY_SOURCE=3 -fstack-protector-strong`,
  `-fstack-clash-protection`, `-fcf-protection`, PIE + full RELRO, `-fPIE -pie`,
  `-Wl,-z,now -Wl,-z,relro`.

## Memory & type safety
- **Prefer C++ over C** and the standard library over raw constructs: `std::string`/
  `std::vector`/`std::span` over C strings/arrays; **smart pointers** (`unique_ptr`/
  `shared_ptr`) over `new`/`delete`; RAII for all resources. Follow the C++ Core Guidelines.
- **No** `gets`, `strcpy`/`strcat`/`sprintf`, unchecked `memcpy`, or unbounded scanf — use
  bounded/safe variants and check lengths. Validate all sizes/indices; guard against integer
  overflow before allocation/arithmetic on untrusted values.
- Avoid manual pointer arithmetic; check bounds; initialize all variables; no use-after-free
  / double-free (ownership via RAII). Never return pointers/refs to locals.

## Tooling (CI)
- **Sanitizers in test builds:** ASan, UBSan, and TSan (for threaded code); fuzz untrusted
  parsers with libFuzzer/AFL++ (`@rules/std-cwe.md` memory-safety entries).
- Static analysis: clang-tidy + clang-analyzer, cppcheck; `-Weverything` triage for clang.
- Format with clang-format; dependency/SCA scanning on third-party libs.
- Doc comments on every public class/function (feeds `docs/` mandate); enforce with Doxygen
  `WARN_IF_UNDOCUMENTED=YES` and treat doc warnings as errors.
- Crypto/RNG from vetted libs (libsodium/OpenSSL), never custom (`@rules/topic-cryptography.md`).

## Concurrency
- Data races are **undefined behavior** — protect shared state with `std::mutex`/`std::lock_guard`
  or `std::atomic`; prefer RAII locks, a consistent lock order, and `std::scoped_lock` for
  multiple locks. Run **TSan**. Prefer higher-level tasks (`std::async`/thread pools) over raw
  threads. See `@rules/topic-concurrency.md`.

## Testing
- Unit tests (GoogleTest/Catch2) run under sanitizers; coverage + fuzzing per master §4.

## Embedded / firmware note
- For embedded targets, additionally follow **MISRA C/C++** and **CERT C** (wiki.sei.cmu.edu);
  prefer static allocation, bounded loops, watchdogs, and freestanding-safe subsets; no dynamic
  allocation in critical paths; validate all hardware/serial input as untrusted.

## References & style guides
- **C++ Core Guidelines** — isocpp.github.io/CppCoreGuidelines.
- **Google C++ Style Guide** — google.github.io/styleguide/cppguide.html.
- **SEI CERT C/C++ Secure Coding** — wiki.sei.cmu.edu. Index: `@rules/reference-style-guides.md`.
