# PHASE12 Closure / Archive / Commit / Push

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE12_closure-archive-commit-push
mode: closure

## 目标

完成 Program 3 closure：归档 PHASE01-PHASE12、写 closure summary、把 `.agent/programs/` 切回 no-active 或打开下一 program 前的等待状态、运行最终验证、提交并推送。

## 范围

- 写 `closure-summary.md`。
- 归档到 `docs/history/programs/zuno-enterprise-ingestion-async-infrastructure-v1/`。
- 更新 latest completed program。
- 确认 Program 4-6 queued 状态。
- 最终验证、commit、push。

## 禁止范围

- 不跳过 workflow / docs self-review。
- 不把未实现外部服务写成 Current。
- 不 force push、不 amend、不 reset。
- 不删除 Program 1 / Program 2 归档。

## 验收闸门

- Program 3 closure summary 明确列出 completed Current、remaining Target、blocked evidence、verification results。
- `.agent/programs/` 状态一致。
- `docs/history/programs/zuno-enterprise-ingestion-async-infrastructure-v1/` 包含 README、current、roadmap、closure checklist、closure summary 和 PHASE01-PHASE12。
- 最终验证通过。
- commit 和 push 成功。

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
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_ingest_async_runtime.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## 需要先读取

- `.agent/programs/closure-checklist.md`
- 所有 Program 3 PHASE 文件
- `docs/architecture/production-readiness.md`
- verifier outputs
- `git status --short --branch`

## 需要修改的文件

- `.agent/programs/`
- `docs/history/programs/zuno-enterprise-ingestion-async-infrastructure-v1/`
- `.agent/references/current-program.md`
- `AGENTS.md`
- `README.md`
- architecture docs / mirrors
- verifier / repo tests as needed

## 执行拆解

1. 完成 workflow / docs self-review。
2. 写 closure summary。
3. 复制归档文件。
4. 切换 `.agent/programs/` 状态。
5. 运行最终验证。
6. `git status` 审查。
7. commit。
8. push。

## 多 agent 分工

- Closure Agent：审 archive completeness。
- Verification Agent：跑最终验证。
- Integration Reviewer Agent：审 diff 和 Current / Target 边界。

## 需要返回的证据

- closure summary 路径。
- archive 文件清单。
- 验证命令与结果。
- commit hash。
- push status。
- 未完成项和 blocked evidence。

## 停止条件

- 最终验证失败且无法定位根因。
- 推送被网络或权限阻塞。
- 发现未说明的用户修改。
- closure summary 需要把 Target 写成 Current 才能通过。
