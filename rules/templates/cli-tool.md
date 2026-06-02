# Template: CLI Tool — project CLAUDE.md

Copy to a new project's root `CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.
Swap the language module for the implementation language.

```markdown
# <ToolName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-go.md               # or lang-rust / lang-python / lang-typescript
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-owasp-proactive.md   # input handling / secure defaults
@~/.claude/rules/std-supplychain.md       # signed releases, SBOM for distributed binaries
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/topic-testing.md
@~/.claude/rules/topic-license-compliance.md

## Tool specifics
- Distribution: <homebrew / single binary / package registry>
- Inputs: validate args, env, stdin, and files as untrusted (path traversal, injection).
- Secrets: read from env/keychain, never flags (shell history leak); redact in output.
- Exit codes: documented and stable; fail closed on error.

## Project-specific rules
- <commands, config format, deviations with justification>
```
