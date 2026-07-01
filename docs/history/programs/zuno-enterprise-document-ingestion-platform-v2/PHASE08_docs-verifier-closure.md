# PHASE08 Docs / Verifier / Closure

status: completed
program: zuno-enterprise-document-ingestion-platform-v2
phase: PHASE08_docs-verifier-closure
mode: docs-verifier-archive

## 目标

把 Program 1B / V2 的 Current evidence 写入正式文档、Agent surfaces、verifier/tests 和 history archive，并把 `.agent/programs/` 切回 no-active。

## 范围

- `docs/architecture/*` 与 `.agent/architecture/*`。
- `README.md`、`AGENTS.md`、`.agent/references/current-program.md`、`.agent/references/code-map.md`。
- `.agent/programs/` current surfaces。
- repo verifier 和 repo tests。

## 禁止范围

- 不启动 Program 3。
- 不把 Postgres / Redis / MinIO / OCR / VLM / external index 写成 Current。
- 不删除 Program 1A 或 Program 1B history evidence。

## 验收闸门

- Program 1B / V2 archive 存在。
- `.agent/programs/` no-active。
- architecture Markdown / HTML mirrors 同步。
- required verifier 和 focused tests 通过。

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

## 需要先读取

- `AGENTS.md`
- `.agent/references/current-program.md`
- `.agent/references/verification-map.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`

## 需要修改的文件

- Program archive and current surfaces。
- Architecture docs and mirrors。
- Repo verifier/tests for no-active state。

## 执行拆解

1. 写 Program 1B / V2 archive。
2. 更新 no-active current surfaces。
3. 更新 architecture Current / Target 边界。
4. 运行 render architecture。
5. 更新 verifier/tests。
6. 跑 closure validation。

## 多 agent 分工

主线程直接执行；未拆子线程。

## 需要返回的证据

- verification command results。
- archive path。
- commit / push evidence。

## 停止条件

- verifier 要求把未实现生产能力写成 Current。
- push 失败且 OpenSSL fallback 也失败。

## PHASE08 Evidence

本文件在 closure 阶段更新。最终验证结果以 `closure-summary.md` 和提交记录为准。

