# 架构文档

这里是 Zuno 的正式架构入口，只保留当前判断需要的前台文档。

## 首读

1. [当前架构](current-architecture.md)
2. [目标架构](target-architecture.md)
3. [路线图](roadmap.md)
4. [公开证据](../evidence/public-demo.md)
5. [架构决策](decisions/README.md)

## 当前执行程序

当前可执行 Agent program 是：

- `.agent/programs/`

它接在已完成的 Target Architecture Migration V1 closure 之后，按 Phase 05-09 落地目标 runtime。

已完成或被替换的程序都归档在：

- `docs/history/programs/`

其中：

- `docs/history/programs/zuno-target-architecture-migration-v1/` 是已完成的 V1 迁移闭环。
- `docs/history/programs/official-graphrag-cleanup-v1/` 是已完成的 GraphRAG 清理证据。
- `docs/history/programs/zuno-target-runtime-v2/` 保存 V2 已完成 Phase 00-04 的历史材料。

## 当前前台结构

```text
docs/architecture/
  README.md
  current-architecture.md
  target-architecture.md
  roadmap.md
  decisions/
```

过时审计、旧规格、旧 phase、旧计划和旧 runbook 不再放在 `docs/architecture/` 前台，统一归档到 `docs/history/`。

## 边界

- Current：仓库现在真实已经做到的行为。
- Target：近期目标，不等于已经实现。
- Roadmap：当前状态、下一步、非目标和 Phase 执行顺序。
- Decisions：仍影响主线的正式架构决策。
- History：完成或被替换的计划、程序、阶段、审计、规格和旧 Agent 工作流材料。

`AGENTS.md` 是仓库级 Agent 入口；`.agent/` 是 Agent 工作流库；正式结论进入 `docs/`。
