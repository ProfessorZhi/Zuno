# Phase 04: Repository Layout Cleanup

## Goal

Align repository structure with target layout rules after active runtime
dependencies are removed.

## Dependency

Phase 01 through Phase 03 complete.

## Scope

- Move history to `docs/architecture/history/`.
- Keep executable Agent programs in `.agent/programs/`.
- Keep references as indexes, not duplicated target architecture prose.
- Remove or archive dead compatibility folders after grep proof.

## Files To Change

- `.agent/`
- `docs/architecture/history/`
- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_repo_hygiene.py`
- matching repository structure tests

## Files Not To Change

- Runtime code unless a move is already proven by prior phases.
- Generated or local data.
- Catch-all packages named only `services`, `core`, `utils`, `common`, or
  `helpers`.

## Acceptance Gates

- No duplicate active program front paths.
- No superseded execution plan remains in `.agent/programs/`.
- `docs/architecture/history/` is the only history archive.
- Verifiers protect target layout without treating Blocked Legacy as target.

## 2026-06-26 Safe Prework

Retired Domain Pack UI capture and responsive-check scripts were moved out of
active `tools/scripts/` and archived under:

- `docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/`

The move preserves old UI evidence while keeping active repository tools from
generating `docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1` or
mocking retired `/api/v1/domain-packs` and Domain Pack settings pages.

## Verification Commands

```powershell
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_repo_hygiene.py
pytest -q tests/test_repo_structure_consistency.py tests/test_repo_hygiene.py
git diff --check
```

## Evidence To Return

- move table
- verifier output
- final `git status --short`
