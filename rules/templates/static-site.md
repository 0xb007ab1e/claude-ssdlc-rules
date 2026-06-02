# Template: Static Site / JAMstack — project CLAUDE.md

For static sites and SSG/JAMstack (Astro, Next export, Hugo, Eleventy, Gatsby). Copy to the
project's root `CLAUDE.md`. Inherits the master automatically.

```markdown
# <SiteName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-typescript.md        # or lang-shell/none for pure-Markdown SSGs
@~/.claude/rules/topic-web-frontend.md     # CSP, SRI, headers (set at the CDN/edge)
@~/.claude/rules/topic-accessibility.md    # WCAG 2.2 AA
@~/.claude/rules/topic-performance.md      # Core Web Vitals, asset optimization
@~/.claude/rules/topic-i18n.md             # if multi-locale
@~/.claude/rules/std-supplychain.md        # npm deps, SRI on third-party assets
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-release.md       # atomic deploys + CDN purge
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md

## Stack
- Generator: <Astro / Hugo / Eleventy / Next export>; host: <Netlify / Cloudflare Pages / S3+CDN>

## Project-specific rules
- **No secrets in the build output** — everything shipped is public; build-time secrets stay
  in CI env only. Any dynamic behavior goes through a separate API/function
  (`@rules/templates/serverless-function.md`).
- Security headers + strict CSP configured at the CDN/edge (static hosts don't send them by
  default); HTTPS + HSTS; SRI on external scripts.
- Performance + a11y are CI gates (Lighthouse); optimize images and fonts; long-cache hashed
  assets, short-cache HTML (`@rules/topic-caching.md`).
- Atomic deploys with instant rollback; purge CDN on publish (`@rules/workflow-release.md`).
- Pin SSG + plugin versions; audit dependencies (build-time supply chain still matters).
```
