# Program Closure Checklist

state: no-active
active_program: none
current_phase: none
latest_completed_program: `zuno-production-document-ingestion-and-thread-foundation-v1`

## Program 1 收口结果

- [x] PHASE01 完成 parser current audit，列出 supported / fallback / target-blocked 格式。
- [x] PHASE01 明确 workspace ingest 曾绕过 `ParseGateway`，并给出 `_document_from_file()` / `workspace_text_runtime` gap evidence。
- [x] PHASE02 冻结 Document IR、document version、source hash、parser config hash、schema version、parser adapter contract 和 parser capability matrix。
- [x] PHASE03 完成本地 parser worker / job lifecycle / retry / metrics / snapshot / idempotency，并把 outbox / lease / reconciler 保留为 Target。
- [x] PHASE04 完成 native text / structured parser 强化和 focused tests。
- [x] PHASE05 完成 PDF / Office / OCR / VLM enrichment adapter boundary、fallback、network / privacy / budget gate 和 blocked evidence。
- [x] PHASE06 完成 index handoff、manifest provenance、ACL、parse job lineage、citation lineage、golden fixtures。
- [x] PHASE07 写入 Program 2 thread prompts、branch/worktree plan 和合并闸门。
- [x] PHASE08 完成 workspace ingest -> ParseGateway 闭环、验证、文档同步、自维护审查、归档和 no-active 状态交接。

## 当前边界

- [x] Program 1 只把真实可验证能力写成 Current。
- [x] 生产 parser worker、深度 OCR/layout/table/code extraction、外部 index service 没接入前仍是 Target。
- [x] Program 2-4 是 queued program，不是当前 active program。
- [x] Codex 多线程施工不写成 Zuno 产品 runtime 多 Agent 架构。
- [x] Basic RAG / Static GraphRAG 只作为评测 baseline，不写成最终产品模式。
- [x] 生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index 和 reconciler 没有代码证据前仍是 Target。

## 文档同步检查

- [x] `.agent/programs/current.md` 与 no-active 状态一致。
- [x] `.agent/programs/implementation-roadmap.md` 覆盖 Program 1-4 的顺序、依赖和验收。
- [x] `.agent/programs/queued-programs/` 中 Program 2-4 计划仍是 queued，不含 active 状态。
- [x] `.agent/references/current-program.md` 与 `.agent/programs/current.md` 一致。
- [x] `AGENTS.md` 和 README 当前 program 摘要一致。
- [x] `docs/architecture/document-ingestion-foundation.md` 与 Program 1 closure evidence 一致。
- [x] verifier / repo tests 覆盖 no-active 文件清单、latest completed archive、queued program 边界和 Program 1 archive。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_answers_from_ingested_index_with_citations -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
```

## 归档位置

Program 1 已整体归档到：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

归档包含：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `closure-summary.md`
- PHASE01-PHASE08 文件
- `thread-prompts/`
- 验证命令和结果
- commit / push evidence 占位
