# Phase 07: Tests Eval Closure

## Goal

Close the program with tests, evaluation evidence, and final documentation updates.

## Scope

Verification, eval reports, closure docs, and final index updates.

## Files to change

- `docs/history/audits/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
- tests and eval scripts that directly verify the completed program

## Files not to change

- unrelated runtime features
- unrelated frontend pages
- historical closure truth from Phase 0-6

## Acceptance gates

- Required tests pass.
- Eval evidence is linked from docs.
- `docs/architecture/README.md`, `current-architecture.md`, and `target-architecture.md` reflect closure.
- Remaining risks are explicit.

## Verification commands

```powershell
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/test_docs_entrypoints.py
git diff --check
```

## Evidence to return

- final test and eval summary
- closure report
- commit and push result

