# 01 Application & Integration（应用与集成）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么需要应用与集成这一层

Zuno 既可能直接向用户返回答案，也可能被法院已有系统、WorkBuddy、Dify 或其他通用 Agent 宿主调用。入口不同，不应该改变“法律事实由谁拥有”“材料是否可用由谁判断”这些内部规则；但谁负责接收请求、组合这些判断并把结果交回外部系统，必须有一个明确边界。

应用与集成就是这个边界。它解决的是“怎样把 Zuno 接进真实产品”，而不是重新做一遍安全、检索、法律判断或任务规划。

### 一个请求怎样经过这里

简单问答可以直接从入口确认范围和权限，等待材料达到可回答条件，检索原文并生成带依据的结果。应用与集成消费安全、知识和模型等责任域已经给出的判断，组合出“现在能不能执行”和“这个结果能不能由 Zuno 发布”。它不自己重算这些事实。

复杂任务则可能进入智能体运行与控制，最后产生候选结果或正式工作成果。应用与集成负责把结果交回调用者，并在 Zuno 自己负责发布时执行最终发布决定。如果最终展示发生在外部通用宿主中，宿主仍拥有最终界面和展示控制，Zuno 只能返回带资格、引用和策略依据的类型化结果。

### 已发布结果失效时怎么办

假设昨天交付了一份工作成果，今天新证据使它失效。法律领域先确认“这个版本已经失效”；应用与集成随后负责把失效消息送给外部消费者，并记录通知是否送达以及是否观察到对方确认。

这三个事实不能压成一个状态：领域失效不等待外部系统在线；通知失败可以重试；没有收到确认也不能反推对方一定没有处理。

### 它负责什么，不负责什么

它负责请求入口、任务范围组合、Agent Definition / Version 的产品表面、调用决定组合、Zuno 侧答案发布、工作成果交付、失效通知和消费者确认观测。它也负责法院系统和通用宿主的适配边界。

它不要求自己拥有 UI、登录、会话或聊天产品；这些可以由外部宿主负责。它也不能自己批准权限、判断材料已经就绪、修改正式法律事实、宣布外部动作成功，或因为某个 HTTP 调用成功就认为业务已经完成。

### 出问题以后怎么办

最常见的问题不是模型失败，而是“边界不清”：请求没有明确事项或材料范围、外部系统使用了旧 Contract、交付超时、消费者离线。入口信息不够时先补全范围；交付失败时使用稳定的交付身份幂等重试；消费者不可用时保留待交付状态，但不回滚已经成立的领域失效事实。

### 为什么值得独立成一个责任域

如果把这层塞进法律领域，领域模型就会被 UI、Host 和协议细节污染；如果塞进运行时，简单问答也会被迫依赖复杂 Agent 执行。把它单独划出后，Zuno 可以既作为完整产品运行，也可以只提供法律后端能力。

### 当前、目标与缺口

Current Evidence 已能证明 Product API 存在分离的 Application Owner，例如 ProductService、ProductIngestionService、AgentRunApplicationService 和 ProductArtifactService；这说明“入口组合”和“运行机制”已经不是一个全能 Facade。完整的发布资格、失效交付、消费者确认和外部 Host 兼容仍属于 Target，不能宣称已经生产闭环。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：External Task Intake、Agent Definition / Version surface、InvocationDecision composition、Zuno-side Answer Publication、WorkProduct Delivery、Invalidation Delivery、Consumer Acknowledgement Observation、Host/Court Integration。

**Does not own**：Authorization truth、Knowledge Readiness、Canonical Domain State、Runtime completion truth、Tool Effect truth、Model quality truth。

### B2 Inputs / Outputs

主要输入：请求与 Scope、AuthorizationDecision、ReadinessDecision、Capability / Model eligibility、RunOutcome 或直接回答结果、WorkProductVersion、Domain invalidation fact。

主要输出：InvocationDecision、Zuno-side AnswerPublicationDecision、typed result / eligibility evidence、delivery fact、consumer acknowledgement observation。

### B3 Cross-boundary Contracts

沿用总体架构和 ADR-0014：`InvocationDecision`、`AnswerPublicationDecision`、`WorkProductInvalidationFact` 的消费、`InvalidationDeliveryFact`、`ConsumerAcknowledgementObservation`。本骨架不新增字段级 Contract。

### B4 State / Lifecycle

至少区分请求组合状态、发布状态、交付状态和消费者确认观测。Domain invalidation、Delivery、Acknowledgement 必须分别持久化和演进，不能复用一个 `WorkProduct.status`。

### B5 Failure / Recovery / Idempotency

- Scope 不完整：拒绝或补充，不让模型猜。
- 下游 eligibility 不成立：不执行或不发布。
- Delivery 暂时失败：按稳定 delivery identity 重试。
- Consumer offline：保留交付状态；不阻塞领域失效。
- Host contract drift：兼容或拒绝，不自行重算领域事实。

### B6 Security / Persistence / Observability

每次新的受保护入口和发布行为消费当前授权与策略引用。交付状态和确认观测需要可恢复持久化；普通 Trace 只做关联，不代替发布或交付事实。

### B7 Current / Target / Gap

Current 证据见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md)。Target 是完整的 Invocation / Publication / Delivery 边界。Gap 是跨 Host E2E、失效推送/查询、幂等交付和消费者确认故障测试。

### B8 Code / Database / Migration Constraints

本设计不授权新增 God Service，不要求独立微服务，也不冻结表名或 API。后续实现必须复用其他责任域给出的权威决定，而不是在 Application 层复制安全、知识或领域规则。
