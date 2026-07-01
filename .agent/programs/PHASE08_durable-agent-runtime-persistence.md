# PHASE08 Durable Agent Runtime Persistence

status: pending

## 目标

把 Agent Runtime 推进到生产级 durable persistence：LangGraph-compatible persistence、进程重启恢复、approval wait/resume、cancel 和 exactly-once tool boundary。

## 范围

- `src/backend/zuno/agent/durable_runtime.py` 和 workspace task runtime。
- checkpoint、interrupt、resume、cancel、failure snapshot。
- tool boundary ledger 和 post-turn commit。

## 禁止范围

- 不把 LangGraph 作为规划模块本身。
- 不改成多 Agent runtime 主线。
- 不绕过现有 GeneralAgent single loop 集成点。

## 验收闸门

- durable state 可持久化并可恢复。
- approval wait/resume 和 cancel 有 tests。
- failure snapshot 能和 trace / task / artifact 关联。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_agent_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/api/test_workspace_task_runtime.py -p no:cacheprovider
```
