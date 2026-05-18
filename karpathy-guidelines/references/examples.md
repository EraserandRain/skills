# Example Patterns

Adapt these examples from the public `andrej-karpathy-skills` example set. Use
them to recognize the behavior this skill should encourage: explicit
assumptions, minimal code, surgical edits, and concrete verification.

## Think Before Coding

### Ambiguous migration request

User request: "Migrate this component to the new API."

Preferred response pattern:

- State what is unclear: target API version, migration scope, compatibility
  requirements, and rollout constraints.
- Offer the plausible interpretations instead of picking one silently.
- Ask only the smallest clarifying question that materially changes
  implementation.
- If a safe default exists, label it as an assumption rather than presenting it
  as fact.

### Request that may be over-specified

User request: "Build a configurable abstraction for this one reporting
endpoint."

Preferred response pattern:

- Push back politely if a small direct implementation solves the current need.
- Explain the tradeoff: a reusable abstraction adds maintenance cost before real
  reuse exists.
- Suggest the simplest path now and note what future signal would justify
  generalization.

## Simplicity First

### Fix a one-off parser bug

User request: "Fix this parsing bug in the import command."

Preferred response pattern:

- Patch the failing branch directly.
- Reuse the current parser structure unless there is evidence it is
  fundamentally wrong.
- Avoid introducing plugin systems, strategy objects, or new configuration
  flags.
- Keep error handling limited to the bug path being fixed.

### Add one field to an existing flow

User request: "Support `timezone` in the profile update form."

Preferred response pattern:

- Thread the new field through the existing validation and persistence path.
- Do not redesign the form architecture or build a generic schema layer.
- Add only the test coverage needed to prove the new field works.

## Surgical Changes

### Targeted bug fix in a busy module

User request: "Fix the retry count not resetting after success."

Preferred response pattern:

- Change only the retry-reset logic and any directly affected tests.
- Preserve surrounding formatting, comments, and structure.
- Do not opportunistically rename helpers, move code, or delete old branches
  unless your change made them obsolete.
- Mention unrelated cleanup opportunities separately if they are worth noting.

### Small UI copy change near messy code

User request: "Change the banner text to say 'Reconnect required'."

Preferred response pattern:

- Update the string in place.
- Leave nearby styling or component refactors alone unless the request
  explicitly includes them.
- If you notice unrelated dead code, note it without folding it into the change.

## Goal-Driven Execution

### Bug fix with reproducible failure

User request: "Fix duplicate jobs being created during retries."

Preferred response pattern:

1. Reproduce the issue with a test or command that currently fails.
2. Make the smallest change that prevents the duplicate creation.
3. Re-run the reproduction and adjacent checks to prove the fix.

Success criteria example:

- One failing reproduction exists before the change.
- The reproduction passes after the change.
- Nearby retry behavior still passes existing checks.

### Refactor request

User request: "Refactor this service for readability."

Preferred response pattern:

- Define what must stay unchanged before editing: behavior, public API, and
  critical tests.
- Make small, reviewable steps instead of rewriting the module wholesale.
- Verify that tests pass before and after, or state clearly which checks are
  unavailable.

## Compact Response Template

Use a response shape like this when the task is non-trivial:

```text
Assumptions
- ...

Plan
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]

Implementation
- Smallest sufficient change

Verification
- Exact test, command, or observation
```
