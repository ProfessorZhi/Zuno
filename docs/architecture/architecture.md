# Zuno 总体 Target 架构

updated: 2026-08-14
status: normative-target
architecture_state: ACCEPTED_TARGET
overall_architecture_state: REFINED_BASELINE_READY_FOR_FREEZE_REVIEW
target_product_thesis_state: TARGET_HYPOTHESIS_PENDING_RED_TEAM
module_candidate_count: 10
final_module_count: NOT_FROZEN
module_decomposition_gate: NOT_OPEN
observability_architecture: OTEL_COMPATIBLE
langsmith_role: PREFERRED_AGENT_TRACE_AND_EVAL_PROVIDER
competitor_baseline_as_of: 2026-08
canonical_question: Zuno 为什么存在，Target Product、Domain、Capability、Runtime、Service、Data、Security 和 Eval 如何形成可反转的闭环？
owner: Cross-cutting Architecture Owner
acceptance_scope: Target Architecture baseline；实现、测量和外部资格尚未完成
readability_state: READABILITY_BASELINE_REFOUNDED
readability_gate: REQUIRED_BEFORE_NEXT_RED_BLUE_PROTOCOL
document_role: cross-cutting integration source
canonical_taxonomy: docs/architecture/ 仅保存总体架构四文件；项目背景与开发事实由 docs/project/ 负责
current_state_source: docs/project/ 和 docs/evidence/
review_history_source: docs/history/red-blue/
decision_sources: docs/decisions/0003-wave1-cross-module-contract-freeze.md、0005-official-langgraph-postgres-checkpointer.md、0006-evidence-driven-agentic-graphrag.md、0007-reuse-first-provider-boundary.md、0008-legal-domain-kernel-and-host-boundary.md、0009-python-only-backend.md、0012-evidence-gated-physical-service-split.md

> 本文先说明问题和产品动机，再说明 Target 责任边界，最后给出 Contract。项目上下文和开发事实由 `docs/project/` 负责；当前代码与运行证据由 `docs/evidence/` 负责；Red / Blue History 只解释架构演进理由。本正文不创建第二套事实状态机，也不把 Target 写成 Current。

## Part A — Architecture Narrative

### 阅读地图

第一次阅读只需回答四个问题：产品为什么存在？哪些内容只是 Target/Hypothesis？Domain State
与 Runtime、Memory、Knowledge、Tool Effect 如何分开？复杂度在什么证据不足时应被删除？这些
问题都在 Part A 用普通工程语言回答；Part B 只在需要实现或验证时展开 Contract、Version、
Retry、Recovery、Security 和 Eval。理解顺序由架构问题决定，而不是由旧模块编号、服务清单
或内部术语决定。

### 1. 为什么做这个系统

普通 Agent Host 可以很好地完成对话、模型接入、一般 Knowledge、Tool / MCP 和 Workflow 编排。对于简单问题，`Question → Top-K Chunks → LLM → Answer` 可能已经足够。

高风险法律任务的难点不只是“找到一段相关文字”。用户还需要知道：结论依赖了哪些材料，材料处于哪一版，证据是否足够，多个陈述是否冲突，法律依据是否适用，谁确认了结果，以及新证据到来后旧结论是否仍然有效。如果这些内容全部被压缩进聊天上下文、Memory 或 Runtime Checkpoint，系统就很难解释、复核和持续更新一个法律工作结果。

因此，Zuno 的 `TARGET PRODUCT THESIS` 不是“比 WorkBuddy / Dify 功能更多”，也不是未经测量的质量或安全宣传，而是一个可证伪的问题：

> 在高风险法律任务中，Legal Domain State、Evidence Dependency、Versioned Finding、Citation、Human Decision、Staleness、Controlled Side Effect 和 Legal Evaluation，是否会比通用 Host 单独编排产生可测量的质量、效率或可验证性收益？

当前状态是 `TARGET_HYPOTHESIS_PENDING_RED_TEAM`，不是 `PROVEN_DIFFERENTIATION`、`PRODUCTION_READY` 或 `MEASURED_ADVANTAGE`。如果 A/B/C Benchmark、Generic Host Integration Spike、真实专家验证和领域 Eval 不能证明收益，对应自研复杂度就不应保留。

### 1.1 Target User Pain Model

Zuno Target 假设要解决的不是抽象的“企业需要 AI”，而是专业人员在高风险法律任务中反复遇到的具体问题：

1. 案件和司法材料数量大，阅读、定位和核对成本高；
2. 关键事实散落在多份材料中，普通摘要可能遗漏跨文档关系；
3. 不同当事人的陈述可能表达同一事件，但内容存在冲突，需要事件对齐而不是普通相似度；
4. 法律检索不仅要判断文本是否相关，还要判断 jurisdiction、version、authority 和 applicability；
5. LLM / RAG 仍可能产生错误引用、错误适用和推理错误，专业人员必须能够检查依据；
6. 单项论文算法进入法院业务系统时，还要解决输入输出 Contract、版本、权限、Fallback、Eval 和运行治理；
7. 法院已有信息系统，甲方通常更需要可嵌入的领域能力，而不是为了一个 AI 功能推倒重建现有平台。

这些是 `TARGET_ONLY` 的领域问题模型，受到 [`docs/project/project-background.md`](../project/project-background.md) 中公开研究上下文的启发，不是历史客户原始需求或 Zuno 已测量的用户痛点。

### 2. 历史事实、当前仓库和 Target 不是一条时间线

历史项目来自智慧司法研发背景，曾有内部 Demo、客户侧 Demo、法院侧测试和 Pilot Validation，但尚未正式生产；客户明确反馈过回答质量需要提高。今天仍用于理解项目边界的背景见 [`../project/project-background.md`](../project/project-background.md)，开发过程见 [`../project/development-process.md`](../project/development-process.md)，架构审查过程见 [`../history/red-blue/`](../history/red-blue/README.md)。

当前 main 能证明 Python / FastAPI、PostgreSQL Migration、Compose、Agent / Knowledge / Memory / Tool 等代码或配置表面，但不能证明这些组件曾在历史客户环境同时运行，也不能证明用户本人负责全部能力，详见 [`../evidence/README.md`](../evidence/README.md)。

本文以下关于 Domain State、Evidence Dependency、Knowledge Readiness、Result Eligibility、Continuous Authorization、Capability Governance 和物理服务拆分的完整机制，都是 Target 或待测假设，不是历史实现回溯。但这不表示“法律智能平台 + 多专业 Agent + 科研成果产品化”是后来重新发明的故事；该原始产品意图属于 `docs/project/` 的项目事实。当前架构文档是在这一产品方向之上形成的 Target formalization，不证明历史版本已经实现全部机制。

### 3. 一个 Target 场景

这是一个用于架构推理和 Benchmark 的 Target Scenario，不是历史确认的法院 SOP：

```text
User / Generic Host submits task
  → establish Task / Document Scope
  → bind Document Versions
  → Knowledge Readiness Gate
  → authorize protected access
  → Task Analysis
  → deterministic simple Plan or dynamic bounded Plan
  → Evidence Retrieval
  → optional Legal Capability / Memory / Tool
  → Proposal
  → Evaluation / Reflection when required
  → Synthesis
  → Result Eligibility / Domain Admission
  → Human Review when required
  → Canonical Domain Commit
  → Response / WorkProduct
  → later Evidence may invalidate dependencies
```

这条流程把“任务范围”“材料是否可用”“找到材料”“理解法律结构”“结果能否正式提交”分开。上传文档只建立输入，不自动建立可供 Formal Run 使用的完整 Knowledge View。Knowledge 负责材料与证据候选；Legal Intelligence、Memory 和 Tool 只能提供受约束的 Proposal、Context、Observation 或 Effect Receipt；Domain Admission 决定什么可以成为正式业务状态；Runtime 负责执行控制而不是拥有法律事实。`Result Is Eligible for Formal Business Use` 是独立于 `Execution Can Continue` 的资格判断。

