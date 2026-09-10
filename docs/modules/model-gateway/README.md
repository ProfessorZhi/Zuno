# 07 Model Gateway（模型网关）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail_design: candidate-v1 -->

## Part A — Human Narrative

### 当“调用模型”从一行 SDK 变成系统依赖

最早的实现通常很简单。某个模块需要总结合同，就直接调用一个模型 SDK；另一个模块要做 query rewrite，再调用另一套接口。模型只有一两个、数据都能发送、成本也不敏感时，这种做法没有问题，额外增加 Gateway 反而只是包装。

Zuno 的问题出现在同一项法律任务开始同时使用多种模型角色以后。Planner 需要较强的推理能力，Query Rewrite 更在意延迟，结构化抽取可能适合更小、更稳定的模型；某些案件材料只能发给特定地域或特定 Provider，另一家 Provider 可能临时限流，任务又已经接近预算上限。此时“业务代码里写死一个 model name”会让质量、安全、成本和故障处理纠缠在每个调用点。

07 的作用是把模型变成一项受控依赖。上层说明这次调用需要什么能力、结构化约束和 deadline，Gateway 在当前允许且合格的候选中选择实际 Provider / Model，记录真实调用和 Usage，再把结果交还调用方。Planner 的业务 Prompt 仍属于 Runtime，专业抽取语义仍属于 Capability；Gateway 不因为掌握模型 SDK 就拥有这些业务含义。

### 先描述需要的能力，再决定今天用哪一个模型

设想 Runtime 需要生成下一版任务计划。如果代码直接写 `model="某厂商-x-large"`，产品很快会把“规划”这项需求和今天某个 SKU 绑死。模型升级、供应商停服、私有部署上线或者数据外发政策变化时，调用方都要跟着改。

Target 更稳定的输入是 Model Role。Planner 表达“我需要满足这类规划质量、上下文和结构化输出要求的模型”，Extractor 表达另一类要求，Gateway 再根据当前资格选择实现。Role 稳定的是调用方真正依赖的能力边界，Provider / Model 是可以变化的实现选择。

这并不意味着 Gateway 自己发明一套永久模型排行榜。模型是否适合某个 Role，需要 09 的 Eval 证据；数据能否发给某个 Provider，需要 08 的当前安全决定；预算和整个 Run 还能消耗多少资源，需要 04 的控制。07 只把这些约束组合成一次具体的路由选择，并保存当时为什么能够使用这个候选。

因此 API health 绿色只是最弱的一层信息。一个 Provider 技术上能调用，可能因为数据地域限制而当前不能用，也可能没有通过这个 Role 的质量基线。Fallback 也只能在仍然满足这些条件的集合里发生，不能因为主 Provider 503 就退到一个“能返回 JSON 但没验证过”的模型。

### 一次模型调用的结果，要和后续业务成功分开

Provider 返回 200、JSON schema 也正确，只能证明这次模型调用在 transport 和基本格式上完成了。Capability 可能发现内容不符合专业语义，Runtime 可能因为输入已经 stale 而拒绝结果，Domain 也可能因为证据不足而不正式接纳。

07 因此保存的是模型调用事实：选了谁、真实发出了哪次 Attempt、返回了什么结构、消耗了多少 Usage、是否发生 retry 或 fallback。它不会把自己的 success 升级成 Step accepted、Domain admitted 或 Answer published。

这个分离在晚到响应里尤其重要。Provider A timeout 后，Gateway 可能根据当前策略启动 B；几秒后 A 又返回结果。系统不能只保留“最终答案”并把 A 抹掉，因为 A 的调用和费用真实发生过。两个 Attempt 都保留，哪个结果还能被当前 Plan 使用，由 04 / 05 根据版本和验收条件决定。

取消也是类似的。调用方发出 cancel request 时，远端模型可能已经完成，也可能正在生成，还可能根本不支持可靠取消。07 不能根据本地取消标记推断费用为零。它需要继续区分 provider-confirmed cancellation、completed-before-cancel 和 billing / outcome still unknown，并把真实 Usage 结算给上层预算。

### Retry 和 fallback 受同一个预算与资格边界约束

模型 503、网络抖动或偶发格式错误可以做有限 Retry；某个 Provider 持续不可用时，可以切到另一个当前合格的候选。问题在于每一次“再试一次”都在真实消耗时间、token 和费用。

如果每个调用点自行 retry，再由 SDK 自动 retry，外层 Runtime 又做一次 fallback，一次坏请求可能悄悄放大成许多真实模型调用。07 因而需要让每个 Attempt 和 Usage 可见，04 再从 Run 级 Budget 决定继续、降级、Replan 或停止。没有合格 fallback 时，正确行为可以是返回上层等待、人工复核或 abstain，而不是无限降低质量要求。

