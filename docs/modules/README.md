# Zuno 模块架构

九个模块首先是一张**责任地图**：当一次法律任务跨越材料、模型、专业分析、正式结果、现实副作用和外部交付时，哪一类事实由谁最终负责，失败以后先相信谁。它们不是九段固定流水线，也不是九个微服务。

第一次阅读本目录，不需要先记 `AdmissionReceipt`、`PlanVersion`、`PreparedAction` 等内部对象。先理解三条任务路径和九个责任域为什么存在；真正实施时再进入每篇 Part B / Part C 查精确 Contract、状态和 Crash Window。

## 先用三条任务路径建立 mental model

### 简单法律问答

用户问“合同第 8 条写了什么”时，最短合理路径是：明确 Scope，检查当前授权，确认所需材料已经就绪，检索原文和稳定引用，受控调用模型，最后检查答案是否可以发布。

这条路径不默认需要 Native Runtime、Dynamic DAG、Multi-Agent、Long-term Memory 或 GraphRAG。通用 Host 如果遵守同样的安全、知识和发布边界，也完全可以承担会话和 UI。

### 复杂法律分析

多材料争议分析开始需要显式控制：系统先确认材料版本和知识覆盖，再由 Runtime 组织多步依赖、并行专业能力和必要人工复核。检索和模型产生的内容仍然只是候选，只有需要成为长期法律业务事实的结果才进入 02 Formal Admission。

这里最重要的不是“经过多少 Agent”，而是运行控制、专业计算和正式业务事实始终保持三个边界。Runtime 可以完成任务，但不能替 Domain 宣布正式结果。

### 带现实副作用的任务

如果系统要向外围法院系统提交结果，问题从“算得对不对”增加到“现实世界到底发生了什么”。动作发送前要重新确认授权、必要审批、幂等和强制审计；发送后 timeout 时先对账，禁止因为本地没有响应就盲重试。

06 负责现实 Effect truth，01 负责产品交付语义，08 负责当前是否允许。三个模块协作，但互不冒充对方的完成事实。

## 九个责任域分别为什么存在

| 编号 | 责任域 | 用一句人话说明它保护什么 | 文档 |
| --- | --- | --- | --- |
| 01 | Application & Integration | 把内部权威事实组合成稳定请求、发布、交付和失效传播语义 | [01](01-application-integration.md) |
| 02 | Legal Domain & Work Product | 决定什么最终成为正式、长期、可审计的法律业务事实 | [02](02-legal-domain-work-product.md) |
| 03 | Knowledge & Evidence | 区分正式材料、可重建知识派生、任务就绪和检索候选 | [03](03-knowledge-evidence.md) |
| 04 | Agent Runtime & Control | 控制长任务怎样计划、并行、暂停、重规划和恢复 | [04](04-agent-runtime-control.md) |
| 05 | Capability & Skill | 把研究算法和 Provider 变成稳定、版本化、可替换的专业能力 | [05](05-capability-skill.md) |
| 06 | Tool Runtime & Effects | 在现实副作用发生前后保护动作身份、结果确认和对账 | [06](06-tool-runtime-effects.md) |
| 07 | Model Gateway | 把模型调用变成受质量、安全、预算和用量约束的依赖 | [07](07-model-gateway.md) |
| 08 | Security & Governance | 持续回答下一次受保护动作现在是否仍被允许 | [08](08-security-governance.md) |
| 09 | Observability & Evaluation | 解释系统发生了什么，并验证复杂度是否值得保留 | [09](09-observability-evaluation.md) |

这些责任域按事实 Ownership 切分，不按技术栈切分。默认可以共处模块化 Python 后端；只有吞吐、安全隔离、故障半径或部署生命周期出现证据时才拆物理服务。

## Part A、Part B、Part C 应该怎么读

Part A 可以很长，它负责把概念设计讲透：问题是什么、最简单方案为什么不够、边界如何推导、典型失败怎样恢复、替代方案和删除条件是什么。长度应该来自推理，而不是名词密度。

Part B 把已经理解的设计精确化成 Owner、Contract、状态、事务、幂等、持久化和 Detail Freeze Candidate；Part C 再检查这些语义跨模块以后，完成证明、版本、新鲜度、取消、晚到和恢复是否仍然一致。

如果一个对象名必须先读 Part B 才知道它为什么存在，Part A 应补概念解释；反过来，如果 Part A 开始连续枚举字段、enum 和 crash-window 表格，则应该下沉到 Part B。

> **第一次阅读到这里可以停。** 你现在只需要能说清三条任务路径的复杂度差异、九个责任域分别保护什么，以及什么时候读 Part A / B / C。下一步应按问题选择一到两个 Module Part A，而不是继续顺序背下面的 Ownership 表、Completion Proof、Cancellation、Late Result 和 Recovery Reference。下面开始更偏向架构维护者和跨模块审查。

## 修改一个模块时，先定位事实，不要先画调用链

跨模块设计最容易被“谁调用谁”带偏。A 调 B，并不表示 A 拥有 B 的结果；异步消息也不天然比同步 RPC 更解耦。先问当前变化涉及的事实是什么、由谁最终证明、消费者最多能做什么，再决定它通过函数调用、Queue、Event、数据库查询还是缓存传播。

例如 04 可以调用 02 请求 Formal Admission，但完成证明仍然来自 02；01 可以查询 06 的 Effect，但不能因为自己发起了 Delivery 就拥有现实结果；09 可以订阅所有模块事件，却不会因为信息最全就升级成业务 Authority。调用方向是实现拓扑，事实 Ownership 才是架构边界。

## 模块边界不等于同步 RPC 边界

九个责任域可以先共处一个进程，也可以在以后按吞吐或隔离需要拆开。即使物理共进程，也应该保持 Owner fact、版本和完成证明；即使物理拆成服务，也不意味着每次判断都必须远程同步调用。

对可重建 Projection，可以异步传播；对当前安全门，可以在受保护动作前消费仍有效的 Decision；对正式提交和现实 Effect，则要读取能够证明完成的 durable fact。通信方式应由一致性、延迟和恢复要求决定，而不是由“模块已经画了边界”自动推出。

## 一个跨模块改动至少要通过四个问题

第一，新增事实到底由谁拥有，是否出现两个 Owner；第二，消费者看到什么才算完成，什么明确不能作为证明；第三，Owner 已成功但消费者 Projection 失败时怎样恢复；第四，旧版本、晚到结果和权限变化后，这个事实是否仍然有资格继续使用。

如果四个问题只能靠“大家约定不要出错”回答，说明 Contract 还不够稳；如果为了回答它们必须创建一个全局万能状态表，说明责任边界可能被重新混在一起。Part C 的价值就是在这里检查局部正确的模块设计跨边界后是否仍然成立。

## 当前模块设计状态

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

**9/9 Detail Design Candidate 只表示 Target Design 已达到冻结前可审查粒度。** Current、实现、质量和生产资格继续回到 `docs/evidence/`；`DETAIL DESIGN CANDIDATE V1 AVAILABLE` 不等于 `Module Detail Freeze Review` 已通过。

## 为什么下面还保留大量 Reference

从下一节开始，本 README 转入跨模块 Reference：事实 Ownership、Completion Proof、Cancellation、Late Result、Idempotency、Recovery 和横向系统设计。它们用于整体一致性审查，不要求第一次阅读全部记住。

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