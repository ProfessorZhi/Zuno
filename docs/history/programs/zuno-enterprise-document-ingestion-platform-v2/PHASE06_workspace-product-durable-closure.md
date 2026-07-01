# PHASE06 Workspace Product Durable Closure

status: completed
program: zuno-enterprise-document-ingestion-platform-v2
phase: PHASE06_workspace-product-durable-closure
mode: tdd-implementation

## 目标

让 workspace task、task events、artifact metadata、artifact content/ref 和 feedback 进入 local durable store，artifact download 不再只能依赖 `_artifact_content` 内存。

## 范围

- Workspace task / event / artifact / feedback SQLite tables。
- `WorkspaceTaskRuntimeService.get_task_snapshot()` 和 `record_feedback()` 的 durable persistence。
- rehydrate 后的 task snapshot、events、artifact content 和 feedback ids。

## 禁止范围

- 不接生产 trace DB。
- 不改 public API response shape。
- 不把 `SingleControllerDurableRuntime` 的完整生产 DB persistence 写成 Current。

## 验收闸门

- completed task 可 fresh store rehydrate。
- events 可通过 `/task/{task_id}/events` 查询。
- artifact content 可通过 `/artifact/{artifact_id}` 查询。
- feedback ids 可在 task snapshot 中恢复。

## 验证命令

```powershell
pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_restart_rehydrates_cited_artifact_and_feedback -p no:cacheprovider
pytest -q tests/api -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/api/dto/workspace.py`

## 需要修改的文件

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/storage/sqlmodel_models.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 执行拆解

1. 写 restart recovery focused test。
2. 新增 task/event/artifact/feedback records 和 tables。
3. 在 task snapshot/feedback endpoint 保存 API DTO payload。
4. 在 `rehydrate=True` 时重建 class-level runtime state。
5. 用 public GET endpoints 验证恢复。

## 多 agent 分工

主线程直接执行；未拆子线程。

## 需要返回的证据

- red failure：缺少 `reset_runtime_state_for_tests()` 和 rehydrate API。
- green result：restart recovery test 通过。

## 停止条件

- 如果恢复需要生产外部服务则停止。
- 如果必须破坏 task/artifact/feedback API 兼容性则停止。

## PHASE06 Evidence

- `pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider`：`4 passed`。
- `pytest -q tests/api -p no:cacheprovider`：`52 passed`。

