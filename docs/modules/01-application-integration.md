# 01 Application & Integration（应用与集成）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块解决的是“Zuno 怎样进入真实产品”，不是再造一个万能业务层

Zuno 既可能被自有 Web 页面调用，也可能被法院已有系统、通用 Agent Host、批处理任务或 API 客户端调用。外部系统只关心“我提交的是什么任务、现在进展到哪里、返回的是什么结果、这个结果当前还能不能用”，不应该理解内部九个责任域的全部实现细节。

01 Application & Integration（应用与集成）的职责，就是把这些内部权威事实组合成稳定的产品语义。它负责请求进入、Scope 归一化、调用路径选择、普通答案发布、正式工作成果交付、失效通知和 Host 兼容；但它不能因为最靠近用户，就顺手拥有授权、知识就绪、Domain、Runtime 或 Effect 的真相。

### 为什么 01 必须“负责组合，不负责重新发明事实”

01 会同时看到 08 的 AuthorizationDecision、03 的 ReadinessDecision、04 的 RunOutcome、02 的 AdmissionReceipt、06 的 EffectReceipt 和 07 的模型调用结果。如果 Application Service 为了调用方便，把这些事实各自复制成一套本地 `status`，很快就会出现两个来源互相打架。

因此这个模块的核心约束是：**负责组合，不负责重新发明事实**。它可以形成 InvocationDecision（调用决定）或 AnswerPublicationDecision（答案发布决定），但必须保留所消费的权威 refs，不能自己把“知识 PARTIAL”改成“可以完整回答”，也不能因为 Runtime completed 就推断 WorkProduct 已正式准入。

### 三种“已经完成”为什么必须分开

外部产品最容易把不同层的完成压成一个 `success=true`。Zuno 必须明确：

```text
Run completed
!=
Domain admitted
!=
Answer publishable
!=
Consumer displayed
```

Runtime completed 说明控制流程结束；Domain admitted 说明正式法律业务事实成立；Answer publishable 说明 Zuno 当前允许发布这个普通答案；Consumer displayed 则属于外部 Host 自己的最终 UI / 采用事实。四者可以相关，但不能互相替代。

### 简单问答为什么不应该被统一入口强制塞进 Native Runtime

用户问“合同第 8 条写了什么”，如果当前 Scope 明确、08 授权允许、03 对对应 DocumentVersion 已 READY，并能返回稳定 CitationLineage，07 完成受控生成，那么 01 可以直接做答案资格检查并返回。

```text
01 Intake / Scope
→ 08 Authorization
→ 03 Readiness + Retrieval
→ 07 Model
→ 01 AnswerPublicationDecision
```

这条路径不因为“平台有 Runtime”就必须生成动态 DAG。只有需要多步依赖、并行、暂停、重规划、外部 Effect 或正式复杂 WorkProduct 时才路由到 04。保持简单路径短，是删除不必要复杂度的一部分。

### 复杂任务为什么需要 InvocationDecision，而不是一个 if/else 路由

复杂任务进入前，01 要组合任务目标、Scope、AgentVersion、当前 Authorization、Knowledge Readiness、必要 Capability / Model eligibility，以及任务是否需要 Native Runtime / Formal Admission 等条件。

InvocationDecision 只是对这些权威事实的产品层组合：允许简单执行、路由 Native Runtime、等待知识就绪、要求补充 Scope、进入人工 Review 或拒绝。它不能重新计算下游的安全、知识、模型或能力资格。

### Scope 为什么必须在任务一开始显式化

“帮我分析这个案件”如果没有 Matter、DocumentVersion 范围、用户期望结果和数据边界，后续任何 Readiness、检索、授权和正式准入都无法解释。

01 负责把外部输入归一化成明确 Task / Scope Context，并绑定可信 principal / tenant / matter refs。Scope 不足时应请求补充，而不是让模型根据上下文猜“用户大概想分析哪些材料”。后续如果用户明确缩小或扩大 Scope，应形成新的任务条件并重新消费相应 Readiness / Authorization。

### 外部请求里的身份为什么不能直接成为安全事实

Host 可以传入 user id、tenant id、role，但这些都是 assertion（声明），不是天然可信事实。01 可以接受经过验证的 Host identity assertion、会话身份或受控目录结果，并把稳定 principal / tenant refs 传给 08。

