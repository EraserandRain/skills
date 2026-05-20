# Documentation Types

Use this reference when a repository has unclear document boundaries. It adapts Diataxis-style classification without requiring a strict folder layout.

## Four Core Types

| Type | Purpose | Common locations | Avoid |
| --- | --- | --- | --- |
| Tutorial | Teach through a complete learning path | `docs/tutorials/`, `learn/`, `examples/` | Exhaustive reference details |
| How-to | Solve a specific user goal | `docs/guides/`, `docs/how-to/`, `guides/` | Explaining every design alternative |
| Reference | Provide exact facts and syntax | `docs/reference/`, generated API docs, CLI help | Narrative onboarding |
| Explanation | Explain concepts, architecture, tradeoffs | `docs/concepts/`, `docs/design/`, `docs/architecture/` | Step-by-step task instructions |

## AI-Native Additions

| Type | Purpose | Common locations |
| --- | --- | --- |
| Agent rule | Tell coding agents how to work in this repo | `AGENTS.md`, `CLAUDE.md`, `.cursorrules` |
| Skill | Teach agents a reusable capability | User-level `~/.codex/skills`, project `.agents/skills/`, or project `skills/` |
| Prompt template | Version a prompt used by product code, tests, or workflows | `prompts/`, workflow config, eval fixtures |
| Eval or example | Demonstrate expected behavior and catch regressions | `examples/`, `evals/`, `tests/`, notebooks |
| Docs navigation config | Define information architecture for a docs site | `docs.json`, `mint.json`, `mkdocs.yml`, sidebars |

## Placement Examples

- "How do I run the scheduler locally?" is a how-to.
- "What environment variables exist?" is reference.
- "Why did we choose Playwright over Selenium?" is a design note or decision record.
- "When editing workflow files, run `pnpm typecheck`" is an Agent rule if intended for agents, or contributing docs if intended for humans.
- "A reusable prompt used by a production workflow" is a project prompt asset.
- "A private personal prompt for a one-off interaction" is not a project document.

## Practical Rule

Do not create a new category folder just because the taxonomy has a name. Use the taxonomy to classify the content, then place it in the closest existing project convention.
