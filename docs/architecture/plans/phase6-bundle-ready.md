# Phase 6 Bundle Ready Check

This note records the current operational readiness check for the standalone `Phase 6` bundled node.

## Ready Condition

The bundle is considered ready for real staging when all of the following are true:

1. `python tools/scripts/preview_phase6_bundle_scope.py --summary` reports the expected grouped counts
2. `python tools/scripts/preview_phase6_bundle_scope.py --dry-run` reports the same grouped counts and total path count
3. `python tools/scripts/verify_phase6_bundle_ready.py` passes
4. the recommended sequence still reflects the current branch reality:
   - review `docs_and_contract` first
   - confirm `logical_phase6_delta`
   - if the branch base lacks earlier foundations, keep `eval_entrypoints` and `runtime_foundations` together
   - keep `verification_tests` attached to the same bundled node

## Single Command

```powershell
python tools/scripts/verify_phase6_bundle_ready.py
```

If the local `Phase 6` node has already been committed, the verifier is allowed to fall back from the current worktree preview to either:

- the `HEAD` commit snapshot when the standalone node is still one commit
- the latest two-commit local Phase 6 chain when the node has already been followed by a small readiness-sync commit

## Current Expected Counts

- `docs_and_contract = 3`
- `logical_phase6_delta = 5`
- `eval_entrypoints = 4`
- `runtime_foundations = 22`
- `verification_tests = 20`
- `phase6_node_ops = 6`
- `total_changed = 60`
