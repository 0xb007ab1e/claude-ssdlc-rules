# Rule: Release & Deployment

How changes get versioned, shipped, and rolled back safely. Builds on
`@rules/workflow-cicd.md` (gates) and `@rules/std-supplychain.md` (integrity).

## Versioning & changelog
- **Semantic Versioning** (MAJOR.MINOR.PATCH): breaking / feature / fix. Public contracts
  (APIs, libraries) never break without a major bump (`@rules/topic-api-design.md`).
- Maintain a human-readable **CHANGELOG** per release; automate from Conventional Commits
  where possible (`@rules/workflow-git.md`).
- Tag releases in VCS; releases are built from a tagged, immutable commit.

## Build once, promote
- **One artifact** built once and promoted through environments (`@rules/topic-config-environments.md`);
  never rebuild per environment. Artifact is signed + SBOM'd (`@rules/std-supplychain.md`).
- Deploy is automated and repeatable (no manual prod steps); deploys are themselves auditable.

## Safe rollout
- **Decouple deploy from release** with feature flags (`@rules/topic-config-environments.md`).
- Progressive delivery: **canary or blue-green**, watch SLOs/error budget
  (`@rules/topic-reliability.md`), and **auto-rollback** on regression.
- **Database migrations are backward-compatible** so app and schema can deploy independently
  and roll back safely (expand/contract — `@rules/topic-database.md`).
- Every release has a tested **rollback/forward-fix** path before it ships.

## Verification & records
- Smoke/health checks post-deploy; readiness gates traffic. Roll back fast on failure.
- Record what shipped (version, commit, artifact digest, who, when) for traceability and
  audit (`@rules/std-soc2.md` change management).
- Don't release on a failing gate; don't release what you can't roll back.
