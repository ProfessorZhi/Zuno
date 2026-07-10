# Zuno Lean Complete Product Architecture

updated: 2026-07-10
status: current-target

## 1. 项目定位与边界

一句话定义：

```text
Zuno = Lean Complete Agentic GraphRAG Product
```

Zuno 是一个本地优先、短小精悍但工程完整的企业知识库 Agent 产品。它允许用户配置模型、创建 Workspace、上传资料、解析和索引文档，通过 AgentChat 使用标准检索或深度检索，由 Single Controller Agent 完成规划、混合检索、GraphRAG、证据整理、claim-level citation、回答生成、trace、成本统计和反馈。

本项目解决的问题不是“再做一个普通 RAG demo”，而是让一个企业知识库 Agent 能回答以下工程问题：

- 用户能否从 UI 完成模型配置、知识库准备、提问、引用查看、trace 查看和反馈。
- Agent 能否在同一条运行链路里完成 context 构建、策略选择、检索、证据绑定、工具调用、反思和回答。
- 证据是否能从 source object 回到 source span，而不是只停留在 doc-level retrieval。
- blocked、prepared、runtime observed、measured 是否被严格区分。
- 本地实现能否持久化、恢复、观测和复现实验结果。

目标用户是需要演示、验证和继续开发企业知识库 Agent 的开发者、研究者和产品评审者。近期目标采用本地优先，是因为 Zuno 当前最缺的不是分布式规模，而是可真实运行、可解释失败、可复现质量的完整产品闭环。本地实现只要 owner 清晰、contract typed、配置可替换、状态可恢复、trace 可查询，就可以是正式近期目标，不是低级占位。

Zuno 近期坚持 Single Controller Agent。用户不需要手动拼 RAG、GraphRAG、Tool 和 Memory 流程；Single Controller 负责在一个任务内选择策略、构建计划、执行检索或工具、绑定引用、必要时反思重试，并最终生成 grounded answer。Zuno 不把近期目标写成默认产品级多 Agent 平台。

Zuno 采用 Agentic GraphRAG，是为了把 doc-level retrieval 的增益转成 evidence-span-level retrieval、claim-level citation 和 answer correctness 的可测增益。Graph、vector、BM25、fusion、rerank 和 citation binding 都必须服务于证据可追溯，而不是作为技术名词堆叠。

近期明确不做：

- 大规模多租户和高可用集群。
- Kafka / RabbitMQ 集群、Kubernetes、复杂运维平台。
- Milvus / Neo4j 集群作为近期 blocker。
- 复杂 SSO / DLP / Vault / Firecracker。
- 大规模在线评测平台。
- 大量 parser/provider 并行接入。
- 默认产品级多 Agent runtime。

项目完成定义：

1. 用户可完成真实端到端流程。
2. 每个运行域有唯一 owner。
3. 关键参数来自配置或 DB，不写死在业务流程中。
4. 使用真实 runtime，而不是只有 mock / fixture。
5. 关键状态可以本地持久化和恢复。
6. 失败、blocked、fallback 有明确语义。
7. 模型、检索、工具、citation 有 trace。
8. focused tests 和至少一个 E2E 场景通过。
9. Agentic GraphRAG 与 baseline 使用同一 fixed case set。
10. Agentic GraphRAG 至少不弱于 baseline，并满足 citation / evidence gate。

当前质量口径：

```text
implementation available
measurement blocked
quality not yet proven
```

Agentic GraphRAG 是否真正完成，仍以 fixed benchmark 和 release gate 为准。

## 2. 用户产品场景

| 步骤 | 输入 | 输出 | 状态 | 失败表现 | 后端事实源 |
| --- | --- | --- | --- | --- | --- |
| 配置模型 | provider、base URL、model、slot、timeout、budget | ModelDefinition、ModelSlotBinding | saved / invalid / unavailable | model call rejected、missing key、timeout | `src/backend/zuno/platform/model_gateway.py`、`src/backend/zuno/api/dto/llm.py`、`src/backend/zuno/platform/database/models/llm.py` |
| 创建 Workspace | workspace name、owner、knowledge scope | Workspace、KnowledgeSpace | active / archived | duplicate name、ACL denied | `src/backend/zuno/api/dto/workspace.py`、`src/backend/zuno/platform/database/models/workspace_session.py` |
| 上传文件 | file、workspace_id、metadata | SourceObject、WorkspaceFile | uploaded / rejected | unsupported type、size limit、storage failure | `src/backend/zuno/knowledge/ingestion`、`src/backend/zuno/knowledge/storage/local_object_store.py`、`src/backend/zuno/platform/database/models/knowledge_file.py` |
| 查看解析与索引状态 | file_id、workspace_id | ParseJob、IndexManifest status | parsing / indexed / blocked | parser blocked、index blocked、missing source span | `src/backend/zuno/knowledge/indexing`、`src/backend/zuno/knowledge/storage/durable_ingestion_store.py`、`src/backend/zuno/platform/database/models/knowledge_task.py` |
| 选择知识库 | workspace_id、knowledge_space_id | retrieval scope | selected / empty / stale | no indexed document、ACL denied | `src/backend/zuno/api/dto/knowledge.py`、`src/backend/zuno/knowledge/retrieval` |
| 发起 AgentChat | message、session_id、model slot、retrieval mode | Task、TaskEvent、streaming answer | running / blocked / completed | model unavailable、no evidence、budget exceeded | `src/backend/zuno/api/dto/completion.py`、`src/backend/zuno/agent/core`、`src/backend/zuno/platform/database/models/message.py` |
| 查看引用和 Artifact | answer_id、citation labels、artifact refs | Citation UI、Artifact | available / partial / unsupported | citation missing、artifact generation failed | `src/backend/zuno/knowledge/trace.py`、`src/backend/zuno/api/dto/message.py` |
| 查看运行 Trace | task_id、run_id | span tree、usage、cost、latency、diagnostics | available / redacted / missing | trace missing、span incomplete | `src/backend/zuno/platform/observability`、`src/backend/zuno/platform/common/runtime_observability.py` |
| 提交反馈 | answer_id、rating、comment、correction | Feedback | saved / rejected | invalid target、ACL denied | `src/backend/zuno/platform/database/models/history.py`、feedback DTO owner |
| 刷新或重启后继续查看 | workspace_id、session_id、task_id | restored task、answer、trace、artifact | recovered / partial / unavailable | only in-memory state lost | SQLite、LocalObjectStore、LocalTraceStore |

