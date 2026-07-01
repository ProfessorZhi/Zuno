# PHASE08 Verification、Docs Sync 与 Closure

status: planned
program: zuno-production-document-ingestion-and-thread-foundation-v1

## 目标

完成 Program 1 的验证、文档同步、自维护审查、归档和下一轮状态交接。PHASE08 只在 PHASE01-PHASE07 都有证据时关闭。

## 范围

- 运行 Program 1 focused tests 和 workflow verifiers。
- 更新 README、AGENTS、`.agent/references/current-program.md`、verification map 和必要 repo tests。
- 更新 `docs/architecture/document-ingestion-foundation.md`、`docs/architecture/production-readiness.md` 和总架构入口引用，确保 Current / Remaining Target / blocked evidence 不漂移。
- 写 closure summary。
- 归档 Program 1 到 `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`。
- 选择下一状态：打开 Program 2 或回到 no-active。

## 禁止范围

- 不跳过失败测试直接归档。
- 不把 Program 2-4 写成 completed。
- 不把未实现的 production parser / external index / OCR / eval 写成 Current。
- 不强推、不 reset、不改旧提交。

## 验收闸门

- PHASE01-PHASE07 status 与 evidence 完整。
- `.agent/programs/` 状态与 `.agent/references/current-program.md` 一致。
- Program 1 archive 包含 README、current、roadmap、closure-checklist、closure-summary、PHASE01-PHASE08。
- focused tests、workflow verifier 和 repo tests 通过，或有明确 blocked evidence。
- closure summary 必须单独列出：Current local runtime slice、Remaining Target infrastructure、target-blocked parser / OCR / VLM evidence、workspace ingest -> ParseGateway 闭环证据。
- git commit 和 push 完成，或阻塞原因明确。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
```

## 需要先读取

- PHASE01-PHASE07 文件和 evidence。
- `.agent/references/workflow.md`
- `.agent/references/verification-map.md`
- `docs/architecture/document-ingestion-foundation.md`
- `docs/architecture/production-readiness.md`
- `docs/history/programs/README.md`

## 需要修改的文件

- `.agent/programs/PHASE08_verification-doc-sync-and-closure.md`
- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/references/current-program.md`
- `README.md`
- `AGENTS.md`
- `docs/architecture/document-ingestion-foundation.md`
- `docs/architecture/production-readiness.md`
- verifier / repo tests needed for final state
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/**`

## 执行拆解

1. 检查 PHASE01-PHASE07 是否都已 completed 或 blocked-with-evidence。
2. 运行 focused parser / index tests。
3. 运行 workflow verifiers。
4. 修复文档和 verifier 漂移。
5. 写 closure summary，列出 Current、Remaining Target、blocked evidence、workspace ingest -> ParseGateway 证据和未接生产基础设施。
6. 归档 Program 1。
7. 决定下一状态：active Program 2 或 no-active。
8. 提交并推送。

## 多 agent 分工

- 可用 subagent 做只读 self-review。
- 可用 subagent 做只读 diff / docs consistency review。
- 主线程负责最终验证、归档、commit 和 push。

## 需要返回的证据

- PHASE01-PHASE08 status。
- 修改文件列表。
- 验证命令与结果。
- closure summary path。
- archive path。
- commit hash。
- push status。

## 停止条件

- PHASE01-PHASE07 有未解释的 incomplete。
- focused tests 或 verifier 失败且根因不明。
- 需要真实外部服务才能满足 closure。
- git push 被网络或认证阻塞。
