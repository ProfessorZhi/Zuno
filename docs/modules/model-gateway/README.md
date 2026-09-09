# 07 Model Gateway（模型网关）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 模型调用需要成为受控依赖，而不是散落的 SDK 调用

Zuno 会在规划、改写、抽取、专业分析、批评和综合等位置调用模型。如果每个模块直接使用不同 Provider SDK，短期最方便，长期却无法统一解释为什么选这个模型、当前数据能不能外发、失败以后能不能切换、实际花了多少预算，以及取消后是否仍产生费用。

07 因此统一的是调用边界和事实：上层表达自己需要哪类模型能力和约束，Gateway 选择当前合格 Provider / Model，记录真实 Attempt 与 Usage，再把 typed result 返回调用方。具体业务 Prompt 和专业语义仍属于使用它的模块。

**贯穿这一篇的不是“怎么做一个通用 Model Gateway”，而是一条法律任务中的模型选择链。** Planner 可能需要强推理，Query Rewrite 更重视速度，结构化抽取可能适合小模型；同一份案件材料又可能只允许发给特定地域或特定 Provider。07 的价值，就是让这些调用在不泄漏业务 Authority 的前提下，仍然能解释为什么选这个模型、花了多少、失败后能否切换，以及切换以后还是否合格。


Provider SDK 接入通常只有几十行代码，所以一开始分散调用看起来没有问题。随着模型数量增加，每个模块都会自己实现 timeout、fallback、token 统计、地域限制和 Secret 处理，最后相同问题出现多套答案。

更危险的是业务代码开始直接写某个模型名。模型升级或 Provider 下线时，Planner、Extractor 和 Query Rewriter 都要一起改，模型能力和业务语义产生不必要耦合。

### Model Role 与具体 Provider / Model 解耦

Planner 需要复杂规划能力，Query Rewriter 更关心速度和成本，Extractor 关心结构化输出。上层真正依赖的是任务角色，而不是某个厂商的 SKU。

因此保持 `Model Role 与具体 Provider / Model 解耦`。Role 是稳定语义，实际 Provider / Model 由当前资格、数据政策、预算、延迟和质量要求选择。这样模型供应变化不会迫使业务代码重新定义自己的职责。

### Provider 资格与模型输出都必须服从当前任务边界

API health 绿色只证明技术可调用。当前材料可能因为地域、合同或数据分类禁止外发；某个模型可能没通过当前 Role 的质量基线；预算或配额也可能已经不足。

所以必须保持：

```text
Provider technically available != currently permitted != quality qualified
```

07 只能在安全允许和质量合格的集合中做路由。Fallback 也不能以“API 兼容”为理由越过这些门槛。


模型即使结构正确、置信度很高，也不能自己修改 Domain、批准权限、激活高风险 Tool 或把长期 Memory 写成正式事实。模型适合产生建议、抽取、判断和 Critique，不拥有这些更强业务权威。

07 只证明“这次模型调用发生了什么、返回了什么”。结果是否满足专业语义由 05 / 04 验收，是否进入正式 Domain 由 02 决定，是否允许现实执行由 08 / 06 决定。


Provider 返回 200 和合法 JSON，只说明 transport / model attempt 成功。Capability 可能认为内容不满足专业契约，Runtime Step 可能拒绝，Domain 更可能因为证据不足不准入。

所以保持：`Gateway 调用成功 != Runtime Step accepted != Domain admitted != Answer published`。07 越是稳定地记录自己的事实，越不需要假装拥有更强成功。

### Routing 在质量、安全、预算和延迟之间做受约束选择

复杂规划、关键 Reflection 或高风险综合可能从更强推理模型获益；Query Rewrite、分类、格式转换和简单抽取通常更适合快而便宜的模型。

这不是固定的“模型等级表”。09 应通过 Role 级 Eval 证明升级是否带来足够收益；如果质量没有明显改善，贵模型不应因为品牌或参数规模自动成为默认。

---

