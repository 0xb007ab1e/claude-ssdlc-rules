export const meta = {
  name: 'sdlc-pm-orchestration',
  description:
    'SDLC Project Manager orchestration: plan a goal into disjoint workstreams, fan out to the Software/Infrastructure Architect subagents in parallel worktrees, integrate + validate, review, then halt at a gate-review boundary returning every proposed gated action for human approval. Budget-aware (caps fan-out to the turn token target). Never performs gated actions (no commit/push/deploy/apply) unless an autonomy policy approves the narrow reversible class.',
  phases: [
    { title: 'Plan', detail: 'decompose the goal into disjoint, parallelizable workstreams' },
    { title: 'Challenge', detail: 'red-team the plan; consensus or escalate before building' },
    { title: 'Architect', detail: 'software + infra architects in parallel, worktree-isolated' },
    { title: 'Integrate', detail: 'reconcile worktrees, flag conflicts, validate against gates' },
    { title: 'Review', detail: 'reviewer security/quality gate; a block disables auto-execution' },
    { title: 'Adjudicate', detail: 'gate-approver triages gates (only if autonomy granted)' },
    { title: 'Execute', detail: 'gate-executor runs ONLY approved reversible actions' },
    { title: 'Gate Review', detail: 'consolidate decisions; escalate to human; halt' },
  ],
}

// ---- input ----
const goal =
  args && typeof args === 'object' ? args.goal : typeof args === 'string' ? args : null
if (!goal) return { error: 'Provide args.goal (a string) — what to deliver.' }
// Optional, human-granted autonomy policy for this run (scope + allowlist + spend cap).
// If absent, the gate-approver escalates EVERYTHING (default-safe).
const autonomy = args && typeof args === 'object' ? args.autonomy : null

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

// ---- Challenge (red-team the plan; consensus or escalate before building) ----
phase('Challenge')
const CHALLENGE_SCHEMA = {
  type: 'object',
  properties: {
    consensus: { type: 'boolean' },
    objections: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          point: { type: 'string' },
          severity: { type: 'string' },
          blocking: { type: 'boolean' },
          source: { type: 'string' },
        },
        required: ['point', 'blocking'],
      },
    },
    recommendation: { type: 'string' },
  },
  required: ['consensus'],
}
let challenge
try {
  challenge = await agent(
    `You are the SDLC Red Team. Steelman, then challenge this PLAN for goal "${goal}" before any ` +
      `building: hidden assumptions, failure modes, risks (severity per master §7), missing ` +
      `alternatives, and any non-disjoint/file-overlap or scope problems across workstreams. Cite ` +
      `sources for factual counterpoints. Set consensus=false and blocking=true ONLY for material, ` +
      `unresolved problems. Follow the sdlc-red-team role.\n\n` +
      `Plan: ${JSON.stringify({ assumptions: plan.assumptions, workstreams }).slice(0, 8000)}`,
    { label: 'red-team:plan', phase: 'Challenge', schema: CHALLENGE_SCHEMA, agentType: 'sdlc-red-team' },
  )
} catch (e) {
  // First use of an sdlc-* agentType — fail gracefully with the likely cause + remedy.
  return {
    goal,
    error: `SDLC role agents unavailable: ${String((e && e.message) || e)}`,
    plan: workstreams,
    remedy:
      'The sdlc-* agents/skills register only at SESSION START. If you just created/edited them, ' +
      'RESTART Claude Code, then re-run. Also run Workflow mode from INSIDE the target git repo — ' +
      'the architect/engineer agents use worktree isolation and need a git repo as the cwd.',
  }
}
const blocking = ((challenge && challenge.objections) || []).filter((o) => o.blocking)
if (challenge && challenge.consensus === false && blocking.length) {
  log(`NO CONSENSUS — red team raised ${blocking.length} blocking objection(s). Escalating to the human before building.`)
  return {
    goal,
    halted: 'no-consensus-on-plan',
    assumptions: plan.assumptions || [],
    plan: workstreams,
    blockingObjections: blocking,
    recommendation: challenge.recommendation,
    note: 'Red Team withheld consensus on the plan. Escalated to the parent (human) for a ruling; no work was performed. Resolve the objections, then re-run.',
  }
}
log(`Red Team consensus on the plan${blocking.length ? '' : ' (no blocking objections)'}; proceeding.`)

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

// ---- Review (security & quality gate over the integrated work) ----
phase('Review')
const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['approve', 'changes-requested', 'block'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          severity: { type: 'string' },
          file: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['title', 'severity'],
      },
    },
  },
  required: ['verdict'],
}
const review = await agent(
  `You are the SDLC Reviewer. Review the integrated change for goal "${goal}" against the ruleset ` +
    `(correctness, security→CWE/OWASP, tests/coverage, concurrency/resource/numeric, anti-patterns, ` +
    `docs). Give findings with severity (master §7) + fixes and a verdict. Block on unresolved ` +
    `critical/high security or correctness issues. Advisory — do not commit/merge.\n\n` +
    `Integration: ${String(integration).slice(0, 6000)}\nWork: ${JSON.stringify(work).slice(0, 6000)}`,
  { label: 'reviewer', phase: 'Review', schema: REVIEW_SCHEMA, agentType: 'sdlc-reviewer' },
)
const reviewFindings = (review && review.findings) || []
const reviewBlock =
  (review && review.verdict === 'block') ||
  reviewFindings.some((f) => /crit|high/i.test(f.severity || ''))
