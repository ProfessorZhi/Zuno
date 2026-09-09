# 05 Capability & Skill（专业能力与技能）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 同一个“事件抽取”为什么不能等于同一个实现

Zuno 已经有一个来自研究工作的事件抽取模型。调用方式很简单：传入材料文本，返回一段 JSON。后来团队希望试一个新的 LLM 版本，它也能返回事件列表，而且字段看起来几乎一样。

最直接的做法是把 Runtime 里的 `PaperAExtractor()` 换成新的 Provider，或者给两者各写一个 wrapper。Demo 很快就能跑起来，但真正的问题没有解决：两个实现对“事件”的边界是否一致，空数组表示确实没有事件还是模型失败，哪类材料属于支持范围，旧结果能不能和新结果直接比较，某个 Provider 现在能调用是否意味着它足以处理这类法律任务。

如果这些问题都留给 Runtime，工作流最终会充满实现特例。换一次模型，要改 Planner、错误处理、fallback、Eval 解释和下游判断；研究资产越多，业务代码越难稳定。

05 因此先固定“专业上要完成什么”，再讨论“谁来完成”。事件抽取、冲突识别、证据比较、类案检索、法条推荐都可以成为这种稳定专业承诺。工程上把它叫作 `Capability（专业能力）`。

Capability 不是一个模型类名，也不要求一定有独立服务。它首先规定输入的业务含义、输出代表什么、支持和不支持的范围、成功与不可判定怎样表达，以及后续流程可以怎样消费结果。只有真正改变这些专业语义时，才需要新的 CapabilityVersion。

### 先固定专业承诺，再允许 Provider 竞争

同一个 Capability 可以由研究模型、规则系统、LLM、外部服务甚至人工辅助实现。它们都是 Provider。

这种分离让 Runtime 依赖“事件抽取 v2 的专业承诺”，而不是某个供应商 SDK。模型升级、部署地址变化或 Provider 下线时，只要新的实现仍满足同一个 CapabilityVersion 的语义，上层不必重新理解整套业务。

反过来，如果“事件”的定义、字段含义、错误语义或适用范围已经变化，就不能把升级藏在旧版本后面。即使 API schema 没变，也应该形成新的 CapabilityVersion 或重新明确迁移关系。版本保护的是专业语义，不是为了追求 semver 形式。

ProviderVersion 则记录实现自己的变化，例如模型权重、规则版本、部署或推理配置。两类版本分开以后，质量回退时才能判断到底是能力契约变了，还是某个实现变了。

### 能调用只是接入，能用于当前任务还要过 Qualification

Provider 接上以后，第一道门是 Conformance：字段能否满足契约，错误和 unsupported 是否表达正确，必要来源和版本是否存在。它回答“这个实现有没有遵守这份能力协议”。

通过 Conformance 仍然不代表它适合当前任务。一个 Provider 可以永远返回合法 JSON，却在复杂案件上准确率很差；另一个研究模型可能 benchmark 很好，却只覆盖特定材料类型，遇到扫描件或长文本时没有稳定行为。

所以 05 还需要 Qualification。Eval 在冻结的数据、版本和配置上评估某个 Provider 对哪些 task class、材料类型和风险 profile 足够好；05 再把这些证据和当前条件组合成 Eligibility。Runtime 消费“现在有哪些实现可以用于这项任务”，不用自己重新实现专业质量判断。

健康检查只说明技术上还能请求。资格回答的是更难的问题：这个 CapabilityVersion 的这个 ProviderVersion，在当前任务范围里是否仍然有证据支持。模型、Prompt、ProcessingSpec 或数据分布发生重大变化后，旧资格也需要重新验证，而不是永久保持绿色。

“不会做”必须成为专业能力的一部分。某个事件抽取 Provider 只支持中文合同正文，就应该明确 unsupported；材料不足时可以返回 insufficient / review required。为了提高 success rate 强迫所有输入都产出一个结构完整答案，会把能力边界变成幻觉来源。

### 失败、fallback 和版本变化必须说明语义有没有变

