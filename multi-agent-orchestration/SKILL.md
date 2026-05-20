---
name: multi-agent-orchestration
description:
  "Coordinate checklist-driven multi-agent development where the current agent
  remains the master orchestrator: turn a request into acceptance-oriented
  checklist items, dispatch subagents with explicit write boundaries, validate
  submissions, replace failed workers, and keep the master session clean without
  editing implementation directly. Use only when the user explicitly wants
  subagents, parallel agent work, or a master/worker workflow for coding,
  testing, documentation, or staged delivery."
---

# Multi-Agent Orchestration

## Overview

Use this skill to run a master-only orchestration workflow. Stay responsible for
task breakdown, checklist maintenance, agent dispatch, acceptance, retry
routing, and session hygiene. Do not implement worker-owned checklist items or
patch around failed worker submissions in the master session.

## Activation Preconditions

Use this skill only when the user explicitly asks for subagents, delegation,
parallel agent work, or a master/worker workflow. Do not dispatch subagents for
ordinary large tasks just because the work is broad or complex.

Do not use this skill for:

- ordinary large tasks when the user has not asked for subagents
- a single immediate blocker the master can resolve directly
- pure review, investigation, or Q&A work with no delegated execution

## Core Contract

- Keep the current agent as `master`.
- Let `worker` agents own all implementation changes.
- Use `explorer` only for impact analysis and task shaping.
- Use a `verification worker` for independent verification when risk, cost,
  or parallel submissions justify it.
- Keep the orchestration protocol self-contained; another skill may strengthen
  execution behavior, but the role model, checklist contract, dispatch rules,
  and acceptance flow must still stand on their own.
- Use `references/templates.md` as the single source of truth for checklist
  fields, status values, worker report shapes, integration protocol fields, and
  acceptance actions.

## Codex Tool Mapping

- Use `agent_type: explorer` for impact analysis, dependency mapping, and task
  shaping.
- Use `agent_type: worker` for implementation work.
- Use `agent_type: worker` for verification work with a verification-only
  prompt; do not invent a `validator` agent type.
- Close each subagent with `close_agent` after acceptance, rejection,
  cancellation, replacement, or a blocked verdict.

## Codex Tool Operations

- Before dispatching, decide which task remains on the master's critical path
  and which bounded sidecar tasks can safely run in subagents.
- Use `spawn_agent` only for material checklist items with clear role,
  ownership, and acceptance evidence.
- Set `fork_context: true` when the worker needs the current conversation,
  checklist, or discovered repo context; otherwise pass only the specific
  assignment context.
- Use `wait_agent` only when the master is blocked on a submitted result. While
  workers run, continue non-overlapping master work such as checklist updates,
  baseline checks, review prep, or acceptance command planning.
- Review returned `changed_files`, summaries, and evidence before accepting.
  If the worker produced uploaded changes or branch/worktree output, inspect the
  actual diff against the recorded baseline.
- Use `send_input` at most once for a small, clear, in-scope correction. Use a
  replacement worker or exploration for broader failures.
- Use `close_agent` promptly after an agent is accepted, rejected, cancelled,
  replaced, or blocked.

## Execution Guardrails

All subagents must:

- make material assumptions and blockers explicit
- prefer the simplest sufficient path for the assigned role
- stay within the assigned scope and write boundaries
- provide concrete verification evidence or clearly stated blockers

## Extra Prompt Rules

For risky delegated work, add explicit prompt rules for assumptions, minimal
changes, scope control, and blockers.

## Standard Workflow

1. Normalize the request into acceptance-oriented checklist items.
   - Stay compact for a single explorer, single worker, or isolated delegation.
   - Use `lightweight_parallel` for exactly two independent workers.
   - Expand to full checklist mode only for three or more workers, shared
     foundations, material dependencies, retries, environment locks, or explicit
     allow/block write boundaries.
   - Use the status enum and checklist fields defined in
     `references/templates.md`.
   - If scope or coupling is unclear, dispatch `explorer` before creating
     implementation workers.

2. Dispatch bounded subagents.
   - In git repositories, record the current worktree baseline before
     dispatching implementation workers.
   - Prefer one `worker` per checklist item.
   - Draft `worker` assignment prompts with explicit assumptions, scope control,
     and verification expectations.
   - Use verification workers only for evidence, not repair.
   - Run workers in parallel only when write scopes, verification surfaces, and
     environment locks do not overlap.

3. Accept, reject, or block submitted work.
   - Require each worker to return `changed_files`, `commands_run`, `result`,
     `remaining_risks`, and `ready_for_acceptance`.
   - Process submitted work one item at a time and inspect actual diffs before
     accepting.
   - Run acceptance checks yourself or via a verification worker.
   - Treat conflicts, out-of-scope edits, or shared-surface drift as `redo` or
     `blocked`; do not patch around them in the master session.
   - Use `send_input` at most once for a small, clear, in-scope correction.

4. Recover cleanly.
   - For out-of-scope edits, wrong approach, unclear root cause, or a second
     failure on the same item, record `failure_reason`, increment `retry_count`,
     close the failed worker, and launch a replacement or reopen exploration.
   - Stop replacing workers after two replacement failures for the same item.
   - If repeated failures or write-boundary drift appear, downgrade concurrency
     before launching replacements.

## References To Load

- Read `references/templates.md` before drafting a new checklist, subagent
  assignment prompt, dispatch budget, worktree preflight, integration protocol,
  or acceptance action. Treat it as the canonical source for reusable templates
  and exact fields.
- Read `references/playbook.md` when you need the full role model, state
  machine, phase flow, or anti-pattern list.
- Read `references/parallel-strategy.md` before full parallel dispatch, when
  shared foundations must be stabilized first, or when you need
  dispatch/gate/backlog rules for a staged rollout.

## Response Style

Keep user-facing updates brief and operational:

- what was assigned
- what was accepted or rejected
- what changed in the checklist
- which agent was closed or replaced
