# 术语表

## 用途

保持公开架构术语稳定、简短。详细 target contract 放在 `.agent/architecture/near-term/`。

## 状态标签

- Current：当前代码和测试已经证明。
- Foundation：已有最小可调用 slice，但还不是成熟产品行为。
- Target：近期目标架构，尚未完全实现。
- Future：更长期方向，例如 Java services、microservices、event-driven workers、product-level multi-agent mode、Coding Agent mode。
- History：被替换但保留证据价值的历史材料。
- 受限历史兼容：应退出前台路径，但仍有迁移、DB、eval 或 retirement test 依赖。

## 当前术语

- `GeneralAgent single loop`：当前知识问答会话主线。
- `KnowledgeQueryService`：application knowledge query service，Phase 11A 引入，并在 Target Runtime V2 中移动到 application boundary。
- `GraphRAGQueryService`：GraphRAG Project query runtime。
- `GraphRAGProjectSnapshot`：查询时不可变 project/config snapshot。
- `KnowledgeQueryResult`：包含 answer、documents、evidence、citation、version 和 trace 的结果模型。

## 目标运行时 V2 术语

- 目标运行时 V2 Phase 05：记忆引擎
- 目标运行时 V2 Phase 06：能力与工具检索
- 目标运行时 V2 Phase 07：GraphRAG LLM 实体抽取与知识检索融合
- 目标运行时 V2 Phase 08：GeneralAgent LangGraph 运行时
- 目标运行时 V2 Phase 09：产品边界、Trace 与 Eval 收口
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

这些只应出现在迁移兼容、历史档案、DB 兼容、eval CLI 兼容或 retirement tests 中。
