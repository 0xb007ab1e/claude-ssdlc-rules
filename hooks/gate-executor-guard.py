#!/usr/bin/env python3
"""PreToolUse hard-guard for the sdlc-gate-executor subagent.

A hard boundary (exit 2 = block) layered under the gate-actions policy + approver +
`disallowedTools`. The executor's *only* legitimate job is the narrow reversible class
(local git add/commit, draft PR, run tests/lint/build in a worktree). Anything that pushes,
deploys, applies infra, publishes, touches secrets/cloud/prod, reaches the network, or is
destructive is blocked here regardless of what was "approved".

Fail-closed by construction: any unreadable/unparseable input or internal error exits 2
(block). Only a successfully-parsed, non-matching command exits 0 (defer to normal flow).

Note: command-string matching is strong against chained commands (the whole line is scanned)
but, like all pattern matching, not proof against deliberate obfuscation (env-var rewrites).
It is a backstop against mistakes/mis-marking, not an adversary — paired with policy + scope.
"""

import re
import sys

# Commands the executor must NEVER run. Matched (IGNORECASE) anywhere in the command line,
# so chained forms like `cd x && git push` are caught.
DENY = [
    # VCS: outward / history-rewriting / irreversible
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgit\s+rebase\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\b",
    r"\bgit\b[^|&;]*--force\b",
    r"\bgit\b[^|&;]*\s-f\b",
    r"\bgit\s+tag\s+-d\b",
    # GitHub CLI: merge / publish / mutate (draft PR *create* stays allowed)
    r"\bgh\s+pr\s+merge\b",
    r"\bgh\s+release\b",
    r"\bgh\s+repo\s+(delete|create|edit)\b",
    r"\bgh\s+api\b",
    # IaC / orchestration — executor has no business here (these are escalated)
    r"\b(terraform|tofu|opentofu|pulumi|cdk|kustomize|ansible|ansible-playbook)\b",
    r"\bkubectl\b",
    r"\bhelm\b",
    # Cloud CLIs (mutations & secrets live here) — escalate, never auto-run
    r"\b(aws|gcloud|az|doctl|vault|flyctl|heroku)\b",
    # Containers / publishing
    r"\bdocker\s+(push|build)\b",
    r"\bdocker\b[^|&;]*\spush\b",
    r"\b(npm|pnpm|yarn)\s+publish\b",
    r"\bcargo\s+publish\b",
    r"\bgem\s+push\b",
    r"\btwine\s+upload\b",
    # Network egress (outward) — not needed for the local class
    r"\b(curl|wget|nc|ncat|telnet|scp|rsync|sftp)\b",
    # Destructive / privilege
    r"\brm\s+-[a-z]*r[a-z]*f\b",
    r"\brm\s+-[a-z]*f[a-z]*r\b",
    r"\b(dd|mkfs|shred|truncate)\b",
    r"\b(sudo|su)\b",
    r":\s*\(\)\s*\{",  # fork bomb
]
PATTERNS = [re.compile(p, re.IGNORECASE) for p in DENY]


def block(reason: str) -> None:
    sys.stderr.write(f"[gate-executor-guard] BLOCKED: {reason}\n")
    sys.exit(2)  # fail-closed


def main() -> None:
    try:
        import json

        raw = sys.stdin.read()
        if not raw.strip():
            block("empty hook input — cannot verify command")
        data = json.loads(raw)
        if data.get("tool_name") != "Bash":
            sys.exit(0)  # matcher should scope to Bash; defer otherwise
        command = (data.get("tool_input") or {}).get("command")
        if not isinstance(command, str) or not command.strip():
            block("no command string found in tool_input")
        for pat in PATTERNS:
            if pat.search(command):
                block(f"command matches denied pattern /{pat.pattern}/ — this class is "
                      f"gated to the human, not the executor. Escalate instead.")
        sys.exit(0)  # parsed cleanly, no denied pattern → defer to normal permission flow
    except SystemExit:
        raise
    except Exception as exc:  # ANY unexpected error → fail closed
        block(f"guard error ({type(exc).__name__}: {exc}) — blocking to fail closed")


if __name__ == "__main__":
    main()
