# Template: Mobile App — project CLAUDE.md

For native/hybrid iOS/Android apps. Copy to the project's root `CLAUDE.md`. Inherits the
master automatically. Fills the MASVS standard with a concrete template.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/std-owasp-masvs.md        # primary: mobile app security verification
@~/.claude/rules/lang-swift.md             # iOS — or lang-kotlin (Android), lang-csharp (MAUI),
                                           #        lang-typescript (React Native) — swap per stack
# @~/.claude/rules/lang-kotlin.md          # Android (Kotlin)
@~/.claude/rules/topic-authn-authz.md      # OAuth2/OIDC + PKCE, biometric/local auth
@~/.claude/rules/topic-cryptography.md     # Keychain/Keystore-backed keys
@~/.claude/rules/std-owasp-api.md          # the backend it talks to
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-privacy.md
@~/.claude/rules/topic-accessibility.md    # platform a11y (VoiceOver/TalkBack)
@~/.claude/rules/topic-i18n.md
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-release.md       # staged store rollout
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/topic-testing.md

## Stack
- Platform(s): <iOS (Swift) / Android (Kotlin) / Flutter / React Native>
- Backend API: <...>; auth: <...>

## Project-specific rules
- **Device is hostile:** the backend enforces all security; the client is a convenience layer
  (`@rules/std-owasp-masvs.md`).
- Secrets/keys in Keychain/Keystore — never in the bundle, source, or plaintext storage; no
  secrets in logs/screenshots/backups/clipboard.
- TLS with validation (consider cert pinning); no cleartext traffic; validate all IPC/deep
  links/intents.
- Local/biometric auth bound to a Keychain/Keystore secret, not a bypassable client flag.
- Staged store rollout with crash/ANR monitoring; forced-update path for critical fixes.
- **Design:** follow the platform design system — Apple HIG (iOS) / Material Design 3
  (Android); honor platform a11y and i18n conventions (`@rules/reference-style-guides.md`).
```
