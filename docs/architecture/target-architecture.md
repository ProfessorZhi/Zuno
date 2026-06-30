# 目标架构

## 用途

这份文档描述 Zuno 的近期目标架构。它是 Target，不是 Current；只有已经由代码、测试、trace evidence 和文档边界证明的内容，才能进入 [current-architecture.md](current-architecture.md)。

参考稿：

- [Zuno 的 Agentic RAG 与 GraphRAG 理想架构 PDF](assets/zuno-agentic-rag-graphrag-ideal-architecture.pdf)
- [企业私有知识库与多功能 Agent 助手](product-scenario-enterprise-kb.md)
- [安全与沙箱目标架构](security-and-sandbox.md)
- [架构总览 Markdown](../architecture.md)
- [架构展示 HTML](../architecture.html)

## 核心判断

Zuno 的目标不是把普通 RAG 聊天框做厚，也不是默认改成多 Agent。Zuno 的主场景应收束为**本地优先的企业私有知识库与多功能 Agent 助手**：面向企业内部文档、合同、制度、项目资料、技术文档、HR / 简历资料和个人项目证据，提供可引用问答、文档分析、报告生成和受控工具调用。

```text
Local-first Enterprise Private Knowledge Agent Workspace
= Single Controller Agent
+ Context Builder
+ Agent Core Runtime / Planning Harness
+ Agentic RAG Controller
+ GraphRAG Knowledge Base
+ Document Ingestion / Parse Gateway
+ ToolCard / MCP Tool Layer
+ Security / Policy Guard
+ Hooks / Policy / Budget / Fallback
+ Evidence / Citation / Trace / Eval
+ Session Workspace / Artifact Flow
```

第一性原理是：用户真正需要的不是“多一个 Agent 名词”，而是一个问题进入系统后，能被正确理解、决定是否检索、选择合适知识路径、拿到可引用证据、在证据不足时重试，并把最终答案、引用、Trace 和产物交付出来。

因此，企业内部文档知识库是 Zuno 的主叙事；简历 / HR 资料和个人项目证据是同构的私有知识资料场景，可以作为轻量验证样例。Zuno 不应被表述为普通 RAG demo，也不应被表述为无审批自动执行一切动作的自主办公机器人。

因此 Zuno 近期继续保持：

- Python / FastAPI monorepo。
- 模块化单体，而不是微服务拆分。
- Single Controller Agent，而不是默认产品级多 Agent。
- Agentic RAG + GraphRAG，而不是固定“先 RAG 再回答”。
- Current / Target / History 严格分开。

## 目标架构细化分层

Zuno 下一阶段的架构表达不再只停留在“大模块名”，而要把企业知识库、文档解析、安全和评测这些产品级能力放进同一张可执行蓝图。目标分层如下：

| 层 | 目标职责 | 近期边界 |
| --- | --- | --- |
| Model / Gateway | 管理模型 provider、本地模型、模型选择、上下文窗口、成本和延迟策略。 | 作为 Platform 能力进入目标图，不把某个 vendor 写死为 Current。 |
| Agent Core Runtime | 承载 `prepare_context -> plan -> ReAct -> observe -> reflect -> replan -> post_turn_commit` 的控制循环。 | Planning 是 runtime 内部控制能力，不是独立顶层业务层。 |
| Context / Memory | 生成 Context Pack，管理 Raw Event Log、recent window、task summary、长期语义/情节/程序性记忆、graph memory 和 review / promotion / decay 流。 | 目标是生产级 write-manage-read 记忆系统；当前仍是 foundation。 |
| Capability / Tool | 用 ToolCard / manifest 管理工具语义、权限、成本、健康状态、side effect、approval、executor adapter、result normalization 和 tool trace。 | SDK / API / CLI / SSH / MCP 是 execution mode，不是业务顶层分类。 |
| Knowledge / Retrieval | 管理 `basic / local / global / drift`、GraphRAG、retrieval fusion、evidence、citation。 | Knowledge 可作为 capability 被 Agent 调用，但架构上单独成层。 |
| Document Ingestion | 管理 upload、format detection、parser registry、OCR/VLM、chunk metadata、ACL 继承和 indexing handoff。 | 企业知识库场景的前置层，不能继续隐含在普通工具调用里。 |
| Security / Policy | 管理输入检查、PII/商业秘密脱敏、prompt injection 防护、chunk 级权限、工具审批和输出 DLP。 | 横切层，必须覆盖输入、检索、工具和输出。 |
| Trace / Eval | 管理 runtime trace、LangSmith 映射、offline/online eval、retrieval quality、tool trajectory、latency/cost。 | 当前已有本地 trace/eval foundation；LangSmith 产品化仍是 Target。 |
| Platform / Workspace | 管理 session workspace、artifact store、数据库、向量库、图存储、background jobs 和 provider。 | 近期保持模块化单体，不是微服务拆分。 |

