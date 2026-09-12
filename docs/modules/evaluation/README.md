# 09 Observability & Evaluation（可观测性与评测）

<!-- status: design-baseline-v1; implementation: not-authorized; quality: not-established; deepening: cross-module-consistency-v2; detail_design: candidate-v1 -->

## Part A — Human Narrative

### 当 GraphRAG 已经做出来，问题才真正开始

一条更复杂的检索路线已经实现，能够构图、扩展实体关系并做多跳召回。工程上它能跑，Demo 里也能展示更多中间过程。这个时候最容易犯的错误，是把“已经实现”当成“应该长期保留”。

真正需要回答的是：它在哪些问题上比更简单的 Hybrid Retrieval 找到更多有用证据，是否引入新的误召回，增加多少延迟和成本，失败以后是否更难恢复，以及这些收益能不能在固定数据和配置上重复出现。

Zuno 的历史里已经出现过一个很小但很说明问题的例子。2026-06-20 的 HotpotQA `limit=5` retrieval-only smoke 一开始记录到 local GraphRAG 的 sampled Recall@5 低于 baseline；连续修复 fusion、seed expansion、entity alias 和 ranking 后，同日 rerun 才恢复到与 baseline 对齐。这个结果只能说明**那一小批样本上的回退被消除**，不能证明 GraphRAG 普遍更好，更不能反推客户反馈的根因。详细边界记录在 [`project-fact-provenance.md`](../../governance/project-fact-provenance.md) 的 PF-031 与相关 eval 代码中。

这正是 09 的出发点：Observability 帮助工程师解释一次执行发生了什么；Evaluation 判断结果是否足够好，以及多出来的复杂度是否值得留下。两个问题都需要数据，但它们服务的决策不同。

### 先回答发生了什么，再回答结果好不好

假设用户报告“系统把同一份材料提交了两次”。

Trace 里可能看到两个 HTTP span，也可能因为 sampling 只看到一个。单看 Observability 不能决定现实世界到底发生了几个 Effect。事故调查应该先回到 06 的 PreparedAction、Attempt、EffectReceipt 和 Reconciliation，确认哪个逻辑动作真正发生；再用 Runtime Plan、Security decision、Delivery 和 Trace 拼出为什么走到那里。

同样，Domain 是否正式提交，要查 DomainVersion 和 AdmissionReceipt；某次授权是否有效，要查 08 的耐久安全事实。Telemetry 非常适合关联和解释，但它不应该成为这些 Owner 的替代数据库。

09 因此传播最小的 correlation identity，让工程师能够从 request 找到 run、step、retrieval、model、capability、tool 和 admission；这些 id 用于定位，不自动变成业务主键、幂等 key 或授权 token。

OpenTelemetry / OTLP-compatible contract 是合适的通用边界，LangSmith 可以作为 Agent / LLM Trace 和 Eval 的 Provider，但业务恢复不能依赖某一个 tracing SaaS。Exporter 故障时，普通低优先级 telemetry 可以 buffer、retry 甚至丢弃；Domain、Effect 和 Security 的耐久事实仍然成立。

敏感数据也不能为了“方便排障”进入所有 span。Baggage 和普通日志优先传播 opaque ref；材料正文、PII、Secret 和完整授权内容只有在策略允许且确有诊断价值时进入受控观测路径。尤其 Secret 不因为 trace 很方便就获得例外。

### 一次分数没有可比上下文，就不能支持架构决策

Evaluation 需要把实验输入也当成版本化事实。

今天一百个 case，明天改了二十个标签，如果两次分数直接放到同一张图上，团队无法判断变化来自模型还是数据集。DatasetVersion 因而需要稳定 case identity、材料引用、任务类别、标签或 expected evidence、标注来源和数据政策。

模型、Prompt、Retrieval config、Capability / ProviderVersion、ProcessingSpec 和 Judge 同样会改变结果。一个“82 分”只有和这些配置一起保存，才是一条可以复现和比较的证据。

训练和调参暴露也要记录。已经被 Prompt tuning、few-shot 或模型训练看到的 case，不能在不说明的情况下继续充当独立 test。真实法院材料因为治理限制无法进入 Eval 时，也不能偷偷换成合成集以后仍宣称“法院质量已经验证”。

