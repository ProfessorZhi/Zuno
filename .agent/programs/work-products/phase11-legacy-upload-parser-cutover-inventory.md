# PHASE11 Legacy Upload / Parser Cutover Inventory

status: closure_inventory
phase: PHASE11
updated_at: 2026-07-20

## 边界

本文记录活跃 upload/parser 默认入口的 Cutover 事实。Goal02 closure 后，PHASE11 为 `completed`：生产默认路径已证明完整经过 SourceObject、DocumentVersion、ParsePlan、ParseJob、ParseAttempt、ParseSnapshot、CanonicalDocumentIR、SourceSpan、Quality Gate / Human Review、IndexableDocumentSnapshot 与 Outbox Handoff。

## 判定规则

- `canonical_runtime_candidate`：已有 canonical runtime 线索，但尚未证明是生产默认入口。
- `legacy_active_default`：活跃产品路径仍直接调用旧 parser 或旧 pipeline。
- `retired_removed`：旧实现已从生产源码删除，不再作为可导入兼容运行面存在。
- `canonical_ir_default_no_chunk_projection`：活跃产品路径直接消费 `CanonicalDocumentIR`，不再经过 `ChunkModel` projection，但仍不是 PHASE11 durable ingestion 默认入口。
- `not_phase11_ingestion`：不是 PHASE11 durable ingestion 默认入口，不能当作 parser closure evidence。

## 活跃入口清单

| ID | 路径 | 当前归类 | Owner | 默认入口 | 处理决定 | Removal / Cutover Phase | 验收证据 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P11-LC-01 | `src/backend/zuno/api/v1/upload.py` → `src/backend/zuno/api/services/upload.py` | `not_phase11_ingestion` | Product Surface / Input | `/upload` raw object upload API | 只上传对象并返回 public URL；不作为 SourceObject commit、parser 或 snapshot evidence | PHASE09/10 Product Surface 决定是否接入 SourceObject init/commit | `UploadService.upload_bytes` 只调用 storage client，无 ParseGateway / doc_parser | `not_applicable_to_phase11_default_path` |
| P11-LC-02 | `src/backend/zuno/platform/services/workspace/attachment_service.py` | `canonical_ir_default_no_chunk_projection` | Product Surface / Input | workspace attachment prompt builder | 文档附件默认路径直接调用 `ParseGateway` / `ParseDocumentRequest` 并从 `CanonicalDocumentIR.blocks` 提取 prompt excerpt；不再加载 `chunk_projection_adapter` 或 `ChunkModel` projection；图片路径继续纳入 Parser Adapter / Review 边界 | PHASE22 workspace attachment cutover completed；Knowledge pipeline ChunkModel retirement 另由 P11-LC-03 / PHASE16 blocker 跟踪 | `tests/api/test_workspace_attachment_canonical_ir.py`；`tests/api/test_layered_api_boundaries.py::test_workspace_attachment_uses_canonical_ir_without_chunk_projection_default` | `canonical_ir_default_current` |
| P11-LC-03 | `src/backend/zuno/platform/services/pipeline/manager.py` | `canonical_ir_default_no_chunk_projection` | Input / Knowledge Runtime | knowledge reindex pipeline parse/rag/graph stages | `run_parse_stage` 已直接调用 `ParseGateway` / `ParseDocumentRequest` 并从 `CanonicalDocumentIR.blocks` 记录 parse count；`run_graph_stage` 已直接使用 `build_index_handoff_payload(...).graphrag_documents`；`run_rag_index_stage` 已直接使用 `build_index_handoff_payload(...).vector_documents` 生成 canonical dict payload，Milvus/ES 写入端支持 dict payload；最终 KnowledgeVersion 归 PHASE12 | PHASE22 pipeline default cutover completed；旧 RAG doc_parser / ChunkModel DTO 兼容残留另由 PHASE22 cleanup 跟踪 | `tests/storage/test_pipeline.py::test_pipeline_parse_stage_uses_canonical_ir_without_chunk_projection`；`tests/storage/test_pipeline.py::test_pipeline_graph_stage_uses_canonical_handoff_without_chunk_projection`；`tests/storage/test_pipeline.py::test_pipeline_rag_stage_uses_canonical_handoff_without_chunk_projection`；`tests/storage/test_pipeline.py::test_milvus_lite_client_accepts_canonical_dict_chunks`；`tests/storage/test_pipeline.py::test_es_client_accepts_canonical_dict_chunks` | `canonical_ir_default_current` |
| P11-LC-04 | `src/backend/zuno/platform/services/rag/parser.py` 与 `src/backend/zuno/platform/services/rag/doc_parser/**` | `retired_removed` | Input Parser Adapter Owner | retired legacy doc parser implementation | 已退出 P11-LC-02 / P11-LC-03 的默认文档 parser 调用；`tools/scripts/rebuild_rag_indexes.py`、fixed/local eval、history RAG write 与兼容测试均已改为 Canonical IR / canonical vector payload dict；旧实现已删除，不再作为非默认兼容运行面存在 | PHASE22 cleanup retired | `src/backend/zuno/knowledge/ingestion/vector_payload.py` 为 canonical vector payload helper；`tests/api/test_layered_api_boundaries.py::test_platform_rag_uses_canonical_imports` 禁止旧路径恢复 | `retired_removed` |
| P11-LC-05 | `src/backend/zuno/knowledge/ingestion/gateway.py` | `canonical_runtime_candidate` | Input / Document Ingestion | ParseGateway local runtime | canonical parser gateway 已有 Package A、PostgreSQL/RabbitMQ/MinIO 和 Human Review gate 部分证据，Goal02 limited Closure Review 已完成 | PHASE11 completed | CanonicalDocumentIR、ParseSnapshot、typed failure、Package A production runtime | `implementation_available` |
| P11-LC-06 | `src/backend/zuno/knowledge/ingestion/async_runtime.py` | `canonical_runtime_candidate` | Input / Infrastructure | local durable ingestion worker | 作为 local baseline 和 contract evidence；生产默认路径由 Package A PostgreSQL/RabbitMQ/MinIO runtime 承担，Goal02 limited Closure Review 已完成 | PHASE11 completed | LocalQueueBackend、SQLiteDurableIngestionStore、LocalObjectStore 是 local fallback | `local_fallback_contained` |

## Closure Guard

PHASE11 closure 要求默认生产路径完整进入 SourceObject → ParseSnapshot → Quality/Human Review → IndexableDocumentSnapshot → Outbox Handoff，并通过 RabbitMQ、MinIO、PostgreSQL、lease/fencing、Quality/Human Review 与 outbox handoff focused tests。Goal02 已满足该条件。活跃 workspace attachment、Knowledge pipeline parse/rag/graph、RAG rebuild script、fixed/local eval 与 history RAG write 默认入口均已退出 ChunkModel projection；旧 RAG doc_parser / ChunkModel DTO 兼容运行面已在 PHASE22 cleanup 删除，不得重新解释为 PHASE11 未完成。
