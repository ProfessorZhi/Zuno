---
title: Zuno 架构总览
aliases:
  - Zuno Architecture Overview
tags:
  - zuno/architecture
  - zuno/agentic-rag
status: target
updated: 2026-07-01
---
# Zuno 架构总文档

## 用途

这是 Zuno 当前正式的文字总架构文档。它回答四个问题：

1. Zuno 当前是什么。
2. Zuno 的目标架构是什么。
3. 下一阶段为什么落在企业私有知识库、多格式文档解析、评测观测和安全治理上。
4. 哪些能力仍是 Target，不能写成 Current。
5. 当前第一版 runtime slice 与 production-grade Target 的成熟度边界；展开版成熟度和 runtime-first 交付物口径由 `docs/architecture/production-readiness.md` 维护。

图形化展示以 `docs/architecture/architecture.html` 为准；图源是 `docs/architecture/architecture.md`。Agent 侧维护镜像是 `.agent/architecture/architecture.md`，Agent 侧也保留同名 HTML 镜像。这四个 canonical paths 必须保持一致：

- `docs/architecture/architecture.md`
- `.agent/architecture/architecture.md`
- `docs/architecture/architecture.html`
- `.agent/architecture/architecture.html`

## 核心判断

Zuno 的主叙事是 **本地优先的企业私有知识库与多功能 Agent 助手**，不是普通 RAG 问答 demo，也不是默认多 Agent 平台。

当前仓库已经完成的是架构治理、文档系统、六层后端边界、`GeneralAgent` 单循环主线、Query Router foundation、Context / Memory foundation、ToolCard foundation、GraphRAG query contract、PHASE03 workspace product API / SSE runtime surface、PHASE04 Document Ingestion / Parse Gateway runtime surface、PHASE05 local deterministic index job runtime surface、PHASE06 controller-node durable runtime surface、PHASE07 snapshot / SQLModel-backed memory runtime surface、PHASE08 local deterministic Tool Control Plane runtime surface、PHASE09 Agentic Retrieval / Evidence / Citation runtime、PHASE10 Security / Observability / release eval runtime、PHASE11 Web workspace Agent 产品闭环，以及 PHASE12 release closure。

仍然不能写成 Current 的能力包括：生产级 LangGraph runtime、成熟 Memory DB、完整 dynamic tool orchestration、生产级 Docling / MinerU / Unstructured parser platform、生产级 GraphRAG extraction / fusion / RRF / rerank / 外部 index platform、LangSmith 产品化评测、rootless/gVisor/Firecracker 安全沙箱、外部 vault / OAuth credential broker、生产级输出 DLP、完整前端 trace 面板和默认产品级多 Agent runtime。

```text
Zuno current
  = monorepo
  + FastAPI backend
  + Single GeneralAgent single loop
  + Knowledge / GraphRAG query path
  + evidence / citation / trace foundation

Zuno target
  = Local-first Enterprise Private Knowledge Agent Workspace
  + Single Controller Agent Runtime
  + Document Ingestion / Parse Gateway
  + Context / Memory write-manage-read
  + Tool Control Plane
  + Agentic RAG + GraphRAG
  + Security / Approval / Sandbox
  + LangSmith-compatible Trace / Eval
  + Workspace / Artifact / Event Flow
```

## Current

Current 只写代码、测试和可复现结果已经证明的事实：

- 当前是 monorepo，主要边界是 `apps/web`、`apps/desktop`、`src/backend/zuno`、`tools`、`tests`、`docs` 和 `.agent`。
- 当前 Python 后端 runtime 边界是 `src/backend/zuno`。
- 当前后端目标层已经收口为 `api / agent / memory / capability / knowledge / platform` 六层。
- 当前主线是 `GeneralAgent` single loop，不是完整产品级 LangGraph runtime，也不是默认多 Agent runtime。
- 当前知识问答链路是 `Completion API -> CompletionService -> GeneralAgent single loop -> search_knowledge_base -> KnowledgeQueryService -> GraphRAGQueryService -> RetrievalPlanner / RetrievalOrchestrator -> Evidence / Citation / Trace -> answer`。
- 当前已证明 `product_mode = normal | enhanced | auto` 与 `query_method = basic | local | global | drift` 的 PHASE08 contract：`normal` 强制 basic，`enhanced` 必检索并由 Agent 选通道，`auto` 先判断是否需要检索再选通道；`auto` 是 router，不是第五种最终检索方法。
- 当前 `zuno.knowledge.agentic_graphrag` 已提供 Agentic Retrieval Router、StagedFusionPlan、EvidenceBundle、CitationBuilder、UnsupportedClaimChecker、GraphRAGIndexPipelineContract 和 AgenticGraphRAGTrace。
- 当前 `zuno.platform.security.governance` 已提供 input / retrieval / tool / output gate contract、ToolSecurityProfile、SandboxAuditEvent、policy decision trace 和 secret / PII redaction helper。
- 当前 `zuno.platform.observability.trace_eval` 已提供 OTel / LangSmith-compatible `ZunoSpan` schema、redacted span builder、LangSmith export adapter、eval dataset case、metric threshold、release baseline 和 sandbox audit span bridge。
- 当前 PHASE03 已提供 workspace / session / file / ingest / task / approval / event / artifact / feedback 后端 API 与 SSE runtime surface，覆盖 manual approval wait / resume / reject、artifact read 和 feedback；它仍是 in-process surface，不是 durable task runtime，也不是完整 UI 闭环。
- 当前 PHASE04 已提供 Document Ingestion / Parse Gateway runtime owner surface，覆盖 parser adapter registry、deterministic job status、Document IR normalization、parser diagnostics、legacy chunk normalizer 和 parser golden fixture replay；它不是生产级 Docling / MinerU / Unstructured 平台。
- 当前 PHASE05 已提供 `zuno.knowledge.indexing` 本地 deterministic index job runtime surface，覆盖 knowledge space、BM25 / vector / graph 本地 index、job manifest、失败重试、回放和 retrieval payload；它不是生产级 Elasticsearch / Milvus / Neo4j，也不是完整 GraphRAG extraction / community report runtime。
- 当前 PHASE06 已提供 `zuno.agent.durable_runtime` controller-node 级 durable runtime surface，覆盖 checkpoint、approval interrupt、resume、cancel、recoverable / non-recoverable failure、store snapshot，并接入 workspace task runtime；它不是生产 LangGraph checkpointer，不是进程重启后的持久恢复，也不保证 exactly-once tool execution。
- 当前 PHASE07 已提供 `zuno.memory.store.DatabaseMemoryStore`、`DurableMemoryStore`、`MemoryStoreSnapshot`、memory runtime SQLModel tables、governance ledger、sensitive exclusion、promotion、decay、consolidation、Context Pack include/exclude reasons，并让 `GeneralAgent` 通过 `MemoryEngine` 做 post-turn write / pre-context read；它不是生产级 semantic/vector Memory DB、后台 memory scheduler 或完整隐私治理平台。
- 当前 PHASE08 已提供 `zuno.capability.runtime.ToolControlPlaneRuntime`、`ToolRuntimeRequest`、`InMemoryCredentialBroker`、`SandboxPolicyEnforcer` 和 default tool runtime，覆盖只读工具自动执行、高副作用工具 approval wait / approve 后执行、credential reference、sandbox context、audit trace、workspace task event stream 和最小前端审批卡；它不是 rootless / gVisor / Firecracker sandbox，不是外部 vault / OAuth broker，不是真实网络代理，也不是完整 MCP runtime governance。
- 当前 PHASE09/10/11 已把 Agentic retrieval、citation-rich artifact、security / observability snapshot、release eval 和 Web workspace Agent UI 闭环接入第一版 runtime slice；它不是生产级 GraphRAG extraction / rerank、外部 trace sink、online eval 或 production Desktop 闭环。
- 当前 Memory、Hooks、GraphRAG 和 Runtime Upgrade 仍有 foundation slice；Tool Control Plane 已有第一版本地 runtime surface，但不是成熟生产工具平台。
- 当前 `src/backend/zuno` 是唯一当前 Python 后端 runtime 边界，没有 active root-level `services/` 后端树。

## Target 分层

| 平面 | 目标职责 | 当前边界 |
| --- | --- | --- |
| Presentation / Workspace | Web、Desktop、会话、上传、产物、trace 面板和用户反馈。 | 当前已有 Web / Desktop 工作区和 PHASE03 前端 API helpers；完整产品 UI 闭环仍是 Target。 |
| API / Session | FastAPI routes、DTO、Auth、task / session、SSE / WebSocket、upload / download。 | PHASE03 已打通 workspace session、file registration、ingest acceptance、task、approval、event/SSE、artifact 和 feedback API surface；durable runtime 与完整 UI 仍是 Target。 |
| Agent Core Runtime | `prepare_context -> plan -> ReAct -> observe -> reflect -> replan -> post_turn_commit`。 | 当前是 `GeneralAgent` single loop + RuntimeTurnLedger + PHASE05 Single Controller harness contract + PHASE06 controller-node durable runtime surface，不是完整 LangGraph runtime。 |
| Context / Memory | Raw Event Log、recent window、task summary、structured memory、Context Pack、review / promotion / decay。 | 当前有 PHASE07 snapshot / SQLModel-backed MemoryEngine runtime surface、九类 taxonomy、governance ledger、sensitive exclusion、promotion / decay / consolidation、Context Pack reasons 和 GeneralAgent 接入，不是生产级 semantic/vector Memory DB。 |
| Capability / Tool | ToolCard / manifest、capability retrieval、policy、approval、executor adapter、sandbox、result normalization。 | 当前有 PHASE08 本地 deterministic Tool Control Plane runtime：ToolCardManifest、executor registry、side-effect matrix、approval gate、credential ref broker、sandbox context、audit trace、workspace event bridge 和最小前端审批卡；生产级 sandbox / vault / network proxy / MCP governance 仍是 Target。 |
| Knowledge / Retrieval | Agentic GraphRAG mode policy、Basic RAG、GraphRAG local/global/drift、retrieval fusion、evidence、citation。 | 当前已有 Agentic Retrieval Router、staged fusion、EvidenceBundle、CitationBuilder、unsupported claim check、GraphRAG index pipeline contract、PHASE05 本地 BM25 / vector / graph index job runtime，以及 PHASE09 Agentic Retrieval / Evidence / Citation runtime；生产级 extraction / RRF / rerank / 外部 index platform 仍是 Target。 |
| Document Ingestion | 多格式解析、OCR/VLM、chunk metadata、ACL 继承、BM25/vector/graph index handoff。 | PHASE04 已固定 parser matrix、Document IR、adapter registry、deterministic Parse Gateway runtime、job status、legacy chunk normalizer 和 index handoff；PHASE05 已消费 handoff 建立本地 index job runtime；生产 parser platform 仍是后续目标。 |
| Security / Governance | 输入检查、PII / 商业机密脱敏、prompt injection 防护、权限、审批、输出 DLP、审计。 | 当前已有 security governance contract；PHASE08 已把 tool approval / sandbox audit 接入本地 tool runtime；真实 rootless / gVisor / Firecracker sandbox、外部 vault / OAuth broker、网络代理和生产级 DLP 仍是 Target / Future。 |
| Trace / Eval | runtime trace、LangSmith 映射、dataset、offline / online eval、retrieval / answer / tool / security 指标。 | 当前有 PHASE10 `ZunoSpan`、LangSmith export adapter、dataset / baseline contract 和 redacted failure evidence；LangSmith 产品化、在线采样和持久 trace store 仍是 Target。 |
| Platform | storage、model gateway、worker、artifact、observability 和 provider。 | 近期保持模块化单体，不写成微服务 Current。 |

## 目标架构细化

Zuno 的目标架构可以理解为“单控制器运行时 + 多平面支撑”。单控制器不是简单聊天循环，而是一个能在企业知识库场景里持续做上下文准备、任务规划、工具选择、检索决策、证据检查、质量反思、计划修正和结果提交的运行时。多平面支撑不是微服务拆分，而是把文档解析、知识检索、记忆、工具、安全、评测和平台基础设施各自的责任边界讲清楚。近期实现仍应保持模块化单体，先把内部 contracts、tests、trace 和 verifier 做稳，再决定哪些能力需要 worker、队列或独立服务。

最新研究报告 `zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30` 是本轮详细度基准。本文吸收它的核心结构：User Experience、API & Session、Agent Runtime、Memory & Context、Capability / Tool、Knowledge & Retrieval、Document Ingestion、Security & Governance、Eval & Observability 九个目标平面，以及 Platform / Infra 作为支撑平面。后文所有图和实施计划都围绕这九个平面展开，而不是只停留在“Agent + Tool + Memory + RAG”的粗粒度框架。

### 架构详细度基准与吸收范围

本文的详细度基准是用户 2026-06-30 提供的《Zuno 企业私有知识 Agent Workspace 目标架构与实施报告》。该报告不是历史附件里的普通参考材料，而是本轮目标架构刷新和大型 implementation program 的设计基准。正式架构文档必须至少覆盖报告中的全部主线，并在仓库语境下补足以下内容：Current / Target 边界、Zuno 已有代码路径、目标代码树、程序化 phase、验证入口、文档同步规则和 HTML 展示关系。

吸收范围分四类：

- **产品主叙事**：Zuno 不再以“本地 RAG demo”叙述，而以“企业私有知识 Agent Workspace”叙述。核心用户是企业内部知识工作者、招聘 / HR、法务、研发、项目团队和安全管理员。核心对象是 workspace、knowledge space、task、session、document、artifact、trace、eval dataset 和 approval decision。
- **目标架构平面**：模型与路由、API / Session、Agent Runtime、Memory / Context、Tool / Capability、Knowledge / Agentic GraphRAG、Document Ingestion、Security / Sandbox、Eval / Observability、Platform / Storage / Worker 都必须成为一等架构平面。任何架构图如果只画 Agent、工具、记忆和知识库四个盒子，都不足以支撑下一阶段落地。
- **实施路线**：下一阶段不是单点补 RAG，而是先治理项目文件夹和代码 ownership，再分阶段补企业场景闭环、解析、runtime、memory、tool plane、Agentic GraphRAG、安全、评测、文档展示和 release closure。
- **验证方式**：目标架构不能只停留在文字。每个 plane 都要给出可落地的 contract、tests / verifier、trace 字段或 eval 指标。尚未实现的内容必须留在 Target；只有代码、测试、trace、eval 或可复现验证证明后才能进入 Current。

因此，本文比研究报告多做三件事。第一，把报告里的设计建议映射到 Zuno 当前前台路径，而不是只保留抽象概念。第二，把每个 plane 的对象、输入输出、失败模式和验收指标写成可执行 program 的前置事实。第三，把架构 Markdown、Agent 镜像和 HTML 生成规则写进同一份文档，避免后续出现“PDF 很详细、仓库正式文档很薄”的二次事实源。

### 成熟度差距矩阵

下面的成熟度不是仓库内置指标，也不是对外发布 benchmark；它是基于当前 README、架构页、program closure、代码目录和已验证 runtime foundation 做出的架构判断。它的作用是帮助下一阶段排优先级，不能被写成 Current 功能完成度。