前端只负责交互、展示和临时 UI 状态。业务事实源必须在后端：workspace、file、task、artifact、trace、feedback、model slot 和 retrieval profile 都不能只存在于浏览器 state。当前仍是内存态的任务事件、planner state、部分 retrieval diagnostics 和部分 trace 需要迁入 durable store，避免刷新或服务重启后无法解释一次运行。

## 3. 黄金端到端链路

| 节点 | owner | 主要 contract | 输入 | 输出 | 持久状态 | trace event | 失败语义 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Model Configuration | Product & API / Agent Core | ModelDefinition、ModelSlotBinding | provider、model、base URL、slot | bound model slot | SQLite model tables / config | `model_config.saved` | invalid_config / provider_unavailable |
| Workspace | Product & API | Workspace、KnowledgeSpace | user、workspace metadata | workspace scope | SQLite workspace/session rows | `workspace.created` | acl_denied / duplicate |
| Source Object | Input & Knowledge | SourceObject、WorkspaceFile | uploaded file | object URI、checksum | LocalObjectStore + DB row | `source_object.saved` | storage_failed / unsupported |
| Parse Job | Input & Knowledge | ParseJob、ParseSnapshot | source object | parse status | DurableIngestionStore | `parse.started` / `parse.blocked` | parser_unavailable / blocked_not_indexed |
| Document IR | Input & Knowledge | CanonicalDocumentIR | parse snapshot | normalized document | durable IR snapshot | `document_ir.created` | invalid_ir |
| Block / Citation Chunk | Input & Knowledge | DocumentBlock、CitationChunk、SourceSpan | document IR | citation-sized chunks | chunk table/index manifest | `chunk.created` | missing_source_span |
| Index Manifest | Input & Knowledge | IndexManifest、IndexChunk | chunks、embedding config | index version | local index metadata | `index_manifest.created` | stale_index / index_failed |
| BM25 / Vector / Graph Index | Input & Knowledge | RetrieverResult、GraphEvidence | query、scope | candidate evidence | local index / graph index | `retrieval.candidate` | no_candidate / graph_without_span |
| AgentChat Request | Product & API | CompletionRequest、Task | message、session、mode | task/run id | task and events | `agent_run.started` | invalid_request |
| ContextPack | Agent Core | ContextPack | session、memory、knowledge scope | bounded context | optional ContextPack snapshot | `context_build` | context_over_budget |
| Strategy Selection | Agent Core | StrategyDecision | request、context | standard / deep / agentic route | PlanState | `planning.strategy` | unsupported_strategy |
| RetrievalPlan | Agent Core | RetrievalPlan | strategy、question | query set and retriever mix | PlanState | `planning.retrieval_plan` | invalid_plan |
| Hybrid Retrieval | Input & Knowledge | RetrievalTrace | query set、scope | candidates | retrieval diagnostics | `retrieval` | doc_miss / text_miss |
| Graph Expansion | Input & Knowledge | GraphExpansionTrace | entities、candidate chunks | expanded evidence | graph trace | `graph_expand` | graph_unavailable / no_span |
| Fusion / Rerank | Input & Knowledge / Agent Core | RerankTrace | candidates、weights | ranked evidence | rerank diagnostics | `rerank` | ranker_unavailable |
| EvidenceBundle | Input & Knowledge | EvidenceBundle | ranked evidence | evidence spans | evidence diagnostics | `evidence_bundle` | evidence_unavailable |
| Claim Extraction | Agent Core | ClaimSet | draft answer or question | claims | optional trace payload | `claim_extract` | no_claim |
| Citation Binding | Agent Core / Governance | CitationBinding | claims、evidence | bound citations | citation diagnostics | `claim_binding` | citation_miss / doc_only_not_strict |
| Grounded Synthesis | Agent Core | GroundedAnswer | context、evidence、citations | answer draft | message/artifact row | `answer_synthesis` | unsupported_claim |
| Reflection / Replan | Agent Core | ReflectionDecision | answer draft、diagnostics | finish / retrieve / tool / abstain | PlanState | `reflection` / `replan` | max_steps_reached |
| Final Answer / Artifact | Product & API | Message、Artifact | grounded answer | UI payload | DB + object store | `answer.finalized` | partial_answer / artifact_failed |
| Trace / Eval / Cost | Governance & Observability | ZunoSpan、EvalRun | span tree、usage | diagnostics and gate output | LocalTraceStore / eval reports | `eval` | blocked_not_measured |
| Feedback | Product & API / Governance | Feedback | user rating/comment | feedback row | SQLite | `feedback.saved` | invalid_target |
| Post-turn Memory Commit | Agent Core | MemoryRecord、MemoryGovernanceRecord | final answer、events | memory candidates | memory store | `memory_commit` | privacy_blocked / promotion_pending |

这条链路是近期项目的唯一主叙事。任何新能力都必须说明它插入哪一个节点、使用哪个 contract、是否改变持久状态、如何 trace、如何测试。

## 4. 六个运行域总览

| 运行域 | 定位 | 主要 owner | 核心输出 |
| --- | --- | --- | --- |
| Product & API | 用户可见产品流程和后端业务事实源 | `apps/web`、`src/backend/zuno/api`、`src/backend/zuno/api/dto` | workspace、task、artifact、citation UI、trace summary、feedback |
| Input & Knowledge | 文档进入、解析、切块、索引、检索和证据 lineage | `src/backend/zuno/knowledge`、`src/backend/zuno/platform/services/rag`、`src/backend/zuno/platform/services/graphrag` | Document IR、CitationChunk、IndexManifest、EvidenceBundle |
| Agent Core | 模型、ContextPack、planning/control、Single Controller loop、answer synthesis | `src/backend/zuno/agent`、`src/backend/zuno/memory`、`src/backend/zuno/platform/model_gateway.py` | PlanState、RetrievalPlan、GroundedAnswer、MemoryRecord |
| Capability & Tool | Skill/Capability/Tool 的路由、审批、执行和结果归一 | `src/backend/zuno/capability`、`src/backend/zuno/capability/tools`、`src/backend/zuno/platform/services/*tool*` | CapabilityPlan、ToolRequest、ToolResult、ToolTrace |
| Governance & Observability | 安全门、trace、eval、cost、failure diagnostics 和 release gate | `src/backend/zuno/platform/security`、`src/backend/zuno/platform/observability`、`tools/evals/zuno` | ZunoSpan、EvalRun、failure buckets、release gate |
| Local Infrastructure | 本地存储、队列、索引、配置、迁移、健康检查和恢复 | `src/backend/zuno/platform`、`src/backend/zuno/knowledge/storage` | SQLite rows、LocalObjectStore、LocalQueue、LocalIndex、LocalTraceStore |

