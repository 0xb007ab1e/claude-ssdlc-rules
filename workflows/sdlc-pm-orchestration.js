export const meta = {
  name: 'sdlc-pm-orchestration',
  description:
    'SDLC Project Manager orchestration: plan a goal into disjoint workstreams, fan out to the ' +
    'Software/Infrastructure Architect subagents in parallel worktrees, integrate + validate, ' +
    'then halt at a gate-review boundary returning every proposed gated action for human ' +
    'approval. Budget-aware (caps fan-out to the turn token target). Never performs gated ' +
    'actions (no commit/push/deploy/apply) — that stays with the human in the main session.',
  phases: [
    { title: 'Plan', detail: 'decompose the goal into disjoint, parallelizable workstreams' },
    { title: 'Architect', detail: 'software + infra architects in parallel, worktree-isolated' },
    { title: 'Integrate', detail: 'reconcile worktrees, flag conflicts, validate against gates' },
    { title: 'Gate Review', detail: 'consolidate gated actions; halt for human approval' },
  ],
}

// ---- input ----
const goal =
  args && typeof args === 'object' ? args.goal : typeof args === 'string' ? args : null
if (!goal) return { error: 'Provide args.goal (a string) — what to deliver.' }

// ---- schemas (force structured output) ----
const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    assumptions: { type: 'array', items: { type: 'string' } },
    workstreams: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          role: { type: 'string', enum: ['software', 'infra'] },
          brief: { type: 'string' },
          paths: { type: 'array', items: { type: 'string' } },
        },
        required: ['id', 'role', 'brief', 'paths'],
      },
    },
  },
  required: ['workstreams'],
}

const WORK_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    artifacts: { type: 'array', items: { type: 'string' } },
    decisions: { type: 'array', items: { type: 'string' } },
    gateRequests: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          action: { type: 'string' },
          why: { type: 'string' },
          severity: { type: 'string' },
          rollback: { type: 'string' },
        },
        required: ['action', 'why'],
      },
    },
    needsEngineers: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary'],
}

// ---- Plan ----
phase('Plan')
log(`Goal: ${goal}`)
if (budget.total) log(`Budget target: ~${Math.round(budget.total / 1000)}k output tokens (shared pool).`)

const plan = await agent(
  `You are the SDLC Project Manager. Decompose this goal into INDEPENDENT workstreams, each owned ` +
    `by either the Software Architect (role "software") or Infrastructure Architect (role "infra"). ` +
    `CRITICAL: each workstream must own a DISJOINT set of file paths — no two workstreams may touch ` +
    `the same file (batch-atomicity). Keep it to the minimum set of workstreams that parallelize ` +
    `cleanly. Follow the ruleset in ~/.claude/rules.\n\nGoal: ${goal}`,
  { label: 'plan', phase: 'Plan', schema: PLAN_SCHEMA },
)

let workstreams = (plan && plan.workstreams) || []
if (!workstreams.length) return { goal, error: 'Planning produced no workstreams.' }

// Budget-aware cap — never truncate silently.
if (budget.total) {
  const cap = Math.max(2, Math.floor(budget.remaining() / 120_000))
  if (workstreams.length > cap) {
    log(`Budget cap: running ${cap} of ${workstreams.length} workstreams now; deferring ${workstreams.length - cap} (re-run for the rest).`)
    workstreams = workstreams.slice(0, cap)
  }
}
log(`${workstreams.length} workstream(s): ${workstreams.map((w) => `${w.id}[${w.role}]`).join(', ')}`)

// ---- Architect fan-out (parallel, worktree-isolated) ----
phase('Architect')
const results = await parallel(
  workstreams.map((w) => async () => {
    if (budget.total && budget.remaining() < 30_000) {
      log(`Skipping ${w.id} — budget nearly exhausted.`)
      return null
    }
    const agentType = w.role === 'infra' ? 'sdlc-infra-architect' : 'sdlc-software-architect'
    return agent(
      `Workstream "${w.id}". Brief: ${w.brief}\n` +
        `Owned paths (stay strictly within these, disjoint from peers): ${w.paths.join(', ')}\n` +
        `Do autonomous design / scaffold / code / tests / IaC in your isolated worktree. ` +
        `DO NOT perform gated actions (commit, push, PR/merge, deploy, terraform apply/destroy, ` +
        `real secrets, outward calls, prod/data) — instead return each as a gateRequest. ` +
        `Follow ~/.claude/rules and ~/.claude/rules/workflow-gated-actions.md.`,
      { label: `${w.role}:${w.id}`, phase: 'Architect', schema: WORK_SCHEMA, isolation: 'worktree', agentType },
    ).then((r) => (r ? { ...r, workstream: w.id, role: w.role } : null))
  }),
)
const work = results.filter(Boolean)

// ---- Integrate + validate ----
phase('Integrate')
const integration = await agent(
  `Integrate these worktree results for goal "${goal}". Detect cross-workstream conflicts or ` +
    `file overlaps and flag them explicitly; summarize the combined artifacts; and report ` +
    `validation/gate status (the ruleset validator is ~/.claude/rules/check-rules.sh; the project's ` +
    `CI gates are lint/test/coverage/SAST/SCA/secret). Do NOT commit or merge anything.\n\n` +
    `Results JSON:\n${JSON.stringify(work).slice(0, 12000)}`,
  { label: 'integrate', phase: 'Integrate' },
)

// ---- Gate review (halt; never execute gated actions) ----
phase('Gate Review')
const gateRequests = work.flatMap((w) => (w.gateRequests || []).map((g) => ({ ...g, workstream: w.workstream })))
log(
  gateRequests.length
    ? `GATE REVIEW — ${gateRequests.length} action(s) require HUMAN approval. Halting by policy ` +
        `(workflow-gated-actions): no commit/push/deploy/apply performed.`
    : 'No gated actions proposed by the architects.',
)

return {
  goal,
  assumptions: (plan && plan.assumptions) || [],
  workstreams: work.map((w) => ({ id: w.workstream, role: w.role, summary: w.summary, artifacts: w.artifacts || [] })),
  integration,
  gateRequests,
  needsEngineers: work.flatMap((w) => w.needsEngineers || []),
  tokensSpent: budget.total ? budget.spent() : undefined,
  note:
    'Autonomous phases complete in isolated worktrees. Review gateRequests; the human approves and ' +
    'executes gated actions in the main session, or re-run with the next segment. Coordinators never auto-approve.',
}
