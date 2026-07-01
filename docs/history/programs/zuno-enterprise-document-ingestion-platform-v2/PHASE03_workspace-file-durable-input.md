# PHASE03 Workspace File Durable Input

status: completed
program: zuno-enterprise-document-ingestion-platform-v2
phase: PHASE03_workspace-file-durable-input
mode: tdd-implementation

## 目标

把 `/workspace/file` 从内存 file registry 推进到 Product V1 durable input：保存 local source object、source hash、storage uri 和 workspace file metadata，同时保持原 response 的 `file`、`name`、`uri` 兼容。

## 范围

- `WorkspaceTaskRuntimeService.register_file()`。
- `LocalObjectStore` 和 `SQLiteDurableIngestionStore`。
- `tests/api/test_workspace_durable_ingest_runtime.py` 的 focused API test。

## 禁止范围

- 不接 MinIO / OSS / S3。
- 不改变 `UploadedFileContract` 已有字段语义。
- 不把外部对象存储写成 Current。

## 验收闸门

- `/workspace/file` 返回 additive `source_id`、`source_sha256`、`storage_uri`、`durable_status`。
- fresh SQLite store 可读取 source object 和 workspace file record。
- local object file 内容与上传内容一致。

## 验证命令

```powershell
pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_file_register_persists_source_object_and_content_ref -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_file_ingest_and_approval_runtime_closes_phase03_surface -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/storage/`
- `tests/api/test_workspace_task_runtime.py`

## 需要修改的文件

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 执行拆解

1. 先写 `/workspace/file` durable focused test。
2. 确认 red failure 是缺少 durable runtime hook。
3. 新增 service 配置 hook、source object getter 和 file registration persistence。
4. 跑 focused tests 到 green。

## 多 agent 分工

本 phase 由主线程直接执行；未拆子线程，避免多个 agent 同时修改同一 API service。

## 需要返回的证据

- red failure：`WorkspaceTaskRuntimeService` 缺少 `configure_durable_ingestion()`。
- green result：focused durable file test 通过。
- 兼容 result：既有 workspace file / ingest / approval test 通过。

## 停止条件

- 如果 public response 需要破坏性改名则停止。
- 如果必须接外部 object store 才能继续则停止。

## PHASE03 Evidence

- `pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_file_register_persists_source_object_and_content_ref -p no:cacheprovider`：`1 passed`。
- `pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_file_ingest_and_approval_runtime_closes_phase03_surface -p no:cacheprovider`：`1 passed`。

