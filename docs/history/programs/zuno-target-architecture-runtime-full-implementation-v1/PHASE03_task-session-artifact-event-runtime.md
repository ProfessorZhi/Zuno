# PHASE03 task-session-artifact-event-runtime

status: completed

## 目标

实现 workspace / session / file / ingest / task / approve / artifact / feedback 的后端稳定 API 与 SSE runtime surface，并让同一个 task 串起 `trace_id`、`session_id`、`task_id`、`artifact_id` 和 `feedback_id`。

## 范围

- 补齐 task lifecycle API 和 DTO。
- 优先实现 SSE 事件流，事件至少覆盖 planning、retrieval、answer、artifact_created、eval_diagnostic 和 failure。
- 对齐前端 `apps/web/src/apis/workspace.ts` 的类型与实际 API。

## 禁止范围

- 不只新增 type 而无真实 route。
- 不把 simple chat 当作完整 task runtime。
- 不改成多 Agent 产品 runtime。

## 验收闸门

- API test 能创建 session、上传或引用文件、创建 task、读取 events、读取 artifact、提交 feedback。
- 同一 task 的 trace id 在 API response、runtime event 和 eval payload 中一致。
- README / architecture 只把真实跑通的 API 写成 Current。

## 完成证据

- 新增 `src/backend/zuno/api/services/workspace_task_runtime.py`，提供 in-process task runtime surface，覆盖 file registration、ingest job acceptance、task create、manual approval wait / resume / reject、event list、SSE stream、artifact read 和 feedback。
- 新增 / 对齐 `src/backend/zuno/api/v1/workspace.py` routes：`POST /workspace/file`、`POST /workspace/ingest`、`POST /workspace/task`、`GET /workspace/task/{task_id}`、`GET /workspace/task/{task_id}/events`、`GET /workspace/task/{task_id}/events/stream`、`POST /workspace/task/{task_id}/approve`、`GET /workspace/artifact/{artifact_id}`、`POST /workspace/feedback`。
- `apps/web/src/apis/workspace.ts` 已暴露对应类型和 API helpers。
- `tests/api/test_workspace_task_runtime.py` 覆盖 session -> file -> ingest -> manual approval -> artifact -> feedback，并覆盖 rejected approval 的 `failure` event。
- `tests/frontend/test_workspace_product_loop_types.py` 固定前端 API surface。

## 验证命令

```powershell
git diff --check
pytest -q tests/api tests/frontend -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```
