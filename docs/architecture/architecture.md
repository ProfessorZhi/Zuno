# Zuno 总体 Target 架构

Zuno 面向智慧司法场景，尝试把法律材料、专业分析能力和可复核的业务结果组织成一套可以被独立产品或现有 Agent Host 使用的法律智能能力。它不是把更多 Agent 名词堆在普通 RAG 上，而是要解决一个更具体的问题：当任务涉及多份材料、版本变化、人工判断或外部动作时，系统怎样知道依据是什么、结果是否仍然有效，以及现实世界到底发生了什么。

对简单问题，通用 Host 加检索完全可能已经够用；Zuno 只有在复杂法律任务中确实带来可测量收益时，才值得保留额外的领域状态、证据依赖和恢复控制。本文件记录这一 Target 方向，不把设计自动写成当前实现，也不把 Pilot 写成 Production。

本文的 Part A 先用业务场景解释整体架构，面向新加入的工程师和架构 Review；Part B 再给出 Owner、Contract、状态和恢复规则，面向实现、测试和审查。项目背景见 [`docs/project/`](../project/)，当前代码和验证见 [`docs/evidence/`](../evidence/)，Round 02 的质询过程见 [`docs/history/red-blue/`](../history/red-blue/README.md)。History 解释架构如何演进，不能反过来成为 Current 或 Target 的事实源。

<!--
updated: 2026-08-15
status: normative-target
architecture_state: ACCEPTED_TARGET
architecture_revision: ROUND_02_REVISION_IMPLEMENTED
overall_architecture_state: ROUND_02_REVISED_PENDING_FREEZE_REVIEW
target_logical_module_count: 9
final_module_count: NOT_FROZEN
platform_infrastructure: RESPONSIBILITY_LAYER
context_provider: OPTIONAL
module_decomposition_gate: NOT_OPEN
observability_architecture: OTEL_COMPATIBLE
langsmith_role: PREFERRED_AGENT_TRACE_AND_EVAL_PROVIDER
canonical_question: Zuno 如何把法律领域状态、证据、执行控制、安全和可验证交付组合成可恢复且可替换的 Target？
owner: Cross-cutting Architecture Owner
acceptance_scope: Round 02 Main Judgment 的 Canonical Revision；实现、测量和外部资格尚未完成
readability_state: HUMAN_FIRST_PART_A_AND_PART_B
canonical_taxonomy: docs/architecture/ 仅保存总体架构四文件；项目事实由 docs/project/ 负责
current_state_source: docs/project/ 和 docs/evidence/
review_history_source: docs/history/red-blue/
decision_sources: docs/decisions/0003-wave1-cross-module-contract-freeze.md、0005-official-langgraph-postgres-checkpointer.md、0007-reuse-first-provider-boundary.md、0008-legal-domain-kernel-and-host-boundary.md、0012-evidence-gated-physical-service-split.md、0013-round-02-responsibility-taxonomy.md、0014-round-02-cross-boundary-authority-and-recovery.md
-->

## Part A — Architecture Narrative

### 1. Zuno 是什么

Zuno 是一个面向智慧司法和法律专业工作的 Legal AI / Agent 能力平台。它可以以自己的工作台运行，也可以嵌入法院已有系统、WorkBuddy、Dify 或其他 Generic Host。无论入口在哪里，Zuno 真正要验证的不是“能不能调用模型”，而是能不能把材料、专业能力、人工决定和正式工作结果连成一条可解释的链。

一个法律答案如果只存在于聊天窗口里，通常很难回答几个后续问题：它引用了哪一版材料？这段材料是否真的支持结论？新证据出现后，昨天的结果是否还有效？如果系统调用了外部法院系统，现实世界是否已经执行？Zuno 的 Target 因此围绕版本化材料、证据依赖、正式业务状态、人类复核和受控外部动作展开。

这些是需要验证的产品假设，不是已经测量出的差异化优势。若 Generic Host 加 Legal Backend 与更复杂的 Zuno Native Runtime 没有稳定差异，Native Runtime 就应缩小或删除；若普通 Host 加简单能力已经足够，Zuno 也不应为了保留平台而重复建设通用能力。

### 2. 为什么 Generic Host 有时不够，又为什么很多任务其实够用

对于“合同第 8 条规定了什么违约责任”这类问题，最合理的路径可能就是：确认用户能够访问的材料范围，等待文档可以检索，找到原文，生成带引用的回答，检查依据，然后发布。这个任务不需要动态 DAG、多 Agent、长期 Memory 或复杂的自研 Runtime；如果系统强迫它走完整复杂链路，架构本身就在制造成本。

复杂法律分析则不同。多份合同、补充协议、当事人陈述和历史沟通可能同时有效但适用范围不同。系统需要保留材料版本，找到支持某个 Claim 的证据，判断事件或冲突候选，检查法律适用性，必要时请求人工决定，并把结果保存为一个以后可以被新证据影响的 WorkProduct 版本。这里的增量价值仍然是 Target Hypothesis，必须用真实任务和对照实验验证。

