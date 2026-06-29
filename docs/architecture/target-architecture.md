# 目标架构

## 用途

这份文档描述 Zuno 的近期目标架构。它是 Target，不是 Current；只有已经由代码、测试、trace evidence 和文档边界证明的内容，才能进入 [current-architecture.md](current-architecture.md)。

参考稿：

- [Zuno 的 Agentic RAG 与 GraphRAG 理想架构 PDF](assets/zuno-agentic-rag-graphrag-ideal-architecture.pdf)
- [架构总览 Markdown](../architecture.md)
- [架构展示 HTML](../architecture.html)

## 核心判断

Zuno 的目标不是把普通 RAG 聊天框做厚，也不是默认改成多 Agent。Zuno 应该是一个本地优先的知识工作台：

```text
Local-first Agent Workspace
= Single Controller Agent
+ Context Builder
+ Agentic RAG Controller
+ GraphRAG Knowledge Base
+ ToolCard / MCP Tool Layer
+ Hooks / Policy / Budget / Fallback
+ Evidence / Citation / Trace / Eval
+ Session Workspace / Artifact Flow
```

第一性原理是：用户真正需要的不是“多一个 Agent 名词”，而是一个问题进入系统后，能被正确理解、决定是否检索、选择合适知识路径、拿到可引用证据、在证据不足时重试，并把最终答案、引用、Trace 和产物交付出来。

因此 Zuno 近期继续保持：

- Python / FastAPI monorepo。
- 模块化单体，而不是微服务拆分。
- Single Controller Agent，而不是默认产品级多 Agent。
- Agentic RAG + GraphRAG，而不是固定“先 RAG 再回答”。
- Current / Target / History 严格分开。

## 架构视图目录

目标架构同时保留两套架构描述理论：

- 4+1 视图：Kruchten 经典模型，包含逻辑、开发、进程、物理和场景。
- View & Beyond / C&C 视图体系：包含逻辑视图、Component-and-Connector 视图、部署视图和质量视图，按架构关注点组织文档。

它们不是冲突关系，也不是相加后得到互斥理论。4+1 是经典总框架；C&C / 部署 / 质量视图是更工程化的架构描述方式。Zuno 把这两套视角落成九类理论视图，并额外单独放大 Agent Loop，形成十类架构视图，便于 README、面试、评审和后续 program 使用：