### 4.1 Product & API

| 项 | 内容 |
| --- | --- |
| 定位 | 承载用户可见的 AgentChat、Workspace、Knowledge Space、file status、task lifecycle、Artifact、Citation UI、Trace summary、Feedback 和 recovery action。 |
| 职责 | 将前端操作转成后端 typed DTO 和 durable business state；通过 SSE/events 暴露 task progress；把 citation、artifact、trace summary 显示为产品能力。 |
| 不负责什么 | 不在前端保存业务事实源；不在 API route 内硬编码 retrieval、planner、tool 或 model 逻辑；不绕过 domain owner 直接改 index 或 memory。 |
| 代码 owner | `apps/web`、`src/backend/zuno/api`、`src/backend/zuno/api/dto`、`src/backend/zuno/api/services`。 |
| 核心 contract | `CompletionRequest`、`MessageDTO`、`WorkspaceDTO`、`KnowledgeDTO`、`ToolDTO`、`AgentDTO`、SSE event payload、Artifact reference、Citation payload。 |
| 主要 runtime | FastAPI routes、CompletionService、workspace/file/task APIs、SSE streaming bridge。 |
| 输入 | user request、workspace_id、knowledge_space_id、file upload、model slot、retrieval mode、feedback。 |
| 输出 | task_id、stream events、answer message、citations、artifact refs、trace summary、feedback receipt。 |
| 配置 | UI 读 model slots、retrieval profile、feature flags；默认值来自 DB/config，workspace override 只允许通过后端验证的 DTO。 |
| 持久状态 | Workspace、KnowledgeSpace、WorkspaceFile、Session、Task、TaskEvent、Artifact、Feedback、model slot binding。 |
| 失败与 fallback | API 返回 typed error；SSE 使用 `blocked`、`failed`、`partial`、`completed`；刷新后从 task/event store 恢复，不从前端缓存推断。 |
| 安全边界 | Workspace ACL、file ownership、tool approval target、trace redaction summary。 |
| trace / metrics | `agent_run.started`、`task_event.emitted`、`api.error`、latency、stream interruption、feedback saved。 |
| focused tests | DTO validation、SSE event order、workspace ACL、task recovery、citation payload shape。 |
| E2E 验收 | 用户配置模型、创建 workspace、上传文档、提问、看到引用和 trace、刷新后仍能查看。 |
| 当前状态 | API/DTO、workspace、message、knowledge、tool 和 model 配置入口存在；部分 task/planner/retrieval runtime state 仍需 durable 化。 |
| 短期闭环项 | P0 trace 可查看；P1 task/planner/retrieval/approval 状态本地持久化；P2 前端 E2E 和演示脚本。 |
| Future Optional | 多租户 admin console、复杂团队权限、企业审计门户。 |

### 4.2 Input & Knowledge

| 项 | 内容 |
| --- | --- |
| 定位 | 管理 SourceObject、WorkspaceFile、ParseJob、Document IR、Block/Chunk、IndexManifest、BM25、Vector、Graph、EvidenceBundle 和 CitationLineage。 |
| 职责 | 文档进入、解析、切块、索引、检索和证据回溯；保证 chunk 与 source span 绑定；parser blocked 不得 fake index。 |
| 不负责什么 | 不决定最终回答；不在 parser 内生成 citation claim；不把 Graph evidence 写成无 source span 的 strict evidence。 |
| 代码 owner | `src/backend/zuno/knowledge`、`src/backend/zuno/knowledge/ingestion`、`src/backend/zuno/knowledge/indexing`、`src/backend/zuno/knowledge/retrieval`、`src/backend/zuno/knowledge/graphrag`、`src/backend/zuno/platform/services/rag`、`src/backend/zuno/platform/services/graphrag`。 |
| 核心 contract | SourceObject、ParseSnapshot、CanonicalDocumentIR、DocumentVersion、DocumentBlock、SourceSpan、CitationChunk、ParentChunk、IndexManifest、IndexChunk、CitationLineage、EvidenceBundle。 |
| 主要 runtime | local object store、durable ingestion store、doc parsers、chunker、local index、retrieval orchestrator、GraphRAG retriever、fusion/rerank。 |
| 输入 | uploaded source object、workspace scope、parser config、index config、retrieval query、Graph expansion request。 |
| 输出 | parse status、IR、chunks、index manifest、retrieval candidates、evidence spans、diagnostics。 |
| 配置 | parser provider、chunk size、chunk overlap、parent context size、embedding model、retrieval top-k、candidate pool size、RRF/rerank weights、citation threshold。 |
| 持久状态 | SourceObject checksum/URI、WorkspaceFile、ParseJob、DocumentVersion、DocumentBlock、IndexManifest、IndexChunk、CitationLineage、local index files、graph evidence index。 |
| 失败与 fallback | unsupported file -> parse blocked；parser failed -> no index handoff；missing source span -> not strict citation；graph unavailable -> vector/BM25 can continue with trace flag。 |
| 安全边界 | Workspace ACL on every retrieval scope；redaction before trace export；no cross-workspace index leakage。 |
| trace / metrics | `parse.started`、`parse.blocked`、`chunk.created`、`index.created`、`retrieval`、`graph_expand`、`rerank`、doc_miss / doc_hit_text_miss diagnostics。 |
| focused tests | parser idempotency、chunk span mapping、index rehydrate、retrieval scope ACL、graph evidence to source span、blocked parser no fake index。 |
| E2E 验收 | 文本文档真实闭环；最小 PDF parser 能产出 source span citation；同一 fixed case set 可比较 standard/deep/agentic。 |
| 当前状态 | 文本类文档、local object store、durable ingestion store、GraphRAG、evidence-span hardening 代码已存在；fixed benchmark measured pass 仍 blocked。 |
| 短期闭环项 | P0 fixed benchmark；P1 PDF source span citation；P1 retrieval diagnostics 持久化。 |
| Future Optional | 大量 parser provider、外部 OCR/VLM、外部 graph/vector 集群。 |