**前面先把 Role、Provider 和上层业务语义拆开；现在才进入真正的路由问题。** 路由不是“选当前最强模型”，而是在当前允许集合里做一个可解释的质量 / 安全 / 预算 / deadline 决定。


单纯按价格最低路由会牺牲质量，单纯按 benchmark 最高路由会忽略数据政策和成本。Gateway 的路由是多约束选择：当前 Role 需要什么、哪些 Provider 被允许、哪些已经通过资格、预算和 deadline 是否还能承担。

RoutingDecision 只是对这些约束的调用层组合。08 仍然拥有数据外发和 Credential policy，09 仍然拥有长期 Eval，07 不应重新发明它们。

### Retry、Fallback、Cancellation 与 Deadline 共同形成调用生命周期

模型 503、连接抖动或格式暂时错误，可以做有限 Retry；某个 Provider 长时间不可用时，可以切换到当前同样合格的 fallback。

但 fallback 不是无限降低质量的逃生通道。没有满足 Role 最低要求的替代模型时，正确结果可能是让上层 Replan、Review 或 abstain。Budget、deadline 和安全约束始终限制失败链的放大。


如果每次 Retry 或 fallback 都重新拿一份预算，一次坏请求可以悄悄消耗多倍 token 和费用。实际发生过的 Provider 调用都应该计入 Usage，即使最终结果没有被采用。

07 记录 reservation / estimate / settled usage，04 用这些事实更新 Run Budget。成本事实不会因为 Step 后来失败而消失。


调用方请求取消时，Provider 可能已经完成、正在生成，也可能根本不支持可靠取消。`CANCEL_REQUESTED` 只说明本地意图，不能推断费用为零或远端停止。

Gateway 应区分 provider-confirmed cancelled、completed-before-cancel 和 cancel / billing unknown，并在需要时继续 settlement。取消控制未来等待，不改写已经发生的资源事实。


Provider A timeout 后启动 B，A 的响应可能稍后到达。如果系统只保存“最终模型结果”，就会丢失 A 的真实调用和费用，也无法解释两个结果谁先产生。

每次实际调用保持独立 Attempt identity 和 Usage。04 / 05 决定晚到结果当前是否仍有资格被接受，07 只保证调用历史不被覆盖。

### Prompt、Structured Output、Cache 与 Secret 各有自己的 Owner

Gateway 统一 transport、provider formatting、通用 safety wrapper 和 request schema，但 Planner Prompt 的业务语义属于 04，专业抽取 Prompt 属于 05，对外回答 Prompt 可能属于产品或相应 Capability。

把所有 Prompt 收进 Gateway 会让它成为 God Repository，也让业务语义和 Provider adapter 混在一起。统一调用不等于统一拥有所有 Prompt。


07 可以检查 JSON、schema 和 Provider structured-output 协议是否满足；但字段完整不代表专业内容正确。05 / 04 还需要做语义验收。

把 transport/schema success 与 semantic success 分开以后，Gateway 可以稳定解决 Provider 差异，而不会把法律专业规则塞进 SDK Adapter。


同一 prompt 在模型版本、temperature、provider backend 或时间变化时可能返回不同结果。只有调用方明确允许、任务对差异可接受时，才适合缓存或 duplicate suppression。

cache identity 需要绑定 Role、模型版本、prompt/input hash、generation config、schema 和必要安全 Scope。缓存复用后，上层仍然要做当前业务新鲜度判断。

---

**模型路由一旦稳定，下一层风险来自“调用本身携带了什么”。** API Key 和案件材料都敏感，但前者是 Credential，后者受数据外发政策约束；把两者混成一个 Gateway 配置问题，会让 fallback 变成绕过安全边界的捷径。


API Key 是 Secret，Prompt 中的案件材料是受保护业务数据。Secret 应通过受控引用和短期 Lease 使用，不能进入 Prompt、普通日志或 Checkpoint；业务数据能否外发则由 08 的数据政策决定。

