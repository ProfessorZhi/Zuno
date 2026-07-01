# Program Closure Checklist

state: no-active
active_program: none
current_phase: none
latest_completed_program: `zuno-enterprise-document-ingestion-platform-v2`

## Program 2 收口结果

- [x] PHASE01 完成 truth source and gap audit。
- [x] PHASE02 完成 durable storage contract。
- [x] PHASE03 完成 `/workspace/file` source object 和 workspace file metadata durable closure。
- [x] PHASE04 完成 parse job、snapshot、document version、document blocks 和 blocked diagnostics persistence。
- [x] PHASE05 完成 index manifest、index chunk、citation lineage persistence 和 fresh runtime rehydrate。
- [x] PHASE06 完成 task、events、artifact content/ref 和 feedback durable closure。
- [x] PHASE07 完成 restart recovery focused E2E。
- [x] PHASE08 完成 docs / verifier / archive closure。

## Current 边界

- [x] Program 2 只把真实可验证能力写成 Current。
- [x] Postgres、Redis、MinIO / S3、outbox、worker lease、external OCR / VLM、external index 和 reconciler 仍是 Target / Production Scale Target。
- [x] Program 3-5 是 queued program，不是当前 active program。
- [x] Codex 多线程施工不写成 Zuno 产品 runtime 多 Agent 架构。

## 文档同步检查

- [x] `.agent/programs/current.md` 与 no-active 状态一致。
- [x] `.agent/programs/implementation-roadmap.md` 覆盖 Program 1-5 顺序。
- [x] `.agent/programs/queued-programs/` 中 Program 3-5 计划仍是 queued。
- [x] `.agent/references/current-program.md` 与 `.agent/programs/current.md` 一致。
- [x] `AGENTS.md` 和 README 当前 program 摘要一致。
- [x] `docs/architecture/document-ingestion-foundation.md` 与 Program 2 closure evidence 一致。
- [x] verifier / repo tests 覆盖 no-active 文件清单、latest completed archive 和 queued program 边界。

## 验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/knowledge -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## 归档位置

Program 2 已整体归档到：

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`

归档包含：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `closure-summary.md`
- PHASE01-PHASE08 文件
