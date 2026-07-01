# PHASE04 Parse / Document Persistence

status: completed
program: zuno-enterprise-document-ingestion-platform-v2
phase: PHASE04_parse-document-persistence
mode: tdd-implementation

## 目标

让 `/workspace/ingest` 继续走 `ParseGateway.submit_parse_job()`，并把 parse job、parse snapshot、document version、document block / IR JSON 落入 SQLite durable store。

## 范围

- `WorkspaceTaskRuntimeService.create_ingest_job()` 的 durable hook。
- `SQLiteDurableIngestionStore` 的 document block 表和读取方法。
- blocked / failed parser diagnostics 的持久化。

## 禁止范围

- 不恢复 `_document_from_file()` / `workspace_text_runtime` 为主链路。
- 不接 Redis / worker lease / outbox。
- 不把 OCR / VLM / PDF / Office 外部 worker 写成 Current。

## 验收闸门

- parse job 和 parse snapshot 可 fresh store 查询。
- document version 和 document blocks 可 fresh store 查询。
- blocked parser diagnostics 持久化。
- blocked 不创建 fake index。

## 验证命令

```powershell
pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_ingest_persists_parse_document_index_and_chunks -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_target_blocked_parser_diagnostics_are_persisted_without_fake_index -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/knowledge/ingestion/gateway.py`
- `src/backend/zuno/knowledge/ingestion/contracts.py`
- `docs/architecture/document-ingestion-foundation.md`

## 需要修改的文件

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/storage/sqlmodel_models.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 执行拆解

1. 写 ingest persistence focused test。
2. 写 blocked diagnostics focused test。
3. 在 ingest service 中复用 durable file/source object。
4. 保存 parse job、snapshot、document version 和 document blocks。
5. 确认 blocked 分支只保存 diagnostics，不写 index manifest。

## 多 agent 分工

主线程直接执行；未拆子线程。

## 需要返回的证据

- red failure：缺少 `durable_status` / `list_document_blocks()`。
- green result：durable ingest 和 blocked diagnostics tests 通过。

## 停止条件

- 如果 ParseGateway 不能提供稳定 snapshot 则停止。
- 如果 blocked 需要假成功 index 才能通过 API 则停止。

## PHASE04 Evidence

- `pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider`：`4 passed`。
- `pytest -q tests/knowledge -p no:cacheprovider`：`50 passed`。

