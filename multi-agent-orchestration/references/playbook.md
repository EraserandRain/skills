# Multi-Agent Orchestration Playbook

This playbook explains how to run a checklist-driven multi-agent workflow while
keeping the current session as the `master`.

Use `references/templates.md` for exact checklist shapes, field lists, worktree
preflight, integration protocol fields, subagent prompts, acceptance flow,
retry stop rules, and dispatch budget rules. This playbook records the
operating model and decision principles only.

## Role Model

The workflow has four roles:

- `master`: always the current agent. Owns intake, checklist structure,
  dispatch, acceptance, retry routing, and final reporting. The master does not
  implement feature code or patch failed submissions.
- `explorer`: optional analysis role. Maps impact, dependencies, risks,
  suggested write boundaries, and acceptance commands. It does not implement.
- `worker`: implementation role. Owns one checklist item, or a small set of
  same-phase items with non-overlapping write scopes. It edits only inside its
  assigned `write_allowlist`.
- `verification worker`: `worker` agent with a verification-only prompt. Runs
  independent checks and reports evidence. It does not fix implementation
  failures.

All subagents must follow the shared execution guardrails:

- make material assumptions and blockers explicit
- prefer the simplest sufficient path for the assigned role
- stay within the assigned scope and write boundaries
- provide concrete verification evidence or clearly stated blockers

For risky delegated work, the master should add explicit prompt rules for
assumptions, minimal changes, scope control, and blockers.

## Codex Agent Types

Use the available Codex agent types directly:

- Use `agent_type: explorer` for impact analysis, dependency mapping, and task
  shaping.
- Use `agent_type: worker` for implementation work.
- Use `agent_type: worker` for verification work with a verification-only
  prompt; do not invent a `validator` agent type.
- Close every subagent after acceptance, rejection, cancellation, replacement,
  or a blocked verdict.

## Codex Tool Operations

Before spawning agents, the master should decide which work is on the critical
path and which bounded sidecar tasks can run without blocking the next master
action. Do not hand off the immediate blocker when the master can resolve it
faster locally through orchestration work such as checklist refinement,
baseline inspection, or acceptance planning.

The exact `spawn_agent`, `fork_context`, `wait_agent`, `send_input`, review,
integration protocol, and closure checklist lives in `references/templates.md`.

## Master Boundary

The master should:

- turn the request into acceptance-oriented checklist items
- assign `write_allowlist`, `acceptance_commands`, and `done_definition`
- plan phases, lanes, dependencies, and concurrency risk when parallel work is
  needed
- dispatch and close subagents
- review changed files, summaries, and evidence
- run or delegate acceptance commands
- update item status and retry metadata
- record the git/worktree baseline before dispatching implementation workers

The master should not:

- directly patch implementation files to rescue a failed worker
- expand a worker's scope after dispatch without updating the checklist
- keep long-lived catch-all workers open across unrelated items
- bury checklist state in free-form conversation
- let verification workers become implementation workers
- stage, unstage, commit, reset, or rewrite history unless the user explicitly
  asked for that exact git action

## Checklist Design

A checklist is an acceptance contract, not a loose task list. Each item should
let the master accept, reject, or block without stepping into implementation.

Use the smallest checklist mode that proves acceptance:

- `compact` for a single explorer, worker, or isolated delegation.
- `lightweight_parallel` for exactly two independent workers with no overlap.
- `full` for three or more workers, shared foundations, retries, explicit
  allow/block boundaries, environment locks, or unclear coupling.

Parallel meta and concurrency fields belong only to full parallel work unless a
specific coordination risk appears. Status values and exact field names live in
`references/templates.md`.

Checklist items should be result-oriented. Prefer "the command accepts X and
returns Y" over "edit file Z". `done_definition` must be clear enough that a
new agent can validate it without verbal context.

Use explicit owner values such as `master`, `unassigned`, or
`worker:<agent-id-or-nickname>` so agent closure and handoff state remain
traceable.

## State Machine

Use the status enum defined in `references/templates.md`.

Recommended transitions:

```text
todo -> assigned -> submitted -> accepted
                     |
                     v
                    redo -> assigned -> submitted

todo/assigned/submitted -> blocked
blocked -> todo/assigned
todo/assigned/redo -> cancelled
```

Important constraints:

- The master accepts only after `submitted`; it does not patch during
  `assigned`.
- Rejection goes through `redo` before reassignment so the failed attempt stays
  visible.
