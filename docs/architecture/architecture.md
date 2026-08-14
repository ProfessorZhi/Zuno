# Zuno 总体 Target 架构

updated: 2026-08-13
status: normative-target
architecture_state: ACCEPTED_TARGET_WITH_OPEN_EVIDENCE
canonical_question: Zuno 为什么存在，Target Product、Domain、Capability、Runtime、Service、Data、Security 和 Eval 如何形成可反转的闭环？
owner: Cross-cutting Architecture Owner
acceptance_scope: Target Architecture baseline；实现、测量和外部资格尚未完成
readability_state: READABILITY_BASELINE_REFOUNDED
readability_gate: REQUIRED_BEFORE_NEXT_RED_BLUE_PROTOCOL
document_role: cross-cutting integration source
canonical_taxonomy: docs/architecture/ 仅保存总体架构四文件；Current Facts 由 docs/facts/ 负责
current_state_source: docs/facts/ 和 docs/evidence/
decision_sources: docs/decisions/0008-legal-domain-kernel-and-host-boundary.md、0009-python-only-backend.md、0010-microservice-target-and-service-boundaries.md、0011-architecture-document-taxonomy.md

> 本文先说明问题和产品动机，再说明 Target 责任边界，最后给出 Contract。项目上下文和当前仓库事实由 `docs/facts/` 负责；当前证据由 `docs/evidence/` 负责。本正文不创建第二套事实状态机，也不把 Target 写成 Current。

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

如果 A/B/C Benchmark 不能证明收益，对应自研复杂度就不应保留。

### 2. 历史事实、当前仓库和 Target 不是一条时间线

历史项目来自智慧司法研发背景，曾有内部 Demo、客户侧 Demo、法院侧测试和 Pilot Validation，但尚未正式生产；客户明确反馈过回答质量需要提高。今天仍用于理解产品边界的上下文见 [`../facts/project-background.md`](../facts/project-background.md)，完整历史过程进入 [`../history/`](../history/README.md)。

当前 main 能证明 Python / FastAPI、PostgreSQL Migration、Compose、Agent / Knowledge / Memory / Tool 等代码或配置表面，但不能证明这些组件曾在历史客户环境同时运行，也不能证明用户本人负责全部能力，详见 [`../evidence/README.md`](../evidence/README.md)。

本文以下内容都是 Target 或待测假设，不是历史项目回溯。

### 3. 一个 Target 场景

这是一个用于架构推理和 Benchmark 的 Target Scenario，不是历史确认的法院 SOP：

```text
用户提出复杂法律任务
  → 系统识别 Claim 与 Evidence Requirement
  → Knowledge 根据 Scope、Query Class 和成本选择检索方式
  → Legal Intelligence 生成 Fact / Event / Conflict / Finding Proposal
  → Agent Runtime 组织有限的计划、并行研究和补证据
  → Domain Owner 校验来源、版本、权限和依赖
  → 必要时进入 Human Review
  → 提交新的版本化 Finding / WorkProduct
  → 新证据到来时标记依赖对象 stale，并重新评估
```

这条流程把“找到材料”“理解法律结构”“提交正式业务状态”分开。Knowledge 负责材料与证据候选；Legal Intelligence 负责候选结构；Domain Owner 决定什么可以成为正式业务状态；Runtime 负责执行控制而不是拥有法律事实。

### 4. 五层责任视图，不是五个最终模块

Target 用五层 Architecture Responsibility Layers 解释系统职责，但不把它们冻结成五个模块、五个服务或五个团队：

1. **Legal Work Surface**：案件分析、合同审查、法律研究、Finding、报告和 Human Review；
2. **Legal Domain & Intelligence**：Evidence、Fact / Event、Conflict、Dispute、Legal Issue、Fact–Article、Finding、Version 和 Staleness；
3. **Agentic Knowledge & Context**：Document Ingestion、Hybrid Retrieval、条件 Graph、Citation、Memory 和 Context Assembly；
4. **Agent Runtime & Execution**：Single Controller、Plan DAG、Step、ReAct、Reflection、Replan、受控 Worker、Model、Skill 和 Tool；
5. **Trust & Platform Engineering**：Permission、Approval、Sandbox、Audit、Observability、Eval 和 Infrastructure。