所以 Build / Buy 的边界不是“Zuno 什么都自己做”。Generic Host 可以负责界面、会话、普通 Workflow 和简单回答；LangGraph 可以提供 Checkpoint、Interrupt 和 Resume；MCP 可以提供 Tool 接入；OpenViking 或其他 Provider 可以提供上下文能力。Zuno 只应拥有那些与法律业务正确性、版本、证据、正式提交和受控副作用直接相关的 Contract。

### 3. 一个简单问题怎样完成

假设用户问：“请说明合同第 8 条的违约责任，并给出原文依据。”系统可以按下面的自然语言流程工作：

```text
用户问题
  → 确认材料范围和当前权限
  → 确认合同版本已经可以用于回答
  → 找到第 8 条原文及其稳定位置
  → 生成带依据的回答
  → 检查回答确实被原文支持
  → 由实际入口决定发布
```

工程上，这些步骤分别对应 Scope、Authorization、Knowledge Readiness、Retrieval、Citation 和 Answer Eligibility。Simple QA 可以由 Generic Host 完成，也可以由 Zuno 的 Application & Integration 边界组合完成；它不必进入 Zuno Native Agent Runtime。若由外部 Host 最终展示答案，最终的 UI/发布决定仍属于该 Host，Zuno 提供类型化结果、引用和资格证据。

### 4. 一个复杂法律分析怎样完成

更复杂的任务可能同时处理原告、被告、补充协议和证据材料。系统先绑定本次任务声明的材料范围及版本，再确认知识视图是否覆盖这些材料；随后用检索和专业能力提出事件、对齐、冲突和法律适用性候选，形成 Finding Proposal，经过质量检查和必要的人审后，才提交新的 WorkProduct 版本。

```text
多方材料和版本
  → 材料可用性检查
  → 检索证据和引用
  → 专业能力提出事件/冲突/适用性候选
  → 形成 Finding Proposal
  → 质量检查与人工复核
  → 正式业务状态提交
  → 版本化 WorkProduct
```

Event、Conflict、Dispute、LegalIssue、ApplicableLaw 和 SimilarCase 在第一阶段默认是 Proposal、Projection、Derived View 或 Capability Output，而不是自动成为 Canonical Domain Object。只有未来证明某类对象有独立身份、版本、来源、Owner、修改权限、依赖、失效、审核和审计需求，才考虑提升为正式业务对象。

### 5. 为什么外部动作必须单独处理

如果系统只查询资料，超时通常首先意味着“这次调用没有拿到结果”。但如果系统要通过 MCP 或其他接口向外部系统提交审查结果，超时的危险在于：请求可能已经执行，只是 Zuno 没有收到回应。此时直接重试可能造成重复提交、重复通知或其他不可逆副作用。

因此外部动作经过准备、当前授权、必要审批、执行记录和 Effect Receipt。结果未知时先用 Operation ID、幂等键、外部回执或资源状态进行 Reconciliation；无法确认时停下来交给人，而不是把 HTTP 错误当成“现实世界没有发生”。Tool Runtime 拥有外部执行语义，Capability 只负责提出专业能力结果，两者的成功、失败、重试和安全含义不能混在一起。

### 6. 系统里的几类状态为什么要分开

Zuno 需要同时处理几种生命周期完全不同的东西：

- **Domain State**：Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision 和 WorkProduct 等正式业务状态；
- **Runtime Control State**：Run、PlanVersion、Step、Branch、Budget、Interrupt 和 Checkpoint 等执行控制；
- **Knowledge Projection**：解析、索引、Graph Projection、Knowledge View、Generation 和 Readiness 等可重建检索投影；
- **Optional Context**：Working/Session Context 和可选的长期 Memory；
- **External Effect State**：PreparedAction、ToolAttempt、EffectReceipt 和 Reconciliation；
- **Security / Audit Facts**：授权、审批、策略版本和必须持久化的审计事实；
- **Telemetry Projection**：Trace、Metric、Log 和评测视图。

这些状态不能因为都能在一次 Run 中被看到就共享一个 Owner。Checkpoint 能说明执行控制走到了哪里，但不能证明 Domain Commit 已经成功；Memory 能帮助组装上下文，但不能覆盖新版本材料；Telemetry 丢失时，关键审计事实仍必须可重建。把这些边界分开，是 Zuno 面对恢复、撤权、版本变化和结果失效时仍能解释行为的前提。

### 7. 九个逻辑责任域如何合作

Round 02 Main Judgment 接受的 Target Taxonomy 是九个 Logical Responsibility Modules。它们是责任域，不是九个进程、容器、数据库、网络服务或团队：

