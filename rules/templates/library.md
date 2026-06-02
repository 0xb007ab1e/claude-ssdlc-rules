# Template: Library / SDK — project CLAUDE.md

Copy to a new project's root `CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.
Libraries are consumed by others — API stability, docs, and supply-chain integrity matter most.

```markdown
# <LibraryName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-rust.md             # or the implementation language module
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-supplychain.md       # signed, reproducible, SBOM'd releases
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/topic-testing.md
@~/.claude/rules/topic-license-compliance.md

## Library specifics
- **Public API is a contract:** semantic versioning; no breaking changes without a major
  bump and a migration note. Keep the public surface minimal.
- **Docs mandate applies fully:** every public symbol documented with runnable examples.
- **No surprise side effects:** no network/filesystem/global state on import; pure where
  possible; let callers inject I/O and configuration.
- **Security:** validate inputs at the public boundary; never log on behalf of the caller;
  surface errors as typed values, don't swallow.
- **Supply chain:** signed releases + provenance + SBOM; minimal, pinned dependencies.

## Project-specific rules
- Supported platforms/versions: <...>
- Deprecation policy: <...>
```