逻辑能力（Logical Capability Architecture）、物理服务与部署（Physical Service / Deployment Architecture）、Worker、Process、Container、Database 和 Team 不做一一映射。上一阶段的 `11 Logical Modules + 1 Architecture` 只是 History / Superseded 文档组织方式；`FINAL_MODULE_COUNT: NOT_DECIDED`。历史材料统一从 [`docs/history/`](../history/README.md) 查阅，当前上下文和仓库状态统一从 [`docs/facts/`](../facts/README.md) 查阅。

### 5. Legal Domain、Knowledge、Intelligence 和 Memory 的边界

这四个概念解决不同问题：

- **Knowledge** 回答“材料在哪里、哪段原文支持什么”，产生 Source、Chunk、EvidenceCandidate、CitationLineage 和 RetrievalReceipt；
- **Legal Intelligence** 回答“材料表达了什么法律结构”，产生 Event、Alignment、Conflict、Fact–Article 或 Finding Proposal；
- **Domain State** 回答“业务世界目前承认什么是真的”，由 Domain Owner 根据版本、来源、权限、依赖和 Review 提交正式状态；
- **Memory** 回答“哪些上下文或经验可以被策略性复用”，可以压缩、过期、删除和按范围召回，但不是 Canonical Legal Fact。

例如，Knowledge 可以找到原告和被告的两份陈述；Legal Intelligence 可以判断它们描述同一事件且存在冲突；Domain Owner 才决定该冲突候选是否进入正式案件状态。Memory 可以帮助下一次任务复用工作上下文，但不能代替 FactVersion 或 FindingVersion。

### 6. WorkBuddy / Dify 的竞争边界

WorkBuddy、Dify 等通用平台应被视为 Generic Agent Host / Workflow Platform：它们可以负责 Conversation、Agent UI、Model Access、一般 Workflow、Knowledge、Skill、Tool、MCP 和通用编排。本文不声称它们缺少这些能力，也不声称闭源或开源天然更安全。

Zuno Target 要验证的是更窄、更高风险的领域纵深：业务状态是否有唯一 Owner，证据是否足够支撑结论，Finding 是否能随依赖变化而 stale，Human Decision 是否可追溯，外部副作用是否可审计。WorkBuddy 可以作为 Zuno Host；如果 `WorkBuddy + Zuno Legal Backend` 已经达到目标质量和恢复边界，就没有理由为了“拥有平台”保留 Native Runtime。

### 7. 四层可验证的 Target Differentiation

**Evidence Depth**：不仅检索相关文本，还要判断证据是否足够、来源和版本是否可追溯。基础是 BM25 / Dense / Hybrid；Graph 和 Agentic Retrieval 只在 Query Class 和 Evidence Requirement 表明值得时启用。

**Legal Intelligence**：模型和 Provider 只能产生 Proposal / Candidate / Observation / Reference / Receipt，不能直接提交 FindingVersion。事件对齐、冲突检测、事实—法条对应和适用性分析都必须可替换、可评测。

**Long-lived Domain State**：法律任务不是一次 Conversation。若 Finding V3 依赖 Evidence A/B/C，新 Evidence D 使依赖冲突，V3 应变为 stale 或 review_required，再产生 Finding V4，而不是继续展示旧结论。

**Enterprise Trust**：谁能看哪些材料、调用什么 Tool、批准什么动作，必须由 Permission、Security Gate、Approval、Sandbox、Effect Receipt、Audit 和 Human Decision 共同约束。安全优势只有在 Source Audit、No-egress、权限、隔离和副作用测试后才可称为 Evidence。

### 8. Runtime 不是业务后端

FastAPI 是 Application / HTTP Interface，负责认证、Matter / Document / Review / Run API 以及状态查询；它不是 Agent Runtime。LangGraph 若被保留，只是 Agent orchestration / durable workflow provider，负责 Run、Plan、Checkpoint、Resume、Interrupt、分支和受控 Replan，不承载普通 CRUD，也不拥有 Canonical Case Fact。

