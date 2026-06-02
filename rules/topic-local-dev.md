# Topic: Local Development Experience

A fast, reproducible, secure local setup. Good DX makes the security/quality gates easy to
follow instead of bypassed. Pairs with `@rules/topic-config-environments.md` (parity) and
`@rules/workflow-bootstrap.md`.

## Reproducible & fast
- **One-command setup** ("clone to running"): a `setup`/`bootstrap` task and a documented
  README quickstart. New contributors productive in minutes, not days.
- **Pin the environment:** devcontainer / Nix / `docker compose` for backing services (DB,
  queue, cache) at **versions matching prod** (dev/prod parity — `@rules/topic-config-environments.md`).
  Avoid "works on my machine."
- **Task runner** (make / just / npm scripts) with standard targets: `setup`, `build`, `test`,
  `lint`, `fmt`, `run`. Same commands locally and in CI.
- **Fast feedback:** watch/hot-reload; keep the unit suite seconds-fast (`@rules/topic-testing.md`).

## Safe by default
- **Local secrets** via a git-ignored `.env` + committed `.env.example` (placeholders only);
  **never real production secrets or prod data locally** (`@rules/workflow-secrets.md`, master §5).
  Use synthetic/seed data; anonymize if derived from real data.
- Don't disable security controls in dev in ways that **hide** issues — mirror prod auth/TLS
  where feasible; if a control is relaxed locally, make it obvious and document why.
- **Pre-commit hooks** shift checks left: format, lint, secret-scan, fast tests — same gates CI
  enforces (`@rules/workflow-git.md`, `@rules/workflow-cicd.md`).

## Consistency
- `.editorconfig` + shared formatter/linter config so style is automatic and uniform.
- Document the setup, common tasks, and gotchas in the README / an onboarding runbook
  (`@rules/topic-documentation.md`); keep it current (stale setup docs are a defect).

## References
- Dev Containers spec (containers.dev); 12-Factor (X. dev/prod parity).
  Index: `@rules/reference-style-guides.md`.
