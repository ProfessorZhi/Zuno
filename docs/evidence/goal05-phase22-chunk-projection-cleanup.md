# Goal05 PHASE22 Chunk Projection Cleanup Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-01
branch: codex/goal05-phase22-chunk-projection-cleanup
base_branch: main
base_sha: a8eecacbe72a1f612f6a3e2f396ed7f083cfbfc7
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的一个窄切片：把生产源码中的 `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` 退役，迁入明确的 `src/backend/zuno/knowledge/ingestion/chunk_projection_adapter.py`，并把 workspace attachment 与 knowledge pipeline 的默认调用入口从 `parse_file_into_legacy_chunks` 改为 `parse_file_into_chunk_model_projection`。2026-08-02 后续切片已把 workspace attachment、Knowledge pipeline parse/rag/graph stages 再推进为直接消费 Canonical IR / canonical handoff，详见 `docs/evidence/goal05-phase22-workspace-attachment-ir-cutover.md`、`docs/evidence/goal05-phase22-pipeline-parse-ir-cutover.md`、`docs/evidence/goal05-phase22-pipeline-graph-ir-cutover.md` 与 `docs/evidence/goal05-phase22-pipeline-rag-ir-cutover.md`。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready，不声明 ChunkModel projection 已退休。

## Implemented

- `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` 物理迁移为 `src/backend/zuno/knowledge/ingestion/chunk_projection_adapter.py`。
- Adapter id 从 `temporary.adapter.phase11.legacy_chunk_projection` 改为 `versioned.adapter.phase22.chunk_model_projection`。
- `src/backend/zuno/platform/services/workspace/attachment_service.py` 曾在本切片改为 `parse_file_into_chunk_model_projection`；后续已改为直接走 `ParseGateway` / `CanonicalDocumentIR.blocks`，不再依赖 ChunkModel projection。
- `src/backend/zuno/platform/services/pipeline/manager.py` 默认 parse / rag index / graph stage chunk projection 入口改为 `parse_file_into_chunk_model_projection`。
- `src/backend/zuno/platform/services/pipeline/manager.py` 的 parse stage 后续已改为直接走 `ParseGateway` / `CanonicalDocumentIR.blocks`；RAG/Graph indexing 仍使用 projection。
- `src/backend/zuno/platform/services/pipeline/manager.py` 的 graph stage 后续已改为直接走 canonical `graphrag_documents` handoff；RAG indexing 仍使用 projection。
- `src/backend/zuno/platform/services/pipeline/manager.py` 的 RAG indexing 后续已改为直接走 canonical `vector_documents` handoff；pipeline 默认路径不再使用 projection。
- `src/backend/zuno/knowledge/ingestion/__init__.py` 只导出新的 chunk projection adapter 常量与函数。
- `.agent/programs/work-products/phase22-removal-candidates.yaml` 把 `legacy_cutover.py` 从 `active_candidate` 改为 `resolved_retired`，并把剩余 blocker 缩小为 ChunkModel projection retirement。
- `tools/scripts/verify_phase22_cleanup_boundary.py` 改为检查新 adapter，并在生产源码扫描中不再允许旧 `legacy_cutover.py` 通过 active allowlist。

## Still Open

- `ChunkModel` projection adapter 仍存在，但 workspace attachment 默认路径和 Knowledge pipeline parse/rag/graph stages 已经退出该 projection；剩余 cleanup 是旧 RAG doc_parser / ChunkModel DTO compatibility 和未使用 projection adapter export surface。
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

