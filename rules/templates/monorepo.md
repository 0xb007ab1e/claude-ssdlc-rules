# Template: Monorepo — project CLAUDE.md

For a multi-package/multi-service repository. Copy to the repo root `CLAUDE.md`. Inherits the
master automatically. **Composition tip:** put shared rules here and add a per-package
`CLAUDE.md` (loaded on demand) that imports the modules specific to that package's stack.

```markdown
# <RepoName> — monorepo rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.
> Each package/app has its own packages/<name>/CLAUDE.md importing its stack modules.

## Repo-wide modules (apply to all packages)
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/std-supplychain.md
@~/.claude/rules/topic-config-environments.md
@~/.claude/rules/topic-documentation.md
@~/.claude/rules/workflow-git.md
@~/.claude/rules/workflow-code-review.md
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/topic-license-compliance.md

## Stack
- Tooling: <Nx / Turborepo / Bazel / pnpm workspaces / Cargo workspace>
- Packages: <list apps/libs>

## Monorepo-specific rules
- **One source of truth for versions:** centralized/pinned dependency management; a single
  lockfile (or workspace-managed) committed; no divergent versions of the same dep.
- **Clear ownership & boundaries:** CODEOWNERS per path; enforce module/dependency boundaries
  (no forbidden cross-package imports); changes reviewed by the owning team.
- **Affected-only CI:** build/test/lint only what a change affects (with caching), but
  security scans (SAST/SCA/secret) cover the whole graph. All gates from
  `@rules/workflow-cicd.md` still apply per package.
- **Independent or coordinated releases:** define versioning strategy (independent vs.
  lockstep) and changelog generation per package (`@rules/workflow-release.md`).
- Per-package `CLAUDE.md` imports its language/standard modules (e.g. a service package adds
  `@~/.claude/rules/lang-go.md` + `std-owasp-api.md`); this root file holds only shared rules.
```
