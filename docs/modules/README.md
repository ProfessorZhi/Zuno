# Zuno 模块架构

总体架构已经冻结九个逻辑责任域。本目录在 Deep Design V1（深化设计 V1）的基础上继续完成 **Cross-Module Consistency V2（跨模块一致性深化 V2）**：九篇模块文档继续保留 Human-first Part A 和 B1–B14 Engineering Reference，并统一增加 Part C，用同一组问题检查完成证明、因果与版本、新鲜度、取消、晚到结果、恢复顺序和跨模块故障一致性。

这仍然不是 Module Detail Freeze（模块细节冻结），也不是 Implementation Authorization（实现授权）。V2 的含义是“九个模块之间的 Target 语义进一步对齐并可机器检查”，不是字段级 Contract、数据库表、Migration、API、物理服务或生产资格已经冻结。

```text
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

## 九个模块与当前深化重点

| 编号 | 模块 | 首先回答的问题 | V2 一致性重点 | 文档 |
| --- | --- | --- | --- | --- |
| 01 | Application & Integration（应用与集成） | 请求怎样进入 Zuno，结果由谁发布、交付和失效通知？ | Publication / Delivery 不是 Domain / Consumer truth；取消和晚到 Ack | [01](01-application-integration.md) |
| 02 | Legal Domain & Work Product（法律领域与工作成果） | 什么才是正式、长期、可审计的法律业务事实？ | matching AdmissionReceipt、历史引用、新证据失效、晚到 Proposal | [02](02-legal-domain-work-product.md) |
| 03 | Knowledge & Evidence（知识与证据） | 哪一版材料现在真的可用于这次任务？ | generation / serving / readiness 分层、build cancel、late retrieval | [03](03-knowledge-evidence.md) |
| 04 | Agent Runtime & Control（智能体运行与控制） | 复杂任务怎样计划、并行、暂停、重试、重规划和恢复？ | control proof 不替代业务 proof、Replan 后 late branch、cancel + receipt recovery | [04](04-agent-runtime-control.md) |
| 05 | Capability & Skill（专业能力与技能） | 专业算法怎样成为版本化、可替换、可评测能力？ | Conformance / Eligibility / Quality / Admission 分层、provider drift | [05](05-capability-skill.md) |
| 06 | Tool Runtime & Effects（工具运行与外部效果） | 现实动作怎样准备、执行、确认、去重和对账？ | EffectReceipt、cancel-in-flight、action hash、outcome unknown | [06](06-tool-runtime-effects.md) |
| 07 | Model Gateway（模型网关） | 模型怎样按角色、安全、预算和资格统一调用？ | call / usage truth 与 Step / Domain truth 分离、cancel / billing settlement | [07](07-model-gateway.md) |
| 08 | Security & Governance（安全与治理） | 长任务中谁现在仍被允许做什么？ | Decision 不是 execution truth、SecurityEpoch freshness、approval hash、lifecycle enforcement | [08](08-security-governance.md) |
| 09 | Observability & Evaluation（可观测性与评测） | 系统发生了什么，复杂度是否值得保留？ | Telemetry / Eval 不替代 Owner truth；opaque correlation；BLOCKED 不伪装 PASS | [09](09-observability-evaluation.md) |

**九篇“深化完成”只表示 Target Design 达到可审查状态，不表示实现、测量、Qualification 或 Production Readiness 已经完成。**

## 先从三条真实任务主线理解九个模块

九个模块不是每个请求都必须依次经过的固定流水线。任务越简单，路径越短；只有风险、恢复和长期业务状态要求增加时，才引入更多责任域。

### 主线一：简单法律问答

例如用户问“合同第 8 条写了什么”。应用与集成明确事项和材料范围，安全与治理给出当前授权，知识与证据确认对应材料对本次任务已经就绪并返回来源，模型网关完成受控生成，应用与集成检查答案资格并发布。

```text
01 请求 / Scope
→ 08 当前授权
→ 03 task-level Readiness + Retrieval
→ 07 受控模型生成
→ 01 Answer Publication
```

这条路径不默认需要 Dynamic Plan、多智能体、长期 Memory 或 GraphRAG。Generic Host（通用 Agent 宿主）只要遵守同一安全、知识和发布 Contract，也可以承担它。

### 主线二：复杂法律分析

```text
01 请求 / Scope
→ 08 当前授权
→ 03 DocumentVersion 对应的知识就绪 / EvidenceCandidate
→ 04 Plan / Step / Parallel / Join
↔ 05 专业 Capability
↔ 07 模型角色调用
→ 02 Finding Proposal / HumanDecision / Formal Admission
→ AdmissionReceipt + WorkProductVersion
→ 01 Publication / Delivery
```

Runtime 负责“这次执行怎样继续”，Capability 负责“怎样做专业分析”，Domain 负责“什么最终成为正式法律业务事实”。

### 主线三：带现实副作用的任务

```text
04 / 05 Action Proposal
→ 06 PreparedAction
→ 08 当前 Authorization / Approval / Audit Requirement
→ 06 ToolAttempt
→ EffectReceipt
→ Outcome Unknown 时 Reconciliation
→ 02 必要时 Formal Admission
→ 01 Delivery / Notification
```

现实结果未知时禁止 Blind Retry（盲重试）。

## 九模块之间最重要的事实所有权

模块可以运行在同一个 Python 进程、同一个 PostgreSQL 实例或同一组 Worker 上，但“谁说了算”必须唯一。

| 事实 / 决定 | 权威责任域 | 其他模块最多能做什么 |
| --- | --- | --- |
| Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct | 02 | 读取引用、提出候选，不直接改正式状态 |
| Formal Admission、AdmissionReceipt、WorkProductCitationBinding、Domain invalidation truth | 02 | 04 用回执恢复；01 做发布 / 失效交付 |
| KnowledgeGeneration、ReadinessDecision、EvidenceCandidate、CitationLineage | 03 | 02 可接纳候选为正式 Evidence / 正式引用 |
| AgentRun、PlanVersion、StepRun、Branch / Join、Budget、Checkpoint、RunOutcome | 04 | 其他模块返回 facts / receipts，不接管计划状态 |
| Capability identity / version、Conformance、Eligibility、专业 Proposal | 05 | 04 调度；02 决定是否正式接纳 |
| PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt | 06 | 08 决定是否允许；外部系统拥有其内部最终事实 |
| Model role mapping、ModelRoutingDecision、ModelCallAttempt、Quota、Usage / Cost | 07 | 09 评测；08 决定外发 / Credential policy |
| AuthorizationDecision、SecurityEpoch、ApprovalDecision、EffectiveLifecycleDecision、AuditRequirement | 08 | 各执行边界 / Store 负责自己的执行事实 |
| Trace、Metric、Eval Dataset / Result、Experiment、ReleaseEvaluationEvidence | 09 | 只做投影 / 测量，不接管业务 truth |
| External Task Intake、InvocationDecision、AnswerPublicationDecision、Delivery、InvalidationDelivery、Consumer Ack Observation | 01 | 外部 Host 拥有自己的最终 UI / 内部采用事实 |

## 几组绝对不能再次混淆的边界

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
```

