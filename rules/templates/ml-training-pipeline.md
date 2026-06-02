# Template: ML Training Pipeline / MLOps — project CLAUDE.md

For model **training** pipelines (distinct from `ai-llm-service`, which is inference/agents).
Copy to the project's root `CLAUDE.md`. Inherits `~/.claude/CLAUDE.md` automatically.

```markdown
# <ProjectName> — project rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-python.md
@~/.claude/rules/std-owasp-llm.md          # LLM03 data poisoning, LLM05/10 model supply chain & theft
@~/.claude/rules/std-owasp-proactive.md
@~/.claude/rules/std-cwe.md
@~/.claude/rules/topic-database.md
@~/.claude/rules/topic-iac-cloud.md        # training infra, GPU clusters
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/std-privacy.md            # training data often contains personal data
@~/.claude/rules/std-supplychain.md        # datasets, base models, ML deps
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-data-lifecycle.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md
@~/.claude/rules/topic-testing.md
# @~/.claude/rules/topic-model-serving.md # if this pipeline also deploys/serves the model

## Stack
- Framework: <PyTorch / JAX / TF>; orchestration: <Kubeflow / Metaflow / Airflow / SageMaker>
- Experiment tracking: <MLflow / W&B>; registry: <...>; feature store: <...>

## Project-specific rules
- **Reproducibility:** version data, code, config, AND environment; pin seeds; log every run
  (params, metrics, artifacts) to the experiment tracker. A model is reproducible from its
  recorded inputs.
- **Data provenance & integrity:** vet and version training datasets; guard the pipeline
  against poisoning (authorize/validate sources — LLM03); track data lineage; no real
  personal data without classification + minimization (`@rules/std-privacy.md`).
- **Model registry & versioning:** every promoted model is versioned with its training data
  hash, code commit, metrics, and an eval report (a model card).
- **Eval gates (master §4 analog):** quality + fairness/bias + safety evals must pass before
  promotion; check for regression vs. the current production model; hold out a clean test set.
- **Supply chain:** verify provenance of base models and datasets; pin ML deps; scan
  (`@rules/std-supplychain.md`). Protect model weights/keys (LLM10 model theft).
- **Cost/compute limits:** bound and monitor training cost; least-privilege access to data,
  compute, and the registry.
```
