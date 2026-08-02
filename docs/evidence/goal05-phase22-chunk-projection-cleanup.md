# Goal05 PHASE22 Chunk Projection Cleanup Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-01
branch: codex/goal05-phase22-chunk-projection-cleanup
base_branch: main
base_sha: a8eecacbe72a1f612f6a3e2f396ed7f083cfbfc7
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的历史窄切片：生产源码中的 `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` 已退役。2026-08-02 后续切片已把 workspace attachment、Knowledge pipeline parse/rag/graph stages、RAG rebuild script 与 fixed/local eval 入口继续推进为直接消费 Canonical IR / canonical handoff，并删除 `chunk_projection_adapter.py` export surface；详见 `docs/evidence/goal05-phase22-workspace-attachment-ir-cutover.md`、`docs/evidence/goal05-phase22-pipeline-parse-ir-cutover.md`、`docs/evidence/goal05-phase22-pipeline-graph-ir-cutover.md`、`docs/evidence/goal05-phase22-pipeline-rag-ir-cutover.md` 与 `docs/evidence/goal05-phase22-rag-eval-ir-cutover.md`。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready。

## Implemented

- `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` 已退役；后续 `src/backend/zuno/knowledge/ingestion/chunk_projection_adapter.py` 也已退役。
- `src/backend/zuno/platform/services/workspace/attachment_service.py` 曾在本切片改为 `parse_file_into_chunk_model_projection`；后续已改为直接走 `ParseGateway` / `CanonicalDocumentIR.blocks`，不再依赖 ChunkModel projection。
- `src/backend/zuno/platform/services/pipeline/manager.py` 的 parse stage 后续已改为直接走 `ParseGateway` / `CanonicalDocumentIR.blocks`。
- `src/backend/zuno/platform/services/pipeline/manager.py` 的 graph stage 后续已改为直接走 canonical `graphrag_documents` handoff。
- `src/backend/zuno/platform/services/pipeline/manager.py` 的 RAG indexing 后续已改为直接走 canonical `vector_documents` handoff；pipeline 默认路径不再使用 projection。
- `src/backend/zuno/knowledge/ingestion/__init__.py` 后续只导出 canonical vector payload helper，不再导出 chunk projection adapter 常量与函数。
- `.agent/programs/work-products/phase22-removal-candidates.yaml` 把 `legacy_cutover.py` 从 `active_candidate` 改为 `resolved_retired`，并把剩余 blocker 缩小为 ChunkModel projection retirement。
- `tools/scripts/verify_phase22_cleanup_boundary.py` 后续改为要求 `chunk_projection_adapter.py` 不存在，并检查 canonical vector payload helper。

## Still Open

- 旧 RAG doc_parser / ChunkModel DTO compatibility 已在后续 PHASE22 cleanup 切片退役，见 `docs/evidence/goal05-phase22-rag-parser-dto-retirement.md`。
- `src/backend/zuno/agent/core/agents/general_agent.py` 仍是 PHASE22 removal candidates 中唯一 `active_candidate`。
- Fixed benchmark 仍是 `BLOCKED / blocked_not_measured`。
- Program 仍不能归档，`.agent/programs/` 不能恢复 no-active。

## Verification

```text
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
python -m pytest -q tests/knowledge/test_legacy_cutover_adapter.py tests/repo/test_phase22_cleanup_boundary_allowlist.py tests/repo/test_phase11_legacy_upload_parser_cutover.py -p no:cacheprovider
python -m pytest -q tests/storage/test_pipeline.py::test_pipeline_manager_updates_task_and_file_state -p no:cacheprovider -vv --tb=short
rg -n "legacy_cutover|parse_file_into_legacy_chunks|canonical_ir_to_legacy_chunks|LEGACY_ADAPTER|temporary\.adapter\.phase11\.legacy_chunk_projection" src/backend/zuno
rg --files src/backend/zuno | rg "(^|/)(legacy|legacy_|.*_legacy)(/|\.)|legacy_aliases"
```

预期结果：两个 verifier 通过；相关 focused tests 通过；两个 production source 搜索均无命中。

