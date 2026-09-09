# 06 Tool Runtime & Effects（工具运行与外部效果）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块从一个最危险的问题开始：HTTP 超时以后，现实世界到底发生了什么

调用一个纯函数 timeout，通常重新计算就行；调用外围法院系统创建记录、提交材料或触发流程时，timeout 只说明本地没有拿到确定响应。远端可能没执行，也可能已经执行成功，只是响应丢了。

06 的存在，就是为了不把“网络调用状态”伪装成“现实效果状态”。它负责把一个准备执行的现实动作稳定下来，记录实际尝试，在结果未知时对账，并为上层提供能够证明当前 Effect truth 的耐久事实。

### 最简单的 try/except + Retry 为什么会制造重复副作用

常见实现是 `try POST; except timeout: retry`。如果第一次请求其实已经在远端成功，第二次就可能重复创建、重复提交或重复通知。

对只读、天然幂等操作这不是大问题；对高风险副作用，这是架构错误。系统必须先知道“这是不是同一个逻辑动作”“远端是否支持幂等”“第一次发送后是否可能已经生效”，再决定能不能重新执行。

### Transport Success 不等于 Effect Success

HTTP 200 只证明传输层观察到了一个成功响应，不必然证明远端业务效果已经满足 Zuno 期待；HTTP timeout 也不证明业务失败。

因此必须保持 `Transport Success 不等于 Effect Success`。06 记录尝试和远端证据，再把能够确认的现实效果表达成更强 Receipt，而不是让 status code 直接成为业务真相。

### 为什么先“准备动作”，再真的发送

模型或 Capability 产生的 Action Proposal 还可能缺少稳定参数、当前授权、审批、幂等身份和审计要求。直接把模型输出传进 SDK，会让“模型建议”和“系统决定执行”没有清楚边界。

Target 使用 Propose–Verify–Execute–Observe：先把动作规范化，校验目标、关键参数、ToolVersion、EffectClass、当前安全和恢复能力；通过后才形成稳定的 `PreparedAction`，随后进入真实 send boundary。

### PreparedAction 保护的是什么

PreparedAction 不是为了增加 DTO，而是冻结“系统这次究竟准备让现实世界发生什么”。如果 Replan 后参数或目标变化，就应该形成新的逻辑动作，而不是继续沿用旧审批和旧幂等身份。

稳定 action identity 使系统能把多次网络 Attempt 识别为同一个现实意图，也让审批、审计和后续 Reconcile 都能绑定同一件事。

### 幂等为什么既看 key，也看动作内容

只保存 idempotency key 会有一个危险漏洞：调用方误用同一个 key，却传入不同目标或参数，系统如果直接返回第一次结果，就会把业务冲突隐藏成成功。

因此 `same key + different action hash 必须拒绝`。同一个逻辑动作可以安全重放查询或返回既有结果，不同动作复用同一身份必须显式冲突。

### Send Boundary 为什么是恢复设计的关键切点

真正把请求交给远端之前，系统还能确定“现实动作尚未发生”；一旦越过 send boundary，进程崩溃或网络断开就可能失去确定结果。

因此发送前需要先耐久保存足够的 PreparedAction / Attempt identity 和必要安全证明。这样即使进程在发送后立即崩溃，恢复也知道应该对账哪个现实动作，而不是只能猜要不要重试。

### Outcome Unknown（结果未知）不得映射为普通 Failed

发送以后 timeout、连接断开或 Worker crash，都可能让本地无法判断远端结果。这种状态不是“失败”，而是证据不足。

所以 `Outcome Unknown（结果未知）不得映射为普通 Failed`。只要现实结果仍然未知，系统就不能自动开启一个全新的同类副作用；先进入 Reconciliation，确认 CONFIRMED、NOT_EXECUTED 或需要人工处理。

### Reconcile 到底在做什么

Reconcile 的目标不是“再执行一次”，而是查询过去的动作。优先使用远端幂等键、业务唯一键、查询 API、回执号或外部 correlation 确认结果；没有可靠机器接口时进入人工对账。

