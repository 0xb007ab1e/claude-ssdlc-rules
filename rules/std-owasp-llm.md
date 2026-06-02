# Standard: OWASP Top 10 for LLM Applications

For any system using LLMs, RAG, or autonomous agents. Treat model output and any
external/tool-fetched content as **untrusted input**.

1. **LLM01 Prompt Injection:** direct and indirect (poisoned web pages, docs, tool results).
   Separate system instructions from user/external content; don't let fetched content carry
   privileged instructions; constrain with strict system prompts; validate/sanitize inputs;
   prefer allow-listed actions over free-form. Assume injection *will* happen — limit blast
   radius rather than relying on prevention.
2. **LLM02 Insecure Output Handling:** never `eval`/exec, render as HTML, run as SQL/shell,
   or auto-execute model output without validation + encoding. The model is an untrusted
   upstream (`@rules/std-owasp-api.md` API10, `@rules/std-cwe.md`).
3. **LLM03 Training-Data / RAG Poisoning:** vet and provenance-check data sources and
   fine-tuning corpora; isolate/authorize what goes into the retrieval index.
4. **LLM04 Model Denial of Service / Unbounded Consumption:** cap input size, output tokens,
   recursion/agent steps, and tool-call count; rate-limit; budget per user (cost-DoS). The same
   limits + caching reduce normal cost — see `@rules/topic-token-optimization.md`.
5. **LLM05 Supply-Chain:** vet models, datasets, plugins, and ML deps; verify provenance and
   integrity (`@rules/std-supplychain.md`); pin versions.
6. **LLM06 Sensitive Information Disclosure:** don't put secrets/PII in prompts or context;
   redact retrieved data; filter outputs; the model may memorize/leak — apply data
   classification and master §5 redaction.
7. **LLM07 Insecure Plugin/Tool Design:** tools take typed, validated, least-privilege
   parameters; no free-form code/SQL/shell params; authorize each tool call server-side.
8. **LLM08 Excessive Agency:** grant the agent the **least capability, permission, and
   autonomy** needed; require human approval for high-impact/irreversible actions; scope
   tokens per action; make destructive operations confirm. Apply the gate policy in
   `@rules/workflow-gated-actions.md` (autonomous vs. human-approved actions).
9. **LLM09 Overreliance:** validate/ground outputs (cite sources, verify claims); don't trust
   the model for security or correctness-critical decisions without checks; label AI output.
10. **LLM10 Model Theft:** protect model weights/keys; access control + monitoring on model
    and inference endpoints; rate-limit to deter extraction.

## Practices
- **Trust boundary** between the model and everything it can affect; log prompts/responses/
  tool calls (redacted) for audit (`@rules/topic-logging-observability.md`).
- Adversarially test for jailbreaks/injection; treat agent autonomy as privilege escalation
  in threat modeling (`@rules/workflow-threat-model.md`).