#### Target Scenario：案件争议焦点辅助分析

`TARGET SCENARIO`、`INSPIRED BY PUBLIC RESEARCH`、`NOT HISTORICAL SOP`：

```text
Plaintiff / Defendant materials
  → Document Version + Knowledge Readiness
  → Event Extraction Capability
  → Event Alignment Capability
  → Conflict Detection Capability
  → Dispute Candidate
  → Applicable Law / Similar Case Retrieval
  → Evidence Sufficiency / Applicability Check
  → Finding Proposal
  → Human Review
  → Versioned WorkProduct
```

如果新材料改变了依赖关系，系统应将受影响 Finding 标记为 `stale` 或 `review_required`，再启动有边界的重新评估，而不是继续把旧聊天答案当作最新结论。这个场景用于设计和 Benchmark，不能证明历史 Zuno 曾按此流程运行。

`Document Uploaded != Knowledge Ready`。Formal Run 必须知道声明覆盖的材料 Scope、绑定的 Document Version，以及当前 Knowledge View 是否足够覆盖该 Scope。必要材料未 Ready 时，默认等待或拒绝 Formal Run；若产品允许 Partial Run，必须显式缩小 Scope，Partial Knowledge View 不得静默获得 Full Scope Formal Result 的资格。

### 3.1 三条代表性 End-to-End Flow

总体架构不能只描述一条“万能 Agent 链”。简单问题应保持简单，复杂法律分析才启用动态规划，外部副作用必须经过独立的准备、授权、审批和对账边界。

#### FLOW A — Simple Grounded QA

```text
Question
  → Task / Scope
  → Current Authorization
  → Knowledge Readiness
  → Hybrid / ordinary Retrieval
  → EvidenceCandidate / CitationLineage
  → grounded Answer Proposal
  → Deterministic Final Gate
  → Response
```

Simple QA 默认不强行启用 Dynamic Planning、GraphRAG、Multi-Agent、Reflection 或 Long-term Memory。若简单问题也必须经过完整复杂 Runtime，说明系统没有控制复杂度。

#### FLOW B — Complex Legal Analysis

```text
Matter / Task
  → bind Declared Document Scope
  → bind Document Version Set
  → Knowledge Readiness
  → Continuous Authorization
  → Task Analysis
  → Dynamic DAG Plan
  → Retrieval / Evidence Alignment
  → optional Specialist Agent
  → Legal Capability
  → Conflict / Dispute Proposal
  → Applicable Law / Similar Case
  → Step / Join Evaluation
  → Final Synthesis
  → Result Eligibility
  → Human Review when required
  → Domain Admission
  → Versioned WorkProduct
```

新 Evidence 到来时，通过依赖关系定位受影响对象，标记 `stale` / `review_required`，再执行有边界的 targeted reevaluation；旧结果保留用于解释，但不能继续静默充当最新结果。

#### FLOW C — Controlled External Effect

```text
Task
  → Plan
  → Tool Proposal
  → PreparedAction
  → current Authorization
  → Approval when required
  → Execute
  → Observation / EffectReceipt
  → Reconcile if outcome is unknown
  → Continue / Stop / Human Review
  → Final Gate
  → Domain / WorkProduct result
```

Tool 成功与否不能只由模型输出或 HTTP Timeout 判断；未知外部结果必须先 Reconcile，不能盲目重试。

### 4. 五层责任视图，不是五个最终模块（并列出 10-MODULE LOGICAL CANDIDATE）

五层 Architecture Responsibility Layers 仍然是帮助读者理解跨层关系的视角，不是最终模块、服务或团队数量：

1. **Legal Work Surface**：案件分析、合同审查、法律研究、Finding、报告和 Human Review；
2. **Legal Domain & Intelligence**：Evidence、Fact / Event、Conflict、Dispute、Legal Issue、Fact–Article、Finding、Version 和 Staleness；
3. **Agentic Knowledge & Context**：Document Ingestion、Hybrid Retrieval、条件 Graph、Citation、Memory 和 Context Assembly；
4. **Agent Runtime & Execution**：Single Controller、Plan DAG、Step、ReAct、Reflection、Replan、受控 Worker、Model、Skill 和 Tool；
5. **Trust & Platform Engineering**：Permission、Approval、Sandbox、Audit、Observability、Eval 和 Infrastructure。

逻辑能力（`Logical Capability Architecture`）、候选模块、物理服务与部署（`Physical Service / Deployment Architecture`）、Worker、Process、Container、Database 和 Team 不做一一映射。旧的 `11 Logical Modules + 1 Architecture` 现在只作为 `History` 记录和映射来源；当前建立的是 `NEW_10_MODULE_SET: CANDIDATE_ONLY`，不是最终冻结的模块集合；`FINAL_MODULE_COUNT: NOT_DECIDED`，即 `FINAL_MODULE_COUNT: NOT_FROZEN`。下一步仍需 Overall Architecture Freeze Red / Blue 攻击候选边界后，才能打开 `MODULE_DECOMPOSITION_GATE`。

#### 10 个逻辑模块候选

| 编号 | Candidate | 主要责任 | 明确不负责 |
|---|---|---|---|
| 01 | Product Surface & Agent Portfolio | UI / API / Workbench、Workspace、Matter / Task 入口、Agent Catalog / Definition / Version / Invocation、Review / WorkProduct Surface、Generic Host / Court Integration | Plan 执行、Retrieval、Domain Admission、Tool Effect、LLM Provider 细节 |
| 02 | Legal Domain & Work Product | Matter、业务 Document / Evidence 引用、Fact、Event、Conflict、Dispute、LegalIssue、Finding、HumanDecision、WorkProduct、Domain Admission、Version / Staleness / Supersede | LLM 直接提交 Canonical Fact、Runtime Checkpoint、Knowledge Projection、Tool Effect |
| 03 | Knowledge & Evidence | Ingestion、Parse / Normalize、Chunk、Index、BM25 / Vector / Hybrid、Rerank、条件 Graph、Knowledge View / Generation / Readiness、EvidenceCandidate、CitationLineage | 业务 Document 身份与正式版本、法律适用最终判断、Canonical Domain State |
| 04 | Agent Runtime & Multi-Agent Orchestration | Single Controller、Plan DAG、ReAct、Reflection、Replan、Parallel Step、受控 Specialist Agent、Join、Budget、RunOutcome、Checkpoint 协作 | Canonical Legal Fact、权限批准、未经 Gate 的 Effect、长期 Memory 提交 |
| 05 | Capability / Skill & Tool Runtime | 统一管理 Capability / Skill Provider 与 Tool / External Action 的 Contract、Resolution、Evaluation、PreparedAction、Approval 协作、EffectReceipt、Reconciliation | Capability Proposal 直接成为 Domain Fact；Tool 直接绕过 Security / Approval |
| 06 | Model Gateway | 多模型 Provider、Role、Routing、Budget / Quota、Token / Cost、Timeout、Fallback、Structured Output、Egress Policy、Usage Receipt | 业务状态、权限决定、PlanVersion 激活、未经审批的副作用 |
| 07 | Memory & Context | Context Assembly、短期 / 长期 Memory、Summary、Preference、Experience、Reflexion Candidate、Retention / Expiry / Deletion、Provider Integration | Domain Fact、Knowledge View、Runtime Checkpoint |
| 08 | Security & Governance | Identity、Tenant、Principal、Grant、Policy、Authorization、Approval、Secret、Classification、Model Egress、Tool Permission、Audit Requirement | 业务结果、模型推理、Runtime Plan、Provider 自行扩大权限 |
| 09 | Observability & Evaluation | OTel-compatible Trace / Metrics / Logs Contract、Decision Trace、Redaction、Trace Export、Dataset / Experiment / Eval、Release Gate | 业务状态 Owner、单一 SaaS Provider、把存在 Adapter 写成完整链路 Current |
| 10 | Infrastructure & Persistence | PostgreSQL、Runtime Checkpointer、Object / Vector / Graph Store、Queue、Worker、Deployment、Backup / DR、连接与资源原语 | 逻辑模块边界、Canonical 业务判断、自动把模块变成 Network Service |

