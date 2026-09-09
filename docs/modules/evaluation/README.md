# 09 Observability & Evaluation（可观测性与评测）

<!-- status: design-baseline-v1; implementation: not-authorized; quality: not-established; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### Observability 解释发生了什么，Evaluation 判断设计是否值得保留

系统出故障时，工程师需要沿一次请求找到相关 Run、检索、模型、Capability、Tool、Domain 和 Delivery；架构演进时，团队又需要判断 GraphRAG、Reflection、Native Runtime 或强模型是否真的提高质量。

Observability 负责解释系统发生了什么，Evaluation 负责判断结果好不好、复杂度是否值得保留。两者共享版本、关联和数据治理，但不能因为都“看数据”就混成一个 Dashboard。

GraphRAG、Reflection、强模型、Specialist 或 Native Runtime 是否值得保留，是 09 必须持续回答的设计问题。团队既要知道一次真实请求发生了什么，也要把同一 task class 放进可复现实验，与更简单 baseline 比质量、恢复、时延和成本。Observability 提供因果线索，Evaluation 提供决策证据；两者都不拥有业务 Truth。

### Trace 只能解释过程，事故调查先回到 Owner Fact

Trace 非常适合关联调用，但它可能被采样、Exporter 失败、网络中断或 redaction 删除内容。如果恢复和业务判断依赖 Trace，观测系统故障会反过来破坏业务正确性。

因此保持：

```text
Telemetry != Durable Audit != Business Truth
```

02、06、08 等 Owner 保存自己的耐久事实，09 引用它们解释时间线。漂亮 span 不能替代 AdmissionReceipt、EffectReceipt 或安全审计证明。


用户报告“系统重复提交了两次”，第一步不是统计 Trace 里有几个 HTTP span，而是查询 06 的逻辑动作、Attempt、EffectReceipt 和 Reconciliation，确认现实世界到底发生了几个效果。

随后再用 Runtime Plan、Security decision、Delivery 和 Trace 对齐时间线。Observability 的价值是帮助解释“为什么发生”，不是自己裁决“业务事实是什么”。

### Correlation、OpenTelemetry Baggage 与 Sampling 只服务观测，不升级成业务权威

九个责任域各自拥有事实，如果没有稳定 correlation，就很难回答某次模型调用属于哪个 Step、产生哪个 Capability output、最后是否正式进入 Domain。

系统可以传播 request / run / step / action / admission 等 opaque refs 做定位，但 correlation id 不能自动成为幂等 key、授权 token 或业务主键。关联帮助查询，不产生权威。


Baggage 会跨进程广泛传播，如果把 tenant 名称、案件名称、用户 PII、材料正文或授权内容直接塞进去，诊断便利会扩大敏感数据暴露面。

默认只传播最小 opaque identity，在可信边界回查 Owner fact。尤其 `Secret NEVER EXPORT`。必要业务文本只有在策略允许、完成 redaction 且确实有诊断价值时才进入受控 Telemetry。


高吞吐系统不可能永久保存每一个成功 span，Sampling 是合理成本控制。可以提高 error / high-risk task 采样率，降低普通成功请求采样。

但 Sampling 不能决定 Domain、Effect、Authorization 或 Mandatory Audit 是否存在。关闭 tracing 不能让系统失去恢复能力，也不能让安全证明消失。

可比较的 Eval 建立在可解释运行事实之上。Dataset、版本、训练暴露关系和 Judge 先被冻结，再比较不同设计；Dashboard 上的单一数字不足以支持架构选择。

### Eval Dataset、Judge 与 PASS / FAIL / BLOCKED 需要版本化边界

今天一百个 case，明天修改二十个标签，如果两次分数直接比较，就无法判断变化来自模型还是数据集。Dataset 本身也是实验输入。

DatasetVersion 需要稳定 case identity、材料 refs、任务类别、标签 / expected evidence、annotation provenance 和数据政策。数据集变化产生新版本，保证实验结果可解释。


Prompt tuning、few-shot、模型训练或人工调参如果已经看过某些 case，这些样本就不能在不说明的情况下继续充当独立 test。