07 消费 Credential ref 和 egress decision，执行允许的模型调用。它不能因为 Provider fallback 方便就扩大外发范围。

---

**到这里先收束一次边界本身。** 逻辑上统一模型调用，不等于物理上必须多一次网络跳；如果没有 Secret isolation、独立吞吐、网络出口或部署生命周期证据，07 应继续是薄的模块边界，而不是为了“AI Infra 完整”自造平台。

### Gateway 默认是逻辑责任，版本漂移和 Provider 差异由治理吸收

把 Provider SDK 集中到一个逻辑边界，不自动要求增加一次网络跳转。默认可以作为模块化 backend / worker 中的 adapter 和 service 实现。

只有 Secret isolation、独立吞吐扩缩、网络出口、合规边界或部署生命周期出现明确证据时，才值得拆成服务。逻辑统一比服务数量更重要。


Provider 可以保持同一个 REST schema，却在底层模型升级后改变规划长度、抽取偏好、工具调用方式或拒答行为。对上层来说，这种 behavioral drift 可能比 API breaking change 更危险，因为它不一定触发编译错误。

因此 ModelVersion / qualification 要能标识真正影响行为的版本，关键 Role 在升级前后做回归。若 Provider 不提供稳定模型快照，系统至少记录可获得的版本标识和调用时间，并通过 Eval 监控漂移，而不是假设相同 model name 永远等价。

Gateway 不应该用隐蔽后处理强行把新行为伪装成旧行为；上层假设失效时应明确调整 Prompt、Capability 或 Plan。


如果每个请求都根据瞬时价格、延迟或 benchmark 在多个模型间频繁切换，同一任务不同 Step 的行为可能不可预测，排障和评测也难以重现。

对需要一致性的长 Run，可以在开始时绑定允许的 routing profile / model family，在明确故障或 Replan 时再切换。对普通独立请求则可以更灵活地动态路由。稳定性和优化程度需要按任务权衡。

这说明路由目标不是单一最优函数，而是在质量、安全、成本、延迟和可复现性之间选择可解释策略。


一个强模型可能质量最好，但预计响应时间已经超过用户 deadline；一个便宜模型虽然快，却不满足最低质量。Gateway 需要把可用候选限制在同时满足 quality floor、security、quota 和时间预算的集合。

如果没有任何候选满足，正确结果不是一定找个模型调用，而是向上层报告不可满足，让 Runtime 调整计划、缩小任务或进入人工处理。路由层不应该通过偷偷放宽质量和安全条件来提高“成功率”。


Query rewrite Provider 故障时，可以直接使用原 query 或更简单 deterministic 规则；Planner 强模型故障时，简单任务也许退回固定 Plan；关键 legal synthesis 如果没有合格 fallback，则可能必须等待或 Review。

因此 degraded mode 与 Role 绑定，而不是 Gateway 统一写“主模型失败就用备用模型”。这种差异让系统可以安全少做，而不是在关键任务上无条件降质。


即使 prompt hash 相同，不同 tenant、matter、SecurityEpoch 或数据生命周期可能不允许共享响应。跨用户全局 cache 可以非常省钱，也可能成为数据泄露通道。

只有输入可公开共享、调用方明确允许且安全 Scope 相容时才适合复用。敏感法律任务默认把 tenant / matter / policy scope 纳入 identity，或者直接关闭响应缓存。成本优化不能扩大数据可见范围。


模型调用已经发出后，即使上层后来取消 Run、拒绝结果或 Replan，Provider 仍可能已经消耗 token 并产生费用。只在“最终采用结果”上记成本，会系统性低估失败链和 fallback 的真实代价。

因此每个 Attempt 的 Usage 应独立 settlement，再沿 causation 归因到 Run / Step。这样 04 可以看见当前 Budget 还剩多少，09 也能回答一次 Reflection、Planner retry 或 Provider fallback 到底放大了多少成本。