Single Controller 是默认起点。复杂任务可以派生 Ephemeral Worker 或受控 Specialist Agent，但只有当角色拥有独立 Context、Permission、Capability、Lifecycle 或 Resource 时，才有理由称为 Agent。否则它可能只是 Step、Skill 或 Tool。Persistent Multi-Agent Team 不是默认结论。

### 9. 物理服务的理由与代价

Python-only 是 Owner Target Constraint，理由是当前 AI / NLP / PyTorch / LangGraph 生态与团队复杂度；这不是“Python 性能够用”的空泛结论。LLM、Embedding、Vector DB、Graph DB、PostgreSQL、Object Storage 和外部 API 多数是 I/O 或外部服务边界，OCR、Parsing、Embedding、Graph Build 和 Eval 等 CPU / GPU 重任务应进入独立 Worker，不阻塞 FastAPI 请求线程。

Microservice 是部署方向，但服务数量不由用户数量自动决定。只有当 Platform / Domain 的事务工作、Agent Runtime 的长任务、Knowledge 的 CPU / GPU / I/O 工作、Tool / Sandbox 的安全边界或 Eval 的离线批处理确实需要独立扩缩容、故障隔离、安全隔离、部署生命周期或可用性时，才拆物理服务。每个候选都要回答：**Why service? Why not library? Why not worker?**

网络延迟、序列化、Schema version、Partial Failure、Retry Storm、Tracing、Secret Distribution 和本地开发复杂度都是实际代价。默认可以从模块化 Python 服务加独立 Worker 开始；Service Count、Database physical split、Queue technology、Model Gateway 和 Graph Provider 都保持可反转。

### 10. 最危险的失败与恢复

需要优先解决的不是“哪个框架更潮”，而是状态不一致：Domain Commit 已成功但 Runtime Checkpoint 仍停在执行前；Tool 已执行但消息重复投递；新证据使 Fact / Conflict / Finding stale；权限在等待期间被撤销；Provider 返回 unknown outcome。

恢复时先读取 Domain Owner 的最后合法版本，再比较 Runtime Control State、Knowledge Projection、EffectReceipt、Provider Operation ID 和当前权限。只有完成对账，才能选择 Resume、Retry、Replan 或 Human Review。HTTP 200、Queue ACK、Index Write 或 Checkpoint Commit 只能证明各自边界，不代表业务事实已完成。

### 11. A/B/C Kill Test

比较必须控制 Same Base Model、Same Raw Corpus、Same External Tools、Comparable Prompt、Comparable Token Budget 和 Comparable Time Budget：

```text
A — Generic Host + Legal Prompt / Skills
B — Generic Host + Zuno Legal Backend / Legal Capabilities
C — Zuno Native Runtime + First-class Legal Domain State
```

如果 `B > A`，说明 Legal Backend / Legal Capability 可能产生价值；如果 `C ≈ B`，应缩减或外部化 Native Runtime；只有 `C > B` 且收益可归因、可重复时，才支持 Domain-aware Native Runtime；如果 `B ≈ A`，应删除没有产生收益的 Legal Backend 复杂度。

指标必须覆盖 Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict / Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance、Task Completion、Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls 和 Domain State Reuse Rate。不能只比较单一 LLM Judge 分数。

### 12. 取舍与反转条件

这套 Target 付出的成本是版本、证据依赖、跨服务序列化、运行恢复、可观测性、评测和部署复杂度。它只有在复杂法律任务中带来可测量收益时才值得保留：

- Host + Legal Backend 足够：缩减 Native Runtime；
- Hybrid Retrieval 已覆盖关系型任务：Graph 降为条件 Provider；
- Single Agent + 并行工具足够：不升级为 Persistent Multi-Agent；
- Matter DB + Runtime Checkpoint 足够：删除不必要的 Memory 层；
- 模块化服务 + Worker 已满足资源和故障隔离：合并服务；
- MCP / 现有 Sandbox 已满足安全边界：不重复建设 Tool Runtime。

## Target Status Boundary

