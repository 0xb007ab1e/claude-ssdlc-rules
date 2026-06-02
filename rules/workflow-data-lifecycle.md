# Rule: Data Lifecycle Management

Govern data from creation to deletion. Operationalizes master §5 and `@rules/std-privacy.md`.

## Classify & inventory
- Classify every dataset (public / internal / confidential / restricted) and tag PII/PHI/
  cardholder data; maintain a data inventory + data-flow map (feeds `@rules/workflow-threat-model.md`).
- Classification drives encryption, access, logging, retention, and residency rules
  automatically — don't decide handling ad hoc.

## Minimize & retain
- **Collect the minimum** needed for a stated purpose (`@rules/std-privacy.md` minimization).
- Define an explicit **retention period** per data class/type; document the purpose and legal
  basis. No indefinite "keep everything."
- **Enforce deletion** when retention expires or on a valid erasure request (GDPR/CCPA) —
  automated where possible, across primary stores, caches, search indexes, logs, **and
  backups** (or document backup-expiry handling). Track that deletion completed.

## Protect
- Encrypt in transit/at rest; least-privilege access; tenant isolation (master §5,
  `@rules/topic-database.md`).
- **Pseudonymize/anonymize** for analytics and non-prod; never use real personal data in
  non-production (synthesize or irreversibly mask).
- Control data residency/cross-border transfer per regulation (`@rules/std-privacy.md`).

## Backup & recovery
- Automated, **encrypted** backups on a schedule matching the data's RPO; protect backups
  with the same classification rules as the source.
- **Restore-test on a schedule** — an unverified backup doesn't count
  (`@rules/topic-reliability.md`). Define RTO and document the restore procedure (runbook).
- Immutable/offline copies for ransomware resilience on critical data.

## Disposal
- Securely destroy data and media at end of life (crypto-erase / secure wipe); decommission
  storage so residual data isn't recoverable. Record disposal for audit.
