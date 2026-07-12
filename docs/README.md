# Zuno 文档入口

前台文档默认使用中文，承载当前正式结论；历史材料保留在 `docs/history/`，不删除、不改写成当前事实。

## 首读路径

- [目标总架构](./architecture/architecture.md)：重文字设计文档，说明“轻量实现、成熟设计”、十一逻辑模块、完整 Agent 闭环、Owner、Contract、状态、失败语义和验收。
- [Mermaid 图源](./architecture/architecture-views.md)：4+1、Views & Beyond 与 Zuno Product Core 共十类视图。
- [架构 HTML 展示](./architecture/architecture.html)：以 Mermaid 图为主的 Architecture Atlas。
- [模块设计](./modules/README.md)：十一个逻辑模块的实施级设计入口。
- [Production Readiness](./status/production-readiness.md)：当前状态、短期闭环、Measurement Blocked、Completed 和 Future Optional。
- [架构决策](./decisions/README.md)：仍影响当前主线的正式 ADR。
- [工程治理](./governance/repo-ownership-matrix.md)：代码 Owner、迁移边界和兼容路径。
- [公开证据](./evidence/public-demo.md)：精选可展示证据。
- [历史归档](./history/README.md)：过时计划、旧 Program 和历史证据。

```text
architecture/    总架构四个 canonical 文件
modules/         十一个逻辑模块设计
status/          Current 与差距
decisions/       ADR
governance/      工程与文档治理
evidence/        验证证据
history/         历史归档
```

## 当前模块设计

- [02 Input / Document Ingestion](./modules/02-input-document-ingestion.md)
- [03 Knowledge / Agentic GraphRAG](./modules/03-knowledge-agentic-graphrag.md)
- [05 Memory & Context](./modules/05-memory-context.md)
- [06 Agent Core / Planning & Control](./modules/06-agent-core-planning-control.md)
- [07 Capability / Skill](./modules/07-capability-skill.md)
- [10 Observability & Eval](./modules/10-observability-eval.md)

其余模块会按同一编号规则逐步细化。模块文档服从总架构，不得把 Target 冒充为 Current。