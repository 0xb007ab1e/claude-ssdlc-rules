# Rule: Issue Tracking & Open Contribution

All product development is tracked with issues; external contributions enter the same review
pipeline as internal work. Complements `@rules/workflow-git.md` (PR flow) and
`@rules/workflow-code-review.md` (what reviewers check).

## Track everything with issues
- Every feature, change, and bug has a tracking issue (the platform's tracker) capturing the
  requirement/acceptance and status. Work does not start untracked.
- PRs reference their issue (`Closes #N` / `Fixes #N`) so every merged change traces back to a
  requirement; branch names may carry the issue id.
- Issues are the single source of truth for planned / in-progress / shipped — keep status current;
  don't let the tracker drift from reality.

## Open contribution
- External bug fixes and suggestions are welcome and go through the **same review pipeline** as
  internal work — triaged, labeled, reviewed (approving review; security-focused review if
  security-relevant), and **never merged unreviewed**.
- Provide the on-ramp: issue templates (bug report, feature/suggestion), a PR template (issue link +
  checklist), and a `CONTRIBUTING.md` (how to file, branch, test, submit). Route security reports to
  a **private** channel (advisory) — never a public issue (`@rules/workflow-vuln-mgmt.md`).
- Enable the tracker; triage promptly; acknowledge external contributors.

## Traceability & history
- Keep the requirement → issue → PR → commit chain intact as change-management evidence
  (`@rules/std-soc2.md`).
- If issue tracking is adopted after work already shipped, **backfill** issues for the historical
  changes — labeled `backfilled`, closed as completed, linked to the delivering PR — and record the
  mapping in-repo. Backfilled issues are honest retroactive records, not a claim the work was
  tracked at the time; never rewrite signed history to fake it (`@rules/workflow-git.md`).

## References
- master §1/§8; `@rules/workflow-git.md`, `@rules/workflow-code-review.md`, `@rules/std-soc2.md`.
  Index: `@rules/reference-style-guides.md`.
