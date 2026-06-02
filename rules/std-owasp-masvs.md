# Standard: OWASP MASVS (Mobile App Security)

For native/hybrid mobile apps (iOS/Android). Use the MASVS control groups as the
verification checklist; the MASTG provides test procedures. Remember: the device and client
are hostile environments — **the backend enforces all security** (see `@rules/std-owasp-api.md`).

## MASVS control groups
- **MASVS-STORAGE:** no sensitive data in plaintext on device; use Keychain/Keystore for
  secrets and keys; nothing sensitive in logs, backups, screenshots, clipboard, or caches.
- **MASVS-CRYPTO:** platform crypto APIs + Keychain/Keystore-managed keys; strong algorithms
  (`@rules/topic-cryptography.md`); no hardcoded keys.
- **MASVS-AUTH:** delegate to backend; OAuth2/OIDC + PKCE; biometric/local auth bound to a
  Keychain/Keystore-protected secret, not a client-side bypassable flag.
- **MASVS-NETWORK:** TLS 1.2+ with validation; consider certificate pinning; never disable
  cert checks; no cleartext traffic (`usesCleartextTraffic=false` / ATS on).
- **MASVS-PLATFORM:** safe IPC (validate intents/deep links/URL schemes); least permissions;
  protect exported components; guard WebViews (no `javascriptInterface` to untrusted content,
  no file access).
- **MASVS-CODE:** validate all input/IPC data; keep dependencies patched; handle errors
  safely; enable platform exploit mitigations.
- **MASVS-RESILIENCE:** (defense-in-depth, not a substitute for the above) anti-tampering,
  root/jailbreak awareness, obfuscation for high-risk apps; don't rely on it for security.
- **MASVS-PRIVACY:** minimize data collection; clear consent; honor platform privacy
  requirements (`@rules/std-privacy.md`).

## Practices
- Pick a verification level proportional to risk; run mobile SAST/DAST and dependency scans
  in CI. Never ship secrets in the app bundle — they are extractable.
