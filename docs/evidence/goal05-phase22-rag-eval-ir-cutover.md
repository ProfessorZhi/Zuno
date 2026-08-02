# Goal05 PHASE22 RAG Eval Canonical IR Cutover Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-02
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的一个窄切片：RAG rebuild script、stackless local eval 与 multihop real-runtime eval 不再调用旧 `doc_parser` / `ChunkModel` parser 路径。默认评测与重建入口改为 `ParseGateway` / Canonical IR / canonical vector payload dict。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready。旧 `src/backend/zuno/platform/services/rag/parser.py` 与 `doc_parser/**` 已在后续 PHASE22 cleanup 切片退役。

## Implemented

- 新增 `src/backend/zuno/knowledge/ingestion/vector_payload.py`，把 `CanonicalDocumentIR` 的 `vector_documents` handoff 转为 Milvus / ES 可消费的 canonical dict payload。
- `tools/scripts/rebuild_rag_indexes.py` 改为通过 `ParseGateway` 解析下载后的本地文件，再调用 `canonical_ir_to_vector_payloads`。
- `tools/evals/zuno/rag_eval/run_stackless_local_eval.py` 改为通过 `ParseGateway` 解析 prepared corpus，并用 dict chunk store / Graph extractor。
- `tools/evals/zuno/multihop_eval/run_real_runtime_eval.py` 的 synthetic corpus 直接生成 canonical-shaped dict payload，不再构造 `ChunkModel`。
- `src/backend/zuno/knowledge/ingestion/chunk_projection_adapter.py` 与旧 adapter test 已退役。

## Still Open

- 旧 RAG doc_parser / ChunkModel DTO compatibility 已在后续 PHASE22 cleanup 切片退役；history service 已在后续切片改为 canonical dict payload。
- Fixed benchmark 仍是 `BLOCKED / blocked_not_measured`。
- Program 仍不能归档，`.agent/programs/` 不能恢复 no-active。

## Verification

```powershell
python -m py_compile tools/scripts/rebuild_rag_indexes.py tools/evals/zuno/rag_eval/run_stackless_local_eval.py tools/evals/zuno/multihop_eval/run_real_runtime_eval.py src/backend/zuno/knowledge/ingestion/vector_payload.py
python -m pytest -q tests/storage/test_pipeline.py::test_pipeline_rag_stage_uses_canonical_handoff_without_chunk_projection tests/storage/test_pipeline.py::test_milvus_lite_client_accepts_canonical_dict_chunks tests/storage/test_pipeline.py::test_es_client_accepts_canonical_dict_chunks -p no:cacheprovider --tb=short
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
python tools/scripts/verify_phase22_cleanup_boundary.py
```
