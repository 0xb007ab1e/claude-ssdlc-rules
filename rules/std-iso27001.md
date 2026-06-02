# Standard: ISO/IEC 27001 (+ 27002 controls)

Relevant when the organization runs an ISMS or pursues certification. For development work,
honor the Annex A control themes that touch software:

## Information Security Management System (ISMS)
- Decisions are risk-based: identify information assets, assess risk, treat per a documented
  risk treatment plan. Maintain a Statement of Applicability for selected controls.
- Everything is documented, reviewed, and continually improved (PDCA cycle).

## Annex A control themes for software/engineering
- **Organizational:** policies, access control policy, supplier/third-party security,
  threat intelligence, secure-by-design requirements, incident management.
- **People:** least privilege, separation of duties, security awareness, access removal on
  role change.
- **Physical:** protect facilities and media (mostly infra/ops concern).
- **Technological:**
  - Access control & privileged access management (A.8.2–8.5).
  - Cryptography & key management (A.8.24) — see master §5, `@rules/workflow-secrets.md`.
  - **Secure development** (A.8.25–8.31): secure dev policy, secure SDLC, secure coding,
    security testing, separation of dev/test/prod, outsourced-development oversight,
    change management — this ruleset implements these.
  - Logging & monitoring (A.8.15–8.16); protection of logs.
  - Data masking, data leakage prevention, backup (A.8.10–8.13).
  - Vulnerability management (A.8.8) — see `@rules/workflow-vuln-mgmt.md`.

> Keep evidence: link controls to concrete artifacts (this ruleset, CI gate results, review
> records, threat models) so audits map cleanly.