| 编号 | 责任域 | 主要负责什么 | 明确不负责什么 |
| --- | --- | --- | --- |
| 01 | Application & Integration | 任务进入、Agent 定义/版本、调用组合、Host/法院系统集成、结果发布与失效通知 | 重新计算安全、知识、模型或领域事实；不要求自有 UI |
| 02 | Legal Domain & Work Product | Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct 和正式版本 | 让模型直接提交正式事实；不拥有检索投影或 Runtime Checkpoint |
| 03 | Knowledge & Evidence | 文档处理、Knowledge Generation、Readiness、检索、重排、EvidenceCandidate、CitationLineage | Canonical Finding、历史 WorkProduct 引用权威和最终法律准入 |
| 04 | Agent Runtime & Control | Controller、Plan、Step、Budget、并行、Retry、Replan、Reconcile、Resume 和 Checkpoint 控制 | Canonical Domain Commit、权限批准和外部 Effect 真相 |
| 05 | Capability & Skill | Event Extraction、Conflict Detection、Fact–Article Mapping、Legal Applicability 等专业能力 Contract | Canonical Domain Commit、外部副作用真相 |
| 06 | Tool Runtime & Effects | PreparedAction、Approval Binding、ToolAttempt、幂等、Effect Receipt 和 Reconciliation | 专业能力判断、扩大权限和替代外部系统事实 |
| 07 | Model Gateway | 模型角色、Provider 路由、配额、Usage/Cost Receipt 和允许范围内的 Fallback | 业务状态、授权决定和未经审批的副作用 |
| 08 | Security & Governance | 身份、授权、Security Epoch、审批策略、模型外发、Tool 权限、秘密和生命周期政策 | 业务结果、模型推理和 Runtime 计划 |
| 09 | Observability & Evaluation | OTel-compatible Trace、诊断视图、评测、发布评估输入和质量证据 | Canonical Domain Truth、授权真相、Effect 真相和强制审计持久性 |

另有一个 **Platform / Infrastructure Responsibility Layer**，提供 PostgreSQL、对象存储、队列、Worker、Checkpointer Adapter、CAS、Lease、Fencing、时钟、索引适配器、备份恢复、网络和秘密交付等物理原语。它支撑逻辑责任域，但不拥有 Domain Success、Knowledge Success、Runtime Success、Capability Success 或 Tool Effect Success。

Memory 不再是一级逻辑模块。它是一个 **Optional Context Provider Boundary**：Working/Session Context 可以由 Host 或 Runtime 管理，Long-term Memory 只有在消融和评测证明有收益后才启用，也可以由 OpenViking、Generic Host 或其他 Provider 提供。拥有 Memory Contract 不等于必须维护一个 Memory 模块。

### 8. 任务失败以后怎样恢复

系统先区分三类情况。执行暂时失败、计划和能力假设仍成立时 Retry；计划依赖、权限、能力语义或事实假设失效时创建新的 PlanVersion 并 Replan；外部 Effect 结果未知时先 Reconcile。三者不能都叫“重试”。

正式业务提交还有一个额外条件：如果某个 Step 的完成条件要求 Domain Admission，Runtime 不能只凭自己的 Checkpoint 宣布完成，必须存在 durable AdmissionReceipt，把 Run、Plan、Step、Proposal、Admission 和结果 Domain Version 关联起来。Domain mutation 与这份 Receipt 必须位于同一个 Domain transactional durability boundary；这不要求 PostgreSQL 和 LangGraph Checkpointer 使用 2PC。

例如 Domain Commit 和 AdmissionReceipt 都成功但 Checkpoint 更新失败时，恢复逻辑可以查询匹配 Receipt 并修正 Runtime Control State。如果 Checkpoint 显示 completed 但 Receipt 不存在，系统不能推断正式准入已经发生；如果 Domain 有更高版本但因果关系不匹配，也不能把别的 Run 的结果冒充当前 Step 的结果。

### 9. 安全、审批、人工复核与审计

模型只能提出 Proposal。它不能自己决定权限、批准高风险动作、把候选 Finding 写成正式状态或把一次调用变成不可逆 Effect。Security & Governance 决定当前 Authorization、Approval Policy、Model Egress、Tool Permission、Audit Requirement 和 Effective Lifecycle Policy；各 Store 负责在自己的边界执行这些决定。

长任务开始时获得的权限不是整个 Run 生命周期的永久通行证。每次新的文档读取、检索、秘密读取、模型外发、Tool Call、外部 Effect 和正式提交都要依据当前 Policy。撤权至少阻止后续新的越权访问；已经载入内存的数据在撤权后是否允许继续 CPU-only 处理，留给更细的 Security 规则冻结。

Retention 不等于 Recall Eligibility。Memory 或其他副本被删除后，未来不得继续召回；仍保留的历史副本是否可以保留、是否受 Legal Hold 或审计要求约束，由有效生命周期政策决定。

高风险动作的关键链应能回答“做了什么、为什么允许、谁批准、现实世界发生了什么”。它依赖 PreparedAction/ToolAttempt、Authorization Decision、Approval Decision、Audit Persistence Receipt、EffectReceipt、必要时的 ReconciliationReceipt 和 AdmissionReceipt。LangSmith、OpenTelemetry 等只是诊断、评测和可视化投影，不能替代缺失的 durable fact。

### 10. Build / Buy / Reuse