本节是 Target 设计状态，不是 `docs/facts/` 的 Current 事实。`ACCEPTED_TARGET` 只表示方向已被治理接受；它不表示代码已实现、收益已测量或外部生产资格已获得。

| Target 能力 / 边界 | 状态 | 关闭或反转条件 |
| --- | --- | --- |
| Python-only Backend | `ACCEPTED_TARGET` | Owner 工程约束；不证明历史或生产链路 |
| Microservice Direction | `ACCEPTED_TARGET` | 服务数量和边界仍需扩缩容、故障、安全和生命周期证据 |
| Legal Domain State | `ACCEPTED_TARGET` | 需要复杂法律任务 Benchmark 证明收益 |
| Evidence / Citation Provenance | `ACCEPTED_TARGET` | 需要真实 QA 证明来源和引用闭环 |
| Legal Intelligence Provider Boundary | `ACCEPTED_TARGET` | Provider 输出必须可替换、可评测，不能直接提交 Domain Fact |
| Hybrid Retrieval | `ACCEPTED_TARGET` | 需要 Recall、Citation、Latency 和 Cost 测量 |
| Agentic Retrieval / GraphRAG | `PROPOSED` / `HYPOTHESIS` | 只有 A/B/C 与 Graph Kill Test 证明增益才保留 |
| Memory / Context | `PROPOSED` / `DEFERRED` | 不能成为 Canonical Legal Fact；需要替换和质量证据 |
| Single Controller / Controlled Multi-Agent | `ACCEPTED_TARGET` / `PROPOSED` | 与更简单的单 Agent + 并行工具比较 |
| Tool / MCP / Security / Human Review | `ACCEPTED_TARGET` | 需要授权、审批、幂等、Receipt、对账和真实 Review 证据 |
| Physical Service Count | `MEASUREMENT_BLOCKED` | `FINAL_MODULE_COUNT: NOT_DECIDED`；按 Workload / Failure / Security / Scaling 收敛 |
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

## Part B — Detailed Architecture Specification

### Cross-layer Contract Registry

| Contract | 输入 | 输出 | 唯一 Owner | 失败与验证 |
|---|---|---|---|---|
| Domain Admission | Proposal、Evidence Reference、权限上下文、DomainVersion | Canonical Version、review_required 或 rejected | Domain Owner | CAS 冲突、来源不足；Admission Contract Test |
| Runtime Execution | PlanVersion、Domain Snapshot、Budget、Policy | Step / Branch Result、Checkpoint、RunOutcome | Agent Runtime | Domain Generation 不一致；Recovery Replay |
| Evidence Retrieval | QueryClass、Claim、Scope、DocumentVersion | EvidenceCandidate、CitationLineage、RetrievalReceipt | Knowledge | 索引 stale、ACL 泄漏、引用错 span；Citation / Graph Ablation |
| Legal Capability | Evidence / Fact Candidate、Capability Contract、Provider Policy | Proposal、Observation、Reference 或 Receipt | Legal Intelligence Owner | Provider 不可用、版本不兼容；Provider Replacement Test |
| External Effect | PreparedAction、SecurityEpoch、Approval、Idempotency Key | EffectReceipt、outcome_unknown 或 rejected | Tool / Security Owner | 超时、重复副作用；Fault Injection / Reconciliation |
| Evaluation | DatasetVersion、Variant、预算、Trace | RawResult、Metric、Comparison、ReleaseDecision | Eval Owner | 分母变化、不可比、阻塞；Reproducible Eval |

### Service、通信与队列边界

候选物理角色可以包括 Edge / API、Platform / Domain、Agent Runtime、Knowledge、Tool / Sandbox 和 Eval Worker，但它们不是最终服务清单，也不是 Current。是否拆分必须由独立 Scaling、Failure、Security、Availability、Lifecycle 或 Team Ownership 证据支持。

CRUD、小命令和外部互操作默认使用 HTTP / API；长运行 Agent Run、Ingestion、Embedding、Graph Build、Sandbox 和 Eval 才进入带 JobId、Attempt、Timeout、Cancellation、Retry、Dead Letter 和 Backpressure 的异步队列。高吞吐内部 gRPC 只是候选，不默认所有服务都使用 gRPC，也不默认所有交互都用 Event。

