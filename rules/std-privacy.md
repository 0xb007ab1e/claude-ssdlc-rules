# Standard: Privacy (GDPR / HIPAA / CCPA)

Apply whenever the system handles personal data. Ties directly into master §5
(encryption / redaction / isolation). Identify the applicable regime by data + jurisdiction.

## Cross-cutting privacy-by-design principles
- **Data minimization:** collect only what's needed for a stated purpose; don't retain
  "just in case." Define and enforce retention + deletion.
- **Purpose limitation:** use data only for the purpose it was collected for.
- **Lawful basis / consent:** capture consent or another lawful basis; make it revocable.
- **Privacy by design & default:** the most privacy-protective setting is the default.
- **Data subject rights:** support access, rectification, deletion ("right to be forgotten"),
  portability, and objection — design data models so a subject's data is findable/erasable.
- **Records & DPIA:** maintain processing records; run a Data Protection Impact Assessment
  for high-risk processing.

## GDPR specifics
- Lawful basis required; honor data-subject rights within statutory timelines.
- **Breach notification** to the supervisory authority within **72 hours** of awareness.
- Govern international transfers (SCCs/adequacy); bind processors with DPAs.

## HIPAA specifics (PHI)
- Apply the Security Rule safeguards: administrative, physical, technical (access control,
  audit controls, integrity, transmission security, encryption).
- Minimum necessary access; Business Associate Agreements with vendors touching PHI.
- Breach notification per the Breach Notification Rule.

## CCPA/CPRA specifics
- Honor rights to know, delete, correct, and opt out of sale/sharing; provide notice.
- Treat "sale/sharing" of personal information carefully; support a global opt-out signal.

## Engineering controls
- Classify and **tag PII/PHI** at the schema level; let tags drive encryption, access,
  logging, and retention automatically.
- **Redact** personal data from logs, traces, analytics, and errors by default (master §5).
- **Pseudonymize/anonymize** where possible; isolate personal data stores; encrypt in
  transit/at rest; never use real personal data in non-production.
