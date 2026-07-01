# Program Closure Checklist

state: active
active_program: `zuno-production-document-ingestion-and-thread-foundation-v1`
current_phase: `PHASE07_program2-thread-prompts-and-branch-plan.md`
latest_completed_program: `zuno-production-architecture-and-deliverables-completion-v1`

## Program 1 收口目标

- [x] PHASE01 完成 parser current audit，列出 supported / fallback / target-blocked 格式。
- [x] PHASE01 明确 workspace ingest 是否仍绕过 `ParseGateway`，并给出 `_document_from_file()` / `workspace_text_runtime` gap evidence。
- [x] PHASE02 冻结 Document IR、document version、source hash、parser config hash、schema version、parser adapter contract 和 parser capability matrix。
- [x] PHASE03 完成本地 parser worker / job lifecycle / retry / metrics / snapshot / idempotency，并把 outbox / lease / reconciler 保留为 Target。
- [x] PHASE04 完成 native text / structured parser 强化和 focused tests。
- [x] PHASE05 完成 PDF / Office / OCR / VLM enrichment adapter boundary、fallback、network / privacy / budget gate 和 blocked evidence。
- [x] PHASE06 完成 index handoff、manifest provenance、ACL、parse job lineage、citation lineage、golden fixtures。
- [ ] PHASE07 写入 Program 2 thread prompts、branch/worktree plan 和合并闸门。
- [ ] PHASE08 完成验证、文档同步、自维护审查、归档和下一轮状态交接。

## 必须保留的边界

- [ ] Program 1 只把真实可验证能力写成 Current。
- [ ] 生产 parser worker、深度 OCR/layout/table/code extraction、外部 index service 没接入前仍是 Target。
- [ ] Program 2-4 是 queued program，不是当前 active program。
- [ ] Codex 多线程施工不写成 Zuno 产品 runtime 多 Agent 架构。
- [ ] Basic RAG / Static GraphRAG 只作为评测 baseline，不写成最终产品模式。
- [ ] 生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index 和 reconciler 没有代码证据前仍是 Target。

## 文档同步检查

- [ ] `.agent/programs/current.md` 与当前 phase 一致。
- [ ] `.agent/programs/implementation-roadmap.md` 覆盖 Program 1-4 的顺序、依赖和验收。
- [ ] `.agent/programs/queued-programs/` 中 Program 2-4 计划仍是 queued，不含 active 状态。
- [ ] `.agent/references/current-program.md` 与 `.agent/programs/current.md` 一致。
- [ ] `AGENTS.md` 和 README 当前 program 摘要一致。
- [ ] `docs/architecture/document-ingestion-foundation.md` 与 Program 1 phase evidence 一致。
- [ ] verifier / repo tests 已覆盖 active program 文件清单、phase section、queued program 边界。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## 归档要求

Program 1 完成后必须整体归档到：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

归档必须包含：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `closure-summary.md`
- PHASE01-PHASE08 文件
- Program 2 thread prompts 或提示词生成记录
- 验证命令和结果
- commit / push evidence
