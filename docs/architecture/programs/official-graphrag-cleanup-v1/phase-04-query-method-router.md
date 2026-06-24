# Phase 04: Query Method Router

## Goal

Define the router that selects query methods for GraphRAG-aligned retrieval.

## Scope

Architecture contract, route semantics, tests, and evaluation criteria.

## Files to change

- `docs/architecture/specs/`
- `docs/architecture/audits/`
- route tests in a later implementation task

## Files not to change

- storage migrations unless a later phase explicitly approves them
- unrelated UI code
- archived plans

## Acceptance gates

- Query methods are named.
- Router inputs, outputs, and fallback behavior are documented.
- Evaluation metrics are tied to route behavior.

## Verification commands

```powershell
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/test_docs_entrypoints.py
```

## Evidence to return

- router contract path
- test or audit evidence
- fallback risks
