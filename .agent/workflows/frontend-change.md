# Frontend Change Workflow

## Trigger

Use for changes under `apps/web`.

## Required Reading

- `.agent/references/code-map.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
- `.agent/workflows/frontend-change.md`

## Steps

1. Confirm whether the change is visual, interaction, API contract, or internal.
2. For visual or layout changes, create an isolated preview under
   `.agent/local/previews/<task-id>/` and capture screenshots before changing
   production UI.
3. Wait for user confirmation before implementing visual prototypes in product
   pages.
4. If API fields change, sync backend DTOs, frontend types, and contract tests.
5. Do not expose internal route names, old GraphRAG names, or migration fields
   in user-facing UI.

## Verification

```powershell
npm run frontend:lint
npm run frontend:build
```
