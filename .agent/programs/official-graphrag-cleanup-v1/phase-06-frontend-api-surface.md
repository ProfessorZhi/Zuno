# Phase 06: Frontend API Surface

## Goal

Align frontend and API surfaces with the official GraphRAG cleanup model.

## Scope

API contracts, UI-facing terminology, and integration tests after the docs gate.

## Files to change

- `docs/architecture/specs/`
- API contract docs
- frontend/API code only in a later bounded implementation task

## Files not to change

- unrelated backend internals
- unrelated desktop shell behavior
- archived program files

## Acceptance gates

- UI-facing terms match the target architecture.
- API payload boundaries are documented.
- Any implementation work has tests and rollback notes.

## Verification commands

```powershell
python tools/scripts/verify_docs_entrypoints.py
npm --prefix apps/web run build
```

## Evidence to return

- contract docs
- UI/API verification output
- remaining compatibility risk
