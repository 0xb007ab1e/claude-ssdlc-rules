# Standard: SOC 2 (Trust Services Criteria)

Relevant for SaaS/service organizations demonstrating controls to customers. SOC 2 is about
**operating controls consistently and evidencing them**, not a fixed tech checklist.

## Trust Services Criteria
- **Security (Common Criteria — required):** access control, change management, risk
  assessment, monitoring, incident response, logical/physical access, vendor management.
- **Availability:** capacity, backups, DR, monitoring, SLAs (if you commit to uptime).
- **Processing Integrity:** processing is complete, valid, accurate, timely, authorized.
- **Confidentiality:** protect data designated confidential (encryption, access limits,
  retention/disposal).
- **Privacy:** handle personal information per notice/consent (overlaps `@rules/std-privacy.md`).

## What this means for engineering
- **Change management:** every prod change is reviewed, tested, approved, and traceable
  (PR + CI evidence — `@rules/workflow-git.md`, `@rules/workflow-cicd.md`).
- **Access control:** least-privilege, provisioning/deprovisioning, periodic access reviews,
  MFA on admin access. Evidence the reviews.
- **Logging & monitoring:** security events logged, alerted, retained; tamper-resistant.
- **Vulnerability & incident management:** documented, on SLAs, with evidence
  (`@rules/workflow-vuln-mgmt.md`).
- **Encryption & data handling:** in transit/at rest per master §5; key management.
- **Vendor/subprocessor management:** assess and track third parties.

> The auditable difference: controls must run **continuously over the audit period** and
> produce evidence (tickets, logs, review records). Design controls to emit evidence
> automatically.

## Related compliance & governance frameworks
Most controls here map across other frameworks — implement once, evidence many:
`@rules/std-iso27001.md` (ISMS) · `@rules/std-nist.md` (800-53) · `@rules/std-fedramp.md`
(US federal) · `@rules/std-hitrust.md` (healthcare) · `@rules/std-csa-ccm.md` (cloud) ·
`@rules/std-privacy.md` (privacy). Assess maturity with `@rules/std-samm.md`.
