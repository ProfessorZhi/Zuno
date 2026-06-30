# PHASE06 durable-single-controller-runtime

status: completed

## 目标

在 `agent/harness.py` 的节点定义之上，实现 durable checkpoint、resume、interrupt、approval wait、cancel 和 replan，让 Single Controller runtime 成为真实长任务状态机。

## 范围

- 将 task lifecycle 与 runtime state 绑定。
- 实现 checkpoint persistence adapter 和 resume path。
- 让 approval-required interrupt 能暂停并恢复执行。

## 禁止范围

- 不把 harness contract 当作 durable runtime。
- 不把产品 runtime 改成默认多 Agent。
- 不绕开 task/session/event trace。

## 验收闸门

- focused tests 能启动任务、写 checkpoint、模拟中断、恢复并继续输出 event。
- RuntimeTurnLedger、trace id、task id 在 resume 前后保持一致。
- recoverable failure 与 non-recoverable failure 可区分。

## 完成证据

- `src/backend/zuno/agent/durable_runtime.py` 新增 PHASE06 durable runtime owner surface。
- `SingleControllerDurableRuntime` 支持 start_task、checkpoint、approval interrupt、resume、cancel、recoverable / non-recoverable failure 和 store snapshot。
- `WorkspaceTaskRuntimeService` 已把 task_id、session_id/thread_id、trace_id、approval、cancel 和 runtime snapshot 接到 durable runtime。
- `/api/v1/workspace/task/{task_id}/cancel` 与前端 `cancelWorkspaceTaskAPI` 已补齐。
- `tests/agent/test_single_controller_durable_runtime.py` 证明 checkpoint / resume / cancel / failure 和新 runtime 实例复用同一 store。
- `tests/api/test_workspace_task_runtime.py` 证明 workspace approval resume、cancel 和 SSE trace 回放。

## Current / Target 边界

Current 是 controller-node 级 in-process durable runtime surface；不是生产 LangGraph checkpointer，不是进程重启后的持久恢复，不保证 exactly-once tool execution，也不把产品 runtime 改成默认多 Agent。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_single_controller_runtime_harness.py tests/agent -p no:cacheprovider
```
