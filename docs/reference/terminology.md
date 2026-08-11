# 术语表

## 用途

保持公开架构术语稳定、简短。详细 Target Contract 放在当前 `docs/project/architecture/` 和 `docs/project/<topic>/` 正式文档；旧 `docs/project/modules/` 只作 Superseded 迁移材料。

## 状态标签

- Current：当前代码和测试已经证明。
- Foundation：已有最小可调用 slice，但还不是成熟产品行为。
- Target：近期目标架构，尚未完全实现。
- Future：更长期方向，例如 Java services、microservices、event-driven workers、product-level multi-agent mode、Coding Agent mode。
- History：被替换但保留证据价值的历史材料。
- 受限历史兼容：应退出前台路径，但仍有迁移、DB、eval 或 retirement test 依赖。

## 当前术语

- `GeneralAgent single loop`：当前知识问答会话主线。
- `KnowledgeQueryService`：application knowledge query service，位于 application boundary。
- `GraphRAGQueryService`：GraphRAG Project query runtime。
- `GraphRAGProjectSnapshot`：查询时不可变 project/config snapshot。
- `KnowledgeQueryResult`：包含 answer、documents、evidence、citation、version 和 trace 的结果模型。

## Target Runtime 术语

- Memory Engine
- Capability and Tool Retrieval
- GraphRAG entity extraction and retrieval fusion
- GeneralAgent LangGraph runtime
- Product boundary, Trace and Eval
- Context / Memory Engine
- Summary Compression
- Structured Extraction
- ToolCard
- Capability / Tool Retrieval
- Native BM25
- Optional vector tool search
- Multi-query retrieval
- Multi-retriever recall
- RRF fusion
- Optional rerank
- GraphRAG Project
- Basic / Local / Global / DRIFT query methods
- `auto` router
- Evidence / Citation / Trace / Eval

## 术语边界

- Native BM25：本地 BM25 排序算法。Elasticsearch 可以作为 external adapter 提供 BM25 scoring，但 Elasticsearch 不是算法本体。
- ToolCard：tool、MCP connector、skill 或 knowledge capability 的可检索轻量元数据，不是完整注入的 tool schema。
- RRF fusion：粗融合方法，默认 `k = 60`；启用时后面可接 optional rerank。
- `auto` router：选择 `basic`、`local`、`global` 或 `drift`，不是第五种 GraphRAG query mode。
- External Knowledge：RAG / GraphRAG / file / web evidence，不是 Agent Memory。

## 退休术语

- Domain Pack
- `domain_pack_id`
- `DomainQAGraph`
- `MultiAgentSupervisorGraph`

这些不属于当前运行时、API 或架构入口。