| 平面 | Current 事实 | Target 能力 | 当前差距 | 第一落地点 |
| --- | --- | --- | --- | --- |
| 文档 / 工作流治理 | `AGENTS.md`、`.agent/`、`docs/architecture/`、历史归档和 verifiers 已形成闭环。 | 文档、计划、HTML、verifier 和 release evidence 随每个 program 自维护。 | 高完成度，但仍要防止研究 PDF 与正式文档脱节。 | 本文与 `.agent/architecture/architecture.md`、HTML 同源；program phase 固定更新规则。 |
| 代码布局治理 | `src/backend/zuno` 顶层六层已收口；legacy alias surface 已集中。 | 六层内部也能表达 ownership，`platform/services`、compat、vendor 和 provider tree 不再混住。 | 中等差距；读者仍会觉得零碎和历史包袱重。 | PHASE02 ownership matrix、compat/vendor 分离、repo structure guard。 |
| API / 产品闭环 | Completion / knowledge query path foundation 存在；PHASE03 已补 workspace product object、request envelope、stream id contract，并打通 session、file、ingest、task、approval、event/SSE、artifact、feedback 后端 runtime surface；PHASE06 已把 runtime snapshot、approval resume 和 cancel 接入 workspace task；PHASE08 已把 tool approval / audit events 接入 workspace task stream；PHASE11 已让 Web workspace Agent 模式消费 file / ingest / task / SSE / approval / artifact / trace-eval / feedback 路径。 | Workspace、task/session、upload、artifact、SSE/WS、download、feedback、trace panel 的生产级 Web/Desktop 闭环。 | 后端 API surface 和 Web 第一版产品闭环已可测；生产级 Desktop、下载体验、长任务恢复提示和外部发布 gate 仍是 Target。 | PHASE03/04/05/06/08/09/10/11 已完成第一版 runtime vertical slice；PHASE12 已完成 release gate。 |
| Agent Runtime | `GeneralAgent` single loop、RuntimeTurnLedger、最小 evidence chain、PHASE05 `zuno.agent.harness` state / node / checkpoint / interrupt / stream event contract、PHASE06 `SingleControllerDurableRuntime` controller-node checkpoint / interrupt / resume / cancel / failure surface 已有。 | LangGraph-compatible durable runtime：durable persistence、真实 interrupt/resume、streaming、plan/replan/reflection 执行、exactly-once tool boundary。 | 中等差距；controller-node durable surface 已定，但不是 production-grade LangGraph current。 | PHASE07/08/09/10 必须消费同一 runtime state / trace contract。 |
| Memory / Context | PHASE07 已有 `MemoryEngine`、`DurableMemoryStore`、`DatabaseMemoryStore`、memory runtime SQLModel tables、Raw Event Log、Recent Window、Task Summary、approved durable memory、candidate review/retrieve、governance ledger、promotion、decay、consolidation、Context Pack renderer 和 include/exclude reasons，并已接入 GeneralAgent post-turn write / pre-context read。 | 生产级 semantic/vector Memory DB、后台 promotion/decay/consolidation job、深度 PII/secret detection、隐私删除平台和 memory eval baseline。 | 中等差距；runtime adapter 已定，生产检索、后台调度和隐私治理仍未成熟。 | PHASE08/09/10 继续消费同一 `trace_id` / `task_id` / source event contract。 |
| Tool Control Plane | PHASE08 已有 `ToolControlPlaneRuntime`、default tool manifests、executor adapter registry、side-effect risk matrix、ApprovalGate、ToolSecurityGate、credential ref broker、sandbox context、NormalizedToolResult、sandbox audit task events 和前端审批卡；PHASE11 已让审批后 snapshot / artifact 刷新进入 Web 产品闭环。 | 生产级 dynamic tool orchestration、rootless / gVisor / Firecracker sandbox、真实网络代理、外部 vault / OAuth credential broker、持久 approval DB、tool trajectory eval。 | 中等差距；本地 deterministic runtime 已定，生产隔离与外部治理仍未成熟。 | PHASE09/PHASE10/PHASE11 消费 side-effect、approval、audit、trace 和 UI feedback 字段。 |
| Knowledge / Agentic GraphRAG | 已有 `AgenticRetrievalRouter`、`ProductMode` / `QueryMethod`、`StagedFusionPlan`、`EvidenceBundle`、`CitationBuilder`、`UnsupportedClaimChecker`、`GraphRAGIndexPipelineContract` 和 trace payload contract；PHASE05 已有 `KnowledgeIndexRuntime` 本地 BM25 / vector / graph index job、manifest、retry、replay 和 retrieval payload；PHASE09 已消费 PHASE05 index runtime 与 evidence、citation、ACL 和 trace 字段。 | 生产级 multi-channel retrieval、GraphRAG extraction、community report、RRF / rerank、外部 index platform、retrieval / citation eval baseline。 | 中等差距；index runtime 第一版已定，但 production fusion / rerank / graph extraction / eval runtime 未成熟。 | PHASE12 已完成 release gate；下一轮继续生产化加深。 |
| Document Ingestion | PHASE04 已有 Parser Capability Matrix、Canonical Document IR、router contract、adapter registry、deterministic Parse Gateway runtime、job status、legacy chunk normalizer、index handoff 和 parser golden fixture replay；PHASE05 已证明 handoff 可进入本地 index job runtime。 | 生产级 parser platform、真实 Docling / MinerU / Unstructured adapter、OCR/layout/table/code chunk 深度抽取、parser queue 和 parser metrics。 | 第一版 runtime owner surface 已完成；生产 parser 平台和队列接入仍未完成。 | PHASE09/10 消费 evidence、citation 和 eval 字段，PHASE12 已完成 release gate。 |
| Security / Governance | PHASE10 已有 `InputSecurityGate`、`RetrievalSecurityGate`、`ToolSecurityGate`、`OutputSecurityGate`、`ToolSecurityProfile`、`SandboxAuditEvent`、redaction helper 和 workspace task security event；PHASE11 已在 Web trace 面板展示 security / failure 状态。 | 真实 sandbox runtime、生产级 approval UI、credential broker、network proxy、生产级 DLP、security eval baseline。 | 中等差距；runtime gate 已接入第一版闭环，但隔离执行和外部治理平台未完成。 | PHASE12 已完成 release gate。 |
| Eval / Observability | PHASE10 已有 OTel / LangSmith-compatible `ZunoSpan` schema、redacted `ZunoSpanBuilder`、`LangSmithExportAdapter`、`EvalDatasetCase`、`ReleaseEvalBaseline` 和 sandbox audit span bridge；PHASE11 已让 Web trace 面板消费 observability snapshot、trace replay source refs 和 release eval 状态。 | 生产级 LangSmith / OTel sink、在线采样平台、持久化 trace store、完整 RAG/answer/agent/security eval dataset、CI release gates。 | 中等差距；第一版 Web 可见 trace/eval 已接通，但持续评测台、统一指标面和外部 sink runtime 未完成。 | PHASE12 已完成 release gate。 |
| Platform / Worker | 模块化单体基础存在；完整 worker/object/vector/graph/provider abstraction 未成熟。 | Local-first modular monolith + optional workers + replaceable storage/model/MCP providers。 | 中等差距；worker / 微服务只能作为 Target/Future 候选，不能写成 Current。 | PHASE02/03/04/10 分别把 storage、jobs、artifact、observability 边界拉清。 |

这张矩阵决定实施顺序：先整理目录和 ownership，再建立产品闭环；先把文档解析和 runtime state 做成可测 contract，再扩大 GraphRAG、Memory、Tool、安全和 eval；最后才把完成事实写回 Current。

### 核心对象模型

Zuno 的目标架构必须围绕企业工作空间里的对象组织，而不是围绕“调用了哪个模型”组织。对象模型是后续 API、trace、memory、tool、GraphRAG 和 eval 的共同语言。

| 对象 | 作用 | 关键字段 | 归属平面 |
| --- | --- | --- | --- |
| `Workspace` | 企业、部门、项目、招聘流程或合同库的隔离边界。 | workspace_id、owner、members、policy_profile、storage_scope、retention_policy。 | API / Session、Security、Platform |
| `KnowledgeSpace` | 一组文档、索引、GraphRAG project 和 citation policy。 | knowledge_space_id、workspace_id、graph_project_id、index_version、acl_policy、citation_policy。 | Knowledge、Document Ingestion |
| `Document` | 原始上传或同步文件的逻辑记录。 | document_id、source_uri、mime_type、hash、parser_result_id、security_label、acl_scope。 | Document Ingestion、Security |
| `DocumentBlock` | 可检索、可引用、可脱敏的最小结构单元。 | block_id、type、text、page、bbox、table_cell、line_range、source_span、confidence。 | Document Ingestion、Knowledge |
| `Session` | 用户和 Agent 的交互上下文。 | session_id、workspace_id、user_id、created_at、active_task_id、policy_context。 | API / Session、Memory |
| `Task` | 一次可追踪、可恢复的目标执行。 | task_id、thread_id、goal、product_mode、status、budget、approval_mode、trace_id。 | API / Session、Agent Runtime |
| `ContextPack` | 每轮送入模型的受控上下文包。 | recent_window、task_summary、selected_memory、retrieval_preview、policy_notes、budget。 | Memory、Agent Runtime |
| `PlanStep` | 计划 / ReAct / replan 的可执行步骤。 | step_id、goal、expected_evidence、allowed_tools、status、observations、retry_count。 | Agent Runtime |
| `ToolCard` | 工具的声明式身份证。 | tool_id、input_schema、output_schema、execution_mode、side_effect_level、approval_policy、sandbox_policy。 | Capability |
| `RetrievalDecision` | Agentic GraphRAG 的路由结果。 | product_mode、candidate_methods、resolved_methods、route_reason、fallback_reason、budget_used。 | Knowledge、Trace |
| `EvidenceBundle` | 进入答案合成的证据包。 | evidence_id、source_blocks、scores、trust_label、citation_refs、unsupported_claims。 | Knowledge、Eval |
| `Artifact` | 任务生成的 Markdown、PDF、JSON、citation bundle 或 trace report。 | artifact_id、task_id、kind、uri、hash、created_by、download_policy。 | API / Artifact、Platform |
| `TraceSpan` | 一次运行的可观测事实单元。 | trace_id、session_id、thread_id、task_id、turn_id、run_id、parent_run_id、run_type、span_kind、inputs、outputs、redacted_payload、latency、cost、policy_decision。 | Eval / Observability、Security |
| `ApprovalDecision` | 高风险工具或输出的人工 / 策略批准记录。 | approval_id、task_id、tool_call_id、risk_reason、decision、approver、audit_note。 | Security、Capability |
| `MemoryCandidate` | 可能进入长期记忆的结构化候选。 | candidate_id、source_trace_id、kind、content、confidence、privacy_label、review_status。 | Memory、Security |

这些对象之间的关系决定了实现路线。`DocumentBlock` 是 retrieval、citation、DLP 和 eval 的共同锚点；`Task` 是 runtime、streaming、artifact 和 trace 的共同锚点；`ToolCard` 是 capability、approval、sandbox 和 audit 的共同锚点；`TraceSpan` 是 eval、debug、release gate 和 resume metric 的共同锚点。缺少这些对象，后续功能会退化成散落的 service 文件。

PHASE03 的 Current 事实已经从 contract 推进到后端 API runtime surface：后端 `zuno.schema.workspace` 暴露 `WorkspaceContract`、`KnowledgeSpaceContract`、`WorkspaceSessionContract`、`WorkspaceTaskContract`、`UploadedFileContract`、`ArtifactContract`、`TraceEventContract`、`CitationContract`、`FeedbackContract`、`WorkspaceTaskBudget`、`WorkspaceOutputContract` 和 `WorkspaceProductStreamEvent`；`src/backend/zuno/api/services/workspace_task_runtime.py` 提供 in-process task runtime surface，覆盖 file registration、ingest acceptance、task create、manual approval wait / resume / reject、event list、SSE stream、artifact read 和 feedback；`src/backend/zuno/api/v1/workspace.py` 暴露对应 route；前端 `apps/web/src/apis/workspace.ts` 已同步类型和 API helpers。这里的 Current 不包含 durable task runtime、真实 parser/index runtime、trace panel 或完整 UI 闭环，这些仍是后续 Target。

### Runtime 契约与事件模型

目标 runtime 不应该只暴露“同步返回一个 answer”的函数。企业知识任务需要被建模为可观测、可暂停、可恢复的任务流。

#### Task request envelope

```json
{
  "workspace_id": "ws_internal_hr",
  "session_id": "sess_20260630_001",
  "user_id": "user_hr_01",
  "goal": "对比这 12 份候选人简历和岗位 JD，生成面试优先级和引用依据",
  "product_mode": "contract_review",
  "knowledge_space_ids": ["ks_resume_2026", "ks_jd_backend"],
  "uploaded_file_ids": ["file_resume_batch_001"],
  "approval_mode": "required_for_risky_tools",
  "budget": {
    "max_steps": 12,
    "max_tokens": 80000,
    "timeout_seconds": 300,
    "cost_ceiling": 2.5
  },
  "output_contract": {
    "format": "markdown",
    "citation_required": true,
    "trace_required": true,
    "artifact_kinds": ["markdown", "pdf", "citation_bundle"]
  }
}
```

#### Runtime state

```json
{
  "task_id": "task_xxx",
  "thread_id": "thread_xxx",
  "trace_id": "trace_xxx",
  "context_pack_id": "ctx_xxx",
  "plan": [
    {
      "step_id": "step_1",
      "goal": "解析岗位 JD 和简历字段",
      "expected_evidence": ["JD 要求", "候选人项目经历", "技能关键词"],
      "allowed_capabilities": ["knowledge.search", "artifact.write"]
    }
  ],
  "current_step": "step_1",
  "observations": [],
  "retrieval_events": [],
  "tool_calls": [],
  "approval_interrupts": [],
  "memory_candidates": [],
  "artifact_refs": []
}
```

#### Event stream

事件流不等于 trace 全量数据。事件流是用户和前端可感知的增量状态；trace 是事后可回放的事实表。推荐第一版事件包括：

- `task_started`：任务创建，返回 task_id、trace_id、workspace_id。
- `context_building`：任务状态进入上下文构建阶段，和 `WORKSPACE_TASK_STATUS_FLOW` 对齐。
- `context_built`：Context Pack 完成，包含 selected memory count、retrieval preview count、policy notes。
- `plan_created`：计划生成，包含 step count、expected artifacts、risk notes。
- `retrieval_started` / `retrieval_completed`：包含 product_mode、candidate methods、resolved method、evidence count、fallback reason。
- `tool_call_requested`：模型建议的工具调用，包含 tool_id、side_effect_level、approval_required。
- `approval_required`：高风险动作进入 human-in-the-loop。
- `tool_call_completed`：工具输出已经 normalized，包含 status、latency、result summary。
- `reflection_completed`：质量检查结果，包含 pass / retry / replan / ask_user。
- `artifact_created`：产物生成，包含 artifact_id、kind、download policy。
- `eval_diagnostic`：评测诊断，包含 citation coverage、faithfulness、security flags。
- `task_completed` / `task_failed` / `task_cancelled`：终态事件。

这个事件模型能把后端 runtime、前端 trace panel、LangSmith-compatible trace、artifact download 和 eval baseline 串起来。当前若只保留同步 answer，后续很难解释任务为什么失败、为什么重试、为什么要求审批、为什么选择 GraphRAG local 而不是 basic。

### Data Contract 细化

#### Canonical Document IR

Document Ingestion 的输出必须是一种稳定 IR，而不是 parser 原生文本。建议最小形态：

```json
{
  "document_id": "doc_xxx",
  "workspace_id": "ws_xxx",
  "source_uri": "uploads/policy.pdf",
  "mime_type": "application/pdf",
  "parser": {
    "name": "pymupdf4llm",
    "version": "target-adapter",
    "confidence": 0.93
  },
  "security": {
    "acl_scope": "workspace:hr",
    "sensitivity": "internal",
    "pii_detected": true
  },
  "blocks": [
    {
      "block_id": "blk_001",
      "type": "paragraph",
      "text": "候选人资料仅限招聘团队内部使用。",
      "page": 3,
      "bbox": [72, 180, 520, 240],
      "heading_path": ["招聘制度", "隐私规则"],
      "source_span": "doc_xxx#page=3&bbox=72,180,520,240",
      "chunk_policy": "semantic",
      "index_targets": ["bm25", "vector", "graph_candidate"]
    }
  ]
}
```

GraphRAG extraction、BM25、vector embedding、citation builder、DLP、eval 都应消费这个 IR。没有统一 IR，后续每个 parser 都会把 source span、表格、页码和 ACL 用不同方式传递，最终破坏引用和安全。

#### ToolCard manifest

