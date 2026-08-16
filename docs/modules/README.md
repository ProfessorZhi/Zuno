# Zuno 模块架构

总体架构已经冻结九个逻辑责任域。九篇模块文档均保留 Human-first Part A、B1–B14 Engineering Reference 和 Part C Cross-Module Consistency；在 Deep Design V2 的基础上，**九个模块现在全部进入 Detail Design Candidate V1**。每篇 B14 下都继续细化 B14.1–B14.8，把字段语义、版本与新鲜度 Guard、幂等 namespace、事务 / 持久化边界、Crash Window、Schema Evolution 和 Failure Injection 推到冻结前可盘问粒度。

这仍然不是 Module Detail Freeze（模块细节冻结），也不是 Implementation Authorization（实现授权）。Candidate 的含义是“已经形成可逐字段、逐故障窗口审查的 Target 候选”，不是 ORM、最终 enum、数据库表、Migration、API、物理服务或生产资格已经冻结。

```text
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

## 九个模块与 Detail Design Candidate 重点

| 编号 | 模块 | 首先回答的问题 | Detail Design Candidate V1 重点 | 文档 |
| --- | --- | --- | --- | --- |
| 01 | Application & Integration（应用与集成） | 请求怎样进入，结果由谁发布、交付和失效通知？ | Request / Scope / Invocation / AgentVersion / Publication / Delivery / Outbox / Host Contract | [01](01-application-integration.md) |
| 02 | Legal Domain & Work Product（法律领域与工作成果） | 什么才是正式、长期、可审计的法律业务事实？ | Admission / Receipt / Canonical Object Version / Dependency / PostgreSQL / Invalidation | [02](02-legal-domain-work-product.md) |
| 03 | Knowledge & Evidence（知识与证据） | 哪一版材料现在真的可用于这次任务？ | Generation / ProcessingSpec / Manifest / Serving / Readiness / Retrieval / Worker / Cache | [03](03-knowledge-evidence.md) |
| 04 | Agent Runtime & Control（智能体运行与控制） | 多步任务怎样计划、并行、暂停、重规划和恢复？ | AgentRun / PlanVersion / StepRun / Ready Guard / Replan Barrier / Checkpoint / Takeover | [04](04-agent-runtime-control.md) |
| 05 | Capability & Skill（专业能力与技能） | 专业算法怎样成为版本化、可替换、可评测能力？ | CapabilityVersion / ProviderBinding / Conformance / Eligibility / Invocation / Fallback | [05](05-capability-skill.md) |
| 06 | Tool Runtime & Effects（工具运行与外部效果） | 现实动作怎样准备、确认、去重和对账？ | PreparedAction / Attempt / EffectReceipt / Reconciliation / RetrySafety / Send Boundary | [06](06-tool-runtime-effects.md) |
| 07 | Model Gateway（模型网关） | 模型怎样按角色、安全、预算和资格统一调用？ | Request / Routing / Attempt / Qualification / Usage / Cost / Cancellation / Fallback | [07](07-model-gateway.md) |
| 08 | Security & Governance（安全与治理） | 长任务中谁现在仍被允许做什么？ | Authorization / Approval / SecurityEpoch / Secret Lease / Audit / Lifecycle Enforcement | [08](08-security-governance.md) |
| 09 | Observability & Evaluation（可观测性与评测） | 系统发生了什么，复杂度是否值得保留？ | TelemetryEnvelope / Redaction / Sampling / Dataset / EvalRun / Release Evidence / Kill Test | [09](09-observability-evaluation.md) |

**9/9 Detail Design Candidate 只表示 Target Design 达到冻结前审查粒度。Current、实现、质量和生产资格仍必须回 `docs/evidence/`。**

## 先从三条真实任务主线理解九个模块

九个模块不是固定流水线。任务越简单，路径越短；只有长期状态、风险、恢复或现实副作用需要时，才引入相应责任域。

### 主线一：简单法律问答

```text
01 Request / Scope
→ 08 current Authorization
→ 03 task-level Readiness + Retrieval
→ 07 controlled Model call
→ 01 AnswerPublicationDecision
```

这条路径不默认需要 Native Runtime、Dynamic DAG、Multi-Agent、Long-term Memory 或 GraphRAG。只要通用 Host 遵守同一安全、知识和发布边界，也可以承担入口 / 会话 / UI。

### 主线二：复杂法律分析

```text
01 Request / Scope
→ 08 Authorization
→ 03 Readiness / EvidenceCandidate
→ 04 Plan / Step / Parallel / Join
↔ 05 Capability
↔ 07 Model roles
→ 02 Finding Proposal / HumanDecision / Formal Admission
→ AdmissionReceipt + WorkProductVersion
→ 01 Publication / Delivery
```

04 负责“怎样继续执行”，05 负责“怎样完成专业语义”，02 负责“什么最终成为正式业务事实”。

### 主线三：带现实副作用的任务

```text
04 / 05 Action Proposal
→ 06 PreparedAction
→ 08 Authorization / Approval / AuditRequirement
→ 06 ToolAttempt
→ EffectReceipt
→ OUTCOME_UNKNOWN 时 Reconciliation
→ 02 必要时 Formal Admission
→ 01 Delivery / Notification
```

现实结果未知时禁止 Blind Retry。

## 九模块最重要的事实所有权

| 事实 / 决定 | 权威责任域 | 其他模块最多做什么 |
| --- | --- | --- |
| Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct | 02 | 读取引用、提出候选 |
| Formal Admission、AdmissionReceipt、WorkProductCitationBinding、Domain invalidation | 02 | 04 用 Receipt 恢复；01 发布 / 交付 |
| KnowledgeGeneration、ReadinessDecision、EvidenceCandidate、CitationLineage | 03 | 02 可正式接纳候选 |
| AgentRun、PlanVersion、StepRun、Branch / Join、Budget、Checkpoint、RunOutcome | 04 | 其他模块提供 facts / receipts |
| CapabilityVersion、Conformance、Eligibility、专业 Proposal | 05 | 04 调度；02 决定正式准入 |
| PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt | 06 | 08 决定是否允许；远端拥有内部真相 |
| ModelRole、RoutingDecision、ModelCallAttempt、Quota、Usage / Cost | 07 | 09 评测；08 决定外发 / Credential policy |
| AuthorizationDecision、SecurityEpoch、ApprovalDecision、LifecycleDecision、AuditRequirement | 08 | 执行模块记录自己的 execution fact |
| Trace、Metric、Eval Dataset / Run / Result、Experiment、ReleaseEvidence | 09 | 只测量 / 投影，不接管业务 truth |
| External Request、InvocationDecision、Publication、Delivery、InvalidationDelivery、Ack Observation | 01 | 外部 Host 拥有其最终 UI / adoption truth |

## 绝对不能再次混淆的边界

```text
EvidenceCandidate != Evidence
CitationLineage != WorkProductCitationBinding
KnowledgeGeneration lifecycle != task-level ReadinessDecision

