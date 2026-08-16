# 01 Application & Integration（应用与集成）

<!-- status: design-baseline-v1; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么需要应用与集成这一层

Zuno 既可能自己面向用户，也可能被法院已有系统、WorkBuddy、Dify 或其他通用 Agent 宿主调用。入口不同，不应该改变“法律事实由谁拥有”“材料是否已经可用”“当前权限是否允许”这些内部规则；但谁负责接收请求、组合这些判断并把结果交回调用者，必须有一个稳定边界。

应用与集成解决的是“怎样把 Zuno 放进真实产品和现有系统”，而不是重新做一遍安全、检索、法律判断或任务规划。它是产品入口与内部责任域之间的协调层，也是 Zuno 对外承担发布和交付责任的位置。

### 简单问答和复杂任务怎样经过这里

简单问答可以很短：入口确认事项、材料范围和用户意图，消费安全与治理给出的授权结果，等待知识与证据确认材料具备用于当前问题的条件，随后完成检索和受控模型生成。应用与集成最后组合“这个请求能不能执行”和“这个答案现在能不能由 Zuno 返回”，而不是自己重新判断权限或重新计算检索质量。

复杂任务可能进入智能体运行与控制，由运行时组织专业能力、模型和工具。即便如此，运行完成也不自动等于结果可以发布。应用与集成仍需要读取 `RunOutcome`、领域版本、证据和策略引用，形成 Zuno 侧的发布决定；如果最终展示发生在外部宿主中，Zuno 只能返回带资格、引用和策略依据的类型化结果，最终界面和展示行为仍由外部宿主负责。

### 三种“发布成功”不能混成一个状态

这里最容易产生误解的是“发布”。至少要区分三件事。

第一，普通答案是否可以由 Zuno 返回，这是应用与集成的答案发布问题。第二，一份 `WorkProduct`（工作成果）是否已经成为正式法律业务事实，这是法律领域的正式准入问题。第三，如果 Zuno 被嵌入外部平台，最终页面是否真的展示给用户，是外部宿主自己的产品行为。

因此 HTTP 200、运行时 completed、工作成果正式准入和外部页面展示，不能共用一个 `success=true`。

### Agent 版本和某次运行计划也不是一回事

应用与集成拥有 `Agent Definition / Version` 的产品表面：一个产品 Agent 对外声明什么能力、默认策略和允许范围。某次复杂运行内部使用的 `PlanVersion` 则属于运行与控制。升级一个 Agent 版本不应该偷偷改写已经激活的运行计划，运行时重规划也不应该反向改写产品 Agent 定义。

这个区分让“产品发布了哪个 Agent 版本”和“这一轮任务执行了哪一版计划”都能被独立追溯。

### 已经交付的结果失效时怎么办

假设昨天向法院系统交付了工作成果 V5，今天新证据使它失效。法律领域先确认“V5 已失效或需要复核”；应用与集成随后负责把这件事通知外部消费者，并记录通知是否发送、是否失败重试，以及是否观察到对方确认。

这里有三个事实：领域结果已经失效、通知是否送达、外部消费者是否确认。消费者离线不能阻塞领域失效成立，通知发送成功也不能证明对方已经更新自己的内部认知。目标形态同时支持主动失效推送和外部系统按需查询当前有效性。

### 出问题以后怎样恢复

这个模块最常见的问题不是模型失败，而是边界信息和外部交付失败。请求缺少事项或材料范围时，应补充或拒绝，而不是让模型猜；调用资格已经失效时，不启动或不继续发布；外部交付暂时失败时，使用稳定的交付身份幂等重试；消费者长期离线时保留交付状态，但不回滚已经成立的领域事实。

如果外部接口版本漂移，适配层可以兼容旧版本或明确拒绝，但不能为了“让接口继续工作”自行重算安全、知识或领域规则。对外兼容的代价应该留在适配边界，而不是污染内部事实所有权。

### 为什么值得独立成一个责任域

把这层塞进法律领域，领域模型会被 UI、Host、HTTP 和交付协议污染；把它塞进运行时，简单问答也会被迫依赖复杂 Agent 执行；让每个 Provider 自己负责发布，又会出现互相冲突的资格判断。

独立的应用与集成边界允许 Zuno 既作为完整产品运行，也可以只提供法律后端能力。它保护的是产品组合和发布责任，而不是一个新的“万能服务”。

### 当前、目标与缺口

Current Evidence 能证明 Product API 已存在分离的 Application Owner，例如 `ProductService`、`ProductIngestionService`、`AgentRunApplicationService` 和 `ProductArtifactService`，说明入口组合和运行机制已经不是一个单一 Facade。完整的 `InvocationDecision`、答案发布资格、失效交付、消费者确认、跨 Host 兼容和交付故障恢复仍是 Target，不能宣称已经生产闭环。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

