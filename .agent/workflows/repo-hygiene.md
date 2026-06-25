# Repository Hygiene Workflow

## Trigger

Use for directory moves, deletion, ignore rules, generated outputs, local data,
and structure verification.

## Steps

1. Run `git status --short` and `git status --short --ignored`.
2. Classify suspicious paths as Current, Target, Future, History, Generated,
   Local, Dead, or Blocked.
3. Preserve Current and Blocked paths.
4. Move History into `docs/architecture/history/`.
5. Move Agent execution material into `.agent/`.
6. Add Generated or Local outputs to `.gitignore` or `.dockerignore`; do not
   commit them.
7. Delete only Dead files with no references and no evidence value.
8. Update `tools/scripts/verify_repo_structure.py` and matching tests.

## Stop Conditions

- Active imports, routes, scripts, or tests still reference a deletion target.
- Runtime logic changes would be required.
- The path may contain local user data.

## Verification

```powershell
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_repo_hygiene.py
pytest -q tests/test_repo_structure_consistency.py
git diff --check
```
