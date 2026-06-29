# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。当前前台已打开一个 active program；完成后必须整体归档到 `docs/history/programs/`，再回到等待态。

## 当前 Active Program

- Program: `zuno-eight-deliverables-full-realization-v1`
- State: active
- 执行模式：主线程目标模式，默认开启线程内多 agent 协作；不是多线程模式。
- 当前入口：[current.md](current.md)
- 总路线：[implementation-roadmap.md](implementation-roadmap.md)
- 收口闸门：[closure-checklist.md](closure-checklist.md)

## Phase 文件

- [PHASE01_program-boot-baseline.md](PHASE01_program-boot-baseline.md)
- [PHASE02_workflow-self-maintenance-system.md](PHASE02_workflow-self-maintenance-system.md)
- [PHASE03_architecture-docs-html-system.md](PHASE03_architecture-docs-html-system.md)
- [PHASE04_query-router-mode-policy.md](PHASE04_query-router-mode-policy.md)
- [PHASE05_context-builder-memory-system.md](PHASE05_context-builder-memory-system.md)
- [PHASE06_capability-toolcard-mcp-system.md](PHASE06_capability-toolcard-mcp-system.md)
- [PHASE07_hooks-evidence-trace-artifact-system.md](PHASE07_hooks-evidence-trace-artifact-system.md)
- [PHASE08_graphrag-knowledge-runtime-system.md](PHASE08_graphrag-knowledge-runtime-system.md)
- [PHASE09_runtime-upgrade-integration.md](PHASE09_runtime-upgrade-integration.md)
- [PHASE10_validation-release-closure.md](PHASE10_validation-release-closure.md)

## 历史边界

已完成 program 不在当前前台展开：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`
- `docs/history/programs/zuno-six-layer-internalization-v1/`

`.agent/architecture/future/programs/` 中的 queued drafts 只作为本轮 program 的输入参考，不是 active 执行入口。