V2 再增加四组不能混淆的边界：

```text
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

不同模块不共享一张“万能状态表”，但一次任务必须能通过稳定 identity / refs 串起来。目标上的因果主干是：

```text
ExternalRequestIdentity / InvocationIdentity
→ AgentDefinitionVersion
→ [RunId → PlanVersion → StepRun / Branch]
→ KnowledgeGeneration / ReadinessDecision / EvidenceCandidate refs
→ CapabilityVersion / Invocation refs
→ ModelRoutingDecision / ModelCallAttempt refs
→ PreparedAction / ToolAttempt / EffectReceipt refs
→ AuthorizationDecision / ApprovalDecision / SecurityEpoch refs
→ DomainVersion / AdmissionReceipt / WorkProductVersion
→ PublicationIdentity / DeliveryIdentity
→ Telemetry / Eval correlation refs
```

这里的箭头表示“可追溯关联”，不是把所有对象放进一张表，也不表示每个任务一定经过全部节点。

## 每个模块都必须明确“什么才算完成”

| 模块 | 本模块权威完成证明 | 明确不是完成证明的东西 |
| --- | --- | --- |
| 01 | Publication / Delivery 自己的 durable fact | Run complete、DomainVersion、Consumer display |
| 02 | matching DomainVersion + AdmissionReceipt；必要历史引用绑定 | Checkpoint、Telemetry、更高但因果不匹配的 DomainVersion |
| 03 | validated manifest / serving fact；task-level ReadinessDecision | 单个 index / OCR / embedding success |
| 04 | Runtime control state / Step Acceptance / RunOutcome | Domain Admission、Tool Effect、Publication truth |
| 05 | Capability Contract + Conformance / Eligibility 下的 typed output | Provider 2xx；正式 Domain acceptance |
| 06 | EffectReceipt / ReconciliationReceipt | HTTP 2xx、ToolAttempt finished、Checkpoint |
| 07 | Routing / Attempt / Usage facts | Step Acceptance、Capability quality、Domain Admission |
| 08 | Authorization / Approval / Policy decision | 实际读取、模型调用、Effect、purge completion |
| 09 | Telemetry projection；版本化 Eval / Release Evidence | Domain / Security / Effect truth；Production Readiness 本身 |

任何模块都不得用自己最容易获得的 `success` 替代相邻模块更强的完成证明。

## Cancellation（取消）是停止未来工作，不是全局回滚

跨模块统一取消语义：

1. 01 取消请求或 04 取消 Run，只阻止后续可以停止的调度 / 计算；
2. 已经提交的 02 Domain transaction 不因 Run 取消而消失；
3. 已经确认的 06 EffectReceipt 不因 Run 取消而撤销；
4. 06 已发出但结果未知的外部动作必须继续 Reconcile；
5. 07 的 model cancel 可能仍存在 Usage / Billing ambiguity，需要独立结算；
6. 03 未完成 generation 被取消后不能静默激活 Serving；
7. 01 已经发送到远端的 Delivery 不能因为本地 cancel 就声称“消费者未收到”；
8. 09 可以记录 cancel 后晚到 telemetry，但不能用晚到 span 改业务状态。

真正需要“撤销现实效果”时，应有明确补偿 / 反向业务动作；不能把本地 cancel flag 当成回滚协议。

## Late Result（晚到结果）统一验收规则

晚到结果不是自动丢弃，也不是自动接受。消费者必须检查与自己相关的当前条件：

```text
causation identity still matches?
PlanVersion / input versions still valid?
DocumentVersion / KnowledgeGeneration still applicable?
Capability / Tool / Model version still eligible?
SecurityEpoch / Authorization still sufficient for the next protected use?
Domain expected prior version still matches?
side effect already happened even if branch is stale?
```

对纯计算结果，如果任一关键假设已经失效，通常丢弃、重评、Review 或 Replan。对现实 Effect，即使旧 Plan 已过期，也不能因为“分支过期”否认已经发生的现实事实；仍以 06 Receipt 为准。

## Idempotency（幂等）不是一个全局 key

不同语义边界必须拥有不同幂等 namespace：

```text
request / invocation idempotency          → 01
knowledge generation / processing item    → 03
step / action execution identity           → 04
capability invocation identity             → 05
prepared action / external effect          → 06
model attempt / usage settlement           → 07
security decision / approval identity      → 08
formal admission idempotency               → 02
publication / delivery identity             → 01
eval run / experiment identity             → 09
```

跨模块通过 causation refs 关联这些 identity，而不是把一个 key 复用于多个语义边界。尤其 `same key + different action hash`、`same admission key + different canonical input` 必须拒绝。

## 恢复时先找 Owner Fact，再修复 Projection

不存在一句无条件的“Domain wins”。恢复必须先问当前故障涉及哪个事实 Owner，再使用相应 durable proof：

| 故障 | 第一恢复锚点 | 后续修复 |
| --- | --- | --- |
| Domain commit 后 Checkpoint 失败 | 02 matching AdmissionReceipt | 04 Runtime Control State |
| Checkpoint completed 但 AdmissionReceipt 缺失 | 02 causation query | 04 撤销 formal-complete 推断 / Review |
| POST timeout outcome unknown | 06 action / attempt / external correlation | Reconcile 后修复 04 / 01 |
| Knowledge build partial write | 03 generation / manifest / serving pointer | 重建 / Retry processing，不改 Domain |
| SecurityEpoch 在等待期变化 | 08 current decision | 目标模块在下次受保护访问重新门禁 |
| Consumer offline while WorkProduct stale | 02 invalidation truth | 01 Delivery 重试；Pull validity 仍返回 stale |
| Telemetry provider outage | 各 Owner durable facts | 09 后续恢复诊断投影 |
| Model cancel / billing unknown | 07 Attempt / provider usage refs | settlement；04 Budget 累计修复 |

恢复和对账都不能以普通 Trace 作为唯一依据。

## Correlation（关联）也必须遵守安全边界

跨模块 Trace 需要稳定关联，但 correlation context 默认只传播不含业务含义的 opaque identity（不透明身份）。tenant、用户身份、案件名称、材料正文、Secret 或授权正文不能为了“查日志方便”直接放进 OpenTelemetry Baggage（上下文行李）。Baggage 只在策略明确允许时传播最小 opaque ref，接收端在可信边界内回查真实事实。

## 横向系统设计问题：规模、性能、一致性和可靠性落到哪里

高级系统设计追问通常不会按九模块逐个问，而会横向追问“并发上来了怎么办、哪里能扩容、哪里必须强一致、缓存会不会读脏、队列积压怎么办、服务挂了怎么恢复”。这些问题不能重新创造一个“平台模块”统一接管，而要回到事实 Owner。

| 横向问题 | 首要责任域 | Target 原则 |
| --- | --- | --- |
| 重复 HTTP 请求、异步长任务、交付重试 | 01 | 请求 / invocation / delivery 身份分离；已受理不等于已完成 |
| 正式领域并发写、版本冲突、事务提交 | 02 | 单个领域提交在 Owner Store 内保证事务；expected prior version / 幂等身份防覆盖 |
| OCR / embedding / index 构建吞吐 | 03 + Platform | generation 内可并行处理；Serving 只切到完整验证的一代；队列成功不等于 Ready |
| 动态 DAG 并发、资源冲突、积压和取消 | 04 | Ready Step 受依赖、资源、副作用、Budget、Quota、Security Gate 约束；过载时显式背压 |
| 专业 Provider 与模型 Provider 容量 | 05 / 07 | eligibility、quota、timeout、fallback 与质量 / 安全边界共同决定，不以“有备用模型”替代能力契约 |
| 外部系统限流、超时和结果未知 | 06 | 已知未执行才 Retry；未知先 Reconcile；现实 Effect 不被本地队列状态覆盖 |
| 租户 / 案件隔离、数据外发、Secret | 08 | 每次受保护访问消费当前安全事实；租户标识不是 Trace 中可随意传播的业务文本 |
| 延迟、吞吐、错误率、Token、成本 | 09 | 统一测量但不接管业务完成事实；容量结论必须有 Benchmark / Load Evidence |
| PostgreSQL、对象存储、Queue、Worker、Checkpoint、Backup | Platform / Infrastructure Responsibility Layer | 只提供物理原语；逻辑模块仍拥有业务完成和恢复语义 |

### 扩容先按“工作类型”而不是按“模块数量”

入口 HTTP、知识构建、模型调用、Eval、外部 Tool 等负载特性不同。默认物理形态仍可以是模块化 Python Backend 加必要 Worker，但耗时和可并行的工作应能够从请求线程中解耦，通过 Worker Pool、Provider 并发限制和 Queue 做受控调度。

扩容顺序优先考虑：先减少不必要工作和重复调用，再优化批处理 / 缓存 / Provider 路由，再独立扩展真正的热点 Worker；只有当独立扩缩容、故障隔离、安全边界、可用性目标或部署生命周期反复出现时，才把某个边界拆成网络服务。九个逻辑模块绝不自动对应九组 Deployment。

### Backpressure（背压）必须显式，而不是让系统慢到超时

队列积压、模型限流、数据库连接耗尽或下游法院系统变慢时，系统需要把“当前不能继续”变成可观测的控制事实：01 可以拒绝或延迟受理，04 可以暂停新的 Ready Step，07 可以执行配额 / 预算路由，06 可以尊重外部限流，03 可以限制新的知识构建任务。

背压不能静默降级成错误业务结果。知识不完整就返回 PARTIAL / BLOCKED 类资格，预算不足就不能假装完整执行，Tool outcome unknown 就不能用 Retry 掩盖。

### Cache（缓存）只能加速 Projection，不能成为新的 Truth Owner

检索结果、模型路由信息、Provider metadata、权限辅助索引和页面结果都可能缓存，但缓存必须携带足够的版本 / freshness 条件。缓存命中不能跳过 SecurityEpoch、DocumentVersion、KnowledgeGeneration、CapabilityVersion 或 DomainVersion 的适用性检查。

对正式领域提交、EffectReceipt、Approval、AdmissionReceipt 等恢复锚点，缓存最多用于读优化，不能成为唯一耐久证明。缓存丢失应该影响性能，不应该改变系统对业务事实的判断。

### 一致性按 Owner 边界设计，不追求跨所有 Store 的全局强一致

02 的领域事务、06 的 Effect 记录、08 的安全决定、04 的 Checkpoint、03 的知识 Serving 都有不同事务边界。Target 不使用跨所有 Store 的 2PC 来制造“全系统一次提交”。Owner 内部需要能够给出自己的 durable proof，跨 Owner 通过 receipt、version、causation ref 和恢复流程收敛。

这意味着系统允许“Domain 已提交但 Runtime Checkpoint 尚未更新”这样的短暂不一致，但必须有 AdmissionReceipt 等恢复锚点使它可识别、可修复；允许“新 WorkProduct 已 stale 但外部消费者暂时离线”，但 02 的 invalidation truth 不能因此回滚。

### HA / DR 和大规模容量仍是待证明工程能力

文档已经定义恢复方向，不代表已经完成高可用、灾备或大规模容量验证。真正声称 HA / DR，需要明确 RPO / RTO、故障域、数据库和对象存储恢复、Checkpointer 恢复、Worker takeover / fencing、外部 Effect 重建以及演练证据；真正声称可支撑某个 QPS / 并发，也需要真实负载、数据规模和 Provider 配额下的测量。

因此面试中可以解释“目标上怎么扩、怎么保持一致、怎么恢复”，但不能把架构原则直接换算成已经测出的生产容量。

## 全模块共同遵守的架构不变量

1. **模型只产生 Proposal。** 模型、Capability、Retrieval、Memory、Specialist Agent 都不能直接提交 Canonical Domain State。
2. **文件上传不等于知识就绪。** Readiness 是 task scope + DocumentVersion + KnowledgeGeneration + requirement + security 的判断。
3. **原生运行时中的任务一定有 Plan。** 简单 = Deterministic Single-Step；复杂 = Dynamic DAG。
4. **PlanVersion 激活后不可原地修改。** Replan 创建新版本；并行重规划经过 Replan Barrier。
5. **Retry != Replan != Reconcile。** 执行暂时失败才重试；计划假设失效要重规划；现实副作用结果未知要对账。
6. **领域状态与运行控制状态分开。** Domain Store 与 LangGraph Checkpointer 的语义不同，不用 Checkpoint 证明正式提交。
7. **安全是持续门禁。** 新读取、模型外发、Secret、Tool Effect 和 Formal Admission 都消费当前安全决定。
8. **高风险 Effect 必须保护审计与幂等。** Mandatory Audit 要求存在时先取得持久化证明；Outcome Unknown 禁止 Blind Retry。
9. **可观测性不是业务真相。** OTel / LangSmith 等只提供 Projection、diagnosis 和 Eval；关键恢复依赖 Owner facts / receipts。
10. **复杂度必须被测量。** Native Runtime、Long-term Memory、Specialist / Multi-Agent、GraphRAG 都是 measurement-gated / evidence-gated。
11. **逻辑模块不等于微服务。** 默认物理起点仍是 Modular Python Backend + Workers where justified。
12. **Platform / Infrastructure 不是第十个业务模块。** 它只提供 physical primitives，不拥有业务成功事实。
13. **Memory / Context 不是一级模块。** 它是 Optional Provider Boundary，不能覆盖 Domain truth 或安全策略。
14. **Current / Target / Gap 必须分开。** 文档写得完整不证明代码已经实现。
15. **Cancellation 不是全局回滚。** 已成立的 Domain / Effect / Usage / Delivery facts 继续按各自 Owner 解释。
16. **Late result 必须重新验收。** 计算成功发生在过去，不代表当前仍有资格进入 Plan / Domain。
17. **Idempotency namespace 分离。** 不使用一个全局 key 混合 request、step、effect、admission、delivery 等语义。
18. **Correlation 不携带权威和敏感语义。** Trace refs 只帮助定位，不成为 Authorization / Business Truth。

## 九篇模块文档采用统一 A / B / C 结构

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

Part C  Cross-Module Consistency
  C1 Completion Proof / Non-proof
  C2 Causation / Version / Freshness Bindings
  C3 Cancellation / Late Result / Staleness Rules
  C4 Recovery Order / Consistency Tests
```

