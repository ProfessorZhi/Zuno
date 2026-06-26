# Phase 02: GraphRAG Project Settings

## Goal

Define how Zuno should represent official GraphRAG Project settings without mixing them with legacy local-only vocabulary.

## Scope

Architecture docs, specs, config design, and acceptance gates.

## Files to change

- `docs/history/specs/`
- `docs/architecture/decisions/`
- implementation files only in the later implementation task that this phase approves

## Files not to change

- unrelated UI surfaces
- unrelated eval datasets
- historical docs except for archival pointers

## Acceptance gates

- Project-level settings are named and scoped.
- Migration from local legacy terminology is documented.
- Existing runtime behavior is not claimed changed until code verifies it.

## Verification commands

```powershell
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/test_docs_entrypoints.py
```

## Evidence to return

- spec or ADR paths
- verified terminology decisions
- remaining implementation risks
