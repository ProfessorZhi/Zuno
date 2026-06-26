# Docs Maintenance Workflow

## Trigger

Use for `docs/`, `.agent/`, `AGENTS.md`, references, workflows, skills,
templates, or history changes.

## Steps

1. Read `AGENTS.md`.
2. Read `docs/architecture/current-architecture.md`,
   `docs/architecture/target-architecture.md`, and `docs/architecture/roadmap.md`.
3. Read `.agent/references/docs-map.md` and `.agent/references/code-map.md`.
4. Decide whether the change is Current, Target, Future, History, Agent-only,
   or Local.
5. Put formal conclusions in `docs/`.
6. Put Agent execution aids in `.agent/`.
7. Move superseded material to `docs/architecture/history/`; do not delete
   evidence value.
8. Update verification scripts and tests that protect the changed boundary.

## Verification

Run the smallest relevant subset:

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/test_docs_entrypoints.py tests/test_repo_structure_consistency.py
git diff --check
```
