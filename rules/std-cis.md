# Standard: CIS Benchmarks & Controls (Hardening)

Apply CIS hardening to runtime/infrastructure. Use the specific CIS Benchmark for each
platform in use (OS, container, Kubernetes, cloud, database, web server).

## Configuration hardening
- Start from the relevant **CIS Benchmark** and codify it as scanned policy (IaC + a
  config scanner in CI, see `@rules/workflow-cicd.md`). Document any justified deviations.
- **Least functionality:** disable/remove unused services, ports, accounts, sample content,
  and default credentials. Change all defaults.
- **Containers:** non-root user, read-only root filesystem, drop all Linux capabilities then
  add back only those required, no privileged mode, pinned minimal base image, no secrets
  in layers, healthchecks defined.
- **Kubernetes:** enforce Pod Security Standards (restricted), NetworkPolicies (default
  deny), RBAC least privilege, no `hostPath`/host networking unless justified.
- **Cloud:** private-by-default networking, no public storage buckets, encrypted volumes,
  flow/audit logging on, MFA on privileged accounts, least-privilege IAM.

## CIS Critical Security Controls (operational baseline)
- Maintain inventories of assets and software; control installed software (allow-listing).
- Continuous vulnerability management (ties to `@rules/workflow-vuln-mgmt.md`).
- Centralized, protected audit logging and monitoring.
- Secure configuration enforced and drift-detected; least-privilege access management.
- Data protection and recovery (encryption, backups, tested restores).
