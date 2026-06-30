# 架构索引

## 默认阅读顺序

1. [架构工作集说明](README.md)
2. [Agent 侧总架构文档](overall-architecture.md)
3. [近期目标说明](near-term/README.md)
4. [目标运行架构](near-term/01-target-runtime-architecture.md)
5. [上下文与记忆架构](near-term/02-context-memory-architecture.md)
6. [能力、工具与检索架构](near-term/03-capability-tool-retrieval-architecture.md)
7. [知识、GraphRAG 与检索融合](near-term/04-knowledge-graphrag-retrieval-fusion.md)
8. [仓库边界与验收闸门](near-term/05-repository-boundaries-and-acceptance-gates.md)
9. [架构决策](decisions/architecture-decisions.md)
10. [未来方向](future/future-horizon.md)

## 重构规则

近期代码重构工作在读取正式 `docs/architecture/` 后，优先读取 `near-term/`。

近期目标主线是：

```text
Single GeneralAgent
  + Context/Memory
  + Capability/Tool Retrieval
  + Knowledge/GraphRAG
  + Retrieval/Fusion/Evidence
  + Trace/Eval
```

只有讨论 Java 业务服务、微服务、事件 worker、独立 GraphRAG/eval 服务或多 Agent 方向时，才读取 `future/`。这些方向不能变成近期验收闸门，除非用户明确打开未来方向实现程序。

`docs/architecture/overall-architecture.md` 是正式文字总架构文档。`.agent/architecture/overall-architecture.md` 是 Agent 侧总架构维护文档，必须与正式总架构文档保持一致。`docs/architecture/` 是正式文档真相。`.agent/architecture/` 是 Agent 侧详细目标设计库。
