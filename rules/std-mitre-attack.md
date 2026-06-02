# Standard: MITRE ATT&CK (Detection Engineering)

A knowledge base of real-world adversary **tactics, techniques, and procedures (TTPs)**.
Use it to drive **detection and defense**, not just prevention — the attacker's-eye view that
complements the build-time controls in the other modules. Pairs with
`@rules/topic-logging-observability.md` and `@rules/workflow-incident-response.md`.

## How to use it
- **Tactics** = the adversary's goal at each stage (Initial Access, Execution, Persistence,
  Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement,
  Collection, Exfiltration, Impact). **Techniques** = how they achieve each.
- **Map your detections to techniques:** for the techniques relevant to your stack/threat
  model, ensure you log the right telemetry and have an alert. Find your **coverage gaps**
  (ATT&CK Navigator) and prioritize closing the high-likelihood ones.
- Feed **threat modeling** (`@rules/workflow-threat-model.md`): for each trust boundary, ask
  which ATT&CK techniques apply and whether you'd detect them.
- Drive **detection-as-code:** version detection rules, test them (can you trigger the alert
  in a safe range?), and treat coverage as a tracked metric.

## Engineering implications
- Emit security-relevant telemetry that makes techniques detectable: authentication events,
  process/command execution, privilege changes, network egress, secret access, config
  changes (`@rules/topic-logging-observability.md`). You can't detect what you don't log.
- Alert on technique signatures + anomalies; route to incident response with the mapped
  technique as context (`@rules/workflow-incident-response.md`).
- Use ATT&CK as a common vocabulary in post-mortems ("they used T1078 Valid Accounts") and to
  drive purple-team/adversary-emulation exercises.
- For LLM/agent systems, pair with `@rules/std-owasp-llm.md` (ATT&CK has emerging AI-focused
  TTPs / see MITRE ATLAS for ML-specific adversary techniques).

> Detection-focused; layers on top of the preventive controls — assume-breach (`@rules/std-zero-trust.md`).
