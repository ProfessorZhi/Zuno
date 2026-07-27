# Current Program Reference

state: active
active_program: zuno-canonical-architecture-runtime-realization-v1
current_phase: PHASE10
phase_count: 22
program_version: 2

当前唯一 active Program 是十一模块新架构完整实现与旧架构迁移总计划。

2026-07-20 Goal01 audit 曾将 PHASE11 从 completed 重新打开为 in_progress；2026-07-23 的 0b1e087a closure 与 PR #41 初版 Goal02 final closure 被本轮目标订正为不足证据。Goal02 final closure repair 已恢复传输并通过有限 Closure Review：PHASE05 completed，PHASE06 completed，PHASE07 completed；PHASE08 completed；PHASE11 completed。

Goal03 Backend Platform Expansion 已通过 Wave A 和 Wave B Gate：PHASE09、PHASE12、PHASE13、PHASE14、PHASE15 completed；PHASE10、PHASE16 ready；当前执行入口为 PHASE10。Goal03 completed；production readiness not established。

Goal04 PR B 已启动：PHASE16 Tool Side Effect and Reconciliation 在 `codex/goal04-phase16-tool-side-effect` 中为 `in_progress`，当前 evidence 覆盖 P16-T01 至 P16-T18 focused slices。这不是 completed 证据；PHASE17、PHASE18、PHASE19 仍受依赖约束，不得提前标记 in_progress。

入口：

```text
.agent/programs/current.md
.agent/programs/implementation-roadmap.md
.agent/programs/task-execution-contract.md
.agent/programs/codex-medium-runbook.md
.agent/programs/legacy-to-target-migration-map.md
.agent/programs/program-manifest.yaml
.agent/programs/closure-checklist.md
.agent/programs/PHASE01_*.md ... PHASE22_*.md
```

## 目标

- 把十一模块 Target 完整转成 Runtime Current。
- 完成 PostgreSQL、RabbitMQ、Object Store、LangGraph Checkpointer 和 Alembic 迁移。
- 完成 Single Controller、Dynamic DAG、Agentic GraphRAG、Memory、Capability、Tool Runtime、Security、Observability/Eval。
- 完成 Product Backend、Web 和 Desktop Contract/Projection/SSE 适配。
- 完成 Fault、E2E、Fixed Benchmark、Cutover、Legacy Removal 和归档。

## 执行规则

- 使用 Codex GPT-5.5 medium 时，一次只执行一个 Work Package。
- 任务上下文由 Phase 文件和 Minimal Read Set 提供，不重新推导全部架构。
- 降低 Token 不能降低架构、故障、安全、恢复或测试要求。
- 最小 Vertical Slice 只能作为中间证据，不能关闭 Phase。
- 每个任务使用独立 Worktree/Branch，完成真实代码、Migration、测试、证据、Commit 和 Push。
- 当前状态为 `implementation available / measurement blocked / production readiness not established`。

## 最近完成 Program

`zuno-real-unified-runtime-cutover-v1` 已归档到：

```text
docs/history/programs/zuno-real-unified-runtime-cutover-v1/
```

其本地实现基线是本 Program 的 Current 输入，不是新 Target 已全部实现的证明。
