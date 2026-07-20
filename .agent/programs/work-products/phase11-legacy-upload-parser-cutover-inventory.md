# PHASE11 Legacy Upload / Parser Cutover Inventory

status: active_reopen_guard
phase: PHASE11
updated_at: 2026-07-20

## 边界

本文只记录活跃 upload/parser 默认入口的 Cutover 事实，不得作为 PHASE11 完成证据。PHASE11 仍为 `in_progress`，因为生产默认路径尚未证明完整经过 SourceObject、DocumentVersion、ParsePlan、ParseJob、ParseAttempt、ParseSnapshot、CanonicalDocumentIR、SourceSpan、Quality Gate / Human Review、IndexableDocumentSnapshot 与 Outbox Handoff。

## 判定规则

- `canonical_runtime_candidate`：已有 canonical runtime 线索，但尚未证明是生产默认入口。
- `legacy_active_default`：活跃产品路径仍直接调用旧 parser 或旧 pipeline。
- `versioned_adapter_required`：活跃产品路径已显式进入版本化过渡 adapter，但仍输出旧消费者需要的格式，必须绑定 Owner、Removal Phase、显式入口和剩余 cutover。
- `not_phase11_ingestion`：不是 PHASE11 durable ingestion 默认入口，不能当作 parser closure evidence。

## 活跃入口清单

| ID | 路径 | 当前归类 | Owner | 默认入口 | 处理决定 | Removal / Cutover Phase | 验收证据 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P11-LC-01 | `src/backend/zuno/api/v1/upload.py` → `src/backend/zuno/api/services/upload.py` | `not_phase11_ingestion` | Product Surface / Input | `/upload` raw object upload API | 只上传对象并返回 public URL；不得作为 SourceObject commit、parser 或 snapshot evidence | PHASE11 不负责删除；后续 Product Surface 需决定是否接入 SourceObject init/commit | `UploadService.upload_bytes` 只调用 storage client，无 ParseGateway / doc_parser | `target_not_current` |
| P11-LC-02 | `src/backend/zuno/platform/services/workspace/attachment_service.py` | `versioned_adapter_required` | Product Surface / Input | workspace attachment prompt builder | 文档附件已显式进入 `temporary.adapter.phase11.legacy_chunk_projection`，由 ParseGateway 生成 CanonicalDocumentIR 后再转换为过渡文本 excerpt；图片路径仍走 `_image_to_text`，必须继续纳入 Parser Adapter / Review 边界 | PHASE16 removal；PHASE11 继续 cutover 图片与生产默认链路 | `parse_file_into_legacy_chunks`；`src/backend/zuno/knowledge/ingestion/legacy_cutover.py` | `target_not_current` |
| P11-LC-03 | `src/backend/zuno/platform/services/pipeline/manager.py` | `versioned_adapter_required` | Input / Knowledge Runtime | knowledge reindex pipeline parse/rag/graph stages | `_parse_chunks` 已改为调用 `temporary.adapter.phase11.legacy_chunk_projection`：ParseGateway 先生成 CanonicalDocumentIR，再显式转换为旧 RAG/Graph 消费的 ChunkModel；仍不是最终 IndexableDocumentSnapshot / Outbox handoff | PHASE16 removal；PHASE12 前必须迁移旧 Knowledge chunk/fact 写入 | `parse_file_into_legacy_chunks`；`tests/storage/test_pipeline.py` focused path | `target_not_current` |
| P11-LC-04 | `src/backend/zuno/platform/services/rag/parser.py` 与 `src/backend/zuno/platform/services/rag/doc_parser/**` | `versioned_adapter_required` | Input Parser Adapter Owner | legacy doc parser implementation | 已退出 P11-LC-02 / P11-LC-03 的默认文档 parser 调用；仍作为旧实现保留给其他未迁移路径和兼容测试，必须由 PHASE16/PHASE22 清理或继续封装 | PHASE16/PHASE22 if unused | `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` 明确 owner/removal；旧 parser 仍输出 `ChunkModel`，不得作为 PHASE11 closure evidence | `target_not_current` |
| P11-LC-05 | `src/backend/zuno/knowledge/ingestion/gateway.py` | `canonical_runtime_candidate` | Input / Document Ingestion | ParseGateway local runtime | 作为 canonical parser gateway 候选继续推进；尚未证明 PostgreSQL/RabbitMQ/MinIO 生产默认路径和 Human Review gate | PHASE11 completion | 已有 CanonicalDocumentIR、ParseSnapshot、typed failure 线索，但不是活跃产品默认入口 | `target_not_current` |
| P11-LC-06 | `src/backend/zuno/knowledge/ingestion/async_runtime.py` | `canonical_runtime_candidate` | Input / Infrastructure | local durable ingestion worker | 只能作为 local baseline 和 contract evidence；不得用 SQLite/LocalQueue 关闭生产 durable ingestion | PHASE11 completion | LocalQueueBackend、SQLiteDurableIngestionStore、LocalObjectStore 仍是 local fallback | `target_not_current` |

## Reopen Guard

即使 `P11-LC-02` 与 `P11-LC-03` 已降为 `versioned_adapter_required`，PHASE11 Matrix 的 `Legacy upload/parser Cutover` 行仍必须保持 `target_not_current`，直到默认生产路径不再输出旧 Knowledge chunks/facts，而是完整进入 SourceObject → ParseSnapshot → Quality/Human Review → IndexableDocumentSnapshot → Outbox Handoff。任何把该行改为 `completion_candidate` 或 `completed` 的变更，必须先提交代码证据证明默认入口已迁移、旧 parser 已版本化或删除，并通过 RabbitMQ、MinIO、PostgreSQL、lease/fencing、Quality/Human Review 与 outbox handoff focused tests。
