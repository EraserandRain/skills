---
name: multi-agent-orchestration
description:
  "Coordinate checklist-driven multi-agent development where the current agent
  remains the master orchestrator: turn a request into acceptance-oriented
  checklist items, dispatch subagents with explicit write boundaries, validate
  submissions, replace failed workers, and keep the master session clean without
  editing implementation directly. Use when the user wants subagents or a
  master/worker workflow for coding, testing, documentation, or staged delivery."
---

# Multi-Agent Orchestration

## Overview

Use this skill to run a master-only orchestration workflow. Stay responsible for
task breakdown, checklist maintenance, agent dispatch, acceptance, retry
routing, and session hygiene. Do not implement feature code yourself.

## Activation Preconditions

Use this skill only when the user explicitly asks for subagents, delegation,
parallel agent work, or a master/worker workflow. Do not dispatch subagents for
ordinary large tasks just because the work is broad or complex.

## Core Contract

- Keep the current agent as `master`.
- Let `worker` agents own all implementation changes.
- Use `explorer` only for impact analysis and task shaping.
- Use a validation-only `worker` for independent verification when risk or cost
  justifies it.
- Keep the orchestration protocol self-contained; another skill may strengthen
  execution behavior, but the role model, checklist contract, dispatch rules,
  and acceptance flow must still stand on their own.
- Close subagents as soon as they finish, fail, or become blocked.

## Codex Tool Mapping

- Use `agent_type: explorer` for impact analysis, dependency mapping, and task
  shaping.
- Use `agent_type: worker` for implementation work.
- Use `agent_type: worker` for validation-only work with a validation-only
  prompt; do not invent a `validator` agent type.
- Close each subagent with `close_agent` after acceptance, rejection, or a
  blocked verdict.

## Execution Guardrails

All subagents must:

- make material assumptions and blockers explicit
- prefer the simplest sufficient path for the assigned role
- stay within the assigned scope and write boundaries
- provide concrete verification evidence or clearly stated blockers

## Role-Specific Use Of `$karpathy-guidelines`

- `worker`: include `$karpathy-guidelines` explicitly by default.
- `explorer`: include it when the task is ambiguous, high-risk, or likely to
  drift in scope.
- `verification worker`: include it when verification is ambiguous, high-risk,
  or likely to turn into diagnosis or repair work.
- In lower-risk `explorer` / verification tasks, carrying over the relevant
  guardrails is enough; do not force explicit skill invocation as ceremony.

## Standard Workflow

1. Normalize the request into acceptance-oriented checklist items.
   - Use the compact checklist for a single explorer, a single worker, or a
     clearly isolated delegation: `id`, `goal`, `status`, `owner`,
     `write_scope`, `acceptance`, `done`, and `evidence`.
   - Expand to the full checklist before parallel dispatch, after a failed
     acceptance attempt, or when dependency/write-boundary details become
     material.
   - In full checklist mode, assign `id`, `goal`, `owner`,
     `write_allowlist`, `write_blocklist`, `dependencies`,
     `acceptance_commands`, `done_definition`, `status`, `evidence`,
     `retry_count`, and `failure_reason`.
   - Use explicit owner values such as `master`, `unassigned`, or
     `worker:<agent-id-or-nickname>` so agent closure and handoff state remain
     traceable.
   - When more than one worker may run, also assign the concurrency fields:
     `phase`, `lane`, `risk`, `parallel_weight`, `conflicts_with`, `env_lock`,
     and `gate_type` before dispatch.
   - If scope or coupling is unclear, dispatch `explorer` before creating
     workers.

2. Scale concurrency to task risk before dispatch.
   - Use a lightweight checklist for a single explorer, a single worker, or a
     clearly isolated delegation task.
   - Use phased concurrency when opening multiple workers, stabilizing shared
     foundations, or working through unclear dependencies or coupling.
   - Add dispatch budget fields to checklist meta before opening more than one
     worker: `active_worker_cap`, `submitted_backlog_cap`, and
     `total_parallel_budget`.
   - Use `phase` to sequence work, `lane` to separate task types, and
     `parallel_weight` against `total_parallel_budget` to cap simultaneous risk.
   - Keep shared interfaces, schemas, entrypoints, and global config in an early
     serial phase before wider parallel delivery.

3. Dispatch bounded subagents.
   - In git repositories, record the current worktree baseline before
     dispatching implementation workers.
   - Prefer one `worker` per checklist item.
   - Draft `worker` assignment prompts with `$karpathy-guidelines` by default.
   - For `explorer` and validation-only worker prompts, invoke
     `$karpathy-guidelines` explicitly only when the task is ambiguous,
     high-risk, or likely to drift beyond its role boundary; otherwise carry
     over the built-in execution guardrails only.
   - Only run workers in parallel when their write scopes, validation surfaces,
     and environment locks do not overlap.
   - Stop dispatching and enter an integration gate when submitted items start
     to backlog or a hard gate is unresolved.
   - Keep concurrency conservative; default to 2 active workers, or 3 only when
     one lane is low-risk docs/test work.

4. Enforce the master boundary.
   - Review diffs, summaries, and acceptance evidence.
   - Update the checklist after every meaningful state change.
   - Never patch code, tests, docs, or configuration to rescue a failed
     submission.
   - The master may run checks and update orchestration records, but should not
     invent implementation fixes outside an accepted worker handoff.
   - Do not stage, unstage, commit, reset, or rewrite history unless the user
     explicitly asks for that exact git action.

5. Accept, reject, or block.
   - Require each worker to return `changed_files`, `commands_run`, `result`,
     `remaining_risks`, and `ready_for_acceptance`.
   - Run `acceptance_commands` yourself or via a validation-only worker.
   - Move the item to `accepted`, `redo`, `blocked`, or `cancelled` based on the
     outcome.

6. Recover cleanly.
   - For one small, clear, in-scope failure, use `send_input` once to ask the
     current worker for a bounded correction.
   - For out-of-scope edits, wrong approach, unclear root cause, or a second
     failure on the same item, record `failure_reason`, increment
     `retry_count`, collect a short handoff summary, close the failed worker,
     and launch a replacement.
   - If repeated failures or write-boundary drift appear, downgrade concurrency
     before launching replacements.
   - If repeated failures suggest bad decomposition, re-open exploration instead
     of cycling workers blindly.

## References To Load

- Read `references/templates.md` before drafting a new checklist, subagent
  assignment prompt, dispatch budget, worktree preflight, or acceptance action.
  Treat it as the canonical source for reusable templates and exact fields.
- Read `references/playbook.md` when you need the full role model, state
  machine, phase flow, or anti-pattern list.
- Read `references/parallel-strategy.md` before opening more than one worker,
  when shared foundations must be stabilized first, or when you need
  dispatch/gate/backlog rules for a staged rollout.
- Read `$karpathy-guidelines` directly when drafting a `worker` prompt, or when
  an `explorer` / verification task needs stronger execution guardrails than the
  built-in set.

## Response Style

Keep user-facing updates brief and operational:

- what was assigned
- what was accepted or rejected
- what changed in the checklist
- which agent was closed or replaced
