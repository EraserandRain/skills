# Parallel Strategy

Use this guide when the master may open more than one worker, or when shared
foundations must be stabilized before wider fan-out.

## Three-Layer Model

- `phase`: define ordering. Use phases to keep shared contracts, entrypoints, or
  config changes ahead of parallel delivery.
- `lane`: define task type. Common lanes are `core`, `test`, `docs`, and
  `verify`.
- `budget`: define how much simultaneous risk is allowed. Budget is not just
  worker count; it is the sum of active `parallel_weight`.

Treat these as checklist fields, not as loose planning notes.

## Recommended Phase Split

Use this default sequence unless the task is clearly smaller:

1. `phase-0 / intake`
   - master only
   - normalize the request, hard constraints, and checklist

2. `phase-1 / explore`
   - usually one `explorer`
   - map impact, dependencies, risky shared files, and suggested write
     boundaries

3. `phase-2 / foundation`
   - usually one `core` worker
   - stabilize shared interfaces, schemas, entrypoints, migrations, or global
     config

4. `phase-3 / parallel-delivery`
   - two workers by default, three only when one lane is low-risk `test` or
     `docs`
   - implement independent modules or follow-up work with non-overlapping write
     scopes

5. `phase-4 / integration-gate`
   - stop new delivery dispatch
   - accept, reject, reroute, and collect evidence

6. `phase-5 / sidecars-and-final-validation`
   - optional `docs`, `test`, and `verify` follow-up
   - final acceptance and cleanup

## Lane Model

- `core`: risky implementation or shared logic; keep this lane narrow
- `test`: targeted tests, fixtures, or validation helpers; do not overlap with
  active `core` test surfaces
- `docs`: user-facing docs or examples; prefer after interfaces stabilize
- `verify`: validation-only worker lane for independent acceptance evidence

Give each checklist item one primary lane so the master can reason about caps
and conflicts quickly.

## Budget Model

Start with a total budget of `4`.

- `high` risk item -> `parallel_weight: 3`
- `medium` risk item -> `parallel_weight: 2`
- `low` risk item -> `parallel_weight: 1`

Safe default combinations:

- `1 high + 1 low`
- `2 medium`
- `1 medium + 2 low`

Do not use a larger budget unless the repository boundaries are already proven
stable for this task.

## Admission Rules

Open a new worker only when all of the following are true:

- the item's `dependencies` are `accepted`
- no active worker overlaps the item's `write_allowlist`
- `conflicts_with` does not name an active item
- required `env_lock` is free
- adding the item keeps active `parallel_weight` within budget
- the current `submitted` backlog is below the cap
- no unresolved `hard` gate blocks the current phase

If one of these checks is unclear, keep the work serial.

## Stage Gates

Use two gate types:

- `hard`: shared contracts, schemas, CLI entrypoints, global config, migrations,
  or anything that must settle before more fan-out
- `soft`: isolated tests, docs, or independent follow-up work

Rules:

- do not enter a wider phase while a `hard` gate item is `submitted`, `redo`, or
  `blocked`
- allow `soft` gate items to overlap only when their write scope is isolated
- enter `phase-4 / integration-gate` before starting any new branch that depends
  on a just-landed shared foundation

## Submitted Backlog Control

Keep `submitted` backlog at `2` or less.

Why:

- the master must be able to accept or reject items without creating an evidence
  queue
- too many pending submissions hide dependency mistakes and boundary drift

Rule:

- if backlog reaches `2`, stop opening new workers
- clear the backlog in the integration gate before resuming dispatch

## Failure Downgrade Strategy

Use rejection to lower concurrency when the system shows instability.

- first failure on an item: mark `redo`, replace the worker, keep the same phase
  if the boundary still looks valid
- second failure on the same item: pause the lane, re-check decomposition, and
  consider reopening `explorer`
- any out-of-scope edit: reject immediately and reduce active worker cap by one
  for the rest of the phase
- repeated boundary drift or shared-surface conflicts: collapse to serial
  delivery until a new foundation plan is accepted

Do not let the master patch around a failed phase. Change the checklist, not the
implementation.

## Default Strategy

Use this unless the task proves it needs something else:

- `phase-0`: master only
- `phase-1`: max `1 explorer`
- `phase-2`: max `1 core worker`
- `phase-3`: max `2 workers`; allow `3` only when the third is low-risk `test`
  or `docs`
- `phase-4`: no new delivery workers; accept or reroute only
- `phase-5`: max `1 implementation worker + 1 validation-only worker`
- `submitted_backlog_cap: 2`
- one shared directory or shared file owner at a time

## Example Task Split

Example: add a new CLI feature with implementation, tests, and docs.

`phase-1 / explore`

- `ITEM-001`, lane `core`: inspect `scripts/main.py`, `scripts/commands/`,
  affected tests, and docs; propose boundaries

`phase-2 / foundation`

- `ITEM-002`, lane `core`, gate `hard`: update shared CLI contract and command
  registration in `scripts/main.py`

`phase-3 / parallel-delivery`

- `ITEM-003`, lane `core`: implement command logic in
  `scripts/commands/<feature>.py`
- `ITEM-004`, lane `test`: add isolated tests in `tests/test_<feature>.py`
- optional `ITEM-005`, lane `docs`, risk `low`: update examples after `ITEM-002`
  is accepted

`phase-4 / integration-gate`

- master accepts `ITEM-003` and `ITEM-004`
- if `ITEM-003` fails, mark `redo`, close that worker, and do not open new
  `core` work until the replacement passes

`phase-5 / sidecars-and-final-validation`

- `ITEM-005` docs if still pending
- a validation-only worker runs the final acceptance commands and records
  concise evidence
