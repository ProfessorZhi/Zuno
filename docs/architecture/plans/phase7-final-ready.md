# Phase 7 Final Ready Check

This note records the current readiness rule for the final `Phase 7` interview-facing cleanup node.

## Ready Condition

The node is considered ready when all of the following are true:

1. 最终面试讲解路径已经固定
2. 最终 smoke tests 已经通过
3. 最终 publish boundary 检查已经通过
4. `python tools/scripts/verify_phase7_readiness.py` 通过

## Single Command

```powershell
python tools/scripts/verify_phase7_readiness.py
```
