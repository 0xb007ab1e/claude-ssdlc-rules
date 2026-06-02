# Standard: HITRUST CSF (Healthcare)

For organizations handling healthcare data that need HITRUST certification. The HITRUST CSF
is a **harmonizing framework** that maps HIPAA, NIST, ISO 27001, PCI, and others into one
certifiable control set. Pairs with `@rules/std-privacy.md` (HIPAA) and `@rules/std-nist.md`.

> **Apply when:** healthcare customers/regulators require HITRUST. **Otherwise**
> `@rules/std-privacy.md` (HIPAA) + `@rules/std-soc2.md` usually suffice for healthcare SaaS.

## Foundations
- HITRUST is **risk- and compliance-based**: control requirements scale with organizational,
  system, and regulatory **risk factors** (e.g. data volume, internet-facing, regulated data).
- Certification levels (e.g. e1 / i1 / r2) reflect assurance depth; r2 is the comprehensive,
  risk-based assessment.
- Because it cross-references other frameworks, satisfying HITRUST largely means satisfying
  this ruleset's HIPAA, NIST, ISO, and access/crypto/logging controls — then evidencing them.

## Control domains (the 19, condensed)
Information protection program & risk management; access control & identity
(`@rules/topic-authn-authz.md`); endpoint, mobile, and portable media protection; wireless &
network protection; configuration & vulnerability management (`@rules/std-cis.md`,
`@rules/workflow-vuln-mgmt.md`); transmission & at-rest protection (`@rules/topic-cryptography.md`);
password/credential management; audit logging & monitoring
(`@rules/topic-logging-observability.md`); education & awareness; third-party/supplier
assurance; incident management (`@rules/workflow-incident-response.md`); business continuity &
disaster recovery (`@rules/topic-reliability.md`); data protection & privacy
(`@rules/std-privacy.md`); physical & environmental security.

## Engineering implications
- Treat PHI as **restricted** data (master §5); encrypt in transit/at rest, least-privilege
  access, full audit trail, and Business Associate Agreements with vendors touching PHI.
- Maintain **mapped evidence**: because controls map across frameworks, keep one evidence set
  that satisfies HITRUST, HIPAA, and the others (`@rules/std-soc2.md`, `@rules/std-iso27001.md`).

> Niche — only when healthcare customers/regulators require HITRUST certification.
