# 目标架构

## 用途

这份文档描述近期目标架构。它是目标状态，不是当前完成声明。

## 总目标

Zuno 的近期目标是：

```text
现在保持 monorepo，近期形成模块化单体，未来具备服务拆分条件
```

核心目标模型：

```text
Local-first Agent Workspace
= Single GeneralAgent Runtime
+ Context / Memory Engine
+ Capability / Tool Retrieval
+ Knowledge / GraphRAG Retrieval
+ Evidence / Citation / Trace / Eval
+ Typed API + Web/Desktop
```

目标 runtime 图见：

- [diagrams.md](diagrams.md)

## 分层架构

近期目标用六个主层表达，Trace / Eval / Policy 作为横切治理层贯穿每个主层：

1. API 层：FastAPI routes、DTO、Auth、SSE、typed request / response 和 Application Services。
2. Agent 层：Single GeneralAgent Runtime，目标形态是 `prepare_context -> agent_loop -> post_turn_commit`。
3. Memory 层：L0 Working Context、L1 Recent Window、L2 Task Summary、L3 Structured Long-term Memory、L4 External Knowledge boundary、Raw Event Log。
4. Capability 层：ToolCard Registry、keyword / alias search、Native BM25 over ToolCards、optional vector search、permission / health / cost filter、CapabilitySelectionTrace。
5. Knowledge 层：`KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot`、LLM-first entity / relation extraction、`basic`、`local`、`global`、`drift`、`auto` router、retrieval / fusion / evidence。
6. Platform 层：PostgreSQL、Redis、RabbitMQ、MinIO、Milvus、Neo4j、optional Elasticsearch adapter、model gateway、storage、background jobs。

横切治理层：Evidence / Citation / Trace / Eval / Policy。它记录 trace_id、evidence bundle、citation coverage、latency、cost、permission decision、fallback reason 和 eval profile，但不单独拥有业务入口。

## 记忆目标边界

- 目标策略是 Summary Compression + Structured Extraction。
- Sliding Window 只用于 L1 recent-window 和 token-budget 保护。
- summaries 和 structured memories 必须保留 `source_event_ids`。
- Summary 不能替代 Raw Event Log。
- External Knowledge 是 RAG / GraphRAG / file / web evidence，不是 Agent Memory。
- Prompt Caching 是 compute-layer hint，不是 memory compression。

## 检索目标边界

- Native BM25 是本地 BM25 排序算法。
- Elasticsearch 只是可选外部 adapter，不是 BM25 算法本体。
- GraphRAG 实体抽取默认主路径是 LLM 抽取，不是规则匹配或正则表达式。
- 知识库配置必须能选择 `graph_index_settings.entity_extraction_mode = llm`、`model_refs.entity_extraction_llm_id`、prompt / schema version、cost / latency policy 和 eval profile，用于 GraphRAG entity / relation extraction。
- 规则、正则和词典只用于日期、金额、条款号等确定格式辅助、preprocessing、fallback 或 baseline test。
- enhanced path 可以生成 query variants，但必须保留 original query。
- multi-retriever recall 可使用 Native BM25、Dense Vector、Graph Local 和 Community Global。
- deduplication 使用稳定 id，例如 `chunk_id`、`document_id + span`、`graph_node_id`、`community_report_id`。
- RRF 是默认 coarse fusion，默认 `k = 60`，后面可接 optional rerank。
- `auto` 是 router，用来选择 `basic`、`local`、`global` 或 `drift`，不是第五种 GraphRAG query mode。

## 替换方向

```text
Domain Pack front path -> GraphRAG Project
domain_pack_id target name -> graphrag_project_id
rag_graph_deep -> Enhanced Mode plus query_method
local_graphrag -> local
community_global -> global
drift_like -> drift
```

## 仓库前台目标

- `docs/` 只保留正式人类真相：当前架构、目标架构、路线图、ADR、证据、术语和 history index。
- `.agent/` 只保留本地 Agent Skill System：active program、target design、references skills、templates 和过渡期 verifier。
- `docs/history/` 保存旧 lessons、old phases、retired plans、replaced fragments、completed programs、旧 audits/specs/runbooks/prototypes。
- transient screenshots、browser snapshots、caches 和 local reports 不进入提交的前台路径。
- 新增或重写的前台文档使用中文；历史档案可保留原文。

## 非近期目标

- Java business services
- microservice extraction
- event-driven workers
- product-level multi-agent mode
- Coding Agent mode
- independent GraphRAG or indexing services

## 与 Current 的硬边界

这些内容即使出现在目标设计里，也不能写成 Current：

- 完整 `prepare_context -> agent_loop -> post_turn_commit` LangGraph runtime。
- 生产级 Memory DB、成熟 memory extraction / retrieval / consolidation。
- 产品级动态 Capability Selector。
- 完整 frontend trace 面板。
- Java、微服务、事件驱动 worker 或产品级多 Agent 模式。

Domain Pack 只保留为历史或迁移兼容语境；公开目标身份字段是 `graphrag_project_id`。

## 执行边界

本文件不承担 active program、active phase 或 queued program 的执行入口。当前状态、下一步和队列顺序以 [roadmap.md](roadmap.md) 为正式人类入口；Agent 执行计划以 `.agent/programs/` 为准。

目标架构进入 Current 的条件是：对应代码、测试、trace evidence 和文档边界都已证明；否则保持 Target。

## 详细设计

详细目标设计放在：

- `.agent/architecture/near-term/`
- `.agent/architecture/future/`
- `.agent/architecture/decisions/`

Canonical Target / Proposed visual blueprint：

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`

Canonical near-term Markdown：

- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`

只有已实现并通过测试证明的结论，才能从 `.agent/` 提升到正式 `docs/`。