Zuno 的默认策略是先复用，再证明必须自有。Python-only 是当前后端的 Target 约束，但不等于预先冻结服务数量；FastAPI 可以作为 Application / HTTP Interface，Generic Host、LangGraph、MCP、模型 Provider、OpenViking、Vector/Graph Store 和基础存储都可以作为 Provider 或 Platform 原语。Zuno 自己要保护的是法律 Domain Contract、Evidence Semantics、历史引用绑定、正式 Admission、生命周期政策和高风险 Effect 的可对账边界。

Physical Service / Deployment 也不提前承诺 Microservice。默认从 Modular Python Backend 加必要的 Independent Worker 开始；只有出现可重复的独立扩缩容、故障隔离、安全/秘密隔离、可用性、独立部署生命周期、稳定跨主机 Contract 或独立数据/运营 Owner 证据时，才拆成独立 Network Service。每次拆分都必须回答：Why service? Why not library? Why not worker?

### 11. 当前还没有证明什么

这次 Revision 只把 Round 02 的 Target Decisions 写回 Canonical Architecture，不改变实现状态。以下仍然需要证据：

- Native Runtime 是否比 Generic Host + Legal Backend 有额外收益；
- Long-term Memory 是否对法律任务有稳定收益；
- Specialist / Multi-Agent 是否优于 Single Controller + 并行工具；
- GraphRAG 是否在特定 Query Class 上带来足够收益；
- Legal Backend 的 Domain State 和 Evidence Binding 是否比简单 Host 方案更有价值；
- 安全、恢复、评测和外部部署是否达到 Production 资格。

当前模块分解闸门仍关闭，详细 `docs/modules/*.md` 尚未建立。总体架构已完成 Round 02 Revision，但仍等待 Main Architecture Freeze Review；这不是 Production Ready，也不是 Module Freeze。

## Target Status Boundary

以下表格是当前架构状态；它只说明本文件的 Target 治理状态，不证明实现或生产资格。

| 项目 | 当前状态 |
| --- | --- |
| Canonical Revision | `ROUND_02_REVISION_IMPLEMENTED` |
| Overall Architecture | `ROUND_02_REVISED_PENDING_FREEZE_REVIEW` |
| Logical Responsibility | 9 个 Target Logical Modules |
| Platform / Infrastructure | Responsibility Layer，不是第 10 个逻辑业务模块 |
| Context Provider | Optional，不是一级逻辑模块 |
| Native Runtime | Conditional / Measurement-gated |
| Long-term Memory | Optional / Measurement-gated |
| GraphRAG | Query-class / Evidence-gated |
| Production Readiness | Not established |
| Module Decomposition Gate | Not open |

## Part B — Detailed Architecture Specification

Part B 是 Part A 的工程参考。它不把设计写成当前实现，也不增加 Part A 没有解释过的重大决策。

### B1 Scope and Global Invariants

1. Logical Responsibility 不等于 Process、Container、Database、Worker、Network Service 或 Team。
2. Domain State、Runtime Control State、Knowledge Projection、Optional Context、External Effect State、Security/Audit Fact 和 Telemetry Projection 拥有不同 Owner。
3. Model、Capability、Retrieval、Memory 和 Runtime 只能产生 Proposal、Candidate、Observation、Reference 或 Receipt，不能直接提交 Canonical Domain State。
4. Simple QA 可以由 Generic Host 完成，不强制进入 Zuno Native Agent Runtime。
5. `Retry != Replan != Reconcile`；外部结果未知时禁止 Blind Retry。
6. Formal Admission 的完成必须有 AdmissionReceipt；Checkpoint 不能单独证明 Domain Commit。
7. Current 只能由代码、测试、Migration、Trace 或真实运行证据证明；本文件其余架构均为 Target 或 Hypothesis。
8. Network Service Split 必须由证据门控；默认物理起点是 Modular Python Backend + Independent Workers where justified。

### B2 Responsibility / Ownership Map

| Fact / State | Authoritative Owner | 允许其他边界消费的形式 |
| --- | --- | --- |
| Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct | Legal Domain & Work Product | Snapshot、Reference、Admission Input |
| KnowledgeGeneration、KnowledgeView、Readiness | Knowledge & Evidence | Readiness Decision、EvidenceCandidate |
| CitationLineage | Knowledge & Evidence | Retrieval/Citation Reference |
| Historical WorkProduct Citation Binding | Legal Domain & Work Product | Immutable source binding |
| AgentRun、PlanVersion、Step、Branch、Budget、Checkpoint | Agent Runtime & Control / Runtime Provider | Control State、RunOutcome |
| CapabilityRequirement、CapabilityVersion、ProviderConformance | Capability & Skill | Proposal、Observation、Evaluation Reference |
| PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt | Tool Runtime & Effects | Effect Outcome、Control Decision |
| Model Usage / Cost Receipt | Model Gateway | Usage、Cost、Provider Reference |
| Authorization、SecurityEpoch、Approval、Lifecycle Policy | Security & Governance | AuthorizationDecision、ApprovalDecision、Policy Reference |
| Durable Audit Persistence Fact | Its persistence boundary under Security requirement | AuditPersistenceReceipt |
| Trace、Metric、Eval、Release Evaluation | Observability & Evaluation | Diagnostic View、Evaluation Evidence |
| Physical durability primitive | Platform / Infrastructure | Storage/Queue/Worker Receipt |

