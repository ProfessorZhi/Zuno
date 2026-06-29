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

近期目标后端闭环不是把 Zuno 改成默认多 Agent，而是让一个任务能从输入、检索、取证、生成到交付被完整解释：

```text
User task
  -> Typed API task / session
  -> Session Workspace
  -> Single GeneralAgent
  -> Capability Selector
  -> Web / structured data / GraphRAG-RAG adapter / uploaded file capabilities
  -> Evidence / Citation / Trace
  -> Answer / Markdown / PDF / Artifact
  -> SSE or WebSocket event stream
```

这个表达吸收 DeepSearchAgents 的工程优点：多来源检索、上传附件、任务产物、长任务观测和前后端闭环。但 Zuno 的目标身份仍是 Local-first Agent Workspace；Tavily、MySQL、RAGFlow 这类具体工具只能作为可替换 provider 或 adapter，不是 Zuno 的核心身份。

目标 runtime 图见：

- [diagrams.md](diagrams.md)

## 分层架构

近期目标用六个主层表达，Trace / Eval / Policy 作为横切治理层贯穿每个主层：

1. API 层：FastAPI routes、DTO、Auth、SSE / WebSocket event stream、typed request / response、task / session、upload、artifact list / download 和 Application Services。
2. Agent 层：Single GeneralAgent Runtime，目标形态是 `prepare_context -> agent_loop -> post_turn_commit`。Agent 负责规划、调用 capability、汇总 evidence 和生成回答或交付物；默认不拆成固定三助手。
3. Memory 层：L0 Working Context、L1 Recent Window、L2 Task Summary、L3 Structured Long-term Memory、L4 External Knowledge boundary、Raw Event Log。
4. Capability 层：ToolCard Registry、keyword / alias search、Native BM25 over ToolCards、optional vector search、permission / health / cost filter、CapabilitySelectionTrace。Web search、structured data connector、GraphRAG / RAG adapter、file reader、Markdown / PDF writer 都应表现为可选择能力，而不是硬编码成默认子智能体。
5. Knowledge 层：`KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot`、LLM-first entity / relation extraction、`basic`、`local`、`global`、`drift`、`auto` router、retrieval / fusion / evidence。公开网页、结构化查询结果、内部文档、上传文件都必须归一成 Evidence / Citation / Trace 后再进入 Agent。
6. Platform 层：PostgreSQL、Redis、RabbitMQ、MinIO、Milvus、Neo4j、optional Elasticsearch adapter、model gateway、session workspace、artifact store、connector config、storage、background jobs 和 observability。

横切治理层：Evidence / Citation / Trace / Eval / Policy。它记录 trace_id、evidence bundle、citation coverage、latency、cost、permission decision、fallback reason 和 eval profile，但不单独拥有业务入口。

## 多来源 Evidence Channel 目标边界

Zuno 可以学习 DeepSearchAgents 的 Tavily / MySQL / RAGFlow / 上传附件分工，但在目标架构里应使用 Zuno 自己的通用边界：

| DeepSearchAgents 例子 | Zuno 目标边界 | 输出 |
| --- | --- | --- |
| Tavily 公开网络检索 | Web Search Capability，可替换 provider | web evidence、URL、source span、latency / cost trace |
| MySQL 结构化查询 | Structured Data Capability，不等于 Zuno 自身持久化层 | table / row evidence、query trace、permission decision |
| RAGFlow 私有知识库 | External RAG Adapter 或 GraphRAG Capability，不替代 `GraphRAGProject` | document evidence、citation、retrieval trace |
| 上传附件 | File / Artifact Capability；文件先属于 Session Workspace | file evidence、hash、path、extraction trace |
| Markdown / PDF 生成 | Artifact Capability，由 Platform 保存和发布 | artifact id、download path、artifact_created event |

这些来源都可以进入本轮 Agent Context，但它们不是 Agent Memory 本身。需要长期保留的事实必须经过 Raw Event Log、Summary Compression、Structured Extraction 和权限边界。

## 会话、产物与实时观测目标边界

目标形态需要一个 Session Workspace，把 task id / session id、上传暂存、运行中间物、最终 artifact、event index 和 trace id 绑定在一起。实现可以是本地文件系统、对象存储或混合方案；`session_dir` 和 `ContextVar` 只是可选实现手段，不写死为架构身份。

长任务必须可观察。目标事件流至少覆盖 task_started、workspace_created、capability_selected、tool_call_started、evidence_ready、artifact_created、task_cancelled、error 和 fallback_applied。SSE 或 WebSocket 都可以作为传输方式；monitor stream 是 Trace / Observability 的展示通道，不是独立业务层。

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
