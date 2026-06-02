# Standard: FedRAMP / FISMA (US Government)

For cloud services sold to US federal agencies (FedRAMP) or federal information systems
(FISMA). Built on **NIST SP 800-53** — see `@rules/std-nist.md` for the control families.

> **Apply when:** pursuing/holding a federal ATO or selling to the US government. **Skip
> otherwise** — for commercial assurance use `@rules/std-soc2.md` / `@rules/std-iso27001.md`.

## Foundations
- **FISMA** mandates the NIST Risk Management Framework (RMF) for federal systems; **FedRAMP**
  is the standardized program for authorizing cloud services (a "do once, use many times"
  authorization — ATO).
- **Categorize** the system impact level (FIPS 199: Low / Moderate / High) by confidentiality,
  integrity, availability. The level selects the FedRAMP/800-53 control baseline.
- Implement the baseline, document it in a **System Security Plan (SSP)**, and have it assessed
  by a 3PAO; maintain the authorization via **continuous monitoring (ConMon)**.

## Engineering implications
- Implement the **800-53 control families** proportional to the baseline (`@rules/std-nist.md`):
  AC, IA, AU, SC, SI, CM, CP, IR, RA, etc. Most are realized by this ruleset's modules.
- **FIPS 140-2/3 validated cryptography** is mandatory — use validated modules
  (`@rules/topic-cryptography.md`).
- **Boundary & inventory:** maintain an authorization boundary diagram and component
  inventory; everything in-boundary is controlled and monitored.
- **Continuous monitoring:** ongoing vulnerability scanning, monthly reporting, POA&M
  (Plan of Action & Milestones) for open findings with remediation timelines
  (`@rules/workflow-vuln-mgmt.md`).
- **Audit logging & retention** per AU controls (`@rules/topic-logging-observability.md`);
  incident reporting to US-CERT within required timelines (`@rules/workflow-incident-response.md`).
- Use **FedRAMP-authorized** services/infrastructure underneath; inherit and document their
  controls.

> Niche — only when pursuing federal authorization. Treat data as "restricted" (master §5)
> and keep audit-ready evidence (`@rules/std-soc2.md`, `@rules/std-iso27001.md`).