### B3 Cross-boundary Contracts

以下是本层真正跨责任边界的 Contract。字段级数据库设计、ORM 类和 Migration 不在本次 Revision 中冻结。

#### InvocationDecision

- Purpose：判断请求现在是否允许执行，并组合其他边界已经做出的决定。
- Producer：Application & Integration。
- Consumer：Host、Runtime 或直接回答路径。
- Authoritative Owner：Application & Integration；它消费而不重算 Security、Knowledge、Capability 或 Model Fact。
- Input / Output：请求、Scope、AuthorizationDecision、ReadinessDecision、Capability/Model Eligibility、适用时的 Runtime Control Decision → InvocationDecision。
- Versioning：绑定请求、策略和相关版本引用。
- Validation：Scope、权限、材料可用性和 Provider Eligibility 必须可追溯。
- Failure Semantics：拒绝、等待、需人工处理或允许执行。
- Idempotency / Replay：同一请求身份不得重复创建未绑定的 Invocation。
- Security Requirements：使用当前 Authorization 和 Policy Epoch。
- Persistence Requirement：保存足以解释组合决定的引用或 Receipt。
- Observability Requirement：记录决定来源，不把组合决定伪装成底层事实。
- Evidence：Integration、Authorization 和 Readiness Tests。

#### AnswerPublicationDecision

- Purpose：判断普通答案是否可以发布。
- Producer / Consumer：Zuno Application & Integration 或外部 Generic Host。
- Authoritative Owner：Zuno 发布时由 Application & Integration 拥有；外部 Host 发布时由 Host 拥有最终 UI/发布权。
- Input / Output：Typed Result、Citation、Eligibility Evidence、Policy References → Publication Decision。
- Versioning：绑定结果版本和引用版本。
- Validation：引用、资格、权限和发布策略可检查。
- Failure Semantics：Draft、Review Required、Reject 或不发布。
- Idempotency / Replay：发布 Delivery 使用独立的 delivery identity。
- Security Requirements：遵守当前发布权限和脱敏策略。
- Persistence Requirement：至少保存发布决定及必要 Delivery Fact。
- Observability Requirement：区分 Zuno 决定和外部 Consumer 展示。
- Evidence：Publication and Host Integration Tests。

#### WorkProductCitationBinding

- Purpose：保存正式 WorkProductVersion 当时实际引用的不可变材料位置。
- Producer：Legal Domain & Work Product，在 Admission 时建立。
- Consumer：Review、Audit、Delivery、后续失效分析。
- Authoritative Owner：Legal Domain & Work Product。
- Input / Output：DocumentVersion、immutable source reference/hash、stable location/span、source representation identity/hash、必要 excerpt/evidence hash、可选 CitationLineage → durable binding。
- Versioning：绑定 WorkProductVersion，不被新 Index 覆盖。
- Validation：源版本和位置可回到原始表示；Chunk ID、Vector ID、Graph Node ID 不能单独作为唯一权威。
- Failure Semantics：无法稳定绑定时不得 Formal Admit。
- Idempotency / Replay：同一 WorkProductVersion 的绑定写入幂等。
- Security Requirements：遵守材料访问和脱敏策略。
- Persistence Requirement：位于 Domain durable boundary。
- Observability Requirement：只记录引用身份，不把敏感全文写入普通 Trace。
- Evidence：Citation Binding and Source Replacement Tests。

#### EffectiveLifecycleDecision

- Purpose：决定 Retention、Deletion、Legal Hold 和 Compliance Exception 的有效政策。
- Producer：Security & Governance。
- Consumer：Domain、Memory/Context Provider、Audit、Observability、Platform Stores。
- Authoritative Owner：Security & Governance；各 Store 是 Enforcement Owner。
- Input / Output：主体、数据分类、Retention、Legal Hold、Deletion Policy → 当前生命周期决定。
- Versioning：绑定 Policy Epoch。
- Validation：删除不得解除有效 Legal Hold；未来 Recall 资格必须重新检查。
- Failure Semantics：政策不明时 fail closed 或进入 Review。
- Idempotency / Replay：重复执行删除/保留决定必须可识别。
- Security Requirements：不得由 Memory Provider 自行放宽。
- Persistence Requirement：政策和关键执行 Receipt 必须可审计。
- Observability Requirement：记录策略引用，避免导出秘密和全文。
- Evidence：Retention、Deletion、Legal Hold、Recall Eligibility Tests。

#### AdmissionReceipt