是否有权访问某 Matter、是否允许模型外发或交付，仍由 08 决定。Application Adapter 不能因为某个 Header 写着 `role=admin` 就提高权限。

### Agent Version 和 PlanVersion 为什么不是一回事

**Agent Version = 产品能力 / 配置版本**。它表示这个产品 Agent 当前声明了哪些默认能力、Prompt / policy / runtime profile / supported task class 等配置，是 01 产品表面需要稳定暴露的版本。

PlanVersion 是 04 某一次运行里的控制事实，由 Planner 针对具体任务创建，激活后不可变。AgentVersion 升级不会把已经运行中的 PlanVersion 原地改掉；新请求可以选择新 AgentVersion，既有 Run 继续按自己绑定的版本和兼容策略解释。

### 普通 Answer Publication 和正式 WorkProduct Publication 为什么不同

简单问答可以只需要当前授权、Readiness、Citation / AnswerPolicy 等资格，由 01 做 Zuno 侧 AnswerPublicationDecision。

正式 WorkProduct 则必须先由 02 完成 Formal Admission，拥有 matching AdmissionReceipt、版本和必要历史引用。01 可以负责把这个正式版本发布 / 交付出去，却不能自己把一个 Runtime Draft 提升成正式 WorkProduct。

因此同一个“发布按钮”背后也有两条权威链：普通答案资格归 01 组合；正式成果资格来自 02，01 只消费。

### 外部 Host 最终显示为什么仍不是 Zuno 的真相

如果 Zuno 被 Generic Host 或法院门户嵌入，Zuno 可以返回答案、资格、引用、WorkProductVersion 和 current validity，但 Host 最终是否显示、如何排序、是否被内部流程采用，是 Host 自己的产品事实。

Zuno 不需要控制外部 UI 才能保持架构完整。关键是明确自己对 Zuno-side publication 和 delivery 负责，而不把“远端页面显示了”伪装成本地可证明事实。

### 新证据让 WorkProduct 失效以后，三条状态怎样分开

02 发现新的正式 Evidence 使 WorkProduct V5 stale，这个 Domain invalidation truth 立即成立。01 负责把失效事实推送给已经接收 V5 的外部消费者，并提供 pull validity 查询。

因此必须分开：

```text
WorkProduct invalidated     → 02
Invalidation delivered      → 01
Consumer acknowledged       → 01 对外部响应的 observation
```

外部系统离线不能阻止 V5 在 Domain 中变 stale，也不能让 01 把 stale 恢复成 current。通知可以重试，业务有效性不能倒退。

### 为什么失效既需要 Push，也需要 Pull

Push 可以尽快告诉外部系统“你之前拿到的 V5 已失效”，但远端可能离线、网络失败或通知队列积压。仅靠 Push 无法保证消费者在任何时刻都知道最新有效性。

因此 Target 同时保留 Pull validity：外部系统在使用正式成果前可以查询当前版本是否仍有效。Push 降低传播延迟，Pull 提供最终可检查性，两者都不改变 02 的 Domain truth。

### Delivery 为什么需要自己的 identity

一个 WorkProductVersion 可能要交付给多个外部系统，也可能因为网络失败重试。只用 WorkProduct id 无法区分“同一个成果给系统 A”和“给系统 B”，也无法安全去重。

01 需要稳定 DeliveryIdentity，绑定目标系统、payload schema/version、业务对象版本和 idempotency key。普通明确未发送的 delivery 可以按同 identity Retry；具有现实副作用且 outcome unknown 的交付要交 06 Effect Control / Reconcile。

### 为什么 side-effecting Delivery 必须和 06 协作

有些“交付”只是返回 HTTP response；有些却意味着远端创建记录、正式提交材料或触发业务流程。后者本质上是现实 Effect。

01 仍拥有产品上的 Delivery 状态，但不能自己猜远端是否执行。它把具体外部动作交给 06，消费 PreparedAction / EffectReceipt / ReconciliationReceipt，再更新自己的交付 observation。这样 Delivery 语义和 Effect truth 不会被混在一个 retry loop 里。

### Consumer Ack 为什么只是 Observation

远端返回 `ack=true` 能证明 Zuno 观察到一个响应，但不能证明远端内部所有业务流程已经采用该结果。尤其在异步外围系统里，ACK 可能只代表消息已接收。