### 4.3 Agent Core

| 项 | 内容 |
| --- | --- |
| 定位 | 收口 Model Runtime / Gateway、Model Slot、ContextPack、Memory Read、StrategySelector、PlannerOutput、PlanState、RetrievalPlan、CapabilityPlan、AgentControlRuntime、Observation、Reflection、Replan、Grounded Answer Synthesis、Post-turn Memory Commit。 |
| 职责 | Single Controller Agent 执行完整循环；所有真实模型调用统一经过 Model Runtime / Gateway；规则 planner 与 model planner 共享 contract。 |
| 不负责什么 | 不直接写前端状态；不直接操作低层存储；不绕过 capability policy 执行副作用工具；不建设默认多 Agent 平台。 |
| 代码 owner | `src/backend/zuno/agent`、`src/backend/zuno/agent/core`、`src/backend/zuno/memory`、`src/backend/zuno/platform/model_gateway.py`、legacy `src/backend/zuno/agent/core/models` 只作为兼容层逐步收口。 |
| 核心 contract | ModelCallRequest/Response、ModelSlotBinding、ContextPack、PlannerOutput、PlanState、RetrievalPlan、CapabilityPlan、Observation、ReflectionDecision、GroundedAnswer、MemoryRecord。 |
| 主要 runtime | GeneralAgent single loop、model gateway、context builder、memory engine、planner/controller、claim binder、answer synthesis。 |
| 输入 | AgentChat request、workspace scope、model slot、memory scope、retrieval diagnostics、tool results。 |
| 输出 | plan, observations, answer, citations, abstain/fallback reason, memory commit candidates。 |
| 配置 | model provider/name/base URL、model slot、thinking mode、max agent steps、model timeout、retry count、budget、memory read policy、context budget。 |
| 持久状态 | PlanState、TaskEvent、ContextPack snapshot、model usage、MemoryRecord、MemoryGovernanceRecord。 |
| 失败与 fallback | finish when answer grounded or abstain chosen；re-retrieve when evidence insufficient；use tool when CapabilityPlan approved；abstain when citation/grounding fails；max steps yields blocked/partial with trace。 |
| 安全边界 | model input redaction、workspace memory scope、tool approval handoff、output gate before final answer。 |
| trace / metrics | `context_build`、`memory_read`、`planning`、`model_call`、`claim_binding`、`answer_synthesis`、`reflection`、`replan`、`memory_commit`。 |
| focused tests | model gateway no bypass、planner contract parity、max step handling、abstain semantics、ContextPack observable in AgentChat。 |
| E2E 验收 | Single Controller uses configured model, retrieves evidence, cites claims, handles insufficient evidence, writes trace and memory candidates。 |
| 当前状态 | GeneralAgent、model manager/gateway surfaces、memory contracts、claim binder 和 evidence-aware pieces exist；所有真实模型调用统一入口仍是 P0 closure。 |
| 短期闭环项 | P0 unified Model Runtime / Gateway；P1 Memory ContextPack in real AgentChat observable；P1 PlanState durable。 |
| Future Optional | product-level multi-agent orchestration、distributed controller runtime。 |

### 4.4 Capability & Tool

| 项 | 内容 |
| --- | --- |
| 定位 | 管理 SkillCard、CapabilityCard、CapabilityRouter、KnowledgeCapability、ToolCapability、ArtifactCapability、ToolCard、ToolRequest、Approval、CredentialRef、ExecutionAdapter、ResultNormalizer 和 ToolTrace。 |
| 职责 | Skill 定义任务方法，Tool 执行具体动作；Capability policy 决定可用性、审批、凭据和执行边界。 |
| 不负责什么 | Skill 不是 Tool；planner 不硬编码工具执行；工具 adapter 不决定 Agent 策略；本轮不建设 marketplace。 |
| 代码 owner | `src/backend/zuno/capability`、`src/backend/zuno/capability/tools`、`src/backend/zuno/capability/mcp`、`src/backend/zuno/platform/services/tool_*`、`src/backend/zuno/platform/services/user_defined_tool_runtime.py`。 |
| 核心 contract | SkillCard、CapabilityCard、ToolCard、ToolRequest、ApprovalRequest、CredentialRef、ExecutionAdapterResult、NormalizedToolResult、ToolTrace。 |
| 主要 runtime | capability registry、selector/router、control plane、policy/approval gate、tool execution adapter、MCP adapter、result normalizer。 |
| 输入 | CapabilityPlan、tool args、workspace/user policy、credential ref、approval decision。 |
| 输出 | ToolResult、artifact refs、normalized observations、tool trace。 |
| 配置 | enabled skills/tools、tool timeout、retry count、credential ref, side-effect policy, sandbox policy。 |
| 持久状态 | ToolRequest、Approval、ToolResult、ToolTrace、credential reference metadata、artifact object。 |
| 失败与 fallback | approval_required、approval_denied、timeout、adapter_error、idempotency_conflict；Agent observes failure and can replan or abstain。 |
| 安全边界 | no raw secret in trace；side-effect tools require approval；credential by reference；local sandbox sufficient for near-term。 |
| trace / metrics | `tool_call` span with approval, adapter, latency, timeout, normalized result, redaction status。 |
| focused tests | approval gate、timeout、idempotency key、credential redaction、result normalizer、tool failure observation。 |
| E2E 验收 | 2-3 real tools complete approval / timeout / trace loop from AgentChat。 |
| 当前状态 | capability layer、tool registry/control plane、MCP/tool adapters and multiple tools exist；near-term needs smaller real tool closure instead of marketplace expansion。 |
| 短期闭环项 | P1 2-3 个真实 Tool 完成 approval / timeout / trace 闭环。 |
| Future Optional | marketplace、remote enterprise tool governance、Firecracker isolation。 |

### 4.5 Governance & Observability