- Purpose：证明 `Step → Proposal → Formal Admission → resulting Domain Version` 的因果链。
- Producer：Legal Domain & Work Product 的 Domain Admission 边界。
- Consumer：Agent Runtime & Control、Recovery、Audit、Review。
- Authoritative Owner：Legal Domain & Work Product。
- Input / Output：Run identity、PlanVersion、StepRun identity、Proposal/Admission identity、Idempotency identity、expected prior Domain Version → resulting Domain Version Receipt。
- Versioning：每次 Admission 绑定唯一结果版本和预期前置版本。
- Validation：Domain mutation 与 Receipt 必须在同一 Domain transactional durability boundary。
- Failure Semantics：没有匹配 Receipt 时，Runtime 不能宣布要求 Formal Admission 的 Step 完成。
- Idempotency / Replay：使用 Admission identity 和 Idempotency identity 去重。
- Security Requirements：Admission 必须消费当前 Authorization、Approval 和 Human Decision。
- Persistence Requirement：不得只写入 Runtime Checkpoint。
- Observability Requirement：可由 Trace 引用，但不以 Trace 代替 Receipt。
- Evidence：Admission Causation and Recovery Tests。

#### WorkProductInvalidationFact / InvalidationDeliveryFact / ConsumerAcknowledgementObservation

- Purpose：分别表达 Domain 失效、通知交付和 Consumer 是否被观察到确认。
- Producer / Owner：Domain Invalidation Truth 由 Legal Domain & Work Product 拥有；Delivery Fact 和 Acknowledgement Observation 由 Application & Integration 拥有。
- Consumer：Host、法院系统、Review、Current-validity Query。
- Input / Output：新 Evidence/依赖变化 → `STALE`；通知尝试 → `PENDING/SENT/FAILED/RETRYING`；Consumer 返回 → `ACKNOWLEDGED/NO_ACK/UNKNOWN`。
- Versioning：每个 WorkProductVersion 和 Delivery identity 独立版本化。
- Validation：不能用一个 `WorkProduct.status` 代替三类事实。
- Failure Semantics：Domain 已失效不等待 Consumer 在线；Delivery 失败可重试；Ack 未知不能声称远端已知。
- Idempotency / Replay：Delivery 使用幂等标识；支持 push invalidation 和 pull current-validity query。
- Security Requirements：遵守当前 Consumer 权限和数据范围。
- Persistence Requirement：Domain 失效与 Delivery/Ack 各自持久化。
- Observability Requirement：区分 Domain Truth、Delivery Fact 和 Observation。
- Evidence：Invalidation, Delivery and Ack Fault Tests。

#### AuthorizationDecision / ApprovalDecision

- Purpose：分别说明当前访问是否获准，以及高风险动作是否需要并已获得批准。
- Producer / Owner：Security & Governance。
- Consumer：Application、Knowledge、Runtime、Model Gateway、Tool Runtime、Domain Admission。
- Input / Output：Principal、Scope、Policy Epoch、Action Risk → authorization/approval decision。
- Versioning：绑定当前 Security Epoch 和请求身份。
- Validation：每次新的受保护访问重新检查；Resume/Retry/Replan 不沿用失效决定。
- Failure Semantics：Deny、Pause、Review 或不可继续。
- Idempotency / Replay：决定引用稳定的 authorization identity。
- Security Requirements：秘密和策略不得进入普通 Prompt/Trace。
- Persistence Requirement：高风险动作的决定和必要 Audit Persistence Receipt 必须耐久化。
- Observability Requirement：只记录可审计引用和脱敏原因。
- Evidence：Revoked Permission、Model Egress、Tool Permission Tests。

#### PreparedAction / ToolAttempt / EffectReceipt / ReconciliationReceipt

- Purpose：在执行前绑定动作，在执行中记录尝试，在执行后记录现实结果，未知时记录对账。
- Producer：Tool Runtime & Effects；Consumer：Runtime、Application、Domain、Audit。
- Authoritative Owner：Tool Runtime 拥有 Tool Effect Semantics；External System 拥有现实世界最终事实。
- Input / Output：Tool Definition、参数、Authorization、Approval、Idempotency → Attempt → Receipt / Unknown → Reconciliation。
- Versioning：绑定 action identity、action hash、run/step causation 和 idempotency identity。
- Validation：调用前校验 Schema、语义、权限和能力版本；Unknown 不等于 Failed。
- Failure Semantics：瞬时执行失败可 Retry；Outcome Unknown 必须 Reconcile；无安全路径则 Human Review。
- Idempotency / Replay：外部副作用必须有幂等或对账路径。
- Security Requirements：执行时重新授权；敏感参数不进入普通日志。
- Persistence Requirement：Attempt、Receipt 和必要对账事实必须耐久化。
- Observability Requirement：Telemetry 只能引用这些事实。
- Evidence：Duplicate Effect、Timeout、Provider Drift、Reconciliation Tests。

#### AuditPersistenceReceipt