FastAPI 只拥有 Application / HTTP Interface；LangGraph 只拥有 Agent Control State。PostgreSQL 保存 Canonical Business / Domain State；Runtime Checkpoint 保存 Graph Control / Execution State。两者必须分别验证和恢复，不能把 Checkpoint 当成 Case Fact。

### State、Version 与 Recovery Contract

本节先给出跨 Domain、Runtime 和 Memory 的共同恢复原则：版本化业务事实由 Domain Owner
管理；Runtime 只保存执行控制；Memory 只保存可按策略复用的上下文。任何新输入都必须比较
依赖、版本、权限和副作用状态，再决定继续、重试、重规划或人工复核。

### Domain State、Runtime State 与 Memory

Domain State 包括 Matter、DocumentVersion、Evidence、Fact、Event、Conflict、Dispute、Finding、HumanDecision 和 WorkProduct。Runtime State 包括 AgentRun、Plan、Step、Branch、Interrupt、Checkpoint 和 Budget。Memory 包括 Working、Session、Matter Context、Long-term 或 Reflexion Candidate，必须可以按策略过期或删除。

New Evidence 到来时，系统通过 Dependency 发现受影响的 Fact / Conflict / Finding；将旧版本标为 stale 或 review_required，创建新的 bounded evaluation run，并由 Domain Owner / Human Review 提交新版本。不能因为 Memory 召回了旧文本，就把它当作最新业务事实；也不默认采用 Event Sourcing，PostgreSQL 当前事实及版本足够时优先保持简单。

### Owner Registry

| Owner | Canonical State | 允许跨边界输出 |
|---|---|---|
| Domain | Matter、DocumentVersion、Fact、Evidence、Conflict、Finding、HumanDecision、WorkProduct | Proposal、Version、Reference |
| Runtime | AgentRun、Plan、Step、Branch、Checkpoint、Budget | Snapshot、RunOutcome、Control Receipt |
| Knowledge | Source、Parse、Chunk、Index、Retrieval、CitationLineage、Projection | Candidate、Reference、Retrieval Receipt |
| Legal Intelligence | Capability Contract、Provider Resolution、Algorithm Observation | Proposal、Candidate、Observation、Reference、Receipt |
| Security | Principal、Grant、Approval、SecurityEpoch、Policy Decision | Authorization Decision |
| Tool | PreparedAction、ToolAttempt、EffectReceipt、Reconciliation | Receipt、Outcome |
| Eval | DatasetVersion、EvaluationRun、Metric、Comparison、ReleaseDecision | Evidence Report |

### Security、Deployment 与验证要求

每个跨边界操作绑定 Tenant、Matter、Scope、Policy Epoch、Idempotency Key 和 Trace。不可逆 Effect 必须执行时重新授权并经过 Approval；不可信文档不能改变策略。Sandbox 的 Target 边界包括 Filesystem、Network Egress、Secret、Resource Limit、Cleanup 和 Audit。

Developer、Staging、Production 是不同证据等级；Compose、Kubernetes、容器或配置文件存在不等于 Production Ready。验证需要覆盖 No-egress、Allowlist、Secret Leakage、Cross-tenant、Prompt Injection + Tool、Sandbox Escape、Revoked Permission、Stale Credential、Duplicate Side Effect、SBOM、签名 Artifact、质量、效率、恢复和替换成本。

### Implementation、Measurement 与 External Gaps

`Current` 只由代码、测试、Trace、Migration 或真实运行证据证明；`Target` 记录已接受的方向；`Hypothesis` 需要 Benchmark、Spike、Security Evidence 或 User Validation；`Future` 是长期可选；`UNKNOWN` 保留未恢复事实。当前开放 Gap 包括 Court QA、A/B/C、负载、故障注入、HA、备份恢复、Sandbox 资格、Provider 替换和外部许可。

本文不承载工作流状态、实施授权或最终模块/服务数量。总体架构图由 [`architecture-views.md`](architecture-views.md) 提供展示配对；它不拥有第二套架构事实。
