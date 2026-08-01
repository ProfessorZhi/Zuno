# Goal05 PHASE22 Knowledge Pipeline Graph Canonical IR Cutover Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-02
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的一个窄切片：Knowledge pipeline 的 `run_graph_stage` 不再调用 `_parse_chunks` / `parse_file_into_chunk_model_projection`。Graph stage 现在直接通过 `ParseGateway` 生成 `CanonicalDocumentIR`，再使用 `build_index_handoff_payload(document).graphrag_documents` 交给 Graph extractor / writer。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready，也不声明全仓 `ChunkModel` 已退休。`run_rag_index_stage` 仍依赖 `_parse_chunks` / `versioned.adapter.phase22.chunk_model_projection`，因为 RAG / Milvus / optional ES indexing consumer 仍接收 `ChunkModel`。

## Implemented

- `src/backend/zuno/platform/services/pipeline/manager.py` 新增 `_parse_graph_documents`，使用 `knowledge.pipeline.graph_index.canonical_handoff` parser config。
- `run_graph_stage` 改为消费 canonical `graphrag_documents` dict payload，不再为了 Graph indexing 生成 `ChunkModel`。
- Graph extractor 已接收 dict payload；`source_chunk_id` delete 和 project payload 传递保持不变。
- `tests/storage/test_pipeline.py::test_pipeline_graph_stage_uses_canonical_handoff_without_chunk_projection` 用失败替身证明 graph stage 不调用 `parse_file_into_chunk_model_projection`。
- `tests/storage/test_pipeline.py::test_pipeline_graph_stage_passes_project_payload_to_extractor` 覆盖 canonical dict payload 仍传递 project payload。
- `tests/api/test_layered_api_boundaries.py::test_knowledge_pipeline_parse_stage_uses_canonical_ir_before_chunk_projection` 记录默认边界：parse / graph 已 Canonical IR，RAG projection 仍开放。

## Still Open

- `run_rag_index_stage` 仍调用 `_parse_chunks` 并把 ChunkModel 交给 `RagHandler.index_milvus_documents` / optional ES indexing。
- `src/backend/zuno/platform/services/rag/es_client.py` 与部分 RAG doc parser 仍直接依赖 `ChunkModel`。
- `src/backend/zuno/knowledge/ingestion/chunk_projection_adapter.py` 仍存在，直到 Knowledge pipeline RAG indexing consumer 退休 `ChunkModel`。
- Fixed benchmark 仍是 `BLOCKED / blocked_not_measured`。
- Program 仍不能归档，`.agent/programs/` 不能恢复 no-active。

## Verification

```powershell
python -m pytest -q tests/storage/test_pipeline.py::test_pipeline_graph_stage_passes_project_payload_to_extractor tests/storage/test_pipeline.py::test_pipeline_graph_stage_uses_canonical_handoff_without_chunk_projection tests/storage/test_pipeline.py::test_pipeline_manager_updates_task_and_file_state -p no:cacheprovider --tb=short
python -m pytest -q tests/api/test_layered_api_boundaries.py -p no:cacheprovider --tb=short
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
python tools/scripts/verify_current_program.py
```
