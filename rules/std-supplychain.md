# Standard: Software Supply Chain Security (SLSA + SSDF PS)

Protect the path from source to deployed artifact against tampering and compromise.

## Dependencies
- Pin every dependency with a lockfile **and** cryptographic hashes; pin CI actions and
  container base images by **digest**, not floating tags.
- Vet new dependencies (maintenance, provenance, license, known CVEs) before adoption;
  prefer fewer, well-maintained deps. Continuous SCA (`@rules/workflow-vuln-mgmt.md`).
- Use a pull-through/private registry where possible; guard against dependency confusion
  (claim internal package names; scope/namespace private packages).

## Build integrity (target SLSA levels)
- **Scripted, reproducible builds** on ephemeral, isolated runners — no manual steps, no
  builder access to other tenants' secrets.
- Generate **provenance/attestation** describing how the artifact was built (SLSA
  provenance) and store it with the artifact.
- **Sign artifacts and provenance** (e.g. Sigstore/cosign); verify signatures before deploy.
- Aim for **SLSA Build L3** for production artifacts (non-falsifiable provenance, isolated
  build); minimum L2 (signed provenance) for internal tooling.

## Transparency & verification
- Produce an **SBOM** (CycloneDX or SPDX) per release; keep it queryable for CVE impact.
- Verify integrity of third-party artifacts and updates before use (checksums/signatures);
  no insecure auto-update without verification.
- Maintain a `SECURITY.md` and, for published software, signed releases with provenance.

> Integrates with `@rules/workflow-cicd.md` (gates) and `@rules/std-nist.md` (SSDF PS group).