```json
{
  "tool_id": "mail.send_draft",
  "display_name": "邮件草拟与发送",
  "description": "根据任务上下文草拟邮件；真正发送需要审批。",
  "capability_tags": ["email", "side_effect", "external_write"],
  "input_schema": {"type": "object", "required": ["to", "subject", "body"]},
  "output_schema": {"type": "object", "required": ["message_id", "status"]},
  "execution_mode": "api",
  "trust_tier": "managed_provider",
  "side_effect_level": "high",
  "permissions_required": ["email:send"],
  "approval_policy": "always_before_send",
  "sandbox_policy": "network_allowlist",
  "credential_policy": "brokered_secret",
  "audit_policy": "full_intent_args_result"
}
```

ToolCard 的关键点不是把工具描述给模型看，而是让 runtime 能在模型输出后做机械判断：是否在 workspace scope 内、是否需要审批、是否允许联网、是否需要 credential broker、是否应该被 sandbox、结果如何标准化、失败是否能 fallback。

#### RetrievalDecision

```json
{
  "product_mode": "auto",
  "need_retrieval": true,
  "candidate_methods": ["basic", "local", "global", "drift"],
  "resolved_methods": ["global", "local"],
  "route_reason": "跨多份制度文档的全局归纳后需要局部证据回填",
  "fallback_reason": null,
  "budget": {"max_chunks": 40, "max_communities": 6, "max_followups": 4},
  "security_scope": {"workspace_id": "ws_xxx", "acl_filter": "user_can_read"},
  "trace": {"router_version": "target-v1", "decision_id": "ret_dec_xxx"}
}
```

这里再次强调：`auto` 是产品模式或请求策略，不是最终 resolved query method。最终方法只能落到 `basic / local / global / drift` 或它们的 staged combination。

#### EvidenceBundle

```json
{
  "evidence_bundle_id": "ev_xxx",
  "task_id": "task_xxx",
  "items": [
    {
      "evidence_id": "ev_1",
      "document_id": "doc_policy",
      "block_id": "blk_001",
      "retrieval_method": "local",
      "score": 0.87,
      "source_span": "doc_policy#page=3",
      "citation_label": "[policy-3]",
      "trust_label": "internal_verified"
    }
  ],
  "coverage": {
    "claims_total": 8,
    "claims_supported": 7,
    "citation_coverage": 0.875
  },
  "unsupported_claims": [
    "候选人 A 曾在某公司担任负责人"
  ]
}
```

EvidenceBundle 的存在让回答合成、引用检查、faithfulness eval、安全审计和用户复盘共用同一证据对象。它比“把 chunks 拼进 prompt”更适合长期项目。

#### LangSmith-compatible span

```json
{
  "trace_id": "trace_xxx",
  "run_id": "run_retriever_001",
  "parent_run_id": "run_agent_001",
  "session_id": "sess_xxx",
  "thread_id": "thread_xxx",
  "run_type": "retriever",
  "name": "agentic_graphrag_router",
  "inputs": {"product_mode": "enhanced", "query": "总结合同风险"},
  "outputs": {"resolved_methods": ["global", "local"], "evidence_count": 12},
  "status": "ok",
  "latency_ms": 384,
  "cost": {"tokens": 0, "usd": 0.0},
  "feedback_stats": {"citation_coverage": 0.92}
}
```

Zuno 可以先用本地 JSONL / database 保存这种 span，再选择性导出到 LangSmith。这样不会把正式事实源锁定在外部 SaaS，也能使用 LangSmith 的 dataset、experiment、online evaluator 和 trace UI。

### 运行失败模式与治理策略

企业私有知识 Agent 的失败模式不能只归因于“模型不聪明”。常见失败应在架构中提前建模：

| 失败模式 | 根因 | 检测信号 | 治理策略 |
| --- | --- | --- | --- |
| 检索不到证据 | 文档未解析、ACL 过滤过严、query method 选择错误、索引版本旧。 | evidence_count 低、fallback_reason、citation coverage 低。 | Router fallback、ask user、index freshness check、global -> local/basic staged retry。 |
| 引用不闭合 | chunk 没有 source span、答案合成脱离证据、LLM 编造。 | unsupported_claims、citation coverage 低、faithfulness 低。 | Evidence check gate、unsupported claim rewrite、禁止无证据事实口吻。 |
| 工具误调用 | 工具描述模糊、权限没过滤、side effect 未分级。 | tool_call_requested 与 policy decision 不匹配。 | ToolCard schema、selector filter、approval_required、tool eval。 |
| Prompt injection | 外部文档或网页包含恶意指令。 | untrusted content 中出现 system override、secret exfiltration 语句。 | 内容标签、指令隔离、tool gate、least privilege、audit trace。 |
| 泄露隐私 / 商业机密 | PII 未脱敏、跨 workspace 检索、输出 DLP 缺失。 | output_dlp_violation、retrieval_acl_denied、redaction_miss。 | 输入/检索/输出三层 DLP、workspace scope、credential broker。 |
| 长任务跑偏 | plan 过长、局部 ReAct 追逐噪声、没有 reflection stop rule。 | step_count 过高、重复 tool call、budget exhaustion。 | plan budget、reflection gate、replan threshold、task cancel/resume。 |
| 记忆污染 | 误把临时信息、敏感信息或错误结论写入长期记忆。 | memory_candidate confidence 低、privacy label 高、conflict detected。 | review/promotion/decay、sensitive memory suppression、source trace binding。 |
| 评测不可复现 | trace 字段不全、dataset 未版本化、线上样本没回流。 | missing run_id、missing version、eval drift。 | LangSmith-compatible schema、本地 release baseline、dataset versioning。 |

这些失败模式应进入 tests / eval / verifier，而不是只写在风险说明里。PHASE10 以后，release gate 至少应能回答：这次改动有没有降低 citation coverage、有没有让 auto router 更爱误选 global、有没有让高风险工具绕过 approval、有没有让 prompt injection 测试漏过。

### 多 Agent 与多线程执行边界

Zuno 产品 runtime 的近期主线仍是 Single Controller Agent。工程交付中的 Codex 多 agent / 多 worktree 不是产品多 Agent 架构。两者必须在文档里分开：

- **产品 runtime**：默认一个 Controller Agent 管理计划、检索、工具、审批、记忆和输出。子 Agent 只作为未来可选 delegated worker 或 capability 进入，不作为近期默认架构。
- **工程执行模式**：大型 program 可以拆成多个 Codex worker，在独立 worktree 和独立 `codex/` 分支上并行处理 docs、runtime、memory、tool、security、eval 等互不重叠范围。

如果未来打开产品多 Agent，也必须满足三个条件：任务确实需要角色分工；子 Agent 的输入输出、权限和 trace 可以被 Controller 管住；失败和成本可评测。否则，多 Agent 只会增加不可控性，而不是提升企业可信度。

### 第一版落地范围

第一版落地不应追求“所有目标一次完成”。建议按最短能证明产品价值的切片推进：

1. **文档摄取**：支持 PDF、DOCX、MD、TXT、代码文件和图片 OCR 的第一批完整 parser matrix，输出 Canonical Document IR。
2. **检索问答**：normal 强制 basic；enhanced 让 Agentic Retrieval Router 在 basic/local/global/drift 中选择；auto 先判断是否检索。
3. **证据链**：每个回答输出 evidence bundle、citation coverage、unsupported claim diagnostics。
4. **任务闭环**：task/session/event/artifact 可运行闭环，至少一种 SSE 或 WebSocket 实时事件。
5. **工具动作**：先接 read_file、graphrag_query、run_python_sandbox、send_email_draft 四类工具；真正 send 默认审批。
6. **安全闸门**：输入、检索、工具、输出四道闸先有 contract 和 regression tests。
7. **评测台**：本地 offline eval + LangSmith-compatible export，先测 retrieval relevance、citation coverage、faithfulness、tool trajectory、approval compliance。

这个范围足以支撑企业内部文档知识库 + 多功能助手的 demo，也能给简历提供量化指标。完整 Neo4j、完整微服务、完整多 Agent 编排或全量在线监控都属于 Target/Future 候选，不能写成 Current，也没有必要第一版就引入。

### 企业私有知识场景平面

产品主场景是企业内部文档知识库与多功能 Agent 助手。它不是“用户问一句，向量库召回几段，然后模型回答”的普通 RAG demo，而是围绕企业工作空间组织知识、任务、权限、文件、产物和审计。一个 workspace 可以绑定部门、项目、合同库、简历库、制度库或研发知识库；一个 knowledge space 管理文档集合、GraphRAG project、索引版本、ACL 和 citation policy；一个 tool space 管理搜索、数据库、邮件、文件、浏览器、CLI、MCP 和内部 API 等动作能力。

这个场景决定了 Zuno 不能只优化答案质量，还要关心文件从哪里来、谁有权看、解析是否保留页码和表格、检索结果是否可引用、工具动作是否需要审批、输出是否泄露隐私或商业机密、trace 能不能复盘。企业用户真正需要的是“可理解、可追溯、可执行、可评测、可治理”的知识工作台。问答只是入口，后续还要支持制度解释、文档对比、合同审查、候选人简历匹配、项目复盘摘要、竞品报告、邮件草拟、表单填充和报告产物下载。

### API / Session / Artifact 平面

API 层的目标不是只提供 completion endpoint，而是形成 task / session / artifact / event 的产品闭环。任务启动时，API 应创建会话、绑定 workspace scope、记录用户身份和权限上下文，并把上传文件、选定知识库、product mode、query method preference、工具授权策略写入 request envelope。运行过程中，SSE 或 WebSocket 推送 planning、retrieval、tool_call、approval_required、artifact_created、eval_diagnostic 和 error 等事件。运行结束后，artifact list / download 提供 Markdown、PDF、JSON、citation bundle 和 trace report。

这个平面是 deepsearch 类产品看起来“完整”的原因，也是 Zuno 下一阶段补产品感的关键。它不是近期 Current，也不要求立即做复杂微服务；但要求后端 contracts 把 session id、task id、trace id、artifact id、workspace id 和 graph project id 串起来。没有这层，LangSmith trace、文档解析、工具审批和产物下载都会各自存在，不能形成用户能感知的闭环。

#### API / Session / Task / Artifact / Event Contract

目标 API 契约应按“任务生命周期”组织，而不是按“聊天接口”组织。第一版建议 endpoints 如下：

| Endpoint | 目标职责 | 输出 / 事件 | Current 边界 |
| --- | --- | --- | --- |
| `POST /v1/workspaces` | 创建或绑定企业知识工作空间。 | workspace_id、policy_profile、default_knowledge_space。 | Target。 |
| `POST /v1/sessions` | 创建用户会话，绑定 workspace、user、policy context。 | session_id、thread_id、trace_root。 | Target。 |
| `POST /v1/files` | 上传文档、图片、代码包或临时附件。 | file_id、mime_type、security_label、parse_status。 | Target。 |
| `POST /v1/knowledge-spaces/{id}/ingest` | 将文件放入 Parse Gateway 和 index job。 | ingest_job_id、parser_route、index_targets。 | Target。 |
| `POST /v1/tasks` | 启动 Agent task，包含 product_mode、budget、approval_mode。 | task_id、trace_id、event_stream_url。 | Target。 |
| `GET /v1/tasks/{task_id}` | 查询任务状态、当前 step、approval pending、artifact refs。 | task status envelope。 | Target。 |
| `GET /v1/tasks/{task_id}/events` | SSE 事件流。 | task_started、plan_created、retrieval_completed 等。 | Target，第一版可优先选 SSE。 |
| `WS /v1/tasks/{task_id}/ws` | 双向事件和用户中断。 | event stream + user approval / cancel。 | Target，若第一版选 SSE，则 WS 后置。 |
| `POST /v1/tasks/{task_id}/approve` | 人工批准高风险工具动作。 | approval_decision、resume_token。 | Target。 |
| `POST /v1/tasks/{task_id}/cancel` | 取消长任务。 | task_cancelled event。 | Target。 |
| `GET /v1/artifacts/{artifact_id}` | 下载报告、PDF、citation bundle、trace report。 | artifact payload / signed local path。 | Target。 |
| `POST /v1/feedback` | 用户反馈写回 eval dataset 候选。 | feedback_id、dataset_candidate_id。 | Target。 |

第一版建议优先落地 SSE，而不是同时实现 SSE 和 WebSocket。原因是任务进度、检索事件、工具事件、artifact_created 和 eval_diagnostic 都是 server-to-client 主导；审批可以通过单独 `POST approve` 完成。WebSocket 更适合后续需要低延迟双向控制、实时协作或多步骤人工输入时再打开。无论选择 SSE 还是 WebSocket，trace schema 必须相同，不能让传输协议成为事实源。

#### Runtime Task API、事件流与失败恢复

Task 状态机建议从第一版就固定：

```text
created
  -> context_building
  -> planning
  -> running
  -> approval_waiting
  -> resuming
  -> finalizing
  -> completed | failed | cancelled
```

失败恢复要和状态机一起设计。`context_building` 失败通常是权限、文件解析或 memory read 错误；`planning` 失败通常是模型输出不合 schema 或预算不足；`running` 失败可能来自工具、检索、沙箱、网络或 provider；`approval_waiting` 卡死需要超时和 reminder；`finalizing` 失败可能是 artifact render、citation coverage 或 output DLP 阻断。每一种失败都应有 `failure_reason`、`recoverable`、`resume_token` 和 `user_action_required` 字段。

推荐事件 envelope：

```json
{
  "event_id": "evt_xxx",
  "task_id": "task_xxx",
  "trace_id": "trace_xxx",
  "type": "retrieval_completed",
  "timestamp": "2026-06-30T12:00:00Z",
  "status": "ok",
  "payload": {
    "product_mode": "enhanced",
    "resolved_methods": ["global", "local"],
    "evidence_count": 12,
    "citation_coverage": 0.92
  }
}
```

Task API 的验收不是“接口能返回 200”，而是同一个 task 能从 session、context、retrieval、tool、approval、artifact、trace、eval 全链路回放。PHASE03 应把这套契约作为后端产品闭环的验收表。

### Single Controller Agent Runtime 平面

规划模块在 Zuno 里不应被画成独立于 Agent 的第五个大脑，而应落在 Single Controller Agent Runtime 内部。目标状态机是：

```text
prepare_context
  -> intent_and_policy_route
  -> plan
  -> act_react_loop
  -> observe
  -> evidence_check
  -> reflect
  -> replan_if_needed
  -> answer_or_artifact
  -> post_turn_commit
```

`plan` 负责把复杂目标拆成可执行步骤；`act_react_loop` 负责单步工具调用、检索和观察；`reflect` 负责检查当前答案是否有足够证据、格式是否正确、是否可能泄密或越权；`replan_if_needed` 在检索不足、工具失败或用户目标变化时重写剩余步骤；`post_turn_commit` 把 trace、artifact、memory candidate、eval diagnostics 和安全审计写回。LangGraph 适合承载这类 runtime，不是因为项目需要“装了 LangGraph”，而是因为 durable execution、interrupt / approval、streaming、checkpoint、resume 和状态图正好对应企业任务运行时的需求。

当前 Zuno 可以说已经有 `GeneralAgent` single loop、RuntimeTurnLedger、最小 evidence chain foundation，`zuno.agent.harness` 中的 Single Controller runtime contract，以及 `zuno.agent.durable_runtime` 中的 controller-node durable runtime surface。PHASE05 固定了 `ControllerRuntimeState`、十个 runtime node contract、checkpoint snapshot、interrupt/resume envelope 和 traceable stream event bridge；PHASE06 在其上补了 `SingleControllerDurableRuntime`、`InMemoryDurableRuntimeStore`、runtime snapshot、approval interrupt、resume、cancel、recoverable / non-recoverable failure，并接入 workspace task。完整 production-grade LangGraph runtime 仍是 Target：现在的 Current 不是已经替换主循环的 LangGraph execution engine，也不是进程重启后的生产持久恢复。近期最短路径不是一开始就做多 Agent，而是先把单控制器的状态、输入输出、事件、失败恢复和审批点做稳。未来如果引入子 Agent，也应该作为工具或 delegated worker，由单控制器管理，而不是让产品架构默认变成多 Agent 混战。

