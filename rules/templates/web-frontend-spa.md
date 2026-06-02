# Template: Web Frontend / SPA — project CLAUDE.md

For browser apps (React/Vue/Svelte/Angular, SSR or SPA). Copy to the project's root
`CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-typescript.md
@~/.claude/rules/topic-web-frontend.md     # CSP, SRI, CORS, cookies, XSS, clickjacking
@~/.claude/rules/topic-authn-authz.md      # token handling on the client
@~/.claude/rules/std-owasp.md
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-supplychain.md        # npm deps, SRI, lockfile
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-realtime.md      # if using WebSocket/SSE
@~/.claude/rules/std-privacy.md            # if it handles personal data / analytics

## Stack
- Framework: <React / Vue / Svelte / Next.js>; build: <Vite / ...>
- Rendering: <SPA / SSR / SSG>; state: <...>

## Project-specific rules
- **Client is untrusted:** every security check is also enforced by the backend API.
- CSP is strict (nonce/hash-based, no unsafe-inline/eval); security headers set at the edge.
- Tokens kept in memory (never localStorage); cookies Secure/HttpOnly/SameSite.
- No secrets/API keys in the bundle; strip source maps from prod.
- Accessibility (WCAG) and i18n are acceptance criteria where applicable.
```
