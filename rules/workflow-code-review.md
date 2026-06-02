# Rule: Code Review (security + quality checklist)

Goes beyond the PR mechanics in `@rules/workflow-git.md` — this is *what* a reviewer checks.
Every change gets a substantive review; security-relevant changes get a security-focused one.

## Reviewer mindset
- Review for **correctness, security, and maintainability** — not style (automate style).
- Small PRs get real review; push back on oversized diffs. Understand the *why* before the
  *how*; if you can't, ask. Approve only what you understand.
- Be specific and kind; suggest, cite the rule/standard; distinguish blocking from optional
  (prefix nits). Author and reviewer share responsibility for the merged result.

## Quality checklist
- [ ] Does it do what the PR says, and only that? No unrelated/scope-creep changes.
- [ ] Readable and consistent with surrounding code; sound naming; no needless complexity.
- [ ] Clean control flow — guard clauses over deep nesting; reasonable function size/complexity;
      named constants over magic numbers; invariants asserted (`@rules/topic-defensive-programming.md`).
- [ ] No code smells / anti-patterns introduced (god object, primitive obsession, hidden
      dependencies, copy-paste); dependencies injected, not located; pure logic isolated from I/O
      (`@rules/topic-anti-patterns.md`, `@rules/topic-dependency-injection.md`, `@rules/topic-architecture-patterns.md`).
- [ ] Errors handled (no swallowed exceptions, fail-closed); edge cases and nulls considered.
- [ ] Concurrency hazards checked — shared mutable state guarded, no data races/TOCTOU, no
      deadlock-prone lock ordering, async work cancellable (`@rules/topic-concurrency.md`).
- [ ] Resource cleanup on every path; no leaks (handles, listeners, tasks — `@rules/topic-resource-management.md`).
- [ ] Numeric/temporal correctness where relevant — money as decimal, overflow guarded, UTC/monotonic
      clocks (`@rules/topic-numeric-correctness.md`); stateful flows have valid transitions (`@rules/topic-state-management.md`).
- [ ] No obvious performance traps (N+1, unbounded queries — `@rules/topic-performance.md`).
- [ ] Tests present and meaningful (cover the change + a failing-then-fixed test for bugs);
      meet master §4 gates. Not just coverage theater.
- [ ] Docs updated for new/changed public symbols (`@rules/topic-documentation.md`).

## Security checklist (CWE/OWASP-aware — `@rules/std-cwe.md`, `@rules/std-owasp.md`)
- [ ] Input validated at boundaries; output encoded; queries parameterized (no injection).
- [ ] AuthZ enforced server-side; object ownership checked (no IDOR/BOLA — `@rules/std-owasp-api.md`).
- [ ] No secrets/keys/credentials in the diff; sensitive data redacted from logs (master §5).
- [ ] Crypto uses approved primitives (`@rules/topic-cryptography.md`); no homemade crypto.
- [ ] New/updated dependencies vetted and pinned (`@rules/std-supplychain.md`).
- [ ] AI-generated/copied code verified — compiles, tested, no hallucinated deps (mandate §1).
- [ ] No new attack surface left unauthenticated/unrate-limited.

## Process
- All CI gates green before approval (`@rules/workflow-cicd.md`). Use automated review tools
  to augment, not replace, human judgment. Re-review after significant changes.
