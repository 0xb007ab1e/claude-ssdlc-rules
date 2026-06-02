# Topic: Event-Driven & Messaging

For systems using queues/streams (Kafka, RabbitMQ, SQS/SNS, Pub/Sub, NATS). Async coupling
needs explicit guarantees — make delivery, ordering, and schema contracts deliberate.

## Event/message contracts
- **Versioned, documented event schemas** (Avro/Protobuf/JSON Schema) in a **schema
  registry**; evolve compatibly (additive, with compatibility checks) — events are a
  long-lived contract like an API (`@rules/topic-api-design.md`).
- Include a stable event ID, type, version, timestamp (UTC), and a correlation/trace ID for
  end-to-end tracing (`@rules/topic-logging-observability.md`).
- Treat consumed event payloads as **untrusted input** — validate before processing.

## Delivery semantics
- Assume **at-least-once** delivery by default → **consumers must be idempotent** (dedupe by
  event ID / idempotency key). Exactly-once is rare and expensive; don't assume it.
- Handle **out-of-order** delivery unless the broker + partitioning guarantee order
  (and even then only within a partition/key).
- **Dead-letter queues** for poison messages; cap retries with backoff; alert on DLQ growth.
  Never silently drop failed messages.

## Patterns
- **Transactional outbox** (or CDC) to publish events atomically with the DB write — avoid
  dual-write inconsistency between DB and broker.
- **Sagas** for distributed workflows with compensating actions (no distributed 2PC).
- Backpressure / consumer lag monitoring; scale consumers by partition; bound concurrency.

## Operations & security
- Authenticate/authorize producers and consumers; encrypt in transit; least-privilege topic
  access (`@rules/std-zero-trust.md`). No secrets/PII in events without classification +
  redaction (master §5).
- Monitor lag, throughput, error/DLQ rates; define SLOs (`@rules/topic-reliability.md`).

## References
- **Enterprise Integration Patterns** (Hohpe) — enterpriseintegrationpatterns.com.
- **AsyncAPI** — asyncapi.com; **CloudEvents** — cloudevents.io. Index: `@rules/reference-style-guides.md`.
