# Runbook: Scaling

> Copy to `docs/runbooks/scaling.md` and fill in `<...>`. Rules: `@rules/topic-reliability.md`,
> `@rules/topic-performance.md`.

## When to use
- Sustained high load, latency/error-budget burn, a planned traffic event, or scaling down to
  cut cost.

## Prerequisites & access
- Access to the orchestrator/autoscaler and dashboards; know current limits, quotas, and the
  downstream bottleneck (DB connections, queue depth, third-party rate limits).

## Steps
1. Confirm the bottleneck from metrics (CPU/mem/connections/queue lag) — **scale the actual
   constraint**, not reflexively the web tier.
2. Scale out/up: `<autoscale or replica cmd>`. Respect downstream limits — don't overwhelm the
   DB/dependencies (connection pools — `@rules/topic-database.md`).
3. Shed/queue load if needed: enable rate limiting / backpressure
   (`@rules/topic-reliability.md`); serve degraded/cached responses (`@rules/topic-caching.md`).
4. For known events, pre-scale ahead of time and warm caches.

## Verification
- Latency/error rate back within SLO; saturation down; no new bottleneck pushed downstream.

## Scaling back down
- Reduce gradually while watching metrics; respect minimums for HA; confirm no thrashing.

## Escalation
- If scaling doesn't relieve it (or hits a hard quota), page `<on-call>` / open an incident.

## Related
- `runbooks/on-call.md`, `runbooks/incident-response.md`; `@rules/topic-performance.md`.

---
_Last validated: <date>. Owner: <team>._