这组分层是 Target。它用于指导后续 program，不表示上述所有能力都已经成为 Current。

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

## 六个代码主层与目标能力映射

Zuno 目标仍用六个主层承载代码和责任边界：

1. API 层：FastAPI routes、DTO、Auth、SSE / WebSocket event stream、task / session、upload、artifact list / download。
2. Agent 层：Single Controller Agent，目标形态是 `prepare_context -> agent_loop -> post_turn_commit`，内部细化为 Agent Core Runtime / Planning Harness。
3. Memory 层：短期状态、工作记忆、长期语义记忆、长期情节记忆、程序性记忆、Raw Event Log。
4. Capability 层：ToolCard Registry、keyword / alias search、Native BM25 over ToolCards、optional vector tool search、permission / health / cost filter、CapabilitySelectionTrace、MCP adapter 和 execution adapter metadata。
5. Knowledge 层：`KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot`、LLM-first entity / relation extraction、`basic / local / global / drift`、retrieval / fusion / evidence，以及 Document Ingestion handoff。
6. Platform 层：PostgreSQL、Redis、RabbitMQ、MinIO、Milvus、Neo4j、optional Elasticsearch adapter、model gateway、session workspace、artifact store、storage、background jobs、observability 和 LangSmith / trace backend adapter。

横切治理层是 Evidence / Citation / Trace / Eval / Policy。它记录 trace_id、evidence bundle、citation coverage、latency、cost、permission decision、fallback reason 和 eval profile，但不单独拥有业务入口。

## Document Ingestion 与企业知识库

企业知识库不是“上传文件后直接丢给 RAG”。目标链路是：

```text
upload
  -> file validation
  -> format detection
  -> parser registry
  -> OCR / VLM / structure extraction
  -> chunk metadata
  -> ACL inheritance
  -> BM25 / vector / graph index handoff
  -> parse trace / eval sample
```

目标 Parser Capability Matrix 至少要覆盖：

| 类型 | 目标处理方式 | 关键证据锚点 |
| --- | --- | --- |
| PDF | PyMuPDF4LLM / Docling 路径，保留 page、text span、image/table metadata。 | page number、span、image id、table id。 |
| DOCX / PPTX / XLSX | Office parser 或 convert-to-PDF fallback，保留 heading、slide、sheet、table。 | document id、section、slide、sheet、row/column。 |
| TXT / MD / CSV / JSON / HTML | 轻量 text loader，加结构化 metadata。 | line range、heading、row id、DOM section。 |
| 图片 / 扫描件 | OCR / VLM 路径，输出视觉描述和 OCR 文本。 | image id、bbox、OCR confidence。 |
| 代码文件 | code-aware chunking，保留语言、symbol、line range。 | language、path、symbol、line range。 |

当前仓库已有部分 parser foundation 和多模态路径，但统一 Parse Gateway、格式矩阵、代码文件解析、ACL 继承和 parser eval 仍是 Target。

## Context Builder 与记忆

Zuno 的记忆层不等于聊天历史拼接，也不等于把所有知识库证据塞进向量库。目标 Memory Layer 是一个 write-manage-read 子系统：先把运行事件作为事实源保存，再通过摘要压缩和结构化抽取生成候选记忆，经过 review / promotion / decay 后进入长期层，最后由 Context Builder 按任务、权限、预算和相关性选入 Context Pack。

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

| 层级 | 目标职责 | 进入模型方式 |
| --- | --- | --- |
| Raw Event Log | append-only 保存用户、Agent、工具、检索、文件解析和输出事件，是审计、回放、重总结和评测事实源。 | 默认不直接进入模型，只通过 summary、retrieval 或 debug trace 间接进入。 |
| L0 Working Context | 本轮真正 model-visible 的上下文包，包含当前目标、约束、证据、工具状态和少量选中记忆。 | 由 Context Builder 装配为 `ModelContextPacket`。 |
| L1 Recent Window | 最近连续对话和完整 tool call / result group，保护本轮 coherence。 | 按 token budget 裁剪，不能打断未闭合工具组。 |
| L2 Task Summary | 当前 task / thread 的 goals、constraints、decisions、TODO、artifact refs、open questions。 | 优先作为长期任务连续性的压缩表示进入 Context Pack。 |
| L3 Structured Long-term Memory | semantic / episodic / procedural memory：用户偏好、项目术语、失败修正、成功路径、规则和策略。 | 通过 scope、relevance、importance、recency、confidence、privacy risk 过滤后进入。 |
| L4 Graph Memory | 实体、关系、社区、历史决策和项目对象的图式记忆。 | Target 扩展；用于 local/global/drift 线索，不与 chunk 证据硬混排。 |

长期记忆内容类型：

