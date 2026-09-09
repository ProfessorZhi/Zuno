# Zuno 目标架构：让每一种事实都有自己的凭据

法律智能系统更危险的故障，常发生在一次执行表面成功、却留下几种含义完全不同的“成功”时。显式模型报错反而更容易识别和处理。

设想一个合同争议事项。系统已经从合同新版本中找到付款条款，模型完成了逾期判断，专业人员也接受了其中一个结论。就在正式结果提交以后，运行进程崩溃，新的 Checkpoint 还没来得及写入。稍后，系统又向外围平台提交一项动作，请求在收到响应前超时。

此时至少有四件事必须分别回答：模型有没有完成计算，任务控制走到了哪里，正式法律工作成果是否已经成立，现实世界里的外部动作究竟有没有发生。把它们都压成一个 `success`，系统在顺利运行时看不出问题；一旦重启、重试、补交材料或人工复核，错误就会沿着这些模糊状态扩散。

Zuno 的 Target Architecture 从一个很朴素的规则出发：**不同种类的事实，由不同的责任域证明；一个事实跨越边界以后，必须留下足以支持恢复和审计的因果记录。** 系统边界先由这条规则确定，Agent、RAG、GraphRAG、模型网关和工作流框架再作为实现手段进入设计。

Target Architecture 只定义设计阶段的跨责任边界。模块内部 Contract、状态机和事务细节进入 [`docs/modules/`](../modules/README.md)；长期架构决策进入 [`docs/decisions/`](../decisions/README.md)；代码、测试、性能和生产资格只有在 [`docs/evidence/`](../evidence/README.md) 出现真实证据以后，才属于 Current。研究和外部方案进入 [`docs/research/`](../research/README.md)，用于提出和校准设计，不构成实现证明。

<!--
status: normative-target
architecture_state: ACCEPTED_TARGET
overall_architecture_state: ROUND_02_FROZEN
target_logical_module_count: 9
final_module_count: 9
module_decomposition_gate: OPEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_detail_freeze: NOT_YET
implementation_authorization: NO
owner: Cross-cutting Architecture Owner
canonical_question: Zuno 作为一个长期法律智能工作系统，应该怎样划分事实权威、执行控制、知识能力、安全和现实副作用，使系统可以解释、恢复和演进？
project_source: docs/project/README.md
module_source: docs/modules/
decision_source: docs/decisions/
evidence_source: docs/evidence/
research_source: docs/research/
-->

## Part A — Human Narrative（人类技术叙事）

### 简单法律问答保持短路径

简单法律问答没有必要承担这套复杂度。用户询问“合同第 8 条约定了什么”，系统只需要确认访问范围，读取材料，完成检索和生成，再检查引用与发布条件。受控 RAG 加普通应用服务已经能够完成这类任务。

复杂性来自结果开始拥有生命周期以后。

一个真实事项可能同时存在起诉状、答辩材料、合同、补充协议、扫描附件和后续补交证据。合同已经更新到 v3，某份扫描附件还在 OCR，聊天记录刚刚补入。对于“付款日期是什么”这个问题，现有材料也许已经足够；对于“全部违约金额是否能够确认”，缺失附件可能使任务根本不具备完整判断条件。

材料准备好以后，系统会继续做事件抽取、冲突识别、类案检索和法律适用分析。机器能够产生很有价值的候选，但这些候选会被专业人员接受、修改或拒绝。新的证据进入以后，昨天成立的 WorkProduct 也可能需要重新判断。任务如果持续几十分钟，期间还会出现权限变化、模型失败、服务重启和外部系统超时。

结果进入长期生命周期以后，系统必须持续回答一组比“模型输出是什么”更难的问题：当时依据的是哪一版材料；知识是否覆盖了当前任务需要的范围；哪些内容只是机器候选；哪些结果已经成为正式业务事实；谁做过专业判断；旧结果为什么失效；崩溃以后应该相信哪一份记录；外部动作究竟有没有真实发生。

Zuno 的架构就是为这些问题服务。简单任务继续保持短路径；只有材料版本、长期状态、正式接纳、人工决定或现实副作用真正出现时，系统才引入对应的复杂机制。

### 一项法律工作会同时留下五类事实

这些事实的 Authority、生命周期和恢复依据彼此不同。