- Purpose：证明要求必须耐久化的 Audit Fact 已落盘。
- Producer：对应持久化边界；Consumer：Security、Observability、Tool、Domain。
- Authoritative Owner：执行该耐久化边界；Audit Requirement 的策略 Owner 仍是 Security。
- Input / Output：Audit Requirement、source event、policy reference → committed/failed Receipt。
- Versioning：绑定 source event 和 requirement version。
- Validation：`MANDATORY_BEFORE_EFFECT` 在高风险动作前必须取得 committed Receipt。
- Failure Semantics：要求耐久化但写入失败时阻止或按政策降级，不用 Telemetry 补齐。
- Idempotency / Replay：source event identity 去重。
- Security Requirements：脱敏、最小化、Secret NEVER EXPORT。
- Persistence Requirement：Receipt 本身位于 durable boundary。
- Observability Requirement：可被 Trace 引用但不能被 Trace 替代。
- Evidence：Audit durability and loss tests。

### B4 Domain / Control Objects

第一阶段 Canonical Legal Domain Kernel 仅包括：Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct。Event、Conflict、Dispute、LegalIssue、StatuteVersion、LegalElement、ApplicableLaw 和 SimilarCase 默认是 Typed Proposal、Projection、Derived View 或 Capability Output。

Runtime Control Objects 包括 AgentRun、PlanVersion、StepRun、Branch、Budget、Dispatch/Join、Interrupt、Checkpoint 和 RunOutcome。Knowledge Objects 包括 KnowledgeGeneration、KnowledgeView、Readiness、EvidenceCandidate、CitationLineage 和 RetrievalReceipt。Memory Entry、Summary、Preference 和 Experience 只属于 Optional Context Provider，不得冒充 Domain Object。

### B5 State Machines

#### Formal Admission

```text
Proposal
  → EligibilityCheck
  → HumanDecision when required
  → Domain Admission
  → AdmissionReceipt
  → Canonical Domain Version
```

#### Knowledge Readiness

```text
UPLOADED → PROCESSING → READY
                    ↘ PARTIAL / STALE / MISSING_REQUIRED_SOURCE / VERSION_MISMATCH
```

声明 Scope 未达到任务最低要求时，默认等待或拒绝 Formal Run。允许 Partial Run 时必须缩小 Scope，不能生成完整 Scope 的正式结果。

#### External Effect

```text
PreparedAction
  → AUTHORIZED / APPROVAL_REQUIRED
  → ToolAttempt
  → SUCCEEDED / FAILED / OUTCOME_UNKNOWN
  → Reconciliation
  → CONFIRMED / NOT_EXECUTED / MANUAL_RECONCILIATION
```

### B6 Retry / Replan / Reconcile

| 控制 | 允许条件 | 结果 |
| --- | --- | --- |
| Retry | 执行失败，但计划、能力假设、依赖和安全条件仍成立 | 重试同一 Step/Attempt，保留预算和幂等身份 |
| Replan | 计划结构、依赖、能力、权限或事实假设失效 | 创建新的 immutable PlanVersion；通过 Replan Barrier |
| Reconcile | 外部 Effect 结果未知 | 查询 Operation ID、幂等键、Receipt 或外部事实；禁止盲重试 |
| Recovery | Domain Commit 与 Runtime Checkpoint 不一致 | 读取 Domain Owner 的耐久事实和 Receipt，再修复 Control State |
| Staleness | 新 Evidence 影响依赖 | 标记 stale/review_required，执行 bounded reevaluation |

### B7 Failure Semantics

Provider 降级不等于结果仍然有正式资格。Answer Policy 和 Domain Admission 必须重新检查 Evidence Sufficiency、Quality Requirement、Security Requirement 和 Human Review Requirement。结果可以成为正常 Canonical Version，也可以只能进入 `review_required`、非 Canonical Draft 或 `rejected/abstain`。

Tool/Capability Schema 或语义发生变化时，Agent 不得猜新参数；先做 Capability Re-resolution，必要时 Replan。Memory Provider 不可用可以在不依赖长期 Memory 的任务中降级；关键证据、权限、Effect 对账或最低质量要求不满足时必须停止或交人。

### B8 Security / Approval / Audit

每个跨边界操作绑定 Tenant、Matter、Scope、Policy Epoch、Idempotency Key 和 Trace Reference。Security & Governance 是 Authorization、Approval、Model Egress、Tool Permission、Secret/Credential 和 Effective Lifecycle Policy 的唯一政策 Owner；各 Store 只执行政策，不得自行扩大权限。

Audit Requirement 决定哪些事实必须在动作前耐久化。Telemetry 与 Durable Audit 分离；OpenTelemetry、LangSmith、日志和指标丢失不能使关键 Domain、Approval、Effect、Admission 或 Audit Fact 消失。Secret Material 不得写入 Prompt、Checkpoint、普通 Trace、普通 Audit Payload 或普通数据库列。

### B9 Recovery and Idempotency

关键恢复顺序是：读取 Domain 的最后合法版本 → 检查 AdmissionReceipt/EffectReceipt/Authorization/Audit facts → 对账 Runtime Checkpoint 和 Knowledge Projection → 决定 Resume、Retry、Replan 或 Human Review。