所以 ConsumerAcknowledgementObservation 归 01，保存观察到的 ack / no-ack / remote correlation；外部系统内部最终 adoption truth 仍归外部系统。Zuno 不越权定义它。

### 重复请求为什么不能启动第二个复杂 Run

移动网络、浏览器重试、API Gateway 超时都会造成同一个请求重复到达。01 需要把 ExternalRequestIdentity、request idempotency 和 InvocationIdentity 分开：重复 transport request 如果 canonical task input 相同，可以返回已经受理的 invocation / result；同 key 不同 task hash 则冲突。

这样客户端在“提交成功但响应丢失”后重试，不会启动第二个 AgentRun 或重复正式交付。

### 请求取消为什么不能撤销已经发生的事

用户取消一个长任务时，01 可以向 04 请求停止未来运行工作，也可以停止尚未发送的 Delivery。但已经提交的 02 Domain transaction、已经确认的 06 Effect、已经发送到远端的 Delivery 都不会因为本地 cancel flag 消失。

01 的 cancel response 必须反映“取消请求已接受 / 控制停止中 / 已存在不可撤销事实”等真实语义，而不是简单返回 `cancelled=true` 让用户误以为现实已回滚。

### Host Adapter 为什么只能处理兼容，不能改业务语义

不同法院系统可能字段命名、认证方式、同步 / 异步协议不同。Host Adapter 可以做 payload mapping、protocol version、transport error mapping、签名和 endpoint compatibility。

但 Adapter 不能把 `PARTIAL` 改成 `READY`，不能把 Draft 标成正式 WorkProduct，也不能为了兼容旧 Host 而跳过 Approval / Security / Effect Control。协议兼容层不能成为架构后门。

### 为什么 Outbox 可以有，但不能成为第二套 Domain Truth

正式 WorkProduct 已准入以后，01 可以使用 Outbox / Queue 做可靠交付。Outbox 记录“有一条 Delivery 工作要执行”，不是 WorkProduct 当前有效性的权威。

Domain invalidation 发生后，即使旧 Delivery message 还在队列，发送前也应重新检查 payload / current validity / delivery policy；不能因为队列里已有消息就继续向外发布 stale 正式成果。

### Backpressure 为什么必须在入口暴露

当 Runtime queue、知识构建、模型配额或外围系统已经过载，01 不应继续无限受理然后让所有请求在内部超时。对于异步任务可以返回明确 accepted / queued / deferred；对于无法保证资源的同步请求可以限流或拒绝。

背压是产品语义，不是把超时包装成“处理中”。它也不能通过降低授权、Readiness 或正式结果质量门槛换取吞吐。

### API / Host Contract 为什么需要版本

外部系统升级节奏可能慢于 Zuno。一个字段从“可选”变“必填”，或一个状态被拆成两个，如果没有 HostContractVersion，就可能让旧消费者错误解释新响应。

01 需要版本化外部 Contract，优先 additive compatibility；语义变化创建新版本并提供明确迁移 / 兼容窗口。Adapter 能兼容 transport schema，但不能同时维护两套互相冲突的业务 truth。

### 从一个完整工作日看 01 的真实责任

上午用户通过 Zuno UI 做简单条文问答；中午法院系统通过 API 发起复杂分析，Runtime 产生 WorkProduct V3；下午新 Evidence 让 V3 stale，01 向法院系统发送 invalidation；晚上外部系统离线，通知仍 pending，但 pull validity 已能返回 stale。

四个阶段使用不同入口和传输，却共享同一个 Matter、Domain truth、Security policy 和 Knowledge facts。01 的价值就是把这些事实稳定地组合成外部可以理解的产品生命周期，而不是把所有底层逻辑搬到 API 层。

### 什么时候应该让 01 保持“无聊”

Application 层最容易成为 God Service：缺字段就在这里补、状态难查就在这里缓存、外部失败就在 Adapter 里无限重试。健康的 01 反而应尽量“无聊”：明确读取 Owner facts，做归一化、组合、路由、发布、交付和兼容。

需要准入找 02，需要 Readiness 找 03，需要复杂运行找 04，需要专业能力找 05，需要 Effect 找 06，需要模型调用找 07，需要安全找 08，需要测量找 09。边界稳定，外部产品才不会把内部偶然实现变成长期 API 负担。

### 当前、目标与缺口

