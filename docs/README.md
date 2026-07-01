# Zuno 文档入口

`docs/` 是 Zuno 面向人的正式文档入口，只保留当前仍会影响判断的核心文档。前台文档默认使用中文；历史档案可以保留原文。

## 首读路径

1. [仓库 README](../README.md)
2. [总架构文档](./architecture/architecture.md)
3. [Production Readiness Baseline](./architecture/production-readiness.md)
4. [架构 HTML](./architecture/architecture.html)
5. [公开演示证据](./evidence/public-demo.md)
6. [Eval Baseline](./evidence/eval-baselines.md)
7. [术语表](./reference/terminology.md)
8. [历史档案](./history/README.md)

## 当前目录

- [architecture/](./architecture/README.md)：当前总架构 Markdown、生产成熟度基线、生成 HTML、正式 ADR 和附件。
- [evidence/](./evidence/README.md)：精选证据入口。
- [reference/terminology.md](./reference/terminology.md)：仍然有效的公共术语。
- [history/](./history/README.md)：历史档案，包含旧计划、旧规格、旧审计、旧 runbook 和被替换材料。

## 清理规则

如果一个文档不再改变当前决策，把它移动到 `docs/history/`，并更新引用。不要把旧材料留在前台路径里制造“当前仍有效”的错觉。

本轮架构前台瘦身归档在：

- `docs/history/architecture-surface-cleanup-2026-06-30/`
