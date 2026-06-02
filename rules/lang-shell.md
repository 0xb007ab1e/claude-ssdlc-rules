# Rule: Shell / Bash

Shell is injection-prone and error-silent by default — be strict.

## Safety preamble
- Start scripts with `#!/usr/bin/env bash` and `set -euo pipefail` (exit on error, unset
  var, and pipe failure). Set `IFS=$'\n\t'` where word-splitting matters.
- Prefer Bash over POSIX `sh` only when you use Bash features; otherwise target `sh` and say so.
- For anything non-trivial or with real logic, prefer a real language (Python/Go) over shell.

## Quoting & injection (the main risk)
- **Always quote expansions:** `"$var"`, `"${arr[@]}"`, `"$(cmd)"`. Unquoted expansions cause
  word-splitting/globbing bugs and injection.
- **Never `eval`** with untrusted input. Avoid building commands from strings; use arrays:
  `cmd=(rsync -a "$src" "$dst"); "${cmd[@]}"`.
- Don't pipe remote content straight into a shell (`curl | bash`) — download, verify
  checksum/signature, then run.
- Use `--` to end option parsing before user-supplied paths; validate/allow-list input.
- Avoid parsing `ls`; use globs or `find -print0 | xargs -0`.

## Robustness
- Check command existence and exit codes; `trap` for cleanup of temp files (`mktemp`).
- Quote in `[[ ... ]]` (prefer over `[ ]`); use `(( ))` for arithmetic.
- No secrets on the command line (visible in `ps`/history) — read from env/file/stdin;
  redact in output (`@rules/workflow-secrets.md`).
- Restrictive `umask`; create temp files/dirs with `mktemp` (no predictable `/tmp` names).

## Tooling & tests
- **ShellCheck** clean (zero warnings) in CI; format with `shfmt`.
- Test with bats (or equivalent); keep functions small and pure where possible.

## References & style guides
- **Google Shell Style Guide** — google.github.io/styleguide/shellguide.html.
- **ShellCheck wiki** — github.com/koalaman/shellcheck/wiki (per-code rationale).
- **BashFAQ / Greg's Wiki** — mywiki.wooledge.org/BashFAQ. Index: `@rules/reference-style-guides.md`.
