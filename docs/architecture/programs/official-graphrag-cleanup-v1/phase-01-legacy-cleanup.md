# Phase 01: Legacy Cleanup

## Goal

Remove or archive stale front-path references that make old architecture routes look current.

## Scope

Docs, tests that verify doc entrypoints, and workflow references.

## Files to change

- `docs/architecture/`
- `.agent/references/`
- doc entrypoint tests if they exist

## Files not to change

- runtime backend code
- frontend product code
- infrastructure runtime files

## Acceptance gates

- Legacy service-migration and superseded program references are marked historical.
- Current entrypoints do not point to archived programs as active work.
- No long-term duplicate Agent entrypoints exist.

## Verification commands

```powershell
git grep -n "<legacy lowercase Agent entrypoint filename>"
git grep -n "knowledge-product-refactor-deep-graphrag-v1"
python tools/scripts/verify_docs_entrypoints.py
```

## Evidence to return

- grep hits classified as current, historical, migration-note, or fixed
- docs entrypoint verification result
