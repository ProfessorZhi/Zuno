# 02 Legal Domain & Work Product（法律领域与工作成果）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail_design: candidate-v1 -->

## Part A — Human Narrative

### 一条模型结论怎样变成长期业务记录

一项合同争议分析已经接近结束。检索系统找到了付款条款，模型判断付款已经逾期，并给出一段事实摘要。专业人员复核后发现模型把补充协议的签署时间写错了一天，于是修改这处事实，接受剩余判断，并把它放进正式工作成果。

如果系统只保存最后那段文本，今天看起来没有问题。几周后再回来看，却很难回答：机器原来建议了什么，专家具体改了哪里，采用的是合同 v2 还是 v3，这个结论引用了哪一页材料，后来新增证据以后旧成果为什么还在页面上。

02 存在于这个“结果开始需要长期负责”的时刻。它保存的不是模型运行历史，而是法律业务愿意长期承认、版本化、引用和复核的事实。Matter、正式材料版本、Evidence、Finding、HumanDecision 和 WorkProduct 因此拥有比一次 AgentRun 更长的生命周期。

对一次性 Demo，最简单的 `result` 表完全够用。只有当结果需要被交付、复核、追责，或者会被后来的证据改变时，才值得建立更明确的领域边界。

机器先产出候选，是因为“算出来”还没有业务权威。检索可能漏材料，模型可能误读，当前 Scope 可能不完整，专业人员也可能修改或拒绝结果。02 在满足材料版本、专业规则、必要人审和当前安全条件以后，才把需要长期保存的内容接纳进正式领域状态。

工程参考把这个边界压缩成：

```text
EvidenceCandidate（证据候选）
    ≠
Evidence（正式证据）
```

这行符号只有在前面的业务区别已经理解以后才有价值。候选可以被重新计算和替换；正式 Evidence 一旦成立，就需要保留来源、版本和后续失效关系。

### 正式提交必须能跨过崩溃窗口

正式准入最危险的故障并不是数据库事务回滚，而是事务已经成功、调用方却还不知道。

假设 Runtime 把一个已经复核的 Finding 交给 02。Domain transaction 完成，新 DomainVersion 已经写入；Runtime 正准备更新自己的 Checkpoint 时进程崩溃。新的 Worker 接管以后，只看到旧 Checkpoint，很容易再次提交同一份结果。

如果 02 只返回一次 `200 OK`，这次成功已经随着进程消失。恢复系统需要一个可以重新查询的业务完成证明。Target 因此让正式准入在同一业务事务里留下 `AdmissionReceipt（正式准入回执）`，它绑定这次准入的因果、输入和对应 DomainVersion。

重启后的顺序由此很清楚：先查询 DomainVersion + matching AdmissionReceipt，确认正式业务世界是否已经变化；如果已经提交，Runtime 修复自己的进度，不重复写正式事实；如果 Receipt 不存在，才按当前版本和当前条件重新决定是否提交。

这也是为什么 Domain 和 Runtime 各自保留状态。Checkpoint 对控制恢复很重要，但它只能说明 Controller 上次记到哪里。正式法律结果是否成立，由 02 的耐久事实证明。两边通过 causation refs 互相定位，却不共享一个万能 `completed`。

正式准入还需要乐观并发语义。两个专业人员或一个人和后台 Agent 都可能基于 DomainVersion V10 工作：一边新增 Evidence，另一边准备接受旧 Finding。后一个提交如果不声明自己依据的版本，就可能把“基于旧世界的判断”写进新世界。

因此提交会携带 expected DomainVersion 一类因果条件。发生版本冲突时，调用方重新读取当前事实、合并或重新判断。冲突不是普通数据库噪音，它表示原来的业务前提已经变化。

### 新证据进来后，历史不能被改写

下午又上传了一份关键补充协议。它改变了付款日期的认定。

这时 WorkProduct V3 有两件事同时为真：它上午确实作为正式成果存在过；它现在已经不适合继续当作当前有效结论。最省事的做法是直接修改 V3，或者把它删掉再生成 V4，但这样会让已经交付的旧版本和审计记录指向一个从未真实存在过的历史。

