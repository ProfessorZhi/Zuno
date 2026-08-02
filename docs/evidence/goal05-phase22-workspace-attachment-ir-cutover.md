# Goal05 PHASE22 Workspace Attachment Canonical IR Cutover Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-02
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的一个窄切片：workspace 文档附件默认路径不再调用 `parse_file_into_chunk_model_projection`，也不再加载 `chunk_projection_adapter` 或 `ChunkModel`。该路径现在直接通过 `ParseGateway` / `ParseDocumentRequest` 生成 `CanonicalDocumentIR`，再从 `CanonicalDocumentIR.blocks` 生成 prompt excerpt。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready，也不声明全仓 `ChunkModel` 已退休。Knowledge pipeline 的 RAG/Graph 下游仍有 `ChunkModel` consumer，由 PHASE16/PHASE22 后续 cleanup 继续处理。

## Implemented

- `src/backend/zuno/platform/services/workspace/attachment_service.py` 文档附件路径改为直接调用 `ParseGateway.parse_document`。
- 文档附件 parser config 使用 `product.workspace_attachment.canonical_ir`，明确 owner、consumer 和 projection。
- `_extract_attachment_text` 直接从 `CanonicalDocumentIR.blocks` 提取文本，不再先生成 `ChunkModel`。
- `tests/api/test_workspace_attachment_canonical_ir.py` 验证真实文本附件可通过 Canonical IR 提取，并用失败替身证明 `parse_file_into_chunk_model_projection` 不会被调用。
- `tests/api/test_layered_api_boundaries.py` 新增静态 guard，禁止 workspace attachment 默认路径重新引入 `chunk_projection_adapter` / `ChunkModel`。
- `tools/scripts/verify_phase11_legacy_upload_parser_cutover.py` 与 cutover inventory 同步为 `canonical_ir_default_no_chunk_projection`。

## Still Open

- Knowledge pipeline parse/rag/graph、RAG rebuild script 与 fixed/local eval 入口已在后续切片退出 ChunkModel projection。
- 旧 RAG doc_parser / ChunkModel DTO compatibility 仍作为非默认兼容残留存在。
- Fixed benchmark 仍是 `BLOCKED / blocked_not_measured`。
- Program 仍不能归档，`.agent/programs/` 不能恢复 no-active。

## Verification

```powershell
python -m pytest -q tests/api/test_workspace_attachment_canonical_ir.py tests/api/test_layered_api_boundaries.py -p no:cacheprovider --tb=short
python -m pytest -q tests/agent/test_workspace_usage_agent_name.py -p no:cacheprovider --tb=short
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
python tools/scripts/verify_phase22_completion_blockers.py
```
