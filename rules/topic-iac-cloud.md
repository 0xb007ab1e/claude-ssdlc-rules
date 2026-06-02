# Topic: Infrastructure as Code & Cloud Security

Fills the "scan IaC" reference in `@rules/workflow-cicd.md` with concrete rules. Pairs with
`@rules/std-cis.md` (benchmarks) and `@rules/topic-container-k8s.md`.

## Infrastructure as Code
- **All infrastructure is code** (Terraform/OpenTofu, Pulumi, CloudFormation, Bicep) —
  no click-ops in production. Changes go through PR review + CI like app code.
- **Scan IaC** in CI (tfsec/checkov/KICS/Trivy); block on high/critical misconfig.
- **Remote, encrypted, locked state**; never commit state files or `.tfvars` with secrets.
  Pull secrets from a vault at apply time.
- **Pin** provider/module versions; review third-party modules before use (supply chain —
  `@rules/std-supplychain.md`).
- Plan/apply with least-privilege CI identity (OIDC, not static keys); require approval for
  prod applies; keep environments in separate state/accounts.

## Cloud configuration (provider-agnostic)
- **IAM least privilege:** no wildcard `*` actions/resources; one role per workload; no
  long-lived user access keys (use roles/workload identity/OIDC); MFA on human privileged
  access; periodic access review (`@rules/std-soc2.md`).
- **Network private-by-default:** resources in private subnets; no `0.0.0.0/0` ingress
  except deliberate edges; security groups deny by default; no public storage buckets/blobs.
- **Encryption on:** encrypt volumes, databases, object storage, and queues at rest with
  KMS-managed keys (`@rules/topic-cryptography.md`); enforce TLS in transit.
- **Logging on:** enable audit/flow/access logs (CloudTrail/Activity Log/Audit Logs) and
  ship to a central, protected, retained store (`@rules/topic-logging-observability.md`).
- **No secrets in:** env vars baked into images, user-data, or tags — use the cloud secret
  manager (`@rules/workflow-secrets.md`).
- **Tag & classify** resources (owner, env, data-classification) to drive policy and cost.
- **Backups + tested restores**, multi-AZ/region for critical data; guardrails via
  org policy / SCP / Azure Policy / GCP Org Policy.

## References
- **AWS / Azure / GCP Well-Architected** (Security pillar); **CIS Benchmarks** — cisecurity.org.
- **HashiCorp Terraform** style + best practices. Index: `@rules/reference-style-guides.md`.