Part A 先让人理解问题和流程；Part B 固定模块内部工程语义；Part C 强制回答“这个模块放进九模块整体以后，会不会和别人对同一个事实说出两套答案”。三部分不一致时必须暴露 Architecture Gap，而不是分别维护三套事实。

## 推荐的设计依赖顺序与当前进度

```text
Stage 1: 02 法律领域 + 03 知识证据          DEEP DESIGN V2 AVAILABLE
Stage 2: 08 安全治理 + 06 工具外部效果      DEEP DESIGN V2 AVAILABLE
Stage 3: 05 专业能力 + 04 运行控制          DEEP DESIGN V2 AVAILABLE
Stage 4: 07 模型网关 + 09 可观测性评测      DEEP DESIGN V2 AVAILABLE
Final:   01 应用与集成                       DEEP DESIGN V2 AVAILABLE
```

这个顺序是设计依赖，不是运行时固定调用顺序。

## 下一道门仍然不是“立即实现全部模块”

九模块 V2 完成后仍保持：

```text
module_detail_freeze: NOT_YET
implementation_authorization: NO
quality_proven: NO
production_readiness: NOT_ESTABLISHED
```

下一步应该继续用完整 E2E 与故障注入场景盘问：字段级 Contract 是否足够表达 V2 的 identity / version / freshness / cancellation / receipt；哪个 Store 持久化哪些 durable fact；数据库与 Migration 是否能支持幂等、因果与历史；哪些目标其实可以继续删除或外置。

