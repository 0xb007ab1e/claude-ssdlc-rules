# Rule: Ruby (+ Rails)

## Project setup
- Supported Ruby version pinned (`.ruby-version`); Bundler with committed `Gemfile.lock`.
- CI runs RuboCop (zero offenses), Brakeman (Rails SAST), and `bundle audit` (SCA).

## Style & types
- Follow the community style guide; RuboCop-enforced. Small methods, clear naming.
- Consider RBS/Sorbet for type checking on larger codebases. YARD doc comments on public
  methods/classes (feeds `docs/` mandate); enforce class/module docs with RuboCop
  `Style/Documentation`.

## Secure coding
- **No `eval`/`send` with untrusted input**; avoid `Object#send` to arbitrary methods —
  allow-list. No `Marshal.load`/`YAML.load` on untrusted data (use `YAML.safe_load`).
- SQL via ActiveRecord parameterization / placeholders — never string-interpolated SQL or
  raw `where("... #{x}")`. Avoid `find_by_sql` with interpolation.
- **Mass assignment:** use Strong Parameters (`params.require/permit`); never `permit!`.
- Output: rely on ERB/Rails auto-escaping; avoid `html_safe`/`raw` with untrusted data;
  keep CSRF protection on (`protect_from_forgery`).
- Avoid command injection (`system`/backticks/`%x` with interpolation) — pass arg arrays.
- Crypto via `OpenSSL`/`SecureRandom` (never `rand` for security); Rails credentials/ENV for
  secrets, never committed (`@rules/workflow-secrets.md`).
- Keep Rails and gems patched; Brakeman + bundler-audit gate in CI.

## Resource management
- **Cleanup:** prefer block forms (`File.open { }`, `pool.with { }`) that auto-close; otherwise
  `begin/ensure` to release on every path. See `@rules/topic-resource-management.md`.

## Testing
- RSpec/Minitest; factories over fixtures where helpful; isolate DB and mock external calls.
- Coverage (SimpleCov), mutation (mutant), and contract requirements per master §4.

## References & style guides
- **Ruby Style Guide** — rubystyle.guide (enforced by RuboCop); **Rails Style Guide** — rails.rubystyle.guide.
- **Ruby on Rails Guides** — guides.rubyonrails.org; **Rails Security Guide**.
- **Brakeman** security scanner. Index: `@rules/reference-style-guides.md`.