| 事实类型 | 典型内容 | 谁拥有最终解释权 | 失败以后应该相信什么 |
|---|---|---|---|
| 材料与知识事实 | `DocumentVersion`、`KnowledgeGeneration`、`ReadinessDecision`、检索 lineage | `DocumentVersion` canonical identity 归 Legal Domain & Work Product；`KnowledgeGeneration`、`ReadinessDecision` 与检索 lineage 归 Knowledge & Evidence | 正式材料版本读取 02 的领域事实；知识派生与任务就绪读取 03 的耐久事实 |
| 机器候选 | `EvidenceCandidate`、Finding Proposal、模型或算法输出 | 产生候选的 Knowledge / Capability / Model 路径，没有正式业务权威 | 候选本身及其来源、版本、模型/能力调用记录 |
| 正式法律事实 | Evidence、Finding、HumanDecision、WorkProduct、DomainVersion | Legal Domain & Work Product | Domain 的耐久提交和匹配的 `AdmissionReceipt` |
| 运行控制事实 | AgentRun、PlanVersion、StepRun、Checkpoint、等待和取消 | Agent Runtime & Control | 当前有效计划、步骤状态和耐久 Checkpoint |
| 现实副作用事实 | `PreparedAction`、实际 Tool Attempt、`EffectReceipt`、Reconciliation 结果 | Tool Runtime & Effects | 外部动作身份、真实尝试和确认后的结果 |

Security & Governance 横跨这些事实之间的转换。它判断某个受保护动作在**现在**是否仍然被允许，必要时要求 Approval 和审计先落盘。Observability & Evaluation 记录、解释和评测整个过程，但不因为“看见了”某个事件就拥有该事件的业务权威。

这些事实边界直接约束后续的完成证明、恢复顺序、版本新鲜度和权限判断。

`KnowledgeGeneration lifecycle != task-level ReadinessDecision`：知识构建完成到什么程度，与当前任务是否已经拥有足够材料，是两个问题。

`EvidenceCandidate != Evidence`：机器找到或生成的候选，与业务正式接受的证据，是两个生命周期。

`CitationLineage != WorkProductCitationBinding`：检索为什么找到某段文本，与历史 WorkProduct 当时正式引用了哪一版材料、哪个稳定位置，也属于不同事实。

一次模型调用成功、一个 Runtime Step 完成、一个 Domain 事务提交、一个外部 Effect 被确认，分别证明不同事情。恢复时先确定当前问题属于哪一种事实，再读取对应 Owner 的完成证明；全局 `success=true` 无法承担这个角色。

**四次跨边界动作让信息获得更强的业务语义。**

Zuno 的主要工程边界都出现在“某种信息准备获得更强语义”的时刻。正常流程中这些边界只增加必要约束；材料不完整、进程崩溃、权限变化或网络结果未知时，它们决定系统依据什么事实继续收敛。

**材料进入知识系统。** 一份正式材料先获得稳定 `DocumentVersion`。OCR、切分、Embedding、图结构和索引围绕它形成 `KnowledgeGeneration`，这些派生可以因为算法升级而重建。当前任务真正开始使用这些知识以前，还要形成面向任务范围的 `ReadinessDecision`。一百份材料处理完成九十八份，并不能自动推出“全案已经 Ready”；缺少的两份可能恰好决定当前问题。

**机器候选进入正式业务状态。** 检索、模型和专业 Capability 可以产生 EvidenceCandidate 或 Proposal。需要长期保存的法律结果进入 Legal Domain 后，Domain 根据材料版本、专业规则、必要的人审与当前安全条件决定是否接纳。接纳事务同时形成新的 DomainVersion 和 `AdmissionReceipt`。Receipt 记录“这个正式结果为什么成立”的耐久因果凭据，后续恢复以这份事实确认正式提交是否已经发生。

**运行进度与业务提交分开。** Runtime 负责计划和执行，却不能因为某个 Step completed 就宣告正式法律事实已经成立。Domain commit 可以先于下一次 Checkpoint 成功；Checkpoint 也可能记录“调用已经返回”，而 Domain 最终拒绝候选。两种状态互相引用，但拥有不同 Authority。

**本地意图进入现实世界。** 创建记录、发送通知、向外围平台提交材料之前，Tool Runtime 先生成稳定 `PreparedAction`，固定 operation identity 和动作内容。远端明确确认后才形成 `EffectReceipt`。如果请求超时，本地只知道通信中断，并不知道远端没有执行还是已经执行但响应丢失。这个状态必须保留为 Outcome Unknown，随后进入 Reconcile。

Security 在每一次受保护的跨越前重新判断当前权限、数据政策、Approval 和 Secret 条件。检查点集中在真正改变业务事实、暴露受保护数据或影响现实状态的边界，低风险纯计算继续保持较轻路径。

### 九个责任域来自事实 Authority

前面的事实类型和跨边界动作稳定以后，九个长期 Owner 随之确定。每个责任域存在，是因为有一类事实需要唯一的最终解释权和恢复依据。

