# Program Closure Checklist

state: completed
active_program: none
current_phase: none
latest_completed_program: `zuno-enterprise-document-ingestion-platform-v2`

## Program 1B / V2 收口结果

- [x] PHASE01 完成 truth source 与 gap audit，列出 Program 1A 之后的 durable ingestion 缺口。
- [x] PHASE02 用 TDD 固定最小 SQLModel / SQLite-compatible durable store contract。
- [x] PHASE03 将 `/workspace/file` 接入 source object、source hash、storage uri 和 workspace file metadata 持久化。
- [x] PHASE04 将 `ParseGateway.submit_parse_job()` 结果、parse snapshot、document version 和 document blocks 持久化。
- [x] PHASE05 持久化 index manifest、index chunks 和 citation lineage，并支持本地 index rehydrate。
- [x] PHASE06 持久化 workspace task、events、artifact content/ref 和 feedback。
- [x] PHASE07 证明 fresh service rehydrate 后仍可生成 cited artifact 并保留 feedback。
- [x] PHASE08 完成 docs、architecture mirror、verifier、repo tests、归档和 no-active closure。

## 当前边界

- [x] Program 1B / V2 只把真实可验证能力写成 Current。
- [x] 生产 parser worker、深度 OCR/layout/table/code extraction、外部 index service 没接入前仍是 Target。
- [x] Program 3-5 是 queued program，不是当前 active program。
- [x] Codex 多线程施工不写成 Zuno 产品 runtime 多 Agent 架构。
- [x] Basic RAG / Static GraphRAG 只作为评测 baseline，不写成最终产品模式。
- [x] 生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index 和 reconciler 没有代码证据前仍是 Target。

## 文档同步检查

- [x] `.agent/programs/current.md` 与 no-active 状态一致。
- [x] `.agent/programs/implementation-roadmap.md` 覆盖 Program 1A、Program 1B / V2 和 Program 3-5 的顺序、依赖和验收。
- [x] `.agent/programs/queued-programs/` 中 Program 3-5 计划仍是 queued，不含 active 状态。
- [x] `.agent/references/current-program.md` 与 `.agent/programs/current.md` 一致。
- [x] `AGENTS.md` 和 README 当前 program 摘要一致。
- [x] `docs/architecture/document-ingestion-foundation.md` 与 Program 1B / V2 closure evidence 一致。
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

Program 1B / V2 已整体归档到：

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`

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
