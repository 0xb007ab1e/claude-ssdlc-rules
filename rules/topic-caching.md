# Topic: Caching

Caching trades freshness for speed/cost — make the trade-off explicit and safe.
Pairs with `@rules/topic-performance.md`.

## Strategy
- Cache only what's hot and expensive; measure hit rate. A low-hit-rate cache adds
  complexity and staleness for little gain.
- Pick a pattern deliberately: **cache-aside** (lazy, most common), read-through,
  write-through, or write-behind. Document which and why.
- Set an explicit **TTL** for every entry; prefer short TTLs + revalidation over long ones.
  Add small random jitter to TTLs to avoid synchronized expiry.

## Invalidation (the hard part)
- Define how each cached item is invalidated up front (TTL expiry, event-driven bust on
  write, or versioned keys). Stale data is a correctness bug.
- Use **versioned/namespaced keys** so a deploy or data change can invalidate cleanly.
- **Cache-stampede protection:** single-flight / request coalescing, locks, or early
  recompute so a popular key expiring doesn't hammer the origin.

## Correctness & safety
- **Never cache sensitive/personalized data in a shared cache** without a per-user/tenant
  key; respect data classification (master §5). Set `Cache-Control: private/no-store` for
  sensitive HTTP responses; vary on auth where relevant.
- Keep the cache as a performance layer, not the source of truth — the system must be correct
  (if slower) with the cache empty/down.
- Bound cache size with a sane eviction policy (LRU/LFU); monitor memory and hit rate.

## HTTP / CDN
- Use `Cache-Control`/`ETag`/`Last-Modified` correctly; immutable hashed assets get long
  `max-age`; HTML/API responses are short-lived or `no-cache`.
- Purge CDN on deploy for changed content; never cache `Set-Cookie`/auth'd responses at a
  shared CDN.

## References
- **HTTP Caching** — RFC 9111; **MDN HTTP caching** + **web.dev** caching guides.
- CDN provider docs (Cloudflare/Fastly/CloudFront). Index: `@rules/reference-style-guides.md`.
