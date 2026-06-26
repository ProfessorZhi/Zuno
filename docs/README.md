# Zuno 文档入口

`docs/` 是 Zuno 面向人的正式文档入口，只保留当前仍会影响判断的核心文档。

## 边界

- 当前事实、目标架构、路线图、正式决策、精选证据和术语表放在这里。
- Agent 工作流、可复用提示、脚本和执行辅助放在 `.agent/`。
- 过时计划、旧阶段、旧审计、旧规格、旧 runbook、旧 UI 原型和被替换设计归档到 `docs/history/`。
- 历史档案保留证据价值，不再作为默认阅读路径。
- 前台文档默认使用中文；历史档案可保留原文。

## 首读路径

1. [仓库 README](../README.md)
2. [当前架构](./architecture/current-architecture.md)
3. [目标架构](./architecture/target-architecture.md)
4. [路线图](./architecture/roadmap.md)
5. [公开演示证据](./evidence/public-demo.md)
6. [Eval Baseline](./evidence/eval-baselines.md)
7. [术语表](./reference/terminology.md)

## 目录

- [architecture/](./architecture/README.md)：当前架构、目标架构、路线图和正式 ADR。
- [evidence/](./evidence/README.md)：精选证据入口。
- [reference/terminology.md](./reference/terminology.md)：仍然有效的公共术语。
- [history/](./history/README.md)：历史档案，包含旧计划、旧规格、旧审计、旧 runbook 和被替换材料。

## 清理规则

如果一个文档不再改变当前决策，把它移动到 `docs/history/`，并更新引用。不要把旧材料留在前台路径里制造“当前仍有效”的错觉。