#### Model Gateway 与模型路由策略

Agent Runtime 不能把“模型”理解成一个固定 chat completion provider。目标上至少要区分 planner model、executor model、critic / reflection model、embedding model、rerank model、OCR / vision model 和 optional local model。不同模型进入不同节点：

| 模型角色 | 使用节点 | 目标能力 | 第一版策略 |
| --- | --- | --- | --- |
| Planner model | `plan` / `replan` | 拆任务、生成步骤、设置 evidence expectation。 | 可与 executor 共用同一模型，但 trace 中标记 run_type。 |
| Executor model | `act_react_loop` | 工具选择、检索决策、答案草拟。 | 当前 GeneralAgent foundation 逐步迁移。 |
| Critic model | `reflect` | 质量检查、unsupported claim、DLP 初筛、格式校验。 | 可先用同模型 + evaluator prompt。 |
| Embedding model | ingestion / retrieval | chunk embedding、memory retrieval。 | provider adapter，不写死 vendor。 |
| Rerank model | retrieval fusion | rerank 或 evidence precision 提升。 | Target；第一版可 optional。 |
| Vision / OCR model | Parse Gateway | 图片、扫描件、图表、公式辅助解析。 | Target candidate，不写成 Current。 |

Model Gateway 的职责是把 provider、模型配置、成本预算、超时、重试、日志脱敏、token / cost 统计和 fallback 封装起来。Agent Runtime 只表达“需要 planner / executor / critic”，不直接依赖某个 provider。这样后续本地模型、API 模型、混合部署和评测实验才能替换。

#### Runtime 节点输入输出

| 节点 | 输入 | 输出 | Trace span | 失败处理 |
| --- | --- | --- | --- | --- |
| `prepare_context` | task request、session、workspace policy、memory read、uploaded files。 | ContextPack。 | `chain:prepare_context`。 | 缺权限或 context 过大时进入 ask_user / fail。 |
| `intent_and_policy_route` | goal、ContextPack、product_mode。 | intent、risk notes、retrieval need、allowed capabilities。 | `chain:route`。 | schema fail 时重试一次，否则 fallback。 |
| `plan` | goal、intent、ContextPack、budget。 | PlanStep list / DAG。 | `llm:planner`。 | plan 过深时压缩或询问用户。 |
| `act_react_loop` | current step、allowed tools、memory、retrieval state。 | tool call / retrieval call / draft answer。 | `chain:react_step`。 | step budget 限制，重复调用检测。 |
| `observe` | tool / retrieval result。 | normalized observation。 | `tool` / `retriever` child span。 | error -> retry / fallback / replan。 |
| `evidence_check` | draft claims、EvidenceBundle。 | supported / unsupported claims。 | `chain:evidence_check`。 | unsupported -> rewrite or retrieve more。 |
| `reflect` | observations、draft、policy、budget。 | continue / replan / finish / ask_user。 | `llm:critic`。 | critic fail 不直接放行高风险输出。 |
| `post_turn_commit` | final answer、trace、artifact refs、memory candidates。 | committed trace、memory review items、artifact metadata。 | `chain:post_turn_commit`。 | commit fail 可返回答案但标记 partial_commit。 |

PHASE05 已把 LangGraph-compatible harness 的最小契约落到 `src/backend/zuno/agent/harness.py`：这些节点可以成为 state graph nodes，checkpoint snapshot 绑定 `trace_id` / `task_id` / `thread_id`，interrupt envelope 绑定 approval reason，stream event bridge 统一输出 runtime node event。PHASE06 进一步把 `src/backend/zuno/agent/durable_runtime.py` 做成 controller-node runtime owner surface：同一 task 可以启动、写 checkpoint、进入 approval interrupt、批准后从 checkpoint resume、cancel、记录 recoverable / non-recoverable failure，并通过 `WorkspaceTaskRuntimeService` 暴露 runtime snapshot。仍然不能把它写成完整生产 runtime；真实 durable persistence、进程重启恢复、exactly-once tool execution、approval UI 和主循环深度切换仍是后续 Target。

### Context / Memory 平面

Memory 不是“把历史聊天塞进 prompt”。Zuno 的目标记忆层至少分五类：Raw Event Log、Recent Window、Task Summary、Structured Long-term Memory 和 Model Context Pack。Raw Event Log 是可审计的原始事件账本；Recent Window 是当前任务短期上下文；Task Summary 是压缩后的阶段状态；Structured Memory 是经过 review / promotion 的长期事实、偏好、项目状态或经验；Model Context Pack 是每轮真正喂给模型的受控上下文包。

记忆压缩应按风险和用途分层。滑动窗口只解决 token 预算；摘要压缩解决长任务连续性；结构化抽取解决可检索、可审计和可更新；反思型记忆解决失败经验和工具偏好沉淀。企业场景里，长期记忆还必须绑定 workspace、user、project、source、confidence、privacy label、retention policy 和 last_verified_at。敏感记忆不能因为“对回答有用”就自动进入 prompt；它必须经过权限检查、脱敏策略和上下文预算策略。

当前 Zuno 的 Context / Memory 已从 foundation 推进到 PHASE07 runtime surface：`MemoryEngine` 能写 raw event、构造 recent window、生成 task summary、抽取候选记忆、review approved durable memory、检索 approved memory、渲染带 include/exclude reason 的 Context Pack；`DurableMemoryStore` 支持 snapshot / replay；`DatabaseMemoryStore` 通过 SQLModel 表持久化 raw event、task summary、candidate、review decision 和 governance ledger；`GeneralAgent` 已通过 `MemoryEngine` 做 post-turn write 与 pre-context read。production-grade semantic/vector memory retrieval、后台 consolidation / decay scheduler、深度 PII/secret detection、隐私删除平台和正式 memory eval baseline 仍是 Target。

#### Context Builder、九类 Memory 与写入契约

正式目标中，Memory 至少拆成九类对象，而不是泛泛一个“长期记忆”：

| Memory 类型 | 内容 | 是否默认进 prompt | 风险控制 |
| --- | --- | --- | --- |
| Raw Event Log | 每次 user、model、tool、retrieval、approval、artifact、eval 原始事件。 | 否。 | 只用于审计、replay、eval；不直接送模型。 |
| Working Memory | 当前 step 的临时观察和中间结果。 | 是，但只在当前 task。 | task 完成后不自动长期保存。 |
| Recent Window | 当前会话短期消息窗口。 | 是，按 token budget 裁剪。 | 敏感内容先脱敏或 scope check。 |
| Task Summary | 长任务阶段摘要。 | 是。 | 摘要需绑定 source trace 和 confidence。 |
| Episodic Memory | 过去任务经验、用户偏好、项目上下文。 | 条件进入。 | workspace/user scope、freshness、privacy label。 |
| Semantic Memory | 稳定事实、实体、术语、项目知识。 | 条件进入。 | 需要 evidence/source binding。 |
| Procedural Memory | 工具使用偏好、失败修复经验、workflow lesson。 | 条件进入。 | 不能覆盖安全 policy。 |
| Graph Memory Candidate | 从交互或文档中抽取的实体关系候选。 | 不直接进入。 | 需 review / promote 到 graph 或 knowledge layer。 |
| Model Context Pack | 本轮实际送模型的上下文组合。 | 是。 | 可解释 included/excluded reason。 |

Memory write contract：

```text
raw events
  -> candidate extraction
  -> sensitivity labeling
  -> dedupe / conflict check
  -> source binding
  -> human or policy review
  -> promote | decay | discard
  -> retrieval policy for future context pack
```

Memory API 建议：

```text
append_event(event)
build_recent_window(session_id, budget)
summarize_task(task_id, policy)
extract_memory_candidates(trace_id)
review_memory_candidate(candidate_id, decision)
retrieve_memory(query, workspace_id, user_id, filters, budget)
render_context_pack(task_request, memory_selection, retrieval_preview, policy_notes)
```

Memory eval 不能只测“能不能召回”。它还要测 over-retention、敏感信息误入 prompt、过期信息未衰减、冲突记忆未标记、无 source 的长期事实被使用。企业场景里，记住错误信息和泄露敏感信息一样危险。

### Document Ingestion / Parse Gateway 平面

企业知识库的质量首先取决于文档摄取，而不是检索算法。目标 Parse Gateway 应负责格式识别、parser routing、OCR / layout、结构抽取、chunk、metadata、ACL 继承、provenance 和 index handoff。它的输出不应是一段裸文本，而应是 Canonical Document IR，例如 document、section、page、paragraph、table、image、code_block、metadata、source_span 和 acl_scope 组成的结构化对象。

最低支持矩阵应覆盖 PDF、DOCX、PPTX、XLSX、TXT、MD、HTML、CSV / JSON、图片 / 扫描件和代码文件。PDF 需要页码、bbox、表格和 OCR fallback；Office 文件需要 heading、slide、sheet、table 和批注；Markdown / HTML 需要标题层级和链接；代码文件需要语言、路径、symbol、line range 和代码感知切块；图片需要 OCR 文本、视觉描述、bbox 和 confidence。Docling、PyMuPDF4LLM、MarkItDown、Unstructured、OCR / VLM 可以作为 adapter 候选，但 Zuno 自己要维护统一的 ParseRequest、ParseResult、Document IR、parser capability matrix 和 golden tests。

最新报告把 parser router 拆得更具体：TXT / MD / Code / HTML 走 native parser；复杂 PDF、表格和版面信息优先走 Docling / PyMuPDF4LLM；扫描件、公式、图表和 OCR-heavy 材料进入 MinerU / PaddleOCR-VL / VLM 路径；长尾办公格式用 Unstructured 或 MarkItDown 补齐。所有 parser 的输出都必须归一到结构化 Markdown / JSON，并保留 block-level provenance：文件 id、页码、bbox、表格单元、章节层级、parser id、confidence 和 ACL scope。GraphRAG indexing、citation、security DLP 和 eval 都只能消费这个统一 IR，而不是直接消费 parser 原始输出。

这就是为什么 Document Ingestion 不能继续隐含在工具层里。工具层负责“怎么调用解析器”，但知识系统需要“解析后的结构如何进入 BM25、vector、graph、citation 和 eval”。如果解析阶段没有保留 page、table、source span 和 ACL，后面的 citation、DLP、GraphRAG entity extraction 和 answer grounding 都会变弱。

#### Parse Gateway Parser Matrix 与 Document IR Contract

PHASE04 当前已经把 parser matrix、Document IR、router contract、adapter registry、deterministic Parse Gateway runtime、parser diagnostics、job status、legacy chunk normalizer 和 index handoff 固定在 `src/backend/zuno/knowledge/ingestion/`，并用 `tests/knowledge/test_document_ingestion_contract.py`、`tests/knowledge/test_parse_gateway_runtime.py` 与 `tests/fixtures/parser_golden/manifest.json` / `tests/fixtures/parser_golden/inputs/` 证明可复现。这里的 Current 是“Parse Gateway runtime owner surface 已可测”，不是“生产级 Docling / MinerU / Unstructured 平台已经迁移完成”。

| format | default_parser | fallback | structure_kept | evidence_anchor | tests |
| --- | --- | --- | --- | --- | --- |
| pdf | docling_pymupdf | mineru_ocr_vlm | pages、tables、layout | page、bbox、section_path | pdf_table |
| scanned | mineru_ocr_vlm | docling_pymupdf | pages、figures、ocr_text | page、bbox | scanned_image |
| image | mineru_ocr_vlm | unstructured_markitdown | figures、ocr_text | bbox | scanned_image |
| docx | unstructured_markitdown | native | headings、tables | section_path、table_cell | docx_heading_table |
| pptx | unstructured_markitdown | mineru_ocr_vlm | slides、figures | slide、bbox | pptx_slide |
| xlsx | unstructured_markitdown | native | sheets、tables | sheet、table_cell | xlsx_sheet |
| txt | native | unstructured_markitdown | plain_text | line_range | code_file |
| md | native | unstructured_markitdown | headings、links | line_range、section_path | markdown_link |
| csv | native | unstructured_markitdown | rows、columns | line_range、table_cell | xlsx_sheet |
| json | native | unstructured_markitdown | keys、paths | line_range、section_path | code_file |
| html | native | unstructured_markitdown | headings、links、tables | section_path、line_range | markdown_link |
| code | native | unstructured_markitdown | line_numbers、symbols | line_range | code_file |

Parser routing policy：

```text
detect mime/hash/size
  -> validate file and security label
  -> select parser by capability matrix
  -> run parser in sandbox if heavy/untrusted
  -> normalize to Document IR
  -> attach ACL and provenance
  -> emit index payloads
  -> emit parser metrics and failure examples
```

PHASE04 的验收不能只看“解析出文本”，而要看 Document IR 是否能同时支持 BM25、vector、GraphRAG extraction、citation、DLP 和 eval。

### Tool Control Plane 平面

工具层按 capability domain 治理，不按 API / SDK / CLI / MCP 这些执行方式拆顶层业务分类。搜索、文件、数据库、邮件、浏览器、代码执行、知识库查询和内部系统访问是 capability；local function、SDK、HTTP API、CLI、SSH、MCP stdio、MCP HTTP 是 executor adapter。ToolCard 是工具的声明式身份证，运行时代码只是其中一个执行后端。

目标 ToolCard 至少需要 tool_id、display_name、description、input_schema、output_schema、capability_tags、execution_mode、trust_tier、side_effect_level、permissions_required、workspace_scope、rate_limit、timeout、cost_hint、secrets_required、approval_policy、audit_policy、failure_modes 和 result_normalizer。Tool Router 的顺序应是作用域过滤、权限过滤、trust tier 过滤、side-effect 分级、健康检查、成本 / 延迟策略、schema compatibility 和 fallback。高副作用工具，例如 send_email、外部写数据库、SSH、删除文件或覆盖产物，默认进入 approval / interrupt / resume 流程。

当前已有 ToolCard compact metadata、Native BM25 ToolCard retrieval、MCP/local tool policy trace、capability selection trace bridge，以及 PHASE08 的本地 deterministic Tool Control Plane runtime：`ToolControlPlaneRuntime` 能从 `ToolCardManifest` 选择 executor，复用 `ApprovalGate` / `ToolSecurityGate`，注入 credential reference，构造 sandbox context，执行只读工具，拦住或等待高副作用工具审批，并把 `tool_call`、`sandbox_audit`、`approval_required`、`tool_result` 写入 workspace task event stream；Web workspace 已有最小工具审批卡调用 `approveWorkspaceTaskAPI`。完整动态工具编排、rootless / gVisor / Firecracker sandbox、真实网络代理、外部 vault / OAuth broker、持久 approval DB 和真实 MCP runtime governance 仍是 Target。

#### ToolCard v1 Schema、风险矩阵与注册 UX

ToolCard v1 目标字段：

| 字段 | 作用 |
| --- | --- |
| `tool_id` | 稳定工具 id，不能用展示名代替。 |
| `owner` | 维护方：core、workspace_admin、external_provider、mcp_server。 |
| `capability_domain` | file、knowledge、mail、database、browser、code、shell、internal_api。 |
| `description_for_model` | 给模型看的短描述，禁止包含 secrets。 |
| `description_for_user` | UI 展示说明。 |
| `input_schema` / `output_schema` | JSON schema，用于校验和 result normalization。 |
| `execution_mode` | local_function、api、local_cli、ssh、mcp_local、mcp_remote、sandbox。 |
| `trust_tier` | core_trusted、workspace_trusted、third_party_reviewed、untrusted。 |
| `side_effect_level` | none、read、write_local、write_external、destructive。 |
| `approval_policy` | never、on_high_risk、always、admin_only。 |
| `sandbox_profile` | none、workspace_ro、workspace_rw、network_limited、microvm_candidate。 |
| `credential_policy` | none、brokered_secret、user_oauth、service_account。 |
| `network_policy` | deny、allowlist、workspace_proxy、external_provider。 |
| `audit_policy` | none、intent_only、args_redacted、full_intent_args_result。 |
| `budget` | timeout、max_calls、max_cost、rate_limit。 |
| `failure_modes` | timeout、empty_result、permission_denied、schema_error、provider_error。 |

