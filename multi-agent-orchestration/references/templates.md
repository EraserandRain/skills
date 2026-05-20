# Templates

This file is the canonical source for reusable orchestration templates,
checklist fields, status values, dispatch budget fields, integration protocol
fields, and acceptance action shapes. Other references should summarize these
contracts and link back here instead of copying full templates.

## Compact Checklist Template

Use this for a single explorer, a single worker, or a clearly isolated
delegation where parallel dispatch, retries, and dependency management are not
yet needed.

```md
# Checklist

## Meta

- objective:
- owner: master
- updated_at:
- mode: compact
- notes:

## Items

### ITEM-001

- id: ITEM-001
- goal:
- status: todo
- owner: unassigned
- write_allowlist:
  - path-or-area/
- acceptance:
  - command or check
- done:
  - condition
- evidence:
- notes:
```

Compact defaults:

- `dependencies`: none
- `write_blocklist`: none unless a boundary is risky
- `retry_count`: 0
- `failure_reason`: blank

Stay compact by default. Use the lightweight parallel template for exactly two
independent workers. Expand to the full template only before dispatching three
or more workers, after a failed acceptance attempt, when dependencies become
material, or when the write scope needs explicit allow/block boundaries.

## Lightweight Parallel Checklist Template

Use this when exactly two workers can run at the same time and their write
scopes, acceptance commands, and expected outputs are clearly independent. If
any of those checks are unclear, use the full checklist or keep delivery serial.

```md
# Checklist

## Meta

- objective:
- owner: master
- updated_at:
- mode: lightweight_parallel
- notes:

## Items

### ITEM-001

- id: ITEM-001
- goal:
- status: todo
- owner: unassigned
- write_allowlist:
  - path-or-area/
- dependencies:
  - none
- acceptance:
  - command or check
- done:
  - condition
- evidence:
- notes:
```

Do not add `dispatch_budget`, `phase`, `lane`, `env_lock`, or `gate_type` in
lightweight parallel mode unless a concrete coordination risk appears. If that
happens, expand the affected item to the full template.

## Full Checklist Item Template

```md
# Checklist

## Meta

- objective:
- owner: master
- updated_at:
- acceptance_owner: master
- mode: full
- notes:

## Items

### ITEM-001

- id: ITEM-001
- title:
- goal:
- status: todo
- owner: unassigned
- dependencies:
  - none
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

## Parallel Dispatch Budget Appendix

Add this to checklist `Meta` only in full parallel mode, usually before opening
three or more workers or when shared foundations, retries, environment locks, or
hard gates require explicit coordination:

```md
- dispatch_budget:
  - active_worker_cap: 2
  - max_low_risk_cap: 3
  - submitted_backlog_cap: 2
```

## Concurrency Fields Appendix

Add these fields only in full parallel mode, or when shared foundations,
dependencies, retries, or environment locks need explicit coordination:

```md
- phase:
- lane:
- risk:
- conflicts_with:
  - ITEM-000
- env_lock:
- gate_type:
```

Add `unblock_condition` only when `status = blocked`:

```md
- unblock_condition:
```

Rules:

- Compact item fields: `id`, `goal`, `status`, `owner`, `write_allowlist`,
  `acceptance`, `done`, and `evidence`.
- Lightweight parallel item fields: compact fields plus `dependencies`.
- Full item fields: `id`, `goal`, `status`, `owner`,
  `dependencies`, `write_allowlist`, `write_blocklist`, `acceptance_commands`,
  `done_definition`, `evidence`, `retry_count`, and `failure_reason`.
- Concurrency-only fields for full parallel mode: `phase`, `lane`, `risk`,
  `conflicts_with`, `env_lock`, and `gate_type`.
- Parallel meta fields for full parallel mode:
  `active_worker_cap`, `max_low_risk_cap`, and `submitted_backlog_cap`.
- Do not add parallel meta or concurrency fields to compact or
  `lightweight_parallel` work unless a concrete dependency, shared write
  surface, environment lock, or retry risk requires them.
- Use owner values that remain traceable: `master`, `unassigned`, or
  `worker:<agent-id-or-nickname>`.
- Restrict `status` to the agreed enum.
- Let only the master update `retry_count`.
- Use `phase`, `lane`, and `risk` before dispatching full parallel work.
- Use `gate_type: hard` for shared contracts, entrypoints, schemas, or global
  config; use `soft` for isolated follow-up work.
- Use `unblock_condition` only when `status = blocked`.
- Keep `evidence` short and referential, not a full log dump.

## Status Enum

Use only these status values:

- `todo`: defined but not assigned
- `assigned`: assigned to an agent
- `submitted`: worker has returned a result and is awaiting acceptance
- `accepted`: accepted by the master
- `redo`: rejected and waiting for a replacement worker
- `blocked`: blocked by missing information, environment, or external dependency
- `cancelled`: no longer needed or merged into another item

## Git / Worktree Preflight Template

Use this before dispatching implementation workers in a git repository.

```md
# Worktree Baseline

- baseline_command: git status --short
- staged_state:
- unstaged_state:
- user_owned_changes:
- protected_git_actions:
  - do not stage unless explicitly asked
  - do not unstage unless explicitly asked
  - do not commit unless explicitly asked
  - do not reset or rewrite history unless explicitly asked
- acceptance_diff_check:
  - compare changed files against baseline
  - reject or reroute out-of-scope edits
  - preserve unrelated user changes
