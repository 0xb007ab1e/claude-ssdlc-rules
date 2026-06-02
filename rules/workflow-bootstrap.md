# Rule: Project Bootstrap

The procedure for starting a new project so it inherits the SSDLC ruleset correctly from
commit one. Ties the templates, modules, workflows, and docs together. Run this when creating
a repo.

## Steps
1. **Classify the project.** Kind (service / library / CLI / frontend / mobile / data /
   infra / AI), stack/language, data sensitivity & classification (master §5), and any
   compliance context (PCI/HIPAA/SOC2/FedRAMP). This drives every choice below.
2. **Pick the matching template** from `~/.claude/rules/templates/` (see README table). Copy it
   to the repo-root **`CLAUDE.md`**. It inherits `~/.claude/CLAUDE.md` automatically.
3. **Compose imports — lean.** Uncomment/keep only the `@import` modules that actually apply
   (most projects need ~6–10; see master §6 "import lean"). Fill the project-specific rules
   (stack, data classification, deviations-with-reasons).
4. **Create the repo skeleton:** `README.md`, `LICENSE` (decide deliberately —
   `@rules/topic-license-compliance.md`), `.gitignore`, `SECURITY.md`, `.editorconfig`,
   `docs/`, `docs/runbooks/`, `.env.example` (no real secrets — `@rules/workflow-secrets.md`),
   and a `CODEOWNERS` if shared.
5. **Local dev setup** so the team can clone-to-running fast (`@rules/topic-local-dev.md`):
   reproducible env (devcontainer/compose), task runner, seed/synthetic data, pre-commit hooks
   (format/lint/secret-scan).
6. **CI security gates** from `@rules/workflow-cicd.md` — lint, test+coverage, SAST, SCA,
   secret-scan, IaC/image scan — wired as **merge-blocking**. Branch protection + signed commits
   (`@rules/workflow-git.md`).
7. **Threat-model** if it's a new service or introduces a trust boundary
   (`@rules/workflow-threat-model.md`); record in `docs/security/threat-model.md`.
8. **Seed docs & runbooks:** `docs/` per `@rules/topic-documentation.md`; copy the standard
   runbooks for deployable services into `docs/runbooks/` and fill them
   (`@rules/workflow-runbooks.md`).
9. **Test scaffold** with the coverage gate (master §4, `@rules/topic-testing.md`) green on an
   empty project, so the gate is enforced from the start.
10. **First commit** with the mandated noreply email (master §1); open a PR; confirm all gates
    pass before merging to `main`.

## Bootstrap "done" checklist
- [ ] Root `CLAUDE.md` from the right template, lean imports, project rules filled.
- [ ] Repo skeleton (README, LICENSE, SECURITY.md, .gitignore, .env.example, docs/, runbooks/).
- [ ] One-command local setup works; pre-commit hooks active.
- [ ] CI gates green and merge-blocking; branch protection + signing on.
- [ ] Threat model recorded (if a service); data classification documented.
- [ ] Runbooks present (deployable services); docs build wired.
- [ ] Coverage gate enforced on the empty/initial codebase.

> Subdirectories with distinct concerns can carry their own `CLAUDE.md` (loaded on demand) —
> e.g. a monorepo package importing its own stack modules (`@rules/templates/monorepo.md`).