本模块负责外部请求进入 Zuno 后的组合、Zuno 侧发布、工作成果交付和外部消费者适配。它必须遵守：不重新计算其他模块的权威事实；简单问答不因统一入口被强制送入原生运行时；外部 Host 的最终 UI / 展示不由 Zuno 冒充拥有。

### B2 Responsibility / Ownership

**Owns**：External Task Intake、Agent Definition / Version surface、InvocationDecision composition、Zuno-side Answer Publication、WorkProduct Delivery、Invalidation Delivery、Consumer Acknowledgement Observation、Host / Court Integration。

**Does not own**：Authorization truth、Knowledge Readiness、Canonical Domain State、Runtime completion truth、Tool Effect truth、Model provider eligibility truth、外部 Host 内部展示事实。

### B3 Upstream / Downstream

上游包括用户、法院系统和通用宿主。下游主要消费 08 的授权与策略、03 的就绪和证据资格、07 的模型资格与结果、04 的运行结果、02 的领域版本 / 工作成果 / 失效事实，以及必要时 06 的效果回执。

它向外部调用者输出类型化答案、资格证据、引用、策略引用、工作成果版本、交付状态和当前有效性信息。

### B4 Authoritative Facts / Core Objects

核心事实族包括：请求范围与调用上下文、Agent Definition / Version、调用决定、答案发布决定、交付状态、失效通知状态和消费者确认观测。`PlanVersion`、`WorkProduct` 正式状态和授权决定均只是引用，不在本模块复制为第二套真相。

### B5 Cross-boundary Contracts

沿用总体架构和 ADR-0014：`InvocationDecision`、`AnswerPublicationDecision`、`WorkProductInvalidationFact` 的消费、`InvalidationDeliveryFact`、`ConsumerAcknowledgementObservation`。Agent Definition / Version 对运行时只提供稳定产品配置引用，不直接修改激活中的 `PlanVersion`。

### B6 Normal Flow

简单问答：intake → scope normalization → current authorization → knowledge readiness / retrieval → model result → answer eligibility → Zuno publication。

复杂任务：intake → invocation composition → runtime / domain work → consume RunOutcome and domain evidence → publication decision → deliver typed result / WorkProduct → optional invalidation delivery later。

### B7 State / Lifecycle

至少区分：请求组合状态、调用决定、答案发布状态、工作成果交付状态、失效通知状态、消费者确认观测。Domain invalidation、Delivery、Acknowledgement 必须分别演进，不能复用一个 `WorkProduct.status`。

Agent Definition / Version 具有自己的产品生命周期；运行中的 PlanVersion 一旦激活，后续产品版本变化不反向篡改该运行事实。

### B8 Failure Taxonomy

主要失败包括：Scope 不完整、身份或租户上下文缺失、下游资格不成立、Host Contract drift、发布决定缺少必要证据、交付超时、重复交付、消费者离线、失效通知长期失败。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Scope 不完整属于拒绝或补充，不是 Retry。Delivery 暂时失败可按稳定 `delivery_identity` 重试；同一交付身份必须幂等。外部消费者离线不触发领域回滚。若交付本身具有现实副作用且结果未知，必须交给 06 的 effect / reconciliation 语义，不能在 Application 层盲目重发。

### B10 Security / Approval / Audit

请求进入、受保护结果发布、跨系统交付都消费当前安全决定。应用层不能缓存过期授权为永久通行证，也不直接持有长期秘密。需要审批的现实动作由 08 和 06 约束，Application 只组合其结果。

### B11 Persistence / Transaction Boundaries

请求、发布和交付是否需要持久化按恢复需求决定；失效交付和确认观测需要可恢复保存。Domain transaction 不等待远端 Consumer。目标实现可以使用 Outbox / delivery queue，但 Outbox 只是交付机制，不拥有领域失效事实。

### B12 Observability / Evaluation

至少观测 intake latency、decision latency、publication outcome、delivery retry、consumer acknowledgement lag、Host contract rejection 和 stale-result delivery。Trace 关联 request / run / WorkProduct / delivery identity，但不替代发布和交付事实。

### B13 Current / Target / Gap / Evidence

Current 证据见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md) 和现有 Product API。Target 是完整 Invocation / Publication / Delivery / Host Compatibility 边界。Gap 包括跨 Host E2E、答案资格故障测试、失效 push + pull、幂等交付、消费者离线和 Agent Version / PlanVersion 兼容验证。

### B14 Code / Database / Migration Constraints

不授权新增 God Service，不要求独立微服务或独立数据库。后续代码必须通过 typed ports 消费其他责任域的决定，不在 Application 层复制安全、知识、领域和工具规则。数据库表、Outbox 结构、API 路径和 Host adapter 只有在详细设计和兼容性测试后冻结。