02 因而保存版本和有效性变化，而不是重写过去。V3 可以被标记为需要复核、被新版本取代或因某条新 Evidence 失效；V4 再基于新的正式事实形成。历史查询仍能回答“当时为什么得到 V3”，当前视图则能回答“现在应该使用哪一版”。

正式工作成果的引用也必须跟随这种时间语义。Retriever 今天重新跑一次，可能因为 chunk、Embedding、reranker 或索引版本变化找到另一段文字；历史 WorkProduct 需要回到提交当时真正采用的材料版本和稳定位置。

所以检索层提供当前候选的 CitationLineage，02 在正式准入时保存 WorkProductCitationBinding。前者帮助解释“为什么这次检索找到这里”，后者保护“这份正式成果当时引用了什么”。索引可以重建，正式历史引用不能跟着漂移。

新增 Evidence 也不必让全案所有结果重算。只要正式对象保存了足以解释重要依赖的关系，系统就可以沿 Evidence、Finding、WorkProduct 的业务因果判断哪些成果可能受影响。Target 不要求把每个 token、每次 Reflection 或模型中间变量都升级成长期领域对象；那些过程继续留在 Runtime、Capability、Model 和 Observability。

### 人工判断、审批和纠错属于不同责任

专业人员点击“接受”一个 Finding，表达的是法律业务判断。管理员批准把某份成果发送到外围系统，表达的是安全或治理决定。两种动作可能在同一个页面上出现，但它们不能拥有同一种后果。

HumanDecision 因此跟随被判断的业务对象和版本，记录接受、修改、拒绝或要求补证等专业决定。ApprovalDecision 则由 08 管理，约束具体受保护动作。专家认可结论不自动授权外发，管理员批准发送也不自动把模型文本变成正式法律事实。

真实系统还必须允许更正自己。材料元数据可能录错，人工决定可能需要修正，WorkProduct 也可能发现引用绑定错误。直接 `UPDATE` 历史行会让已经发生的业务时间线消失。更稳妥的方式是保留原记录和更正原因，形成新版本、supersede / invalidation 或受治理的修正关系。

冲突证据也不应该为了“数据库干净”被覆盖。两份证言完全可以同时都是正式 Evidence，却互相矛盾。Domain 保存它们的来源和业务身份，Finding 与 HumanDecision 再解释怎样处理冲突。正式接纳表示“Zuno 当前愿意长期负责这条记录及其来源”，不表示世界从此没有不确定性或专业分歧。

### 什么时候不需要完整 Domain Kernel

如果产品只是一次性问答，没有长期 WorkProduct、人工专业决定、正式版本历史和失效传播，一个轻量 answer record 足以完成业务。为了 DDD 完整而提前建立大量领域对象，只会增加 Migration、事务和维护成本。

即使进入正式业务，一级对象也应该克制。新增对象前需要问：它是否有独立生命周期，是否会被长期引用，是否需要人工操作或独立版本语义。如果只是某个 Capability 的中间 JSON、一次 Eval 标签或 UI projection，就不应该进入 Canonical Domain。

完整 Domain Kernel 的成本包括版本管理、并发控制、准入事务、依赖传播和历史保留。只有长期业务事实真的需要这些能力时，这些成本才有意义。

### Current / Target / Gap

**Target：** 02 拥有正式法律业务状态、DomainVersion、Formal Admission、AdmissionReceipt、WorkProduct 历史引用和正式失效关系；机器候选、Runtime 控制状态、知识派生和外部 Effect 仍由各自 Owner 管理。

**Current：** 文档中的七对象 Kernel、完整 Admission transaction、版本冲突处理和失效传播属于 Target 设计，不能因为文档完整就视为已经实现。现有代码、Migration 和测试能证明到哪里，只以 `docs/evidence/` 和代码证据为准。

**Gap：** 字段级冻结、真实并发冲突、Domain commit / Checkpoint crash-window 故障注入、Migration 方案、跨对象失效传播和真实法院工作流成本仍需要独立验证。

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
