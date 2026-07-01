# PHASE02 Durable Storage Contract

status: completed
program: zuno-enterprise-document-ingestion-platform-v2
phase: PHASE02_durable-storage-contract
mode: tdd-implementation

## 目标

把 PHASE01 的 gap audit 转成最小可执行 contract：先用 focused tests 固定 durable store API、SQLite round-trip、local object store 边界和 restart recovery 输入事实，再实现最小后端持久化 store。

本 phase 不追求完整生产 DB / object store / Redis；它只关闭 Launchable Prototype 的第一块基建：

```text
SQLite-compatible durable store contract
+ local file/object store boundary
+ source object / workspace file / parse snapshot / document version / index chunk round-trip
```

## 范围

- 新增 focused tests，先证明当前缺 durable store contract。
- 新增 `src/backend/zuno/knowledge/storage/` 或等价模块，定义 Product V1 local durable store。
- 允许新增 SQLModel models、repository / store contract、SQLite test factory、local object store helper。
- 允许新增 `tests/knowledge/test_enterprise_ingestion_storage_contract.py`。
- 只在确实需要时新增 API 层测试种子；API runtime 接入可以留到后续 phase。

## 禁止范围

- 不改 `GeneralAgent` 主循环。
- 不启动 Program 3 Memory / Tool / Security / GraphRAG。
- 不引入必须运行的 Postgres、Redis、MinIO、Kafka、Elasticsearch、Milvus、Neo4j、OCR / VLM 服务。
- 不把 Redis / object store / outbox / worker lease / external OCR / VLM / external index 写成 Current。
- 不破坏现有 `/workspace/file`、`/workspace/ingest`、task、artifact、feedback response shape。

## 验收闸门

1. 先写 focused test。
2. 运行并确认失败原因是缺 module / 缺 contract / 缺持久化能力。
3. 实现最小代码。
4. focused test 通过。
5. repo verifier 和 guardrail tests 通过。

## 需要先读取

- `docs/architecture/document-ingestion-foundation.md`
- `src/backend/zuno/knowledge/ingestion/contracts.py`
- `src/backend/zuno/knowledge/indexing/contracts.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `tests/knowledge/`

## 需要修改的文件

- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/storage/local_object_store.py`
- `src/backend/zuno/knowledge/storage/sqlmodel_models.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `src/backend/zuno/knowledge/storage/__init__.py`
- `tests/knowledge/test_enterprise_ingestion_storage_contract.py`

## 执行拆解

1. 写 durable ingestion store focused test，并确认 red failure。
2. 定义 source object、workspace file、parse job、document version、index manifest 和 index chunk records。
3. 实现 local object store 和 SQLite durable ingestion store。
4. 跑 focused test、knowledge tests 和 repo verifier。

## 多 agent 分工

本 phase 由主线程直接执行；未拆子线程，避免在 store contract 和 SQLModel schema 上产生并行冲突。

## 需要返回的证据

- red failure：缺少 `zuno.knowledge.storage` module。
- green result：`tests/knowledge/test_enterprise_ingestion_storage_contract.py` 通过。
- 边界证据：生产 Postgres、Redis、MinIO、external OCR / VLM 和 external index 仍保留为 Target。

## 停止条件

- 如果必须接入外部 DB / object store / queue 才能继续，停止并回报。
- 如果必须破坏 `/workspace/file` 或 `/workspace/ingest` response shape，停止并回报。

## 最小 store contract

PHASE02 必须至少覆盖：

- `save_source_object()`
- `save_workspace_file()`
- `create_parse_job()`
- `save_parse_snapshot()`
- `save_document_version()`
- `save_index_manifest()`
- `save_index_chunk()`
- `get_workspace_file()`
- `get_parse_job()`
- `get_document_version()`
- `get_index_manifest()`
- `list_index_chunks()`

本 phase 可以先不接入 `WorkspaceTaskRuntimeService` 主链路；但 schema / store API 必须能承接 PHASE03-PHASE06。

## 验证命令

```powershell
pytest -q tests/knowledge/test_enterprise_ingestion_storage_contract.py -p no:cacheprovider
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## PHASE02 Evidence

### TDD Red

已先写 focused test：

- `tests/knowledge/test_enterprise_ingestion_storage_contract.py::test_sqlite_store_round_trips_source_file_parse_snapshot_and_index_manifest`

首次运行：

```powershell
pytest -q tests/knowledge/test_enterprise_ingestion_storage_contract.py -p no:cacheprovider
```

结果：失败，原因符合预期：

```text
ModuleNotFoundError: No module named 'zuno.knowledge.storage'
```

### TDD Green

新增最小实现：

- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/storage/local_object_store.py`
- `src/backend/zuno/knowledge/storage/sqlmodel_models.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `src/backend/zuno/knowledge/storage/__init__.py`

当前 contract：

- `LocalObjectStore.save_text()` 保存本地 source content，返回 `SourceObjectRecord`、`storage_uri`、`source_sha256`、ACL 和 sensitivity。
- `SQLiteDurableIngestionStore` 支持 source object、workspace file、parse job、parse snapshot、document version、index manifest 和 index chunk round-trip。
- 当前不接 Postgres / Redis / MinIO / OSS / worker lease / external OCR / VLM；这些仍是 Target。

再次运行：

```powershell
pytest -q tests/knowledge/test_enterprise_ingestion_storage_contract.py -p no:cacheprovider
```

结果：

```text
1 passed in 1.01s
```

### 验证结果

2026-07-01 已运行：

- `pytest -q tests/knowledge/test_enterprise_ingestion_storage_contract.py -p no:cacheprovider`：通过，`1 passed`。
- `pytest -q tests/knowledge -p no:cacheprovider`：通过，`50 passed`。
- `git diff --check`：通过；仅出现 Windows 工作树 CRLF 提示。
- `python tools/agent/render_architecture.py --check`：通过。
- `python tools/scripts/verify_docs_entrypoints.py`：通过。
- `python tools/scripts/verify_repo_structure.py`：通过。
- `python .agent/scripts/verify_agent_system.py`：通过。
- `python .agent/scripts/verify_doc_boundaries.py`：通过。
- `python .agent/scripts/verify_repo_hygiene.py`：通过。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`：通过。
- `pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider`：通过，`72 passed`。
