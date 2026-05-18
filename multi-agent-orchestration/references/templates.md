# Templates

## Master Checklist Template

```md
# Checklist

## Meta

- objective:
- owner: master
- updated_at:
- acceptance_owner: master
- notes:

## Items

### ITEM-001

- title:
- goal:
- status: todo
- phase:
- lane:
- risk:
- parallel_weight:
- owner:
- dependencies:
- conflicts_with:
- env_lock:
- gate_type:
- unblock_condition:
- write_allowlist:
  - path/
- write_blocklist:
  - path/
- acceptance_commands:
  - command 1
  - command 2
- done_definition:
  - condition 1
  - condition 2
- evidence:
- retry_count: 0
- failure_reason:
- notes:
```

Rules:

- Restrict `status` to the agreed enum.
- Let only the master update `retry_count`.
- Use `phase`, `lane`, and `parallel_weight` before dispatching more than one
  worker.
- Use `gate_type: hard` for shared contracts, entrypoints, schemas, or global
  config; use `soft` for isolated follow-up work.
- Use `unblock_condition` only when `status = blocked`.
- Keep `evidence` short and referential, not a full log dump.

## Execution Guardrails

Apply these to every subagent prompt, even when `$karpathy-guidelines` is not
invoked explicitly:

- make material assumptions and blockers explicit
- prefer the simplest sufficient path for the assigned role
- stay within the assigned scope and write boundaries
- provide concrete verification evidence or clearly stated blockers

## Subagent Assignment Prompt Templates

Use `$karpathy-guidelines` explicitly for implementation worker prompts by
default. For `explorer` and validation-only worker prompts, add it only when the
task is ambiguous, high-risk, or likely to drift beyond the assigned role.

### Worker Assignment Prompt Template

```text
Apply $karpathy-guidelines for this item.

You own checklist item: <ITEM-ID>

Role contract:
- Own implementation and the smallest relevant self-checks only.
- Do not edit the checklist.
- Do not modify files outside the write_allowlist.
- Do not take over other checklist items.

Execution guardrails:
- Make material assumptions and blockers explicit.
- Prefer the simplest sufficient implementation path.
- Stay within the assigned scope and write boundaries.
- Complete the required self-checks or clearly report blockers.

Goal:
<goal>

Done definition:
<done_definition>

Allowed write scope:
- <path-or-file>
- <path-or-file>

Blocked write scope:
- <path-or-file>
- <path-or-file>

Dependencies:
- <dependency or none>

Required self-checks before handoff:
- <command>
- <command>

Final report format:
changed_files:
commands_run:
result:
remaining_risks:
ready_for_acceptance:

Extra rules:
- If a material ambiguity changes the implementation, stop and report it
  instead of guessing.
- If the checklist is wrong or incomplete, report that instead of rewriting it.
- If blocked, explain the blocker and give the next agent a concrete starting point.
```

### Explorer Assignment Prompt Template

Default:

- Use this template with the built-in execution guardrails.
- Prepend `Apply $karpathy-guidelines for this item.` only when the exploration
  task is ambiguous, high-risk, or likely to drift in scope.

```text
You own exploration for checklist item: <ITEM-ID>

Role contract:
- Produce impact analysis, dependency notes, decomposition advice, and
  acceptance-shaping only.
- Do not implement the feature or take over delivery work.
- Do not edit the checklist.
- Do not modify files unless the prompt explicitly authorizes a tiny analysis
  artifact.

Execution guardrails:
- Make material assumptions and blockers explicit.
- Prefer the simplest sufficient analysis path.
- Stay within the assigned scope and read/write boundaries.
- Support conclusions with concrete evidence or clearly stated blockers.

Goal:
<goal>

Questions to answer:
- <question>
- <question>

Relevant read scope:
- <path-or-file>
- <path-or-file>

Allowed write scope:
- none by default

Final report format:
assumptions:
commands_run:
findings:
recommended_next_steps:
remaining_risks:
ready_for_dispatch:

Extra rules:
- If evidence is incomplete, say what is missing instead of guessing.
- If the safest recommendation is to simplify or reduce scope, say so directly.
```

