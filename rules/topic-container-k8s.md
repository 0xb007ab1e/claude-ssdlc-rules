# Topic: Containers & Kubernetes

Expands the container/K8s items in `@rules/std-cis.md`. Apply the relevant CIS Benchmark
(Docker, Kubernetes, cloud-managed K8s) and enforce via policy + scanning.

## Container images
- **Minimal base** (distroless/alpine/scratch); pin by **digest**, not tag. Multi-stage
  builds so build tools don't ship in the runtime image.
- **Non-root user**; `USER` set; read-only root filesystem; drop all Linux capabilities,
  add back only what's required; no `--privileged`.
- **No secrets in layers/ENV/ARG**; inject at runtime (`@rules/workflow-secrets.md`).
- **Scan images** in CI for OS/lib CVEs (Trivy/Grype) and misconfig; block on high/critical;
  rescan on a schedule (`@rules/workflow-vuln-mgmt.md`).
- **Sign images** and verify on deploy (cosign/Sigstore — `@rules/std-supplychain.md`);
  generate an SBOM per image.
- Define `HEALTHCHECK`/probes; set resource requests/limits; one concern per container.

## Kubernetes
- **Pod Security Standards = restricted** (or equivalent admission policy via OPA
  Gatekeeper/Kyverno): non-root, no privilege escalation, dropped capabilities, read-only FS,
  seccomp `RuntimeDefault`.
- **NetworkPolicies default-deny**; allow only required flows. No `hostNetwork`/`hostPID`/
  `hostPath` unless justified and reviewed.
- **RBAC least privilege**; no cluster-admin for workloads; one ServiceAccount per workload;
  disable automount of SA tokens where unused.
- **Secrets:** use a secrets store / external secrets operator + encryption at rest for etcd;
  never plain ConfigMaps for sensitive data.
- **Namespaces** isolate tenants/environments; resource quotas + limit ranges prevent
  noisy-neighbor/DoS.
- Enable **audit logging** on the API server; ship to central logging
  (`@rules/topic-logging-observability.md`). Keep nodes and control plane patched.
- Admission control blocks unsigned images, `:latest` tags, and policy violations.

## References
- **CIS Docker/Kubernetes Benchmarks** — cisecurity.org; **NSA/CISA Kubernetes Hardening Guide**.
- **Docker / Kubernetes** official best practices; **OWASP Docker Top 10**. Index: `@rules/reference-style-guides.md`.
