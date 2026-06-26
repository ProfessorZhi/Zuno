# 架构决策摘要

这个目录只保留 Agent 侧当前仍有用的轻量决策摘要。正式 ADR 放在 `docs/architecture/decisions/`。

## 当前文件

- [Architecture Decisions](architecture-decisions.md)

## 作用

`decisions/` 用来回答“为什么”：

- 为什么近期仍保留 monorepo。
- 为什么同步聊天主路径只进入一个 GeneralAgent。
- 为什么 GraphRAG 是 Knowledge Capability，不是第二套聊天 runtime。
- 为什么按 phase 的执行计划放在 `.agent/programs/`，不放在 `.agent/architecture/`。

旧决策碎片已归档到：

- `docs/history/agent-architecture-decision-fragments/`