| 项 | 内容 |
| --- | --- |
| 定位 | 合并 Input Gate、Retrieval Gate、Tool Gate、Output Gate、ACL、Redaction、ZunoSpan、Trace tree、Usage、Cost、Latency、Evidence diagnostics、Citation diagnostics、Failure buckets、Benchmark 和 Release gate。 |
| 职责 | 每次 Agent run 可追踪；blocked、prepared、runtime observed、measured 严格区分；Agentic GraphRAG 使用同一 fixed case set 与 baseline 比较。 |
| 不负责什么 | 不把 incomplete run 写成 measured；不把 doc-level citation 写成 strict citation；不要求近期完整 LangSmith / OTel 平台。 |
| 代码 owner | `src/backend/zuno/platform/security`、`src/backend/zuno/platform/observability`、`src/backend/zuno/platform/common/runtime_observability.py`、`src/backend/zuno/knowledge/trace.py`、`tools/evals/zuno`。 |
| 核心 contract | ZunoSpan、TraceTree、UsageRecord、CostRecord、EvidenceDiagnostics、CitationDiagnostics、FailureBucket、EvalRun、ReleaseGateResult。 |
| 主要 runtime | local trace store、runtime observability helpers、eval runners、release gate reports、redaction/security gates。 |
| 输入 | agent events、model usage、retrieval traces、tool traces、citation bindings、eval case set。 |
| 输出 | span tree、diagnostics、metrics.json、report.md、failure_cases.md、release gate status。 |
| 配置 | trace retention、redaction policy、benchmark case set、release thresholds、export sink、sampling。 |
| 持久状态 | TraceSpan、EvalRun、failure cases, benchmark reports, usage/cost records。 |
| 失败与 fallback | missing trace fields -> unavailable_due_to_missing_trace_fields；incomplete profile -> blocked_not_measured；prepared data -> not measured。 |
| 安全边界 | redacted trace export、workspace ACL for trace view、secret-free model/tool metadata。 |
| trace / metrics | agent span tree plus recall, evidence available, citation accuracy, answer correctness, unsupported claim rate, latency, cost。 |
| focused tests | blocked_not_measured, doc-level citation not strict, four failure buckets, missing trace fields unavailable。 |
| E2E 验收 | one AgentChat run visible in trace UI/summary; fixed benchmark generates comparable baseline and agentic reports。 |
| 当前状态 | local trace/eval surfaces and failure bucket diagnostics exist; no complete fixed EnterpriseRAG measured pass for agentic profile。 |
| 短期闭环项 | P0 Agent run trace persisted and viewable; P0 fixed benchmark reaches baseline gate。 |
| Future Optional | full LangSmith/OTel backend, online eval platform, enterprise compliance dashboards。 |

Agent run span tree:

```text
agent_run
  -> context_build
  -> memory_read
  -> planning
  -> retrieval
  -> graph_expand
  -> rerank
  -> model_call
  -> tool_call
  -> claim_binding
  -> answer_synthesis
  -> output_gate
  -> memory_commit
  -> eval
```

### 4.6 Local Infrastructure

| 项 | 内容 |
| --- | --- |
| 定位 | 管理 SQLite、LocalObjectStore、LocalQueue、LocalWorker、LocalIndex、LocalGraphIndex、LocalTraceStore、Configuration、Migration、Health、Backup/export 和 Restart recovery。 |
| 职责 | 提供正式近期目标的本地持久化、队列、索引和恢复能力；接口清晰、配置化、可替换。 |
| 不负责什么 | 不追求分布式规模；不在 business service 写死路径、模型、阈值或 provider；不把 external cluster 作为短期 blocker。 |
| 代码 owner | `src/backend/zuno/platform`、`src/backend/zuno/platform/config`、`src/backend/zuno/platform/database`、`src/backend/zuno/platform/storage`、`src/backend/zuno/knowledge/storage`。 |
| 核心 contract | Database URL、migration contract、LocalObjectStore contract、LocalQueue event、LocalWorker result、LocalIndex manifest、LocalTraceStore span record、HealthCheck。 |
| 主要 runtime | SQLite/SQLModel, local object store, in-process runner, local index, local graph index, trace store, config loader。 |
| 输入 | configuration, DB migrations, object payloads, queue jobs, index manifests, trace spans。 |
| 输出 | durable records, object URIs, job status, index handles, health state, export bundle。 |
| 配置 | storage path、database URL、index path、trace retention、queue concurrency、migration mode、backup/export path。 |
| 持久状态 | DB rows, source objects, parse snapshots, index files, graph files, trace spans, eval reports, artifacts。 |
| 失败与 fallback | transaction rollback, idempotency conflict, storage unavailable, migration failed, stale index, recovery partial。 |
| 安全边界 | workspace-scoped storage paths, secret-free config snapshots, redacted export。 |
| trace / metrics | `storage.write`、`queue.job`、`migration`、`health`、recovery status、index rehydrate latency。 |
| focused tests | local object round trip, restart recovery, idempotency, migration smoke, index rehydrate, trace retention。 |
| E2E 验收 | stop/start service after upload and AgentChat; workspace/file/task/answer/trace recover without front-end state。 |
| 当前状态 | SQLite models, local object store, config, database and storage surfaces exist; some runtime state still needs durable migration。 |
| 短期闭环项 | P1 task/planner/retrieval/approval durable state; P2 reproducible startup path。 |
| Future Optional | Postgres、Redis、MinIO、RabbitMQ、external vector/graph index adapters。 |

## 5. 代码 Ownership Matrix

| 运行域 | 主要 owner | 兼容层 | 禁止新增逻辑的位置 |
| --- | --- | --- | --- |
| Product & API | `apps/web`、`src/backend/zuno/api`、`src/backend/zuno/api/dto`、`src/backend/zuno/api/services` | DTO facade、legacy service wrapper | frontend state、API route 内硬编码 runtime、legacy service 新增业务分支 |
| Input & Knowledge | `src/backend/zuno/knowledge`、`src/backend/zuno/platform/services/rag`、`src/backend/zuno/platform/services/graphrag` | legacy query adapters、old parser adapters | API route、Agent class、frontend upload state |
| Agent Core | `src/backend/zuno/agent`、`src/backend/zuno/memory`、`src/backend/zuno/platform/model_gateway.py` | `src/backend/zuno/agent/core/models` legacy manager | direct SDK call、tool adapter、retrieval service 内生成最终回答 |
| Capability & Tool | `src/backend/zuno/capability`、`src/backend/zuno/capability/tools`、`src/backend/zuno/capability/mcp` | legacy tool facade、platform tool services | planner 内硬编码执行、API route 直接调用副作用工具 |
| Governance & Observability | `src/backend/zuno/platform/security`、`src/backend/zuno/platform/observability`、`src/backend/zuno/platform/common/runtime_observability.py`、`tools/evals/zuno` | old trace helpers、eval report adapters | feature module 自建不可汇总 trace、报告里 fake measured |
| Local Infrastructure | `src/backend/zuno/platform`、`src/backend/zuno/platform/database`、`src/backend/zuno/platform/storage`、`src/backend/zuno/knowledge/storage` | local adapters、compatibility aliases | business service 写死存储路径、runtime 内写死 DB URL |