Admission Recovery 的三个规范场景：

- Domain Commit 和 AdmissionReceipt 成功、Checkpoint 失败：查询匹配 Receipt，修复 Runtime Control State；
- Checkpoint 显示完成、AdmissionReceipt 缺失：不能宣称 Formal Admission 成功；
- Domain 存在更高版本但因果关系不匹配：不能把其他 Run/Step 的结果冒充当前结果。

### B10 Persistence Boundaries

PostgreSQL 或其他 Domain Store 保存 Canonical Business/Domain State 及 AdmissionReceipt；Runtime Provider 的 Checkpointer 保存 Graph Control/Execution State；Knowledge Store 保存可重建的 View/Index/Generation；Context Provider 保存按政策可复用的上下文；Tool Runtime 保存 Attempt/Effect/Reconciliation；Observability 保存 Projection 和 Eval Artifact；Platform Layer 提供耐久性原语。

Domain mutation 与 AdmissionReceipt 必须在同一 Domain transactional durability boundary。不得把 PostgreSQL 与 LangGraph Checkpointer 的 2PC 作为默认方案，也不得把 Queue ACK、Index Write、HTTP 2xx 或 Checkpoint Commit 当成 Domain Success。

### B11 Observability / Evaluation

跨层使用 OTel-compatible Telemetry Contract，贯通 request_id、task_id、run_id、plan_version、step_run_id、tool/action identity、knowledge_generation、domain_version 和 security_epoch。Observability & Evaluation 负责 Trace Projection、Decision Trace、指标、数据集、实验和 Release Evaluation Input；它不拥有 Domain Truth、Security Authorization Truth、Tool Effect Truth 或 Mandatory Audit Durability。

评测至少比较：Generic Host + Legal Skills、Generic Host + Zuno Legal Backend、Zuno Native Runtime + First-class Domain State。指标覆盖 Citation Correctness、Evidence Sufficiency、Unsupported Claim Rate、Reviewer Acceptance、Applicability Accuracy、Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls 和 Domain State Reuse Rate。Offline Release Eval 不等于单次任务的正式资格。

### B12 Current / Target / Gap

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 9-module Target Responsibility Taxonomy | Target, revision implemented | 仍等待 Main Architecture Freeze Review；不等于模块正文已经建立 |
| Legal Domain Kernel | Accepted Target | 只冻结七个第一阶段 Kernel 对象 |
| Simple QA outside Native Runtime | Accepted Target | 具体 Host Integration 仍需验证 |
| AdmissionReceipt | Accepted Target | 仅冻结语义，不是 DB 实现 |
| Historical Citation Binding | Accepted Target | 必须独立于 Index identity |
| Effective Lifecycle Policy | Accepted Target | 删除/保留和 Recall Eligibility 分开 |
| Native Runtime | Conditional / Measurement-gated | 未证明优于 Generic Host + Legal Backend |
| Long-term Memory | Optional / Measurement-gated | 可由 Provider 提供，也可删除 |
| Specialist / Multi-Agent | Optional / Measurement-gated | 默认 Single Controller |
| GraphRAG | Query-class / Evidence-gated | 不默认启用 |
| Production Readiness | Not established | 需独立运行、安全、HA、Eval 和外部资格证据 |

### B13 Evidence / Verification

在实现前后需要保留可复现证据：Simple QA Host Integration Spike、Simple RAG vs Legal Backend、A/B/C Runtime Kill Test、Graph/Memory Ablation、Partial Knowledge Fault Test、Dynamic Permission Fault Test、Admission Recovery Fault Test、Tool Reconciliation Fault Test、Invalidation Delivery Fault Test 和 Service Split Evidence。

Architecture Revision 本身不是这些实验的结果。当前仓库中存在的类、Provider、配置或测试只能在 `docs/evidence/` 以相应证据说明，不得因为本文件新增了 Contract 就把 Current 状态升级。

### B14 Code / Database / Migration Constraints

本次 Revision 不实现 AdmissionReceipt、Lifecycle Engine、Invalidation Outbox、Tool Runtime、Migration、SQLAlchemy Model、Kafka、Kubernetes、Event Sourcing、2PC 或新的 API。本文件不冻结字段、表、ORM、服务数量或最终部署拓扑。

实现任务必须先读取 Part A、Part B、相关 ADR、Evidence 和 Governance，并单独经过实现授权、测试和审查。`docs/modules/` 仍只有 README；模块正文要等 Main Architecture Freeze Review 明确打开 Module Decomposition Gate 后再建立。

## Architecture Freeze Boundary

本次状态是 `ROUND_02_REVISED_PENDING_FREEZE_REVIEW`。Canonical Revision 已完成，但不能在本任务中宣布 `OVERALL_ARCHITECTURE_FROZEN`，也不能打开 `MODULE_DECOMPOSITION_GATE`。后续 Main Review 应确认本文件忠实实现 Round 02 Main Judgment，再决定是否冻结总体架构和开始模块设计。