候选模块只表达责任域，不能直接生成 `docs/modules/*.md`，也不能解释为 10 个 Microservice。`OLD_11_FUNCTIONAL_COVERAGE: PRESERVED`：原有 11 个功能域全部保留，只重新组织边界。

#### 旧 11 功能到新候选的映射

| 旧功能 | 新候选 |
|---|---|
| Old 01 Product Surface | New 01 Product Surface & Agent Portfolio |
| Old 02 Input / Document Ingestion + Old 03 Knowledge / Agentic GraphRAG | New 03 Knowledge & Evidence |
| Old 04 Model Gateway | New 06 Model Gateway |
| Old 05 Memory & Context | New 07 Memory & Context |
| Old 06 Agent Core / Planning & Control | New 04 Agent Runtime & Multi-Agent Orchestration |
| Old 07 Capability / Skill + Old 08 Tool Runtime | New 05 Capability / Skill & Tool Runtime；模块合并，语义仍分离 |
| Old 09 Security | New 08 Security & Governance |
| Old 10 Observability & Eval | New 09 Observability & Evaluation |
| Old 11 Infrastructure | New 10 Infrastructure & Persistence |
| 新增一等业务责任 | New 02 Legal Domain & Work Product |

Ingestion 与 Knowledge 合并，是因为两者共同负责形成可供 Formal Run 信任的 Knowledge View；Capability 与 Tool 暂时合并，是为了避免过早拆成两个模块，但 Capability Evaluation 与 External Effect / Receipt / Reconciliation 仍是两套严格不同的语义。若后续证明两者拥有不同 Owner、状态机、持久化、安全、恢复或部署边界，再拆回两个模块。

### 5. Legal Domain、Knowledge、Intelligence 和 Memory 的边界

这四个概念解决不同问题：

- **Knowledge** 回答“材料在哪里、哪段原文支持什么”，产生 Source、Chunk、EvidenceCandidate、CitationLineage 和 RetrievalReceipt；
- **Legal Intelligence** 回答“材料表达了什么法律结构”，产生 Event、Alignment、Conflict、Fact–Article 或 Finding Proposal；
- **Domain State** 回答“业务世界目前承认什么是真的”，由 Domain Owner 根据版本、来源、权限、依赖和 Review 提交正式状态；
- **Memory** 回答“哪些上下文或经验可以被策略性复用”，可以压缩、过期、删除和按范围召回，但不是 Canonical Legal Fact。

例如，Knowledge 可以找到原告和被告的两份陈述；Legal Intelligence 可以判断它们描述同一事件且存在冲突；Domain Owner 才决定该冲突候选是否进入正式案件状态。Memory 可以帮助下一次任务复用工作上下文，但不能代替 FactVersion 或 FindingVersion。

Knowledge & Evidence 的候选生命周期是：

```text
Document Version Reference
  → Parse / Normalize
  → Chunk
  → Embedding / Index
  → optional Graph Projection
  → Knowledge View / Generation
  → Readiness
  → Retrieval / Rerank
  → EvidenceCandidate
  → CitationLineage / RetrievalReceipt
```

Document 作为业务材料的身份、适用范围和正式版本由 Domain / Document Owner 管理；Parse、Chunk、Embedding、Index、Projection 和 Retrieval View 属于 Knowledge。`Knowledge Projection != Domain Truth`。

### 6. Multi-Agent Boundary

Zuno 可以拥有多个专业 Agent，但“产品有多个 Agent”不等于“每个任务都启动多个自治 Agent”。一次 `AgentRun` 的默认控制器仍然是 `Single Controller`：

```text
Agent Portfolio
  → Single Controller
  → Plan DAG
  → Step / optional Specialist Agent
  → Join
  → Final Synthesis
  → Domain Admission
```

只有当执行角色拥有独立 Context、独立 Permission、独立 Capability / Tool Set、独立 Model Profile、独立 Lifecycle、独立 Resource 或有意义的并行调查边界时，才允许升级为 `Specialist Agent`。Query Rewrite、Extraction、Rerank、一次 Tool Call 和普通 Reasoning 默认仍然是 Step、Capability、Skill 或 Tool，不是 Agent。

Specialist Agent 只能产生 `Proposal`、`BranchResult`、`EvidenceReference`、`Observation` 或 `Recommendation`。它不能直接修改 Canonical Domain State、批准权限、绕过 Budget、激活新 PlanVersion、未经审批执行副作用或提交长期 Memory。所有并行结果必须回到 `Controller → Join → Evaluation → Final Synthesis → Domain Admission`。

总体 Runtime 采用：

```text
Fixed AgentRunGraph
  + Dynamic Plan DAG
  + Fixed StepExecutionGraph
```

Simple Task 使用 Deterministic Single-Step Plan；Complex Task 才使用 Dynamic DAG Plan。任何任务都不能通过 `direct_answer` 绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。

### 7. Capability / Skill & Tool Runtime Boundary

05 是一个候选模块，但模块合并不表示语义合并。

**Capability / Skill** 面向专业能力：

```text
CapabilityRequirement
  → Provider Resolution
  → Provider Conformance
  → Execute
  → Capability Evaluation
  → Proposal / Candidate / Score / Reference
```

Event Extraction、Event Alignment、Conflict Detection、Dispute Identification、Fact–Article Mapping、Legal Applicability、Similar Case Analysis 和 Statute Recommendation 都只能通过受控 Capability Contract 进入 Runtime。`Research Artifact != Capability`，`Capability != Tool`，`Capability Result != Canonical Domain Fact`。

**Tool / External Action** 面向外部查询或副作用：

```text
Agent Proposal
  → PreparedAction
  → Security Gate
  → Approval Gate when required
  → Execute
  → Observation / EffectReceipt
  → Reconcile
```

Tool Runtime 处理 Idempotency、Approval、Effect、Outcome Unknown、Retry、Reconciliation 和 Capability Drift。`Timeout != Tool Failed`；Unknown external outcome 必须先 Reconcile，不能 Blind Retry。MCP 是一种接入协议，不替代 Zuno 的业务权限、审批、参数校验、幂等和审计。

### 8. Model Gateway

Model Gateway 作为独立候选责任域，因为 Model 不只服务 Runtime，也服务 Knowledge、Capability、Eval、Extraction、Rerank、Critic 和 Synthesis。它负责 Model Role、Provider、Routing、Budget、Quota、Token、Cost、Timeout、Fallback、Structured Output、Egress Policy 和 Usage Receipt。

候选角色包括 `TASK_ANALYZER`、`PLANNER`、`PLAN_REPAIR`、`EXECUTOR_FAST`、`EXECUTOR_REASONING`、`QUERY_REWRITER`、`EXTRACTOR`、`CRITIC`、`SYNTHESIZER` 和 `FINAL_CRITIC`。弱模型升级可以遵循：

```text
EXECUTOR_FAST
  → Parameter Retry
  → EXECUTOR_REASONING
  → Critic: Retry / Replan / Abstain
```

模型只能产生 Proposal，不能提交 Canonical DB、批准权限、激活 PlanVersion、绕过 Budget、执行未经审批的 Effect 或提交长期 Memory。

### 9. Memory & Context

Memory 负责 Context Assembly、Short-term Context、Long-term Memory、Reusable Summary、Preference、Experience、Reflexion Candidate、Retention、Expiry、Deletion 和 Provider Integration。OpenViking 可以作为 Memory / Context Provider，但不是唯一 Provider，也不属于 Zuno 的不可替换架构核心。

```text
Memory != Domain State
Memory != Knowledge View
Memory != Runtime Checkpoint
```