## 6. 配置化与禁止写死契约

| 配置类别 | 必须配置化的值 | 默认值 owner | 优先级 | workspace override | 运行时记录 |
| --- | --- | --- | --- | --- | --- |
| Model runtime | model provider、model name、base URL、model slot、thinking mode、model timeout、retry count、budget | `src/backend/zuno/platform/config` + DB model definitions | DB workspace binding > environment secret/ref > YAML default > code fallback only for tests | 允许，但必须通过 model slot validation | `model_config.effective` span records provider/model/slot/timeout/budget without secrets |
| Embedding / rerank | embedding model、rerank model、candidate pool size、rerank weights | Input & Knowledge config owner | DB retrieval profile > YAML > test default | 允许 per knowledge space | `retrieval.config.effective` |
| Retrieval | retrieval top-k、RRF weights、citation threshold、parent context size | retrieval profile owner | workspace profile > global config > benchmark manifest | 允许，benchmark run must pin values | `retrieval.plan` and eval report |
| Chunking | chunk size、chunk overlap、parent context size | Parse/index config owner | parser profile > global config | 允许 per knowledge space before indexing | IndexManifest includes effective chunk config |
| Agent loop | max agent steps、model timeout、tool timeout、retry count、budget | Agent Core config owner | request override if allowed > workspace policy > global config | only within policy limits | `agent_run.config` |
| Tool execution | tool timeout、retry count、approval policy、credential ref | Capability & Tool owner | workspace/user policy > tool manifest > global default | policy controlled | `tool_call.config` with credential ref only |
| Storage | storage path、database URL、index path、trace retention | Local Infrastructure owner | environment > YAML > local dev default | no workspace override for path/DB; retention may vary by workspace policy | health/config snapshot |
| Eval / release | benchmark case set、release thresholds | Governance & Observability owner | benchmark manifest > repo default | no runtime override for release judgment | metrics.json records case set and thresholds |

业务代码禁止写死 provider、model、threshold、top-k、chunk size、storage path、DB URL、timeout、budget 和 release threshold。测试可以使用 explicit fixture defaults，但必须在测试名或 fixture 中暴露，不得伪装成 production default。

## 7. 数据与状态模型

| 对象 | 唯一 ID | workspace scope | 生命周期 | 持久化位置 | restart recovery |
| --- | --- | --- | --- | --- | --- |
| ModelDefinition | model_definition_id | global / workspace visible | created -> active -> disabled | SQLite model/config table | yes |
| ModelSlotBinding | slot_binding_id | workspace | bound -> updated -> disabled | SQLite | yes |
| Workspace | workspace_id | workspace root | active -> archived | SQLite | yes |
| KnowledgeSpace | knowledge_space_id | workspace | active -> reindexed -> archived | SQLite | yes |
| SourceObject | source_object_id / checksum | workspace | uploaded -> retained -> deleted | LocalObjectStore + SQLite | yes |
| WorkspaceFile | file_id | workspace | uploaded -> parsing -> indexed / blocked | SQLite | yes |
| ParseJob | parse_job_id | workspace | queued -> running -> completed / blocked | SQLite / durable ingestion store | yes |
| DocumentVersion | document_version_id | workspace | created -> indexed -> superseded | SQLite / IR snapshot | yes |
| DocumentBlock | block_id | workspace | created -> indexed -> retired | SQLite / local index | yes |
| IndexManifest | index_manifest_id | workspace | created -> active -> stale | SQLite / local index metadata | yes |
| IndexChunk | chunk_id | workspace | active -> superseded | local index + metadata | yes |
| CitationLineage | citation_lineage_id | workspace | created with chunk -> retired with version | SQLite / metadata | yes |
| Session | session_id | workspace/user | open -> archived | SQLite | yes |
| Task | task_id | workspace/session | queued -> running -> completed / blocked / failed | SQLite | yes |
| TaskEvent | event_id | task/workspace | appended -> retained | SQLite / event log | yes |
| PlanState | plan_state_id | task | created -> updated -> finalized | SQLite / trace payload | yes |
| ToolRequest | tool_request_id | task/workspace | proposed -> approved / denied -> executed | SQLite | yes |
| Approval | approval_id | workspace/user | pending -> approved / denied / expired | SQLite | yes |
| ToolResult | tool_result_id | task/tool_request | created -> consumed | SQLite / object store for large payload | yes |
| Artifact | artifact_id | task/workspace | created -> updated -> archived | SQLite + LocalObjectStore | yes |
| TraceSpan | span_id | task/workspace | started -> ended / errored | LocalTraceStore / SQLite | yes |
| EvalRun | eval_run_id | benchmark scope | prepared -> running -> measured / blocked | eval output directory + metadata | yes |
| Feedback | feedback_id | workspace/session | submitted -> reviewed | SQLite | yes |
| MemoryRecord | memory_record_id | workspace/user/session policy | candidate -> active -> decayed/deleted | memory store / SQLite | yes |
| MemoryGovernanceRecord | memory_governance_id | workspace/user | pending -> approved / rejected / expired | SQLite | yes |

## 8. Agentic GraphRAG

Zuno 的 retrieval modes 是产品入口，不是用户手动装配工具箱：

- standard retrieval：以 BM25/vector 检索和 citation 为主，作为 fixed baseline。
- deep retrieval：扩大 query、candidate、rerank 和 evidence diagnostics。
- agentic retrieval：Single Controller Agent 基于 ContextPack 和 StrategyDecision 规划检索、Graph expansion、fusion/rerank、citation binding、reflection/replan 和 abstain。