| 责任域 | 为什么存在 | 它拥有的权威 | 明确不拥有的事实 |
|---|---|---|---|
| **01 Application & Integration** | 给专业用户、法院系统和 Generic Host 一个稳定产品边界 | Matter / Scope 的产品组合、调用入口、发布和交付语义 | 不重新裁决 Domain、Knowledge 或 Security 的结论 |
| **02 Legal Domain & Work Product** | 让 Matter、DocumentVersion 与正式法律结果拥有长期身份、版本、接纳和失效语义 | Matter、DocumentVersion、Evidence、Finding、HumanDecision、WorkProduct、DomainVersion、Admission causation | 不把机器候选或 Runtime completed 当正式事实 |
| **03 Knowledge & Evidence** | 围绕正式 DocumentVersion 构建可重建知识、任务就绪和检索候选 | KnowledgeGeneration、ReadinessDecision、检索 lineage 及相关派生状态 | 不拥有 Matter / DocumentVersion canonical identity，也不拥有正式 Evidence / WorkProduct 的业务接纳 |
| **04 Agent Runtime & Control** | 让长任务可以计划、等待、取消、并发和恢复 | AgentRun、PlanVersion、StepRun、Checkpoint、控制因果 | 不拥有 Domain commit 或外部 Effect truth |
| **05 Capability & Skill** | 把研究算法和专业处理封装成稳定、可替换的能力 | Capability 语义、版本、Provider Conformance 与任务资格 | 不因为 Provider 返回成功就宣布业务结论成立 |
| **06 Tool Runtime & Effects** | 让现实副作用拥有稳定动作身份和结果确认 | PreparedAction、Tool Attempt、EffectReceipt、Reconciliation | 不拥有正式法律结论，也不把网络失败直接等同业务失败 |
| **07 Model Gateway** | 把模型从业务代码中的具体 SDK 变成受控依赖 | Model Role、Provider eligibility、真实调用、用量和成本 | 不拥有专业质量、Domain 接纳或发布决定 |
| **08 Security & Governance** | 让长任务中的权限、审批、数据外发和 Secret 使用持续受控 | AuthorizationDecision、ApprovalDecision、安全审计前置条件 | 不替专业人员做 HumanDecision |
| **09 Observability & Evaluation** | 让系统可以解释发生了什么，并用实验决定复杂度是否值得存在 | Telemetry、Eval run、实验结果和质量证据 | 不拥有 Domain、Security、Knowledge 或 Effect truth |

Platform / Infrastructure 位于这些责任域之下，提供 PostgreSQL、Object Store、Queue、Checkpointer、CAS、Lease、Fencing、Clock、Backup/Restore、Network 和 Secret Delivery 等技术原语。这些能力优先复用成熟平台；数据库事务成功只证明对应技术提交完成，上层业务事实仍由各自 Owner 解释。

Optional Context Provider 也遵循同样边界。它可以向 Runtime 提供经过策略约束的上下文，却不能越过 Knowledge、Domain 或 Security 成为新的事实 Authority。

这九个责任域首先是逻辑 Ownership。它们可以落在同一个 Python 进程里，也可以按工作负载拆成 Worker；是否成为独立网络服务由扩缩容、安全隔离、故障半径和部署生命周期等约束决定，与逻辑模块数量分开。

### 故障恢复先回到 Owner Fact

长任务恢复从当前问题对应的 Owner Fact 开始。离崩溃最近的状态可能只是较弱的 Runtime、Cache、Projection 或通知记录；确认权威事实以后，再修复这些派生状态。

最典型的 crash window 发生在 Domain 和 Runtime 之间。

Runtime 把一个候选交给 Domain。Domain 在事务中完成正式接纳，写入 DomainVersion 和 `AdmissionReceipt`。就在响应返回后、Runtime 写下一次 Checkpoint 以前，进程崩溃。重启以后旧 Checkpoint 仍显示这一步没有完成。

如果恢复逻辑只看 Checkpoint，它会再次提交同一份正式结果。系统应按稳定 causation 查询 Domain：匹配的 AdmissionReceipt 已经存在，说明正式业务提交已经成立。Runtime 随后把自己的控制状态修到与 Domain 一致，使较弱的控制投影重新跟随较强的领域事实。

这种分工也解释了为什么 Runtime 仍然需要 `Single Controller`。复杂任务可以并行派发检索、专业 Capability 和模型调用，但全局计划版本、Barrier、取消和接纳顺序最终由一个逻辑控制者收敛。PlanVersion 激活后保持稳定；新材料进入或计划假设改变时，新结构通过新的 PlanVersion 表达，而不是在旧计划上静默改写已经发生的因果关系。

