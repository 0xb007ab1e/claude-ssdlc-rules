# Topic: Reliability & Resilience (SRE)

Design for failure — every dependency can be slow, fail, or return garbage.

## Targets & error budgets
- Define **SLIs** (latency, error rate, availability) and **SLOs** for critical paths;
  track against an **error budget**. Budget burn gates feature velocity vs. hardening.
- Alert on SLO burn rate and symptom (not just cause); see
  `@rules/topic-logging-observability.md`.

## Resilience patterns
- **Timeouts** on every network/IO call (no unbounded waits). Set connect + read timeouts.
- **Retries** only for idempotent ops, with exponential backoff + jitter and a max attempt
  cap; never retry non-idempotent writes without an idempotency key.
- **Circuit breakers** to stop hammering a failing dependency; fail fast and shed load.
- **Bulkheads / isolation:** pools and limits per dependency so one slow service can't
  exhaust all threads/connections.
- **Graceful degradation:** serve stale/cached/partial results over a hard failure where
  acceptable; feature-flag risky paths.
- **Backpressure & rate limiting** to protect against overload (DoS — `@rules/std-owasp-api.md`).
- **Idempotency** for all mutating operations (idempotency keys) so retries are safe.

## Recovery & continuity
- **Backups** automated, encrypted, and **restore-tested on a schedule** (an untested backup
  is not a backup). Define RPO/RTO for critical data.
- **DR plan:** multi-AZ/region for critical services; documented failover; periodic drills.
- **Graceful shutdown:** drain connections, finish/checkpoint in-flight work on SIGTERM.
- **Health checks:** liveness vs. readiness probes distinct; readiness reflects dependencies.

## Verification
- Load/soak/stress test critical paths; **chaos/fault-injection** tests for dependency
  failure, latency, and partial outages. Ties into master §4 testing gates.

## References
- **Google SRE / SRE Workbook** — sre.google/books; *Release It!* (Nygard) for resilience patterns.
- **AWS / Azure Well-Architected** (Reliability pillar). Index: `@rules/reference-style-guides.md`.
