# Standard: NIST SSDF (SP 800-218) + SP 800-53

## Secure Software Development Framework (SP 800-218 SSDF)
Organize secure-development work into the four SSDF practice groups:

- **PO — Prepare the Organization:** define security requirements, roles, and toolchains;
  establish criteria for security checks (this ruleset *is* that definition).
- **PS — Protect the Software:** protect code from tampering (access control, signing),
  protect releases (signed artifacts, provenance — `@rules/std-supplychain.md`), and
  archive each release with its integrity data.
- **PW — Produce Well-Secured Software:** threat-model designs
  (`@rules/workflow-threat-model.md`), reuse vetted secure components, follow secure-coding
  rules (language + `@rules/std-owasp-proactive.md`), and review/test for vulnerabilities
  (master §4, `@rules/workflow-cicd.md`).
- **RV — Respond to Vulnerabilities:** monitor, triage, and remediate on SLAs, with root-
  cause analysis (`@rules/workflow-vuln-mgmt.md`).

## SP 800-53 control families (apply by data sensitivity)
Select and implement controls proportional to system impact (low/moderate/high). Most-
relevant families for application work:

- **AC** Access Control — least privilege, separation of duties, RBAC, session control.
- **IA** Identification & Authentication — MFA, credential management, device identity.
- **AU** Audit & Accountability — security event logging, protection, and retention.
- **SC** System & Communications Protection — encryption in transit/at rest, boundary
  protection, key management.
- **SI** System & Information Integrity — flaw remediation, malware/intrusion detection,
  input validation, error handling.
- **CM** Configuration Management — baseline configs, least functionality, change control.
- **RA** Risk Assessment — vulnerability scanning, risk-based prioritization.
- **CP / IR** Contingency Planning & Incident Response — backups, runbooks, response.

> For FedRAMP/government context, map to the appropriate 800-53 baseline and document the
> control implementation (see `@rules/std-fedramp.md`). For Zero Trust architecture see
> `@rules/std-zero-trust.md` (SP 800-207). Otherwise use these families as a coverage checklist.
