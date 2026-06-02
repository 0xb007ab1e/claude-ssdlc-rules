# Rule: Vulnerability & Patch Management

## Continuous monitoring
- SCA runs in CI **and** on a schedule against `main` so new CVEs in existing deps surface
  even without a code change.
- Subscribe to advisories for the language ecosystem, base images, and key frameworks.
- Maintain the SBOM (see `@rules/std-supplychain.md`) so impact of a new CVE is queryable.
- For how findings are identified, scored (CVSS/EPSS/KEV), reachability-assessed (VEX), and
  tracked to closure, follow `@rules/workflow-cve-management.md`. This module owns the SLAs.

## Remediation SLAs (from disclosure/detection)
- **Critical (CVSS ≥ 9.0 or actively exploited):** patch/mitigate within **24–72h**.
- **High (7.0–8.9):** within **7 days**.
- **Medium (4.0–6.9):** within **30 days**.
- **Low (< 4.0):** next scheduled maintenance.
- If a fix isn't available, apply a compensating control and track it; never silently accept.

## Waivers
- Any accepted risk is documented (who, why, scope, expiry) and time-boxed; it auto-expires
  and re-blocks CI on lapse. No permanent ignores.

## Coordinated disclosure (for software you publish)
- Provide a `SECURITY.md` with a reporting channel and response expectations.
- Triage reports promptly, fix under embargo, then publish an advisory + patched release
  with CVE/credit. Notify affected downstreams.

## Incident response
When a vulnerability is actively exploited or a breach/outage occurs, escalate to the
dedicated process in `@rules/workflow-incident-response.md` (severity, containment, recovery,
blameless post-mortem). Routine, non-exploited findings stay in the SLA flow above.