Current Evidence 已证明 Product API 有分离的 Application Owner：`ProductService`、`ProductIngestionService`、`AgentRunApplicationService`、`ProductArtifactService` 等，当前 Runtime Baseline 也明确 Product API 不再依赖一个全能 Runtime Facade。

Target 是完整 External Task Intake、TaskScope、AgentDefinition / AgentVersion、InvocationDecision、AnswerPublicationDecision、WorkProduct Delivery、Invalidation Delivery、Consumer Ack Observation、current-validity query 和多 Host compatibility。Gap 仍包括 Simple QA Host E2E、publication qualification、可靠 delivery / outbox、push + pull invalidation、Consumer offline fault、Host contract versioning、AgentVersion / PlanVersion compatibility 和 side-effect delivery handoff。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. 01 负责 External Intake / Composition / Zuno-side Publication / Delivery，不重新计算其他 Owner 的事实。
2. 负责组合，不负责重新发明事实。
3. Simple QA 不因统一入口被强制进入 Native Runtime。
4. RunOutcome != Domain Admission != AnswerPublication != Consumer Display。
5. WorkProduct formal eligibility 来自 02；01 只发布 / 交付合法版本。
6. 外部 Host 拥有其最终 UI / internal adoption truth。
7. Domain invalidation、InvalidationDelivery、ConsumerAckObservation 是三个事实。
8. Agent Version = 产品能力 / 配置版本；PlanVersion = 04 单次运行控制版本。
9. side-effecting Delivery outcome unknown 交 06 Reconcile，01 不 blind retry。
10. request / invocation / publication / delivery / ack identity namespace 分离。
11. Host Adapter 不改变 Authorization / Readiness / Domain / Effect semantics。
12. Cancel 不是 Domain / Effect / remote delivery rollback。

### B2 Responsibility / Ownership

**Owns**：ExternalRequestIdentity、TaskScope normalization、trusted Host assertion binding、AgentDefinition / AgentVersion product surface、InvocationDecision composition、Zuno-side AnswerPublicationDecision、DeliveryIdentity / DeliveryState、InvalidationDeliveryFact、ConsumerAcknowledgementObservation、HostContractVersion / AdapterRef、current-validity product query composition。

**Does not own**：Authorization / Approval；Knowledge Readiness / CitationLineage；Runtime / PlanVersion；Canonical Domain / AdmissionReceipt；Tool Effect；Model qualification / usage；外部 Host final display / adoption。

### B3 Upstream / Downstream

上游：用户、自有 UI、Generic Host、法院系统、batch/API clients、trusted identity providers。

下游消费：08 current Authorization / delivery policy；03 Readiness / Evidence / Citation；07 Model result for simple path；04 RunOutcome；02 DomainVersion / WorkProduct / invalidation / citation refs；06 Effect / Reconciliation for side-effect delivery；09 diagnosis/eval refs。

### B4 Authoritative Facts / Core Objects

ExternalRequestIdentity、NormalizedTask / TaskScopeContext、AgentDefinition、AgentVersion、InvocationIdentity / InvocationDecision、AnswerPublicationDecision、PublicationIdentity、DeliveryIdentity / DeliveryAttempt / DeliveryState、InvalidationDeliveryFact、ConsumerAcknowledgementObservation、HostContractVersion、AdapterRef。

### B5 Cross-boundary Contracts

#### InvocationDecision

绑定 normalized request / scope、AgentVersion、AuthorizationDecision ref、ReadinessDecision ref、必要 Capability / Model / Runtime routing facts，输出 `SIMPLE_PATH | NATIVE_RUNTIME | WAIT | REVIEW | REJECT` 等语义。01 不重新计算底层判断。

#### AnswerPublicationDecision

普通答案由 01 根据 AnswerPolicy、current Authorization、Readiness / citation / model result eligibility 组合。正式 WorkProduct 的 publication input 必须包含 02 matching AdmissionReceipt / WorkProductVersion / current validity。

#### Delivery / InvalidationDelivery

绑定 target system / endpoint contract、business object version、payload hash/schema、idempotency identity、attempts 和必要 06 action/effect refs。Invalidation delivery 不修改 02 invalidation truth。

#### ConsumerAcknowledgementObservation

只记录 Zuno 观察到的 remote ack / no-ack / remote correlation，不推断外部 internal adoption。

### B6 Normal Flow

**Simple QA**

