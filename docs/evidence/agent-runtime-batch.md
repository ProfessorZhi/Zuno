# Agent Runtime Batch Evidence

## Scope

本证据覆盖 `ARCH-AGENT-001` 到 `ARCH-AGENT-080`。本批证明 Agent Core / Planning & Control 的 runtime batch 边界达到 `implementation_available`：Single Controller、Plan/ReAct/Reflection/Replan/Reflexion 分层、Runtime State 序列化恢复、Budget/Deadline、统一入口 Contract、Interrupt/Resume、Ref-only Graph State、RuntimeEvent/Trace、DAG、PlanVersion/GoalVersion、Step/Action/BranchResult、Effect UNKNOWN/Reconcile、Final Gate/Publication/RunOutcome、Failure/Budget/Recovery/ResultValidity/Outbox/Reconciler 和明确时间语义均可机器验证。它不代表 PHASE08 或全 Program 关闭。

## Implemented Runtime Surface

- `src/backend/zuno/agent/runtime_batch.py`
- `src/backend/zuno/agent/harness.py`
- `src/backend/zuno/agent/durable_runtime.py`
- `src/backend/zuno/agent/planning.py`
- `tools/scripts/verify_agent_runtime_batch.py`
- `tests/agent/test_agent_runtime_batch.py`

## Reproducible Commands

```powershell
python -m py_compile src/backend/zuno/agent/runtime_batch.py tools/scripts/verify_agent_runtime_batch.py
pytest -q tests/agent/test_agent_runtime_batch.py -p no:cacheprovider
python tools/scripts/verify_agent_runtime_batch.py
```

## Results

- `python -m py_compile ...` passed.
- `pytest -q tests/agent/test_agent_runtime_batch.py -p no:cacheprovider` passed: `5 passed`.
- `python tools/scripts/verify_agent_runtime_batch.py` passed: `80 requirements`, `10 runtime nodes`, `4 step runs`, `8 reconcilers`.

## Current Boundary

`validate_agent_runtime_batch()` builds an executable Agent Core fixture and runs the existing Single Controller harness plus durable interrupt/resume runtime. Negative tests prove cyclic Plan DAGs, UNKNOWN effect retry without reconcile, stale publication validity and naive deadline time all fail closed.