确认成功后形成 `EffectReceipt`；确认未执行后，才可能根据当前权限和计划决定是否再次执行；长期无法确认时保持未知并升级人工，而不是为了让流程结束强行选择成功或失败。

### Retry Safety 为什么必须按操作分类

GET、纯计算、远端原生幂等 PUT、带业务唯一键的创建、不可查询的高风险 POST，其安全重试条件完全不同。统一“最多重试三次”不能表达这些差异。

06 应根据 Tool operation 的 EffectClass、远端幂等能力、是否越过 send boundary 和当前结果证据决定 RetrySafe。这个分类属于 Tool/Effect 语义，不应该由通用 HTTP Client 猜。

### Authorization、Approval 和 Audit 为什么在执行前重新检查

动作从 Proposal 到真正发送之间可能等待很久，期间权限、Approval 有效期、SecurityEpoch 或审计策略都可能变化。旧 allow 不能成为永久通行证。

执行前 06 消费 08 的当前安全决定。高风险动作如果要求 `MANDATORY_BEFORE_EFFECT`，必须先确认耐久审计回执存在；普通 Trace 写成功不能替代这个前置条件。

### Compensation 为什么不是“把旧 Receipt 改成失败”

某些现实效果可以通过反向业务动作补偿，例如撤销一条可撤销记录。但补偿本身也是新的现实动作，可能失败、需要审批，也需要独立审计。

所以历史 EffectReceipt 保持“当时确实发生”，Compensation 形成新的 action / effect 因果链。修改旧历史来假装没发生，会破坏审计和恢复。

### Crash Window 为什么要围绕耐久事实设计

执行前 crash，可以根据已保存 PreparedAction 决定是否仍要发送；发送后未记结果 crash，需要 Reconcile；远端结果已确认但本地 Receipt 写失败，也要利用远端 correlation 恢复。

这些窗口说明 06 的状态不是为了“状态机完整”，而是为了让每一个不可逆边界都有可恢复锚点。没有锚点的状态名称再多也没有意义。

### Delivery 和 Tool Effect 为什么要协作而不是合并

01 负责产品交付生命周期，但某些 Delivery 本质上会在远端产生副作用。这时 01 不应该自己猜发送结果，而是把现实动作交给 06。

06 只返回 Effect truth 和对账事实，01 再更新 Delivery observation。这样“产品需要交付什么”和“现实世界实际发生什么”保持两个清楚 Owner。

### 模型为什么只能提出动作，不能批准自己

模型可以根据任务提出“应该调用某个 Tool”，但它不能决定自己是否有权限、审批是否有效或审计是否完成。否则 Prompt Injection 或模型错误会直接升级成现实副作用。

确定性 Tool schema、semantic validator、安全策略、Approval 和 send boundary 共同构成执行门。模型能力越强，这些边界越需要保持独立。

### 什么时候 06 可以很薄

如果 Tool 全部是只读、纯计算或远端明确提供强幂等和可查询结果，Effect Control 可以非常简单，甚至主要复用现成 SDK 和 retry policy。

只有不可逆副作用、结果未知、合规审批和外部系统弱一致性真正出现时，PreparedAction、Receipt 和 Reconciliation 才值得承担复杂度。不能因为“Tool Runtime 是模块”就给所有 GET 请求套完整 Saga。

### Exactly-once 为什么通常不是可以对外承诺的现实语义

在单数据库事务里可以通过唯一约束实现“只写一次”，但远端法院系统、邮件、第三方 API 等现实副作用通常没有和 Zuno 共享事务。请求可能重复、响应可能丢失、双方都可能崩溃，所以端到端绝对 exactly-once 很难证明。

更诚实的目标是 logical exactly-once intent：同一个逻辑动作有稳定身份，本地重复提交被压缩，远端如果支持 idempotency key 就复用；结果不确定时通过 Reconcile 确认。最终系统能够证明“我们没有盲目创造第二个逻辑动作”，而不是宣称网络世界不会重复任何包。

