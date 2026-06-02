# Topic: Cryptography

Concrete algorithm/parameter guidance behind master §5. **Never roll your own crypto** —
use vetted, maintained libraries (libsodium, ring/RustCrypto, Tink, the platform stdlib).

## Approved algorithms (current)
- **Symmetric encryption:** AES-256-GCM or ChaCha20-Poly1305 (AEAD — authenticated). Never
  ECB; never unauthenticated CBC without a separate MAC. Unique random nonce per message.
- **Hashing (integrity):** SHA-256 / SHA-512 / SHA-3. Never MD5 or SHA-1.
- **Password hashing:** argon2id (preferred), bcrypt, or scrypt with sound work factors.
- **Key derivation:** HKDF (from key material); argon2id/PBKDF2 (from passwords).
- **MAC:** HMAC-SHA-256+ or the AEAD's built-in tag.
- **Asymmetric:** RSA-3072+ (or 2048 minimum, legacy), or ECC P-256/P-384, or
  Ed25519/X25519 (preferred for signatures/key exchange).
- **TLS:** 1.3 preferred, 1.2 minimum; disable 1.0/1.1 and weak ciphers; enable forward
  secrecy. HSTS on web.

## Prohibited / deprecated
- DES/3DES, RC4, Blowfish, ECB mode, MD5, SHA-1, RSA < 2048, custom ciphers, hardcoded IVs,
  static nonces, `Math.random()`/non-CSPRNG for any security purpose.

## Practices
- **Randomness:** always a CSPRNG (`secrets`, `crypto/rand`, `RandomNumberGenerator`,
  Web Crypto) — never a general-purpose PRNG.
- **Keys:** generated, stored, and rotated via KMS/HSM (see `@rules/workflow-secrets.md`);
  separate keys per purpose; never hardcoded or logged; enforce rotation and versioning so
  old data stays decryptable during rollover.
- **Encrypt-then-MAC** or use AEAD; verify before decrypting.
- **Constant-time comparison** for secrets/MACs/tokens (avoid timing leaks).
- **Zeroize** key material/plaintext in memory as soon as it's no longer needed; minimize its
  lifetime (language caveats + techniques in `@rules/topic-resource-management.md`).
- **Crypto-agility:** wrap crypto behind an interface and store an algorithm/version tag
  with ciphertext so primitives can be upgraded without data loss.
- **FIPS 140-2/3** validated modules where regulatory context requires it.
- Plan for **post-quantum**: prefer larger keys and agility; track NIST PQC migration for
  long-lived secrets.

## References
- **NIST SP 800-57** (key management), **SP 800-175B**, **SP 800-131A** (algorithm transitions).
- **OWASP Cryptographic Storage Cheat Sheet**; **NIST Post-Quantum Cryptography** project.
- Index: `@rules/reference-style-guides.md`.