- 语义记忆：用户偏好、项目术语、固定约束、架构基线和业务实体事实。
- 情节记忆：过去任务为什么选择某条检索路径、某次失败如何修正、某轮工具轨迹带来的经验。
- 程序性记忆：Current / Target / Future / History 规则、引用规则、预算、权限、审批和安全策略。

目标策略是 Summary Compression + Structured Extraction。Summary 不能替代 Raw Event Log；structured memory 必须保留 `source_event_ids`。Prompt Caching 是 compute-layer hint，不是 memory compression。

Context Pack 的目标 contract 必须同时携带内容、来源、预算和策略：每个 item 至少能追溯 `source_event_ids`、`ContextSource`、token estimate、priority 和 dropped reason；整体 packet 必须说明 compression strategy、structured extraction strategy、review requirement 和缺失 source id 风险。短期状态与工作记忆可以服务本轮调用；语义、情节和程序性记忆进入长期层前必须经过 review / approval，并保留 scope、dedupe key、confidence、retention policy 和来源事件。

目标 read path：

```text
query / step
  -> retrieval-or-not gating
  -> scope and permission filter
  -> recent window + task summary + structured memory recall
  -> relevance / importance / recency / confidence scoring
  -> token budget and eviction
  -> ModelContextPacket with provenance
```

目标 write path：

```text
turn events
  -> Raw Event Log append
  -> summary compression
  -> structured memory candidate extraction
  -> dedupe / conflict check
  -> privacy and retention policy
  -> review / approval
  -> promotion to task summary, semantic, episodic, procedural or graph memory
```

记忆压缩不只发生在 prompt 前。滑动窗口只保护最近上下文，摘要压缩负责长期任务连续性，重要性过滤负责写入和读取阶段，结构化抽取负责可检索 durable memory。Prompt caching 只降低重复前缀成本和延迟，不解决“该记住什么”的问题。

目标存储映射：

| 存储 | Memory 角色 | 边界 |
| --- | --- | --- |
| PostgreSQL | Raw Event Log、memory metadata、review state、provenance、retention policy 的真相源。 | 不把全文检索和向量搜索都塞进 SQL。 |
| Redis | thread state、hot summary、TTL、checkpoint cache 和 write-behind buffer。 | 不是长期审计真相源。 |
| Vector store | semantic / episodic memory candidate recall。 | 必须回连 PostgreSQL metadata 和 `source_event_ids`。 |
| Graph store | graph memory、entity/relation、community memory 和项目对象关系。 | Target 扩展，不把知识库 GraphRAG 与 Agent Memory 混成一个无边界图。 |
| Optional lexical index | exact match、术语、错误码、文件名、字段过滤。 | 作为 adapter，不是 Memory 层唯一检索方式。 |

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

Zuno 的规划范式不是三套框架硬拼。Planning 是 Agent Core Runtime 的核心控制能力，runtime / harness 负责把状态、工具、记忆、安全、trace 和失败恢复串起来。

目标链路是：

```text
prepare_context
  -> intent / mode router
  -> coarse plan
  -> ReAct step
  -> tool / retrieval dispatch
  -> observation
  -> gated reflection
  -> replan or finish
  -> post_turn_commit
```

Planner 只负责把用户目标拆成有限个可检查步骤。ReAct 层负责每轮决定是否检索、调用哪个 capability、是否重写 query、是否补证据。Reflection 只在证据不足、检索冲突、回答覆盖率低、结构化输出不合格或连续两轮没有增量收益时触发。Replan 只改写剩余计划，不抹掉已验证证据。

LangGraph 是这个 Agent Core Runtime 的目标实现候选：它适合承载 state graph、checkpoint、durable execution、streaming、interrupt / human-in-the-loop 和 resume。它不是“规划模块本身”，而是把 planning runtime 工程化的框架。

ToT / LATS 这类高成本树搜索不作为产品默认路径；它们只能作为未来困难模式或离线分析路径。

## ToolCard、manifest 与 Tool Control Plane

工具层按能力语义治理，不按接入方式拆顶层目录。目标形态是 Tool Control Plane：

```text
Tool Manifest
  -> ToolCard Registry
  -> Capability Selector
  -> Tool Policy / Approval Gate
  -> Executor Adapter
  -> Sandbox / Budget / Timeout
  -> Result Normalizer
  -> Tool Trace / Audit Event
```

Tool Manifest 是工具注册真相源，ToolCard 是给检索和模型选择使用的 compact projection。Runtime 先检索 compact ToolCard，选中后再加载 full input/output schema 和 executor metadata，避免每轮把所有工具完整 schema 塞进上下文。

目标 ToolCard / manifest 至少描述：

```text
tool name / aliases / owner
capability type: search | document | email | database | artifact | code | ssh | retrieval
execution mode: local_function | local_sdk | sdk_to_api | api | local_cli | cli_to_api | ssh | mcp_local | mcp_remote | graph_retrieval
input_schema / output_schema
permission level
side effect level
cost / latency / timeout
approval policy
health and fallback policy
result normalization contract
audit and trace contract
```