风险矩阵：

| side effect | 示例 | 默认审批 | 默认沙箱 | 备注 |
| --- | --- | --- | --- | --- |
| `none` | format_json、citation_check | 否 | 否 | 纯计算、无外部读写。 |
| `read` | search_knowledge_base、read_file | 按 ACL | workspace_ro | 需要 scope 和审计。 |
| `write_local` | generate_markdown、save_artifact | 低风险可免批 | workspace_rw | 只能写 artifact 区。 |
| `write_external` | send_email、create_ticket、update_crm | 是 | network_limited | 默认 interrupt + approval。 |
| `destructive` | delete_file、drop_table、overwrite_repo | 是，且 admin_only | 强沙箱 / 默认禁用 | 第一版不开放自动执行。 |

首批演示工具建议：

- `file.read_scoped`：只读 workspace 文件，验证 ACL 和 path scope。
- `knowledge.agentic_graphrag_query`：GraphRAG / basic 检索工具，返回 EvidenceBundle。
- `code.run_python_sandbox`：受限 Python 执行，用于表格处理和小脚本，不给 secrets，不默认联网。
- `mail.draft_and_send`：草拟可自动，真正发送必须 approval。

用户注册 UX 目标：管理员上传或启用工具时，必须选择 capability domain、execution mode、trust tier、side effect、credential policy 和 approval policy。系统根据 ToolCard 自动生成风险提示和测试清单。模型不能绕过 ToolCard 直接请求执行任意命令。

#### MCP Trust Governance 与 Tool Sandbox Profiles

MCP 是一种 executor / provider 边界，不是“安全默认可信工具库”。Zuno 应把 MCP server 拆成 local stdio、local HTTP、remote HTTP 三类，并要求：

- 明确 server trust list，未注册 server 不可被模型发现。
- 每个 server 声明 allowed tools、scopes、transport、auth、origin policy 和 data egress policy。
- remote MCP 使用 OAuth / token audience / PKCE 等授权能力时，Zuno 只保存 brokered credential，不把 token 放进 prompt。
- MCP 工具返回内容默认视为 untrusted external content，进入 prompt 前要做 content labeling 和 instruction isolation。
- local MCP server 如果能访问文件系统、网络、shell 或 secrets，必须进入 workspace / execution / network sandbox。

Sandbox profiles：

| Profile | 目标 | 默认限制 |
| --- | --- | --- |
| `workspace_ro` | 只读企业文件或上传文件。 | path allowlist、no write、no secrets。 |
| `workspace_rw_artifacts` | 生成报告和中间产物。 | 只能写 artifact/tmp，禁止改源码和原始知识库。 |
| `network_limited` | 邮件、内部 API、受控 HTTP。 | domain allowlist、proxy、credential broker。 |
| `execution_restricted` | Python/CLI/解析器重任务。 | timeout、CPU/memory、cwd、no raw secrets、audit。 |
| `microvm_candidate` | 高风险代码执行或不可信工具。 | gVisor / Firecracker 候选，不写成第一版 Current。 |

这些技术名是候选方案，不是 Current。第一版可以先用本地受限执行、路径 allowlist、timeout、credential broker stub 和 audit trace 建立 contract，再根据风险升级 rootless container、gVisor 或 Firecracker。

### Knowledge / RAG / GraphRAG 平面

Zuno 的目标不是“普通 RAG 加一个 GraphRAG 按钮”，而是 **Agentic GraphRAG**。用户只需要理解产品模式：`normal`、`enhanced`、`auto`。底层 `basic / local / global / drift` 是 Agent 和 Query Router 的内部检索通道，不应直接暴露成主用户心智。

三种产品模式的边界必须清楚：

- `normal`：强制走 `basic`，也就是低延迟、可预测的传统混合 RAG 路径，面向精确问答、条款定位、制度查找和普通知识库问答。
- `enhanced`：一定检索，但由 Agentic Retrieval Router 根据问题类型、上下文、预算和证据状态选择 `basic / local / global / drift` 中的一个或多个通道。用户选择的是“增强推理与更强证据”，不是手动选择某个 GraphRAG 子算法。
- `auto`：Agent 先判断是否需要检索；如果不需要，直接回答或执行轻量任务；如果需要，再进入 Agentic Retrieval Router 选择 `basic / local / global / drift`。证据不足时可以升级检索通道、重试、replan 或要求补充输入。

内部通道的语义也要保持分层。`basic` 适合精确片段问答、合同条款查找、制度定位和低延迟回答，目标是 BM25 + dense vector + metadata filter + RRF + optional rerank。`local` 是 GraphRAG 的局部图谱路径，适合围绕实体、关系、人物、项目、条款或组织局部邻域的问题。`global` 是 GraphRAG 的社区/摘要路径，适合跨文档主题、社群摘要和全局 sensemaking，它应作为 community-level prior，而不是和 chunk-level BM25 结果直接硬混排。`drift` 是 Agentic GraphRAG 的复杂研究路径，先用 global primer 形成主题和子问题，再用 local / basic 回补可引用证据。

因此，Zuno 的 Knowledge 平面应该表达成两层：第一层是用户可见的产品模式策略，第二层是 Agent 可调度的 retrieval method。Agentic GraphRAG 的价值不在于把四个检索按钮摆给用户，而在于让 Single Controller Agent 根据任务、证据、成本和安全策略动态选择、组合、升级或回退检索通道。

Evidence / Citation 是 RAG 产品化的底座。检索结果进入答案前，应经过 evidence bundle 构造、citation coverage 检查、source trust label、ACL check、freshness check 和 answer grounding check。没有证据的答案可以草拟，但不能伪装成已引用知识库结论。对于企业知识库，引用不仅是“好看”，还是审计、合规、复盘和 eval 的入口。

当前 Zuno 有 KnowledgeQueryService、GraphRAGQueryService、GraphRAGProjectSnapshot、KnowledgeQueryResult、query_method trace、citation contract foundation，PHASE08 的 `AgenticRetrievalRouter`、`StagedFusionPlan`、`EvidenceBundle`、`CitationBuilder`、`UnsupportedClaimChecker`、`GraphRAGIndexPipelineContract` 和 `AgenticGraphRAGTrace`，以及 PHASE05 的 `KnowledgeIndexRuntime` 本地 BM25 / vector / graph index job runtime。生产级 LLM-first entity / relation extraction、community report 生成、完整 RRF / rerank、外部 GraphRAG index platform 和 eval baseline 仍是 Target。

#### GraphRAG Index Pipeline、Evidence Bundle 与 Citation Schema

Agentic GraphRAG 必须同时有 index side 和 query side。只有 query method contract，不等于成熟 GraphRAG。目标 index pipeline：

```text
Canonical Document IR
  -> TextUnit / Block selection
  -> entity and relation extraction
  -> entity resolution and normalization
  -> relationship validation and confidence scoring
  -> graph upsert
  -> community detection
  -> community report generation
  -> embedding and sparse index update
  -> index manifest and eval sample generation
```

Query pipeline：

```text
product_mode
  -> Agentic Retrieval Router
  -> basic | local | global | drift
  -> staged fusion
  -> evidence bundle
  -> citation builder
  -> unsupported claim check
  -> answer synthesis
```

`global` 的正确位置是 community prior。它先返回主题、community report、子问题或 corpus-level summary，再触发 `local` / `basic` 回补可引用 chunk。直接把 community report 和 BM25 chunk 拉平排一个 top-k，会把全局摘要和局部证据的语义层级混掉。

GraphRAG eval fixture 应覆盖：

- local：给定实体 / 项目 / 条款，能命中邻域关系和原始 chunks。
- global：给定跨文档问题，能命中相关 community reports，并生成子问题。
- drift：global primer 之后能生成 follow-up，再回到 local/basic 找证据。
- fallback：local 命中不足时能退到 basic；global 摘要不足时能要求补证据。
- security：跨 workspace / ACL chunk 不进入 evidence。
- citation：每个关键 claim 至少有 block-level source span。

unsupported claim check 失败时不应直接输出“也许”。建议策略：

```text
unsupported_claims == 0 -> final answer
unsupported_claims <= threshold and retrievable -> retrieve more / rewrite
unsupported_claims > threshold -> ask user or return evidence-limited answer
high_risk_claim unsupported -> block confident wording
```

EvidenceBundle schema 已由 PHASE08 contract 和 tests 固定：同一 query 的 `resolved_methods`、evidence coverage、citation coverage、`unsupported_claims` 和 `fallback_reason` 必须可断言。生产级检索排序和 GraphRAG index job 仍然必须等后续 runtime / eval 证明后才能写入 Current。

### Security / Governance 平面

企业私有知识场景的安全问题主要分四类：稳定性、安全性、隐私和商业机密。稳定性是任务不要乱跑、工具不要误调用、失败要可恢复；安全性是 prompt injection、tool abuse、越权访问、恶意文件和不可信 MCP server 不应突破边界；隐私是 PII、候选人资料、员工信息、客户数据不能被误写入不该去的上下文或输出；商业机密是合同、报价、技术方案、内部策略、源代码和密钥不能被泄露、混入公开 provider 或输出给无权用户。

目标安全链路有四道闸：输入闸门、检索闸门、工具闸门、输出闸门。输入闸门做鉴权、限流、文件校验、PII / secret / injection 检测；检索闸门做 workspace / project scope、chunk ACL、document trust label 和恶意指令净化；工具闸门做 permission decision、side-effect approval、secret broker、network / cwd / host allowlist、timeout 和 sandbox；输出闸门做 DLP scan、citation coverage、敏感字段脱敏、格式校验和 policy violation report。

安全不是单独一个 endpoint，而是横切 runtime。每次检索、每次工具调用、每次输出都要能产出 policy decision 和 audit trace。LangGraph 的 interrupt / resume 可以承载审批恢复点；平台层的 sandbox 和 credential broker 负责把“模型建议调用工具”与“代码真正执行工具”隔开。

最新报告进一步把安全基线拆成四层 sandbox。第一层是 Policy Sandbox：ToolCard 自带 risk_level、side_effect_level、approval_required、sandbox_required、network_policy、credential_policy 和 audit_required。第二层是 Workspace Sandbox：原始知识库、上传文件、临时目录、生成目录、只读源码区和可写 artifact 区必须硬隔离。第三层是 Execution Sandbox：代码执行、CLI、SSH、local MCP server 和重文档解析都必须进入受限执行边界，至少具备 timeout、resource limit、cwd scope、allowlist、secret redaction 和 audit。第四层是 Network / Credential Sandbox：默认 deny，HTTP/HTTPS 通过代理出站，allowed domains 显式列白名单，原始 secrets 不进入 prompt 和 sandbox 文件系统，而由宿主侧 credential broker 注入。提示注入不能被当作一次性修好的输入漏洞；它必须被视为系统级残余风险，通过审批、隔离、最小权限和审计来控损。

当前 PHASE09 已把这一层落成可测 contract：`zuno.platform.security.governance` 覆盖输入、检索、工具、输出四道 gate，能对 prompt injection、PII、secret、跨 workspace chunk、ACL scope、untrusted retrieved instruction、高风险工具、低 citation coverage 输出生成 policy decision 和 audit event。它证明治理字段、redaction 和 trace payload 边界成立，不表示 rootless container、Firecracker/gVisor、真实 credential broker、approval UI、network proxy 或生产级 DLP 已完成。

#### Security Trust Boundaries、Sandbox Tiers 与 Prompt Injection 残余风险

信任边界至少分四层：

- **Client Boundary**：浏览器、桌面端、用户上传文件、剪贴板内容和用户输入。它们都是输入源，但不天然可信。
- **Zuno Trust Boundary**：API、Agent Runtime、Policy Engine、Tool Gateway、Trace/Eval、本地 storage。这里执行仓库代码和安全策略。
- **Enterprise Data Boundary**：企业文档、知识库索引、图谱、候选人资料、合同、项目材料和生成产物。访问必须受 workspace / ACL 控制。
- **External Boundary**：第三方 API、MCP server、邮件服务、浏览器网页、SSH target、公开网页和模型 provider。默认 untrusted 或 provider-trusted，而不是 enterprise-trusted。

`model_intent` 与 `final_decision` 必须分离记录。模型可以表达“我想调用 send_email”，但 Policy Engine 才能决定是否允许、是否要审批、是否需要脱敏、是否进入 sandbox。Audit trace 至少记录：

```json
{
  "tool_call_id": "tool_xxx",
  "model_intent": "发送候选人评估邮件给面试官",
  "tool_id": "mail.draft_and_send",
  "proposed_args_redacted": {"to": "[redacted]", "subject": "面试评估"},
  "risk_reason": ["external_write", "pii_possible"],
  "policy_decision": "require_approval",
  "final_decision": "approved",
  "approver": "user_hr_01",
  "credential_policy": "brokered_secret",
  "sandbox_profile": "network_limited"
}
```

Prompt injection 残余风险处理原则：

- 外部文档、网页、邮件、MCP 返回内容都标记为 untrusted content。
- untrusted content 只能作为 evidence，不得覆盖 system policy。
- 检索结果进入 prompt 前要做 instruction stripping / labeling。
- 高风险工具调用时，审批界面必须展示模型意图、证据来源、敏感字段和真实参数。
- Secrets 不得进入 prompt、trace 明文、artifact、sandbox filesystem 或 parser temporary output。
- Output DLP 不能替代 retrieval ACL；输出前挡住泄露只是最后一道闸。

PHASE09 的 security tests 至少覆盖：直接 prompt injection、间接 prompt injection、跨 workspace 检索、PII 未脱敏输出、secret exfiltration、未审批邮件发送、CLI path escape、MCP untrusted server tool abuse。

### Eval / Observability 平面

评测与观测不是上线后才补的看板，而是 Zuno 能否证明自己进步的质量系统。目标 trace schema 应兼容 LangSmith 的 run / span / thread / dataset / experiment 组织方式，同时保留本地 JSONL 和 pytest / eval runner 作为 release gate。每次请求至少要关联 trace_id、session_id、workspace_id、requested_query_method、resolved_query_method、retrieval events、tool events、evidence bundle、citation coverage、latency、cost、fallback reason、approval decision 和 policy diagnostics。

指标分四层。检索层看 Recall@k、MRR、nDCG、retrieval relevance、context precision / recall、community report hit rate 和 citation coverage。回答层看 correctness、faithfulness / groundedness、answer relevance、format validity 和 hallucination risk。Agent 层看 tool selection、argument correctness、trajectory quality、fallback rate、retry rate、approval rate、task completion rate 和 P50 / P95 latency。安全层看 prompt injection block rate、redaction miss rate、sandbox violation、unauthorized retrieval block 和 output DLP violation。

当前 Zuno 有本地 eval baseline、trace/eval foundation、Contract Review eval 证据，以及 PHASE10 的 `ZunoSpan` / `LangSmithExportAdapter` / `ReleaseEvalBaseline` contract。LangSmith 驱动的持续评测平台、在线采样、持久 trace store 和完整 CI release gate 仍是 Target。实施时应先做 schema mapping 和离线 dataset，再接 online monitoring。这样未来简历或 demo 里可以写出真实数字，而不是只说“做了 RAG 评测”。

最新报告把 observability 的内部标准进一步定为 OTel-compatible span schema，LangSmith 只是第一接收端和实验台，不是唯一事实源。推荐路径是：Zuno runtime 先生成 OTel / LangSmith-compatible spans；OTel Collector 负责 redaction、routing 和 sampling；本地 JSONL / database 保留 release gate 证据；LangSmith sink 承担 trace browser、dataset、offline / online experiment；Prometheus / OpenTelemetry-native backend 承担 latency、error、cost 和 security metrics。这样既能用 LangSmith，又不会把 Zuno 的 trace 数据结构锁死在单一 vendor。

