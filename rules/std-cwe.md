# Standard: CWE Top 25 (Most Dangerous Weaknesses)

A concrete weakness checklist for code review and SAST triage. Map findings to CWE IDs in
reviews and security tests. Recurring high-impact classes to actively prevent:

- **CWE-79** Cross-site Scripting → context-aware output encoding; CSP.
- **CWE-89** SQL Injection → parameterized queries only.
- **CWE-78** OS Command Injection → arg arrays, no shell interpolation.
- **CWE-20** Improper Input Validation → allow-list validation at boundaries.
- **CWE-22** Path Traversal → canonicalize + confine to allowed root.
- **CWE-352** CSRF → anti-CSRF tokens / SameSite cookies.
- **CWE-434** Unrestricted Upload → validate type/size, store outside web root, scan.
- **CWE-862 / 863 / 269** Missing/Incorrect Authorization & Privilege Mgmt → deny by
  default, check ownership, least privilege.
- **CWE-287 / 306** Improper / Missing Authentication → enforce auth on every path.
- **CWE-502** Insecure Deserialization → never deserialize untrusted data natively.
- **CWE-918** SSRF → allow-list outbound targets; block metadata IPs.
- **CWE-77** Command/argument injection → safe APIs.
- **CWE-119/125/787/416/476** Memory safety (buffers, use-after-free, null deref) →
  prefer memory-safe languages; bound/validate in unsafe contexts; run sanitizers.
- **CWE-190** Integer Overflow → checked arithmetic on untrusted values.
- **CWE-798** Hardcoded Credentials → secrets manager only (`@rules/workflow-secrets.md`).
- **CWE-200 / 532** Information Exposure (incl. through logs) → redact (master §5).
- **CWE-94** Code Injection → no `eval`/dynamic code on untrusted input.

> Treat any SAST finding mapping to a Top-25 CWE as high priority. Add a regression/security
> test (master §4) for each fixed weakness.
