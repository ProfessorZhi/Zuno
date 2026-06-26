# Phase 05: Storage Versioning

## Goal

Define versioning rules for GraphRAG project settings, indexing artifacts, and query behavior.

## Scope

Specs, ADRs, migration notes, and later bounded implementation work.

## Files to change

- `docs/history/specs/`
- `docs/architecture/decisions/`
- migration docs if storage behavior changes

## Files not to change

- database migrations without a dedicated implementation gate
- unrelated eval reports
- archived history except for pointers

## Acceptance gates

- Version keys are explicit.
- Reindex triggers are documented.
- Backward compatibility rules are stated.

## Verification commands

```powershell
python tools/scripts/verify_docs_entrypoints.py
git diff --check
```

## Evidence to return

- versioning spec or ADR
- compatibility notes
- verification summary
