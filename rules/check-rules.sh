#!/usr/bin/env bash
# Validate the SSDLC ruleset: every @import resolves, and every module is listed in
# both the master catalog (~/.claude/CLAUDE.md §6) and rules/README.md.
# Usage: ~/.claude/rules/check-rules.sh   (exit 0 = clean, 1 = problems found)
set -euo pipefail
IFS=$'\n\t'

# Derive paths from this script's own location (rules/check-rules.sh) so it works both
# in-place (~/.claude) and from a CI checkout of the claude-ssdlc-rules repo.
RULES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$RULES")"
MASTER="${ROOT}/CLAUDE.md"
README="${RULES}/README.md"
fail=0

echo "== 1. @import path resolution =="
# Every @<path>.md reference across the master and all rule/template files (real imports
# and in-body cross-references) must point at a file that exists.
mapfile -t imports < <(grep -rhoE --include='*.md' '@[A-Za-z0-9/_.~-]+\.md' "$MASTER" "$RULES" | sed -E 's/^@//' | sort -u)
for imp in "${imports[@]}"; do
  case "$imp" in
    "~/.claude/"*) path="${ROOT}/${imp#\~/.claude/}" ;;  # template form → repo root (CI-safe)
    "~/"*)         path="${HOME}/${imp#\~/}" ;;          # other ~ paths
    /*)            path="$imp" ;;
    *)             path="${ROOT}/${imp}" ;;              # @rules/x.md (relative to root)
  esac
  if [[ ! -f "$path" ]]; then
    echo "  BROKEN: @${imp} -> ${path}"
    fail=1
  fi
done
[[ $fail -eq 0 ]] && echo "  all ${#imports[@]} import paths resolve"

echo "== 2. Catalog / README drift (modules) =="
for f in "$RULES"/*.md; do
  base="$(basename "$f" .md)"
  [[ "$base" == "README" || "$base" == "check-rules" ]] && continue
  grep -q "\`${base}\`" "$README" || { echo "  not in README: ${base}"; fail=1; }
  grep -q "\`${base}\`" "$MASTER" || { echo "  not in master catalog: ${base}"; fail=1; }
done

echo "== 3. Catalog / README drift (templates) =="
for f in "$RULES"/templates/*.md; do
  base="$(basename "$f" .md)"
  grep -q "templates/${base}" "$README" || { echo "  not in README: templates/${base}"; fail=1; }
  grep -q "templates/${base}" "$MASTER" || { echo "  not in master catalog: templates/${base}"; fail=1; }
done

echo "== 4. Runbooks indexed in workflow-runbooks.md =="
RUNBOOKS_RULE="${RULES}/workflow-runbooks.md"
for f in "$RULES"/runbooks/*.md; do
  base="$(basename "$f" .md)"
  [[ "$base" == "_TEMPLATE" ]] && continue
  grep -q "$base" "$RUNBOOKS_RULE" || { echo "  runbook not indexed: ${base}"; fail=1; }
done

echo
if [[ $fail -eq 0 ]]; then
  echo "✓ Ruleset OK — all imports resolve and catalogs are in sync."
else
  echo "✗ Problems found (see above)."
fi
exit $fail
