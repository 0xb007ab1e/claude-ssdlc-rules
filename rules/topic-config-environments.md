# Topic: Configuration & Environments

12-Factor config discipline and clean environment separation. Secrets are governed by
`@rules/workflow-secrets.md`; this is about non-secret config and environment parity.

## Configuration
- **Config in the environment**, not in code (12-Factor III). The same built artifact runs in
  every environment; only config differs — no environment-specific builds or branches.
- **Validate config at startup** against a schema; **fail fast** (refuse to boot) on missing/
  invalid values rather than failing later at runtime. Provide a documented `.env.example`.
- Strong typing for config (parse to typed values); sane, safe defaults; defaults must be the
  secure/conservative option (master §2).
- No secrets in plain config/VCS — pull from the secret manager (`@rules/workflow-secrets.md`).
  Don't log full resolved config (may contain secrets — redact, `@rules/topic-logging-observability.md`).

## Environments
- Maintain **dev/test/staging/prod parity** (12-Factor X): same OS, runtime, dependency
  versions, and backing-service types across environments — minimize drift.
- **Isolate** environments: separate accounts/projects/namespaces, credentials, data stores,
  and networks. Never let non-prod reach prod data or services (master §5; no prod data in
  non-prod).
- Promote the **same artifact** through environments (build once, deploy many); never rebuild
  per environment.

## Feature flags
- Use flags to decouple deploy from release and to hide incomplete work (enables trunk-based
  dev — `@rules/workflow-git.md`). Default new flags to **off/safe**.
- Flags are short-lived: track and **remove stale flags** to avoid combinatorial debt.
- Don't gate security controls behind a flag that can be disabled to bypass them; evaluate
  authorization flags server-side.
- Changing a flag is a production change — audit it (`@rules/workflow-release.md`).

## References
- **The Twelve-Factor App** — 12factor.net (config, parity, processes, disposability).
- Feature-flag practice (OpenFeature — openfeature.dev). Index: `@rules/reference-style-guides.md`.
