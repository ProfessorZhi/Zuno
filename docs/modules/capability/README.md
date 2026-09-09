# 05 Capability & Skill（专业能力与技能）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 专业能力先成为稳定产品契约，再选择实现

Zuno 会使用事件抽取、事件对齐、争议识别、证据分析、类案检索、法条推荐和其他法律算法。这些能力可能来自课题组研究、规则代码、传统模型、新 LLM 或外部服务。直接让 Runtime 依赖某个脚本或 Provider，短期最省事，长期却会把业务语义和实现版本绑死。

05 的职责是把“能完成什么专业任务”稳定下来，再允许不同 Provider 去实现。Runtime 调用的是专业能力语义，Eval 判断当前实现是否合格，Domain 决定输出能否成为正式事实。

**贯穿这一篇的例子可以只看“事件抽取”这一项能力。** 早期它可能由课题组研究模型实现，后来也可能出现规则版本、LLM Provider 或外部服务。如果 Runtime 直接依赖 `PaperAExtractor()`，每次换实现都会把 Workflow、失败语义和质量假设一起带着改；真正需要稳定下来的，是“事件抽取这项专业能力到底承诺什么”，而不是某个算法名字。下面的 Capability / Provider / Conformance / Qualification 都围绕这个问题展开。


一个研究模型刚接入时，最简单方案是写一个 Python wrapper：传入文本，返回 JSON。只要 Demo 跑通，看起来已经是 Skill。

随着模型升级、输入材料类型变化、多个 Provider 共存，问题就出现了：不同实现对“事件”定义是否一致；失败返回空数组是“没有事件”还是“模型故障”；新版字段是否兼容旧调用方；某个 Provider 技术可调用是否意味着质量足够。没有稳定能力语义，Runtime 只能不断理解每个实现的特殊情况。

### Capability = 稳定专业语义

Capability 的核心不是类名，而是一份专业承诺：输入是什么业务含义，输出表达什么，哪些情况算成功、拒绝、不可判定或需要 Review，以及结果可以被哪些后续流程消费。

实现可以变化，但同一 CapabilityVersion 下的语义必须稳定。真正改变专业含义时创建新版本，而不是在旧接口后面偷偷改变“同一个字段是什么意思”。


一个 Capability 可以由课题组旧模型、现代 LLM、规则系统或外部服务实现。把 Provider identity 从能力语义中分离，Runtime 才能根据当前资格选择实现，而不把业务代码绑定到某个框架或模型家族。

Provider 变化可以是部署、性能或模型升级；Capability 版本变化则表示专业契约变化。两类版本分开以后，回放和 Eval 才能解释质量变化来自哪里。

### Provider Conformance != task quality

Conformance 回答“这个 Provider 是否遵守 Capability 契约”：字段、错误语义、版本、必要来源和行为边界是否一致。它是接入门槛，不是专业质量证明。

所以必须保持 `Provider Conformance != task quality`。一个 Provider 可以完全符合 schema，却在复杂案件上准确率很差；反过来，一个研究脚本可能某项 benchmark 很强，却没有稳定错误语义，不适合直接进入生产调用路径。


Provider 超时、依赖 503、GPU 不可用，属于实现执行失败；如果同一个版本突然改变事件边界、字段含义或输出约束，则属于能力语义漂移，不能通过普通 Retry 掩盖。

```text
provider execution failure
!=
capability semantic drift
```

前者可以 fallback 或 retry，后者应该阻断资格、触发版本升级或重新验证。把两类失败都叫“调用失败”，会让系统在语义已经不可信时继续切换重试。


Provider 健康只说明技术上能调用。某次任务能否使用，还取决于 CapabilityVersion、Conformance、质量基线、数据限制、当前材料类型和任务风险。

Eligibility 是这些条件的任务级组合。它防止“API 是绿的”被误解成“这个实现适合当前法律任务”。Runtime 可以消费资格，却不应该自己重新实现专业评测逻辑。


专业输出需要能解释“由哪个 CapabilityVersion、哪个 ProviderVersion、基于哪些材料和参数产生”。否则模型升级后出现质量变化，系统无法重放或归因。

Invocation identity 还帮助处理重复执行和 cache。它不应该和 Runtime Step id 合并，因为同一个 Step 可能多次尝试不同 Provider，而同一 Capability 也可能被不同 Run 调用。


Provider A 不可用时切到 B 看起来只是可用性优化，但 B 必须满足同一 Capability 的最低语义和质量要求。否则“fallback 成功”可能只是换成了一个会返回 JSON、却不适合当前任务的实现。

因此 fallback 候选来自当前资格集合，而不是所有技术兼容 Provider。没有合格实现时，正确结果可能是让 Runtime Replan、进入 Review 或明确 abstain，而不是无限降低标准。


某些确定性或高重复能力可以缓存，但 cache identity 需要绑定输入版本、Capability / Provider 版本、配置和必要安全 Scope。材料或专业语义变化后，旧结果不能静默复用。

