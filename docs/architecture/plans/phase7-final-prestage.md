# Phase 7 Final Prestage Checklist

Use this note immediately before staging the standalone `Phase 7` final interview-facing cleanup node.

## Intended Scope

This prestage flow is only for the final `Phase 7` cleanup surface:

- final public README / docs / architecture wording
- final interview reading path
- final smoke / publish-boundary / structure verification entry

## Prestage Commands

Run these in order:

```powershell
python tools/scripts/verify_phase7_readiness.py
git diff -- README.md docs/architecture/README.md docs/architecture/plans/
git status --short README.md docs/architecture/README.md docs/architecture/plans/ tools/scripts/verify_phase7_readiness.py tests/test_publish_boundary.py
```

## What To Confirm

Before treating this as the real `Phase 7` node, confirm:

1. 最终面试讲解路径已经固定
2. 公开 README / architecture / current-phase-audit 口径一致
3. `python tools/scripts/verify_phase7_readiness.py` 通过
4. 最终 smoke tests、最终 publish boundary 检查、结构检查已经由统一入口串起来
