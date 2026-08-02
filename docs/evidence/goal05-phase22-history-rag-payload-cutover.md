# Goal05 PHASE22 History RAG Payload Cutover Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-02
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的一个窄切片：`HistoryService.save_es_documents` 与 `HistoryService.save_milvus_documents` 不再构造 `ChunkModel`，改为生成 canonical-shaped dict payload，并继续写入 ES / Milvus 兼容入口。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready。旧 RAG `parser.py` / `doc_parser/**` 已在后续 PHASE22 cleanup 切片退役，见 `docs/evidence/goal05-phase22-rag-parser-dto-retirement.md`。

## Implemented

- `src/backend/zuno/api/services/history.py` 移除 `from zuno.api.dto.chunk import ChunkModel`。
- 新增 `_history_chunk_payload`，输出 `chunk_id`、`content`、`file_id`、`knowledge_id`、`document_hash`、`chunk_hash`、`source_chunk_id`、`metadata` 等 dict 字段。
- `tests/api/test_history_canonical_payload.py` 验证 history RAG payload 形状。
- `tests/api/test_layered_api_boundaries.py` guard 禁止 history service 重新导入 `ChunkModel`。

## Still Open

- 旧 RAG doc_parser / ChunkModel DTO compatibility 已在后续 PHASE22 cleanup 切片退役。
- Fixed benchmark 仍是 `BLOCKED / blocked_not_measured`。
- Program 仍不能归档，`.agent/programs/` 不能恢复 no-active。

## Verification

```powershell
python -m pytest -q tests/api/test_history_canonical_payload.py tests/api/test_layered_api_boundaries.py::test_api_service_layer_uses_canonical_platform_imports -p no:cacheprovider --tb=short
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_current_program.py
```
