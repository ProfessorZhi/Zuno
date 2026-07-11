# Zuno 文档入口

前台文档默认使用中文，承载当前正式结论；历史材料保留在 `docs/history/`，不删除、不改写成当前事实。

## 首读路径

- [目标总架构](./architecture/architecture.md)：重文字设计文档，说明“轻量实现、成熟设计”、十一逻辑模块、完整 Agent 闭环、owner、contract、状态、失败语义和验收。
- [Mermaid 图源](./architecture/architecture-views.md)：4+1、Views & Beyond 与 Zuno Product Core 共十类视图，每类 Overall + Local 图。
- [架构 HTML 展示](./architecture/architecture.html)：以十类 Mermaid 图为主的 Architecture Atlas，适合项目介绍、答辩和关系梳理。
- [Production readiness](./architecture/production-readiness.md)：当前状态、短期闭环、measurement blocked、completed 和 Future Optional。
- [公开证据](./evidence/public-demo.md)：精选可展示证据。
- [历史归档](./history/README.md)：过时计划、旧 program 和历史证据。

```text
architecture.md        讲目标设计
architecture-views.md  维护图源
architecture.html      看图
production-readiness   看 Current
```

## 运行域专题

- [Document ingestion foundation](./architecture/document-ingestion-foundation.md)
- [Agent core runtime](./architecture/agent-core-runtime.md)
- [Memory and context engineering](./architecture/memory-and-context.md)
- [Capability and skill layer](./architecture/capability-and-skill-layer.md)
- [Agentic retrieval planner](./architecture/agentic-retrieval-planner.md)
- [Eval, observability and cost](./architecture/eval-observability-and-cost.md)
- [Input layer and document processing](./architecture/input-layer-and-document-processing.md)
- [Knowledge space product configuration](./architecture/knowledge-space-product-configuration.md)

这些专题文档服从十一逻辑模块和六个物理运行域，不承担完整目标架构设计；完整设计以 `architecture.md` 为准。