能用 deterministic checker 的地方优先不用 LLM Judge。引用是否存在、JSON 是否合法、action hash 是否一致、是否产生重复 Effect，都有更稳定的程序化判断。开放式法律论证和表达质量才更适合 Judge；Judge 自己也需要版本、校准和人工金标准。

当 Judge 不可用、样本不足、凭证缺失或 baseline 根本不可比时，评测没有资格给出 Pass 或 Fail。Target 用 BLOCKED / `MEASUREMENT_BLOCKED` 表达这种“还不能判断”，防止流水线为了有一个绿色数字而把未知写成成功。

### 真实专业工作应该反哺评测，但不能把每次人工修改直接当成标签

离线 Benchmark 很重要，却很难提前覆盖真实案件中的所有失败。系统进入专业人员工作以后，会自然产生另一类信号：某个候选经常被改日期，某类检索总要人工补找证据，某个模型在多主体案件里经常混淆行为人，某种 Agentic Retrieval 经常多跑几轮却没有找到新材料。这些现象比“模型在某个公开集合上又提高两分”更直接地告诉团队产品还在哪里需要改进。

09 应该接住这些信号，但不能直接复制业务数据库当训练集。02 中的 HumanDecision 表示专业人员当时对具体案件做了什么业务判断；它可能受到新证据、案件策略、表达偏好和后续更正影响。只有在用途、权限、脱敏、样本选择和 Reviewer protocol 都满足以后，某些投影才有资格进入 Eval Dataset。

一个专家把模型生成的句子重写得更简洁，适合分析表达偏好，不一定能证明原答案法律错误；一个 Finding 因新补充协议而失效，说明世界变了，也不能直接把旧模型标成错。相反，如果多个独立案件里同一 Provider 持续漏掉同类事件，而且专业人员在相同材料条件下反复补正，这才更可能形成稳定的 failure class 和 Regression case。

这样形成的闭环不是“线上数据自动训练模型”，而是：真实工作发现稳定失败 → 人工和规则把失败归类 → 形成受治理 Task Class / Regression case → 研究或工程提出修改 → 新 Provider / Prompt / Retriever / Agent Harness 在同一组条件下重测 → 通过以后再进入受控发布。历史 HumanDecision 保持原样，新 Eval 只判断新的实现有没有改善。

### 研究资产要转成资格体系，而不是只留下论文分数

葛季栋 / LIPLAB 已有的 Benchmark 与测试研究可以成为这套体系的上游，而不是停留在论文附录。

LawBench 的价值在于把法律能力拆成不同认知层和任务类别。对 Zuno 来说，它更适合帮助建立 Provider capability profile：一个模型可以在事件理解上合格、在复杂法律适用上不合格，而不是用一个总分决定“全局替换”。

LJPCheck 的功能测试思路更接近长期 Regression。模型总体准确率没有明显变化，并不代表事实扰动、边界条件、复杂主体或特定失败模式没有退化。Zuno 应优先把真实 Bad Case 和研究中的功能性 failure taxonomy 转成稳定测试，而不是只积累更多平均分。

CMDL 一类复杂多主体数据集则适合扩展 Task Class 的边界。Provider 在简单单主体材料上通过资格，不意味着它自动有资格处理多主体、跨行为关系和案件级一致性更复杂的工作。

这些研究资产只能提供方法、数据和问题结构。最终 release evidence 仍要绑定 Zuno 当前 DatasetVersion、材料治理条件、ProviderVersion、配置和真实任务范围。公开 Benchmark PASS 不等于法院场景 Production qualification。

### Release 需要看关键失败，不只看平均分

法律系统里的某些错误不能被高平均准确率抵消。

一次越权读取、一次重复高风险 Effect、正式引用无法回到材料版本、旧 WorkProduct 已经 stale 却继续发布，这些事件即使只发生一次，也可能比平均分高两点更重要。Release Evaluation 因此同时看 aggregate metrics 和 critical failure taxonomy。

任务类别也必须拆开。简单条款定位、跨文档争议分析、长期 Agent 任务和带现实副作用的流程拥有不同目标。把它们混成一个“Agent Success Rate”，简单题数量很容易掩盖最需要架构保护的路径。

