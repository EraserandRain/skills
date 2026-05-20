# Drift Detection

Use this reference when code, examples, prompts, skills, or documentation changed and you need to decide what else may be stale.

## Drift Map

| Changed asset | Check for related updates |
| --- | --- |
| Public API, exported type, CLI flag | Reference docs, README snippets, examples, changelog |
| Configuration or environment variable | `.env.example`, config reference, deployment docs, AGENTS commands |
| Workflow/business behavior | Workflow docs, examples, tests, scheduler docs |
| Adapter or integration selector | Integration docs, replay tests, screenshots/traces policy |
| Prompt template | Prompt examples, evals, tests, expected output docs |
| Skill instructions | Skill examples, AGENTS routing, docs that describe the skill |
| Docs page added/moved/deleted | Docs navigation, redirects, internal links |
| Example code | README links, docs snippets, test coverage |

## Contract Levels

Use the lightest contract that catches the real risk.

1. Manual checklist: good for small repos and low-risk docs.
2. Manifest mapping: a YAML or JSON file maps code areas to docs/tests/examples.
3. CI guard: changed code without mapped docs produces a warning or failure.
4. Generated reference: source code or schemas generate reference docs.
5. Semantic duplicate scan: reports similar paragraphs as warnings only.

## Recommended CI Behavior

- Fail when generated docs are stale.
- Fail when docs navigation references missing pages.
- Fail when code examples in docs do not run and the project expects runnable examples.
- Warn when mapped docs did not change with related code.
- Warn for semantic duplication unless the project has tuned thresholds.

## Manifest Example

```yaml
areas:
  workflow-upload:
    code:
      - workflows/upload.workflow.ts
      - adapters/upload.adapter.ts
    docs:
      - docs/workflows/upload.md
    examples:
      - examples/upload.json
    tests:
      - tests/workflows/upload.spec.ts
```

When adding a manifest to a project, keep it small and scoped to areas where stale docs have already caused pain.
