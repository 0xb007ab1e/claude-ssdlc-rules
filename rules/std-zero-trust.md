# Standard: Zero Trust Architecture (NIST SP 800-207)

"Never trust, always verify." No implicit trust from network location — every request is
authenticated, authorized, and encrypted regardless of where it originates.

## Tenets
- **No network-based trust:** being "inside the perimeter" grants nothing. Internal
  service-to-service traffic is authenticated and encrypted (mTLS) just like external.
- **Per-request authZ:** evaluate every access against policy using identity, device
  posture, and context — not a one-time login. Continuous/dynamic, not perimeter-once.
- **Least privilege + just-in-time:** grant the minimum access for the task, time-boxed;
  no standing broad privileges.
- **Assume breach:** segment to limit lateral movement; minimize blast radius; monitor and
  log everything (`@rules/topic-logging-observability.md`).

## Engineering implications
- **Strong workload & user identity:** every service has a cryptographic identity (SPIFFE/
  workload identity); humans use phishing-resistant MFA (`@rules/topic-authn-authz.md`).
- **mTLS everywhere** between services (service mesh or explicit); encrypt all traffic
  (`@rules/topic-cryptography.md`).
- **Policy as code:** centralized policy engine (OPA/Cedar) evaluated at each access point;
  default deny.
- **Micro-segmentation:** network policies default-deny (`@rules/topic-container-k8s.md`,
  `@rules/topic-iac-cloud.md`); isolate workloads and data per sensitivity.
- **Device & posture signals** feed access decisions for sensitive resources.
- **Continuous verification & monitoring:** detect anomalies, re-evaluate sessions, revoke
  fast. Short-lived credentials over long-lived (`@rules/workflow-secrets.md`).
