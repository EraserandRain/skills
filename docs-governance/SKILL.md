---
name: docs-governance
description: Govern repository documentation so README files, agent instructions, docs sites, examples, prompts, skills, and design notes stay organized, deduplicated, and synchronized with code. Use when adding, editing, reorganizing, or reviewing documentation; changing code that may require docs updates; updating AGENTS/CLAUDE/Cursor rules; creating examples; checking docs drift; or deciding where information belongs.
---

# Docs Governance

Use this skill to make documentation changes that fit the repository already in front of you. Do not impose a universal directory layout. First discover the project's existing documentation system, then apply SSOT, content boundaries, and drift checks.

## Workflow

1. Discover the local documentation system before editing:
   - Inspect root files such as `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `mkdocs.yml`, `docs.json`, `mint.json`, `docusaurus.config.*`, and `package.json`.
   - Inspect documentation-like folders such as `docs/`, `examples/`, `articles/`, `guides/`, `rfcs/`, `decisions/`, `adr/`, `.agents/skills/`, `skills/`, and `prompts/`.
   - Run `scripts/docs_governance_scan.py <repo>` when a quick map of docs assets would help.

2. Classify the information before deciding where it belongs:
   - Entry point: install, quickstart, project overview.
   - Agent rule: commands, constraints, repo-specific runtime instructions for coding agents.
   - Human guide: tutorials, how-to steps, troubleshooting.
   - Reference: APIs, CLI, config, schemas, generated material.
   - Example: runnable sample or cookbook-style use case.
   - Design note: architecture, system shape, tradeoffs.
   - Decision record: durable decision, rejected alternatives, consequences.
   - Prompt or skill asset: only if the project already treats prompts or skills as versioned project assets.

3. Preserve a single source of truth:
   - Put authoritative content in one place and link to it elsewhere.
   - Do not copy long rules between README, AGENTS, docs pages, prompts, and skills.
   - If duplication already exists, prefer reducing it while preserving user-facing navigation.

4. Respect project conventions:
   - If the repo has a docs navigation file, update it when adding, moving, or deleting pages.
   - If the repo has generated docs output, do not edit generated output directly.
   - If the repo has prose lint, link checks, docs tests, or example tests, run the narrow relevant command.

5. Check drift risk:
   - Code behavior changed: docs, examples, tests, and agent rules may need updates.
   - Public API or config changed: reference docs and examples may need updates.
   - Workflow or CLI changed: README, how-to docs, and scheduler/runbook docs may need updates.
   - Prompt or skill changed: examples and tests may need updates.

## Decision Rules

- Keep README short: overview, install, quickstart, links, and essential status.
- Keep AGENTS/CLAUDE/Cursor rules operational: commands, constraints, project map, and Agent-specific gotchas.
- Put durable human explanation under the existing docs system.
- Put runnable examples under the existing examples or cookbook system.
- Add decision records only when the project already has `adr/`, `decisions/`, `rfcs/`, or when a decision is long-lived and likely to be re-litigated.
- Add project-local skills or prompts only when the repository already version-controls them or the user explicitly asks for project-owned AI assets.
- Prefer warnings over hard failures for semantic duplicate detection. Similar wording can be legitimate across overview and reference docs.

## References

- For placement rules, read `references/content-boundaries.md`.
- For common documentation types and Diataxis-style classification, read `references/doc-types.md`.
- For drift checks and CI contract ideas, read `references/drift-detection.md`.
- For ADR/RFC/decision-record guidance, read `references/decision-records.md`.

Load only the reference needed for the current task.