复杂机制还会在准确率以外付出代价。Reflection 可能增加 token 和 P95；Multi-Agent 可能增加协调失败；GraphRAG 增加构建与查询成本；强模型可能提高费用并受地域策略限制；Native Runtime 增加状态和恢复面。

所以同一实验要尽量一起看 evidence sufficiency、citation correctness、unsupported claim、reviewer acceptance、recovery correctness、duplicate effect、latency、token、cost、Replan / reconcile 频率和人工介入。不是所有项目都需要同一套指标，但架构选择必须把主要收益和主要成本放在同一个可比上下文里。

### 产品价值还要看“专业人员更快形成可验证成果”

模型 Benchmark 只能说明局部能力。Zuno 如果最终定位为案件研究与审理辅助工作空间，长期价值还需要回到专业工作本身。

同一类案件中，系统是否减少了专业人员寻找关键材料的时间；候选事件、冲突和法律依据是否降低了从零整理案件的工作量；机器结果被直接接受、局部修改、完全拒绝或要求补证的比例怎样变化；形成一份拥有完整引用和来源的 review-ready WorkProduct 需要多少人工步骤；新 Provider 上线以后，质量提升是否抵消了额外 token、latency 和运维复杂度——这些指标比“聊天回答看起来更聪明”更接近产品价值。

Target 不预设具体改善数字，因为当前没有真实法院工作量和对照实验支持。09 的责任是把这些问题变成可测量设计，并把 `Measurement Needed` 与已经建立的 Evidence 分开。只有当真实专业流程显示稳定收益时，研究资产和 Agent 机制才从“技术可行”升级成“产品值得长期维护”。

### Evaluation 还负责帮助删除复杂度

一个功能做出来以后，团队天然倾向于寻找证明它有价值的案例。09 需要主动做相反的事：设计 baseline、ablation 和 kill test。

GraphRAG 对比 Hybrid Retrieval；Memory on/off；Reflection on/off；更贵模型对比满足最低要求的便宜模型；Generic Host + Legal Backend 对比 Native Runtime。尽量固定语料、task class、模型和预算，只改变需要验证的机制，才能解释边际收益来自哪里。

如果某个机制长期没有稳定收益，正确动作不是继续寻找更漂亮的 Dashboard，而是关闭它、缩小使用范围或回到 baseline。已经实现不构成架构永久保留权。

Evaluation 也不能单独宣布整个系统 Production Ready。一组 Dataset 上的 PASS 只证明这组数据、配置、commit 和 profile 达到定义门槛。容量、HA / DR、安全 qualification、真实外部系统、故障恢复、运维和法院侧结果仍需要各自 Evidence。

Observability 也不应该无限收集。设计前先列最需要回答的问题：一次结果为什么被拒绝，哪个版本导致质量回退，现实 Effect 是否重复，哪个步骤放大了成本，撤权以后是否仍有访问。然后只记录足以回答这些问题的事件和属性。日志越多并不自动让系统更可解释。

### Current / Target / Gap

**Current：** 仓库已经有 RAG / GraphRAG eval、LLM judge、LangSmith trace verification 和 2026-06-20 的小样本 GraphRAG regression / rerun 证据。它们证明评测基础和局部研发迭代存在，不证明完整 Release Evaluation、真实 HumanDecision feedback loop、生产级 Observability 或法院级 benchmark 已经建立。

**Target：** 09 提供稳定 correlation、Telemetry / Eval 数据模型、Dataset / Judge / Config 版本和可比较实验；把经过治理的真实专业反馈转成 Task Class、Regression 与资格证据；让 05 的 Provider qualification 和架构复杂度可以由 baseline、ablation 与 kill test 决定。业务 Truth、Mandatory Audit 和正式发布资格仍由对应 Owner 和治理条件共同决定。

**Gap：** 真实业务 task class 数据集、专家反馈治理、Judge 校准、critical failure 门槛、跨模块恢复 Eval、容量和成本基线、外部 Tool / Security 场景、真实法院人员评测、产品效率指标以及完整 Production qualification 仍需要证据。没有测量时继续写 Unknown / BLOCKED，不制造数字。

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
