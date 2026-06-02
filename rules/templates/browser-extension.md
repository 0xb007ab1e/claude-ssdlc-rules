# Template: Browser Extension — project CLAUDE.md

For Chrome/Firefox/Edge extensions (Manifest V3). Copy to the project's root `CLAUDE.md`.
Inherits the master automatically. Extensions have a unique, high-trust permission model —
treat every boundary as hostile.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-typescript.md
@~/.claude/rules/topic-web-frontend.md     # CSP, DOM/XSS, message handling
@~/.claude/rules/std-owasp.md
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-authn-authz.md      # if it authenticates to a backend
@~/.claude/rules/std-privacy.md            # extensions can see lots of user data
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-release.md       # store review + staged rollout
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md

## Stack
- Target(s): <Chrome / Firefox / Edge>; Manifest V3; bundler: <...>

## Project-specific rules
- **Least privilege:** request the minimum `permissions`/`host_permissions`; prefer
  `activeTab` and optional permissions over broad host access. Each permission is justified.
- **Strict CSP** in the manifest; no remote code (MV3 bans it); no `eval`/inline scripts.
- **Trust boundaries:** content scripts run in hostile pages — validate all messages between
  content script ↔ background ↔ page; never expose privileged APIs to page context; sanitize
  any DOM injection (`@rules/topic-web-frontend.md`).
- **No secrets in the extension bundle** (it's fully inspectable); proxy privileged calls
  through your backend.
- **Privacy:** minimize data collection; clear disclosure + consent; comply with store
  privacy policies; never exfiltrate browsing data without explicit consent.
- Auto-update channel secured; sign packages; monitor store reviews for abuse reports.
```
