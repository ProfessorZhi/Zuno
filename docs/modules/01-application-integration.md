# 01 Application & Integration（应用与集成）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块首先解决“外部产品看到什么”，而不是“谁离用户近谁就拥有一切”

Zuno 可以被自己的 Web 页面、法院已有系统、通用 Agent Host、批处理任务或 API 客户端调用。外部调用方真正需要的是稳定产品语义：我提交了什么任务、当前能不能执行、结果是否可发布、正式成果是否仍有效、交付有没有完成。它没有必要理解九个责任域内部的所有状态机。

最容易出现的设计错误，是因为 Application 最靠近用户，就把授权、知识、Runtime、Domain 和外部 Effect 的状态全部复制成本地 `status`。短期看调用方便，长期却会出现两个模块都声称自己知道“真正状态”。所以 01 的价值不是成为万能业务层，而是把其他 Owner 已经成立的事实组合成对外一致的产品行为。

### 最简单的入口层为什么很快会遇到边界问题

最简单实现可以是一个 Controller：收到请求，调用几个服务，最后返回 `success=true`。简单同步问答完全可以这样工作。

当任务变成长流程以后，同一个 `success` 会同时混入“请求受理”“运行结束”“正式结果提交”“结果允许发布”“外部消费者已经看到”等不同含义。网络重试还可能重复启动任务，权限变化可能让旧结果失去发布资格，外部系统离线又会让交付状态与业务有效性分离。入口层如果不承认这些差异，就会把内部复杂性藏进一组越来越不可解释的布尔字段。

### 负责组合，不负责重新发明事实

01 的核心约束是：**负责组合，不负责重新发明事实**。它可以形成产品层的调用决定和发布决定，但这些决定必须引用当前授权、知识就绪、运行结果、正式准入或 Effect 回执，而不是重新计算另一套安全或业务真相。

例如，03 判断当前 Scope 只有部分关键材料可用，01 可以据此提示用户缩小范围、等待或拒绝完整分析；它不能为了“用户体验”把 PARTIAL 改写成 READY。04 表示 Run completed 时，01 也不能顺手推断正式 WorkProduct 已经存在。

### Scope 为什么必须先于 Agent 和模型

“帮我分析这个案件”不是一个足够稳定的系统输入。系统至少要知道事项、材料范围、目标结果和可信调用主体，否则后续授权、知识就绪、检索和正式准入都无法解释自己的适用范围。

01 因此先把外部输入归一化为稳定任务上下文。Scope 不足时应该请求补充，不让模型猜“用户大概指哪些材料”。如果用户后来扩大或缩小范围，这不是一个 UI 小变化，而是新的任务条件，下游 Readiness 和 Authorization 需要按新范围重新判断。

### 外部身份声明为什么不能直接升级成权限

Host 可以传 user id、tenant、role 或 matter，但这些字段只是 assertion。可信 principal 必须来自受验证会话、可信 Host assertion 或受控目录，再由 08 判断这个主体当前能做什么。

Application Adapter 可以负责认证协议和字段映射，却不能因为某个 Header 写着 `role=admin` 就提高权限。把“谁在请求”和“他现在能做什么”分开，才能让系统在多 Host、后台 Worker 和长任务恢复时仍保持一致安全语义。

### 简单问答为什么应该保持短路径

用户问“合同第 8 条写了什么”，如果 Scope 清楚、当前授权允许、所需材料已经就绪，系统只需要检索稳定原文、受控调用模型、校验引用和当前发布资格。

这类路径没有必要为了统一技术栈先构造动态 DAG。01 可以直接组合 08 的授权、03 的知识与引用、07 的模型结果，再形成 Zuno 侧普通答案发布决定。架构拥有 Runtime，不代表每个请求都必须使用 Runtime。

### 复杂任务为什么需要显式 Invocation，而不是一个巨大 if/else

复杂任务可能需要等待知识、进入 Native Runtime、调用专业能力、等待人工或最终产生正式 WorkProduct。入口层需要把这些条件组合成稳定的调用生命周期，让重复请求、取消、查询状态和结果交付都能引用同一次逻辑调用。

工程上可以把这个产品层决定表达为 InvocationDecision，但关键概念不是名字，而是：01 只决定“这次请求应走哪条产品路径”，不能替 03 重新判断知识资格，也不能替 08 判断授权，更不能替 02 正式准入。

