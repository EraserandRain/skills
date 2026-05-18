---
name: git-staged-commit-message
description:
  Review git staged changes for code-review findings and draft one English
  Conventional Commit message. Use when the user wants staged changes reviewed,
  wants a commit message based only on what is staged in the index, or asks to
  infer commit scope/type from recent git history.
---

# Git Staged Review And Commit Message

Inspect only staged changes.

- Read staged state with commands such as `git diff --cached --stat`,
  `git diff --cached`, and `git status --short`.
- Ignore unstaged changes completely. Use `git status --short` only to
  distinguish staged entries from unstaged ones.
- If both staged and unstaged edits exist in the same repository, base the
  answer only on the staged diff.
- Check recent history with `git log --oneline` to mirror the repository's
  existing commit style and scope naming.
- Review the staged diff first. Prioritize bugs, behavioral regressions, missing
  tests, and risks with file/line references.
- After the review findings, summarize the staged theme in a few words, then
  output exactly one commit message line in English.

Use Conventional Commits unless the repository history clearly uses a different
format.

- Prefer `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, or `test`.
- Reuse an existing scope when the staged files make it clear, such as
  `ai_tools` or `zsh`.
- Keep the subject concise, imperative, and lowercase except for proper nouns or
  fixed product names.
- Do not base findings or commit-message content on unstaged work, speculative
  follow-ups, or unrelated files.

If the staged diff mixes multiple concerns, choose the dominant user-facing or
structural change and produce the best single-line message for the staged set.
