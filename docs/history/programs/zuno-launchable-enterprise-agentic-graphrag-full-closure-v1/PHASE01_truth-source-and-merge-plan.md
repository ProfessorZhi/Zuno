# PHASE01 Truth Source And Merge Plan

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE01_truth-source-and-merge-plan
status: completed

## 目标

把原 active Program 3 与 queued Program 4-6 合并成一个 active mega program，并冻结执行模型：一个总 Program、十五个 Phase Gate、多条并行 Workstream、多个 PR / commit、一个 Coordinator 统一合并、验证和归档。

## 范围

- 确认当前 branch、worktree、Program 1 / 2 archive、原 Program 3 active state 和原 Program 4-6 queued state。
- 更新 `.agent/programs/current.md`、`implementation-roadmap.md`、`closure-checklist.md`、`README.md`。
- 将原 Program 4-6 标注为 `superseded_by` / `merged_into`，保留为历史输入，不写成 completed。
- 建立 owner map、shared file map、workstream map、PR / commit 分组和停止条件。

## 目标架构拼接点

本 phase 不实现 runtime，但要把后续所有 phase 的拼接方式写清楚：

- Input / Async Infrastructure 拼到 Document & User Input Layer。
- Knowledge / Retrieval / GraphRAG 拼到 Knowledge Capability。
- Memory & Context Engine 拼到 Agent Core 的上下文入口。
- Capability / Skill / Tool / MCP 拼到 Capability Layer。
- Model Gateway / Cost 拼到 Model Gateway。
- Planning / ReAct / Reflection / Replan / Reflexion 拼到 Planning & Control Runtime。
- Security / Trace / Eval 拼到 Governance / Trace / Eval Envelope。
- Product API / Frontend Sync 拼到 AgentChat / Workspace 产品入口。

PHASE01 的输出不是代码，而是后续 workstream 的施工蓝图：谁改哪些文件、哪些 contract 先冻结、哪些共享文件只能 Coordinator 改、哪些测试证明可以合并。

## 并行开发可行性

本 phase 必须串行，由 Coordinator 独占。原因是 program state、phase 文件清单、roadmap、README、AGENTS、verifier 和 repo tests 都是共享真相源；如果多个 agent 同时改，会造成 active state 漂移。

本 phase 结束后允许并行的前提：

- PHASE02 共享契约已列出所有 cross-workstream contract。
- 每条 workstream 有不重叠 allowed paths。
- `workspace_task_runtime.py`、`schema/workspace.py`、README、AGENTS、architecture.md、production-readiness.md、current.md、roadmap 归 Coordinator 管。
- 子线程只能在独立 worktree / branch 上工作，且每条线以 focused tests 作为合并条件。

## 详细执行卡

- 输入依赖：当前 `current.md`、roadmap、queued Program 4-6、Program 1/2 closure summary、目标架构文档和 AGENTS 工作流规则。
- 主要交付物：mega program open 状态、merge map、owner map、shared file lock map、phase gate 清单、workstream 边界和 PR / commit 分组建议。
- 可并行工作包：本 phase 本身不并行实现；可以让只读 reviewer 并行检查 Program 4-6 的 scope 是否完整映射到 15 个 phase。
- Coordinator 锁点：`current.md`、roadmap、queued marker、closure checklist、README、AGENTS、architecture summary 只能由 Coordinator 改。
- 下游交接：PHASE02 必须拿到稳定的 phase 列表、共享文件锁和 contract owner；PHASE03-PHASE13 只能在 PHASE02 冻结 contract 后启动。
- PR / commit 建议：`docs(program): open launchable agentic graphrag mega program`，仅包含 program 状态和计划文件，不混入 runtime 代码。

## 禁止范围

- 不启动 runtime 代码实现。
- 不把 PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index 写成 Current。
- 不改写 Program 1 / Program 2 历史归档事实。
- 不把 Codex 多线程工程执行写成 Zuno 产品 runtime 多 Agent。

## 验收闸门

- `.agent/programs/current.md` 指向 `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1` 和本 phase。
- roadmap 明确 Program 1 / 2 completed、Program 3 Mega active、原 Program 3-6 merged_into mega program。
- phase 文件清单为 PHASE01-PHASE15。
- queued Program 4-6 文件仍存在，但状态不再是 queued active pipeline。

## 验证命令

```powershell
git status --short --branch
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## 需要先读取

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/queued-programs/*.md`
- `.agent/references/current-program.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/closure-summary.md`
- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/closure-summary.md`

## 需要修改的文件

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/PHASE01_truth-source-and-merge-plan.md`
- `.agent/programs/queued-programs/*.md`
- `.agent/references/current-program.md`
- `README.md`
- `AGENTS.md`
- verifier / repo tests that pin current active program state

## 执行拆解

1. 读取 current truth source 和 closure summaries。
2. 写明 merged program map：原 Program 3/4/5/6 -> Program 3 Mega。
3. 写明 phase gate sequence：PHASE01-PHASE15。
4. 写明 workstream owner map 和 shared file conflict map。
5. 写明 PR / commit 分组。
6. 更新 verifier / repo tests 中 active program 与 phase 文件清单。

## 多 agent 分工

- Coordinator 独占本 phase。
- Subagent 只能只读审计 verifier 与 program state，不得直接修改共享文件。
- 若需要多线程执行，完整提示词必须另存 `.agent/programs/thread-prompts/`，且必须先确认真实 Codex UI 目标模式和独立 worktree。

## 需要返回的证据

- 当前 branch 和 commit。
- program merge map。
- phase 文件清单。
- verifier / repo tests 更新清单。
- 验证命令和结果。

## Closure Evidence

- 当前 branch：`codex/zuno-truth-source-production-readiness-baseline`。
- 当前 commit：`ec020e86`。
- Program merge map 已在 `current.md`、`implementation-roadmap.md`、README、AGENTS、`.agent/references/current-program.md` 和 queued program 文件中固定：原 Program 3 / 4 / 5 / 6 均合并进 Program 3 Mega。
- phase 文件清单已固定为 PHASE01-PHASE15；PHASE01 关闭后 PHASE02 成为 active shared contract freeze gate。
- queued Program 4-6 文件保留在 `.agent/programs/queued-programs/`，状态为 `superseded` / `merged_into`，不是 active，也不是 completed evidence。
- PHASE01 关闭前验证通过：`git diff --check`、`python tools/scripts/verify_docs_entrypoints.py`、`python tools/scripts/verify_repo_structure.py`、`python .agent/scripts/verify_agent_system.py`、`python .agent/scripts/verify_doc_boundaries.py`、`powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`。

## 停止条件

- worktree 出现用户未说明改动。
- Program 1 / Program 2 closure facts 与当前文件冲突。
- verifier 要求启动 runtime 实现才能让文档自洽。
- 任何文档把未实现外部服务写成 Current。