Provider 503、GPU 不可用或连接超时，是执行层故障。只要输入和能力语义没有变化，Runtime 可以在预算和策略允许时 Retry，或者切换到另一个当前合格 Provider。

如果同一个版本突然改变了字段含义、事件边界或错误语义，问题已经不是“再调用一次”。这种 semantic drift 应该阻断资格、触发重新验证或版本升级。用自动 Retry 掩盖语义漂移，只会让系统更稳定地产生不可比较结果。

Fallback 也只能在当前合格集合里选择。Provider A 挂了以后，换到一个“也能返回 JSON”的 B 并不算可靠降级；如果 B 没有达到这项任务的最低质量或数据政策要求，正确结果可能是 Replan、Review 或 abstain。

每次实际 Invocation 还需要知道自己使用了哪个 CapabilityVersion、ProviderVersion、材料版本和重要配置。这样同一个 Runtime Step 多次尝试不同 Provider 时，不会把所有结果混成一个调用事实；Cache 也能绑定真正影响结果的版本，而不是材料或语义变化后静默复用旧输出。

缓存命中只表示“这次专业计算可以复用”。它不意味着 02 已经正式接纳这份结果，也不意味着当前 Security 和任务新鲜度永远不再检查。

### Research、Build、Buy 通过同一能力边界进入系统

课题组研究成果进入 Zuno 时，最有价值的不是把论文代码包装成一个新 Agent，而是把可复现的算法能力放进稳定专业语义下比较。

一篇论文、一个实验模型或一套规则首先是 Research Artifact。要进入正式调用路径，需要明确它解决的任务、输入输出、适用范围、版本和来源，再形成 Provider；通过 Conformance 和 Eval 以后，才获得具体任务资格。最终输出仍然是 Candidate，是否进入正式法律业务事实由 02 决定。

这条路径也给外部采购留下空间。成熟 OCR、通用 embedding、基础分类、模型 Provider 或第三方服务可以优先 Buy / Extend；真正形成长期差异的法律专业语义、Eval 数据和少数算法资产可以 Build。05 的价值之一就是让 Build 和 Buy 在同一 Capability 下公平竞争，而不是为了“自研平台”把所有东西重新实现。

Capability 也不能吞掉 Model Gateway 和 Tool Runtime。一个专业能力可以内部调用 LLM，07 记录真实模型调用；它也可以提出一个 Action Proposal，现实副作用仍交给 06。专业语义、模型 transport 和现实 Effect 的失败方式不同，把三者统一成万能 Tool Registry 会重新制造 God Layer。

### 什么时候 Capability 层应该很薄

如果系统只有几个稳定内部函数，没有多个 Provider，没有独立质量门槛，也没有跨 Runtime 复用要求，Capability 层可以只是清楚的 Python Protocol、版本常量和测试集合。没有必要先建 registry、marketplace 或独立服务。

只有研究资产多、Provider 经常替换、需要独立 Qualification、或者同一专业能力要被多个执行路径复用时，registry、eligibility 和更完整生命周期才开始有价值。

Provider exit 是检验这层抽象是否真的成立的一个好方法：某个研究模型停维、外部服务下线或质量下降时，系统应该能够撤销它的 Eligibility，而不是重写 Runtime 和 Domain。如果做不到，所谓“可替换能力层”仍然只是接口包装。

### Current / Target / Gap

**Target：** 05 拥有 Capability 语义与版本、Provider binding、Conformance、Qualification / Eligibility 以及调用来源；它产生专业 Candidate / Proposal，不拥有 Formal Admission、模型 transport 或现实 Effect truth。

**Current：** 历史代码已经存在 Skill / Tool、模型、研究算法和部分评测路径，但 Target 中统一 Capability lifecycle、Provider qualification 和任务级 Eligibility 不能从这些实现自动推断为已完成。

**Gap：** 需要进一步冻结 Capability / Provider 的字段级 Contract，建立按 task class 的资格证据、semantic drift 检测、Provider exit 测试，以及真实法律任务上 Build / Buy / LLM / 专用模型的可比评测。

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
