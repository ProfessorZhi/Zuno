# PHASE11 Durable Ingestion and Source Lineage

phase_id: PHASE11
status: completed
depends_on: PHASE04, PHASE05
owner: Module 02 Input / Document Ingestion

## Phase 目标

PHASE04 PostgreSQL Domain and Transaction Foundation 与 PHASE05 Security Control Plane 已由 Coordinator Closure 批准为 completed。2026-07-20 Goal01 audit 曾重新打开 PHASE11：既有 LocalQueue、SQLite runtime batch、target-blocked OCR/VLM 诊断和 degraded/block quality gate 证据不足以证明本 Phase 完整生产默认路径完成。

PHASE11 当前在 Goal02 final closure 中重新批准为 `completed`。0b1e087a 的 closure evidence 保留为历史实现线索；本轮 closure 依据 durable Human Review Resume、Delete / Restore / Reconciliation 和真实运行证据完成。

Goal02 final closure status: PHASE11 completed with implementation_available evidence; coordinator_approval: approved; PHASE09 ready; PHASE12 ready; production ready not established.

实现 SourceObject→DocumentVersion→ParsePlan/Job/Attempt→ParseSnapshot→CanonicalDocumentIR→SourceSpan→Quality Gate→IndexableDocumentSnapshot 的持久异步闭环，具备 Object Store、Queue、Lease/Fencing、Parser Router、OCR/VLM/Human Review、删除和恢复。

## Minimal Read Set

- `docs/modules/02-input-document-ingestion.md`
- PHASE03 Envelope
- PHASE04 PostgreSQL/Object/Queue/Lease
- PHASE05 Security/Redaction
- 当前 upload/file/parser/PDF/OCR/ingestion store/index handoff

## Current Anchors

```text
src/backend/zuno/knowledge/ingestion/**
src/backend/zuno/knowledge/storage/**
src/backend/zuno/api/**/file*
parser/pdf/ocr code
local object/index manifests
```

## Allowed Paths

```text
src/backend/zuno/knowledge/ingestion/**
src/backend/zuno/knowledge/storage/**
src/backend/zuno/platform/database/ingestion/**
parser adapters/workers
alembic/**
tests/ingestion/**
tests/integration/ingestion/**
tests/fault/ingestion/**
docs/evidence/**
```

## Forbidden Paths

- Input 直接拥有 Chunk、Entity、Relation、KnowledgeVersion。
- 覆盖原始 SourceObject 或旧 DocumentVersion。
- Queue ACK 当 Parse/Publish 成功。

## Work Packages

### P11-T01 SourceObject and Object Integrity
- Goal：实现 upload/init/commit、content hash、mime/size/classification、object manifest、dedup/conflict。
- Tests：partial upload、hash mismatch、same content、malicious mime、tenant scope、delete intent。
- Acceptance：原始证据不可覆盖，大 payload 只存 ObjectRef。

### P11-T02 DocumentVersion and ParseSnapshot Domain
- Goal：源内容变化创建 DocumentVersion；parser/model/config/schema 变化创建 ParseSnapshot。
- Tests：version immutability、same source no duplicate、reparse、optimistic concurrency。
- Acceptance：两种版本语义不混合。

### P11-T03 Parse Planner, Job, Attempt and Queue
- Goal：实现 parser route、job/attempt state、outbox dispatch、lease/fencing、heartbeat、retry/dead letter。
- Tests：worker crash、duplicate delivery、lease loss、retry exhausted、cancel/deadline。
- Acceptance：Attempt append-only，旧 worker 结果被 fencing 拒绝。

### P11-T04 Parser Adapter Conformance
- Goal：Native/Layout/PDF/OCR/VLM/Archive/Office adapter 统一 input/output/failure/quality/timeout。
- Tests：golden fixtures、encrypted/corrupt/oversized、OCR fallback、remote provider failure、sandbox。
- Acceptance：远程 Parser 通过 Security/Data Policy，不泄露敏感 payload。

### P11-T05 CanonicalDocumentIR, SourceSpan and TransformLedger
- Goal：实现 block/page/region/order/style/table/image refs、source coordinates、transform provenance。
- Tests：text PDF page citation、table span、OCR bbox、normalization trace、schema round-trip。
- Acceptance：IR 不等于 Knowledge Chunk，SourceSpan 可稳定回溯原证据。

### P11-T06 Quality Gate and Human Review
- Goal：实现 quality metrics、threshold、blocked/review/fallback decision、review task/receipt。
- Tests：low coverage、layout conflict、OCR confidence、review approve/reject/expire。
- Acceptance：缺质量不能自动发布 Indexable Snapshot。

### P11-T07 Indexable Snapshot Handoff
- Goal：生成 immutable IndexableDocumentSnapshotV1 Envelope，包含 version/span/security/delete refs。
- Tests：hash/schema/scope、duplicate handoff、knowledge unavailable、outbox replay。
- Acceptance：Input 只提交 Snapshot，不直接写 Knowledge Index。

### P11-T08 Delete, Recovery and Legacy Parser Cutover
- Goal：实现 visibility revoke→projection cleanup request→physical delete→verification；迁移旧 parser/upload path。
- Tests：legal hold、delete during parse、restore、orphan attempt、old parser fallback/cutover。
- Acceptance：生产代码无 `legacy_parser`/旧 ingestion 目录；必要格式 adapter 位于清晰 adapters 包。

## Phase 完成定义

- 真实文档可从上传到 Indexable Snapshot，SourceSpan 可回溯。
- Queue/Crash/Fencing/Quality/Delete Fault Test 通过。
- 旧 ingestion 路径切流且有删除门。

## Validation

```bash
git diff --check
pytest -q tests/ingestion tests/integration/ingestion tests/fault/ingestion -p no:cacheprovider
# run parser golden suite discovered in PHASE01
```
