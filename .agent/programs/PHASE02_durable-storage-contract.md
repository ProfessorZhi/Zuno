# PHASE02 Durable Storage Contract

status: active
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

## TDD 验收

1. 先写 focused test。
2. 运行并确认失败原因是缺 module / 缺 contract / 缺持久化能力。
3. 实现最小代码。
4. focused test 通过。
5. repo verifier 和 guardrail tests 通过。

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

启动时本节为空；TDD red / green 证据、store contract、验证结果和 commit / push evidence 必须在本 phase 结束前补齐。
