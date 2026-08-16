# 01 Application & Integration（应用与集成）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么需要应用与集成这一层

Zuno 既可能直接向用户返回答案，也可能被法院已有系统、WorkBuddy、Dify 或其他通用 Agent 宿主调用。入口不同，不应该改变“法律事实由谁拥有”“材料是否可用由谁判断”这些内部规则；但谁负责接收请求、组合这些判断并把结果交回外部系统，必须有一个明确边界。

应用与集成解决的是“怎样把 Zuno 接进真实产品”，而不是重新做一遍安全、检索、法律判断或任务规划。

### 一个请求怎样经过这里

简单问答可以从入口确定事项和材料范围，消费安全与知识责任域已经给出的判断，检索原文并形成带依据的回答。应用与集成组合“现在是否允许调用”和“结果是否具备发布资格”，但不自己重算授权、材料就绪或引用正确性。

复杂任务则可能进入智能体运行与控制，最终形成候选结果或正式工作成果。应用与集成负责把结果交给调用者，并在 Zuno 自己承担发布责任时做最终的答案发布决定。

### 三种“发布”不能混在一起

这里至少有三个不同边界。

第一，**普通答案发布**回答“这段回答现在能不能由 Zuno 返回”。应用与集成消费权限、材料就绪、引用和结果资格后做组合决定。

第二，**正式工作成果准入**回答“这份结论是否已经成为长期法律业务事实”。这属于法律领域与工作成果，不由应用层决定。

第三，**外部宿主最终展示**回答“外部系统最终给用户展示什么”。如果 WorkBuddy、法院平台或其他宿主负责最终界面，Zuno 只能返回带资格、引用和策略依据的类型化结果，不能声称控制宿主的最终显示行为。

### Agent Definition / Version 放在哪里

应用与集成拥有 Agent Definition / Version 的产品表面：用户或宿主看到的是一个可调用、可版本化的产品 Agent，而不是底层某个 LangGraph 图或某个 Provider。它负责把产品定义映射到当前可用的知识、能力、模型和运行配置，但不把运行时内部 PlanVersion 冒充成产品 Agent 版本。

### 已发布结果失效时怎么办

假设昨天交付了一份工作成果，今天新证据使它失效。法律领域先确认“这个版本已经失效”；应用与集成随后负责把失效信息送给外部消费者，并记录通知是否送达以及是否观察到对方确认。

这三个事实不能压成一个状态：领域失效不等待外部系统在线；通知失败可以重试；没有收到确认也不能反推对方一定没有处理。

### 出问题以后怎么办

最常见的问题不是模型失败，而是边界和外部交付失败：请求没有明确事项或材料范围、外部系统仍使用旧 Contract、交付超时、消费者离线。入口信息不够时先补全范围；交付失败时使用稳定的交付身份幂等重试；消费者不可用时保留待交付状态，但不回滚已经成立的领域失效事实。

如果下游事实彼此冲突，例如安全授权已撤销但缓存仍显示旧资格，应用层不能自己“选一个看起来合理的”，而应拒绝组合、刷新权威事实或进入人工处理。

### 为什么值得独立成一个责任域

如果把这层塞进法律领域，领域模型会被 UI、Host 和协议细节污染；如果塞进运行时，简单问答也会被迫依赖复杂 Agent 执行。独立以后，Zuno 可以既作为完整产品运行，也可以只作为法律后端嵌入其他宿主。

### 当前、目标与缺口

Current Evidence 已能证明 Product API 存在分离的 Application Owner，例如 ProductService、ProductIngestionService、AgentRunApplicationService 和 ProductArtifactService；这说明入口组合和运行机制已经不是一个全能 Facade。完整发布资格、Agent Definition / Version 生命周期、失效交付、消费者确认和跨 Host 兼容仍属于 Target，不能宣称已经生产闭环。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：External Task Intake、Agent Definition / Version surface、InvocationDecision composition、Zuno-side Answer Publication、WorkProduct Delivery、Invalidation Delivery、Consumer Acknowledgement Observation、Host/Court Integration。

**Does not own**：Authorization truth、Knowledge Readiness、Canonical Domain State、Formal Admission、Runtime completion truth、Tool Effect truth、Model quality truth、external Host final display truth。

### B2 Inputs / Outputs

主要输入：请求与 Scope、AuthorizationDecision、ReadinessDecision、Capability / Model eligibility、RunOutcome 或直接回答结果、WorkProductVersion、Domain invalidation fact。

主要输出：InvocationDecision、Zuno-side AnswerPublicationDecision、typed result / eligibility evidence、delivery fact、consumer acknowledgement observation、Agent Definition / Version product mapping。

### B3 Cross-boundary Contracts

沿用总体架构和 ADR-0014：`InvocationDecision`、`AnswerPublicationDecision`、`WorkProductInvalidationFact` 的消费、`InvalidationDeliveryFact`、`ConsumerAcknowledgementObservation`。本骨架不新增字段级 Contract。

### B4 Publication Boundaries

必须区分：Zuno ordinary answer publication、Legal Domain formal WorkProduct admission、external Host final UI publication。三者不能共用一个 success/status 字段，也不能由 Application 重新推导 Domain 或 Host 的权威事实。

### B5 State / Lifecycle

至少区分请求组合状态、Agent product definition/version、发布状态、交付状态和消费者确认观测。Domain invalidation、Delivery、Acknowledgement 必须分别持久化和演进，不能复用一个 `WorkProduct.status`。

### B6 Failure / Recovery / Idempotency

- Scope 不完整：拒绝或补充，不让模型猜。
- 下游 eligibility 不成立或权威事实冲突：不执行/不发布，刷新或升级处理。
- Delivery 暂时失败：按稳定 delivery identity 重试。
- Consumer offline：保留交付状态；不阻塞领域失效。
- Host contract drift：兼容或拒绝，不自行重算领域事实。

### B7 Security / Persistence / Observability

每次新的受保护入口和发布行为消费当前授权与策略引用。交付状态和确认观测需要可恢复持久化；普通 Trace 只做关联，不代替发布或交付事实。

### B8 Current / Target / Gap

Current 证据见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md)。Target 是完整的 Invocation / Publication / Delivery / Agent Product Surface 边界。Gap 是跨 Host E2E、Agent Definition / Version 生命周期、失效推送/查询、幂等交付和消费者确认故障测试。

### B9 Code / Database / Migration Constraints

本设计不授权新增 God Service，不要求独立微服务，也不冻结表名或 API。后续实现必须复用其他责任域给出的权威决定，而不是在 Application 层复制安全、知识、运行或领域规则。