MCP 可以包装本地函数、SDK、CLI、API、数据库、文件系统或 SSH。CLI 本身通常是本地入口，但它背后可以是本地程序、远程 API 或 SSH 远程 shell。Zuno 不把这些接入方式写成业务顶层分类，而是把它们放进 ToolCard / execution adapter metadata，让 runtime 能统一做权限、预算、审计和 fallback。

高副作用能力，例如邮件发送、SSH、外部写操作、删除/覆盖类工具，默认需要 approval / interrupt / audit trace。

目标执行器边界：

| Executor | 目标作用 | 必要治理 |
| --- | --- | --- |
| `LocalFunctionExecutor` / `LocalSdkExecutor` | 调用进程内函数或本地 SDK。 | input schema、timeout、异常标准化、trace span。 |
| `ApiExecutor` / `RemoteSdkExecutor` | 调用 HTTP / SDK 封装的远程服务。 | auth ref、retry、network policy、cost/latency trace。 |
| `CliExecutor` | 执行本机 CLI。 | command allowlist、cwd/env policy、shell injection 防护、output truncation。 |
| `SshExecutor` | 在远程主机执行受控命令。 | host/user allowlist、approval、timeout、non-root policy、audit event。 |
| `McpExecutor` | 调用 stdio 或 HTTP MCP server 暴露的 tools/resources/prompts。 | transport、server trust profile、auth/audience、session policy、tool allowlist。 |
| `GraphRetrievalExecutor` | 调用 Knowledge / GraphRAG 检索能力。 | product mode、query method、budget、evidence/citation policy。 |

Tool result 不直接作为 final answer。Result Normalizer 必须输出统一对象：`tool_name`、`executor_type`、`ok/error_code`、`latency_ms`、`cost`、`artifact_refs`、`evidence_refs`、`sanitized_content`、`raw_result_ref`、`trace_id`。模型只消费 sanitized content 和必要 evidence refs；raw result 进入受控 artifact / trace 存储。

## Security、Trace 与 Eval

安全与评测必须是同一条链路上的治理能力，而不是事后补丁。

安全与沙箱的完整目标边界见 [security-and-sandbox.md](security-and-sandbox.md)。当前 Zuno 只能说具备 ToolCard / MCP policy、Hooks / Evidence / Trace 和 platform security thin surfaces；不能声称已经有成熟 OS sandbox、credential broker、完整 DLP 或生产级工具审批闭环。

目标安全闸门：

1. 输入闸门：鉴权、限流、文件类型/大小/hash 检查、PII / 商业秘密识别、prompt injection 识别。
2. 解析闸门：恶意文档隔离、OCR/VLM 输出标记、parser failure trace、来源 metadata 固化。
3. 检索闸门：chunk 级 ACL、workspace/project scope、document trust label、retrieval result sanitization。
4. 工具闸门：side effect 分级、permission decision、approval gate、timeout、working directory / host allowlist。
5. 输出闸门：DLP scan、citation coverage、format validation、sensitive field redaction。

目标沙箱分层：

| 层 | 作用 | 当前边界 |
| --- | --- | --- |
| Policy Sandbox | 工具调用前做 risk classification、permission check、approval policy、budget、timeout 和 audit event。 | Target。先治理工具准入，不等于 OS 隔离。 |
| Workspace Sandbox | 限制 readonly sources、writable artifacts、temp、quarantine 和 secrets 访问。 | Target。企业原始文档默认只读。 |
| Execution Sandbox | 隔离 parser、OCR、CLI、MCP local server、代码执行和 SSH wrapper。 | Target / Future。不能写成 Current。 |
| Network / Credential Sandbox | 默认禁网、allowlist 出站、credential broker、secret redaction。 | Future。不能把 raw secret 放进 prompt 或 sandbox filesystem。 |

目标评测面：

- Parser eval：格式支持率、解析失败率、OCR confidence、chunk metadata coverage。
- Retrieval eval：Recall@k、MRR、nDCG、retrieval relevance、citation coverage。
- Memory eval：memory pollution rate、wrong-promotion rate、stale-memory hit rate、duplicate-memory ratio、forgotten-needed-memory rate、cross-session recall benefit。
- Answer eval：correctness、faithfulness / groundedness、answer relevance、format validity。
- Agent eval：tool selection、argument correctness、trajectory quality、approval rate、fallback rate。
- Product eval：latency、cost、retry rate、user feedback、online regression。

LangSmith 作为目标 observability / evaluation adapter，用于映射 Zuno runtime trace、dataset、evaluator、experiment 和 dashboard。本地 pytest / eval runner 仍保留为 release gate。

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
