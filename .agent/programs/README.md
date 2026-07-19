# Agent 执行计划

`.agent/programs/` 当前承载一个 active 总 Program：

```text
zuno-canonical-architecture-runtime-realization-v1
```

该 Program 负责把十一模块 Target 架构完整迁移为 Runtime Current，包括后端、PostgreSQL、RabbitMQ、Object Store、LangGraph Checkpointer、Security、Observability、Agent Core、Agentic GraphRAG、Tool Effect、Web/Desktop、故障恢复、Benchmark、切流和旧路径删除。

## 当前状态

- State: active
- Current phase: `PHASE08`
- Program version: 2
- Phase count: 22
- Atomic Work Packages: 163
- Execution mode: full-scope / runtime-first / vertical-slice checkpoints / evidence-gated
- Implementer target: Codex GPT-5.5 medium，单次只执行一个 Work Package

2026-07-19 PHASE11 Durable Ingestion and Source Lineage 已完成 Coordinator Closure。PHASE05、PHASE06、PHASE07、PHASE11 completed；PHASE08 ready；PHASE12 仍 planned，PHASE09–22 不得提前提升为 Current。

## 必读文件

```text
current.md
implementation-roadmap.md
task-execution-contract.md
codex-medium-runbook.md
legacy-to-target-migration-map.md
canonical-directory-contract.md
program-manifest.yaml
当前 PHASENN_*.md
closure-checklist.md
```

## 使用规则

1. Coordinator 选择一个 `ready` Work Package。
2. Codex 只读取 Runbook 指定的最小文件集，不重新推导整个架构。
3. 每个任务使用独立 Worktree 和 `codex/<task-id>-<slug>` Branch。
4. Implementer 只能提交 `completion_candidate`；Phase `completed` 由 Coordinator 审核后更新。
5. 最小 Vertical Slice 只能作为中间检查点，不能代替当前 Phase 的完整范围、失败恢复和真实依赖证明。
6. 架构能力不得为了节省 Token、时间或测试而删减，也不得把剩余范围无条件推给后续 Phase。
7. 只新增接口、类型、表、Mock、README、Fixture 或未来目录不能关闭 Runtime Task。
8. Readiness/Evidence 仍为 `completion_candidate` 或 Coordinator Approval 仍为 `pending` 时，Manifest 不得写 `completed`。
9. blocked、unavailable、incomparable 和未运行验证必须如实报告。
10. 兼容桥只允许存在于迁移期；PHASE22 后生产源码零 Legacy 文件夹、零 alias registry、零永久双路径。
11. Program 完成后整体归档到 `docs/history/programs/zuno-canonical-architecture-runtime-realization-v1/`，不得拆成多个竞争的 active Program。
