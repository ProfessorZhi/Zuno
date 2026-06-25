# Phase 02: Contract Review Asset Migration

## Goal

Preserve useful Contract Review assets while removing Domain Pack as the active
runtime container.

## Dependency

Phase 01 complete or a narrower asset-only gate approved by the user.

## Scope

- Classify `domain-packs/contract_review` assets as Current, Target, History,
  Eval Fixture, Generated, or Dead.
- Move reusable prompt/schema/eval assets to GraphRAG Project or eval fixture
  destinations.
- Archive superseded Domain Pack documentation under `docs/architecture/history/`.

## Files To Change

- `domain-packs/`
- `tools/evals/zuno/`
- `docs/architecture/history/`
- `.agent/references/`
- tests covering asset resolution

## Files Not To Change

- Runtime behavior before replacement tests exist.
- Database schema.
- Docker topology unless Phase 01 already removed active references.

## Acceptance Gates

- Contract Review evidence is not lost.
- Runtime no longer needs `DomainPackLoader` for Contract Review.
- History paths preserve old Domain Pack evidence.
- Eval fixtures use target names where possible.

## Verification Commands

```powershell
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/test_repo_hygiene.py tests/test_repo_structure_consistency.py
git grep -n "contract_review"
git diff --check
```

## Evidence To Return

- asset migration table
- archived paths
- runtime dependency proof