log(
  `Review verdict: ${(review && review.verdict) || 'n/a'} · ${reviewFindings.length} finding(s)` +
    (reviewBlock ? ' — BLOCKING: autonomous execution disabled; escalate to human.' : '.'),
)

const gateRequests = work.flatMap((w) => (w.gateRequests || []).map((g) => ({ ...g, workstream: w.workstream })))

// ---- Adjudicate (gate-approver — only if the human granted an autonomy policy) ----
phase('Adjudicate')
const ADJUDICATION_SCHEMA = {
  type: 'object',
  properties: {
    decisions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          decision: { type: 'string', enum: ['approve', 'deny', 'escalate'] },
          matchedPolicy: { type: 'string' },
          reason: { type: 'string' },
        },
        required: ['id', 'decision', 'reason'],
      },
    },
    summary: {
      type: 'object',
      properties: { approved: { type: 'number' }, denied: { type: 'number' }, escalated: { type: 'number' } },
    },
  },
  required: ['decisions'],
}

let adjudication = null
if (gateRequests.length && autonomy) {
  adjudication = await agent(
    `You are the SDLC Gate Approver. Adjudicate these gate requests under the human-granted run ` +
      `autonomy policy. APPROVE only the reversible / non-prod / in-scope / rollback class on the ` +
      `allowlist; DENY security or scope violations; ESCALATE everything high-risk, irreversible, ` +
      `or ambiguous. Fail closed (default = escalate). Decide ONLY — do not execute. Follow ` +
      `~/.claude/rules/workflow-gated-actions.md (§ Autonomous approval authority).\n\n` +
      `Run autonomy policy: ${JSON.stringify(autonomy)}\n\n` +
      `Gate requests: ${JSON.stringify(gateRequests).slice(0, 8000)}`,
    { label: 'gate-approver', phase: 'Adjudicate', schema: ADJUDICATION_SCHEMA, agentType: 'sdlc-gate-approver' },
  )
  const c = (adjudication && adjudication.summary) || {}
  log(`Adjudicated under granted autonomy: ${c.approved || 0} approved · ${c.denied || 0} denied · ${c.escalated || 0} escalated.`)
} else if (gateRequests.length) {
  log(`No autonomy policy granted → all ${gateRequests.length} gate(s) escalate to the human (default-safe).`)
}

const decisions =
  (adjudication && adjudication.decisions) ||
  gateRequests.map((g) => ({ id: g.action, decision: 'escalate', matchedPolicy: 'default-escalate', reason: 'no autonomy policy granted' }))
const approved = decisions.filter((d) => d.decision === 'approve')
const escalated = decisions.filter((d) => d.decision === 'escalate')
const denied = decisions.filter((d) => d.decision === 'deny')

// ---- Execute (gate-executor runs ONLY approved, reversible, in-scope actions) ----
phase('Execute')
let executed = null
if (reviewBlock && approved.length) {
  log(`Execution suppressed: the Reviewer blocked the change — even approved gates are escalated to the human.`)
} else if (autonomy && approved.length) {
  executed = await agent(
    `You are the SDLC Gate Executor (separation of duties — you did not decide or raise these). ` +
      `Execute ONLY these already-APPROVED, reversible, non-prod, in-scope actions — verbatim, one ` +
      `at a time, verify and audit each. NEVER push to a protected branch, merge, deploy, apply to ` +
      `real infra, touch secrets/prod, or do anything not in this approved list; if any is ambiguous ` +
      `or out of scope, SKIP and escalate. Follow ~/.claude/rules/workflow-gated-actions.md.\n\n` +
      `Granted autonomy: ${JSON.stringify(autonomy)}\n\nApproved actions: ${JSON.stringify(approved).slice(0, 6000)}`,
    { label: 'gate-executor', phase: 'Execute', agentType: 'sdlc-gate-executor' },
  )
  log(`Executed ${approved.length} approved (reversible/non-prod) action(s) via the gate-executor.`)
} else if (approved.length) {
  log(`${approved.length} action(s) approvable but no autonomy granted → left for the human.`)
}

// ---- Gate review (escalations stay with the human; nothing escalated/denied was executed) ----
phase('Gate Review')
log(
  gateRequests.length
    ? `GATE REVIEW — approved ${approved.length} (executed: ${executed ? 'yes' : 'no'}) · denied ` +
        `${denied.length} · escalated ${escalated.length}. The ${escalated.length} escalation(s) ` +
        `require HUMAN approval; the workflow executed nothing escalated or denied.`
    : 'No gated actions proposed by the architects.',
)

return {
  goal,
  assumptions: (plan && plan.assumptions) || [],
  workstreams: work.map((w) => ({ id: w.workstream, role: w.role, summary: w.summary, artifacts: w.artifacts || [] })),
  integration,
  review: { verdict: (review && review.verdict) || null, findings: reviewFindings, blocked: reviewBlock },
  gateRequests,
  gateDecisions: decisions,
  approved,
  executed,
  escalations: escalated,
  denied,
  needsEngineers: work.flatMap((w) => w.needsEngineers || []),
  tokensSpent: budget.total ? budget.spent() : undefined,
  note:
    'Autonomous phases done in isolated worktrees. With autonomy granted, the gate-executor ran ONLY ' +
    'the approved reversible/non-prod class (separation of duties from the approver). Escalations ' +
    'and denials were NOT executed — the human rules on escalations in the main session.',
}
