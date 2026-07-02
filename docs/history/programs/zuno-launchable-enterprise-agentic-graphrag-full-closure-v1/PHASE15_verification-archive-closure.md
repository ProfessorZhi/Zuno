# PHASE15 Verification Archive Closure

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE15_verification-archive-closure
status: completed

## 目标

完成 full verification、closure summary、archive、no-active state、commit 和 push，把 Program 3 Mega 归档为 launchable enterprise Agentic GraphRAG product baseline。

## 范围

- 运行完整 verifier、repo guardrails、runtime focused tests、E2E tests、eval tests。
- 写 `closure-summary.md`。
- 归档到 `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`。
- `.agent/programs/` 回到 `no-active`，或明确等待下一 program。
- commit and push。

## 目标架构拼接点

本 phase 不再新增功能，而是证明所有拼接点都已经闭环：

- Input -> Knowledge -> Memory -> Capability -> Planning -> Security -> Eval -> Product API -> Docs。
- 每条 workstream 都有 focused tests。
- E2E 证明整条 product runtime path 可运行。
- Trace / Eval / Cost 证明质量、成本和耗时可观测。
- Docs / Archive 证明 Current / Target / Production Scale 边界清楚。

closure summary 必须用证据说话，不能用“还很远”或“应该可以”的泛化话术。

## 并行开发可行性

本 phase 必须由 Coordinator 串行收口。各 workstream 只能修自己路径内的验证失败，不能直接改 archive、current.md 或 closure summary。

可并行：

- Workstream owners 修各自 failing tests。
- Coordinator 并行读取各 workstream report。

不可并行：

- 多个 agent 同时改 `.agent/programs/current.md`。
- 多个 agent 同时写 `closure-summary.md`。
- 未跑完整验证就 commit / push。

## 详细执行卡

- 输入依赖：PHASE01-PHASE14 全部 evidence、focused tests、E2E output、trace/eval/cost metrics、docs render、workflow self-review。
- 主要交付物：full verification log、closure-summary.md、history archive、no-active current state、commit and push evidence、remaining Production Scale targets。
- 可并行工作包：verification log collection、archive draft、workflow self-review 可并行准备；最终 closure wording、state flip、commit/push 只能 Coordinator 做。
- Coordinator 锁点：不得用未跑通的 tests 声称 completed；不得把 external deployments 写成 Current；不得保留 active/queued 状态冲突。
- 下游交接：这是本 mega program 的最终出口；后续 program 只能从 archived closure summary 和 no-active state 开始。
- PR / commit 建议：`docs: close launchable enterprise agentic graphrag baseline`，最终 commit 必须包含 archive、state、docs、verifier 同步。

## 禁止范围

- 不在未验证通过时写 completed。
- 不把 remaining production deployment targets 写成架构缺口。
- 不 force push、不 reset、不 amend。
- 不删除 Program 1 / Program 2 归档 evidence。

## 验收闸门

- `.agent/programs/` 回到 no-active。
- mega program 完整归档。
- closure summary 写清 Completed Product Baseline、Current evidence、Focused tests、E2E scenario、Metrics captured、Remaining production deployment targets。
- final report 写：`Launchable enterprise Agentic GraphRAG product baseline completed; production scale external deployments remain replaceable targets.`

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
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
pytest -q tests/api -p no:cacheprovider
pytest -q tests/evals -p no:cacheprovider
```

## Closure Evidence

- PHASE15 关闭前已从 clean worktree 运行 full verification：repo verifiers、workflow verifier、focused durable ingest/task tests、knowledge suite、agent suite、api suite 和 eval suite 均通过。
- 完整归档已写入 `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`，包含 `README.md`、`current.md`、`implementation-roadmap.md`、`closure-checklist.md`、`closure-summary.md`、PHASE01-PHASE15 文件和 merged queued inputs。
- `.agent/programs/` 已回到 no-active：只保留 `current.md`、`README.md`、`implementation-roadmap.md`、`closure-checklist.md` 和 `queued-programs/README.md`。
- `closure-summary.md` 写清 Completed Product Baseline、Current evidence、Focused tests、E2E scenario、Metrics captured 和 Remaining Production Scale targets。
- 本地目标要求 no push / no PR unless explicitly requested，因此本 phase 的本地 closure commit 不执行 push；push 仍等待用户明确请求。

## 需要先读取

- all PHASE01-PHASE15 files
- `.agent/programs/closure-checklist.md`
- verification outputs
- E2E trace/eval/cost reports
- docs updated in PHASE14

## 需要修改的文件

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/**`
- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/references/current-program.md`
- README / AGENTS if final state changes

## 执行拆解

1. Run full verification from clean current state.
2. Fix any failing verifier/test from root cause.
3. Write closure summary with evidence.
4. Archive program files.
5. Set active program state to no-active.
6. Run verification again.
7. Commit and push.

## 多 agent 分工

- Coordinator owner。
- Workstream owners can fix failures in their allowed paths only。
- Coordinator reviews final diff, archive, verification and git state。

## 需要返回的证据

- branch。
- commit hash。
- push status。
- active program closure status。
- modified files list。
- per-workstream completion summary。
- full verification command results。
- E2E scenario results。
- remaining production scale targets。
- worktree clean status。

## 停止条件

- verifier 失败且根因不明。
- E2E 链路无法在 local implementation 下运行。
- security / citation / blocked OCR 被 fake success 掩盖。
- worktree 出现用户未说明改动。
