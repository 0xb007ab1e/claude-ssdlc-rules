# Rule: CI/CD Security Gates

Every pipeline enforces these gates. A failing gate blocks merge/release — no overrides
without a documented, time-boxed exception approved by a human.

## Required gates (in order)
1. **Build** — reproducible; pinned toolchain; no network access to untrusted sources.
2. **Lint & format** — zero errors; style enforced automatically.
3. **Unit + integration tests** with the coverage gate from master §4 (100% critical /
   90% line+branch elsewhere; no regression).
4. **SAST** — static analysis on first-party code; block on new high/critical findings.
5. **SCA** — dependency vulnerability scan; block on known high/critical CVEs without an
   accepted, time-boxed waiver.
6. **Secret scan** — block on any detected secret.
7. **IaC / container scan** — scan Dockerfiles, images, and infra-as-code for
   misconfiguration and vulnerable base layers.
8. **DAST / E2E** — dynamic test against a deployed ephemeral environment for services.

## Supply-chain integrity (see `@rules/std-supplychain.md`)
- Generate an **SBOM** (CycloneDX/SPDX) per build and store it with the artifact.
- **Sign artifacts** and generate provenance/attestation (e.g. SLSA, cosign/Sigstore).
- Pin all dependencies (lockfiles + hashes) and pin CI actions/images by digest, not tag.

## Pipeline hygiene
- Least-privilege CI credentials via OIDC/workload identity; no long-lived cloud keys.
- Build runners are ephemeral and isolated; untrusted PR code cannot access prod secrets.
- Protect `main`: required status checks + required review (see `@rules/workflow-git.md`).
- Fail closed: an errored/skipped security stage counts as a failure, not a pass.
