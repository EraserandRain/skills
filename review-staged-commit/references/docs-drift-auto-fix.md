# Docs Drift Auto-Fix

Use this reference only when docs/example drift auto-fix is enabled and the
staged review found drift.

## Workflow

1. Complete staged-only inspection first.
2. Identify drift against the staged code, config, public contract, CLI
   behavior, examples, or output shape.
3. Load and follow `docs-governance` placement and ownership rules before editing.
4. Fix only documentation, examples, or docs-contract tests needed to align with
   the staged public contract.
5. Do not change production code unless the user explicitly asks.
6. Do not run `git add`, `git commit`, `git restore --staged`, `git reset`, or
   any other index/history mutation.
7. If editing a file that is already staged, leave the new edits unstaged and
   report that the file now has unstaged changes on top of staged content.
8. Run narrow relevant validation when available.
9. Report the original finding, files edited, validation run, and exact
   `git add ...` command the user can run.

## Common Drift Checks

- Staged config points to a docs/example/input path that is missing from the
  index.
- Staged workflow input schema fields differ from documented example fields.
- Staged summary/output fields differ from documented output fields.
- Staged CLI/config behavior changes are missing from the owning docs page.
- Staged docs duplicate a catalog, command list, or config table that has a
  clearer source of truth elsewhere.