只有具体模块完成字段级 Contract、状态转换、错误语义、持久化、Migration、测试与工程证据 Review 后，才考虑 Module Detail Freeze 或生成对应 Codex 实现任务。

## Platform / Infrastructure 与 Optional Context

Platform / Infrastructure（平台与基础设施）继续是责任层，不是第十个逻辑模块。它提供 PostgreSQL、Object Store、Queue / Worker、Checkpointer adapter、CAS、Lease、Fencing、Clock、Network、Secret Delivery、Backup / Restore 等原语；各逻辑模块拥有这些原语承载的业务成功语义。

Memory / Context（记忆与上下文）继续是可选 Provider 边界。Working / Session Context 可以由 Host 或 Runtime 管理；Long-term Memory 只有在消融评测证明收益后才启用，可以由 OpenViking、通用 Host 或其他 Provider 提供。Memory Entry 不能成为 Matter / Evidence / Finding / WorkProduct 的替代真相。

## 状态总结

九个模块现在达到 **Deep Design V2 / Cross-Module Consistency available**：完成证明、因果版本、新鲜度、取消、晚到结果、幂等 namespace、恢复锚点和观测关联已经在九篇中用同一结构表达并准备接受机器校验。

`design available` 不等于 `implementation available`；`implementation available` 不等于 `quality proven`；`quality proven` 也不自动等于 `production ready`。