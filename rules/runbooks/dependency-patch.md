# Runbook: Dependency / CVE Patch

> Copy to `docs/runbooks/dependency-patch.md` and fill in `<...>`.
> Rules: `@rules/workflow-cve-management.md`, `@rules/workflow-vuln-mgmt.md`.

## When to use
- A vulnerable dependency is flagged (SCA, advisory, or new CISA KEV entry matching the SBOM).

## Severity / impact
- Score with CVSS + EPSS + KEV and assess reachability/exposure
  (`@rules/workflow-cve-management.md`); set the remediation SLA (Critical/KEV: 24–72h).

## Prerequisites & access
- The SBOM to locate every affected artifact/version; repo write + CI access.

## Steps
1. Confirm exposure: is the vulnerable code path reachable / the component exposed? Record a
   **VEX** status (`affected` / `not affected` + justification).
2. Determine the fixed version from the advisory (OSV/GHSA/NVD).
3. **Upgrade** the dependency (preferred): `<update + lockfile cmd>`. If no fix exists, apply a
   compensating control and track a time-boxed waiver.
4. Run the full test + security gates (`@rules/workflow-cicd.md`); check for breaking changes.
5. Deploy via `runbooks/deploy.md`; for actively-exploited (KEV) issues, expedite.

## Verification
- Re-run SCA: the finding is gone for all affected artifacts. Add/confirm a regression or
  security test where applicable. Close the tracked finding with resolution + evidence.

## Escalation
- Actively-exploited / breach evidence → escalate to `runbooks/incident-response.md` and rotate
  any potentially exposed secrets (`runbooks/secret-rotation.md`).

## Related
- `runbooks/deploy.md`, `runbooks/incident-response.md`; `@rules/workflow-cve-management.md`.

---
_Last validated: <date>. Owner: <team>._
