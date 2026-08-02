# Goal05 PHASE22 RAG Parser / Chunk DTO Retirement Evidence

日期：2026-08-02

## 结论

本证据记录 PHASE22 cleanup 的一个收口切片：旧 RAG `parser.py`、`doc_parser/**`、`zuno.api.dto.chunk.ChunkModel` 与 `normalize_legacy_chunks_to_ir` 已从生产源码和活跃测试入口退役。默认 RAG indexing、Graph indexing、rebuild、eval、history write 与相关测试均使用 `ParseGateway`、`CanonicalDocumentIR`、canonical handoff 或 canonical dict payload。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready。PHASE22 仍需 fixed benchmark、full final verification、production readiness decision 与 program archive。

## 代码边界

- 删除 `src/backend/zuno/platform/services/rag/parser.py`。
- 删除 `src/backend/zuno/platform/services/rag/doc_parser/**`。
- 删除 `src/backend/zuno/api/dto/chunk.py`。
- 删除 `src/backend/zuno/knowledge/ingestion/normalizer.py`，并从 `zuno.knowledge.ingestion.__all__` / lazy exports 移除 `normalize_legacy_chunks_to_ir`。
- `tools/scripts/verify_model_gateway_boundaries.py` 不再扫描已退休 parser 文件。

## 测试与验证边界

- `tests/api/test_layered_api_boundaries.py::test_platform_rag_uses_canonical_imports` 禁止旧 RAG parser/doc_parser 路径恢复。
- `tests/knowledge/test_parse_gateway_runtime.py` 验证 legacy chunk normalizer 不再导出。
- `tests/storage/test_pipeline.py` 与 `tests/repo/test_phase5_graphrag_index_filters.py` 使用 canonical dict payload 覆盖 GraphExtractor、hash、source_chunk_id 与 graph refresh 合约。
- `tests/evals/test_rag_eval_metrics.py` 使用 `ParseGateway` + `canonical_ir_to_vector_payloads` 覆盖 eval chunk id 稳定性。

## 剩余未完成

- fixed benchmark 仍是 measurement blocked / not measured。
- 正式四 profile runtime decision、full final verification、Production Readiness 判定与 Program archive 仍未完成。
