# PHASE11 Ingestion Source Lineage Evidence

status: `partial_implementation_available`
phase_completion: `not_approved`

本文记录 PHASE11 Durable Ingestion and Source Lineage 的一个局部实现证据：生产 PostgreSQL schema 边界已为 SourceObject、DocumentVersion、ParsePlan、ParseJob、ParseAttempt、ParseSnapshot、SourceSpan、Quality Gate、IndexableDocumentSnapshot、Outbox 和 Dead Letter 建立正式持久化表。

## Current Boundary

```text
infra/db/alembic/versions/20260719_18_ingestion_source_lineage.py
src/backend/zuno/platform/database/schema_registry.py
src/backend/zuno/platform/database/ingestion/persistence.py
tools/scripts/verify_phase11_ingestion_source_lineage.py
tests/repo/test_phase11_ingestion_source_lineage.py
tests/integration/test_phase11_ingestion_persistence_runtime.py
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

## Validation

```powershell
python tools/scripts/verify_phase11_ingestion_source_lineage.py
pytest -q tests/repo/test_phase11_ingestion_source_lineage.py tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider
```

## Limits

该证据不证明 PHASE11 completed。尚未证明真实默认 upload/parser 路径已经迁移到 PostgreSQL repository，也未覆盖 queue crash、lease loss、retry exhaustion、delete/legal hold/restore、OCR/VLM/Human Review adapter conformance 或完整 Phase Closure Decision。