```text
ExternalRequest
→ trusted identity + Scope normalization
→ 08 Authorization
→ 03 task-level Readiness / Retrieval
→ 07 controlled Model call
→ citation / answer eligibility
→ 01 AnswerPublicationDecision
→ typed response
```

**Complex WorkProduct**

```text
ExternalRequest
→ InvocationDecision
→ 04 AgentRun
→ optional 02 Formal Admission
→ matching WorkProductVersion / AdmissionReceipt
→ 01 publication / Delivery
→ later 02 invalidation
→ 01 invalidation push + pull validity
```

### B7 State / Lifecycle

```text
Request: RECEIVED → NORMALIZED → ACCEPTED / REJECTED / NEEDS_CLARIFICATION
Invocation: CREATED → ALLOWED_SIMPLE / ROUTED_RUNTIME / WAITING / REVIEW_REQUIRED / REJECTED → TERMINAL
Publication: DRAFT → ELIGIBLE → PUBLISHED / REJECTED / REVIEW_REQUIRED
Delivery: PENDING → IN_FLIGHT → SENT / FAILED / OUTCOME_UNKNOWN / RETRYING
InvalidationDelivery: PENDING → SENT / FAILED / RETRYING
ConsumerObservation: UNKNOWN → ACKNOWLEDGED / NO_ACK / ACK_INVALID
```

Domain `STALE` 不属于 Delivery lifecycle。

### B8 Failure Taxonomy

| 失败 | Owner / Detection | 01 动作 | Recovery anchor |
| --- | --- | --- | --- |
| principal / matter / scope 缺失 | 01 / 08 | reject / clarify | request identity |
| Authorization denied / expired | 08 | reject / wait | decision ref |
| Knowledge PARTIAL / BLOCKED | 03 | wait / explicitly narrow scope / reject formal route | ReadinessDecision |
| Model unavailable simple path | 07 | qualified fallback / review / fail | routing/attempt refs |
| Runtime failed / abstained | 04 | typed failure / review | RunOutcome |
| WorkProduct not admitted | 02 | 不作为 formal 发布 | AdmissionReceipt absence |
| publication evidence incomplete | 01 | DRAFT / REVIEW | publication identity |
| duplicate request | 01 | dedupe / return existing invocation | request/idempotency |
| response lost after accepted | 01 | replay lookup | invocation identity |
| Host contract drift | 01 | compatible adapter / explicit reject | HostContractVersion |
| Delivery known-not-sent | 01 / 06 if effectful | idempotent Retry | delivery/action identity |
| Delivery outcome unknown | 06 | Reconcile | Effect/Reconciliation refs |
| Consumer offline | 01 | keep pending / retry | DeliveryIdentity |
| invalidation notify failure | 01 | retry independently | InvalidationDeliveryFact |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

语义 / Scope 不清不 Retry。重复 transport request 使用 stable request idempotency；same key + same canonical task hash 返回同一 invocation，same key + different task hash 冲突。

Replan 属于 04。普通明确未发送 Delivery 可按 delivery identity Retry；现实 Effect outcome unknown 交 06 Reconcile。Recovery 优先读取 02 current validity / 06 Effect，再修复 01 Delivery projection。

### B10 Security / Approval / Audit

Intake、受保护结果发布、current-validity query、跨系统 Delivery 都消费当前 08 Decision。Host credential 使用受控 refs / Lease。高风险 Delivery 的 Approval / Mandatory Audit / Effect control 由 08 + 06 负责。

对外响应最小化 / 脱敏，不泄露 Secret、未授权 evidence 或 hidden chain-of-thought。

### B11 Persistence / Transaction Boundaries

External request / invocation 是否全量耐久化取决于恢复需要；异步长任务受理、Publication、Delivery、InvalidationDelivery、AckObservation 必须有足够持久化支持幂等恢复。

02 Domain transaction 不等待外部 Consumer。Outbox / Queue 可以服务 Delivery，但不拥有 Domain truth。01 与外部 Host 不默认 2PC。

### B12 Observability / Evaluation

至少观测 intake latency、scope clarification、simple/runtime routing、publication outcome、Delivery attempts / retries / unknown、Consumer ack lag、Host contract rejection、stale-result prevented、current-validity latency、duplicate suppression、outbox lag。

