# Rule: SQL

Query authoring style and anti-patterns. Schema design, migrations, indexing, and access
control live in `@rules/topic-database.md`; injection prevention is enforced in the `lang-*`
modules (always parameterize).

## Style
- Consistent keyword case (UPPERCASE keywords is common), one clause per line for complex
  queries, meaningful aliases; format consistently (sqlfluff/pgFormatter) — checked in CI.
- **Explicit column lists — never `SELECT *`** in application queries (breaks on schema change,
  over-fetches, defeats covering indexes).
- Prefer explicit `JOIN ... ON` over comma-joins; qualify columns in multi-table queries.
- Keep business logic out of giant SQL where it hurts clarity; but push set-based work to the DB
  rather than looping in app code.

## Correctness & safety
- **Always parameterize** — bind variables/placeholders, never string-concatenate user input
  (SQL injection — `@rules/std-cwe.md` CWE-89). This holds in dynamic SQL too.
- Beware **NULL semantics:** `NULL <> value` is unknown, not true; use `IS [NOT] NULL`; understand
  three-valued logic in `WHERE`/`NOT IN` (NULL in a `NOT IN` list silently drops rows).
- Wrap multi-statement changes in **transactions**; choose the right isolation level; keep
  transactions short to avoid lock contention (`@rules/topic-database.md`).
- Use deterministic `ORDER BY` for pagination (and keyset pagination for large sets — no `OFFSET`
  on huge tables).

## Performance
- Write for the indexes; check the plan with **`EXPLAIN`/`EXPLAIN ANALYZE`** before shipping
  heavy queries. Avoid functions on indexed columns in `WHERE` (kills index use), needless
  `DISTINCT`, correlated subqueries where a join/window works, and `SELECT N+1` patterns
  (`@rules/topic-performance.md`).
- Prefer set-based operations over row-by-row; use window functions and CTEs for readability
  (watch materialization). Batch large writes/deletes.

## References & style guides
- **SQL Style Guide** (Holywell) — sqlstyle.guide; **Use The Index, Luke!** — use-the-index-luke.com;
  your engine's SQL + `EXPLAIN` docs. Index: `@rules/reference-style-guides.md`.
