# Goal05 PHASE22 Knowledge Pipeline Parse Canonical IR Cutover Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-02
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的一个窄切片：Knowledge pipeline 的 `run_parse_stage` 不再为了 parse count 调用 `parse_file_into_chunk_model_projection`。Parse stage 现在直接调用 `ParseGateway` / `ParseDocumentRequest`，生成 `CanonicalDocumentIR` 后以 `CanonicalDocumentIR.blocks` 记录 parse count 和 stage detail。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready。2026-08-02 后续切片已把 `run_graph_stage`、`run_rag_index_stage`、RAG rebuild script 与 fixed/local eval 入口继续推进到 Canonical IR / canonical handoff；旧 RAG doc_parser / ChunkModel DTO 已在后续 PHASE22 cleanup 切片退役。

## Implemented

- `src/backend/zuno/platform/services/pipeline/manager.py` 新增 `_parse_document`，直接通过 `ParseGateway.parse_document` 生成 `CanonicalDocumentIR`。
- `run_parse_stage` 使用 `_parse_document`，从 non-empty `CanonicalDocumentIR.blocks` 计算 count。
- parse stage detail 记录 `projection=canonical_document_ir_blocks`、`parser_id` 和 `document_version_id`。
- RAG/Graph indexing 后续已退出 `_parse_chunks`；parse stage 仍保持直接消费 Canonical IR blocks。
- `tests/storage/test_pipeline.py::test_pipeline_parse_stage_uses_canonical_ir_without_chunk_projection` 用失败替身证明 parse stage 不调用 `parse_file_into_chunk_model_projection`。
- `tests/api/test_layered_api_boundaries.py::test_knowledge_pipeline_parse_stage_uses_canonical_ir_before_chunk_projection` 记录默认边界：parse/rag/graph stages 均已 Canonical IR / canonical handoff。

## Still Open

- 旧 RAG doc_parser / ChunkModel DTO 兼容实现已在后续 PHASE22 cleanup 切片退役。
- Fixed benchmark 仍是 `BLOCKED / blocked_not_measured`。
- Program 仍不能归档，`.agent/programs/` 不能恢复 no-active。

## Verification

```powershell
python -m pytest -q tests/storage/test_pipeline.py::test_pipeline_parse_stage_uses_canonical_ir_without_chunk_projection tests/storage/test_pipeline.py::test_pipeline_manager_updates_task_and_file_state -p no:cacheprovider --tb=short
python -m pytest -q tests/api/test_layered_api_boundaries.py -p no:cacheprovider --tb=short
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
python tools/scripts/verify_current_program.py
```
