# Standard: OWASP SAMM (Software Assurance Maturity Model)

A model for **measuring and improving** the security posture of the SDLC over time. Use it
to assess where a team/project sits and to pick the next improvement, not as a per-PR gate.

## Five business functions × three security practices each
1. **Governance** — Strategy & Metrics · Policy & Compliance · Education & Guidance.
2. **Design** — Threat Assessment · Security Requirements · Security Architecture.
3. **Implementation** — Secure Build · Secure Deployment · Defect Management.
4. **Verification** — Architecture Assessment · Requirements-driven Testing · Security
   Testing.
5. **Operations** — Incident Management · Environment Management · Operational Management.

## How to use it
- **Assess** each practice at maturity level 1–3 (informal → defined → optimized).
- **Set targets** proportional to risk; close the biggest gaps first.
- Map practices to the concrete controls in this ruleset:
  - Threat Assessment → `@rules/workflow-threat-model.md`
  - Secure Build / Deployment → `@rules/workflow-cicd.md`, `@rules/std-supplychain.md`
  - Security Testing → master §4, `@rules/std-owasp.md` (ASVS)
  - Defect / Incident Management → `@rules/workflow-vuln-mgmt.md`
  - Policy & Compliance → `@rules/std-nist.md`, `@rules/std-iso27001.md`, `@rules/std-soc2.md`
- **Re-assess periodically** and track maturity as a metric.