更重要的是，缓存命中只表示“可以复用一次专业计算结果”，仍然不等于 Domain 正式接受。Formal Admission 的业务资格继续由 02 判断。

### Capability、Model 和 Tool 保持不同责任边界

LLM 是一种计算 Provider，Tool 可能产生现实副作用，Capability 则是专业业务语义。三者有交集，但失败和权威不同。

一个专业能力可以内部调用模型，也可以产生一个 Action Proposal；模型调用事实由 07 记录，现实执行由 06 控制，05 只保证专业输出满足自己的契约。把三者统一成万能 Tool，会让预算、安全、Effect 和专业质量边界互相污染。

### 研究成果通过复现与 Qualification 才进入 Capability

研究论文或课题组算法首先证明某个局部问题可能可解，不自动证明它已经是稳定产品能力。进入 Zuno 前，需要明确语义、版本、来源、Provider 接口、Conformance 和 Eval。

这样事件抽取、事件对齐、冲突识别等研究资产可以保留学术价值，又不会因为“是我们自己的模型”就跳过产品化门槛。新的 LLM Provider 也可以在同一专业语义下与旧模型公平比较。


LLM 可以快速覆盖很多专业任务，但成本、延迟、可复现性和结构化稳定性并不总优于专门模型、规则或检索算法。能力层应该允许不同实现按任务价值竞争。

复杂开放判断可能值得更强推理模型，稳定抽取可能更适合小模型或规则。选择依据应该是 Eval 和业务约束，而不是“最新模型能力更强”的抽象印象。


如果某个外部服务停服、研究模型不再维护或质量下降，系统应该能撤销它的 Eligibility，而不要求重写 Runtime 和 Domain。Provider exit 是可替换架构真正成立的测试。

同样，加入新 Provider 也不应该自动获得资格。先证明 Conformance，再证明相应任务质量，最后进入可用集合。


如果系统只有少量稳定内部函数，没有多个实现、版本演进和独立质量门槛，那么 Capability 层可以非常薄，甚至只是清晰的 Python Protocol 和测试集合。

只有研究资产多、Provider 经常变化、需要独立评测和跨 Runtime 复用时，才值得增加 registry、eligibility 和更完整生命周期。能力管理不能为了“平台化”而自我膨胀。

### 版本、资格与 Provider 生命周期共同保护可替换性

如果只是模型权重、部署地址或运行优化改变，而专业输入输出语义保持兼容，通常属于 ProviderVersion 演进；如果“事件”的业务定义、字段含义、错误语义或可接受输出发生变化，则需要新的 CapabilityVersion。

这个区分让上层能够判断兼容性。Runtime 可以在同一 CapabilityVersion 下替换合格 Provider，而不重新理解业务；能力语义真正变化时，上层则明确选择是否迁移，而不是被隐藏升级影响。

版本规则不能只靠 semver 名字，关键是变化是否改变消费者必须理解的专业承诺。


某些专业任务最适合规则或传统模型，另一些需要 LLM 开放推理。Capability 层不应该预设“专业能力就是 Agent”或“就是模型”。

只要输入输出和失败语义相同，deterministic provider、ML provider 和 LLM provider 可以竞争同一能力资格。这样团队可以用更便宜、更稳定的实现替换昂贵模型，也可以在规则覆盖不足时引入 LLM，而不改变 Runtime 的业务调用方式。

这也是研究工程化的重要价值：比较的是解决同一专业问题的方案，而不是比较框架品牌。


一个 Provider 在 Dataset V3 上通过，不代表未来模型、Prompt、ProcessingSpec 或数据分布变化后永久合格。Qualification 需要绑定可复现配置和时间/版本范围，并在重大变化后重新评测。

同时不能把 Eval 服务临时不可用解释成 Provider 自动失败或自动通过。已有 qualification 是否仍在有效期、当前安全政策是否允许、任务是否落在已覆盖 profile，都需要分别判断。

这使 Eligibility 成为“当前任务现在能不能用”的组合，而不是 registry 中一个永远绿色的开关。


课题组拥有研究成果，不等于所有能力都应该自研。成熟 OCR、通用 embedding、基础分类和模型 Provider 可以优先采购或复用；真正体现法律专业资产的语义、Eval 数据和特定算法可以自有。

判断标准是差异是否长期重要、是否有可维护 Evidence，以及替代成本。如果外部能力已经稳定满足专业契约，自研实现没有明显质量、隐私、成本或可控性收益，就不应为了“技术含量”重复建设。

Capability abstraction 的价值之一正是允许 Buy 和 Build 共存，而不是把所有 Provider 都吸收到一套自研框架里。


能力注册表很容易膨胀成所有 Prompt、Tool、MCP server 和插件元数据的统一市场。这样做看似平台化，却会把专业契约、模型调用、现实副作用和安全边界混在一个配置中心。

