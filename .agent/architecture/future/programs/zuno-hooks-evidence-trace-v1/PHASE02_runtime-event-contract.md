# PHASE02：Runtime Event Contract
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

定义 `task_started`、`workspace_created`、`capability_selected`、`tool_call_started`、`evidence_ready`、`artifact_created`、`fallback_applied`、`task_cancelled`、`error`。

## 验收

事件字段包含 trace_id、session_id、task_id、capability_id、fallback_reason 和 timing。
