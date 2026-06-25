# Repository Hygiene Workflow

## Trigger

Use for directory moves, deletion, ignore rules, generated outputs, local data,
and structure verification.

## Steps

1. Run `git status --short` and `git status --short --ignored`.
2. Read `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
   before target layout or directory-boundary work.
3. Classify suspicious paths as Current, Target, Future, History, Generated,
   Local, Dead, or Blocked.
4. Preserve Current and Blocked paths.
5. Move History into `docs/architecture/history/`.
6. Move Agent execution material into `.agent/`.
7. Add Generated or Local outputs to `.gitignore` or `.dockerignore`; do not
   commit them.
8. Delete only Dead files with no references and no evidence value.
9. Update `tools/scripts/verify_repo_structure.py` and matching tests.

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