05 只拥有专业 Capability identity、版本、Provider conformance 与资格。Prompt 的具体业务语义跟随使用场景，Tool effect 由 06，模型 transport 由 07，安全策略由 08。保持这个窄边界，才能让能力层真正稳定。


专业系统容易把 Provider success rate 当成目标，于是实现会倾向于任何输入都返回一个结构完整的结果。但某个 Capability 可能只支持特定材料类型、语言、案件阶段或风险等级；超出已验证范围时，最安全的行为是明确 unsupported / insufficient / review required。

这种“有边界的不会做”必须进入 Capability 语义，否则 Runtime 无法区分“任务本来不适用”和“Provider 临时坏了”。前者可能需要换 Capability、Replan 或人工，后者才适合 retry / fallback。同样，Eval 也应该惩罚在未知范围里自信输出，而不是只奖励覆盖率。

Capability 越能精确声明自己的适用范围，上层越不需要依赖模型自报 confidence 来猜是否可信。专业能力的成熟度不在于永远返回答案，而在于知道自己的资格边界。


一个复杂法律分析可能组合事件抽取、证据比较、法条检索和综合判断。为了调用方便，把整条链包装成一个巨大 Capability 看起来很省事，但会重新隐藏每一步的版本、失败和质量责任。某个子能力升级后，团队也无法判断最终变化来自哪里。

更合理的是只在业务上确实形成稳定整体语义时才提供组合能力，并继续保留关键子能力的 causation。Runtime 可以编排多个 Capability，05 负责每个专业边界的契约和资格；不要因为“一个接口更简单”就牺牲可替换性和可评测性。组合层如果没有独立专业语义，应留在 Runtime Plan，而不是升级成新的长期能力类型。


两个 Provider 都返回同样的 JSON，不代表它们真的实现同一个专业能力。一个事件抽取器可能把“付款发生日”解释为到账日，另一个解释为合同约定日；字段名完全一致，业务含义却已经不同。

因此 Conformance 除了 schema，还要覆盖关键语义样例、边界条件和 failure behavior。CapabilityVersion 是否兼容，最终看消费者能否在不改变专业理解的情况下继续使用，而不是看 Pydantic 能不能 parse。

这也是 Provider adapter 不应该做过度“修复”的原因：如果必须靠大量隐藏规则把一个 Provider 的输出猜成目标语义，更可能说明它没有真正 Conform，而不是 adapter 还不够聪明。


一个模型在中文合同事件抽取上表现很好，不代表它对扫描 OCR 噪声、英文材料、超长案件或高风险正式结论同样合格。全局 `qualified=true` 会把局部 Evidence 放大成所有场景资格。

更合理的是让资格能够说明它覆盖的 task class、输入 profile、风险等级和版本。任务落在未验证范围时，可以选择更保守 Provider、降级、Review 或明确 insufficient，而不是让模型 confidence 自己决定是否“应该能做”。

资格越具体，05 越能支持真实 Build / Buy 比较：外部 Provider 也可以只在它真正有优势的范围内被采用，不需要赢得整个 Capability。


发现新 Provider 更好以后，直接删除旧版本会让正在运行的 Plan 失去自己绑定的实现，也让历史 Eval 无法解释。新请求可以逐步切到新 Provider，但已激活 Run 是否继续旧版本，要看兼容和风险；必要时由 04 明确 Replan，而不是 05 在后台热替换。

旧 Provider 即使不再可调用，它的 version identity、qualification 和历史 invocation refs 仍可能需要保留，用于解释过去 WorkProduct 或 Eval。退役的是“未来可选资格”，不是把历史事实从系统里抹掉。

这使 Capability 生命周期拥有清楚的 migration 语义：新增、限制、降级、停止新流量、最终移除执行能力，都不需要改写过去。


研究论文、实验 notebook 或一次 Demo 可以证明方向值得探索，但 Provider qualification 需要知道实际使用的代码、模型/规则版本、数据处理方式和 Eval 条件。否则团队无法判断后续质量变化来自算法、数据还是运行环境。

Zuno 不需要把研究工程变成沉重 MLOps 平台，但至少要把影响专业语义和质量的 artefact/version refs 与 Eval 绑定。论文是来源证据，能够复现实验并在当前任务上通过资格门，才是工程 Provider 的 Evidence。

这样研究资产可以持续进入产品，又不会因为“这是我们自己的论文算法”获得永久豁免。

### 当前、目标与缺口

Current 已有哪些 Capability、Provider、Conformance test 和真实 Eval，必须回到代码和证据；Target 中列出的研究能力 family 不等于它们全部已经产品化或达到质量门槛。

Target 已明确专业语义与 Provider 解耦、Conformance 与质量分开、fallback 受资格约束，以及 Capability 输出仍是 Proposal。Gap 包括字段级版本策略、真实 Provider 兼容、任务级 Eval、cache/fallback 故障测试和哪些研究资产真正值得长期维护。

---

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