E2E Eval：Simple QA、Complex WorkProduct、new-evidence invalidation、Consumer offline、duplicate request、response loss、Host version drift、side-effect Delivery unknown、Authorization change before publication。

### B13 Current / Target / Gap / Evidence

**Current**：[`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md) 证明 Product Application Owner 已分离，主 Runtime path 不再由一个 Product God Facade 统一拥有；Current 仍不等于完整 publication/delivery/invalidation E2E。

**Target**：External Intake + Scope + AgentVersion + Invocation Composition + Publication + WorkProduct Delivery + Invalidation/Ack + Multi-Host Integration。

**Gap**：Simple QA Host E2E、Invocation / Publication qualification、push+pull invalidation、idempotent Delivery/outbox、Consumer offline fault、Host contract versioning、AgentVersion/PlanVersion compatibility、Effect handoff。

**状态**：detail design candidate available；production integration not established。

### B14 Code / Database / Migration Constraints

- 不建立 Application God Service。
- 通过 typed ports 消费各 Owner facts，不复制底层规则。
- 不要求 Zuno 自己拥有 UI/Login/Session/Conversation。
- 不把 AgentVersion 与 PlanVersion 放进同一生命周期。
- Outbox / Queue 不成为第二套 Domain truth。
- Host Adapter 只处理 transport/payload compatibility。
- 不默认微服务化；物理拆分受 ADR-0012 Evidence Gate。

#### B14.1 Detail Freeze Candidate：ExternalRequest / TaskScope 字段组

`ExternalRequest` candidate 至少包含 `external_request_id`、`request_idempotency_key`、`canonical_task_hash`、`host_ref / host_contract_version`、`trusted_identity_assertion_ref`、`principal_ref`、`tenant_ref`、可选 `matter_ref`、`desired_result_type`、`agent_version_ref`、`raw_input_ref / normalized_input_ref`、`received_at`。

`TaskScopeContext` 至少绑定 `scope_ref`、Matter / DocumentVersion selection、allowed result class、language / locale（如影响行为）、security scope refs、caller constraints、created_from_request`。Scope 变化形成新 scope ref，不原地扩大。

#### B14.2 Detail Freeze Candidate：Invocation 字段组与 Guard

`Invocation` 至少包含 `invocation_id`、request/scope/AgentVersion refs、route、AuthorizationDecision ref、ReadinessDecision ref、Capability/Model eligibility refs（如需要）、AgentRun ref（runtime path）、state、accepted_at/terminal_at、result_ref。

Guard：底层 refs 过期或不满足时不能由 01 改成 ALLOW；Simple path 必须证明无需 Native Runtime；正式复杂路径没有必要 Domain/Runtime capability 时不能假装降级完成。

#### B14.3 Detail Freeze Candidate：AgentDefinition / AgentVersion

AgentVersion 至少包含 `agent_id`、`agent_version`、`supported_task_classes`、`default_capability_profile_ref`、`model_role_profile_ref`、`runtime_profile_ref`、`answer_policy_ref`、`security_policy_profile_ref`、`compatibility_ref`、`activated_at / retired_at`。

已激活 AgentVersion 不原地改变影响行为的配置；新配置创建新 version。既有 AgentRun 继续绑定原 AgentVersion；与新 Runtime / Capability schema 不兼容时明确 drain / compatibility / Replan，不静默重绑定。

#### B14.4 Detail Freeze Candidate：Publication 字段组

`AnswerPublicationDecision` 至少绑定 `publication_id`、result/draft ref、request/invocation ref、AnswerPolicy ref、Authorization ref、Readiness/citation eligibility refs、Domain/Admission refs（formal result only）、decision/outcome、reason、decided_at。

普通 Answer Publication 与 Formal WorkProduct admission 分开。`PUBLISHED` 不能反向创造 DomainVersion；formal delivery 必须引用具体 WorkProductVersion 和 current-validity evidence。

#### B14.5 Detail Freeze Candidate：Delivery / Invalidation / Ack 字段组

Delivery 至少包含 `delivery_id`、publication/work_product/invalidation ref、target_system_ref`、HostContractVersion、payload_schema_version、payload_hash/ref、delivery_idempotency_key、state、attempt_no、next_retry_at、effect_action_ref（如 side-effecting）、remote_correlation_ref、last_error_class、created/updated_at。

AckObservation 至少包含 observation id、delivery ref、remote correlation、observed outcome、observed_at、raw ack hash/ref（必要时）。Ack 不升级成 remote adoption truth。

#### B14.6 Detail Freeze Candidate：Outbox / Crash / Idempotency

候选恢复链：同一 Application Store transaction 中形成需要可靠交付的 Publication/Delivery intent 与 outbox record；Worker at-least-once 消费，以 DeliveryIdentity/idempotency 去重。若真正发送属于现实副作用，06 的 PreparedAction / Effect truth 优先于 outbox ack。

| Crash Window | 恢复 | 禁止 |
| --- | --- | --- |
| request accepted 后 response 丢失 | request key 查既有 invocation | 启动第二个 Run |
| Runtime completed 后 publication 前 crash | 读取 RunOutcome + owner refs 重算 publication eligibility | 把 completed 直接发布 |
| Domain admitted 后 Delivery 前 crash | WorkProductVersion + durable Delivery intent 恢复 | 回滚 Domain |
| Delivery send 后 response lost | 06 Reconcile（effectful）或协议级查询 | blind resend |
| invalidation committed / consumer offline | retry push + pull validity stale | 恢复 Domain current |

#### B14.7 Detail Freeze Candidate：API / Host Contract / Schema Evolution

1. HostContractVersion 语义变化创建新版本；优先 additive compatibility。
2. 状态拆分 / renamed semantics 必须给旧消费者兼容映射或明确 unsupported，不用一个旧字段隐藏新语义。
3. request/task canonical hash algorithm version 化；历史 idempotency 按原算法解释。
4. AgentVersion 不因数据库 cleanup 重编号；旧 Run refs 可读。
5. Publication / Delivery payload schema 升级保留旧 WorkProductVersion 可重新解释，不重写历史正文。
6. Outbox schema migration 不丢 pending / unknown delivery；下线旧 Adapter 前完成 disposition。
7. 外部 API Migration 不能放宽内部 Security / Domain / Effect invariants。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

| 场景 | 必须证明 |
| --- | --- |
| Simple QA | 不进入 Native Runtime 也仍有 Authorization/Readiness/Citation/Publication 资格 |
| duplicate external request | 同 task hash 不启动第二 Run；不同 hash 冲突 |
| accepted request response loss | client replay 返回既有 invocation |
| Authorization revoked before publication | publication blocked / re-evaluated |
| Readiness becomes PARTIAL | 不冒充 full-scope answer |
| Runtime complete but Admission absent | formal WorkProduct 不发布 |
| Domain invalidated while consumer offline | pull stale；push 独立重试 |
| side-effect Delivery response lost | 06 Reconcile，不 blind retry |
| HostContractVersion mismatch | compatible adapter 或明确 reject |
| AgentVersion upgrade during active Run | old Run 仍绑定旧版本 |
| Delivery Worker duplicate | stable delivery idempotency 防重复 |
| Cancel after Domain/Effect exists | 不伪造全局 rollback |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

01 的 InvocationDecision 只证明调用组合；PublicationDecision 只证明 Zuno-side publication；Delivery / Ack 只证明 01 自己的交付 / 观察事实。它们都不能替代 Authorization、Readiness、Admission、Effect 或外部 Host adoption。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

Request → Scope → AgentVersion → Invocation → optional Run / Domain / Effect → Publication → Delivery 使用独立 identity / version refs 串联。新的 publication / delivery 前检查其所依赖 Owner facts 当前仍适用；request、invocation、delivery idempotency namespace 不共用。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

取消只停止未来可取消入口 / Run / Delivery 工作。已经成立的 Domain / Effect / Usage / sent Delivery 按各 Owner 继续解释。晚到 Run / Delivery / Ack 先匹配 causation 和 current validity，再更新 01 projection；stale WorkProduct 不因为旧 Ack 晚到而恢复有效。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
request / invocation / delivery durable identities
→ current 08 Authorization as required
→ 02 Domain / WorkProduct current validity
→ 04 RunOutcome / 06 Effect facts as applicable
→ repair Publication / Delivery / Invalidation projection
→ retry eligible transport work
→ 09 telemetry
```

一致性测试至少覆盖 duplicate request、response loss、simple-path no-runtime、publication security drift、Domain invalidation + offline consumer、Delivery outcome unknown、Host schema drift、AgentVersion upgrade 和 cancel after durable facts。