Memory 可以按 Scope 召回、压缩、过期或删除，但不能替代 `FactVersion`、`FindingVersion`、`HumanDecision` 或 `WorkProduct`。长期 Memory 对法律任务没有稳定收益时，允许删除这一层，只保留当前任务上下文和正式 Domain State。

### 10. Security & Governance

Security 是跨层责任候选，负责 Identity、Tenant、Principal、Grant、Policy、Authorization、Approval、Secret、Data Classification、Model Egress、Tool Permission、Security Gate 和 Audit Requirement。

`Run Start Authorization != Run Lifetime Permanent Lease`。每一次新的 Document Read、Retrieval、Secret Access、Model Egress、Tool Call、External Effect 和 Formal Commit 都必须依据当前 Policy。权限撤销至少阻止新的未授权访问；已经载入内存的数据能否继续 CPU-only 处理，留给 Security Part B / Module 在证据和风险策略基础上冻结。

### 11. Observability & Evaluation

Observability 是一等架构能力，但不是单一 SaaS 产品。所有候选模块都通过 `ObservabilityTracePort / Telemetry Contract` 输出 OTel-compatible signal；LangSmith 是当前 Agent / LLM Trace 与 Eval 的 preferred provider，而不是 Architecture 本身。

当前仓库证据只支持：`ObservabilityTracePort`、Noop / InMemory Adapter、LangSmith-compatible Adapter、metadata / redaction、focused tests 和部分评测 Trace 基础可用。`AgentRunGraph`、`StepExecutionGraph`、Retrieval Round、Tool Gateway、Final Gate 的 full-chain wiring 与 LangSmith Experiment integration 仍是 Target / Gap，不能写成 `FULL OBSERVABILITY CURRENT` 或 Production Ready。

系统层使用 OpenTelemetry-compatible Contract，并允许接入 Grafana-compatible backend；Prometheus、Tempo、Loki 或 LangSmith Cloud 都不是强制的物理选择。Production Provider 必须依据 data residency、法院政策、Security Requirement 和 self-host / on-prem 约束决定。

司法数据默认不完整外传。ID、Hash、Version 和必要 Metadata 可以按 Policy 记录；完整 Document Content、Prompt Content、Tool Result、PII 和 Secret 默认 `REDACT / DISABLED`，Secret `NEVER EXPORT`。具体 Data Classification 由 Security 决定。

### Canonical Trace Dimensions

按适用性贯通：

```text
request_id
task_id
run_id
trace_id
plan_version
step_id
dispatch_group_id
dispatch_item_id
tool_call_id
effect_id
knowledge_generation
domain_version
security_epoch
```

Canonical Agent Trace Nodes 包括 `AgentRun`、`PlanCreation`、`PlanValidation`、`StepExecution`、`RetrievalRound`、`QueryRewrite`、`BM25`、`Vector`、`Graph`、`Fusion`、`Rerank`、`EvidenceAcceptance`、`ToolInvocation`、`StepAcceptance`、`Reflection`、`Replan`、`FinalSynthesis`、`CitationValidation`、`FinalGate` 和 `RunOutcome`。这些是 Trace 节点，不是新的业务状态机。

Decision Trace 必须解释为什么发生 Retry、Replan、Reflection、Human Review、Abstain、Final Reject 或 Degradation。例如：`StepAcceptance: rejected / reason: evidence_insufficient`、`Replan: true / reason: capability_assumption_invalid`、`FinalGate: review_required / reason: degraded_retrieval`。

### 12. WorkBuddy / Dify 的竞争边界

