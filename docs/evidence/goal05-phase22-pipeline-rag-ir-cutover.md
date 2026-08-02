# Goal05 PHASE22 Knowledge Pipeline RAG Canonical IR Cutover Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-02
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的一个窄切片：Knowledge pipeline 的 `run_rag_index_stage` 不再调用 `_parse_chunks` / `parse_file_into_chunk_model_projection`。RAG indexing 现在直接通过 `ParseGateway` 生成 `CanonicalDocumentIR`，再使用 `build_index_handoff_payload(document).vector_documents` 生成 canonical dict payload，并写入 Milvus / optional Elasticsearch。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready，也不声明全仓 `ChunkModel` DTO 已退休。旧 RAG doc_parser、历史服务和部分兼容测试仍可使用 `ChunkModel`，但 Knowledge pipeline 默认 parse/rag/graph 入口已退出 ChunkModel projection；2026-08-02 后续切片也已移除 `chunk_projection_adapter.py` export surface。

## Implemented

- `src/backend/zuno/platform/services/pipeline/manager.py` 新增 `_parse_rag_index_documents`，使用 `knowledge.pipeline.rag_index.canonical_handoff` parser config。
- `run_rag_index_stage` 改为消费 canonical `vector_documents` handoff 生成 dict payload，不再生成 `ChunkModel`。
- `src/backend/zuno/platform/services/rag/vector_db/milvus_lite_client.py` 支持 dict 或旧对象 chunk-like payload。
- `src/backend/zuno/platform/services/rag/es_client.py` 支持 dict 或旧 `to_dict()` payload，并移除生产写入端对 `ChunkModel` 的类型导入。
- `src/backend/zuno/knowledge/ingestion/vector_payload.py` 后续承接 canonical vector payload 生成，供 pipeline / rebuild / eval 默认入口复用。
- `tests/storage/test_pipeline.py::test_pipeline_rag_stage_uses_canonical_handoff_without_chunk_projection` 验证 RAG stage 传递 canonical dict payload。
- `tests/storage/test_pipeline.py::test_milvus_lite_client_accepts_canonical_dict_chunks` 与 `tests/storage/test_pipeline.py::test_es_client_accepts_canonical_dict_chunks` 验证 Milvus / ES dict payload 兼容。

## Still Open

- `src/backend/zuno/platform/services/rag/parser.py` 与 `src/backend/zuno/platform/services/rag/doc_parser/**` 仍保留旧 `ChunkModel` parser 兼容实现。
- Fixed benchmark 仍是 `BLOCKED / blocked_not_measured`。
- Program 仍不能归档，`.agent/programs/` 不能恢复 no-active。

## Verification

```powershell
python -m pytest -q tests/storage/test_pipeline.py::test_pipeline_rag_stage_uses_canonical_handoff_without_chunk_projection tests/storage/test_pipeline.py::test_milvus_lite_client_accepts_canonical_dict_chunks tests/storage/test_pipeline.py::test_es_client_accepts_canonical_dict_chunks -p no:cacheprovider --tb=short
python -m pytest -q tests/storage/test_pipeline.py::test_pipeline_manager_updates_task_and_file_state tests/storage/test_pipeline.py::test_pipeline_graph_stage_uses_canonical_handoff_without_chunk_projection -p no:cacheprovider --tb=short
python -m pytest -q tests/api/test_layered_api_boundaries.py -p no:cacheprovider --tb=short
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
python tools/scripts/verify_current_program.py
```
