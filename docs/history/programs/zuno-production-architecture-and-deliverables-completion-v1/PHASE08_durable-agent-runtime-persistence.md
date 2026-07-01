# PHASE08 Durable Agent Runtime Persistence

status: completed
previous_phase: PHASE07_production-parse-and-index-platform
completed_at: 2026-07-01
next_phase: PHASE09_memory-context-production-governance

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

## 完成证据

- Durable store contract：`InMemoryDurableRuntimeStore.to_persistence_payload()` 和 `from_persistence_payload()` 支持 JSON round-trip，保存 task record、checkpoint、pending interrupt、failure 和 runtime events；新 runtime instance 可从恢复后的 store 继续 `resume_task()`。
- Checkpoint / resume：focused test 在 `act_react_loop` 产生 approval interrupt，模拟进程重启后恢复 store，再从 checkpoint 完成到 `post_turn_commit`。
- Failure snapshot：workspace output security block 会把 durable runtime snapshot 标记为 `failed`，failure payload 绑定 `task_id`、`trace_id`、`workspace_id`、recoverable 标记、source refs、artifact ids 和 release eval status。
- Exactly-once tool boundary：`ToolRuntimeRequest` / task events 暴露 `tool_request_id`、`approval_id`、`tool_execution_id` 和 `tool_result_id`；approval 前后的 request / approval id 保持一致，实际执行结果只有一个 execution id。
- GeneralAgent single loop 未替换；LangGraph 仍只是 production-compatible persistence target，不是当前 planner。

## 验证结果

```powershell
pytest -q tests/agent/test_agent_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/api/test_workspace_task_runtime.py -p no:cacheprovider
# baseline before implementation: 19 passed, 1 warning
# RED before implementation: 3 failed, 17 passed, 1 warning
# GREEN after implementation: 20 passed, 1 warning

python tools/agent/render_architecture.py --check
git diff --check
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_docs_entrypoints.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-docs.ps1
# passed
```

## Remaining Target

- 真实生产 LangGraph checkpointer / DB-backed distributed recovery 仍是 Target；本 phase 只证明 local JSON persistence payload 和 restart/resume contract。
- exactly-once 目前是 task/tool boundary id 和单进程事件去重证据，不是跨 worker 分布式事务。
- production Desktop 进程级恢复和外部发布 replay gate 仍留给后续 phase / release closure。

## 停止条件

- 需要替换 GeneralAgent 主循环。
- 需要真实 LangGraph production checkpointer 但无法提供 local fallback。
- checkpoint 设计需要数据库 schema 破坏性变更。