Usage 同时帮助解释取消边界：本地 cancel 并不撤销已经发生的远端计算。系统可以停止等待或阻止后续调用，但不能为了让 Run 状态好看而把已发生资源事实删除。


统一 API 能屏蔽认证、请求格式和基础 structured output 差异，但不同模型在上下文窗口、tool calling、推理延迟、语言表现和拒答策略上天然不同。如果 Gateway 试图用越来越多隐藏转换把它们伪装成完全等价，上层最终会依赖一套没人能解释的后处理。

更合理的是统一真正稳定的调用 contract，同时让 Role qualification 显式表达差异。上层依赖“这个模型满足当前 Role 的最低行为要求”，而不是相信所有 Provider 是可无损替换的同一种函数。抽象应减少偶然差异，不能抹掉决定质量的真实差异。


即使记录了同一个 ModelVersion、Prompt 和 temperature，外部模型服务仍可能因为底层实现、并行采样或未公开升级返回不同文本。工程上不能承诺“未来重放一定逐 token 相同”。

真正可要求的是可解释重放：知道当时使用的 Role、Provider/Model version、Prompt / input refs、generation config、时间和安全范围，并能在同一资格条件下比较行为。需要强确定性的步骤应该优先用 deterministic checker / rule，而不是把法律正确性建立在模型逐字复现上。

这让历史审计关注“当时基于什么受控输入和模型资格得到这个候选”，而不是追求一个现实上无法保证的随机过程完全重现。


Gateway 最容易因为拥有 token window 和 Provider API，逐渐把 context packing、证据选择和业务 Prompt 都收进自己。这样模型层就会悄悄开始决定法律材料范围，绕过 03 的 Readiness / Retrieval 和 05 的专业语义。

07 可以负责 token limit、transport format、provider-specific encoding 和调用约束，但“哪些业务事实应进入这次推理”由上游 task / Capability / Knowledge 语义决定，08 再决定哪些内容允许外发。Gateway 可以报告输入过大并要求上层缩减，不能自己随意丢掉它认为不重要的 Evidence。

这种边界让换模型时不会顺便改变案件证据选择，也让 context 优化仍然可被专业 Eval 检查。


Provider 限流或成本预算紧张时，多个 Run 可能同时 Retry / fallback。如果每个调用方独立指数重试，容易形成 thundering herd，也可能让一个大任务耗尽整个 tenant 或系统 quota。

07 可以提供 reservation / consumption facts 和当前 quota signal，04 再按 Run Budget 调度；必要时按 tenant、Role 或风险等级做公平限制。目标不是让 Gateway 变成通用 scheduler，而是让资源事实可见，避免“技术上还能发请求”被误解成“这个任务仍有预算资格”。

过载时正确行为可能是排队、换已合格的低成本模型、缩小任务或明确无法满足，而不是用无限 fallback 把 Provider 故障放大成账单故障。


模型行为没变，Provider 调价或计费单位变化也可能让一个原本合理的 fallback 变得不可接受。只把质量 qualification 版本化，却把成本常量硬编码在代码里，会让 Budget 判断长期漂移。

07 应把实际 Usage / Cost settlement 与路由时的预算假设分开：路由根据当前可获得价格和 quota 做决定，事后以真实账单事实结算；09 再观察长期 cost/quality trade-off。成本变化通常不改变 Capability 语义，但可以改变某个模型在特定 profile 下是否值得选。

这样“更便宜/更贵”影响优化策略，不会偷偷改变正式业务正确性。

### 当前、目标与缺口

Current 到底有哪些 Provider、Role routing、usage settlement、cancel semantics 和 qualification evidence，需要回到代码、配置和 Eval；Target 中的完整机制不代表已经实现。

Target 已明确 Role/Provider 解耦、安全与质量双门、受控 fallback、真实 Usage 和 proposal-only 边界。Gap 包括字段级路由策略、Provider 行为测试、真实成本/延迟数据、质量 qualification、取消结算和是否存在独立服务拆分证据。

---

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