Checkpoint completed != Domain committed
Formal Admission-required Step 必须有 matching AdmissionReceipt

Capability Proposal != PreparedAction != ToolAttempt != EffectReceipt

AuthorizationDecision != ApprovalDecision != HumanDecision

WorkProduct invalidated → 02
Invalidation delivered  → 01
Consumer acknowledged   → 01 observation

Telemetry / Trace != Durable Audit != Business Truth

Provider / index write success
!= owner-level completion proof

Cancel requested
!= external operation cancelled
!= Domain fact rolled back

Late result arrived
!= late result still eligible for current Plan / Domain

Same correlation id
!= same idempotency namespace
```

## 跨模块因果主干

不同责任域不共享一张“万能状态表”。一次任务通过稳定 identity / refs 串联：

```text
ExternalRequestIdentity / InvocationIdentity
→ AgentDefinitionVersion
→ [RunId → PlanVersion → StepRun / Branch]
→ KnowledgeGeneration / ReadinessDecision / EvidenceCandidate
→ CapabilityVersion / CapabilityInvocation
→ ModelRoutingDecision / ModelCallAttempt
→ PreparedAction / ToolAttempt / EffectReceipt
→ AuthorizationDecision / ApprovalDecision / SecurityEpoch
→ DomainVersion / AdmissionReceipt / WorkProductVersion
→ PublicationIdentity / DeliveryIdentity
→ Telemetry / Eval correlation refs
```

箭头只表示可追溯关联，不意味着每个任务必须经过全部节点，也不表示对象应放进同一数据库。

## 每个模块都必须明确“什么才算完成”

| 模块 | 本模块权威完成证明 | 明确不是完成证明 |
| --- | --- | --- |
| 01 | Publication / Delivery durable fact | Run complete、DomainVersion、Consumer display |
| 02 | matching DomainVersion + AdmissionReceipt +必要 binding | Checkpoint、Telemetry、无因果更高 DomainVersion |
| 03 | validated Manifest / Serving fact；task ReadinessDecision | 单个 OCR / index / embedding success |
| 04 | Runtime control state / Step Acceptance / RunOutcome | Domain Admission、Effect、Publication |
| 05 | Capability Contract + Conformance / Eligibility + typed output | Provider 2xx、Domain acceptance |
| 06 | EffectReceipt / ReconciliationReceipt | HTTP 2xx、Attempt finished、Checkpoint |
| 07 | Routing / Attempt / Usage / Settlement facts | Step acceptance、Capability quality、Domain admission |
| 08 | Authorization / Approval / Policy decision | 实际读取、模型调用、Effect、purge completion |
| 09 | Telemetry projection；版本化 Eval / ReleaseEvidence | Owner truth、Production Readiness 本身 |

任何模块都不得用自己最容易获得的 `success` 替代相邻 Owner 的更强完成证明。

## Cancellation（取消）是停止未来工作，不是全局回滚

取消只能停止还能安全停止的未来工作。已经提交的 02 Domain transaction 不消失；已确认 06 EffectReceipt 不撤销；in-flight Effect 继续 Reconcile；07 已发生 Usage 继续结算；03 未完成 generation 不得因取消而激活；01 已发送 Delivery 不得声称远端没收到；09 只记录时间线。

真正的补偿必须是新的受控业务动作，而不是改旧 Receipt。

## Late Result（晚到结果）统一验收

晚到结果既不自动丢弃，也不自动接受。消费者至少检查 causation、PlanVersion、input versions、DocumentVersion / KnowledgeGeneration、Capability / Tool / Model versions、SecurityEpoch、Domain expected version，以及现实 Effect 是否已经发生。

纯计算的关键假设过期时进入 reject / reevaluate / Review / Replan；现实 Effect 即使来自旧 Plan，也不能被 Runtime 通过“stale branch”否认。

## Idempotency（幂等）不是一个全局 key

```text
request / invocation idempotency       → 01
knowledge generation / processing item → 03
step / dispatch identity               → 04
capability invocation identity          → 05
prepared action / external effect       → 06
model attempt / usage settlement        → 07
security decision / approval identity   → 08
formal admission idempotency            → 02
publication / delivery identity         → 01
eval run / experiment identity          → 09
```

跨模块用 causation refs 关联，不共用一个万能 key。`same key + different action hash`、`same admission key + different canonical input` 必须冲突失败。

## 恢复时先找 Owner Fact，再修复 Projection

| 故障 | 第一恢复锚点 | 后续修复 |
| --- | --- | --- |
| Domain commit 后 Checkpoint 失败 | 02 matching AdmissionReceipt | 04 Runtime Control State |
| Checkpoint complete 但 Receipt 缺失 | 02 causation query | 04 撤销 formal-complete 推断 |
| POST timeout outcome unknown | 06 Action / Attempt / external correlation | Reconcile 后修复 04 / 01 |
| Knowledge partial write | 03 generation / manifest / serving pointer | Retry / rebuild，不改 Domain |
| SecurityEpoch 在等待期变化 | 08 current decision | 下次受保护访问重新门禁 |
| Consumer offline while WorkProduct stale | 02 invalidation truth | 01 Delivery retry；pull 仍 stale |
| Telemetry provider outage | 各 Owner durable facts | 09 恢复诊断投影 |
| Model cancel / billing unknown | 07 Attempt / Usage refs | settlement；04 修复 Budget |

普通 Trace 从来不是唯一恢复依据。

## Correlation（关联）也必须遵守安全边界

跨模块 correlation 默认传播 opaque identity。tenant / matter 名称、用户 PII、材料正文、Secret、授权正文不能为了日志方便直接进入 OpenTelemetry Baggage。需要真实上下文时在可信边界用 opaque ref 回查 Owner fact。

## 横向系统设计：规模、性能、一致性和可靠性落到哪里

| 横向问题 | 首要责任域 | Target 原则 |
| --- | --- | --- |
| 重复 HTTP、异步受理、交付重试 | 01 | request / invocation / delivery identity 分离；受理 != 完成 |
| 正式领域并发、版本冲突 | 02 | Owner Store 内短事务、expected version、幂等 |
| OCR / embedding / index 构建吞吐 | 03 + Platform | generation 内并行；validated generation 才 Serving |
| DAG 并发、资源冲突、取消 | 04 | Ready 受 dependency/resource/effect/budget/quota/security gates |
| 专业 / 模型 Provider 容量 | 05 / 07 | eligibility + quota + quality + security 一起决定 fallback |
| 外部系统限流、timeout、未知效果 | 06 | known-not-executed 才 Retry；unknown 先 Reconcile |
| tenant / matter 隔离、外发、Secret | 08 | 每次新受保护访问消费当前安全事实 |
| latency、throughput、cost、quality | 09 | 统一测量，不接管业务完成；容量需要真实 Evidence |
| PostgreSQL、Object Store、Queue、Worker、Checkpoint、Backup | Platform / Infrastructure | 提供物理原语，不拥有逻辑成功语义 |

扩容按工作类型和真实瓶颈，而不是把九个逻辑模块机械拆成九个微服务。Backpressure 必须显式；Cache 只能加速 Projection；一致性按 Owner 边界设计，不追求跨所有 Store 的全局 2PC。HA / DR、QPS 和容量只有在 RPO / RTO、load、takeover / fencing、backup / restore 和外部依赖演练形成证据后才能宣称 Current。

## 9/9 Detail Design Candidate 怎样阅读

Detail Candidate 没有新增一套“字段文档”。每篇仍采用同一 A/B/C 文档：Part A 解释业务问题和运行场景；B1–B13 固定模块语义；B14 先声明实现约束，再用 B14.1–B14.8 把冻结前必须钉死的字段、Guard、故障和 Migration 细化；Part C 最后检查跨模块一致性。

九篇 B14.1–B14.8 共同覆盖以下问题：

```text
B14.1  核心输入 / 权威对象字段组
B14.2  第二关键对象 / 版本 / 因果字段组
B14.3  Guard / Eligibility / State / Dependency
B14.4  幂等 / 资格 / 控制语义
B14.5  事务 / 发布 / 执行边界
B14.6  Crash Window / Cancel / Late Result
B14.7  Schema Evolution / Migration / Upgrade
B14.8  Failure Injection / Freeze Evidence
```

具体内容按模块不同，不要求九篇复制同一数据库模型。Candidate 的目的恰恰是暴露每个 Owner 真正需要什么，而不是套模板建九套表。

## 全模块共同遵守的架构不变量

1. 模型、Capability、Retrieval、Memory、Specialist 只产生 Proposal / Candidate，不直接提交 Canonical Domain State。
2. 上传成功不等于 Knowledge Ready；Readiness 相对于 DocumentVersion + generation + task scope + requirement + security。
3. Native Runtime entrant 一定有 Plan：简单单步，复杂 Dynamic DAG。
4. PlanVersion 激活后不可原地修改；Replan 新建版本并经过 Replan Barrier。
5. Retry != Replan != Reconcile。
6. Domain State 与 Runtime Control State 分开；Checkpoint 不证明 Admission。
7. 安全是持续门禁；受保护读取、模型外发、Secret、Tool Effect、Formal Admission 消费当前安全决定。
8. 高风险 Effect 的幂等、Approval、Mandatory Audit、Outcome Unknown 恢复必须闭合。
9. OTel / LangSmith Telemetry 不是 Durable Audit / Business Truth。
10. Native Runtime、Long-term Memory、Specialist / Multi-Agent、GraphRAG 均 measurement / evidence gated。
11. 逻辑模块不等于微服务；默认 Modular Python Backend + justified Workers。
12. Platform / Infrastructure 不是第十个业务模块，只提供 physical primitives。
13. Memory / Context 是 Optional Provider Boundary，不覆盖 Domain / Security truth。
14. Current / Target / Gap 分开；文档完整不证明实现。
15. Cancellation 不是全局 rollback。
16. Late result 必须重新验收。
17. Idempotency namespace 分离。
18. Correlation 不携带权威和敏感业务语义。

## 九篇统一结构

```text
Part A  Human Narrative

