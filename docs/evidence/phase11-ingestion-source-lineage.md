# PHASE11 Ingestion Source Lineage Evidence

status: `reopened_partial_evidence`
phase_completion: `reopened_pending`

本文记录 PHASE11 Durable Ingestion and Source Lineage 的部分实现证据。当前证据证明 PostgreSQL ingestion schema、`IngestionUnitOfWork`、SourceObject 到 IndexableDocumentSnapshot 的持久化边界，以及本地 runtime batch 的若干行为线索；它不证明 PHASE11 已完成。

## Current Boundary

```text
infra/db/alembic/versions/20260719_18_ingestion_source_lineage.py
src/backend/zuno/platform/database/schema_registry.py
src/backend/zuno/platform/database/ingestion/persistence.py
src/backend/zuno/knowledge/ingestion/source_object_commit.py
tools/scripts/verify_phase11_ingestion_source_lineage.py
tests/repo/test_phase11_ingestion_source_lineage.py
tests/integration/test_phase11_ingestion_persistence_runtime.py
tests/knowledge/test_ingestion_source_object_commit.py
docs/evidence/input-runtime-batch.md
```

## Verified Behavior

- Migration 串接到 `20260719_17`，避免产生第二个 Alembic head。
- `ingestion_*` 表统一归属 `Input / Document Ingestion`。
- SourceObject 保留 object manifest、hash、classification 和 security epoch。
- `SourceObjectCommitRuntime` 消费 PHASE04 `ObjectStoreReceipt`，只接受 visible object receipt，并校验 object manifest ref、tenant/workspace object prefix、hash、size、mime type、classification 与 security epoch 后生成 PHASE11 `SourceObjectRecord`。
- DocumentVersion 与 ParseSnapshot 分离；ParseSnapshot 绑定 ParseJob、ParseAttempt 和 DocumentVersion。
- ParseAttempt 持久化 lease、fencing token、attempt number 和状态。
- SourceSpan 可回溯到 ParseSnapshot 与 DocumentVersion。
- Quality Gate 是 IndexableDocumentSnapshot 发布前置条件。
- Input migration 不创建 Chunk、Entity、Relation、KnowledgeVersion、BM25 或 Vector Index。
- `IngestionUnitOfWork` 可在同一 PostgreSQL transaction 中写入 SourceObject、DocumentVersion、ParsePlan、ParseJob、ParseAttempt、ParseSnapshot、SourceSpan、QualityDecision、IndexableDocumentSnapshot 和 outbox event。
- 同一 UoW 中后续 domain write 失败会回滚已写 SourceObject / DocumentVersion。
- 同一 tenant 的 ParseJob idempotency key 由数据库唯一约束保护；重复写入被拒绝且不会新增第二个 ParseJob。
- IndexableDocumentSnapshot 必须引用 QualityGateDecision；缺质量门时数据库 FK 拒绝 handoff。
- SourceObject 写入前验证 `source_sha256` 是 64 位 hash。
- LocalQueue ACK / retry / dead-letter / replay、RabbitMQ target-blocked probe、Redis fallback boundary 只作为线索；外部依赖不可用不能冒充 production dependency。
- PHASE11 重新打开后，ParseAttemptControl、native/PDF parser、OCR/VLM、Office/archive、delete/legal hold/restore 等证据都只保留为部分证据，不能单独关闭 PHASE11。
- `local_office_archive` 当前提供 Office/Archive 的可执行本地 fallback：docx/xlsx 保留 heading/table projection，pptx 保留 slide/figure projection，archive 只读取 manifest、不自动解包；live Unstructured / MarkItDown provider 保持 measurement blocked。

## Validation

```powershell
python tools/scripts/verify_phase11_ingestion_source_lineage.py
pytest -q tests/repo/test_phase11_ingestion_source_lineage.py tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_source_object_commit.py -p no:cacheprovider
pytest -q tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
python tools/scripts/verify_input_runtime_batch.py
pytest -q tests/knowledge/test_input_runtime_batch.py tests/knowledge/test_ingestion_async_infrastructure.py tests/integration/test_phase11_ingestion_persistence_runtime.py tests/repo/test_phase11_ingestion_source_lineage.py -p no:cacheprovider
```

## Boundary

PHASE11 completed 只能表示完整 Phase Scope 内 implementation available；不表示 production ready、quality proven、PHASE12 Knowledge completed 或外部 RabbitMQ/OCR/VLM 生产依赖已在本地环境可用。外部依赖不可用时必须保留 target-blocked diagnostics，不能用 mock 冒充生产能力。

## 2026-07-20 Goal01 Reopen Audit

本文证据保留为 PHASE11 的部分实现线索，但不再证明完整 Phase completed。剩余缺口包括真实 RabbitMQ 生产默认 dispatch/ACK/retry/DLQ/replay、生产默认 worker 接入 PostgreSQL UoW 与 PHASE04 Object Store、可执行 OCR/VLM adapter boundary、Human Review task/decision/receipt 状态机、完整 delete/legal hold/restore fault coverage，以及 legacy upload/parser 默认路径 cutover。
