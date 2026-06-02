# Template: Desktop App — project CLAUDE.md

For cross-platform desktop apps (Electron/Tauri) or native. Copy to the project's root
`CLAUDE.md`. Inherits the master automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-typescript.md        # Electron/Tauri frontend (or lang-rust for Tauri core, lang-cpp for native)
@~/.claude/rules/topic-web-frontend.md     # for webview-based UIs (Electron/Tauri)
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-authn-authz.md
@~/.claude/rules/topic-cryptography.md     # OS keychain for secrets at rest
@~/.claude/rules/topic-accessibility.md
@~/.claude/rules/topic-i18n.md
@~/.claude/rules/std-privacy.md
@~/.claude/rules/std-supplychain.md        # signed, notarized installers + auto-update
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md

## Stack
- Framework: <Electron / Tauri / native (Qt/WinUI/Cocoa)>; platforms: <Win / macOS / Linux>

## Project-specific rules
- **Webview hardening (Electron):** `contextIsolation: true`, `nodeIntegration: false`,
  `sandbox: true`; expose only a minimal, validated IPC bridge via `contextBridge`; strict
  CSP; never load untrusted/remote content with node access. (Tauri: allow-list the command
  API; minimal capabilities.)
- **IPC is a trust boundary:** validate every message from the renderer; the renderer is
  untrusted. No arbitrary FS/shell/command access from the UI.
- **Secrets** in the OS keychain/credential store, never plaintext files
  (`@rules/workflow-secrets.md`).
- **Distribution:** code-sign and notarize installers; **secure auto-update** with signature
  verification (`@rules/std-supplychain.md`) — never auto-run unsigned updates.
- Validate file/URL/protocol-handler inputs; confine file access; keep the framework patched
  (Electron/Chromium CVEs ship often — `@rules/workflow-vuln-mgmt.md`).
- **Design:** follow the platform design language — Fluent (Windows) / Apple HIG (macOS) /
  GNOME HIG (Linux); consistent cross-platform behavior (`@rules/reference-style-guides.md`).
```