Part B  Engineering / Agent Reference
  B1  Scope / Global Invariants
  B2  Responsibility / Ownership
  B3  Upstream / Downstream
  B4  Authoritative Facts / Core Objects
  B5  Cross-boundary Contracts
  B6  Normal Flow
  B7  State / Lifecycle
  B8  Failure Taxonomy
  B9  Retry / Replan / Reconcile / Recovery / Idempotency
  B10 Security / Approval / Audit
  B11 Persistence / Transaction Boundaries
  B12 Observability / Evaluation
  B13 Current / Target / Gap / Evidence
  B14 Code / Database / Migration Constraints
      B14.1–B14.8 Detail Freeze Candidate

Part C  Cross-Module Consistency
  C1 Completion Proof / Non-proof
  C2 Causation / Version / Freshness Bindings
  C3 Cancellation / Late Result / Staleness Rules
  C4 Recovery Order / Consistency Tests
```

## 设计依赖顺序与当前进度

```text
Stage 1: 02 法律领域 + 03 知识证据          DETAIL DESIGN CANDIDATE V1 AVAILABLE
Stage 2: 08 安全治理 + 06 工具外部效果      DETAIL DESIGN CANDIDATE V1 AVAILABLE
Stage 3: 05 专业能力 + 04 运行控制          DETAIL DESIGN CANDIDATE V1 AVAILABLE
Stage 4: 07 模型网关 + 09 可观测性评测      DETAIL DESIGN CANDIDATE V1 AVAILABLE
Final:   01 应用与集成                       DETAIL DESIGN CANDIDATE V1 AVAILABLE
```

这个顺序是设计依赖，不是运行时调用顺序。

## 下一道门：Module Detail Freeze Review

九模块 Candidate 结束后，下一步不是大规模实现，而是逐模块和跨模块 Detail Freeze Review。至少要盘问：字段是否足以表达 identity / version / freshness；状态转换 Guard 是否闭合；不同幂等 namespace 是否会串；Owner Store 的事务 / CAS 是否足够；每个 Crash Window 是否有 durable anchor；Migration 是否保护历史；权限变化和晚到结果是否可控；Failure Injection 是否覆盖正常与异常路径；是否出现不必要的新服务、锁或状态机。

只有 Reviewer 认为模块内部与跨模块语义闭合，才可以把具体模块标记为 `module_detail_freeze: FROZEN` 或等价状态。即使冻结，也仍需要用户明确 Implementation Authorization 后才能生成 Codex 业务实现任务。

当前保持：

```text
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
quality_proven: NO
production_readiness: NOT_ESTABLISHED
```

## Platform / Infrastructure 与 Optional Context

Platform / Infrastructure 继续是责任层，不是第十模块。它提供 PostgreSQL、Object Store、Queue / Worker、Checkpointer Adapter、CAS、Lease、Fencing、Clock、Network、Secret Delivery、Backup / Restore 等原语；业务完成和恢复语义仍由各模块拥有。

Memory / Context 继续是可选 Provider Boundary。Working / Session Context 可以由 Host / Runtime 管理；Long-term Memory 只有在消融评测证明收益后才启用。Memory Entry 不能替代 Matter / Evidence / Finding / WorkProduct。

## 状态总结

九个模块现在都达到 **Detail Design Candidate V1**：不仅说明“模块做什么”，还明确实现前需要审查的核心字段、版本 / 新鲜度、幂等、事务 / 持久化、并发、Crash Window、Schema Evolution 和 Failure Injection。下一步进入冻结审查，而不是自动实施。

`detail design candidate` 不等于 `module detail frozen`；`design available` 不等于 `implementation available`；`implementation available` 不等于 `quality proven`；`quality proven` 也不自动等于 `production ready`。