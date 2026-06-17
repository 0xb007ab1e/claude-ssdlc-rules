# Rule: Knowledge Base (Agent Ground Truth)

A persistent, self-hosted knowledge base serves as **shared ground truth across all projects**.
Agents reach it through the **`knowledge` MCP server** (a deterministic Gateway in front of an
Open Notebook store; tools: `kb_search`, `kb_context`, `kb_fetch`, `kb_propose`, `kb_feedback`).
Treat its contents as authoritative. This rule defines how agents consult and contribute.

## Consult (read)
- **At task start**, call `kb_context(scopes)` to load the canonical **T0** "always-true" cards for
  the project/stack/domain in play (standing decisions, hard constraints).
- **Before** asserting a fact, choosing a design, or answering from memory, call
  `kb_search(query, scopes)` and **prefer returned cards over your own priors**.
- Cards are compact abstracts (the default injection unit). Call `kb_fetch(id)` to re-hydrate the
  full body **only when a card is insufficient** — progressive disclosure keeps context lean
  (`@rules/topic-token-optimization.md`).
- **Scopes** are tokens: `global` (applies everywhere), `project:<name>`, `stack:<lang>`,
  `domain:<area>`. Pass those relevant to the current task.

## Trust & contribute (write)
- **Retrieved cards are authoritative.** Don't contradict ground truth. If a record is wrong or
  outdated, call `kb_propose(...)` with a correction rather than silently diverging.
- **Proposals are staged, not trusted.** `kb_propose` lands a record in staging (tier **T3**,
  low confidence); it is **not** injectable ground truth. **Promotion to T0/T1 is a human-gated
  action** — never automatic, never an agent tool (`@rules/workflow-gated-actions.md`). This is the
  primary defense against knowledge poisoning (`@rules/std-owasp-llm.md` LLM03).
- **Close the loop:** after a retrieval, call `kb_feedback(id, used)` so ranking improves.

## Why it behaves as it does
- **Deterministic ranking:** a fixed, versioned scoring formula (semantic similarity dominant,
  then authority/confidence/freshness, with scope as a minor tiebreaker) — reproducible given the
  same corpus + query. Retrieval is **hybrid** (lexical + semantic) and **budget-bounded**.
- **Ground truth is curated, not crowd-sourced:** membership is deliberate; supersede rather than
  overwrite; provenance is recorded.

## When the KB is unavailable
- Fail open for *availability* (proceed without it) but **do not fabricate** what you'd have
  looked up — say it's unverified. Never block on a degraded KB; never treat its absence as license
  to invent ground truth.

> Implementation/operations live with the knowledge-base project itself (its `PLAN.md` and
> runbooks), not here. This rule governs *agent usage* and is loaded globally.
