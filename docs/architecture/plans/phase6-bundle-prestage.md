# Phase 6 Bundle Prestage Checklist

Use this note immediately before staging the standalone `Phase 6` bundle node from the current clean `main`-based branch.

## Intended Scope

This prestage flow is only for the current real `Phase 6` bundled node:

- `docs_and_contract`
- `logical_phase6_delta`
- `eval_entrypoints`
- `runtime_foundations`
- `verification_tests`
- `phase6_node_ops`

This note does **not** assume a separate local "foundation node" has already been merged. On the current `main` base, the broader bundle is the honest contract.

## Expected Group Counts

Before staging, the grouped preview should resolve to:

- `docs_and_contract = 3`
- `logical_phase6_delta = 5`
- `eval_entrypoints = 4`
- `runtime_foundations = 6`
- `verification_tests = 19`
- `phase6_node_ops = 6`
- `total_changed = 43`

## Prestage Commands

Run these in order:

```powershell
python tools/scripts/preview_phase6_bundle_scope.py --groups
python tools/scripts/preview_phase6_bundle_scope.py --summary
python tools/scripts/preview_phase6_bundle_scope.py --dry-run
python tools/scripts/verify_phase6_bundle_ready.py
python tools/scripts/preview_phase6_bundle_scope.py --stage-command
git diff --cached --stat
```

If the preview still looks right, the canonical stage set is the one printed by:

```powershell
python tools/scripts/preview_phase6_bundle_scope.py --stage-command
```

## What To Confirm

Before treating the bundle as a real `Phase 6` node, confirm:

1. `preview_phase6_bundle_scope.py --summary` reports the expected grouped counts
2. `preview_phase6_bundle_scope.py --dry-run` reports the same grouped counts and total path count
3. `verify_phase6_bundle_ready.py` passes in `worktree` mode
4. the docs claim and the code/test bundle still move together as one node
5. the local operation docs/scripts/tests stay attached too, so the staging contract can be rerun later without guesswork

## If The Cached Diff Looks Wrong

Do not move to `Phase 7` yet.

Instead:

```powershell
git diff --cached --stat
python tools/scripts/preview_phase6_bundle_scope.py --summary
python tools/scripts/preview_phase6_bundle_scope.py --dry-run
git diff --cached -- docs/architecture/plans/current-phase-audit.md docs/architecture/plans/zuno-refactor-execution-plan.md src/backend/agentchat/evals/rag_eval/README.md
```

Then compare the cached diff against the grouped dry-run output before restaging.