Graph evidence 必须回到 source span。没有 source_span 或 citation_label 的 doc-only evidence 不能作为 strict citation。GraphRAG 的质量证明必须来自同一 fixed case set 的 paired benchmark，而不是单次 demo 或 prepared manifest。

短期 baseline gate：

```text
Agentic Recall@5 >= standard_rag
Evidence Text Available@5 >= 0.60
Source Doc Citation Accuracy >= 0.85
Citation Accuracy >= 0.30
Answer Correctness >= standard_rag
Unsupported Claim Rate 不得恶化
```

Failure buckets：

- doc_miss：正确文档没有进入 top-k。
- doc_hit_text_miss：正确文档进入 top-k，但 gold evidence text 没进入 context。
- text_hit_citation_miss：gold evidence text 进入 context，但 citation 没绑定。
- citation_hit_answer_wrong：citation 绑定正确，但 answer synthesis 错。
- unavailable_due_to_missing_trace_fields：底层 trace 字段不足，不能编造诊断。

## 9. Runtime 完成与质量完成

| 能力 | Runtime 完成 | 质量完成 |
| --- | --- | --- |
| Agentic GraphRAG | runtime、evidence、citation 可运行，failure buckets 可输出 | fixed benchmark 完整跑完并达到 gate |
| Model Gateway | 所有调用统一入口，model slot 可配置 | usage/cost/error 无旁路缺失，provider failure 可解释 |
| Memory | ContextPack 真实接入 AgentChat | retrieval relevance、privacy、promotion/decay eval 通过 |
| Tool | approval/execute/result 闭环 | timeout/idempotency/security 测试通过，side-effect trace 可查 |
| Trace | span 写入本地 trace store | 整个 Agent run 可完整查看、重放关键决策并支持 eval attribution |
| Document ingestion | source object -> parse -> chunk -> index -> citation lineage | parser blocked 不 fake index，PDF source span citation 通过 E2E |
| Product E2E | UI/API 能完成黄金链路 | fresh checkout 可复现启动、演示脚本和 front-end E2E 通过 |

## 10. 数据与状态事实源

前端不是业务事实源。后端事实源分为：

- SQLite：workspace、session、message、task、file、knowledge metadata、model binding、tool request、approval、feedback、memory governance、trace metadata。
- LocalObjectStore：source object、artifact、大 payload、parse snapshot。
- LocalIndex / LocalGraphIndex：BM25/vector/graph 的本地 index 和 manifest。
- LocalTraceStore：ZunoSpan、usage、cost、latency、retrieval/citation diagnostics。
- Eval output：fixed benchmark metrics、report、failure cases 和 release gate result。

服务重启后必须恢复：

- workspace、knowledge space、file status、document/index version。
- session、task final state、answer、citation、artifact。
- trace summary 和关键 diagnostics。
- model slot binding、retrieval profile、release threshold。

可以不立即恢复但必须明确为短期 gap：

- running task 的每一步 live stream。
- in-memory planner intermediate state。
- partial tool adapter local process state。

## 11. 短期必须闭环

P0：

- Agentic GraphRAG fixed benchmark 跑通并达到 baseline gate。
- 所有真实模型调用统一进入 Model Runtime / Gateway。
- Agent run trace 持久化并可查看。

P1：

- task / planner / retrieval / approval 状态本地持久化。
- 至少一个真实 PDF parser 跑通 source span citation。
- 2-3 个真实 Tool 完成 approval / timeout / trace 闭环。
- Memory ContextPack 在真实 AgentChat 中可观测。

P2：

- 前端 E2E、项目演示脚本和可复现启动方式。

## 12. 非近期目标

Future Optional Extensions：

- Postgres、Redis、MinIO、RabbitMQ、Kafka、Kubernetes。
- 外部 Milvus / Neo4j 集群和分布式 graph/vector index。
- 复杂 SSO / DLP / Vault、Firecracker。
- 大规模在线评测平台和企业运维门户。
- 大量 parser/provider 并行接入、OCR/VLM enrichment 平台化。
- 产品级多 Agent runtime。

这些能力可以作为可替换 adapter 或远期平台化方向，但不得作为近期 blocker，也不得主导 README、architecture.html 或短期 roadmap。

## 13. 架构图

Markdown 是详细实施蓝图。HTML 是从以下四个 canonical Mermaid section 生成的 visual executive summary。

### Lean System Overview

六个运行域和它们的 owner 边界。Product 触发黄金链路，Agent Core 编排检索和工具，Governance 贯穿 trace/eval/cost，Local Infrastructure 提供本地事实源。

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef guard fill:#eef6ff,stroke:#7aa2d8,stroke-width:1px,color:#16202a;
  classDef infra fill:#f7f7f2,stroke:#b8c2cc,stroke-width:1px,color:#16202a;

  Product["Product & API<br/>AgentChat, Workspace, File, Task, Artifact, Citation UI"]
  Knowledge["Input & Knowledge<br/>Source, Parse, IR, Chunk, Index, EvidenceBundle"]
  Agent["Agent Core<br/>Model Gateway, ContextPack, Planner, Single Controller"]
  Capability["Capability & Tool<br/>Skill, Capability, Tool, Approval, Result"]
  Governance["Governance & Observability<br/>Gates, Trace, Eval, Cost, Release"]
  Infra["Local Infrastructure<br/>SQLite, ObjectStore, Queue, Index, TraceStore"]

  Product --> Agent
  Product --> Knowledge
  Agent --> Knowledge
  Agent --> Capability
  Knowledge --> Governance
  Capability --> Governance
  Agent --> Governance
  Product --> Governance
  Governance --> Infra
  Product --> Infra
  Knowledge --> Infra
  Agent --> Infra
  Capability --> Infra

  class Product,Knowledge,Agent,Capability node;
  class Governance guard;
  class Infra infra;