#### LangSmith / OTel Span Contract、Offline / Online Eval 与 CI Gate

Trace primary keys：

```json
{
  "trace_id": "trace_xxx",
  "session_id": "sess_xxx",
  "thread_id": "thread_xxx",
  "task_id": "task_xxx",
  "turn_id": "turn_xxx",
  "run_id": "run_xxx",
  "parent_run_id": "run_parent_xxx",
  "run_type": "llm|tool|retriever|memory|policy|artifact|chain",
  "name": "graphrag_local_search",
  "status": "ok|error|cancelled",
  "start_time": "ISO8601",
  "end_time": "ISO8601",
  "redaction_profile": "external_sink_safe"
}
```

Dataset schema：

```json
{
  "dataset_id": "ds_contract_review_v1",
  "case_id": "case_001",
  "scenario": "contract_review",
  "workspace_fixture": "ws_contract_fixture",
  "input_query": "找出合同里的付款和违约风险",
  "expected_evidence_refs": ["doc_contract#page=4", "doc_contract#page=7"],
  "expected_behavior": {
    "requires_citation": true,
    "forbidden_tools": ["mail.draft_and_send"],
    "expected_methods": ["local", "basic"]
  },
  "labels": ["rag", "citation", "security"]
}
```

Eval 三层：

- **Offline eval**：PR 或 nightly 上跑，比较 dataset、prompt、router、retriever、tool policy、memory policy 的版本。目标是 regression testing。
- **Online eval**：对 demo / production 采样，运行 reference-free evaluator 和安全 evaluator。目标是监控真实分布，不把 PII 送外部 sink。
- **CI gate**：关键指标低于阈值时阻断合入或标记 release risk。

建议阈值初稿：

| 指标 | 初始门槛 | 说明 |
| --- | --- | --- |
| `retrieval_recall_at_10` | >= 0.80 | 第一版可以低一些，但必须随 dataset 固定。 |
| `citation_coverage` | >= 0.90 | 企业知识回答必须可追溯。 |
| `faithfulness` | >= 0.85 | LLM-as-judge + evidence spot check。 |
| `tool_selection_accuracy` | >= 0.90 | Agent trajectory eval。 |
| `tool_success_rate` | >= 0.95 | 不含故意阻断的安全用例。 |
| `approval_escape_count` | == 0 | 高风险工具不能绕过审批。 |
| `cross_workspace_leak_count` | == 0 | 安全硬门槛。 |
| `secret_redaction_miss_count` | == 0 | 外部 sink 和 artifact 都要检查。 |
| `p95_latency_budget_hit` | >= 0.90 | 场景级预算，不是全局硬值。 |
| `prompt_injection_attack_pass_rate` | >= 0.95 | 模拟攻击阻断率。 |

这些阈值是 Target 初稿，不代表当前仓库已达到。PHASE10 已把 dataset case、metric threshold、metric result、release baseline 和 redacted failure examples 做成可测试 contract；完整 dataset、nightly eval、CI release gate 和在线采样平台仍是 Target。

### Platform / Storage / Worker 平面

近期平台层仍应保持模块化单体；微服务不是近期 Current，也不是默认路线。目标上，Platform 负责 model gateway、settings、database、object storage、vector store、graph store、search index、queue / worker、secrets、observability 和 provider adapter。文档解析、embedding、GraphRAG indexing、artifact rendering 和长任务可以先通过 background job / worker 抽象表达，不需要立刻引入完整分布式架构。

代码布局上，`src/backend/zuno` 顶层六层已经正确：`api / agent / memory / capability / knowledge / platform`。PHASE02 已把六层内部的 owner baseline 写入 `docs/architecture/repo-ownership-matrix.md`，并用 `tools/scripts/verify_repo_structure.py` 固定 `platform/services`、`capability/tools`、`capability/mcp/servers`、`platform/compatibility` 和 `platform/vendor` 的边界。当前事实是：`platform/services` 仍是 migration source；`knowledge/ingestion`、`platform/security`、`platform/observability` 和 `platform/vendor` 已有 README / import guard，且 `platform/security/governance.py` 与 `platform/observability/trace_eval.py` 分别提供 security 与 trace/eval contract foundation；`fastapi_jwt_auth` 仍在 compatibility vendor 兼容路径。任何移动都必须先由 import matrix、focused tests 和 verifier 证明，不为了视觉清爽直接删兼容路径。

目标代码树按最新报告收束为“业务语义拥有代码，platform 只承载跨层基础设施”：

```text
src/backend/zuno/
  api/                         # FastAPI routes, DTO, session/task/artifact contracts
  agent/                       # Single Controller Runtime, state graph, planning, streaming
  memory/                      # context_builder, raw events, summaries, structured memory
  capability/                  # ToolCard registry, selector, policy, executors, MCP adapters
  knowledge/
    ingestion/                 # parser router, Document IR, chunk/provenance, parser golden tests
    retrieval/                 # basic RAG, sparse/dense/hybrid search
    graphrag/                  # entity/relation extraction, community reports, local/global/drift
    evidence/                  # evidence bundle, citation, grounding checks
  platform/
    model_gateway/             # local/API model provider boundary
    storage/                   # SQL, object, vector, graph, search provider adapters
    jobs/                      # ingest/embedding/index/artifact background jobs
    observability/             # OTel/LangSmith-compatible trace, metrics, eval export
    security/                  # policy, DLP, approval, sandbox, credentials
    vendor/                    # vendored shims only
    compatibility/             # legacy import registry only
```

这个代码树不是 Current 承诺。它是 PHASE02 ownership baseline 之后逐步收敛的 Target。当前 Current 只包括六层顶层、ownership matrix、预留 import guard、compat/vendor guard 和 provider 分类 guard；真实 runtime 迁移仍要逐 phase 用 legacy guard tests、repo structure verifier 和 focused runtime tests 证明。

## 主链路

```text
upload / sync enterprise docs
  -> format detection
  -> Parse Gateway
  -> OCR / table / code / metadata extraction
  -> chunk + provenance + ACL
  -> BM25 / vector / graph index
  -> user query
  -> Context Builder
  -> Single Controller Agent
  -> user product mode: normal / enhanced / auto
  -> Agentic Retrieval Router
  -> resolved retrieval method(s): basic / local / global / drift
  -> evidence and citation check
  -> answer / report / artifact
  -> trace / eval / memory candidate
  -> review / promotion / durable memory
```

这条链路解释为什么 Document Ingestion 不能继续隐含在工具层里：企业知识库质量首先取决于解析、metadata、ACL、chunk 和 provenance，而不只是检索算法。

## 文档解析边界

下一阶段需要把文档解析正式成层。目标 Parser Capability Matrix 至少覆盖：

- PDF：页码、span、图片、表格和 OCR metadata。
- DOCX / PPTX / XLSX：heading、slide、sheet、table 和结构信息。
- TXT / MD / CSV / JSON / HTML：行号、标题、row id、DOM section。
- 图片 / 扫描件：OCR 文本、bbox、confidence、视觉描述。
- 代码文件：语言、路径、symbol、line range 和代码感知切块。

这些能力进入 `Document Ingestion / Parse Gateway` program，而不是在当前文档里伪装成已经完成。

## 工具层边界

工具层按能力语义治理，不按 API / SDK / CLI / MCP 拆顶层业务分类。邮件、文件、数据库、搜索、知识库、代码执行和 SSH 是 capability domain；local function、SDK、API、CLI、SSH、MCP stdio、MCP HTTP 是 execution adapter。

高副作用工具，例如 `send_email`、外部写操作、SSH、删除或覆盖类命令，目标上必须经过 approval / interrupt / audit trace。当前可以说 PHASE07 已有 approval gate 和 interrupt envelope contract，不能声称已有完整工具审批 UI、credential broker 和执行沙箱。

## 安全与评测

企业私有知识场景里，安全和评测不是附加功能，而是产品可信度的一部分。

安全目标分四道闸：

1. 输入闸门：鉴权、限流、文件校验、PII / 商业机密识别、prompt injection 检测。
2. 检索闸门：chunk 级 ACL、workspace / project scope、document trust label、检索结果净化。
3. 工具闸门：side effect 分级、permission decision、approval gate、timeout、cwd / host allowlist。
4. 输出闸门：DLP scan、citation coverage、format validation、敏感字段脱敏。

评测目标分四类：

- Retrieval eval：Recall@k、MRR、nDCG、retrieval relevance、citation coverage。
- Answer eval：correctness、faithfulness / groundedness、answer relevance、format validity。
- Agent eval：tool selection、argument correctness、trajectory quality、approval rate、fallback rate。
- Security eval：prompt injection block rate、redaction miss rate、sandbox violation、越权访问阻断率。

LangSmith-compatible Trace / Eval 是统一 trace / span / dataset / evaluator / experiment 的外部适配层；本地 pytest 和 eval runner 仍保留为 release gate。

## 实施落点

当前 active program 是 `zuno-production-architecture-and-deliverables-completion-v1`，当前阶段是 `PHASE01_production-maturity-gap-audit`。它是一次性交付型成熟化 program，目标是把 Zuno 从“第一版 runtime-first vertical slice 已完成”推进到“成熟目标架构和四大总交付物完成”。最近完成并归档的 program 是 `zuno-target-architecture-runtime-full-implementation-v1`，归档位置是 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。它承接 `zuno-master-architecture-implementation-v1` 的 contract foundation，不推翻目标架构，而是把目标架构推进到第一版真实 runtime 闭环。上一轮 foundation program 是 `zuno-master-architecture-implementation-v1`，归档位置是 `docs/history/programs/zuno-master-architecture-implementation-v1/`；它已完成 PHASE01-PHASE12，将目标架构按阶段落地，同时仍然遵守 Current / Target 边界。

本轮 runtime-first program 的核心闭环是：

```text
上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback
```

本轮的十二个 phase：

1. `PHASE01_program-reopen-and-truth-source-freeze`：已打开新 active program，冻结 runtime-first 验收口径和事实源。
2. `PHASE02_runtime-migration-map-and-repo-ownership-lock`：固定旧 runtime 与六层 target owner 的迁移图和兼容策略。
3. `PHASE03_task-session-artifact-event-runtime`：已打通 workspace / session / file / ingest / task / approval / event / artifact / feedback 后端 API 与 SSE runtime surface。
4. `PHASE04_document-ingestion-parse-runtime`：已让 `knowledge/ingestion` 从 contract owner 进入 Parse Gateway runtime owner surface。
5. `PHASE05_index-jobs-and-knowledge-space-runtime`：已将 Document IR 送入本地 BM25 / vector / graph index job runtime，并提供 manifest、失败重试、回放和 retrieval payload。
6. `PHASE06_durable-single-controller-runtime`：已让 Single Controller runtime 支持 controller-node 级 checkpoint、interrupt、resume、cancel、failure snapshot，并接入 workspace task。
7. `PHASE07_memory-db-and-context-governance`：已将 MemoryEngine 升级为 snapshot / SQLModel-backed memory runtime，并接入 GeneralAgent。
8. `PHASE08_tool-control-plane-approval-and-sandbox-runtime`：已接通本地 deterministic executor、approval API/UI bridge、credential ref broker、sandbox context、audit trace 和 workspace event stream。
9. `PHASE09_agentic-retrieval-evidence-citation-runtime`：已让 Agentic retrieval 消费新 index runtime，输出 citation-rich answer，并把 evidence / citation / unsupported claim 指标写入 task retrieval event。
10. `PHASE10_security-observability-and-online-eval`：已将 security gates、ZunoSpan、task observability snapshot、trace replay 和 release baseline 接入 workspace task runtime。
11. `PHASE11_web-desktop-surface-and-feedback-loop`：已把 Web workspace Agent 模式接入 file / ingest / task / SSE / approval / artifact / trace-eval / feedback 产品闭环；Desktop 当前复用 API / bridge，不写成生产桌面闭环。
12. `PHASE12_release-gate-full-e2e-closure`：已完成完整 vertical slice release closure、归档和验证收口。

这十二个 phase 可以按 workstream 拆分并行，但共享状态面、架构源文档、verifier、tests 和 release closure 必须由主线程统一收口。每个 runtime phase 只有在真实 API / runtime / UI 路径、focused tests、trace / eval 或 verifier 证明后才能关闭；只写 contract、schema 或 README 不能关闭 runtime phase。

新的 mature-architecture completion program 从 PHASE01 开始，不把生产级 Target 直接写成 Current。它按四大总交付物推进：工作流自洽与自我维护、文档系统清晰无冗余、文件夹和代码 ownership 清晰、架构功能完整实现；第四项展开为八类 runtime-first 交付物。

## 研究产物归档

用户提供的高质量架构 PDF 已作为 research input 归档到：

- `docs/history/research/chatgpt-research-mode-artifacts/zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.pdf`
- `docs/history/research/chatgpt-research-mode-artifacts/zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.md`
- `docs/history/research/chatgpt-research-mode-artifacts/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf`
- `docs/history/research/chatgpt-research-mode-artifacts/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.md`

这个目录使用英文名 `chatgpt-research-mode-artifacts`，专门保存 ChatGPT 研究模式产物。它不是当前架构事实源。正式架构事实源仍是本文；HTML 展示仍由本文生成。吸收研究报告时，必须重新判断哪些是 Current，哪些是 Target，哪些只能作为 Future 或 History。

同时，最新实施蓝图 PDF 也复制到 `docs/architecture/assets/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf`，作为人类阅读附件。`assets/` 中的 PDF 不是第二事实源；正式架构结论仍以本文和由本文生成的 HTML 为准。

## 当前前台文档边界

`docs/architecture/` 当前只保留少数入口：

- `README.md`
- `architecture.md`
- `production-readiness.md`
- `architecture.html`
- `assets/`
- `decisions/`

以下拆分文档已经被本文和 HTML 吸收，归档到 `docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/`：

- `current-architecture.md`
- `target-architecture.md`
- `roadmap.md`
- `product-scenario-enterprise-kb.md`
- `security-and-sandbox.md`
- `deliverables.md`

`.agent/architecture/` 当前只保留 `README.md`、`architecture.md` 和 `architecture.html`。旧 near-term / future / decisions 工作集归档到 `docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/`。

## 文档一致性规则

- 改文字架构时，先改 `docs/architecture/architecture.md`，再运行 `python tools/agent/render_architecture.py --write` 同步 `.agent/architecture/architecture.md`。
- 改图形架构时，先改 `docs/architecture/architecture.md` 中的 Mermaid 图源，再运行 `python tools/agent/render_architecture.py --write` 更新两个 `architecture.html`。
- 改生产成熟度边界时，同步 `docs/architecture/production-readiness.md`、入口摘要、verifier 和 repo tests；README、AGENTS、`.agent/programs/current.md` 和 `.agent/references/current-program.md` 不重复 phase 目录、Production Target 目录或八类交付物展开。
- 不再新增 `current-architecture.md`、`target-architecture.md`、`roadmap.md` 这类拆分入口，除非先打开新的文档重组 program。
- 高频变化的执行细节放进 `.agent/programs/`。
- Agent 操作规则放进 `.agent/references/`。
- 历史材料进入 `docs/history/`，不要留在当前前台。

