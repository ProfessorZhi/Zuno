# Architecture Specs

这个目录只保留面试前真正需要的稳定架构文档。

目标不是文档越多越好，而是主线越清楚越好。

## 保留原则

保留的文档必须至少满足下面一个条件：

- 定义 LangGraph 主运行时边界
- 定义 GraphRAG / Domain Pack 主线
- 定义检索控制面与治理层
- 定义本地评测与自动化测试主线
- 定义分层架构、目录结构和未来扩展边界

已经被主线吸收、但不再值得单独保留的主题：

- knowledge capability / query policy
- 单独的 GraphRAG 合同场景说明
- 单独的 multi-agent future 方向说明

## 当前保留的核心文档

1. [Platform Evolution And Future Direction](./platform-evolution-and-future-direction.md)
2. [Domain Pack + LangGraph + GraphRAG Architecture](./domain-pack-langgraph-graphrag-architecture.md)
3. [LangGraph Runtime](./langgraph-runtime.md)
4. [Retrieval Orchestrator](./retrieval-orchestrator.md)
5. [Enterprise Retrieval Governance](./enterprise-retrieval-governance.md)
6. [RAG Evaluation And Observability](./rag-evaluation-and-observability.md)
7. [Layered Backend And Service Evolution](./layered-backend-and-service-evolution.md)

## 推荐阅读顺序

如果你要快速理解“面试前项目到底要做到什么程度”，建议按这个顺序读：

1. `platform-evolution-and-future-direction.md`
2. `domain-pack-langgraph-graphrag-architecture.md`
3. `langgraph-runtime.md`
4. `retrieval-orchestrator.md`
5. `enterprise-retrieval-governance.md`
6. `rag-evaluation-and-observability.md`
7. `layered-backend-and-service-evolution.md`

其中最后一篇不只是后端分层说明，也负责回答：

1. 面试前项目结构应该整理到什么程度
2. 当前为什么不建议立刻做激进目录大迁移
3. 未来如果继续演进到更完整 monorepo 结构，应保留哪些边界
