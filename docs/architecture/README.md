# 架构文档

这里是 Zuno 的正式架构入口，只保留当前判断需要的前台文档。

## 首读

1. [当前架构](current-architecture.md)
2. [目标架构](target-architecture.md)
3. [路线图](roadmap.md)
4. [架构图](diagrams.md)
5. [公开证据](../evidence/public-demo.md)
6. [架构决策](decisions/README.md)

## 当前执行程序

当前可执行 Agent program 是：

- `.agent/programs/`

当前没有 active program。`zuno-workflow-doc-system-v1` 和 `zuno-target-architecture-refresh-v1` 已完成并归档。

下一候选 program 是 `zuno-repo-layout-cleanup-v1`，仍在 queued draft 中。

后续 queued programs 存放在：

- `.agent/architecture/future/programs/`

顺序是：仓库目录整理、runtime 架构升级、架构 HTML / Mermaid 展示收口。

已完成或被替换的程序都归档在：

- `docs/history/programs/`

其中：

- `docs/history/programs/zuno-target-architecture-migration-v1/` 是已完成的 V1 迁移闭环。
- `docs/history/programs/official-graphrag-cleanup-v1/` 是已完成的 GraphRAG 清理证据。
- `docs/history/programs/zuno-target-runtime-v2/` 保存已被当前 program 替换的目标运行时 V2 历史材料。
- `docs/history/programs/zuno-architecture-surface-cleanup-v1/` 保存上一轮成熟项目封面化 program。
- `docs/history/programs/zuno-workflow-doc-system-v1/` 保存已完成的本地文档系统和工作流 program。
- `docs/history/programs/zuno-target-architecture-refresh-v1/` 保存已完成的目标架构升版 program。

## 当前前台结构

```text
docs/architecture/
  README.md
  current-architecture.md
  target-architecture.md
  roadmap.md
  diagrams.md
  decisions/
```

过时审计、旧规格、旧 phase、旧计划和旧 runbook 不再放在 `docs/architecture/` 前台，统一归档到 `docs/history/`。

## 边界

- Current：仓库现在真实已经做到的行为，只写代码和测试已经证明的事实。
- Target：近期目标，不等于已经实现；完整 LangGraph runtime、生产级 Memory DB 和完整 frontend trace 都属于这里。
- Roadmap：当前状态、下一步、非目标和 Phase 执行顺序。
- Diagrams：Current Runtime、Target Runtime 和 Maintenance Workflow 的简图，图中 Current / Target 必须分开。
- Decisions：仍影响主线的正式架构决策。
- History：完成或被替换的计划、程序、阶段、审计、规格和旧 Agent 工作流材料。

`AGENTS.md` 是仓库级 Agent 入口；`.agent/` 是本地 Agent Skill System；正式结论进入 `docs/`。
