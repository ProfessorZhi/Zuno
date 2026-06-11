# Phase 6 Bundle Ready Check

This note records the current readiness check for the standalone `Phase 6` bundled node.

## Ready Condition

The bundle is considered ready for real staging when all of the following are true:

1. `python tools/scripts/preview_phase6_bundle_scope.py --summary` reports the expected grouped counts
2. `python tools/scripts/preview_phase6_bundle_scope.py --dry-run` reports the same grouped counts and total path count
3. `python tools/scripts/verify_phase6_bundle_ready.py` passes
4. the recommended sequence still reflects the current branch reality:
   - review `docs_and_contract` first
   - confirm `logical_phase6_delta`
   - keep `eval_entrypoints` and `runtime_foundations` together on the current `main` base
   - keep `verification_tests` and `phase6_node_ops` attached to the same bundled node

## Single Command

```powershell
python tools/scripts/verify_phase6_bundle_ready.py
```

This branch currently expects the verifier to pass from the live worktree first. Commit-history fallback is only a secondary safety net after the current bundle has already been formed once.

## Current Expected Counts

- `docs_and_contract = 3`
- `logical_phase6_delta = 5`
- `eval_entrypoints = 4`
- `runtime_foundations = 6`
- `verification_tests = 19`
- `phase6_node_ops = 6`
- `total_changed = 43`