### 四种“完成”为什么必须明确分开

外部 API 最容易把多个层次压成一个成功值，但 Zuno 必须保持：

```text
Run completed
!=
Domain admitted
!=
Answer publishable
!=
Consumer displayed
```

Runtime 完成说明控制流程结束；Domain admitted 说明正式法律业务事实成立；Answer publishable 说明 Zuno 当前允许把普通答案发布出去；Consumer displayed 则是外部 Host 自己的 UI 或采用事实。01 可以把这些事实组合给调用方，但不能让一个层次的完成替代另一个层次。

### 普通答案和正式 WorkProduct 为什么不能共用同一条发布权威

普通问答通常不需要进入正式领域状态。只要当前授权、材料就绪、引用和 AnswerPolicy 满足要求，01 可以形成普通答案发布决定。

正式 WorkProduct 不一样。它代表长期业务成果，必须先由 02 完成 Formal Admission，并拥有匹配的领域版本和准入证明。01 负责把正式版本发布或交付，但不能把 Runtime Draft 或模型文本包装成正式成果。

### Agent Version = 产品能力 / 配置版本

产品需要知道“当前这个 Agent 产品表面提供什么能力和默认配置”，这与某一次运行内部的计划版本不是同一个概念。Agent Version 可以绑定产品能力、Prompt / policy profile、默认 Runtime 策略和支持的任务类型。

PlanVersion 则属于 04 某一次具体运行。Agent 产品升级后，新请求可以使用新 Agent Version，正在运行的旧任务仍按自己已经绑定的版本解释；不能因为产品升级就在后台把旧 Plan 原地改掉。

### 新证据出现以后，为什么“失效”和“通知成功”必须分开

假设 WorkProduct V5 已经交付给法院系统，下午新 Evidence 进入后，02 判断 V5 需要复核。这个业务失效事实应该立即成立，不应等待外部系统在线。

01 的责任是把失效事实可靠地传播给已经接收 V5 的消费者，并提供 pull validity 查询。外部通知失败只表示传播仍在重试，不会把 Domain 中的 stale 重新变成 current。这样业务有效性不会被网络可用性绑架。

### 为什么 Push 和 Pull 都有价值

Push 能降低失效传播延迟，但消费者可能离线、队列可能积压、网络可能失败。如果系统只依赖 Push，就无法保证外部在真正使用成果时知道当前有效性。

因此 Target 同时保留 Pull validity。使用正式成果前，消费者可以查询当前版本状态。Push 负责尽快通知，Pull 负责最终可检查性，两者都只是传播机制，不改变 02 的业务真相。

### Delivery 为什么需要独立身份

同一个 WorkProduct 可以交付给多个外部系统，同一个目标也可能因为网络错误重复发送。如果只拿 WorkProduct id 当幂等 key，就无法区分“给 A”和“给 B”，也无法判断一次重试是否仍然是同一个逻辑交付。

01 因此需要稳定 Delivery identity，把目标、业务对象版本和 payload / contract 版本绑定起来。它保护的是产品交付语义，不意味着所有 Delivery 都由 01 自己执行现实副作用。

### 为什么有副作用的 Delivery 要交给 06

返回一个 HTTP response 和“在远端创建一条正式记录”不是同一种交付。后者会改变现实世界，一旦 timeout 就可能出现结果未知。

01 仍然拥有产品侧 Delivery 生命周期，但具体副作用要通过 06 的 Effect Control。01 消费 06 的执行和对账事实更新交付 observation，而不是自己写一个无限 retry loop 去猜远端到底发生了什么。

### Consumer Ack 为什么只能叫 Observation

远端返回 `ack=true` 最多证明 Zuno 观察到对方接收了请求或消息。它不一定证明远端内部业务流程已经最终采用，也不代表对方 UI 已经展示。

所以 01 可以保存 acknowledgement observation 和 remote correlation，却不能把外部系统内部 adoption truth 收编成本地事实。边界清楚以后，集成协议可以演进，而 Zuno 不需要控制远端实现才能保持自身一致。

### 重复请求为什么不应该启动第二个复杂 Run

浏览器重试、移动网络抖动和 API Gateway timeout 都可能让同一个逻辑请求重复到达。入口如果每次都新建 Run，会把一个用户动作放大成多个 Agent 运行，甚至重复正式交付。

