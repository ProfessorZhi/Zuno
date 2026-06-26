# Phase 0: Program Documentation

## Goal

Create the formal documentation surface for the new independent program without changing runtime code.

## Why This Phase Exists

The previous architecture round is already closed.

This new round should not be mixed into the completed `Phase 0-6` closure truth.

So this phase creates a new program root, new specs, and new workflow rules first.

## Must Produce

1. the new program root under `docs/architecture/programs/`
2. `Phase 0-5` program files
3. stable specs for product boundary, runtime routing, Domain Pack Builder, and config impact
4. minimal links from the main architecture entrypoints
5. project-level workflow rules that preserve earlier closure truth

## Must Not Change

1. `src/backend/zuno/`
2. `apps/web/`
3. `apps/desktop/`
4. runtime code, retrieval logic, or API behavior
5. the completed closure truth wording of the earlier architecture phase set

## Closure Gate

Phase 0 is complete only when:

1. the new program directory exists
2. the new program `README.md` clearly explains its relation to the earlier completed phase set
3. `phase-00` through `phase-05` documents exist
4. the new stable specs exist
5. `docs/architecture/phases/README.md` only adds a pointer to the new program
6. project-level workflow guidance is updated
7. no runtime code changed

## Verification

Run:

```powershell
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/test_docs_entrypoints.py
git diff -- docs/architecture agent.md
```

Expected:

1. docs entrypoint checks stay green
2. only documentation and workflow files changed
