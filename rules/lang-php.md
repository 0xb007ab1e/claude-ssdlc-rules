# Rule: PHP (+ Laravel/Symfony)

## Project setup
- Supported PHP version (no EOL); Composer with committed `composer.lock`.
- `declare(strict_types=1);` in every file. CI runs a linter/formatter (PHP-CS-Fixer/PHPCS,
  PSR-12), PHPStan/Psalm at a high level, and `composer audit` (SCA).

## Style & types
- Type-declare params, returns, and properties; avoid mixed where possible. Follow PSR
  standards. PHPDoc on public APIs (feeds `docs/` mandate); enforce with phpcs
  `Squiz.Commenting.FunctionComment`.

## Secure coding
- **SQL:** PDO/ORM **prepared statements with bound params** only — never interpolate into
  queries. Avoid raw query builders with user input.
- **No `eval`**, `assert` on strings, `create_function`, or `extract()`/variable variables on
  untrusted input. Don't `unserialize()` untrusted data (object injection) — use JSON.
- **XSS:** escape on output (`htmlspecialchars` / Blade `{{ }}` / Twig auto-escape); avoid
  Blade `{!! !!}` / `|raw` with untrusted data. Set a strong CSP (`@rules/topic-web-frontend.md`).
- **File handling:** validate/allow-list uploads (type, size), store outside web root, never
  `include`/`require` user-controlled paths (LFI/RFI); disable `allow_url_include`.
- Command exec: `escapeshellarg`/arg arrays, never raw interpolation into `exec`/`shell_exec`.
- CSRF tokens on state-changing requests; framework guards on. Secure session cookies
  (`HttpOnly`, `Secure`, `SameSite`); regenerate session ID on login.
- Passwords via `password_hash`/`password_verify` (argon2id/bcrypt); `random_bytes`/
  `random_int` for randomness; secrets in env, never committed (`@rules/workflow-secrets.md`).
- Production `php.ini`: `display_errors=Off`, log errors server-side; keep framework patched.

## Resource management
- **Cleanup:** `try/finally` to release handles/connections on every path; close file handles
  and free large buffers promptly (don't lean on request-end GC for shared/long-lived workers).
  See `@rules/topic-resource-management.md`.

## Testing
- PHPUnit/Pest; isolate DB; mock external calls. Coverage, mutation (Infection), and contract
  requirements per master §4.

## References & style guides
- **PSR standards** (PSR-1/4/12) / **PHP-FIG** — php-fig.org.
- **PHP The Right Way** — phptherightway.com; framework guides (Laravel/Symfony docs).
- **OWASP PHP security**. Index: `@rules/reference-style-guides.md`.