对不能提供幂等或查询能力的远端，高风险动作可能必须人工确认。这是外部约束带来的真实限制，不应该被一个漂亮的 SDK abstraction 隐藏。

### Effect Class 为什么应该影响默认策略

只读查询、可安全重放的更新、具有远端幂等键的创建、可补偿动作和不可逆高风险动作，其 retry / approval / audit 要求不同。如果全部走最强门禁，简单 Tool 成本过高；全部走最弱策略，高风险动作又不安全。

Tool operation 因此需要表达足以决定恢复策略的 EffectClass。分类不是为了枚举完整，而是让系统在发送前知道：是否允许自动 Retry、是否必须 Approval、outcome unknown 时是否有机器 Reconcile 路径、是否需要强制审计。

新增 Tool 时先声明这些行为，比先写 SDK wrapper 更重要。

### Remote Idempotency 为什么必须被验证而不是相信文档一句话

供应商说“支持 idempotency”仍需要确认 key 的作用域、有效期、参数冲突行为和查询能力。如果 key 只保存几分钟，而本地任务可能数小时后恢复，就不能把它当永久保证。

06 应把远端能力作为 ToolVersion 的一部分 qualification：重复相同 key 是否返回同一效果，不同 payload 是否拒绝，超时后能否通过 key 查询。证据不足时按更保守的 EffectClass 处理。

这样恢复策略建立在已验证行为上，而不是对 Provider 的乐观假设。

### Reconciliation 为什么需要明确终止条件

无限轮询远端不是恢复。对账应有 deadline、退避、最大自动尝试和人工升级路径。远端最终返回明确结果时收敛；长期不可查询时保持 unresolved，并阻止可能冲突的新动作。

人工对账也要留下结构化结果和责任人，而不是在聊天里说“应该成功了”然后手工改状态。最终 ReconciliationReceipt 表达系统通过什么证据把 unknown 收敛成什么结论。

这使最坏情况依然有业务闭环：可能变慢、需要人工，但不会用猜测换取状态机绿色。

### Compensation 为什么不能被当作事务 rollback

补偿动作常常不能恢复原世界。例如已经发送通知后再发撤回通知，接收者仍然看到过第一次消息；外部记录删除也可能留下审计历史。

所以 Saga / compensation 表达的是“采取新的业务动作减轻或纠正先前效果”，不是 ACID rollback。原 Effect 保持历史事实，补偿拥有自己的权限、Approval、Attempt 和 Receipt。

只有把这个差异写清楚，系统才不会在 UI 上把 compensated 显示成 never happened，也不会在审计中丢失真实因果。

### “已确认效果”为什么也不等于“远端所有业务语义都完成”

06 能证明的是 Zuno 关心的现实动作结果，例如某个创建请求对应远端记录已经存在、某个提交动作被目标系统接收。它不一定拥有远端系统内部更后续的审批、展示、归档或人工采用状态。

因此 EffectReceipt 需要清楚描述它证明的 Effect boundary，而不是使用含糊的 `SUCCESS` 让上层推断“对方全部处理完成”。如果产品还需要观察远端后续状态，应通过明确查询或 01 的 consumer observation 建模，而不是扩大 06 的权威范围。

这个限制也保护集成可替换性：Zuno 只承诺自己能够用 API、业务唯一键或回执证明的现实事实，不因为缺少对远端数据库的直接控制就伪造更强一致性。

### Tool Adapter 为什么不能吞掉远端的不确定性

SDK 或 Adapter 常常会把底层异常统一成一个漂亮的 `ToolError`。如果这个抽象把“请求尚未发送”“请求已发送但响应未知”“远端明确拒绝”全部合并，上层就失去了选择 Retry 或 Reconcile 所需的信息。

因此 Adapter 应保留影响 Effect truth 的最小传输事实，06 再根据 Tool semantics 判断恢复。抽象的目标是隐藏无关协议细节，不是隐藏决定正确性的故障窗口。一个好的 Tool abstraction 应该让调用方更难误重试，而不是让所有错误看起来一样简单。

### 人工对账为什么也必须重新进入结构化恢复链

