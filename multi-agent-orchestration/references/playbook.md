# Multi-Agent Orchestration Playbook

This playbook explains how to run a checklist-driven multi-agent workflow while
keeping the current session as the `master`.

Use `references/templates.md` for the exact checklist shapes, field lists,
status values, worktree preflight, subagent prompts, acceptance flow, and
dispatch budget rules.

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
- `validation worker`: validation-only `worker` agent. Runs independent checks
  and reports evidence. It does not fix implementation failures.

All subagents must follow the shared execution guardrails:

- make material assumptions and blockers explicit
- prefer the simplest sufficient path for the assigned role
- stay within the assigned scope and write boundaries
- provide concrete verification evidence or clearly stated blockers

Implementation workers should explicitly use `$karpathy-guidelines`.
Explorers and validation workers use it only when the task is ambiguous,
high-risk, or likely to drift beyond the assigned role.

## Codex Agent Types

Use the available Codex agent types directly:

- Use `agent_type: explorer` for impact analysis, dependency mapping, and task
  shaping.
- Use `agent_type: worker` for implementation work.
- Use `agent_type: worker` for validation-only work with a validation-only
  prompt; do not invent a `validator` agent type.
- Close every subagent after acceptance, rejection, or a blocked verdict.

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
- let validation workers become implementation workers
- stage, unstage, commit, reset, or rewrite history unless the user explicitly
  asked for that exact git action

## Checklist Design

A checklist is an acceptance contract, not a loose task list. Each item should
let the master accept, reject, or block without stepping into implementation.

Use the compact checklist from `references/templates.md` for a single explorer,
a single worker, or a clearly isolated delegation. Expand to the full checklist
before parallel dispatch, after a failed acceptance attempt, or when dependency
and write-boundary details become material.

For parallel work, add the dispatch budget fields to checklist meta before
opening workers. Then add the per-item concurrency fields defined in
`references/templates.md`.

Checklist items should be result-oriented. Prefer "the command accepts X and
returns Y" over "edit file Z". `done_definition` must be clear enough that a
new agent can validate it without verbal context.

Use explicit owner values such as `master`, `unassigned`, or
`worker:<agent-id-or-nickname>` so agent closure and handoff state remain
traceable.

## State Machine

Use this status set:

- `todo`: defined but not assigned
- `assigned`: assigned to an agent
- `submitted`: worker has returned a result and is awaiting acceptance
- `accepted`: accepted by the master
- `redo`: rejected and waiting for a replacement worker
- `blocked`: blocked by missing information, environment, or external dependency
- `cancelled`: no longer needed or merged into another item

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

For multi-worker or high-coupling tasks, use this flow:

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
7. `phase-6 / final validation`: master or a validation-only worker runs final
   acceptance checks and records concise evidence.

For a single explorer, a single worker, or a clearly isolated delegation, keep
the flow lightweight: checklist, dispatch, acceptance, closure. Use exploration
only when scope, coupling, or acceptance criteria are unclear.

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
- Out-of-scope edits: reject immediately and reduce concurrency for the phase.
- Environment or external dependency failure: mark `blocked` instead of cycling
  workers.

Use `references/templates.md` for the current worker, explorer, validation, and
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
- Close subagents promptly after they submit, fail, or become blocked.
- Use a validation-only worker when risk, cost, or parallel submissions justify
  independent evidence.

## Anti-Patterns

- The master fixes a failed worker's code directly.
- Multiple workers edit the same entrypoint, fixture, config file, or coupled
  directory at the same time.
- Checklist items describe files to edit but not acceptance conditions.
- Failures are retried without recording `failure_reason` and `retry_count`.
- A worker stays alive across unrelated items and becomes a catch-all context.
- A validation worker patches code while claiming to validate only.
- A worker changes git staging state or history without explicit user approval.

## Operating Principle

The master decomposes, dispatches, accepts, rejects, updates the checklist, and
closes agents. Workers implement. Failed implementation may get one bounded
in-scope correction from the current worker; otherwise it goes to a replacement
worker or back to exploration, not into a master-side patch.