request identity、logical invocation 和下游 Run identity 应分开。相同幂等身份和相同 canonical task input 可以返回已有 invocation；相同 key 却对应不同 task hash 应明确冲突。这样客户端在“提交成功但响应丢失”后可以安全重试。

### 取消为什么只是停止还能停止的未来工作

用户点击取消时，01 可以请求 04 停止未来计划工作，也可以停止尚未发出的 Delivery。但已经提交的 Domain transaction、已经确认的现实 Effect 或已经发送的外部消息不会因为本地 flag 自动消失。

因此取消响应要表达真实边界，例如“停止请求已接受，但已有不可撤销事实仍然存在”。如果业务需要补偿，补偿应该作为新的受控动作执行，而不是回写旧历史伪装成从未发生。

### Host Adapter、Backpressure 和 Contract Version 为什么属于产品边界

不同 Host 的字段、认证和同步 / 异步协议可以由 Adapter 转换，但 Adapter 只能解决兼容，不得改变 READY / PARTIAL、Draft / Formal、Authorization / Approval 等业务含义。

当 Runtime queue、知识构建、模型配额或外围系统过载时，01 也应该把背压显式暴露为 queued、deferred、rate-limited 等产品语义，而不是无限受理后统一超时。外部 Contract 需要版本化，使旧消费者不会把新状态按旧含义解析。

### 什么时候这个模块应该更简单

如果 Zuno 只作为内部库被一个单体应用调用，没有多 Host、异步交付、失效传播或复杂任务受理，那么 01 完全可以保持成很薄的 application layer。稳定产品语义不要求独立微服务，也不要求大型 Integration Platform。

只有外部协议、交付可靠性、Host 生命周期或吞吐隔离出现明确需求时，才值得增加 Adapter、Outbox、Queue 或独立部署。复杂度由集成问题驱动，不由“Application 模块应该很完整”驱动。

### 同步 API 和异步任务为什么要共享业务语义，而不是共享传输形态

同一个法律任务可能从 Web 同步请求进入，也可能由法院 Host 异步提交、随后轮询或接收回调。传输协议不同，不应该导致 READY、PARTIAL、Formal、Stale 等业务概念出现两套解释。

01 因此把协议适配和产品语义分开：Adapter 可以把 REST、消息或 Host SDK 统一成 canonical request；后续状态仍由相同 Owner facts 驱动。这样未来新增一个 Host 主要增加协议映射，而不是复制一套领域和安全规则。

同步接口也不应因为 HTTP 生命周期短就强迫复杂任务同步完成。真正需要长时间运行时，01 返回稳定 invocation identity，让客户端查询或订阅；简单问答仍可以直接返回。产品契约根据任务特征选择交互方式，而不是让传输机制反向决定内部架构。

### 发布决定为什么也需要新鲜度，而不能只在生成结束时判断一次

一个答案在生成完成时满足材料和安全要求，不代表几分钟后仍然允许发布。权限可能撤销，新 Evidence 可能让正式成果 stale，或者当前 consumer 的 Scope 已变化。

所以发布不是“生成完成后的固定副作用”，而是一个需要消费当前事实的边界。普通答案发布前重新确认当前安全和来源资格；正式 WorkProduct 则读取 02 的当前版本有效性。已经交付的历史不被改写，但新的下载、展示或继续使用可以被当前规则阻断。

这使 Application 层能够正确处理“结果存在但现在不该展示”的情况，而不是通过删除数据库结果来模拟权限变化。

### 为什么产品状态应该面向用户行动，而不是暴露内部状态机全集

内部可能同时存在 Run waiting、Knowledge partial、Approval pending、Delivery retrying 等状态。把这些原样全暴露给外部 Host，会让客户端绑定内部实现，未来任何模块演进都变成 API breaking change。

01 更适合组合成用户可行动的产品状态：等待材料、等待审批、正在处理、结果可查看、结果需复核、交付待确认等，同时保留诊断引用供受控排障。产品状态不是隐藏真实错误，而是把多个 Owner facts 翻译成稳定的消费者语义。

当调用方确实需要工程细节时，可以通过专门诊断接口查看 correlation 和 owner state，而不是让普通业务接口承担整个内部 observability schema。

### 多 Host 场景下为什么不能把一个消费者的确认当成全局完成

