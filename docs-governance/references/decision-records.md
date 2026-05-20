# Decision Records

Use this reference when deciding whether to create or update an ADR, RFC, or decision note.

## When to Create One

Create a decision record only for durable choices that future maintainers or agents are likely to question again:

- Choosing one framework, runtime, storage model, or automation layer over another.
- Defining a repository-wide documentation, testing, release, or security policy.
- Accepting a known tradeoff or limitation.
- Changing a public architecture boundary.
- Rejecting an obvious alternative that future contributors may re-propose.

Do not create one for routine implementation details, temporary bugs, small refactors, or decisions already obvious from code.

## Naming

Follow the project's existing convention if present:

- `docs/adr/0001-title.md`
- `docs/decisions/0001-title.md`
- `rfcs/0001-title.md`
- `docs/design/title.md`

If no convention exists, prefer `docs/decisions/` or `docs/design/` over forcing `docs/adr/`.

## Minimal Template

```md
# Title

## Status

Proposed | Accepted | Superseded

## Context

What problem or pressure led to this decision?

## Decision

What did we decide?

## Consequences

What improves, what gets harder, and what must future changes preserve?

## Alternatives Considered

What did we reject, and why?
```

## Agent Guidance

- Link to a decision record instead of copying its rationale into README or AGENTS.
- Update a decision record when the decision changes; do not silently contradict it elsewhere.
- If a decision record is superseded, mark its status and link to the newer record.
