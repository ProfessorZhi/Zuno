# PHASE08 Durable Agent Runtime Persistence

status: active
previous_phase: PHASE07_production-parse-and-index-platform

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

## 需要先读取

- `src/backend/zuno/agent/durable_runtime.py`
- `src/backend/zuno/agent/harness.py`
- `src/backend/zuno/agent/runtime.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/capability/runtime.py`
- `.agent/references/runtime-call-chain.md`

## 需要修改的文件

- `src/backend/zuno/agent/**`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/capability/**` only for tool boundary integration
- `tests/agent/**`
- `tests/api/test_workspace_task_runtime.py`

## 执行拆解

1. 明确 LangGraph-compatible persistence 的接口，而不是把 LangGraph 当规划模块。
2. 实现或封装 durable checkpoint store：task_id、node_id、state snapshot、resume token。
3. 接入 approval wait/resume、cancel、failure snapshot。
4. 定义 exactly-once tool boundary：tool request id、approval id、execution id、result id。
5. 确保 GeneralAgent single loop 仍是当前 runtime 主线。

## 多 agent 分工

- Thread A：durable runtime store / checkpoint。
- Thread B：workspace task resume/cancel integration。
- Thread C：tool boundary ledger。
- Thread D：agent/runtime tests。
- 主线程：验证 task resume 和 post-turn commit 链路。

## 需要返回的证据

- checkpoint schema 或 store contract。
- resume / cancel / approval wait 测试。
- failure snapshot 示例。
- exactly-once tool boundary 证据。

## 停止条件

- 需要替换 GeneralAgent 主循环。
- 需要真实 LangGraph production checkpointer 但无法提供 local fallback。
- checkpoint 设计需要数据库 schema 破坏性变更。