Eval 需要记录 split 和 exposure provenance。真实法院材料受数据政策限制时，也不能偷偷换成合成数据后仍然声称“真实法院质量已验证”；测量范围必须明确。


引用是否存在、JSON 是否合法、action hash 是否一致、重复 Effect 是否发生，都应该优先使用 deterministic checker。开放式法律论证、适用性和表达质量才更适合 LLM Judge。

Judge 自身也有模型、Prompt 和漂移问题，因此 JudgeVersion 需要进入 Eval config，并用人工金标准校准。Judge 不可靠时结果应标记 blocked / unreliable，而不是为了持续产分数而假装可信。


PASS 表示在冻结 Dataset、配置、样本数和阈值下真正达标；FAIL 表示评测有效执行但结果不达标；BLOCKED 表示根本没有资格判断，例如没有样本、凭证缺失、Judge 不可用或 baseline 不可比。

当前正式 benchmark 在证据不足时应明确 `MEASUREMENT_BLOCKED`。Blocked 不是较轻的 Fail，更不能默认为 Pass。

### 质量、恢复、延迟和成本必须按 Task Class 一起评估

法律场景里，越权读取、重复高风险 Effect、正式引用无法回溯、stale WorkProduct 被错误发布等问题不能被高平均准确率抵消。

Release Evaluation 因此既看 aggregate metrics，也看 critical failure taxonomy。平均分很好但触发定义中的关键安全/正确性违规，发布资格仍然可以 Fail。


Agent 复杂度常常在最终准确率以外付出代价：Retry 放大、P95 延迟、人工介入、token 和 Provider 费用。一个方案提高一点准确率，却让成本和恢复失败面翻倍，未必值得保留。

评测因此需要把 evidence sufficiency、citation correctness、unsupported claim、reviewer acceptance、recovery correctness、duplicate effect、Replan rate、reconcile duration、latency、token 和 cost 放在同一实验解释里。


简单条文定位、跨文档争议分析、带现实副作用的任务目标不同。把它们混成一个“Agent Success Rate”，会让简单题数量掩盖复杂路径问题。

每个 EvalCase 应绑定 task class、difficulty / risk profile 和实际执行路径。这样才能回答 GraphRAG 是否只对某类 query 有价值，Native Runtime 是否只在长任务恢复上有收益。

---

**评测真正进入架构决策，是从敢做反事实开始。** 如果只证明整套系统能跑，任何已经实现的复杂机制都会因为沉没成本永久存在；只有 baseline、ablation 和 kill test 才能回答某一层复杂度是否真的贡献了价值。

### Evaluation 的职责包括主动删除没有收益的复杂度

团队已经实现的功能很容易获得沉没成本保护：有 GraphRAG 就只展示 GraphRAG 的分数，有 Reflection 就只证明它“能跑”。

09 应主动设计 baseline、ablation 和 kill test：GraphRAG vs Hybrid Retrieval、Memory on/off、Reflection on/off、Generic Host + Legal Backend vs Native Runtime。在尽量相同语料、模型和预算下比较真实边际收益。


Target 采用 OpenTelemetry / OTLP-compatible contract，让 LangSmith 可以作为 Agent / LLM Trace 与 Eval 的 preferred Provider，但核心运行和审计不能依赖单一 SaaS。

更换 OTel backend 或未来其他观测 Provider 时，稳定 correlation、redaction 和 semantic convention 不应改变业务 Owner。Provider 可替换才说明观测层没有绑架运行架构。


如果 Trace exporter 故障，09 可以 buffer / retry 或丢弃低优先级 telemetry；02 / 06 / 08 的耐久事实继续成立，普通业务不应因为 Dashboard 暂时不可用就全部停止。

只有安全策略明确要求的 Mandatory Audit 走独立 durable boundary。Tracing 可用性和合规审计可用性必须分开。

---

