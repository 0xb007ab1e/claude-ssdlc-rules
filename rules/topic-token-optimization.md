# Topic: LLM Token & Cost Optimization

Reduce tokens (cost + latency) in LLM/agent systems **without degrading correctness**. Pairs
with `@rules/topic-model-serving.md` (serving infra), `@rules/std-owasp-llm.md` (LLM04 unbounded
consumption is also a cost-DoS), `@rules/topic-caching.md`, and `@rules/topic-performance.md`.

> **Correctness first.** Never trade accuracy on correctness-sensitive paths to save tokens —
> measure quality alongside cost and treat a quality regression as a failure (master §4). Save
> tokens where it doesn't move the quality metric.

## Methods (roughly highest-leverage first)
- **Prompt caching** — cache the stable prefix (system prompt, tool definitions, large shared
  context, few-shot examples) so it isn't re-billed/re-processed each call. Order prompts
  **static-first, dynamic-last** to maximize cache hits; mind the provider's cache TTL (e.g.
  Anthropic ~5 min) and structure long-running loops to stay within it. Biggest single win for
  repeated calls.
- **Right-size / route the model** — use a small fast model (e.g. Haiku) for simple/classify/
  extract steps; escalate to a larger model (Sonnet/Opus) only when needed. Cascade: cheap model
  first, fall back to stronger on low confidence.
- **Cap output** — set `max_tokens`; ask for terse/structured output (JSON/enum, no prose
  preamble); use stop sequences. Output tokens usually cost more than input.
- **Trim input / context** — include only what's needed: retrieve (RAG) instead of stuffing whole
  docs; rerank and send **top-k tight** chunks; drop boilerplate; compress/clean scraped or
  retrieved text before sending.
- **Manage conversation history** — summarize or window older turns instead of resending the full
  transcript; keep a rolling summary + recent turns (`@rules/topic-state-management.md`).
- **Batch** — use the Batch API (often ~50% cheaper) for non-real-time work; group requests.
- **Cache responses** — exact-match or semantic cache for repeated/deterministic queries and
  embeddings (`@rules/topic-caching.md`); dedupe identical calls; memoize tool results.
- **Lean tool/function schemas** — tool definitions are sent every call; keep them minimal and
  cache them; expose only the tools a step needs (also reduces excessive agency — `@rules/std-owasp-llm.md`).
- **Fine-tune / distill** to drop large few-shot blocks from every call when volume justifies the
  training cost.
- **Bound agents** — cap agent steps, tool calls, and recursion (also a safety limit —
  `@rules/std-owasp-llm.md` LLM04); stop early when the goal is met.
- Streaming doesn't cut tokens but improves perceived latency — use it for UX, not savings.

## When to apply
- **Always (low-risk, do by default):** prompt caching for stable prefixes, `max_tokens` caps,
  right-sized model per task, lean tool schemas, bounded agent loops.
- **High-volume / cost-sensitive:** batching, response/semantic caching, model routing/cascades,
  fine-tuning/distillation, aggressive context trimming + RAG.
- **Long conversations / agents:** history summarization + windowing, step/tool-call caps.
- **Don't bother / be careful:** one-off or low-volume calls (optimization not worth complexity);
  correctness-critical extraction/reasoning (validate that any trimming/cheaper model holds
  quality — for the scraping product, watch the Silent Corruption Rate, `@rules/templates/web-scraper-crawler.md`).

## Measure
- Track **tokens and cost per request and per feature**, cache-hit rate, and the **quality
  metric** side-by-side (`@rules/topic-logging-observability.md`). Optimize against data, not
  guesses; set a cost budget/alert per request or per tenant (`@rules/topic-multi-tenancy.md`).
- A/B or eval new prompt/model/context changes for quality before rolling out
  (`@rules/topic-model-serving.md`, master §4).

## References
- Anthropic prompt caching, Message Batches, and model-selection docs (and the Claude API
  skill's caching guidance); provider pricing/usage dashboards. Index: `@rules/reference-style-guides.md`.
