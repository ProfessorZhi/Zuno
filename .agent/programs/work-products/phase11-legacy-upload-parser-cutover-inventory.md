# PHASE11 Legacy Upload / Parser Cutover Inventory

status: active_reopen_guard
phase: PHASE11
updated_at: 2026-07-20

## 边界

本文只记录活跃 upload/parser 默认入口的 Cutover 事实，不得作为 PHASE11 完成证据。PHASE11 仍为 `in_progress`，因为生产默认路径尚未证明完整经过 SourceObject、DocumentVersion、ParsePlan、ParseJob、ParseAttempt、ParseSnapshot、CanonicalDocumentIR、SourceSpan、Quality Gate / Human Review、IndexableDocumentSnapshot 与 Outbox Handoff。

## 判定规则

- `canonical_runtime_candidate`：已有 canonical runtime 线索，但尚未证明是生产默认入口。
- `legacy_active_default`：活跃产品路径仍直接调用旧 parser 或旧 pipeline。
- `versioned_adapter_required`：可以保留为临时适配器，但必须绑定 Owner、Removal Phase 和显式入口。
- `not_phase11_ingestion`：不是 PHASE11 durable ingestion 默认入口，不能当作 parser closure evidence。

## 活跃入口清单

| ID | 路径 | 当前归类 | Owner | 默认入口 | 处理决定 | Removal / Cutover Phase | 验收证据 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P11-LC-01 | `src/backend/zuno/api/v1/upload.py` → `src/backend/zuno/api/services/upload.py` | `not_phase11_ingestion` | Product Surface / Input | `/upload` raw object upload API | 只上传对象并返回 public URL；不得作为 SourceObject commit、parser 或 snapshot evidence | PHASE11 不负责删除；后续 Product Surface 需决定是否接入 SourceObject init/commit | `UploadService.upload_bytes` 只调用 storage client，无 ParseGateway / doc_parser | `target_not_current` |
| P11-LC-02 | `src/backend/zuno/platform/services/workspace/attachment_service.py` | `legacy_active_default` | Product Surface / Input | workspace attachment prompt builder | 必须迁移到 canonical ingestion runtime，或封装成版本化 attachment parser adapter；禁止永久隐式 fallback | PHASE11 cutover | 仍直接调用 `doc_parser.parse_doc_into_chunks`，且图片路径走 `_image_to_text` | `target_not_current` |
| P11-LC-03 | `src/backend/zuno/platform/services/pipeline/manager.py` | `legacy_active_default` | Input / Knowledge Runtime | knowledge reindex pipeline parse/rag/graph stages | 必须迁移到 canonical ingestion runtime；解析完成后只能交付 IndexableDocumentSnapshot，不得直接把 Input 结果写成 Knowledge chunks/facts | PHASE11 cutover before PHASE12 | `_parse_chunks` 与 rag/graph stage 仍重复调用 `doc_parser.parse_doc_into_chunks` | `target_not_current` |
| P11-LC-04 | `src/backend/zuno/platform/services/rag/parser.py` 与 `src/backend/zuno/platform/services/rag/doc_parser/**` | `versioned_adapter_required` | Input Parser Adapter Owner | legacy doc parser implementation | 可以作为临时 parser adapter 源实现，但必须挂到统一 Parser Adapter Contract，输入 ObjectRef，输出 CanonicalDocumentIR 或 Typed Failure | PHASE11 adapter cutover; cleanup by PHASE16/PHASE22 if unused | 当前输出 `ChunkModel`，不是 CanonicalDocumentIR / SourceSpan / TransformLedger | `target_not_current` |
| P11-LC-05 | `src/backend/zuno/knowledge/ingestion/gateway.py` | `canonical_runtime_candidate` | Input / Document Ingestion | ParseGateway local runtime | 作为 canonical parser gateway 候选继续推进；尚未证明 PostgreSQL/RabbitMQ/MinIO 生产默认路径和 Human Review gate | PHASE11 completion | 已有 CanonicalDocumentIR、ParseSnapshot、typed failure 线索，但不是活跃产品默认入口 | `target_not_current` |
| P11-LC-06 | `src/backend/zuno/knowledge/ingestion/async_runtime.py` | `canonical_runtime_candidate` | Input / Infrastructure | local durable ingestion worker | 只能作为 local baseline 和 contract evidence；不得用 SQLite/LocalQueue 关闭生产 durable ingestion | PHASE11 completion | LocalQueueBackend、SQLiteDurableIngestionStore、LocalObjectStore 仍是 local fallback | `target_not_current` |

## Reopen Guard

只要 `P11-LC-02` 或 `P11-LC-03` 仍为 `legacy_active_default`，PHASE11 Matrix 的 `Legacy upload/parser Cutover` 行必须保持 `target_not_current`。任何把该行改为 `completion_candidate` 或 `completed` 的变更，必须先提交代码证据证明默认入口已迁移、旧 parser 已版本化或删除，并通过 RabbitMQ、MinIO、PostgreSQL、lease/fencing、Quality/Human Review 与 outbox handoff focused tests。