```

#### 分析

- 六域是近期实施和 ownership 的主边界。
- Governance 不是最后生成报告的脚本，而是贯穿输入、检索、工具、输出和 eval。
- Local Infrastructure 是正式近期目标，不是低级 placeholder。

### Golden Path Runtime

用户从模型配置和 Workspace 进入，文档被解析和索引，AgentChat 触发计划、检索、引用、回答、trace、feedback 和恢复。

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart LR
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef trace fill:#eef6ff,stroke:#7aa2d8,stroke-width:1px,color:#16202a;

  Model["Configure Model"]
  Workspace["Create Workspace"]
  Upload["Upload Document"]
  Parse["Parse Gateway"]
  IR["Document IR and Citation Chunks"]
  Index["BM25 / Vector / Graph Index"]
  Ask["AgentChat Ask"]
  Context["ContextPack"]
  Plan["Strategy and RetrievalPlan"]
  Retrieve["Hybrid Retrieval and Graph Expansion"]
  Rerank["Fusion / Rerank"]
  Cite["Claim-level Citation"]
  Answer["Grounded Answer / Artifact"]
  Trace["Trace / Cost / Eval"]
  Feedback["Feedback"]
  Recovery["Restart Recovery"]

  Model --> Workspace --> Upload --> Parse --> IR --> Index --> Ask --> Context --> Plan --> Retrieve --> Rerank --> Cite --> Answer --> Trace --> Feedback --> Recovery

  class Model,Workspace,Upload,Parse,IR,Index,Ask,Context,Plan,Retrieve,Rerank,Cite,Answer,Feedback,Recovery node;
  class Trace trace;
```

#### 分析

- 这条链路是短期唯一主叙事。
- 每个节点都有 owner、contract、持久状态、trace event 和失败语义。
- Restart Recovery 是产品完成标准的一部分。

### Agentic GraphRAG and Agent Loop

standard、deep 和 agentic 共享 evidence/citation contract；agentic 模式由 Single Controller 规划检索、Graph expansion、claim binding、reflection 和 replan。

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef decision fill:#fff8e8,stroke:#d2a44a,stroke-width:1px,color:#16202a;
  classDef gate fill:#eef6ff,stroke:#7aa2d8,stroke-width:1px,color:#16202a;

  Request["AgentChat Request"]
  Context["ContextPack"]
  Strategy{"Strategy<br/>standard / deep / agentic"}
  Standard["Standard Retrieval<br/>BM25 + Vector baseline"]
  Deep["Deep Retrieval<br/>larger pool + rerank"]
  Agentic["Agentic Plan<br/>query, graph, tool, citation goals"]
  Hybrid["Hybrid Retrieval"]
  Graph["Graph Expansion<br/>entity / relation / community evidence"]
  Evidence["EvidenceBundle<br/>source span required"]
  Claim["Claim Extraction"]
  Bind["Claim-level Citation Binding"]
  Reflect{"Reflect<br/>finish / re-retrieve / tool / abstain"}
  Tool["Capability / Tool Observation"]
  Final["Final Grounded Answer"]
  Eval["Failure Buckets and Release Gate"]

  Request --> Context --> Strategy
  Strategy --> Standard --> Hybrid
  Strategy --> Deep --> Hybrid
  Strategy --> Agentic --> Hybrid
  Agentic --> Graph
  Hybrid --> Evidence
  Graph --> Evidence
  Evidence --> Claim --> Bind --> Reflect
  Reflect -->|finish| Final
  Reflect -->|re-retrieve| Agentic
  Reflect -->|use tool| Tool --> Reflect
  Reflect -->|abstain| Final
  Final --> Eval

  class Request,Context,Standard,Deep,Agentic,Hybrid,Graph,Evidence,Claim,Bind,Tool,Final,Eval node;
  class Strategy,Reflect decision;
```

#### 分析

- agentic 不是独立产品模式，而是 Single Controller 内部策略。
- strict citation 必须绑定 source span，doc-only evidence 不能冒充。
- 质量完成只看 fixed benchmark 和 release gate。

### Local Deployment and State

近期部署是本地优先的正式实现：Web、FastAPI、SQLite、本地对象存储、本地队列、本地索引、模型 provider 和 trace store 构成闭环；外部集群只是可选 adapter。

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef store fill:#f7f7f2,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef future fill:#f3f1ff,stroke:#9a8fd0,stroke-width:1px,color:#16202a;

  Web["Web / Desktop UI"]
  API["FastAPI<br/>DTO + SSE"]
  Agent["Single Controller Agent"]
  Model["Model Provider<br/>OpenAI-compatible / DeepSeek / local adapter"]
  SQLite["SQLite<br/>workspace, task, model, memory"]
  ObjectStore["LocalObjectStore<br/>source, artifact, parse snapshot"]
  Queue["LocalQueue / In-process Runner"]
  Index["LocalIndex / LocalGraphIndex"]
  Trace["LocalTraceStore<br/>span, usage, diagnostics"]
  Config["Configuration<br/>YAML, env, DB override"]
  Future["Optional Future Adapters<br/>Postgres, Redis, MinIO, external vector/graph"]

  Web --> API --> Agent
  Agent --> Model
  API --> SQLite
  Agent --> SQLite
  Agent --> Queue
  Agent --> Index
  API --> ObjectStore
  Agent --> Trace
  Config --> API
  Config --> Agent
  SQLite --> Future
  ObjectStore --> Future
  Queue --> Future
  Index --> Future
  Trace --> Future

  class Web,API,Agent,Model,Config node;
  class SQLite,ObjectStore,Queue,Index,Trace store;
  class Future future;
```

#### 分析

- 本地状态必须能支持 restart recovery。
- 外部 Postgres / Redis / MinIO / graph/vector store 是可替换方向，不是近期 blocker。
- 配置最终生效值必须进入 trace 和 eval 报告。

## 14. 验证和演示方式

最小演示：

1. 从干净环境启动 Web/API。
2. 配置 DeepSeek 或 OpenAI-compatible model slot。
3. 创建 Workspace。
4. 上传文本资料并看到 parse/index 状态。
5. 在 AgentChat 中选择知识库提问。
6. 查看 answer、claim-level citation、artifact 或 trace summary。
7. 提交 feedback。
8. 重启服务后恢复 workspace、file status、answer、citation 和 trace。

最小验证：

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
pytest -q tests/evals/test_enterprise_rag_paired_benchmark.py tests/evals/test_rag_eval_metrics.py -p no:cacheprovider
```

质量验证：

- EnterpriseRAG paired benchmark 必须包含 standard_rag 和 agentic_graphrag 同一 fixed case set。
- `metrics.json`、`report.md`、`failure_cases.md` 必须区分 retrieval、evidence text、citation binding、answer synthesis。
- blocked run 必须写 blocked_reason，不得写 measured。

历史证据只从统一入口查看：

- `docs/history/programs/README.md`
