# Standard: CSA Cloud Controls Matrix (CCM)

The Cloud Security Alliance's cloud-specific control framework. Use it to assure cloud
service security and to clarify the **shared-responsibility** split between provider and
customer. Complements `@rules/topic-iac-cloud.md`, `@rules/std-cis.md`, and `@rules/std-iso27001.md`.

> **Apply when:** assuring cloud security to customers, pursuing CSA STAR, or assessing cloud
> vendors (CAIQ). Useful as a cloud checklist even without formal certification.

## Foundations
- The CCM is a control framework of domains spanning cloud security; it maps to ISO 27001,
  NIST, PCI, SOC 2, etc. — so implementing it reinforces the other standards modules.
- **CAIQ** (Consensus Assessments Initiative Questionnaire) is the companion self-assessment;
  the CSA STAR registry publishes provider assessments. Use CAIQ to evaluate vendors and to
  document your own posture.
- **Shared responsibility:** explicitly document which CCM controls are the cloud provider's,
  which are yours, and which are shared. Don't assume the provider covers a control.

## Representative domains (engineering-relevant)
- Identity & Access Management (`@rules/topic-authn-authz.md`, least-privilege IAM in
  `@rules/topic-iac-cloud.md`).
- Data Security & Encryption / key management (`@rules/topic-cryptography.md`, master §5).
- Application & Interface Security (`@rules/std-owasp.md`, `@rules/std-owasp-api.md`).
- Infrastructure & Virtualization / network security (`@rules/topic-iac-cloud.md`,
  `@rules/topic-container-k8s.md`).
- Logging & Monitoring (`@rules/topic-logging-observability.md`).
- Threat & Vulnerability Management (`@rules/workflow-vuln-mgmt.md`).
- Business Continuity & Operational Resilience (`@rules/topic-reliability.md`).
- Supply Chain / Cloud provider management (`@rules/std-supplychain.md`, vendor assessment).
- Security Incident Management (`@rules/workflow-incident-response.md`).

> Useful as a cloud-security checklist and vendor-assessment tool even without formal CSA
> STAR certification.