**在继续讨论更多观测和评测细节前，先限制 Evidence 自己的权力。** 一组 Eval PASS 可以证明特定 Dataset / config / profile 达标，却不能替容量、HA / DR、安全 qualification、真实外围系统和运维证据宣布 Production Ready。测量越严格，越要说清它没有证明什么。


一组 Eval PASS 只能说明它覆盖的 Dataset、配置、commit 和 profile 达到门槛。生产成熟度还需要容量、HA / DR、安全 qualification、恢复演练、外部依赖和运维证据。

09 可以形成 ReleaseEvaluationEvidence，但不能单独宣布整个系统 production ready。测量越严谨，越应该明确它没有覆盖什么。


如果没有稳定 correlation 和 Owner fact，日志越多越可能只是噪音。观测设计应先列关键问题：一次结果为什么被拒绝、哪一步扩大了成本、现实 Effect 是否重复、哪个版本导致质量回退、权限撤销后是否仍有访问。

然后为这些问题提供最小可关联事件、指标和 trace attributes。高基数字段、敏感正文和每个 token 的细节只有在确有诊断价值时才记录。Observability 的目标是缩短解释时间，不是最大化数据量。

同样，Dashboard 只是 projection。事故裁决仍然回到 durable owner facts，避免“图上没有 span，所以事情没发生”的错误结论。

### 先定义 Decision，再选 Metric；Ablation 与线上数据共同解释因果

“我们要测准确率”不是完整评测目标。先要说清这次实验要决定什么：是否启用 GraphRAG、是否升级模型、是否保留 Reflection、是否允许某 Capability 进入高风险任务。不同 Decision 需要不同 case、指标和阈值。

例如判断 GraphRAG 是否保留，需要在关系型 / multi-hop query class 上和 Hybrid baseline 比质量、延迟与成本；判断 Tool Runtime 是否安全，需要 fault injection 和 duplicate-effect 指标，而不是法律问答准确率。

Metric 因 Decision 而存在，可以防止团队只展示最容易变绿的数字。


复杂系统通常多项机制同时开启：更强模型、GraphRAG、Reflection、Memory、Specialist。最终分数提高时，很难知道到底谁贡献了收益。

Ablation 在尽量相同条件下关闭一个机制，观察质量、成本和恢复变化。必要时做 factorial / 分层实验，至少保证关键架构选择有 simpler baseline。没有这种对照，团队只能证明“整套系统能跑”，不能证明每一层复杂度值得存在。

这也是 Kill Test 的来源：如果关闭某机制几乎不影响目标指标，应该认真考虑删除，而不是寻找更多理由保留。


离线 Dataset 可复现、适合版本比较，却可能覆盖不了真实分布和运维故障；线上 telemetry 反映真实流量，但缺少稳定 ground truth，且受用户行为和版本混杂影响。

两者应互补：离线 Eval 做发布前质量和回归门，线上观测检查 drift、latency、cost、recovery 和真实失败分布，再把重要线上失败沉淀为新的 Eval cases。生产反馈进入数据集时还要遵守隐私和标注 provenance。

只看线下分数会错过运行问题，只看线上成功率又无法公平比较模型和架构版本。


工程团队常希望 CI 最终只有绿色或红色，但质量证据有时就是不完整：样本不足、Judge 不可用、数据政策禁止运行某 profile、baseline 版本不兼容。这时 BLOCKED 比假 Pass 或假 Fail 更准确。

Release policy 可以规定某些关键 gate BLOCKED 就不能发布，也可以允许低风险 profile 在明确 exception 下继续，但必须记录是谁接受了未知风险。系统不能为了流水线顺畅把“没有测”解释成“没有问题”。

Measurement honesty 是 Evaluation 的架构职责之一。


总账单只能告诉团队花了多少钱，无法解释为什么。真正优化需要知道某个 task class、Plan、Step、Capability 或模型 fallback 消耗了多少，以及这些成本是否换来质量收益。

07 提供模型 Usage，03/05/06 提供各自执行事实，09 沿 correlation 做归因和趋势。04 负责单次 Run 的预算控制，但长期“哪个机制值得删”由 09 的跨运行数据回答。