| 图 | 对应视角 | 回答的问题 | 入口 |
| --- | --- | --- | --- |
| Logical View | 4+1 Logical | Zuno 的核心职责如何分层？ | [architecture.md](../architecture.md#logical-view) |
| Development View | 4+1 Development | apps、backend、docs、.agent、tools、tests 如何组织？ | [architecture.md](../architecture.md#development-view) |
| Process View | 4+1 Process | 请求、Agent runtime、工具/检索/LLM 调用和事件流如何运行？ | [architecture.md](../architecture.md#process-view) |
| Physical View | 4+1 Physical | 本地优先部署和外部 provider 如何连接？ | [architecture.md](../architecture.md#physical-view) |
| Scenarios View | 4+1 Scenarios | 一个 query 如何经过 Agentic RAG 变成 answer？ | [architecture.md](../architecture.md#scenarios-view) |
| V&B Logical View | View & Beyond Logical | Runtime、Memory、Tool、Retrieval、Evidence 等领域子系统如何组织？ | [architecture.md](../architecture.md#vb-logical-view) |
| Component-and-Connector View | View & Beyond C&C | API、Agent、Memory、Tool、Retrieval、Evidence、Trace 如何连接？ | [architecture.md](../architecture.md#component-and-connector-view) |
| V&B Deployment View | View & Beyond Deployment | 可替换 provider、存储、模型、搜索和 MCP 如何部署？ | [architecture.md](../architecture.md#vb-deployment-view) |
| Quality View | View & Beyond Quality | 性能、可靠性、安全、可观测性、可修改性和评测如何落地？ | [architecture.md](../architecture.md#quality-view) |
| Agent Loop View | Zuno 专题图 | Agent 如何规划、执行、观察、反思、重规划？ | [architecture.md](../architecture.md#agent-loop-view) |

这十类图不是十张装饰图，也不是理论映射图。前九类来自两套架构描述理论；Agent Loop 可以归入 Process / C&C，但它是 Zuno Agentic RAG 内核，值得单独作为第十类专题图展开。

HTML 生成页：

- [docs/architecture.html](../architecture.html)

## 产品模式与内部 query method

产品层只需要暴露三个选择：

```text
普通模式
增强模式
自动模式
```

内部层保留四个 `query_method`：

```text
basic | local | global | drift
```

`auto` 是 router，用来选择 direct、normal basic、enhanced agentic，以及在增强路径里选择 `basic / local / global / drift`。`auto` 不是第五种 GraphRAG query mode，也不能作为最终 `resolved_query_method`。

Trace / eval contract 必须明确分开三层字段：

| 字段 | 枚举 | 含义 |
| --- | --- | --- |
| `requested_product_mode` / `resolved_product_mode` | `normal / enhanced / auto` | 用户请求和系统最终采用的产品模式。 |
| `router_decision` | `normal_basic / enhanced_basic / enhanced_local / enhanced_global / enhanced_drift / direct` | Router 为什么选择当前路径。 |
| `requested_query_method` / `resolved_query_method` | requested 可为 `auto`；resolved 只允许 `basic / local / global / drift` | 内部检索方法；`auto` 只表示交给 router。 |
| `fallback_reason`、`budget_policy`、`fallback_policy`、`citation_coverage` | trace fields | 解释预算、降级和证据覆盖率。 |

| 产品选择 | 系统行为 | 适合场景 |
| --- | --- | --- |
| 普通模式 | 固定低预算 `basic`，以 Native BM25 + Dense Vector + RRF + optional rerank 为主。 | 快速问答、查原文、低延迟请求。 |
| 增强模式 | 进入受控 Agentic RAG，由系统在 `basic / local / global / drift` 中选择或组合。 | 复杂分析、多跳证据、架构诊断、审查报告。 |
| 自动模式 | Router 先判断 direct / basic / enhanced，再决定是否进入 Agentic RAG。 | 默认用户体验，避免让普通用户理解所有技术模式。 |

高级用户和调试场景可以手动指定 `basic / local / global / drift`。普通用户默认只看到普通、增强、自动。

## Query-to-Answer 主链路

目标闭环是：

```text
User Query
  -> Session Manager
  -> Context Builder
  -> Single Controller Agent
  -> Product Mode Policy: normal / enhanced / auto
  -> Router Decision: direct / normal_basic / enhanced_basic|local|global|drift
  -> Retrieval: basic / local / global / drift
  -> Evidence Check
  -> Answer Synthesizer
  -> Citation Builder
  -> Trace / Eval / Memory Write
  -> Answer / Report / Artifact
```

这个链路吸收 DeepSearchAgents 的清晰工程表达：任务入口、会话目录、上传附件、工具调用、运行事件、Markdown / PDF 产物和前后端闭环。但 Zuno 不把 Tavily、MySQL、RAGFlow 或固定三助手写成身份；它们只应该表现为可替换 capability 或 adapter。

## 六个主层

Zuno 目标仍用六个主层承载代码和责任边界：

1. API 层：FastAPI routes、DTO、Auth、SSE / WebSocket event stream、task / session、upload、artifact list / download。
2. Agent 层：Single Controller Agent，目标形态是 `prepare_context -> agent_loop -> post_turn_commit`。
3. Memory 层：短期状态、工作记忆、长期语义记忆、长期情节记忆、程序性记忆、Raw Event Log。
4. Capability 层：ToolCard Registry、keyword / alias search、Native BM25 over ToolCards、optional vector tool search、permission / health / cost filter、CapabilitySelectionTrace、MCP adapter。
5. Knowledge 层：`KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot`、LLM-first entity / relation extraction、`basic / local / global / drift`、retrieval / fusion / evidence。
6. Platform 层：PostgreSQL、Redis、RabbitMQ、MinIO、Milvus、Neo4j、optional Elasticsearch adapter、model gateway、session workspace、artifact store、storage、background jobs 和 observability。

横切治理层是 Evidence / Citation / Trace / Eval / Policy。它记录 trace_id、evidence bundle、citation coverage、latency、cost、permission decision、fallback reason 和 eval profile，但不单独拥有业务入口。

## Context Builder 与记忆

Zuno 不是“用户问题直接丢给 Agent”。目标流程是先由 Context Builder 生成最小但足够的 Context Pack：

PHASE09 当前已经证明的是 `RuntimeTurnLedger`、当前轮 trace reset、GeneralAgent 最小 evidence chain、post-turn evidence payload、六层目标入口 import guard 和 eval diagnostics。它还不是完整产品级 LangGraph runtime upgrade、成熟 model-visible context injection、生产级 memory retrieval / consolidation、动态工具编排或前端 trace UI。

```text
system rules
+ user settings
+ session state
+ task state
+ selected memory
+ uploaded files summary
+ selected ToolCards
+ selected evidence
-> Context Pack
```

记忆目标边界：

- 短期状态：本轮意图、query_method、当前 plan、最近工具结果、trace id。
- 工作记忆：候选证据包、已打开文件、临时摘要、待验证结论、未完成 todo。
- 长期语义记忆：用户偏好、项目术语、固定约束、架构基线。
- 长期情节记忆：过去任务为什么选择某条检索路径、某次失败如何修正。
- 程序性记忆：Current / Target / Future / History 规则、引用规则、预算和权限规则。

目标策略是 Summary Compression + Structured Extraction。Summary 不能替代 Raw Event Log；structured memory 必须保留 `source_event_ids`。Prompt Caching 是 compute-layer hint，不是 memory compression。

Context Pack 的目标 contract 必须同时携带内容、来源、预算和策略：每个 item 至少能追溯 `source_event_ids`、`ContextSource`、token estimate、priority 和 dropped reason；整体 packet 必须说明 compression strategy、structured extraction strategy、review requirement 和缺失 source id 风险。短期状态与工作记忆可以服务本轮调用；语义、情节和程序性记忆进入长期层前必须经过 review / approval，并保留 scope、dedupe key、confidence、retention policy 和来源事件。

## 检索与 GraphRAG

四个内部方法：

```text
basic
  Native BM25 + Dense Vector + RRF + optional rerank

local
  Entity linking + graph neighborhood + relationship + source chunks

global
  Community reports / global summaries / map-reduce style synthesis

drift
  Community global primer -> follow-up questions -> local/basic evidence loop
```

关键边界：

- Native BM25 是本地 BM25 排序算法。
- Elasticsearch 只是可选外部 adapter，不是 BM25 算法本体。
- RRF 是默认 coarse fusion，默认 `k = 60`，后面可接 optional rerank。
- `global` 不和 BM25 top-k 生硬拼榜单。它先生成 corpus-level prior，再由 `local` 或 `basic` 回补 chunk-level evidence。
- `drift` 是“先总后细”的两阶段或多阶段路径：global primer + local/basic evidence loop。
- enhanced path 可以生成 query variants，但必须保留 original query。
- multi-retriever recall 可使用 Native BM25、Dense Vector、Graph Local 和 Community Global。
- deduplication 使用稳定 id，例如 `chunk_id`、`document_id + span`、`graph_node_id`、`community_report_id`。

GraphRAG 实体抽取默认主路径是 LLM 抽取。知识库配置必须能选择 `graph_index_settings.entity_extraction_mode = llm`、`model_refs.entity_extraction_llm_id`、prompt / schema version、cost / latency policy 和 eval profile。规则、正则和词典只用于日期、金额、条款号等确定格式辅助、preprocessing、fallback 或 baseline test。

PHASE08 当前已经证明的是 extractor config contract、snapshot 传播、query method / citation / retrieval fusion trace contract、global community-only prior 边界和 GeneralAgent 工具文本暴露。它还不是生产级 LLM entity / relation extraction、完整 RRF 实现或成熟 rerank 治理；这些仍留在 Target。

## Plan、ReAct 与 Reflection

Zuno 的规划范式不是三套框架硬拼，而是：

```text
粗计划
  -> ReAct 执行
  -> 门控 Reflection
  -> 局部重规划
```

Planner 只负责把用户目标拆成有限个可检查步骤。ReAct 层负责每轮决定是否检索、调用哪个 capability、是否重写 query、是否补证据。Reflection 只在证据不足、检索冲突、回答覆盖率低、结构化输出不合格或连续两轮没有增量收益时触发。

ToT / LATS 这类高成本树搜索不作为产品默认路径；它们只能作为未来困难模式或离线分析路径。

## Hooks、Policy 与运行事件

Hooks 不是日志装饰，而是治理层控制点：

- agent 开始时注入 thread metadata、route policy 和预算。
- model call 前裁剪上下文、限制工具面、选择模型。
- tool call 前后做权限、缓存、计量、fallback 和结果标准化。
- final answer 前检查 citation coverage、evidence coverage 和输出格式。
- post turn 阶段写 trace、memory candidate、artifact event 和 eval metadata。

长任务必须可观察。目标事件流至少覆盖：

- `task_started`
- `workspace_created`
- `capability_selected`
- `tool_call_started`
- `evidence_ready`
- `artifact_created`
- `fallback_applied`
- `task_cancelled`
- `error`

SSE 或 WebSocket 都可以作为传输方式；monitor stream 是 Trace / Observability 的展示通道，不是独立业务层。

## 多来源 Evidence Channel

| 来源 | Zuno 目标边界 | 输出 |
| --- | --- | --- |
| 公开网络检索 | Web Search Capability，可替换 provider | web evidence、URL、source span、latency / cost trace |
| 结构化业务数据 | Structured Data Capability，不等于 Zuno 自身持久化层 | table / row evidence、query trace、permission decision |
| 内部非结构化文档 | GraphRAG Capability 或 External RAG Adapter | document evidence、citation、retrieval trace |
| 上传附件 | File / Artifact Capability；文件先属于 Session Workspace | file evidence、hash、path、extraction trace |
| Markdown / PDF 生成 | Artifact Capability，由 Platform 保存和发布 | artifact id、download path、artifact_created event |

这些来源都可以进入本轮 Agent Context，但它们不是 Agent Memory 本身。需要长期保留的事实必须经过 Raw Event Log、Summary Compression、Structured Extraction 和权限边界。

## 替换方向

```text
Domain Pack front path -> GraphRAG Project
domain_pack_id target name -> graphrag_project_id
rag_graph_deep -> enhanced mode + query_method
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
- 默认 ToT / LATS 树搜索

## 与 Current 的硬边界

这些内容即使出现在目标设计里，也不能写成 Current：

- 完整产品级 `prepare_context -> agent_loop -> post_turn_commit` LangGraph runtime。
- 生产级 Memory DB、成熟 memory extraction / retrieval / consolidation。
- 产品级动态 Capability Selector。
- 完整 frontend trace 面板。
- 完整 hooks / middleware governance。
- Java、微服务、事件驱动 worker 或产品级多 Agent 模式。

Domain Pack 只保留为历史或迁移兼容语境；公开目标身份字段是 `graphrag_project_id`。

## 执行边界

本文件不承担 active program、active phase 或 queued program 的执行入口。当前状态、下一步和队列顺序以 [roadmap.md](roadmap.md) 为正式人类入口；Agent 执行计划以 `.agent/programs/` 为准。

详细目标设计放在：

- `.agent/architecture/near-term/`
- `.agent/architecture/future/`
- `.agent/architecture/decisions/`

Canonical Target / Proposed visual blueprint：

- `.agent/architecture/near-term/00-architecture-index.md`

Canonical near-term Markdown：

- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