失败以后还需要先判断它属于哪一种恢复动作。

`Retry != Replan != Reconcile`。

模型服务临时 503，而输入、计划和外部世界都没有变化，可以 Retry 同一步。新的关键证据进入，使原计划假设已经失效，应该 Replan。外部 POST 已经发出但响应丢失，本地不知道现实动作是否发生，此时必须 Reconcile。

第二个典型窗口就在外部 Effect。

Tool Runtime 已经持久化 PreparedAction 并向外部系统发送请求，连接随后超时。这个 timeout 不能直接转换成普通 Failed。再次发送可能重复创建记录或重复提交材料。系统先用稳定 operation identity 或业务唯一键查询过去到底发生了什么；确认结果以后，再形成 EffectReceipt 或对应的 Reconciliation 记录，让 Runtime 继续。

取消也遵循事实边界。Cancellation 只停止未来工作；已经正式提交的 Domain fact 和已经发生的现实 Effect 保持历史事实。晚到结果是否仍可接纳，由对应 Owner 根据版本、因果和当前状态判断。

### 研究成果通过 Capability 与 Evaluation 进入工程

Zuno 的研究背景带来另一类长期变化：论文、实验模型和规则系统不断演进，业务系统却需要稳定依赖。Python wrapper 加一次 Demo 只能证明链路能够运行；长期工程能力还需要稳定语义、版本、资格和评测。

一条更可靠的演进链是：

`Research Artifact -> Capability -> Provider -> Qualified Provider -> Candidate -> Formal Business Fact`

Research Artifact 可以是一篇论文、一个实验模型、一套规则或一个外部工具。Capability 定义稳定的专业语义，例如“事件抽取”“冲突识别”“类案检索”。上层依赖 Capability 的输入、输出、版本和资格条件，不依赖某个具体模型类名。

同一个 Capability 可以先由研究模型实现，后来换成规则系统、LLM、外部服务或新的专用模型。Provider 先通过 Conformance 证明自己满足接口和基础语义，再通过 Evaluation 判断在具体任务上是否值得获得资格。`Provider Conformance != task quality`：能按 Contract 返回结果，只是成为候选 Provider 的起点。

Model Gateway 解决的是另一层变化。Capability 或 Runtime 提出模型角色、质量、上下文、数据政策、时延和预算要求，Gateway 在当前允许的 Provider 中选择模型，记录真实调用和成本。模型供应商可以变化，专业能力的语义不需要跟着 API 名称漂移。

这也给 GraphRAG、Agentic RAG、Reflection、Memory 和 Specialist 一个明确位置。它们首先是可以被评测的实现机制或 Capability 组成方式，不因为研究热点或框架 Feature 就自动获得业务 Authority。机器最终产生的是 Candidate；跨入正式法律事实仍然需要 Domain Admission。

### 时间让安全成为持续决策

长任务把权限问题从“请求入口的一次校验”变成了持续状态。一个 AgentRun 可能运行几十分钟，期间用户角色、Matter 归属、材料密级、模型外发政策、Approval 和 Secret 版本都会变化。

因此，新的受保护动作发生前重新消费当前 AuthorizationDecision。读取敏感材料、向外部模型发送数据、获取 Secret、正式接纳结果和执行高风险 Tool，都应在真正跨越边界时重新确认当前条件。旧授权证明过去某个时刻允许，不代表未来所有动作永久有效。

AuthorizationDecision、ApprovalDecision 和 HumanDecision 分别解决三个不同问题。Authorization 判断当前主体能不能执行某类动作；Approval 表示某个具体高风险动作已经得到安全或治理层批准；HumanDecision 表示专业人员是否接受、修改或拒绝法律结论。三者可能连续发生，却不能互相替代。

时间还会改变业务事实本身。新 `DocumentVersion` 进入以后，Knowledge 判断哪些 Generation 与 Readiness 需要重算；Domain 判断已有 Evidence、Finding 或 WorkProduct 是否过期、需要复核或产生新版本。系统保留旧成果曾经为何成立，同时允许新材料改变“现在应该相信什么”。

这种版本化比覆盖旧记录更重要。法律工作需要解释历史判断，而不是只保存今天最后一次计算结果。

### 复杂度只有在测量中证明收益才保留

Zuno 的目标不是把所有任务都送进最强的 Agent Runtime。一个架构如果只能不断增加模块、Agent 和状态机，却没有能力退回简单方案，最终会把研究灵活性变成长期维护成本。

