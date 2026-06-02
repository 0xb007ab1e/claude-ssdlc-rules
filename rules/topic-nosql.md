# Topic: NoSQL / Non-Relational Data

For document, key-value, wide-column, graph, and time-series stores. Complements
`@rules/topic-database.md` (which is RDBMS-leaning); the master §5 data-protection and
`lang-*` injection rules still apply.

## Choose the right store
- Match the model to the access pattern: **document** (JSON aggregates, flexible schema),
  **key-value** (cache/session/simple lookups), **wide-column** (massive write/time-series scale),
  **graph** (relationship-heavy traversal), **time-series** (metrics/events). Don't force one to
  do another's job; polyglot persistence is fine when justified.
- NoSQL trades joins/transactions for scale/flexibility — know what you're giving up.

## Data modeling
- **Model for queries, not entities:** design around access patterns up front (esp.
  wide-column/DynamoDB — single-table design). Denormalization and duplication are normal.
- **Schema-on-read still needs a schema:** validate document structure in the app/at the boundary
  (the DB won't) — use schema validation where the engine supports it. Version documents and
  handle mixed-version reads during migrations.
- Bound document/item size; avoid unbounded arrays that grow forever (hot/large items).

## Consistency & integrity
- Understand the engine's **consistency model** (eventual vs. strong); read-your-writes and
  cross-document atomicity are often NOT guaranteed — design idempotent, conflict-tolerant writes
  (`@rules/topic-event-driven.md`). Use the engine's transactions only where it truly supports them.
- No referential integrity across documents — enforce invariants in the app and accept/repair drift.

## Security
- **NoSQL injection is real:** never build queries/filters from unsanitized input (e.g. operator
  injection like `{"$gt": ""}` in document stores); use the driver's parameterized/typed query API
  and validate input types (`@rules/std-cwe.md`, `@rules/std-owasp.md`).
- **Secure defaults:** many NoSQL engines historically shipped open/no-auth — require auth, bind to
  private networks, enable TLS + at-rest encryption, least-privilege roles (`@rules/topic-iac-cloud.md`).
- Tenant scoping per `@rules/topic-multi-tenancy.md`; classify and protect data per master §5.

## Operations
- Partition/shard key choice determines scale and hotspots — pick high-cardinality, even
  distribution. Index for query patterns (indexes cost writes/storage). Backups + tested restores
  and retention per `@rules/workflow-data-lifecycle.md`.

## References
- Each engine's official docs + data-modeling guides (e.g. DynamoDB, MongoDB, Cassandra, Neo4j).
  Index: `@rules/reference-style-guides.md`.