只有成本和质量共享可比较的实验身份，团队才能判断一个额外 Reflection 或 Graph route 是投资还是浪费。


SLO 更关注运行服务是否在承诺时间内可用、延迟和错误率是否受控；Eval 关注法律结果、证据、恢复和复杂机制的质量是否达到目标。一个系统可以 P99 很漂亮但引用质量很差，也可以离线准确率很高却经常因为外部 Effect unknown 无法完成真实任务。

因此运行可靠性和结果质量需要分别定义，再按 task class 一起看。SLO 告诉团队“服务有没有稳定工作”，Eval 告诉团队“稳定工作出来的东西是否值得”。把二者压成一个总分，很容易让高流量简单请求掩盖低频高风险错误。

09 可以把两类 Evidence 关联到同一版本和发布决策，但不能让一个维度自动替另一个维度通过。


Trace 可以显示 GraphRAG 打开时某次请求更慢，也可以显示 Reflection 发生后结果最终通过，但这只是同一时间线上的相关性。要证明某机制导致质量提升，需要尽量控制其他变量的 A/B、ablation 或 counterfactual 比较。

这就是 Observability 和 Evaluation 的互补：前者帮助找到假设，后者用实验验证假设。仅凭 Dashboard 上两个曲线同时变化，就决定永久增加一个架构组件，很容易把偶然相关写成设计因果。

反过来，实验发现收益后仍要回到线上观察真实分布和故障面，避免离线环境的因果结论在生产条件下失效。


一旦团队知道 release gate 只看某个数字，就会自然优化这个数字：检索器可能通过返回更多重复片段提高某种 recall，模型可能学会 Judge 偏好的表达，人工标注也可能逐渐适应系统输出。指标继续变绿，不代表真实法律工作更好。

所以关键决策要保留多维指标、critical failure、holdout / exposure provenance 和人工抽查，并定期检查“这个 Metric 是否仍然代表原始目标”。尤其 LLM Judge 不能成为唯一自我循环的裁判。

Evaluation 的职责不是制造一个永远上涨的分数，而是持续发现现有指标在哪些情况下会说谎。


确定性 schema、引用、幂等和安全 Contract 可以在每次变更快速检查；小规模高价值案例适合常规回归；昂贵 LLM Judge、fault injection、长任务恢复和大样本 benchmark 可以按风险与发布阶段运行。把所有验证都放在同一层，要么 CI 慢到没人愿意跑，要么为了速度被迫把深度测试删掉。

因此 Evaluation 可以形成测试金字塔：便宜、确定的 gate 高频运行；高成本专业 Eval 在影响相关能力时运行；更大规模 baseline / ablation 在架构或发布决策前执行。具体自动化频率是工程选择，原则是让证据成本与风险匹配。

这也帮助保持 BLOCKED 的诚实语义：高成本条件暂时不具备时，可以明确哪些证据缺失，而不是用一组便宜测试冒充完整质量证明。


把线上失败沉淀成回归 case 很有价值，但如果同一 case 立刻被 Prompt tuning、few-shot 或人工规则直接针对，随后又继续留在“独立测试集”，分数会越来越乐观。

因此生产事故进入 Eval 后需要记录 exposure：它可以成为 regression set，验证同类错误不再出现；真正评估泛化能力仍要保留未暴露 holdout 或新的代表性样本。线上反馈、训练资产和测试证据不能因为都在一个仓库里就失去边界。

这让“系统从事故中学习”和“我们仍然有可信的独立评测”可以同时成立。

### 当前、目标与缺口

Current 到底有哪些 Trace、Metric、Dataset、Judge、release gate 和真实 benchmark，必须回到证据；没有样本或 Provider 条件时保持 BLOCKED，而不是从 Target 推断质量。

Target 已明确 Telemetry 与业务真相分离、Dataset / Eval 版本化、deterministic checker 优先、复杂度 kill test 和 provider-neutral observability。Gap 包括真实基准数据、Judge 校准、生产 telemetry 成本、隐私 redaction 验证、恢复与 Effect fault injection，以及复杂机制是否真正值得保留。

---

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