截至 2026-08，公开官方资料已经显示 WorkBuddy / CodeBuddy 企业智能体覆盖 Agent Runtime / Session、模型和 System Prompt、Skill、Expert / Expert Team、MCP、Memory、Knowledge Base / RAG、Subagent、沙箱、凭据和 Manifest 等能力；Expert Team 还支持多角色拆解、并行执行和整合交付。见 [WorkBuddy 企业智能体](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/CloudAgent)、[WorkBuddy 专家中心](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Expert-Center) 和 [WorkBuddy MCP 指南](https://www.workbuddy.ai/docs/zh/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide)。

Dify 官方文档也已经覆盖 Visual Workflow / 应用编排、Knowledge / Datasource、Agent Strategy、Model、Tool、Extension / HTTP Endpoint、Trigger、Application API 和 Monitoring 等扩展或运营边界；其插件选择文档明确区分 Tool、Model、Agent Strategy、Extension、Datasource 和 Trigger。见 [Dify 插件类型选择](https://docs.dify.ai/en/develop-plugin/getting-started/choose-plugin-type)、[Dify 知识库检索](https://docs.dify.ai/guides/knowledge-base/retrieval) 和 [Dify 产品介绍](https://docs.dify.ai/versions/3-7-x/zh/user-guide/introduction)。上述资料是截至当前检查时间的外部 Baseline，具体版本和部署能力仍需在 Benchmark 前重新核对。

因此，下列能力不能单独作为 Zuno 的核心 Differentiation，而是 `TABLE_STAKES`：

```text
Agent / Multi-Agent
Knowledge Base / RAG
Skill / Tool / MCP
Memory
Workflow
Model switching
通用 Agent UI、Session 和基础编排
```

Zuno 不需要证明 WorkBuddy / Dify “做不到”这些能力，也不以通用 Host Feature 作为主要竞争维度。Zuno Target 要验证的是更窄、更高风险的 Domain Depth：业务状态是否有唯一 Owner，证据是否足够支撑结论，Finding 是否能随依赖变化而 stale，Human Decision 是否可追溯，外部副作用是否可审计。WorkBuddy 或 Dify 可以作为 Zuno Host；如果 `Generic Host + Zuno Legal Backend` 已经达到目标质量和恢复边界，就没有理由为了“拥有平台”保留 Native Runtime。

#### 面向关键追问的 Build / Buy 答案

- **为什么不是 Dify？** 如果任务只是通用 Workflow、RAG 或 Tool，优先复用 Dify；Zuno 只保留被验证有必要的 Legal Capability、Legal Domain State、Evidence / Applicability、Human Review、Legal Eval 和特殊恢复 / 审计。
- **为什么不是 WorkBuddy？** WorkBuddy 已覆盖通用 Agent、Expert、Skill、MCP、Memory、Knowledge 和 Subagent；它可以成为 Host。Zuno 的问题不是再造通用 Agent Surface，而是提供 Domain Capability Contract、Legal Evidence Semantics、Persistent Legal State、Domain Admission 和 Legal Evaluation。
- **为什么要 Agent？** 固定任务如果 Workflow 足够，就使用 Workflow；只有 Evidence 会改变后续步骤、需要动态补证据、能力选择或 Replan 时，才引入受控 Agent Runtime。
- **为什么 Multi-Agent？** 默认不需要。优先使用 Single Controller + Capability + Step；只有角色真正拥有独立 Context、Permission、Lifecycle、Resource 或并行调查边界时，才升级为 Specialist Agent。
- **为什么不直接把论文模型包装成 API？** API 只解决“能调用”，真实产品还要解决版本、适用任务、权限、输入输出 Contract、可用性、Fallback、Eval、Trace、Evidence 和 Human Review，因此需要 Capability Governance。

### 13. 六个可验证的 Target Differentiation

这些不是已经证明的产品优势，而是 `TARGET_HYPOTHESIS_PENDING_RED_TEAM` 下需要由真实任务、专家验证和 A/B/C Benchmark 证伪或收敛的六个候选方向。

#### A. RESEARCH-TO-CAPABILITY

科研成果不是论文列表，而是候选能力的来源：

```text
Research Artifact
  → Domain Capability
  → Versioned Provider
  → Provider Conformance / Legal Eval
  → Agent / Skill Availability
```

候选能力可以包括 Event Extraction、Event Alignment、Conflict Detection、Dispute Identification、Evidence Chain、Legal Element Extraction、Fact–Article Mapping、Statute Recommendation 和 Similar Case Retrieval。具体 Provider 必须可替换；论文、专利和 Research Prototype 不是 Runtime Object，也不能直接成为 Canonical Domain State。

#### B. LEGAL EVIDENCE & APPLICABILITY

普通 RAG 主要回答“有没有相关文本”。Zuno Target 还要验证：Evidence 来源是什么、属于哪个 Document Version、是否支持具体 Claim、Authority 的 jurisdiction / version / scope 是什么、是否适用于当前事实、是否存在冲突、证据是否足够。目标概念包括 `Evidence Sufficiency`、`Legal Applicability`、`Citation Lineage` 和 `Authority Version / Scope`，但不在本层预先设计数据库表。

#### C. PERSISTENT DOMAIN STATE

普通 Agent Output 是一段 Answer 或 Artifact；Zuno Target 把 Matter、Evidence、Fact、Event、Conflict、Dispute、Legal Issue、Finding、Human Decision 和 WorkProduct 作为可能长期存在、版本化和可追溯的业务对象。`Chat Answer != Canonical Legal Result`，`Runtime Checkpoint != Domain State`。新 Evidence 到来时，旧 Finding 可以成为 `stale`、`review_required` 或 `superseded`，不能继续作为永远正确的聊天历史。

#### D. HUMAN-VERIFIABLE PROFESSIONAL WORK

AI 可以承担 reading、retrieval、extraction、alignment、comparison、candidate reasoning 和 drafting；专业人员负责 review、legal judgment、approval 和 formal adoption。正式交付应允许查看 Evidence、Citation、Conflict、Proposal 和 Human Decision，而不是只展示一段不可复核的聊天答案。

#### E. LEGAL EVAL / RELEASE GATE

法律 AI 不能以“感觉回答不错”作为发布标准。Target 逐步需要 Task Dataset、Failure Taxonomy、Retrieval Eval、Citation Eval、Applicability Eval、Fact / Event Eval、Conflict Eval、Grounded Answer Eval 和 Human Review Eval。Provider 或 Agent Version 只有通过对应 Eval Gate，才获得相应的 Usage Eligibility；这些能力目前都不是 Current 证明。

#### F. NATIVE + EMBEDDED PRODUCT MODE

Zuno 不要求甲方替换现有系统。Native 模式可以是：

```text
Zuno Judicial Workbench
  → Zuno Agent
  → Domain Capability
  → Versioned Domain Result
```

Embedded 模式可以是：

```text
Court Existing System / WorkBuddy / Dify / Other Agent Host
  → API / MCP / Versioned Contract
  → Zuno Domain Capability / Agent
  → Domain Result / Eval
```

产品策略是“能合作就合作，只自研 Generic Host 无法替代且被验证有价值的 Domain Depth”。

四条需要保持的概念边界是：

```text
Research Artifact → Domain Capability
Business Process   → Skill / Task Template / Policy
Business Fact      → Domain State
Execution          → Runtime
```

这四条是 Conceptual Target，不是历史项目事实，也不冻结最终模块数量。

### 14. Runtime 不是业务后端

FastAPI 是 Application / HTTP Interface，负责认证、Matter / Document / Review / Run API 以及状态查询；它不是 Agent Runtime。LangGraph 若被保留，只是 Agent orchestration / durable workflow provider，负责 Run、Plan、Checkpoint、Resume、Interrupt、分支和受控 Replan，不承载普通 CRUD，也不拥有 Canonical Case Fact。

Single Controller 是默认起点。复杂任务可以派生 Ephemeral Worker 或受控 Specialist Agent，但只有当角色拥有独立 Context、Permission、Capability、Lifecycle 或 Resource 时，才有理由称为 Agent。否则它可能只是 Step、Skill 或 Tool。Persistent Multi-Agent Team 不是默认结论。

### 15. 物理服务的理由与代价

Python-only 是 Owner Target Constraint，理由是当前 AI / NLP / PyTorch / LangGraph 生态与团队复杂度；这不是“Python 性能够用”的空泛结论。LLM、Embedding、Vector DB、Graph DB、PostgreSQL、Object Storage 和外部 API 多数是 I/O 或外部服务边界，OCR、Parsing、Embedding、Graph Build 和 Eval 等 CPU / GPU 重任务应进入独立 Worker，不阻塞 FastAPI 请求线程。

Microservice 不是预先承诺的终局 Target，而是 `EVIDENCE-GATED DEPLOYMENT REFINEMENT`。默认物理起点是 `Modular Python Backend` 加上有理由的独立 Worker。只有当某个边界出现可重复证据，证明它需要 Independent Scaling、Failure Isolation、Security / Secret Isolation、Distinct Availability、Independent Deployment Lifecycle、Stable Cross-host API 或 Distinct Data / Operational Ownership 时，才拆成独立 Network Service。每个候选都要回答：**Why service? Why not library? Why not worker?**

网络延迟、序列化、Schema version、Partial Failure、Retry Storm、Tracing、Secret Distribution 和本地开发复杂度都是实际代价。默认可以从模块化 Python 服务加独立 Worker 开始；Service Count、Database physical split、Queue technology、Model Gateway 和 Graph Provider 都保持可反转。

### 10. 最危险的失败与恢复（扩展后的跨层恢复规则）

需要优先解决的不是“哪个框架更潮”，而是状态不一致：Domain Commit 已成功但 Runtime Checkpoint 仍停在执行前；Tool 已执行但消息重复投递；新证据使 Fact / Conflict / Finding stale；权限在等待期间被撤销；Provider 返回 unknown outcome。系统还能继续生成结果，不等于结果仍然有资格作为正式业务使用。

恢复时先读取 Domain Owner 的最后合法版本，再比较 Runtime Control State、Knowledge Projection、EffectReceipt、Provider Operation ID 和当前权限。只有完成对账，才能选择 Resume、Retry、Replan 或 Human Review。HTTP 200、Queue ACK、Index Write 或 Checkpoint Commit 只能证明各自边界，不代表业务事实已完成。

Provider 降级以后必须重新判断 Evidence Requirement、Quality Requirement、Security Requirement 和 Human Review Requirement。结果可以继续执行，但可能只能进入正常 Formal Admission、`review_required`、非 Canonical Draft 或 `Abstain / Reject`；不能只靠 UI Warning 表达质量变化，也不创建第二套 Degradation State Machine。

Run Start Authorization 不是 Run Lifetime Permanent Lease。长任务每一次新的 Document Read、Retrieval、Secret Access、Model Egress、Tool Call、External Effect 和 Formal Commit 都必须依据当前有效 Policy。权限撤销至少阻止新的未授权访问；已经载入内存的数据在撤权后的 CPU-only 处理策略留给 Security Part B 冻结。

长任务也不能假定 Tool / MCP / Capability 从 Plan 创建到真正执行期间永久不变。调用前必须重新确认当前能力仍满足 Plan / Step 的 Capability Assumption；瞬时执行失败才 Retry，能力、Schema、语义或权限变化导致原计划假设失效时进行 `Capability Re-resolution` 并必要时 Replan，没有安全兼容路径就 Stop / Human Review。Agent 不得看到新 Schema 后自行猜参数继续执行，Unknown External Effect 必须先 Reconcile，不能盲目 Retry。

### 17. A/B/C Kill Test

比较必须控制 Same Base Model、Same Raw Corpus、Same External Tools、Comparable Prompt、Comparable Token Budget 和 Comparable Time Budget：

```text
A — Generic Host + Legal Prompt / Skills
B — Generic Host + Zuno Legal Backend / Legal Capabilities
C — Zuno Native Runtime + First-class Legal Domain State
```

如果 `B > A`，说明 Legal Backend / Legal Capability 可能产生价值；如果 `C ≈ B`，应缩减或外部化 Native Runtime；只有 `C > B` 且收益可归因、可重复时，才支持 Domain-aware Native Runtime；如果 `B ≈ A`，应删除没有产生收益的 Legal Backend 复杂度。

指标必须覆盖 Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict / Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance、Task Completion、Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls 和 Domain State Reuse Rate。不能只比较单一 LLM Judge 分数。

### 12. 取舍与反转条件（复杂度删除规则）

这套 Target 付出的成本是版本、证据依赖、跨服务序列化、运行恢复、可观测性、评测和部署复杂度。它只有在复杂法律任务中带来可测量收益时才值得保留：

- Host + Legal Backend 足够：缩减 Native Runtime；
- Hybrid Retrieval 已覆盖关系型任务：Graph 降为条件 Provider；
- Single Agent + 并行工具足够：不升级为 Persistent Multi-Agent；
- Matter DB + Runtime Checkpoint 足够：删除不必要的 Memory 层；
- 模块化服务 + Worker 已满足资源和故障隔离：合并服务；
- MCP / 现有 Sandbox 已满足安全边界：不重复建设 Tool Runtime。

## Target Status Boundary

本节是 Target 设计状态，不是 `docs/project/` 的历史事实或 `docs/evidence/` 的 Current 证据。`ACCEPTED_TARGET` 只表示方向已被治理接受；它不表示代码已实现、收益已测量或外部生产资格已获得。

| Target 能力 / 边界 | 状态 | 关闭或反转条件 |
| --- | --- | --- |
| Target Product Thesis | `TARGET_HYPOTHESIS_PENDING_RED_TEAM` | 尚未完成 WorkBuddy / Dify 对比、法院真实 A/B 或 Domain Layer 收益验证；不得写成 Proven Differentiation |
| Research-to-Capability Governance | `TARGET_ONLY` / `PROPOSED` | 需要 Provider Conformance、Capability Evaluation 和真实任务证明研究成果工程化链路有收益 |
| Python-only Backend | `ACCEPTED_TARGET` | Owner 工程约束；不证明历史或生产链路 |
| Physical Service Split | `EVIDENCE-GATED` | 默认模块化 Backend + Worker；只有独立扩缩容、故障、安全、可用性、生命周期、跨主机 Contract 或独立数据/运营 Owner 证据成立才拆分 |
| Legal Domain State | `ACCEPTED_TARGET` | 需要复杂法律任务 Benchmark 证明收益 |
| Evidence / Citation Provenance | `ACCEPTED_TARGET` | 需要真实 QA 证明来源和引用闭环 |
| Legal Intelligence Provider Boundary | `ACCEPTED_TARGET` | Provider 输出必须可替换、可评测，不能直接提交 Domain Fact |
| Hybrid Retrieval | `ACCEPTED_TARGET` | 需要 Recall、Citation、Latency 和 Cost 测量 |
| Agentic Retrieval / GraphRAG | `PROPOSED` / `HYPOTHESIS` | 只有 A/B/C 与 Graph Kill Test 证明增益才保留 |
| Memory / Context | `PROPOSED` / `DEFERRED` | 不能成为 Canonical Legal Fact；需要替换和质量证据 |
| Single Controller / Controlled Multi-Agent | `ACCEPTED_TARGET` / `PROPOSED` | 与更简单的单 Agent + 并行工具比较 |
| Tool / MCP / Security / Human Review | `ACCEPTED_TARGET` | 需要授权、审批、幂等、Receipt、对账和真实 Review 证据 |
| Physical Service Count | `NOT_DECIDED` / `EVIDENCE-GATED` | `FINAL_MODULE_COUNT: NOT_DECIDED`；不预先承诺 Network Service 数量 |
| Knowledge Readiness | `ACCEPTED_TARGET` | 必要 Scope、Version Set 和 Knowledge View 未 Ready 时等待、拒绝或显式缩小 Scope |
| Result Eligibility / Domain Admission | `ACCEPTED_TARGET` | 降级上下文必须重新检查证据、质量、安全和人审要求 |
| Continuous Authorization | `ACCEPTED_TARGET` | 每次新的受保护访问都按当前 Policy 决定；具体撤权后内存处理策略仍开放 |
| Tool Capability Compatibility | `ACCEPTED_TARGET` | 兼容则继续，瞬时失败 Retry，假设失效 Replan，无安全路径 Stop / Review |
| 10-Module Logical Candidate | `CANDIDATE_ONLY` | Freeze Red / Blue 发现职责重叠、缺失或错误边界时合并、拆分或删除候选 |
| Observability Contract | `OTEL_COMPATIBLE` / `TARGET` | 保持 Provider 可替换；完整链路、生产数据策略和 Experiment 仍需证据 |
| Native + Embedded Product Mode | `TARGET_ONLY` / `PROPOSED` | 需要 Integration Spike 证明 Host Contract、Domain Capability 和结果回传边界可行 |
| Production Readiness | `NOT_ESTABLISHED` | 由独立运行、安全、HA、Eval 和外部资格证据证明 |

## Product Thesis 与 A/B/C Kill Test

Zuno 的 Target 差异不是堆更多 Agent，而是验证高风险法律任务是否需要可追溯、可复核、可持续更新且拥有明确状态 Owner 的法律工作结果。比较必须使用相同模型、原始语料、外部 Tool、相近 Prompt、Token 和时间预算：

```text
A — Generic Host + Legal Prompt / Skills
B — Generic Host + Zuno Legal Backend / Legal Capabilities
C — Zuno Native Runtime + First-class Domain State
```

- `B > A`：支持 Legal Backend / Legal Capability 有价值；
- `C ≈ B`：缩减复杂 Native Runtime，优先 Host + Legal Backend；
- `C > B`：才支持 Domain-aware Native Runtime 的额外复杂度；
- `B ≈ A`：删除没有产生收益的 Legal Backend 复杂度。

指标至少包括 Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Reviewer Acceptance、Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls 和 Domain State Reuse Rate。

## OVERALL_ARCHITECTURE_FREEZE_GATE

当前状态：`REFINED_BASELINE_READY_FOR_FREEZE_REVIEW`。这不是模块冻结，也不是 Production Gate。只有下一轮 Overall Architecture Freeze Red / Blue 通过以下检查，才允许把候选模块图提交为冻结结果：

1. 高级工程师只读 `architecture.md` 能讲完整 Zuno；
2. Simple Grounded QA、Complex Legal Analysis 和 Controlled External Effect 三条 Flow 都闭合；
3. 每种长期 Fact / State 都有唯一 Owner；
4. Domain、Runtime、Memory 和 Knowledge Projection 边界清晰；
5. Retry、Replan、Reconcile 和 Recovery 不混用；
6. Security Gate 不可绕过；
7. Human Review 位置明确；
8. Multi-Agent 不是自治默认模式；
9. Capability 与 Tool 虽暂时共候选模块，但 Effect Semantics 仍分离；
10. Observability 可以重建关键 Run 和关键决策；
11. LangSmith 是 Provider，不是硬编码 Architecture；
12. Physical Service Count 仍然 Evidence-gated；
13. Red Team 已难以提出新的跨层责任缺口。

在 Freeze Review 通过前：

```text
MODULE_DOCUMENTS: NONE
MODULE_DECOMPOSITION_GATE: NOT_OPEN
```

## Part B — Detailed Architecture Specification

### Cross-layer Contract Registry

| Contract | 输入 | 输出 | 唯一 Owner | 失败与验证 |
|---|---|---|---|---|
| Product / Agent Invocation | User / Host Request、Workspace、Matter、Agent Version、Configuration | Task、AgentRun Request、Review / WorkProduct Surface | Product Surface & Agent Portfolio | Scope 不完整、Agent Version 不可用、Host Contract 不兼容；API / Integration Test |
| Domain Admission | Proposal、Evidence Reference、权限上下文、DomainVersion、Degradation Context、Quality / Security Decision | Canonical Version、review_required 或 rejected | Domain Owner | CAS 冲突、来源不足、降级后不合格；Admission Contract Test |
| Runtime Execution | PlanVersion、Domain Snapshot、Budget、Policy | Step / Branch Result、Checkpoint、RunOutcome | Agent Runtime | Domain Generation 不一致；Recovery Replay |
| Evidence Retrieval | QueryClass、Claim、Declared Scope、DocumentVersion Set、Knowledge View | EvidenceCandidate、CitationLineage、RetrievalReceipt | Knowledge | PARTIAL、STALE、MISSING_REQUIRED_SOURCE、VERSION_MISMATCH、ACL 泄漏、引用错 span；Readiness / Citation / Graph Ablation |
| Legal Capability | Evidence / Fact Candidate、Capability Contract、Provider Policy | Proposal、Observation、Reference 或 Receipt | Capability / Tool Runtime | Provider 不可用、版本不兼容；Provider Conformance / Replacement Test |
| External Effect | PreparedAction、SecurityEpoch、Approval、Idempotency Key | EffectReceipt、outcome_unknown 或 rejected | Tool / Security Owner | 超时、重复副作用；Fault Injection / Reconciliation |
| Model Invocation | Model Role、Provider Policy、Budget、Egress Policy、Structured Output Contract | Model Output、Usage Receipt、Provider Error | Model Gateway | Timeout、Quota、Cost、Egress 或 Schema 失败；Fallback / Usage Test |
| Context Assembly | Task Scope、Domain Snapshot、Memory Policy、Knowledge References | Working Context、Memory Reference、Context Receipt | Memory & Context | Scope 泄漏、过期内容、Provider 不可用；Retention / Redaction Test |
| Observability Telemetry | Trace Dimensions、Decision Event、Redaction Policy、Run / Eval Event | OTel-compatible Signal、Trace Reference、Decision Trace | Observability & Evaluation | 脱敏失败、Delivery Failure、链路断裂；Trace Contract / Redaction Test |
| Persistence / Worker | Domain / Runtime / Knowledge / Effect / Eval Artifact、Job | Durable Record、Checkpoint、Object / Index Artifact、Worker Outcome | Infrastructure & Persistence | Durability、Duplicate Job、Backpressure、Recovery；Persistence / Fault Test |
| Evaluation | DatasetVersion、Variant、预算、Trace | RawResult、Metric、Comparison、ReleaseDecision | Eval Owner | 分母变化、不可比、阻塞；Reproducible Eval |

### Capability Governance Contract Skeleton

以下是 Research → Capability 的最小 Contract Skeleton，只冻结概念边界，不提前设计表、类或最终模块：

| Concept | 作用 | 不能替代 |
|---|---|---|
| `DomainCapability` | 面向一个专业任务的稳定能力契约、输入输出和适用范围 | 论文、Prompt 或 Runtime Step |
| `CapabilityRequirement` | 任务对输入材料、权限、质量和运行条件的要求 | 用户随口提出的未验证需求 |
| `CapabilityProvider` | 实现 Capability 的模型、算法、服务、Tool 或外部 Provider | Canonical Domain Owner |
| `CapabilityVersion` | 可选择、可回滚、可比较的能力版本 | Document Version 或 Domain Version |
| `ProviderConformance` | 检查 Provider 是否满足 Contract、权限和输入输出约束 | 业务结果审批 |
| `CapabilityEvaluation` | 记录针对任务类别的质量、成本、延迟和失败证据 | 单次 Demo 的主观印象 |
| `CapabilityAvailability` | 表达某能力版本在当前租户、任务、权限和环境下是否可用 | 模型自行决定是否可以调用 |

研究论文 / 专利不是 Runtime Object。研究成果只有经过 Engineering Provider、Conformance 和 Evaluation，才可能获得某个受控的 Capability Availability；模型和算法仍然只能产生 Proposal、Candidate、Score、Observation 或 Reference，不能直接提交 Canonical Domain State。

### Knowledge View Readiness Contract

Formal Run 必须绑定四类概念：Declared Scope、Document Version Set、Knowledge View / Generation 和 Readiness Receipt。它们是跨层 Contract，不等于必须新增数据库表或 Readiness Service。Readiness Receipt 只能说明当前 Knowledge View 对声明 Scope 的覆盖状态，不能把未声明材料静默纳入结果。

最低失败语义是：`PARTIAL` 表示声明 Scope 尚未完全可用；`STALE` 表示 View 与绑定版本不再一致；`MISSING_REQUIRED_SOURCE` 表示必要来源缺失；`VERSION_MISMATCH` 表示检索视图与 Run 绑定版本不一致。默认情况下这些状态阻止 Formal Run；若允许 Partial Run，必须显式缩小 Scope，结果不能直接取得 Full Scope Formal Admission。

### Result Eligibility 与 Domain Admission Contract

`Execution Can Continue` 与 `Result Is Eligible for Formal Business Use` 是两个不同判断。Graph、Memory、Model、Retrieval 或 Capability Provider 降级后，Answer Policy 必须把 Degradation Context 传给 Domain Admission；Admission 重新检查 Evidence Sufficiency、Quality Evaluation、Security Decision 和 Human Review Requirement。结果只能进入现有的 Canonical Version、`review_required` 或 `rejected` 语义；Draft 如果保留，只表示尚未 Canonical Admission 的输出，不是新的正式 Domain State。

### Continuous Authorization Contract

Security Owner 拥有 Authorization Decision。每一次新的 Read、Retrieval、Model Egress、Secret、Tool、Effect 和 Commit 都依据当前 Policy Epoch / Current Authorization；Domain、Runtime、Knowledge 和 Tool 只能消费该决定，不能自行扩大权限。Resume、Retry、Replan 后不得沿用已经失效的旧 Authorization Decision。撤权后至少阻止新的未授权访问，已经加载内容是否允许继续 CPU-only processing 留给 Security Part B / Module，不在本轮冻结。

### Capability Compatibility Contract

Plan / Step 可以依赖一个 Capability Assumption，但不预设全局 Schema Registry。真正调用前重新解析当前 Tool / MCP / Capability；兼容则继续，Capability 语义未变的瞬时执行失败才 Retry，原假设失效则 Capability Re-resolution 后 Replan。Capability 消失、权限变化或 Schema / semantics 没有安全兼容路径时 Stop / Human Review。`Retry != Replan`。External Effect Outcome Unknown 先 Reconcile；Agent / Model 不得猜新参数继续执行。

### Service、通信与队列边界

Logical Responsibility 不等于 Physical Service。候选物理角色可以包括 Edge / API、Platform / Domain、Agent Runtime、Knowledge、Tool / Sandbox 和 Eval Worker，但它们不是最终服务清单，也不是 Current。默认保持模块化 Backend + Worker；是否拆分必须由独立 Scaling、Failure、Security、Availability、Lifecycle、Stable Cross-host API 或独立 Data / Operational Ownership 证据支持。

### Physical Deployment Gate

服务拆分是证据闸门，而不是服务清单。每个候选边界至少要说明 Scaling、Failure、Security、Availability、Lifecycle、Cross-host Contract 或 Operational / Data Ownership 中的可重复证据，并明确 Why Service、Why not Library、Why not Worker。Service Count、Database-per-service、Kafka、Kubernetes、Service Mesh、2PC 和 Saga Framework 均不在本总体架构中预冻结。

### Failure / Recovery Semantics

这些语义属于跨层架构，不能由各候选模块各自发明一套互不兼容的状态机：

| 控制 | 触发条件 | 总体动作 |
|---|---|---|
| Retry | Execution failed，但 Plan / Capability Assumption / 依赖和安全条件仍成立 | 重试同一个 Step / Attempt；保留 Idempotency 和 Budget |
| Replan | Plan structure、Dependency、Capability、Permission 或事实假设失效 | 创建新的 immutable `PlanVersion`；并行任务经过 Replan Barrier |
| Reconcile | External Effect outcome unknown | 查询 Provider Operation ID、Idempotency Key、Receipt 或外部资源事实；禁止 Blind Retry |
| Recovery | Domain Commit 成功但 Runtime Checkpoint stale | Domain State wins；读取最后合法 Domain Version，再修复 Runtime Control State |
| Staleness | 新 Evidence 使 Finding Dependency 失效 | 标记 `stale` / `review_required`，启动 targeted reevaluation，不静默覆盖历史版本 |

`Retry != Replan`。瞬时网络错误不能证明计划失效；Tool Schema / semantics / permission 漂移则不能猜参数继续。Unknown External Effect 也不能由 Checkpoint 状态代替真实外部事实。

### Safe Parallelism 与 Quality Control

Ready Step 只有在 Dependencies Ready、Inputs Ready、No Resource Conflict、No Conflicting Side Effect、Budget / Quota Allows 和 Security Gate Allows 全部满足时才允许并行。`LangGraph Send`、`DispatchGroup`、`DispatchItem`、`StepRun`、`BranchResultRef` 和 Idempotent Reducer 是候选执行机制，不是新的模块。

默认串行的情况包括 Data Dependency、Same Resource Write、Irreversible Side Effect、Exclusive Resource、Replan 和 Final Synthesis。每个 Action 都需要 Evaluation，每个 Step 都需要 Acceptance，但不是每个 Step 都自动触发 LLM Reflection。Acceptance Failure、Evidence Conflict、Critical Decision、Repeated Failure 和 High Risk 才触发 Step Reflection；Partial Failure 或 Conflicting Branch Result 触发 Join Reflection。

CRUD、小命令和外部互操作默认使用 HTTP / API；长运行 Agent Run、Ingestion、Embedding、Graph Build、Sandbox 和 Eval 才进入带 JobId、Attempt、Timeout、Cancellation、Retry、Dead Letter 和 Backpressure 的异步队列。高吞吐内部 gRPC 只是候选，不默认所有服务都使用 gRPC，也不默认所有交互都用 Event。

FastAPI 只拥有 Application / HTTP Interface；LangGraph 只拥有 Agent Control State。PostgreSQL 保存 Canonical Business / Domain State；Runtime Checkpoint 保存 Graph Control / Execution State。两者必须分别验证和恢复，不能把 Checkpoint 当成 Case Fact。

### State、Version 与 Recovery Contract

本节先给出跨 Domain、Runtime、Knowledge 和 Memory 的共同恢复原则：版本化业务事实由 Domain Owner
管理；Runtime 只保存执行控制；Memory 只保存可按策略复用的上下文。任何新输入都必须比较
依赖、版本、Knowledge Generation / Readiness、权限和副作用状态，再决定继续、重试、重规划或人工复核。

### Domain State、Runtime State 与 Memory（含 Knowledge Projection）

Domain State 包括 Matter、DocumentVersion、Evidence、Fact、Event、Conflict、Dispute、Finding、HumanDecision 和 WorkProduct。Runtime State 包括 AgentRun、Plan、Step、Branch、Interrupt、Checkpoint 和 Budget。Memory 包括 Working、Session、Matter Context、Long-term 或 Reflexion Candidate，必须可以按策略过期或删除。Knowledge Projection 包括 Parse、Chunk、Index、Graph Projection、Knowledge View、Generation 和 Readiness；它是可重建的检索投影，不是 Domain Truth。

```text
Domain State != Runtime State != Memory State
Knowledge Projection != Domain Truth
```

New Evidence 到来时，系统通过 Dependency 发现受影响的 Fact / Conflict / Finding；将旧版本标为 stale 或 review_required，创建新的 bounded evaluation run，并由 Domain Owner / Human Review 提交新版本。不能因为 Memory 召回了旧文本，就把它当作最新业务事实；也不默认采用 Event Sourcing，PostgreSQL 当前事实及版本足够时优先保持简单。

### Owner Registry（Canonical Ownership Matrix）

任何模块、Provider、Agent 或 Receipt 都不能因为“看到了数据”就成为该数据的 Owner。特别是 Receipt 只能证明某个边界发生了什么，不能冒充其他模块的领域成功。

| State / Fact / Artifact | 唯一 Owner | 允许输出或引用 |
|---|---|---|
| Matter | Legal Domain & Work Product | Domain Snapshot、Matter Reference |
| Document business identity / version | Legal Domain & Work Product / Document Owner | DocumentVersion Reference |
| Evidence business reference | Legal Domain & Work Product | Evidence Reference |
| Knowledge View / Generation / Readiness | Knowledge & Evidence | Knowledge View Reference、Readiness Receipt |
| EvidenceCandidate | Knowledge & Evidence | Candidate、CitationLineage、RetrievalReceipt |
| CitationLineage | Knowledge & Evidence | Citation Reference |
| Event / Conflict / Dispute Proposal | Capability / Skill & Tool Runtime | Proposal、Observation、Reference |
| Canonical Fact / Finding / LegalIssue | Legal Domain & Work Product | Version、Admission Result |
| HumanDecision | Legal Domain & Work Product | Review Decision、Admission Input |
| WorkProduct | Legal Domain & Work Product | Versioned WorkProduct、Response |
| Agent Definition / Version / Configuration | Product Surface & Agent Portfolio | Invocation Request、Agent Reference |
| AgentRun / Plan / Step / Branch / Budget | Agent Runtime & Multi-Agent Orchestration | Snapshot、RunOutcome、Control Receipt |
| Runtime Checkpoint | LangGraph Runtime Provider / Infrastructure & Persistence | Resume Control State；不是 Domain Fact |
| CapabilityRequirement / Provider Conformance / Capability Version | Capability / Skill & Tool Runtime | Capability Proposal、Availability、Evaluation Reference |
| PreparedAction / ToolAttempt | Capability / Skill & Tool Runtime | Action Reference、Attempt Result |
| External Effect | External System | External Operation Reference |
| EffectReceipt / Reconciliation | Capability / Skill & Tool Runtime | Receipt、Outcome、Reconciliation Result |
| Model Usage Receipt | Model Gateway | Usage、Cost、Provider Reference |
| Memory Entry / Summary / Preference / Experience | Memory & Context | Context Reference、Memory Receipt |
| Grant / Policy / SecurityEpoch / Authorization Decision | Security & Governance | Authorization Decision、Approval Reference |
| Trace / Decision Trace / Redaction Result | Observability & Evaluation | Trace Reference、Evidence Report |
| Dataset / Evaluation Run / Metric / Release Decision | Observability & Evaluation | Eval Evidence、Release Gate |
| PostgreSQL / Object / Index / Queue / Worker durability primitive | Infrastructure & Persistence | Durable Artifact、Job Outcome、Recovery Primitive |

### Security、Deployment 与验证要求

每个跨边界操作绑定 Tenant、Matter、Scope、Policy Epoch、Idempotency Key 和 Trace。每一次新的受保护访问都必须重新使用当前 Authorization Decision；不可逆 Effect 必须执行时重新授权并经过 Approval；不可信文档不能改变策略。Sandbox 的 Target 边界包括 Filesystem、Network Egress、Secret、Resource Limit、Cleanup 和 Audit。

Developer、Staging、Production 是不同证据等级；Compose、Kubernetes、容器或配置文件存在不等于 Production Ready。验证需要覆盖 No-egress、Allowlist、Secret Leakage、Cross-tenant、Prompt Injection + Tool、Sandbox Escape、Revoked Permission、Stale Credential、Duplicate Side Effect、SBOM、签名 Artifact、质量、效率、恢复和替换成本。

### Implementation、Measurement 与 External Gaps

`Current` 只由代码、测试、Trace、Migration 或真实运行证据证明；`Target` 记录已接受的方向；`Hypothesis` 需要 Benchmark、Spike、Security Evidence 或 User Validation；`Future` 是长期可选；`UNKNOWN` 保留未恢复事实。当前开放 Gap 包括 Court QA、A/B/C、负载、故障注入、HA、备份恢复、Sandbox 资格、Provider 替换和外部许可。

本文不承载工作流状态、实施授权或最终模块/服务数量。总体架构图由 [`architecture-views.md`](architecture-views.md) 提供展示配对；它不拥有第二套架构事实。
