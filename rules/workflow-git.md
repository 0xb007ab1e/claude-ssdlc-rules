# Rule: Git & PR Workflow

Trunk-based development with short-lived branches.

## Branching
- `main` is always releasable and protected. No direct pushes; no force-push to `main`.
- Branch off `main`; keep branches short-lived (< ~2 days). Rebase, don't merge-commit, to
  stay current. Use feature flags to hide incomplete work rather than long-lived branches.
- Naming: `type/short-description` (e.g. `feat/oauth-pkce`, `fix/null-deref-parser`).

## Commits
- Commit author email: `134006168+0xb007ab1e@users.noreply.github.com` (mandate).
- **Sign commits** (GPG/SSH) where the platform supports it; CI verifies signatures.
- Conventional Commits format: `type(scope): summary` (`feat`, `fix`, `docs`, `refactor`,
  `test`, `chore`, `build`, `ci`, `perf`, `security`). Imperative mood, ≤72-char subject.
- Atomic commits: one logical change each; never mix refactor + behavior change.
- Never commit secrets, credentials, or generated artifacts. Pre-commit secret scan runs.

## Pull requests
- Every change to `main` goes through a PR — no exceptions, including your own.
- **Mandatory review:** at least one approving review; security-relevant changes
  (auth, crypto, data handling, dependencies, CI) require a security-focused review.
- PRs must be small and single-purpose. Large diffs get split.
- PR description states: what, why, risk, test evidence, and any security/privacy impact.
- All CI gates green before merge (see `@rules/workflow-cicd.md`). Merge is squash or
  rebase to keep `main` linear; no merge bubbles.
- Don't push or open PRs unless the user asked. End PR bodies per environment policy.

## Repository hygiene
- **No large/binary blobs in Git history** — use **Git LFS** (or an artifact store) for assets,
  datasets, and media; commit a `.gitattributes` for LFS-tracked types. A committed large file
  is permanent bloat (rewriting history is disruptive).
- Keep a sensible **`.gitignore`** (build output, deps, env files, local config); never commit
  secrets or generated artifacts (`@rules/workflow-secrets.md`).
- **Signature verification is enforced, not just enabled:** branch protection requires signed
  commits; CI/branch rules reject unsigned or unverified-author commits. Use the mandated
  noreply email (master §1).
- **Monorepos:** use `CODEOWNERS` per path; enforce module/dependency boundaries; scope CI to
  affected projects while running security scans across the graph (`@rules/templates/monorepo.md`).
- Protect history: no force-push to shared branches; require linear history; tag releases
  (`@rules/workflow-release.md`).