```

For non-git workspaces, record the equivalent file-state boundary in plain
language before dispatch.

## Integration Protocol Template

Use this when a worker returns uploaded changes, branch/worktree output, a patch,
or any submission that must be applied or merged into the master's workspace.

```md
# Integration Protocol

- item_id:
- base_revision:
- integration_method:
  - uploaded_changes | branch | worktree | patch | direct_workspace
- conflict_owner: master
- applied_files:
  - path/
- post_apply_checks:
  - command or check
- integration_evidence:
```

Rules:

- Record `base_revision` before dispatch when the workspace is a git repository.
- Prefer one submitted item at a time; do not apply a dependent submission until
  its dependencies are accepted.
- Compare `applied_files` against the worker's `changed_files`,
  `write_allowlist`, and the recorded baseline.
- If the submission has conflicts, out-of-scope edits, or shared-surface drift,
  reject or block it instead of patching around the problem in the master
  session.
- Run `post_apply_checks` after applying each accepted submission.

## Codex Tool Operation Template

Use this checklist before and during dispatch:

```md
# Codex Tool Operations

- critical_path_owner: master
- sidecar_candidates:
  - ITEM-000
- spawn_rule:
  - spawn only material checklist items with clear role, ownership, and
    acceptance evidence
- fork_context:
  - true when the worker needs current conversation, checklist, or discovered
    repo context
  - false when the assignment is self-contained and narrower context is safer
- wait_rule:
  - wait only when the master is blocked on a submitted result
  - keep doing non-overlapping master work while workers run
- review_rule:
  - inspect changed_files, worker summary, evidence, and actual diff against the
    recorded baseline before accepting
- correction_rule:
  - use send_input once for a small, clear, in-scope correction
  - replace the worker or reopen exploration for broader failures
- close_rule:
  - close each agent after acceptance, rejection, cancellation, replacement, or
    blocked verdict
```

## Execution Guardrails

Apply these to every subagent prompt:

- make material assumptions and blockers explicit
- prefer the simplest sufficient path for the assigned role
- stay within the assigned scope and write boundaries
- provide concrete verification evidence or clearly stated blockers

## Subagent Assignment Prompt Templates

For risky delegated work, add explicit prompt rules for assumptions, minimal
changes, scope control, and blockers.

### Worker Assignment Prompt Template

```text
You own checklist item: <ITEM-ID>

Role contract:
- Own implementation and the smallest relevant self-checks only.
- Do not edit the checklist.
- Do not modify files outside the write_allowlist.
- Do not take over other checklist items.
- You are not alone in the codebase: do not revert edits made by others, and
  adapt your implementation to concurrent changes when they appear.

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

Default: use this template with the built-in execution guardrails.

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

Default: use this template with the built-in execution guardrails. Spawn this as
a `worker` agent with a verification-only prompt; do not use an unsupported
`validator` agent type.

```text
You own verification for checklist item: <ITEM-ID>

Role contract:
- Run independent verification and summarize evidence only.
- Do not implement fixes or expand scope.
- Do not edit the checklist.
- Do not modify files unless the prompt explicitly authorizes a verification-only
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
- If verification fails, describe the failure precisely and stop; do not patch the
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

## Step 2B: Integrate One Submission

Use this step when multiple workers have submitted changes:

- process one submitted item at a time
- record or update the item's integration protocol before applying the
  submission
- inspect the actual diff, not only the worker summary
- compare changed files against the recorded write_allowlist and baseline
- integrate only after the changed files are in scope
- rerun the item acceptance command or a shared smoke check after each
  integration
- accept or reject the integrated item before processing the next dependent item
- treat conflicts, out-of-scope edits, or shared-surface drift as `redo` or
  `blocked`; do not patch around them in the master session

## Step 3A: Accept

Conditions:

- all done_definition conditions satisfied
- acceptance_commands passed
- no out-of-scope edits

Actions:

- set status = accepted
- update evidence
- close current worker

## Step 3B: Correct Current Worker Once

Triggers:

- acceptance command failed for a small, clear, in-scope reason
- done_definition is almost met and no checklist change is needed
- current worker did not drift outside `write_allowlist`

Actions:

- keep status = assigned or submitted, depending on whether a new handoff is due
- record concise failure evidence
- send one bounded correction prompt with `send_input`
- require the same final report format

## Step 3C: Reject And Replace

Triggers:

- out-of-scope edits detected
- implementation approach is wrong or unclear
- same item failed after one bounded correction
- checklist must be decomposed before more implementation
- risk exceeds the allowed threshold

Actions:

- set status = redo
- increment retry_count
- fill failure_reason
- collect handoff summary
- close current worker
- assign replacement worker

Stop rule:

- after two replacement failures on the same item, set status = blocked
- if the same external blocker appears twice, set status = blocked
- record the concrete unblock_condition before closing the worker

## Step 3D: Block

Triggers:

- missing external dependency
- environment prevents valid acceptance
- checklist lacks enough information for a reliable verdict

Actions:

- set status = blocked
- record unblock_condition
- close current worker
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

## Lane Policy

- `core`: shared logic or risky implementation; default cap 1
- `test`: isolated tests or fixtures; may run with `core` only if scopes do not
  overlap
- `docs`: docs/examples only after the related contract is stable
- `verify`: verification worker lane; does not take implementation ownership

## Open A New Worker Only If

- all `dependencies` are `accepted`
- no `write_allowlist` overlap exists with active workers
- `conflicts_with` does not point to an active item
- required `env_lock` is free
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
