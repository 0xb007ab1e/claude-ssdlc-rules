# Rule: Python

## Project setup
- Target a supported CPython (no EOL versions). Isolated environment per project
  (venv/uv/poetry). Pin dependencies with a lockfile **and** hashes.
- Single declarative config in `pyproject.toml`.

## Style & types
- **Type-annotate** all public functions/classes; run a static type checker in CI
  (mypy/pyright) in strict mode for new code.
- Auto-format and lint with zero errors (e.g. ruff/black). No unused imports or names.
- Follow PEP 8 / PEP 20; prefer explicit over clever. Docstrings on every public symbol
  (feeds the `docs/` mandate); enforce with ruff `D` (pydocstyle).

## Secure coding
- **Never** `eval`/`exec`/`pickle` untrusted input; use `defusedxml`/safe parsers for XML.
- Parameterize all SQL (no string-built queries); use an ORM or `?`/`%s` placeholders.
- Validate input at boundaries with a schema lib (e.g. pydantic); never trust request data.
- Subprocess: pass arg lists, never `shell=True` with interpolated input.
- Crypto: use `secrets` for tokens, vetted libs (`cryptography`) — never `random` for
  security, never roll your own crypto or hashing (use bcrypt/argon2 for passwords).
- Paths/files: resolve and confine to an allowed root to prevent traversal.
- Run a Python SAST/security linter (e.g. bandit) and dependency audit (e.g. pip-audit) in CI.

## Resource management
- **Cleanup:** use `with` (context managers) for files, locks, connections, and sessions —
  release on every path; don't rely on the GC/`__del__`. See `@rules/topic-resource-management.md`.

## Concurrency
- The **GIL** means threads don't parallelize CPU-bound work — use `multiprocessing` (CPU) or
  `asyncio` (I/O); the GIL does NOT make compound operations atomic, so still lock shared state.
  Don't block the event loop in `asyncio`. See `@rules/topic-concurrency.md`.

## Testing
- pytest; fixtures over global state; `tmp_path` for filesystem; freeze time/network.
- Coverage and mutation/contract requirements per master §4.

## References & style guides
- **PEP 8** (style), **PEP 257** (docstrings), **PEP 484** + `typing` — peps.python.org.
- **Google Python Style Guide** — google.github.io/styleguide/pyguide.html.
- **The Hitchhiker's Guide to Python**; OWASP secure-coding. Index: `@rules/reference-style-guides.md`.
