# Rule: Threat Modeling (design-time)

Required for every new service and for significant changes to trust boundaries, auth,
data flows, or external interfaces. Do it **before** implementation.

## Method — STRIDE over a data-flow diagram
1. **Diagram** the system: external entities, processes, data stores, data flows, and
   **trust boundaries** (where data crosses a privilege/network/ownership line).
2. For each element/flow, enumerate threats by **STRIDE**:
   - **S**poofing → authentication
   - **T**ampering → integrity (signing, hashing, validation)
   - **R**epudiation → audit logging, non-repudiation
   - **I**nformation disclosure → encryption, access control, redaction
   - **D**enial of service → rate limiting, quotas, timeouts, backpressure
   - **E**levation of privilege → authorization, least privilege, sandboxing
3. **Rate** each threat (likelihood × impact); decide mitigate / accept / transfer.
4. **Mitigate** by mapping to concrete controls and standard modules
   (`std-owasp`, `std-owasp-proactive`, `std-cwe`).
5. **Record** the model (diagram + threats + decisions) in `docs/security/threat-model.md`
   and revisit it when the design changes.

## Focus areas
- Every trust boundary needs explicit authN + authZ and input validation.
- Identify and classify all data crossing boundaries; apply master §5 data-protection rules.
- Abuse cases become security tests (see master §4) and DAST scenarios.
- Use **`@rules/std-mitre-attack.md`** to enumerate realistic adversary techniques per trust
  boundary and check you'd detect them; for ML/agent systems add `@rules/std-owasp-llm.md`.