有些外围系统没有稳定查询 API，自动 Reconcile 最终只能把案件交给人工确认。这里最危险的做法，是工程师在群里说“远端看起来成功了”，然后直接把本地状态手工改绿；这会让下一次恢复无法知道判断依据，也无法审计是谁确认了什么。

人工确认应该针对同一个稳定 action identity，记录查询到的远端证据、确认人、时间和结论，再形成可被 Runtime / Delivery 消费的结构化 reconciliation fact。人工只是替代机器完成“确认现实结果”这一动作，不改变 06 的 Effect truth 边界，也不能顺便批准新的副作用。这样即使自动化能力不足，恢复链仍然闭环而可解释。

### 幂等为什么解决不了两个“不同但冲突”的动作

Action identity 可以防止同一个逻辑动作因为网络重试被执行两次，但它不能阻止两个不同请求对同一远端资源产生冲突。例如两个 Run 分别认为自己应该提交不同版本，二者都有不同且合法的 idempotency key，仍可能在远端互相覆盖。

是否需要 resource version、业务唯一约束、串行化或远端 CAS，要由具体 Tool 语义决定。06 至少要在 Tool 语义中明确这种并发前提是否存在；具体由哪个字段或 Contract 表达留到 Detail Design，而不能把“我们有 idempotency key”误写成“所有并发都安全”。

这再次说明幂等是重复执行问题的一部分，不是分布式正确性的万能答案。

### Outcome Unknown 积压为什么本身就是一种运行风险

单个未知效果可以进入 Reconcile；如果外围系统长期故障，成百上千个 action 都停在 unknown，系统会积累大量“现实世界可能已经发生、也可能没有发生”的债务。此时继续产生新的冲突动作，会让后续对账越来越难。

因此 Reconciliation backlog 应影响新的执行决策：同一资源或同类高风险操作存在未收敛 effect 时，可以暂停冲突动作、降低自动化程度或升级人工。重点不是给 unknown 设置一个漂亮状态，而是限制不确定性继续扩散。

09 可以测量 unknown 数量、持续时间和人工负担；这些指标也能反过来判断某个外部系统是否适合继续自动化集成。

### 远端 API schema 没变，Effect 语义也可能已经漂移

外部 Provider 可能仍返回相同 JSON，却改变幂等窗口、异步处理方式、业务唯一键、错误码含义或“accepted”之后的真实流程。普通 contract test 可能全部通过，恢复假设却已经失效。

因此高风险 Tool 的 qualification 需要包含真正影响 retry / reconcile / confirmation 的行为，而不只检查 OpenAPI schema。发生语义漂移时，04 可能需要暂停相关 Plan，06 重新评估 RetrySafety，而不是靠 Adapter 把新错误翻译成旧枚举继续运行。

ToolVersion 的意义就在这里：版本保护的是现实动作语义和恢复假设，不只是 SDK 版本号。

### 自动化边界为什么应该受“可确认性”约束

一个 Tool 也许技术上能 POST，但如果执行后没有幂等键、查询 API、业务唯一标识，也没有可靠人工确认渠道，那么高风险动作自动化程度应该非常有限。能调用不等于能安全恢复。

因此在决定“要不要让 Agent 自动执行”之前，先问发生 timeout 后怎样确认；答案如果只能是“希望不会超时”，说明执行链还没有闭环。某些场景最成熟的设计反而是只生成 PreparedAction，让人或受控外部流程完成最终执行。

自动化价值应该和可恢复性一起衡量，而不是只比较操作节省了多少点击。

### 当前、目标与缺口

Current 是否已经实现 durable PreparedAction、send boundary、action hash、remote reconciliation 和强制审计集成，必须由代码和 fault-injection 证明；Target 文字不能代替运行证据。

Target 已明确 Proposal/Effect 分离、结果未知不可盲重试、幂等身份绑定动作内容、现实结果通过 Receipt / Reconciliation 收敛。Gap 包括具体 Tool 分类、远端幂等能力证据、crash-window 测试、人工对账流程、补偿策略和真实外围系统行为。

---

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