同一 WorkProduct 可能同时被 Web、法院业务系统和第三方归档服务消费。A 已经成功接收，并不能说明 B 也接收；B 离线也不应该让已经成立的 Domain WorkProduct 变回未完成。

因此 Delivery identity 与 consumer scope 一一绑定，01 记录每个目标的交付 observation，再按产品需求汇总。业务正式状态、发布资格和各消费者交付状态保持分层，才能支持“成果已成立，但某个下游仍在重试”的正常情况。

这也是为什么应用层的可靠性重点是可重复查询和可恢复传播，而不是制造一个跨所有消费者的全局提交事务。

### 01 的复杂度预算应该花在哪里

Application 层最容易膨胀，因为任何跨模块问题都可以被包装成“用户需要”。真正值得留在 01 的复杂度只应服务产品边界：稳定 request identity、Scope、对外状态、发布、交付和失效传播。

如果某段逻辑需要理解 Evidence 如何准入，应该回 02；如果需要理解索引覆盖，回 03；如果需要判断 Plan 是否可继续，回 04；如果需要确认外部 Effect，回 06；如果需要计算授权，回 08。把判断送回 Owner 看似多了一次调用，却避免 Application 成为第二套所有模块的影子实现。

### Application Projection 为什么可以缓存，但不能成为新的业务真相

产品为了快速展示，往往需要把多个 Owner 的状态组合成一个 read model：当前任务是否等待材料、结果是否可查看、哪个消费者还在重试。这样的 Projection 很有价值，但它本质上是可重建视图。

如果 Projection 落后，而 02 已经把 WorkProduct 标成 stale，01 不能继续因为本地 `status=READY` 就发布；如果 06 已经确认 Effect 成功，而 Delivery read model 还在 retrying，也应该由 owner fact 修复 Projection。性能优化可以让普通查询先读缓存，但在会产生新的受保护动作或强业务结论时，必须知道什么时候回查更强事实。

这给 01 一个重要恢复原则：自己的 read model 可以丢、可以重建、可以最终一致；真正不能丢的是 request / publication / delivery 中由 01 自己拥有的产品事实，以及它们引用的上游 Authority。

### API 兼容为什么不仅是字段能不能解析

新增一个 optional field 往往是 schema-compatible，但语义未必兼容。旧客户端如果把新的 `PARTIAL` 当成过去的 `READY`，或者把“交付已受理”理解成“远端已经采用”，即使 JSON 解析完全成功，业务仍然错误。

因此 Host Contract versioning 应保护状态含义、完成条件、错误分类和幂等语义，而不仅是字段形状。新增状态时要问旧消费者会怎样解释未知值；改变默认路径时要问重复请求是否仍指向同一 logical invocation；交付协议升级时要保留旧版本的可恢复性。

真正需要 breaking version 的，是消费者必须改变行为才能继续正确工作的语义变化。内部对象重命名或增加诊断字段则不应轻易升级成产品级 breaking change。

### 入口过载时为什么要拒绝、排队或降级，而不是无限接受

一个入口层如果只追求“请求都收到了”，很容易把容量问题转移成更难恢复的长队列。知识构建堵塞、模型 quota 耗尽、Runtime backlog 或外部法院系统不可用时，继续无界创建 Invocation 只会增加超时、重复请求和取消风暴。

01 应把 admission control 当成产品语义的一部分：哪些请求可以立即处理，哪些可以排队，哪些应该让客户端稍后重试，哪些简单任务可以走更短路径。不同 tenant / task class 还可能需要公平性和配额，避免一个批量任务耗尽所有交互式容量。

这里不要求 01 自研完整流量平台。成熟 Gateway、Queue 和限流器都可以复用；Zuno 自己需要定义的是过载时哪些业务承诺仍然成立，以及拒绝/排队不能绕过幂等、授权和 Scope 语义。

### 当前、目标与缺口

Current 只能回到 `docs/evidence/` 判断；这篇文档完整描述产品边界并不代表 Request ledger、Delivery store、Outbox、Host adapter 或 AgentVersion registry 已经实现。

Target 是让 01 稳定承担请求归一化、产品路径组合、普通答案发布、正式成果交付和失效传播，同时坚持消费其他 Owner facts 而不重新发明它们。Gap 仍包括字段级 Contract、实现、真实 Host 行为、吞吐与交付可靠性测量，以及哪些场景真正需要独立部署。

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