- `blocked` items must record what condition would unblock them.

## Concurrency Rules

Concurrency is useful only when ownership boundaries are clear.

In short: one file has one write owner, highly coupled directories usually have
one owner, and unclear ownership should collapse to serial delivery. The exact
admission checks, caps, budget fields, and backlog rules live in
`references/templates.md` and `references/parallel-strategy.md`.

Keep detailed phase, lane, and budget policy in
`references/parallel-strategy.md`; this playbook only records the core
admission rules.

## Phase Flow

For full parallel or high-coupling tasks, use this flow:

1. `phase-0 / intake`: master clarifies objective, hard constraints, and
   allowed delivery shape.
2. `phase-1 / explore`: optional explorer maps impact, risks, dependencies,
   suggested write scopes, and acceptance commands.
3. `phase-2 / checklist`: master normalizes acceptance-oriented items.
4. `phase-3 / dispatch`: master starts bounded workers only after dependencies
   and write scopes are clear.
5. `phase-4 / acceptance`: master reviews summaries, changed files, and
   evidence; then accepts, rejects, or blocks.
6. `phase-5 / recovery`: master records failure details, closes failed workers,
   and launches replacements or reopens exploration.
7. `phase-6 / final verification`: master or a verification worker runs final
   acceptance checks and records concise evidence.

For a single explorer, a single worker, or a clearly isolated delegation, keep
the flow lightweight: checklist, dispatch, acceptance, closure. Use exploration
only when scope, coupling, or acceptance criteria are unclear.

For `lightweight_parallel`, keep the same lightweight flow but accept and
integrate returned work one item at a time.

## Failure Recovery

When acceptance fails, the master should:

1. Record the failed command or failed condition.
2. Decide whether this is a bounded in-scope correction or a replacement case.
3. For one small, clear, in-scope failure, use `send_input` once to ask the
   current worker for a bounded correction.
4. For out-of-scope edits, wrong approach, unclear root cause, or a second
   failure on the same item, set status to `redo`.
5. Record `failure_reason`, increment `retry_count`, and collect a short
   handoff summary when replacing the worker.
6. Close the failed worker and launch a replacement worker or reopen
   exploration.

Required handoff summary:

```text
changed_files:
commands_run:
what_passed:
what_failed:
suspected_root_cause:
next_agent_starting_point:
```

Retry and replacement guidance:

- First small failure on a valid item: allow one bounded correction from the
  current worker.
- Repeated failure on the same item: re-check decomposition, boundaries, and
  acceptance criteria before retrying.
- Two replacement failures on the same item: mark `blocked` with a concrete
  unblock condition.
- The same external blocker appearing twice: mark `blocked`.
- Out-of-scope edits: reject immediately and reduce concurrency for the phase.
- Environment or external dependency failure: mark `blocked` instead of cycling
  workers.

Use `references/templates.md` for the current worker, explorer, verification, and
acceptance prompt text.

## Best Practices

- Write checklist items as acceptance contracts.
- Use compact checklist mode for isolated delegation, and expand only when the
  workflow needs retries, parallel dispatch, dependencies, or explicit
  allow/block write boundaries.
- Split by write ownership before deciding whether to parallelize.
- Record the git/worktree baseline before implementation dispatch and preserve
  unrelated user changes during acceptance.
- Keep shared interfaces, schemas, entrypoints, and global config in an early
  serial phase.
- Require every worker to run the smallest meaningful self-check, or explicitly
  report why it could not.
- Keep evidence concise and referential; do not paste long logs into the
  checklist.
- Close subagents promptly after acceptance, rejection, cancellation,
  replacement, or a blocked verdict.
- Use a verification worker when risk, cost, or parallel submissions justify
  independent evidence.

## Anti-Patterns

- The master fixes a failed worker's code directly.
- Multiple workers edit the same entrypoint, fixture, config file, or coupled
  directory at the same time.
- Checklist items describe files to edit but not acceptance conditions.
- Failures are retried without recording `failure_reason` and `retry_count`.
- A worker stays alive across unrelated items and becomes a catch-all context.
- A verification worker patches code while claiming to verify only.
- A worker changes git staging state or history without explicit user approval.

## Operating Principle

The master decomposes, dispatches, accepts, rejects, updates the checklist, and
closes agents. Workers implement. Failed implementation may get one bounded
in-scope correction from the current worker; otherwise it goes to a replacement
worker or back to exploration, not into a master-side patch.