路由也不应该退化成“永远用最强模型”或“永远用最便宜模型”。复杂规划在某些 task class 上可能确实值得更强推理，简单改写则可能没有收益。只有冻结任务和可比较配置后的 Eval 才能告诉团队升级的边际价值。价格、延迟、质量和安全是共同约束，不是单一排名指标。

### Gateway 统一 transport，不收编所有 Prompt 和专业语义

集中模型调用很容易继续膨胀：既然所有请求都经过 07，就把 Prompt registry、业务模板、专业 schema、数据政策和 Eval 也全部放进 Gateway。这样很快会形成另一个 God Module。

更窄的边界更容易演进。Gateway 可以统一 Provider adapter、请求 envelope、通用 timeout、structured-output transport、真实 Attempt、Usage、Credential 使用和必要的通用 redaction；但“这个 Prompt 为什么这样写”“事件字段在法律业务里是什么意思”“结果达到什么专业门槛”仍跟随真正使用它的模块。

结构化输出也遵循这个划分。07 可以确认 Provider 返回的 JSON 满足 transport/schema 要求，却不能因为字段完整就认定内容正确。专业能力的 semantic acceptance 继续由 05，计划级 acceptance 继续由 04，正式业务接纳继续由 02。

缓存则需要更谨慎。模型输出并不天然可复现，相同 prompt 在模型版本、temperature 或 Provider backend 变化后可能不同。只有调用方明确允许复用时，才适合建立 cache / duplicate suppression；身份要绑定真正影响结果的 Role、模型版本、输入、generation config、schema 和必要 Scope。缓存命中节省的是一次计算，不会制造新的授权或正式业务事实。

### 数据外发和 Secret 让模型路由受到安全约束

同一份案件材料可能允许发给私有部署，却不允许发到某个公共区域。Gateway 即使知道另一个 Provider 更快，也不能把 fallback 变成绕过数据政策的捷径。08 给出当前 egress decision，07 只在允许集合里选择实际模型。

Credential 也不应该进入 Prompt、普通 Trace 或 Checkpoint。Gateway 获取的是受控 Secret / Credential 引用和必要的短期使用权，执行调用后记录使用了哪个受控版本，而不是把明文 API key 变成可恢复状态的一部分。这样模型 Provider 可以替换，Secret 生命周期仍由安全基础设施管理。

Prompt Injection 更说明了为什么模型不能拥有更强权力。模型输出可以建议下一步动作，但不能因为“模型自己认为合理”就修改正式 Domain、扩大权限或触发高风险 Effect。07 只负责模型调用；后面的专业验收、计划控制、授权和 Tool send boundary 继续由对应责任域保护。

### 供应商不变，模型行为也可能漂移

一个 Provider 可以保持同一 API 和同一个 model name，却在后台升级权重、系统提示或推理策略。对上层来说，规划长度、工具选择、拒答倾向和结构化稳定性都可能变化，而编译和接口测试完全不会报错。

所以模型版本和 qualification 需要尽可能绑定真正影响行为的标识。Provider 能提供稳定快照时记录快照；不能时至少记录可获得的版本标识、调用时间和配置，并用 09 的回归 Eval 观察漂移。Gateway 不应该通过越来越多隐蔽后处理把新行为强行伪装成旧行为；上层假设变化时，应明确调整 Prompt、Capability、Role 或 Plan。

07 默认也是逻辑模块，不自动要求一次额外网络跳。Provider adapter 和路由服务完全可以先在同一个 backend / worker 中运行。只有 Secret isolation、独立网络出口、吞吐扩缩、故障半径或合规边界出现明确证据时，才值得拆成独立服务。

如果系统最终只稳定使用一个受控模型，没有多 Provider、复杂数据外发、独立预算和 Role 差异，Gateway 可以继续缩薄成统一 adapter。抽象层的存在必须由替换性和控制需求证明，不能因为“多模型架构听起来完整”而长期扩大。

### Current / Target / Gap

**Target：** 07 以 Model Role 接收上层需求，在当前安全允许、质量合格、预算和 deadline 可接受的候选中选择 Provider / Model，保存真实 Attempt、Usage、Retry / Fallback 与取消结算；Prompt 的业务语义、专业验收、正式 Domain 和安全政策仍由各自 Owner 管理。

**Current：** 完整 Role routing、资格集合、统一 Usage settlement、跨 Provider cancellation、行为漂移治理和多区域 egress routing 属于 Target 设计。当前已有的模型 SDK、调用封装、LangSmith 或相关基础代码实际证明到哪一步，只能按 `docs/evidence/`、代码、测试和可复现 Eval 描述。

**Gap：** 仍需要 Role 级 benchmark、模型升级回归、fallback 资格测试、真实 Usage / cost 对账、取消边界、数据外发策略验证和是否需要独立部署的容量证据。没有这些证据时，不宣称 Gateway 已经完成生产级多模型路由治理。

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。