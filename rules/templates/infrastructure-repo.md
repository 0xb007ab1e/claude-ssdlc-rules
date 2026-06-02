# Template: Infrastructure (IaC) Repo — project CLAUDE.md

For repos that define cloud/infra as code (Terraform/OpenTofu, Pulumi, CloudFormation,
Bicep, Helm/K8s manifests). Copy to the project's root `CLAUDE.md`. Inherits the master.

```markdown
# <ProjectName> — infrastructure rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/topic-iac-cloud.md        # primary: IaC + cloud hardening
@~/.claude/rules/topic-container-k8s.md    # if it ships K8s manifests/Helm
@~/.claude/rules/std-cis.md                # CIS benchmarks for the platforms in use
@~/.claude/rules/std-zero-trust.md         # network/identity architecture
@~/.claude/rules/topic-logging-observability.md
@~/.claude/rules/std-supplychain.md        # pin modules/providers; vet third-party modules
@~/.claude/rules/workflow-cicd.md          # IaC scan gates (tfsec/checkov/KICS)
@~/.claude/rules/workflow-secrets.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/workflow-cve-management.md
@~/.claude/rules/workflow-release.md
@~/.claude/rules/workflow-incident-response.md
@~/.claude/rules/workflow-runbooks.md

## Stack
- IaC tool: <Terraform / Pulumi / CDK>; cloud(s): <AWS / GCP / Azure>
- State backend: <remote, encrypted, locked>; environments: <dev/stage/prod accounts>

## Project-specific rules
- **No click-ops:** all changes via PR + plan review; prod applies require approval.
- IaC security scan blocks merge on high/critical misconfig; pin provider/module versions.
- Least-privilege CI identity via OIDC; no static cloud keys; secrets from vault at apply.
- Encryption, private networking, audit logging, and tagging are defaults, not options.
- Never commit state files or secret-bearing var files.
```