### Verification Worker Assignment Prompt Template

Default:

- Use this template with the built-in execution guardrails.
- Prepend `Apply $karpathy-guidelines for this item.` only when validation is
  ambiguous, high-risk, or likely to turn into diagnosis or repair work.
- Spawn this as a `worker` agent with a validation-only prompt; do not use an
  unsupported `validator` agent type.

```text
You own validation for checklist item: <ITEM-ID>

Role contract:
- Run independent validation and summarize evidence only.
- Do not implement fixes or expand scope.
- Do not edit the checklist.
- Do not modify files unless the prompt explicitly authorizes a validation-only
  artifact.

Execution guardrails:
- Make material assumptions and blockers explicit.
- Prefer the smallest verification surface that can prove pass or fail.
- Stay within the assigned scope and read/write boundaries.
- Report concrete evidence or clearly stated blockers.

Goal:
<goal>

Acceptance commands:
- <command>
- <command>

Done definition:
<done_definition>

Allowed write scope:
- none by default

Final report format:
assumptions:
commands_run:
evidence:
failed_checks:
remaining_risks:
ready_for_acceptance:

Extra rules:
- If validation fails, describe the failure precisely and stop; do not patch the
  code.
- If the environment prevents a reliable verdict, report the blocker and missing
  prerequisite.
```

## Acceptance / Reject / Retry Template

```md
# Acceptance Flow

## Input

- item_id:
- current_status: submitted
- assigned_worker:
- acceptance_commands:
  - command 1
  - command 2
- done_definition:
  - condition 1
  - condition 2

## Step 1: Review

- check changed_files against write_allowlist
- review worker summary
- confirm no forbidden file changes

## Step 2: Validate

- run acceptance_commands
- capture concise evidence

## Step 3A: Accept

Conditions:

- all done_definition conditions satisfied
- acceptance_commands passed
- no out-of-scope edits

Actions:

- set status = accepted
- update evidence
- close current worker

## Step 3B: Reject

Triggers:

- acceptance command failed
- done_definition not met
- out-of-scope edits detected
- risk exceeds the allowed threshold

Actions:

- set status = redo
- increment retry_count
- fill failure_reason
- collect handoff summary
- close current worker
- assign replacement worker

## Step 3C: Block

Triggers:

- missing external dependency
- environment prevents valid acceptance
- checklist lacks enough information for a reliable verdict

Actions:

- set status = blocked
- record unblock_condition
- close or pause current worker
```

Optional reject appendix:

```text
rejection_reason:
failed_command:
failed_condition:
required_next_action:
replacement_agent_type:
```

## Master Dispatch Rules Template

```md
# Master Dispatch Rules

## Dispatch Budget

- active_worker_cap: 2
- max_low_risk_cap: 3
- submitted_backlog_cap: 2
- total_parallel_budget: 4

## Lane Policy

- `core`: shared logic or risky implementation; default cap 1
- `test`: isolated tests or fixtures; may run with `core` only if scopes do not
  overlap
- `docs`: docs/examples only after the related contract is stable
- `verify`: validation-only worker lane; does not take implementation ownership

## Open A New Worker Only If

- all `dependencies` are `accepted`
- no `write_allowlist` overlap exists with active workers
- `conflicts_with` does not point to an active item
- required `env_lock` is free
- `parallel_weight` keeps the active total within budget
- current `submitted` backlog is below the cap
- no unresolved `hard` gate blocks the current phase

## Stop Dispatching And Enter Integration Gate If

- `submitted` backlog reaches the cap
- any `hard` gate item is `submitted`, `redo`, or `blocked`
- two workers touch adjacent shared foundations and need acceptance before more
  fan-out
- a worker returns out-of-scope edits or boundary drift
- repeated failures suggest the decomposition is wrong

## Integration Gate Actions

- pause new worker creation
- accept or reject all submitted items
- update checklist evidence and retry counts
- reopen exploration or reduce concurrency if failures cluster
```
