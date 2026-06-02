# Topic: Model Serving / Inference Infrastructure

For serving ML models in production (real-time or batch inference). The *app/agent* concerns
live in `@rules/std-owasp-llm.md` and `templates/ai-llm-service.md`; training in
`templates/ml-training-pipeline.md`. This is the serving layer.

## Model management
- **Version every served model**; deployments reference an immutable model version + its
  provenance (training data hash, eval report — `@rules/templates/ml-training-pipeline.md`). Be
  able to identify exactly which model produced any response (log model version per request —
  `@rules/topic-logging-observability.md`).
- **Safe rollout** like code: canary/shadow new models, compare quality + latency against the
  incumbent, **auto-rollback** on regression (`@rules/workflow-release.md`,
  `@rules/topic-reliability.md`). Keep the previous version warm for instant rollback.
- Protect model artifacts/weights and inference endpoints (model theft — `@rules/std-owasp-llm.md`
  LLM10): access control, auth, and rate limits on the inference API.

## Performance & cost
- **Batching:** dynamic/continuous batching to maximize GPU/accelerator throughput; tune batch
  size vs. tail latency. Separate latency-sensitive (online) from throughput-sensitive (batch) paths.
- **Hardware & concurrency:** right-size GPU/CPU; cap concurrency per replica; queue with bounded
  depth + backpressure (reject/shed over capacity — `@rules/topic-reliability.md`).
- **Cache** deterministic results / embeddings where valid (`@rules/topic-caching.md`); use
  quantization/distillation/compilation to cut cost where quality allows. For API-based LLMs,
  reduce tokens via `@rules/topic-token-optimization.md` (prompt caching, routing, context trim).
- **Autoscale on the real bottleneck** (GPU utilization, queue depth — `@rules/runbooks/scaling.md`),
  not just CPU; scale-to-zero for spiky/low-traffic models. Track cost per 1k inferences.

## Reliability & safety
- **Timeouts + fallbacks** on every inference call; degrade gracefully (cached/smaller/default
  model) rather than hard-fail (`@rules/topic-error-handling.md`).
- **Validate inputs and outputs:** bound input size; treat model output as untrusted downstream
  (`@rules/std-owasp-llm.md` LLM02). Guardrails/safety filters on outputs where applicable.
- **Monitor for drift:** track input distribution, prediction distribution, quality/feedback, and
  latency/error SLOs; alert on drift or degradation. Define a retrain/rollback trigger.

## References
- KServe / NVIDIA Triton / TorchServe / vLLM serving docs; Google "Rules of ML".
  Index: `@rules/reference-style-guides.md`.
