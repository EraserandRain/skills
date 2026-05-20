# Agent Skills

Personal skills for Codex and Claude Code.

Each skill is a folder with a `SKILL.md` file, plus optional `references/` and
`agents/` files.

## Included

- `karpathy-guidelines` - simple guardrails for coding, debugging, and review.
- `markdown-linter-fixer` - fix Markdown lint issues with `markdownlint-cli2`.
- `review-staged-commit` - review staged changes and draft one commit message.
- `multi-agent-orchestration` - coordinate master/worker agent workflows.
- `docs-governance` - organize docs and prevent documentation drift.

## Install

Download the skill folder you want, then copy the whole folder into your agent's
skills directory.

For Codex:

```bash
mkdir -p ~/.codex/skills
cp -R path/to/skill-name ~/.codex/skills/
```

For Claude Code personal skills:

```bash
mkdir -p ~/.claude/skills
cp -R path/to/skill-name ~/.claude/skills/
```

For Claude Code project skills:

```bash
mkdir -p .claude/skills
cp -R path/to/skill-name .claude/skills/
```

Restart the agent session after installing.