验证入口：

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
```

## 架构图视图集

以下十类图服务于架构 HTML 展示页，但它们不是独立事实源。每张图都必须能回到上文的文字设计：企业私有知识场景、Single Controller Agent Runtime、Document Ingestion、Memory、Tool Control Plane、Knowledge / GraphRAG、安全治理和 LangSmith-compatible Trace / Eval。

## 一、4+1 View Model

4+1 从五个角度解释同一个系统：Logical、Development、Process、Physical 和 Scenarios。Process View 关注运行时进程、通信、并发和事件流；Agent Loop 是 Zuno 的核心内部循环，但不等同于整个 Process View。

### Logical View

该图回答：Zuno 的目标职责如何分层，以及哪些能力是顶层模块、哪些能力是横切治理。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;
  classDef guard fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;
  classDef mem fill:#f8fbff,stroke:#5b7fa3,stroke-width:1px,color:#16202a;

  USER["User<br/>Workspace"]
  API["API Session<br/>Task Event Artifact"]
  MODEL["Model Gateway<br/>and Policy"]
  CORE["Agent Core<br/>Runtime"]:::accent
  POST["PostTurn<br/>Pipeline"]:::mem
  GOV["Governance Plane<br/>security approval trace eval"]:::guard
  SPAN["ZunoSpan Contract<br/>redacted payload"]:::guard
  BASELINE["Release Baseline<br/>dataset metrics"]:::guard
  PLATFORM["Platform<br/>Infrastructure"]

  subgraph MEMSYS["Context and Memory"]
    direction TB
    PACK["Context Pack"]:::mem
    RECENT["Recent Window"]:::mem
    SUMMARY["Task Summary"]:::mem
    STRUCT["Structured Memory<br/>episodic semantic procedural"]:::mem
    RAW["Raw Event Log"]:::mem
    PACK --> RECENT
    PACK --> SUMMARY
    PACK --> STRUCT
    STRUCT --> RAW
  end

  subgraph KNOWSYS["Knowledge and Ingestion"]
    direction TB
    INGEST["Document Ingestion<br/>Document IR"]
    KNOW["Agentic GraphRAG<br/>Evidence Citation"]
    INGEST --> KNOW
  end

  subgraph ACTSYS["Action and Output"]
    direction LR
    TOOL["Tool Control Plane"]
    REG["Manifest Registry"]:::guard
    SELECT["Capability Selector"]:::guard
    EXEC["Execution Adapter"]:::guard
    NORM["Result Normalizer"]:::guard
    ART["Artifact Workspace"]
    TOOL --> REG --> SELECT --> EXEC --> NORM --> ART
  end

  USER --> API --> CORE
  MODEL --> CORE
  CORE --> PACK
  CORE --> TOOL
  CORE --> KNOW
  CORE --> POST --> RAW
  PACK --> GOV
  NORM --> GOV
  KNOW --> GOV
  GOV --> SPAN --> BASELINE --> PLATFORM
  RAW --> PLATFORM
  ART --> PLATFORM
  class USER,API,MODEL,PLATFORM node;
```

#### 分析

- 关注点：系统职责，而不是物理目录。
- Zuno 映射：默认主线仍是 Single Controller Agent；`Agent Core Runtime` 是 `Single Controller Agent` 的二级展开；Memory 展开为 Raw Event Log、Recent Window、Task Summary、Structured Long-term Memory 和 Context Pack。
- 边界：Knowledge 可以作为 capability 被调用，但在架构上单独成层，因为 GraphRAG、retrieval fusion、citation 和 evidence contract 有独立生命周期。
- 边界：Security、Trace 和 Eval 收束为 Governance Plane；PHASE10 已把 `ZunoSpan`、redacted payload 和 release baseline contract 做成 Current，外部 sink runtime 仍是 Target。

### Development View

该图回答：代码、正式文档和 Agent 工作流如何组织，并说明新增架构细化 program 放在哪里。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;
  classDef guard fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;
  classDef work fill:#f8fbff,stroke:#5b7fa3,stroke-width:1px,color:#16202a;

  R["Repository Root"]:::accent
  R --> APPS["apps"]
  R --> BACKEND["src/backend/zuno"]
  R --> DOCS["docs"]
  R --> AGENT[".agent"]
  R --> TOOLS["tools"]
  R --> TESTS["tests"]
  BACKEND --> API["api"]
  BACKEND --> AG["agent"]
  BACKEND --> MEM["memory"]
  BACKEND --> CAP["capability"]
  BACKEND --> KNO["knowledge"]
  BACKEND --> PLA["platform"]
  API --> APISTATE["session task artifact contracts"]
  AG --> RUNTIME["state graph planning streaming"]
  MEM --> MEMSYS["context builder memory stores"]
  CAP --> TOOLSYS["ToolCard policy executors MCP"]
  KNO --> KNOWSYS["ingestion retrieval GraphRAG evidence"]
  PLA --> PLATSYS["model storage jobs security observability<br/>trace_eval contract"]
  DOCS --> FORMAL["architecture.md source"]
  DOCS --> HTML["architecture.html generated"]
  DOCS --> ASSETS["architecture assets PDFs"]
  AGENT --> PROGRAM["active production completion program<br/>PHASE01 maturity gap audit"]:::guard
  AGENT --> REFS["references governance"]
  AGENT --> TPL["templates skeletons"]
  TOOLS --> RENDER["render architecture"]
  TOOLS --> VERIFY["verifiers"]
  TESTS --> REPO["repo tests"]

  subgraph WORK["Parallel Delivery Worktrees"]
    direction TB
    WA["A architecture docs v2"]:::work
    WB["B code layout rationalization"]:::work
    WC["C document ingestion"]:::work
    WD["D runtime memory tool plane"]:::work
    WE["E security sandbox"]:::work
    WF["F eval observability"]:::work
  end

  PROGRAM --> WORK
  WA --> FORMAL
  WB --> BACKEND
  WC --> KNO
  WD --> AG
  WD --> MEM
  WD --> CAP
  WE --> PLA
  WF --> PLA
  WORK --> VERIFY
  class APPS,BACKEND,DOCS,AGENT,TOOLS,TESTS,API,AG,MEM,CAP,KNO,PLA,APISTATE,RUNTIME,MEMSYS,TOOLSYS,KNOWSYS,PLATSYS,FORMAL,HTML,ASSETS,REFS,TPL,RENDER,VERIFY,REPO node;
```

#### 分析

- 关注点：开发者如何进入项目。
- Zuno 映射：`docs/architecture/architecture.md` 是 Mermaid 图源；`.agent/programs/` 是当前执行计划；`tools/agent/render_architecture.py` 生成 HTML；`docs/architecture/assets/` 保存人类阅读附件。
- 边界：高频执行细节进入 `.agent/programs/`，稳定结论进入 `docs/architecture/`；A-F 是工程交付 worktree，不是产品 runtime 多 Agent 架构。

### Process View

该图回答：一次请求如何经过 API、Context、Agent Core、工具/检索、事件流和评测追踪。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;
  classDef event fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;

  UI["Web or Desktop UI"]
  HTTP["HTTP Command Channel"]
  STREAM["SSE or WebSocket Stream"]
  SESSION["Session Manager"]
  CONTEXT["Context Builder"]
  MEMORY["Memory Read Path<br/>recent summary structured"]
  CORE["Agent Core Runtime"]:::accent
  ROUTER["Mode and Intent Router"]
  DISPATCH["Tool Retrieval Dispatch"]
  OBS["Observation Collector"]
  POST["PostTurn Pipeline"]
  WRITE["Memory Write Gate<br/>candidate review promote"]
  TRACE["ZunoSpan Builder<br/>redacted payload"]:::event
  EVAL["Release Baseline Writer"]:::event
  AUDIT["Sandbox Audit Span"]:::event
  OUT["Answer or Artifact"]

  subgraph IN["Request Stage"]
    direction TB
    UI --> HTTP --> SESSION --> CONTEXT
    MEMORY --> CONTEXT
  end

  subgraph RUN["Runtime Stage"]
    direction TB
    CORE --> ROUTER --> DISPATCH --> OBS
    OBS -. next step .-> CORE
  end

  subgraph AFTER["Commit and Delivery"]
    direction TB
    POST --> WRITE --> MEMORY
    POST --> TRACE
    TRACE --> STREAM --> UI
    EVAL --> TRACE
    AUDIT --> TRACE
    OUT --> HTTP
  end

  CONTEXT --> CORE
  OBS --> POST
  DISPATCH --> AUDIT
  CORE --> EVAL
  CORE --> OUT
  class UI,HTTP,STREAM,SESSION,CONTEXT,MEMORY,ROUTER,DISPATCH,OBS,POST,WRITE,OUT node;
```

#### 分析

- 关注点：运行时控制流、事件流和外部调用。
- Zuno 映射：Process View 覆盖 API、Agent runtime、工具调用、检索、memory read/write、trace 和 eval。
- 边界：SSE / WebSocket 是事件传输通道；trace / eval contract 才是可观测事实。

### Physical View

该图回答：Zuno 在本地优先部署中连接哪些节点，以及哪些 provider 是可替换边界。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;
  classDef guard fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;

  LOCAL["Local Machine"]:::accent
  WEB["Vue Web App"]
  DESKTOP["Electron Desktop"]
  API["FastAPI Backend"]
  WORKSPACE["Workspace Files"]
  ARTIFACT["Artifact Store"]
  SQL["SQL Database"]
  VECTOR["Vector Store"]
  GRAPH["Graph Store"]
  MODEL["Model Provider or Local Model"]
  MCP["MCP Servers"]
  LOCALTRACE["Local Release Evidence"]
  LANGSMITH["LangSmith or Trace Backend<br/>target sink"]:::guard
  LOCAL --> WEB
  LOCAL --> DESKTOP
  WEB --> API
  DESKTOP --> API
  API --> WORKSPACE
  API --> ARTIFACT
  API --> SQL
  API --> VECTOR
  API --> GRAPH
  API --> MODEL
  API --> MCP
  API --> LOCALTRACE
  API --> LANGSMITH
  class WEB,DESKTOP,API,WORKSPACE,ARTIFACT,SQL,VECTOR,GRAPH,MODEL,MCP,LOCALTRACE node;
```

#### 分析

- 关注点：部署节点和外部依赖。
- Zuno 映射：本地文件、数据库、向量/图存储、模型 provider、MCP 和 trace backend 都是可替换边界。
- 边界：近期仍是模块化单体，不是微服务拆分。

### Scenarios View

该图回答：企业知识库场景中，文档如何进入知识空间，并如何变成可引用回答或报告。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef decision fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;

  UPLOAD["1 Upload Enterprise Docs<br/>pdf docx pptx image code"]
  TYPE["2 Type Detection"]
  ROUTEPARSE["3 Parser Router"]
  NATIVE["Native Parser<br/>txt md code html"]
  DOCLING["Docling PyMuPDF<br/>pdf table layout"]
  MINERU["MinerU OCR VLM<br/>scan formula figure"]
  UNSTRUCT["Unstructured MarkItDown<br/>office long tail"]
  NORMALIZE["4 Structured Markdown JSON IR"]
  CHUNK["5 Chunk Evidence Anchor"]
  ACL["6 ACL Scope Sensitivity Tag"]
  INDEX["7 Index<br/>BM25 Vector Graph"]
  QUERY["8 User Query"]
  PRODUCT["9 Task Envelope<br/>workspace session product_mode"]
  CONTEXT["10 Context Builder<br/>query files memory"]
  MEMORY["11 Selected Memory<br/>recent summary structured"]
  AGENT["12 Controller Agent"]:::accent
  MODE{"Retrieval Policy"}:::decision
  NORMAL["basic<br/>force simple retrieval"]
  ENHANCED["graph_required<br/>retrieval required"]
  AUTO["auto<br/>agent decides retrieval"]
  NEED{"Need Retrieval"}:::decision
  ROUTER["Agentic GraphRAG Router<br/>select channel by task evidence budget"]:::accent
  BASIC["basic<br/>BM25 vector"]
  LOCAL["local<br/>entity neighborhood"]
  GLOBAL["global<br/>community prior"]
  DRIFT["drift<br/>global primer local loop"]
  FUSION["Fusion Rerank<br/>Evidence Bundle"]
  EVID["Evidence and Citation Check"]
  RETRY["Retry or Replan Path"]:::decision
  ANSWER["Answer Report Artifact"]:::accent
  TRACE["ZunoSpan Trace Eval Event"]
  BASELINE["Release Baseline Evidence"]
  MEMCAND["Memory Candidate"]
  REVIEW["Review Promote Decay"]
  MEMSTORE["Durable Memory"]
  NEXTREAD["Next Turn Read Policy"]

  UPLOAD --> TYPE --> ROUTEPARSE
  ROUTEPARSE --> NATIVE --> NORMALIZE
  ROUTEPARSE --> DOCLING --> NORMALIZE
  ROUTEPARSE --> MINERU --> NORMALIZE
  ROUTEPARSE --> UNSTRUCT --> NORMALIZE
  NORMALIZE --> CHUNK --> ACL --> INDEX
  INDEX --> QUERY --> PRODUCT --> CONTEXT --> MEMORY --> AGENT --> MODE
  MODE --> NORMAL --> BASIC
  MODE --> ENHANCED --> ROUTER
  MODE --> AUTO --> NEED
  NEED -->|No| ANSWER
  NEED -->|Yes| ROUTER
  ROUTER --> BASIC --> FUSION
  ROUTER --> LOCAL --> FUSION
  ROUTER --> GLOBAL --> FUSION
  ROUTER --> DRIFT --> FUSION
  FUSION --> EVID
  EVID -->|retry| RETRY
  RETRY --> ROUTER
  EVID -->|pass| ANSWER
  ANSWER --> TRACE --> BASELINE --> MEMCAND --> REVIEW --> MEMSTORE
  MEMSTORE --> NEXTREAD
  class UPLOAD,TYPE,ROUTEPARSE,NATIVE,DOCLING,MINERU,UNSTRUCT,NORMALIZE,CHUNK,ACL,INDEX,QUERY,PRODUCT,CONTEXT,MEMORY,NORMAL,ENHANCED,AUTO,BASIC,LOCAL,GLOBAL,DRIFT,FUSION,EVID,TRACE,BASELINE,MEMCAND,REVIEW,MEMSTORE,NEXTREAD node;
```

#### 分析

- 关注点：用企业知识库场景验证架构。
- Zuno 映射：这是 Agentic GraphRAG 产品链路。PHASE03 request envelope 用 `enterprise_kb / hr_resume / contract_review / general_agent` 表达产品场景；retrieval policy 再决定 `basic / local / global / drift` 等知识通道。
- Zuno 映射：文档解析层是企业知识库、GraphRAG、citation 和 eval 的共同前置依赖；parser router 把 native、Docling/PyMuPDF、MinerU/OCR/VLM、Unstructured/MarkItDown 收束为统一 Document IR。
- 边界：`auto` 是产品模式和路由策略，不是第五种最终检索算法；`global` 是 community-level prior，不和 chunk-level BM25 直接生硬混榜。

## 二、View & Beyond

View & Beyond 以 view 为架构文档组织单位。这里采用四个工程化视图：Logical、Component-and-Connector、Deployment 和 Quality。

### V&B Logical View

该图回答：领域子系统如何组成一个 Agent Workspace，并区分顶层能力和横切治理。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;
  classDef guard fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;

  DOMAIN["Zuno Domain"]:::accent
  DOMAIN --> RUNTIME["Agent Core Runtime"]
  DOMAIN --> MEMORY["Context Memory System"]
  DOMAIN --> CAPABILITY["Capability Tool System"]
  DOMAIN --> KNOWLEDGE["Knowledge GraphRAG System"]
  DOMAIN --> INGESTION["Document Ingestion System"]
  DOMAIN --> WORKSPACE["Workspace Artifact System"]
  RUNTIME --> PLAN["Planner ReAct Reflection Replan"]
  MEMORY --> RAW["Raw Event Log"]
  MEMORY --> WINDOW["Recent Window"]
  MEMORY --> SUMMARY["Task Summary"]
  MEMORY --> STRUCT["Structured Memory"]
  STRUCT --> TYPES["Semantic Episodic Procedural"]
  MEMORY --> PACK["Model Context Packet"]
  MEMORY --> GOV["Review Promote Decay"]
  CAPABILITY --> MANIFEST["Tool Manifest"]
  MANIFEST --> CARD["ToolCard Registry"]
  CARD --> SELECT["Capability Selector"]
  SELECT --> TOOLPOL["Tool Policy Gate"]
  TOOLPOL --> EXEC["Execution Adapter"]
  EXEC --> NORMAL["Result Normalizer"]
  NORMAL --> TOOLTRACE["Tool Trace"]
  KNOWLEDGE --> RET["Retrieval Fusion Evidence"]
  INGESTION --> DOC["Parser Registry Chunk ACL"]
  WORKSPACE --> ART["File Artifact Download"]
  POLICY["Policy Security Trace Eval"]:::guard
  PLAN --> POLICY
  TOOLTRACE --> POLICY
  RET --> POLICY
  DOC --> POLICY
  ART --> POLICY
  GOV --> POLICY
  SPAN["ZunoSpan Release Baseline"]:::guard
  POLICY --> SPAN
  class RUNTIME,MEMORY,CAPABILITY,KNOWLEDGE,INGESTION,WORKSPACE,PLAN,RAW,WINDOW,SUMMARY,STRUCT,TYPES,PACK,GOV,MANIFEST,CARD,SELECT,TOOLPOL,EXEC,NORMAL,TOOLTRACE,RET,DOC,ART node;
