# Current Program Reference

state: active
active_program: zuno-canonical-architecture-runtime-realization-v1
current_phase: PHASE01
phase_count: 22
program_version: 2

当前唯一 active Program 是十一模块新架构完整实现与旧架构迁移总计划。

2026-07-16 已撤回 PHASE01–04 的旧完成结论。已有基础产物保留为部分实现证据，但必须按完整目标范围重新关闭；不得以最小闭环、局部测试或后续 Phase 补齐替代当前 Phase Completion。

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
- 当前状态为 `partial implementation available / measurement blocked / quality not yet proven`。

## 最近完成 Program

`zuno-real-unified-runtime-cutover-v1` 已归档到：

```text
docs/history/programs/zuno-real-unified-runtime-cutover-v1/
```

其本地实现基线是本 Program 的 Current 输入，不是新 Target 已全部实现的证明。
