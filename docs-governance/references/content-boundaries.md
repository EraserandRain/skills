# Content Boundaries

Use this reference when deciding where content belongs or when reviewing a documentation change for duplication.

## Default Ownership

| Information | Preferred owner | Link from |
| --- | --- | --- |
| Project overview, install, quickstart | `README.md` | Package pages, docs home |
| Developer setup and contribution process | `CONTRIBUTING.md`, docs contributing page | README, AGENTS |
| Agent-specific runtime rules | `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.agents/` | README only if users need to discover them |
| Product/user docs | Existing docs system: `docs/`, `src/`, `guides/`, docs site | README |
| Tutorials and how-to guides | Existing docs guide/tutorial area | README, docs nav |
| API/CLI/config reference | Generated reference or `docs/reference/` | Guides and examples |
| Runnable examples | `examples/`, `cookbook/`, `notebooks/`, or existing sample area | README, docs pages |
| Design explanation | `docs/design/`, `docs/architecture/`, or existing design area | Relevant docs |
| Decisions and tradeoffs | Existing `adr/`, `decisions/`, `rfcs/`, or `docs/design/` | Design docs and PRs |
| Prompt templates | `prompts/` only when project-owned and versioned | Agent docs or workflow docs |
| Skills | `.agents/skills/` or `skills/` only when project-owned and versioned | AGENTS, README if public |

## SSOT Rules

- One source owns each fact. Other files summarize and link.
- Avoid copying command lists between README and AGENTS. Put user-facing commands in README or docs; put Agent-specific command constraints in AGENTS.
- Avoid copying full skill instructions into AGENTS. AGENTS should route to a skill by name or path.
- Avoid duplicating architecture rationale across README, docs, and comments. Put rationale in a design note or decision record, then link.
- Avoid putting business/domain documentation inside a skill unless the skill needs it to execute a task. Put large domain knowledge in docs or skill references, not both.

## Review Heuristics

Ask these questions before editing:

1. Who is the reader: new user, contributor, maintainer, coding agent, or runtime system?
2. Is this authoritative content or navigation to authoritative content?
3. Will this content become stale when code changes?
4. Is there already a page or generated source that owns this fact?
5. Does adding this file require updating docs navigation, sidebar, registry, or index metadata?

If the answer is unclear, prefer the existing project pattern over a generic structure.