```

#### 分析

- 关注点：领域对象和职责。
- Zuno 映射：Runtime、Memory、Tool、Knowledge、Ingestion、Workspace 和 Policy 是目标领域子系统；Memory 是 write-manage-read 子系统，Tool 是 manifest-driven control plane，不是临时函数列表。
- 边界：GraphRAG 补充 BM25 和向量检索，不替代它们；文档解析是 Knowledge 的上游，不等同于 Memory。

### Component-and-Connector View

该图回答：运行时组件如何连接、由谁调度、在哪些节点做权限和证据检查。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;
  classDef warn fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;

  API["API Controller"]
  SESSION["Session Workspace"]
  CONTEXT["Context Builder"]
  MEMREAD["Memory Read Policy<br/>scope budget scoring"]
  MEMSTORE["Memory Stores<br/>SQL Redis Vector Graph"]
  MEMWRITE["Memory Write Path<br/>raw summary candidate"]
  MEMREVIEW["Memory Review Gate<br/>dedupe conflict retention"]:::warn
  AGENT["Controller Agent"]:::accent
  PLANNER["Planner"]
  REACT["ReAct Executor"]
  TOOLSEL["Capability Selector"]
  TOOLREG["Tool Manifest Registry"]
  TOOLPOL["Tool Policy Approval"]:::warn
  EXECAD["Executor Adapter<br/>SDK API CLI SSH MCP"]
  SANDBOX["Sandbox Budget Timeout"]:::warn
  NORMAL["Result Normalizer"]
  RETROUTER["Retrieval Router"]
  INGEST["Parse Gateway"]
  POLICY["Policy Guard"]:::warn
  OBS["Observation Collector"]
  EVID["Evidence Checker"]:::warn
  CIT["Citation Builder"]
  TRACE["ZunoSpan Builder"]
  BASELINE["Release Baseline Contract"]

  subgraph ENTRY["Entry and Context"]
    direction TB
    API --> SESSION --> CONTEXT
    MEMSTORE --> MEMREAD --> CONTEXT
  end

  subgraph RUNTIME["Agent Runtime"]
    direction TB
    AGENT --> PLANNER --> REACT
    OBS -. next step .-> AGENT
  end

  subgraph CAP["Capability and Evidence"]
    direction TB
    REACT --> TOOLSEL --> TOOLREG --> TOOLPOL --> EXECAD --> SANDBOX --> NORMAL --> POLICY
    REACT --> RETROUTER --> POLICY
    INGEST --> RETROUTER
    POLICY --> OBS --> EVID --> CIT
  end

  subgraph MEMORYC["Memory Commit"]
    direction TB
    OBS --> MEMWRITE --> MEMREVIEW --> MEMSTORE
  end

  CONTEXT --> AGENT
  CIT --> TRACE
  MEMREVIEW --> TRACE
  SANDBOX --> TRACE
  AGENT --> TRACE
  TRACE --> BASELINE
  class API,SESSION,CONTEXT,MEMREAD,MEMSTORE,MEMWRITE,PLANNER,REACT,TOOLSEL,TOOLREG,EXECAD,NORMAL,RETROUTER,INGEST,OBS,CIT,TRACE,BASELINE node;
```

#### 分析

- 关注点：组件和连接器。
- Zuno 映射：控制由 Agent 集中；能力通过 Tool Manifest Registry、Capability Selector、Tool Policy Approval、Executor Adapter、Sandbox、Result Normalizer 和 Retrieval Router 进入结果；Memory 通过 read policy 进入 Context Pack，通过 post-turn write path 进入 durable memory。
- 边界：Planner 是 Agent Core Runtime 的内部控制点，不是一个独立顶层业务层。

### V&B Deployment View

该图回答：工程部署时哪些资源应保持可替换，以及工具执行方式如何作为 adapter 进入系统。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;
  classDef guard fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;

  APP["Zuno App"]:::accent
  STORE["Local Object Storage"]
  SQL["SQL Database"]
  VDB["Vector Store"]
  GDB["Graph Store"]
  SEARCH["Sparse Search Index"]
  JOBS["Background Jobs<br/>ingest embed graph artifact"]
  MODEL["Model Gateway"]
  MCP["MCP Provider"]
  SDK["SDK Adapter"]
  APIAD["API Adapter"]
  CLI["CLI Adapter"]
  SSH["SSH Adapter"]:::guard
  SANDBOX["Execution Sandbox"]:::guard
  NET["Network Proxy"]:::guard
  CREDS["Credential Broker"]:::guard
  OTEL["OTel Contract<br/>redaction routing"]
  TRACE["Local Trace Eval Backend"]
  BASELINE["Release Baseline Evidence"]
  LS["LangSmith Sink<br/>target adapter"]
  APP --> STORE
  APP --> SQL
  APP --> VDB
  APP --> GDB
  APP --> SEARCH
  APP --> JOBS
  APP --> MODEL
  APP --> MCP
  APP --> SDK
  APP --> APIAD
  APP --> SANDBOX
  SANDBOX --> CLI
  SANDBOX --> SSH
  SANDBOX --> NET
  SANDBOX --> CREDS
  APP --> OTEL --> TRACE --> BASELINE
  OTEL --> LS
  class STORE,SQL,VDB,GDB,SEARCH,JOBS,MODEL,MCP,SDK,APIAD,CLI,TRACE,BASELINE,LS node;
```

#### 分析

- 关注点：软件元素到运行环境的映射。
- Zuno 映射：Provider 是边界，核心 runtime 不绑定单一 vendor；OTel 是内部 trace 标准，LangSmith 是第一 sink。
- 边界：SDK、API、CLI、SSH、MCP 是 execution adapter 或 provider metadata，不是 Capability 的业务顶层分类；CLI、SSH、local MCP 和重文档解析必须经过 sandbox / network / credential 边界。

### Quality View

该图回答：质量属性、安全、稳定性、观测和自动化评测如何作为治理闭环落地。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart TB
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;
  classDef warn fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;

  Q["Quality Governance"]:::accent
  INPUT["Input Guard Format PII Injection"]
  ACL["Retrieval ACL Chunk Scope"]
  TOOL["Tool Approval Side Effect Budget"]
  OUTPUT["Output DLP Citation Format"]
  WSBOX["Workspace Sandbox"]
  EXEBOX["Execution Sandbox"]
  NETBOX["Network Credential Sandbox"]
  REL["Reliability Timeout Retry Fallback"]
  OBS["ZunoSpan Schema"]
  COLLECT["Redacted Export Routing"]
  LANG["LangSmith Experiments"]
  EVAL["Release Baseline Contract"]
  RAGMET["Retrieval Metrics<br/>recall mrr ndcg"]
  ANSMET["Answer Metrics<br/>faithfulness citation"]
  AGMET["Agent Metrics<br/>tool trajectory"]
  SECMET["Security Metrics<br/>block redaction sandbox"]
  COST["Cost Latency Budget"]
  GATE["Release Governance Gate"]:::warn
  Q --> INPUT
  Q --> ACL
  Q --> TOOL
  Q --> OUTPUT
  Q --> WSBOX
  Q --> EXEBOX
  Q --> NETBOX
  Q --> REL
  Q --> OBS
  Q --> EVAL
  Q --> COST
  INPUT --> GATE
  ACL --> GATE
  TOOL --> GATE
  OUTPUT --> GATE
  WSBOX --> GATE
  EXEBOX --> GATE
  NETBOX --> GATE
  REL --> GATE
  OBS --> COLLECT --> LANG
  COLLECT --> GATE
  LANG --> EVAL
  EVAL --> GATE
  EVAL --> RAGMET --> GATE
  EVAL --> ANSMET --> GATE
  EVAL --> AGMET --> GATE
  EVAL --> SECMET --> GATE
  COST --> GATE
  class INPUT,ACL,TOOL,OUTPUT,WSBOX,EXEBOX,NETBOX,REL,OBS,COLLECT,LANG,EVAL,RAGMET,ANSMET,AGMET,SECMET,COST node;
```

#### 分析

- 关注点：性能、可靠性、安全、可观测性、可修改性和评测。
- Zuno 映射：Trace、Eval、Evidence、permission、budget、DLP、sandbox、OTel span schema、LangSmith experiment 和 verifier 共同约束质量。
- 边界：输出检查不能替代检索前 ACL 和工具前审批；安全必须贯穿输入、检索、工具和输出；LangSmith 是 sink 和实验台，不是唯一 trace 事实源。

## 三、Agent Loop 专题图

Agent Loop 是 Zuno 的核心运行范式。它属于 Process View 的内部细化，但不代表整个 Process View。

### Agent Loop View

该图回答：主控 Agent 如何在一个可观测的 runtime harness 中计划、执行、观察、反思、重规划并提交 trace / memory / eval。

#### 图

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f7f8fb", "lineColor": "#52616f"}}}%%
flowchart LR
  classDef node fill:#ffffff,stroke:#b8c2cc,stroke-width:1px,color:#16202a;
  classDef decision fill:#fff8e8,stroke:#c59b43,stroke-width:1px,color:#16202a;
  classDef accent fill:#eef6f3,stroke:#7aa59a,stroke-width:1px,color:#16202a;

  GOAL["Goal"]
  PREP["prepare_context"]
  READMEM["memory read<br/>recent task structured"]
  ROUTE["intent and mode router"]
  PLAN["plan"]
  STEP["ReAct step"]
  CALL["tool or retrieval dispatch"]
  OBS["observation"]
  RAW["raw event append"]
  WORK["working memory"]
  REFLECT{"reflection gate"}:::decision
  REPLAN["replan"]
  FINAL["final answer"]:::accent
  COMMIT["post_turn_commit<br/>trace memory eval"]
  AUDIT["security audit span"]
  SUMMARY["task summary update"]
  CAND["structured memory candidate"]
  REVIEW["review promote decay"]:::decision
  LONG["semantic episodic procedural memory"]

  subgraph PREPARE["Prepare"]
    direction TB
    GOAL --> PREP --> READMEM --> ROUTE --> PLAN
  end

  subgraph EXECUTE["Execute"]
    direction TB
    STEP --> CALL --> OBS --> RAW --> WORK --> REFLECT
  end

  subgraph POSTTURN["Post Turn"]
    direction TB
    FINAL --> COMMIT
    COMMIT --> AUDIT
    COMMIT --> SUMMARY
    COMMIT --> CAND --> REVIEW --> LONG
  end

  PLAN --> STEP
  REFLECT -->|continue| STEP
  REFLECT -->|replan| REPLAN --> PLAN
  REFLECT -->|finish| FINAL
  SUMMARY -. next turn .-> READMEM
  LONG -. next turn .-> READMEM
  class GOAL,PREP,READMEM,ROUTE,PLAN,STEP,CALL,OBS,RAW,WORK,REPLAN,COMMIT,AUDIT,SUMMARY,CAND,LONG node;
```

#### 分析

- 关注点：Agent 内部决策循环。
- Zuno 映射：Planning 是 Agent Core Runtime 的控制能力；runtime harness 负责状态、checkpoint、streaming、interrupt、trace、memory read/write 和失败处理。
- 边界：LangGraph 是目标实现候选，用于 state graph、checkpoint、durable execution、human-in-the-loop、streaming 和 resume；它不是“规划模块本身”。
- 边界：Reflection 是门控动作，不是每一步强制执行；ToT / LATS 只作为 Future 或离线困难模式，不进入近期默认路径。

## 边界

> [!warning] Current / Target 边界
> 本文是 Target 架构说明，不声称所有能力已经完成。Current 只写入有代码、测试、trace、eval 或可复现结果证明的事实。

- 产品模式：normal、enhanced、auto，由用户或上层产品策略选择。
- 内部 query method：basic、local、global、drift，由 Agentic Retrieval Router 在 enhanced / auto 模式下解析，不直接作为普通用户主入口。
- Normal 强制 basic；enhanced 一定检索并由 Agent 选通道；auto 先判断是否需要检索，再由 Agent 选通道。
- Global 不和 BM25 chunk ranking 生硬混榜；它更适合作为 community-level prior，再由 local/basic 回补 supporting evidence。
- 生产级 parser platform、外部 index platform、生产级 LangSmith trace / eval、在线采样、持久 trace store、企业知识库完整 UI 闭环、真实 rootless / gVisor / Firecracker sandbox、外部 vault / OAuth credential broker 和生产级 DLP 是本轮目标架构细化和后续执行计划，不是成熟 Current。
- PHASE05 当前已证明 Document IR 可进入本地 BM25 / vector / graph index job runtime，并产生 manifest、retry/replay 和 retrieval payload；这不是生产级 Elasticsearch / Milvus / Neo4j，也不是完整 GraphRAG extraction / community report runtime。
- PHASE08 当前已证明本地 deterministic Tool Control Plane runtime：只读工具自动执行、高副作用工具 approval wait / approve 后执行、credential reference broker、sandbox context、sandbox audit、workspace task event stream 和最小前端审批卡；生产级隔离沙箱、网络代理、外部 vault / OAuth broker、持久 approval DB 和完整 MCP runtime governance 仍是 Target。
- 当前已有 Agentic Retrieval Router、query method / citation / evidence trace contract、GraphRAG index pipeline contract 和 global community-only prior 边界；完整 LLM extraction、RRF/rerank 治理和外部 index platform 仍是 Target，并由当前 PHASE09 推进。
- 当前已有 RuntimeTurnLedger、当前轮 trace reset、GeneralAgent 最小 evidence chain、post-turn evidence payload、六层目标入口 import guard 和 eval diagnostics；完整产品级 runtime upgrade 仍是 Target。
- PHASE06 当前已证明 controller-node 级 durable runtime surface：checkpoint、approval interrupt、resume、cancel、recoverable / non-recoverable failure、runtime snapshot 和 workspace task 接入；生产 LangGraph checkpointer、进程重启恢复、exactly-once tool execution 和主循环深度切换仍是 Target。
- PHASE07 当前已证明 snapshot / SQLModel-backed memory runtime：跨 task raw event、task summary、approved durable memory、review decision、governance ledger、promotion、decay、consolidation、sensitive exclusion、Context Pack reasons 和 GeneralAgent memory 接入；生产级 semantic/vector Memory DB、后台 memory job、深度隐私治理和 memory eval baseline 仍是 Target。
- 当前已有 security governance contract：input/retrieval/tool/output gate、ToolSecurityProfile、SandboxAuditEvent、redaction 和 policy decision trace；PHASE08 已把 tool approval / sandbox audit 接入本地 tool runtime；真实 rootless/gVisor/Firecracker sandbox、外部 vault / OAuth broker、网络代理和生产级 DLP 仍是 Target。
- PHASE10 当前已证明 trace/eval contract：ZunoSpan schema、redacted LangSmith export payload、EvalDatasetCase、MetricThreshold、ReleaseEvalBaseline 和 SandboxAuditEvent 到 sandbox span 的桥接；外部 sink runtime、online eval 和完整 CI gate 仍是 Target。
- Domain Pack 只允许作为历史或兼容语境出现，不进入 Current 或 Target 主线图。
