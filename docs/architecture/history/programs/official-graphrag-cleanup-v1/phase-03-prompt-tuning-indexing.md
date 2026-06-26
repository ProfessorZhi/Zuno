# Phase 03: Prompt Tuning And Indexing

## Goal

Define how Prompt Tuning affects indexing and retrieval behavior.

## Scope

Docs, specs, ADRs, and later bounded implementation work.

## Files to change

- `docs/architecture/specs/`
- `docs/architecture/audits/`
- bounded implementation files only after a separate implementation gate

## Files not to change

- unrelated runtime modules
- unrelated frontend views
- historical closure records

## Acceptance gates

- Prompt tuning inputs and outputs are defined.
- Index rebuild impact is documented.
- Evaluation evidence required for adoption is listed.

## Verification commands

```powershell
python tools/scripts/verify_docs_entrypoints.py
git diff --check
```

## Evidence to return

- changed specs or audits
- verification result
- unresolved design questions
