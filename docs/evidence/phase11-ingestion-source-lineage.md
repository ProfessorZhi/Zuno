# PHASE11 Ingestion Source Lineage Evidence

status: `implementation_available`
phase_completion: `approved`

本文记录 PHASE11 Durable Ingestion and Source Lineage 的实现证据：生产 PostgreSQL schema 边界已为 SourceObject、DocumentVersion、ParsePlan、ParseJob、ParseAttempt、ParseSnapshot、SourceSpan、Quality Gate、IndexableDocumentSnapshot、Outbox 和 Dead Letter 建立正式持久化表；`input-runtime-batch` 已覆盖 `ARCH-ING-001` 到 `ARCH-ING-080` 的 runtime batch 行为。

## Current Boundary

```text
infra/db/alembic/versions/20260719_18_ingestion_source_lineage.py
src/backend/zuno/platform/database/schema_registry.py
src/backend/zuno/platform/database/ingestion/persistence.py
tools/scripts/verify_phase11_ingestion_source_lineage.py
tests/repo/test_phase11_ingestion_source_lineage.py
tests/integration/test_phase11_ingestion_persistence_runtime.py
docs/evidence/input-runtime-batch.md
```

## Verified Behavior

- Migration 链接到 `20260719_17`，避免产生第二 Alembic head。
- `ingestion_*` 表统一归属 `Input / Document Ingestion`。
- SourceObject 保留 object manifest、hash、classification 和 security epoch。
- DocumentVersion 与 ParseSnapshot 分离，ParseSnapshot 绑定 ParseJob、ParseAttempt 和 DocumentVersion。
- ParseAttempt 持久化 lease、fencing token、attempt number 和状态。
- SourceSpan 可回溯 ParseSnapshot 与 DocumentVersion。
- Quality Gate 是 IndexableDocumentSnapshot 发布前置条件。
- Input migration 不创建 Chunk、Entity、Relation、KnowledgeVersion、BM25 或 Vector Index。
- `IngestionUnitOfWork` 可在一笔 PostgreSQL transaction 中写入 SourceObject 到 IndexableDocumentSnapshot 和 outbox event。
- IndexableDocumentSnapshot 必须引用 QualityGateDecision；缺质量门时数据库 FK 拒绝 handoff。
- SourceObject 写入前验证 `source_sha256` 是 64 位 hash。
- LocalQueue ACK / retry / dead-letter / replay、RabbitMQ target-blocked probe、Redis fallback boundary 均已验证，外部依赖不可用不会冒充 production dependency。
- ParseAttemptControl 覆盖 lease、fencing token 和 late result rejection。
- Native/PDF current adapter、OCR/VLM target-blocked diagnostics、Office/archive preservation boundary、delete receipts、legal hold 和 restore verification 均由 `input-runtime-batch` 记录。

## Validation

```powershell
python tools/scripts/verify_phase11_ingestion_source_lineage.py
pytest -q tests/repo/test_phase11_ingestion_source_lineage.py tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider
python tools/scripts/verify_input_runtime_batch.py
pytest -q tests/knowledge/test_input_runtime_batch.py tests/knowledge/test_ingestion_async_infrastructure.py tests/integration/test_phase11_ingestion_persistence_runtime.py tests/repo/test_phase11_ingestion_source_lineage.py -p no:cacheprovider
```

## Boundary

PHASE11 completed 只表示完整 Phase Scope 内 implementation available；不表示 production ready、quality proven、PHASE12 Knowledge completed 或外部 RabbitMQ/OCR/VLM 生产依赖已在本地环境可用。外部依赖不可用时必须保留 target-blocked diagnostics，不能用 mock 冒充生产能力。
