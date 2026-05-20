---
name: review-staged-commit
description: Review Git staged changes only, report code-review findings, and draft one commit message line that matches the repository's local history. Use when the user asks to review staged changes, inspect the index before commit, or write a commit message from staged work. Ignore unstaged changes unless the user explicitly asks for them.
---

# Review Staged Changes

1. Inspect the index only.
   - Use `git diff --cached --stat`, `git diff --cached --name-only`, and `git diff --cached`.
   - Use `git status --short` only to tell staged and unstaged files apart. Do not review unstaged hunks.
2. Review with a code-review mindset.
   - Present findings first, ordered by severity.
   - Focus on bugs, regressions, missing tests, accidental files, and blast radius.
   - If there are no findings, say so and mention residual risks or validation gaps.
3. Draft one commit message.
   - Read recent history with `git log --oneline -n 20`.
   - Use Conventional Commits unless the repository history clearly follows another format.
   - Reuse an existing local scope only when the staged files and recent history make it clear.
   - Omit the scope when no local scope fits naturally.
   - Keep it to one line.
   - Prefer `fix` for behavior corrections, `feat` for new user-visible behavior, `refactor` only when behavior is unchanged, `perf` only for measurable runtime wins, `docs` for documentation-only changes, `test` for test-only changes, and `chore` for housekeeping.
4. Watch for mixed commits.
   - If the staged set mixes multiple concerns, call that out in the review.
   - Still provide one best-fit commit message for the current staged set unless the user asks to split commits.
5. Check documentation drift lightly.
   - Stay staged-only.
   - If staged changes affect CLI commands, configuration, public APIs, user-visible behavior, logging/output format, operational workflows, setup steps, or documented conventions, check whether staged docs/examples/tests were updated.
   - If docs may be missing, report it as a finding or residual risk.
   - Do not run a full documentation-governance workflow unless the user explicitly asks for documentation review.
6. Format the final output.
   - State clearly that the review is based on staged changes only.
   - Keep the commit message separate from the findings.
   - End with exactly one proposed commit message wrapped in backticks.