简单法律问答的 baseline 仍然是受控 RAG。Generic Host 已经能满足 UI、会话和通用工作流时，可以继续使用 Generic Host + Legal Backend。Native Runtime 只有在任务确实需要长期计划、等待、恢复和正式接纳语义时才进入主路径。

GraphRAG 与 Hybrid Retrieval 比较；长期 Memory 与无长期 Memory 比较；Reflection、Specialist、多模型路由和更强模型都需要与更简单方案做对照。Observability 负责说明一次执行发生了什么，Evaluation 负责判断多出来的复杂度有没有带来可重复、可归因的质量、恢复正确性、时延、成本或人工负担收益。

同样的原则适用于基础设施。合理起点是**模块化 Python 后端**，再按资源特征拆分 Knowledge、Model、Tool、Eval 等 Worker。只有独立扩缩容、Secret 隔离、特殊网络出口、更小故障半径、不同部署生命周期或合规边界形成真实约束时，某个逻辑边界才升级成**独立网络服务**。

PostgreSQL、Object Store、Queue、Secret Manager、OpenTelemetry、Checkpointer、模型 SDK 和身份系统优先复用成熟能力。Zuno 应该自己定义的是这些基础设施无法替它决定的业务语义：什么结果正式成立，什么材料足以支持当前任务，哪个外部动作可以安全重试，哪个决定需要人来承担权威。

架构必须允许自己缩小。某项复杂机制长期无法在 Evaluation 中证明收益时，就关闭它、回到 baseline 或恢复共进程部署；这属于正常工程收敛。

### 实施从 Authority、Completion Proof 和 Recovery 开始

这份总体架构冻结的是事实 Authority、跨边界因果和恢复顺序，不冻结数据库、框架、SDK 或部署技术。实施一个责任域时，顺序应该先从“谁拥有事实、什么记录能够证明完成、故障后先相信谁”开始，再进入表结构、API、事务、队列和 Worker。

实施必须保护这些关系：

- 机器结果先作为候选，正式法律事实由 Legal Domain 接纳。
- `KnowledgeGeneration lifecycle != task-level ReadinessDecision`。
- `EvidenceCandidate != Evidence`。
- `CitationLineage != WorkProductCitationBinding`。
- Runtime Checkpoint 证明控制进度，不能单独证明 Domain Commit。
- Formal Admission 留下独立耐久的 `AdmissionReceipt`，供后续恢复确认因果。
- Runtime 的全局控制由 `Single Controller` 收敛，计划变化通过新的 PlanVersion 表达。
- `Retry != Replan != Reconcile`；Outcome Unknown 先 Reconcile，再决定是否继续。
- 外部副作用从 `PreparedAction` 开始，真实结果由 `EffectReceipt` 或 Reconciliation 证明。
- 新的受保护动作重新消费当前 AuthorizationDecision；Authorization、Approval 和 HumanDecision 保持独立 Authority。
- Telemetry 与 Eval 可以解释和评测系统，但不拥有 Domain、Security、Knowledge 或 Effect truth。
- 九个责任域是逻辑 Ownership，不等于九个进程、数据库或网络服务。
- 简单路径继续存在；复杂机制必须通过 Evaluation 证明自己值得保留。

模块状态、Contract、Failure Matrix 和 Persistence 继续进入 [`docs/modules/`](../modules/README.md)。跨模块长期决策进入 [`docs/decisions/`](../decisions/README.md)。研究候选进入 [`docs/research/`](../research/README.md)。代码、测试、故障注入、性能和生产资格进入 [`docs/evidence/`](../evidence/README.md)。

设计先说明系统必须保护什么，再选择最简单的实现；实现结果通过 Evidence 验证、缩小或修正 Target Architecture。代码目录、框架 Feature 和单次 Demo 提供实现或试验信息，不拥有新的事实 Authority。

**研究只用于校准设计方向。**

外部研究只用于验证设计方向，不证明 Zuno 已经实现或验证了相应能力。与本架构关系最直接的研究主要集中在三类问题：Agentic RAG 的多步规划与动态检索，高风险 AI 的 provenance 与审计，以及 Human-in-the-loop 系统中机器建议和人类权威的边界。

这些工作共同支持一个方向：高风险 AI 需要保留来源、版本、过程、人类决定和可恢复的执行记录，并对复杂 Agent 机制进行真实任务评测。Zuno 的具体 Owner、Receipt 和恢复顺序仍然来自项目自己的法律业务约束；是否值得在真实场景长期保留，则要由后续 Evaluation 和工程 Evidence 回答。

---

单个责任域的 Human Narrative 继续进入 [`docs/modules/`](../modules/README.md)；总体 Architecture 的工程 / Agent 精确参考见 [`reference.md`](reference.md)。
