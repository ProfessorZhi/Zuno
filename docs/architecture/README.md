# Zuno 目标架构：让每一种事实都有自己的凭据

法律智能系统最危险的时刻，往往不是模型明确报错，而是一次执行看起来成功了，却留下了几种含义完全不同的“成功”。

设想一个合同争议事项。系统已经从合同新版本中找到付款条款，模型完成了逾期判断，专业人员也接受了其中一个结论。就在正式结果提交以后，运行进程崩溃，新的 Checkpoint 还没来得及写入。稍后，系统又向外围平台提交一项动作，请求在收到响应前超时。

此时至少有四件事必须分别回答：模型有没有完成计算，任务控制走到了哪里，正式法律工作成果是否已经成立，现实世界里的外部动作究竟有没有发生。把它们都压成一个 `success`，系统在顺利运行时看不出问题；一旦重启、重试、补交材料或人工复核，错误就会沿着这些模糊状态扩散。

Zuno 的 Target Architecture 从一个很朴素的规则出发：**不同种类的事实，由不同的责任域证明；一个事实跨越边界以后，必须留下足以支持恢复和审计的因果记录。** Agent、RAG、GraphRAG、模型网关和工作流框架都服务于这条规则，而不是反过来决定系统边界。

本文只描述设计阶段的目标系统。模块内部 Contract、状态机和事务细节进入 [`docs/modules/`](../modules/README.md)；长期架构决策进入 [`docs/decisions/`](../decisions/README.md)；代码、测试、性能和生产资格只有在 [`docs/evidence/`](../evidence/README.md) 出现真实证据以后，才属于 Current。研究和外部方案进入 [`docs/research/`](../research/README.md)，用于提出和校准设计，不构成实现证明。

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
project_source: docs/project/project.md
module_source: docs/modules/
decision_source: docs/decisions/
evidence_source: docs/evidence/
research_source: docs/research/
-->

## Part A — Human Narrative（人类技术叙事）

Part A 解释设计为什么存在。第一次阅读只需要沿着案件、事实、跨边界动作和故障恢复往下读；内部 Contract 名称只在概念已经清楚以后出现。

### A1. 法律智能真正变难的时刻

简单法律问答没有必要承担这套复杂度。用户询问“合同第 8 条约定了什么”，系统只需要确认访问范围，读取材料，完成检索和生成，再检查引用与发布条件。受控 RAG 加普通应用服务已经能够完成这类任务。

复杂性来自结果开始拥有生命周期以后。

一个真实事项可能同时存在起诉状、答辩材料、合同、补充协议、扫描附件和后续补交证据。合同已经更新到 v3，某份扫描附件还在 OCR，聊天记录刚刚补入。对于“付款日期是什么”这个问题，现有材料也许已经足够；对于“全部违约金额是否能够确认”，缺失附件可能使任务根本不具备完整判断条件。

材料准备好以后，系统会继续做事件抽取、冲突识别、类案检索和法律适用分析。机器能够产生很有价值的候选，但这些候选会被专业人员接受、修改或拒绝。新的证据进入以后，昨天成立的 WorkProduct 也可能需要重新判断。任务如果持续几十分钟，期间还会出现权限变化、模型失败、服务重启和外部系统超时。

从这里开始，系统必须持续回答一组比“模型输出是什么”更难的问题：当时依据的是哪一版材料；知识是否覆盖了当前任务需要的范围；哪些内容只是机器候选；哪些结果已经成为正式业务事实；谁做过专业判断；旧结果为什么失效；崩溃以后应该相信哪一份记录；外部动作究竟有没有真实发生。

Zuno 的架构就是为这些问题服务。简单任务继续保持短路径；只有材料版本、长期状态、正式接纳、人工决定或现实副作用真正出现时，系统才引入对应的复杂机制。

### A2. 一件案件里的五种事实

理解 Zuno 最容易的方法，不是先背九个模块，而是先看一项法律工作同时留下哪些事实。

| 事实类型 | 典型内容 | 谁拥有最终解释权 | 失败以后应该相信什么 |
|---|---|---|---|
| 材料与知识事实 | `DocumentVersion`、`KnowledgeGeneration`、`ReadinessDecision`、检索 lineage | Knowledge & Evidence | 稳定材料版本、generation 状态和面向当前任务的就绪判断 |
| 机器候选 | `EvidenceCandidate`、Finding Proposal、模型或算法输出 | 产生候选的 Knowledge / Capability / Model 路径，没有正式业务权威 | 候选本身及其来源、版本、模型/能力调用记录 |
| 正式法律事实 | Evidence、Finding、HumanDecision、WorkProduct、DomainVersion | Legal Domain & Work Product | Domain 的耐久提交和匹配的 `AdmissionReceipt` |
| 运行控制事实 | AgentRun、PlanVersion、StepRun、Checkpoint、等待和取消 | Agent Runtime & Control | 当前有效计划、步骤状态和耐久 Checkpoint |
| 现实副作用事实 | `PreparedAction`、实际 Tool Attempt、`EffectReceipt`、Reconciliation 结果 | Tool Runtime & Effects | 外部动作身份、真实尝试和确认后的结果 |

Security & Governance 横跨这些事实之间的转换。它判断某个受保护动作在**现在**是否仍然被允许，必要时要求 Approval 和审计先落盘。Observability & Evaluation 记录、解释和评测整个过程，但不因为“看见了”某个事件就拥有该事件的业务权威。

这张表决定了后面大量看似细碎的设计选择。

`KnowledgeGeneration lifecycle != task-level ReadinessDecision`：知识构建完成到什么程度，与当前任务是否已经拥有足够材料，是两个问题。

`EvidenceCandidate != Evidence`：机器找到或生成的候选，与业务正式接受的证据，是两个生命周期。

`CitationLineage != WorkProductCitationBinding`：检索为什么找到某段文本，与历史 WorkProduct 当时正式引用了哪一版材料、哪个稳定位置，也属于不同事实。

同样，一次模型调用成功、一个 Runtime Step 完成、一个 Domain 事务提交、一个外部 Effect 被确认，都是“成功”，但它们分别证明不同事情。恢复时最重要的不是寻找一个全局 `success=true`，而是先确定当前问题属于哪一种事实。

### A3. 四次跨边界决定系统是否可信

Zuno 的主要工程边界都出现在“某种信息准备获得更强语义”的时刻。正常流程里这些边界几乎没有存在感；真正的价值体现在材料不完整、进程崩溃、权限变化和网络结果未知时。

**材料进入知识系统。** 一份正式材料先获得稳定 `DocumentVersion`。OCR、切分、Embedding、图结构和索引围绕它形成 `KnowledgeGeneration`，这些派生可以因为算法升级而重建。当前任务真正开始使用这些知识以前，还要形成面向任务范围的 `ReadinessDecision`。一百份材料处理完成九十八份，并不能自动推出“全案已经 Ready”；缺少的两份可能恰好决定当前问题。

**机器候选进入正式业务状态。** 检索、模型和专业 Capability 可以产生 EvidenceCandidate 或 Proposal。需要长期保存的法律结果进入 Legal Domain 后，Domain 根据材料版本、专业规则、必要的人审与当前安全条件决定是否接纳。接纳事务同时形成新的 DomainVersion 和 `AdmissionReceipt`。Receipt 不是为了多造一个对象，它记录的是“这个正式结果为什么成立”的因果凭据，后面的恢复依赖这份事实。

**运行进度与业务提交分开。** Runtime 负责计划和执行，却不能因为某个 Step completed 就宣告正式法律事实已经成立。Domain commit 可以先于下一次 Checkpoint 成功；Checkpoint 也可能记录“调用已经返回”，而 Domain 最终拒绝候选。两种状态互相引用，但拥有不同 Authority。

**本地意图进入现实世界。** 创建记录、发送通知、向外围平台提交材料之前，Tool Runtime 先生成稳定 `PreparedAction`，固定 operation identity 和动作内容。远端明确确认后才形成 `EffectReceipt`。如果请求超时，本地只知道通信中断，并不知道远端没有执行还是已经执行但响应丢失。这个状态必须保留为 Outcome Unknown，随后进入 Reconcile。

Security 在每一次受保护的跨越前重新判断当前权限、数据政策、Approval 和 Secret 条件。这样控制成本集中在真正改变业务事实或现实状态的地方，而不是让每一次低风险计算都经过同样沉重的审批。

### A4. 九个责任域如何从这些边界产生

九个责任域不是先画出来再寻找理由。前面的事实和边界稳定以后，系统自然需要这些长期 Owner。

| 责任域 | 为什么存在 | 它拥有的权威 | 明确不拥有的事实 |
|---|---|---|---|
| **01 Application & Integration** | 给专业用户、法院系统和 Generic Host 一个稳定产品边界 | Matter / Scope 的产品组合、调用入口、发布和交付语义 | 不重新裁决 Domain、Knowledge 或 Security 的结论 |
| **02 Legal Domain & Work Product** | 让正式法律结果拥有长期版本、接纳和失效语义 | Evidence、Finding、HumanDecision、WorkProduct、DomainVersion、Admission causation | 不把机器候选或 Runtime completed 当正式事实 |
| **03 Knowledge & Evidence** | 让材料身份、可重建知识和任务就绪彼此独立 | DocumentVersion ref 上的 KnowledgeGeneration、ReadinessDecision、检索 lineage | 不拥有正式 Evidence / WorkProduct 的业务接纳；DocumentVersion canonical identity 归 02 |
| **04 Agent Runtime & Control** | 让长任务可以计划、等待、取消、并发和恢复 | AgentRun、PlanVersion、StepRun、Checkpoint、控制因果 | 不拥有 Domain commit 或外部 Effect truth |
| **05 Capability & Skill** | 把研究算法和专业处理封装成稳定、可替换的能力 | Capability 语义、版本、Provider Conformance 与任务资格 | 不因为 Provider 返回成功就宣布业务结论成立 |
| **06 Tool Runtime & Effects** | 让现实副作用拥有稳定动作身份和结果确认 | PreparedAction、Tool Attempt、EffectReceipt、Reconciliation | 不拥有正式法律结论，也不把网络失败直接等同业务失败 |
| **07 Model Gateway** | 把模型从业务代码中的具体 SDK 变成受控依赖 | Model Role、Provider eligibility、真实调用、用量和成本 | 不拥有专业质量、Domain 接纳或发布决定 |
| **08 Security & Governance** | 让长任务中的权限、审批、数据外发和 Secret 使用持续受控 | AuthorizationDecision、ApprovalDecision、安全审计前置条件 | 不替专业人员做 HumanDecision |
| **09 Observability & Evaluation** | 让系统可以解释发生了什么，并用实验决定复杂度是否值得存在 | Telemetry、Eval run、实验结果和质量证据 | 不拥有 Domain、Security、Knowledge 或 Effect truth |

Platform / Infrastructure 位于这些责任域之下，提供 PostgreSQL、Object Store、Queue、Checkpointer、CAS、Lease、Fencing、Clock、Backup/Restore、Network 和 Secret Delivery 等技术原语。它们可以非常成熟，也可以完全复用现有平台，但不会因为数据库事务成功就自动拥有更上层的业务语义。

Optional Context Provider 也遵循同样边界。它可以向 Runtime 提供经过策略约束的上下文，却不能越过 Knowledge、Domain 或 Security 成为新的事实 Authority。

这九个责任域首先是逻辑 Ownership。它们可以落在同一个 Python 进程里，也可以按工作负载拆成 Worker；是否成为独立网络服务属于部署问题，而不是架构图上的模块数量问题。

### A5. 故障以后，先找事实再恢复控制

长任务恢复最容易犯的错误，是把“离崩溃最近的状态”当成最可信的状态。Zuno 采用相反顺序：先找到当前问题对应的 Owner Fact，再修复 Runtime、Cache、Projection 或通知状态。

最典型的 crash window 发生在 Domain 和 Runtime 之间。

Runtime 把一个候选交给 Domain。Domain 在事务中完成正式接纳，写入 DomainVersion 和 `AdmissionReceipt`。就在响应返回后、Runtime 写下一次 Checkpoint 以前，进程崩溃。重启以后旧 Checkpoint 仍显示这一步没有完成。

如果恢复逻辑只看 Checkpoint，它会再次提交同一份正式结果。正确顺序是按稳定 causation 查询 Domain：匹配的 AdmissionReceipt 已经存在，说明正式业务提交已经成立。Runtime 随后把自己的控制状态修到与 Domain 一致，而不是让较弱的控制投影推翻较强的领域事实。

这种分工也解释了为什么 Runtime 仍然需要 `Single Controller`。复杂任务可以并行派发检索、专业 Capability 和模型调用，但全局计划版本、Barrier、取消和接纳顺序最终由一个逻辑控制者收敛。PlanVersion 激活后保持稳定；新材料进入或计划假设改变时，新结构通过新的 PlanVersion 表达，而不是在旧计划上静默改写已经发生的因果关系。

失败以后还需要先判断它属于哪一种恢复动作。

`Retry != Replan != Reconcile`。

模型服务临时 503，而输入、计划和外部世界都没有变化，可以 Retry 同一步。新的关键证据进入，使原计划假设已经失效，应该 Replan。外部 POST 已经发出但响应丢失，本地不知道现实动作是否发生，此时必须 Reconcile。

第二个典型窗口就在外部 Effect。

Tool Runtime 已经持久化 PreparedAction 并向外部系统发送请求，连接随后超时。这个 timeout 不能直接转换成普通 Failed。再次发送可能重复创建记录或重复提交材料。系统先用稳定 operation identity 或业务唯一键查询过去到底发生了什么；确认结果以后，再形成 EffectReceipt 或对应的 Reconciliation 记录，让 Runtime 继续。

取消也遵循事实边界。Cancellation 停止未来工作，不会神奇地回滚已经正式提交的 Domain fact 或已经发生的现实 Effect。晚到结果是否仍可接纳，由对应 Owner 根据版本、因果和当前状态判断。

### A6. 研究成果怎样变成工程能力

Zuno 的另一个长期问题来自项目本身的研究背景。论文、实验模型和规则系统不断变化，业务系统却需要稳定依赖。把一个研究模型包一层 Python wrapper 只能证明 Demo 能跑，不能证明它已经成为长期工程能力。

一条更可靠的演进链是：

`Research Artifact -> Capability -> Provider -> Qualified Provider -> Candidate -> Formal Business Fact`

Research Artifact 可以是一篇论文、一个实验模型、一套规则或一个外部工具。Capability 定义稳定的专业语义，例如“事件抽取”“冲突识别”“类案检索”。上层依赖 Capability 的输入、输出、版本和资格条件，不依赖某个具体模型类名。

同一个 Capability 可以先由研究模型实现，后来换成规则系统、LLM、外部服务或新的专用模型。Provider 先通过 Conformance 证明自己满足接口和基础语义，再通过 Evaluation 判断在具体任务上是否值得获得资格。`Provider Conformance != task quality`：能按 Contract 返回结果，只是成为候选 Provider 的起点。

Model Gateway 解决的是另一层变化。Capability 或 Runtime 提出模型角色、质量、上下文、数据政策、时延和预算要求，Gateway 在当前允许的 Provider 中选择模型，记录真实调用和成本。模型供应商可以变化，专业能力的语义不需要跟着 API 名称漂移。

这也给 GraphRAG、Agentic RAG、Reflection、Memory 和 Specialist 一个明确位置。它们首先是可以被评测的实现机制或 Capability 组成方式，不因为研究热点或框架 Feature 就自动获得业务 Authority。机器最终产生的是 Candidate；跨入正式法律事实仍然需要 Domain Admission。

### A7. 安全、人和时间

长任务把权限问题从“请求入口的一次校验”变成了持续状态。一个 AgentRun 可能运行几十分钟，期间用户角色、Matter 归属、材料密级、模型外发政策、Approval 和 Secret 版本都会变化。

因此，新的受保护动作发生前重新消费当前 AuthorizationDecision。读取敏感材料、向外部模型发送数据、获取 Secret、正式接纳结果和执行高风险 Tool，都应在真正跨越边界时重新确认当前条件。旧授权证明过去某个时刻允许，不代表未来所有动作永久有效。

AuthorizationDecision、ApprovalDecision 和 HumanDecision 分别解决三个不同问题。Authorization 判断当前主体能不能执行某类动作；Approval 表示某个具体高风险动作已经得到安全或治理层批准；HumanDecision 表示专业人员是否接受、修改或拒绝法律结论。三者可能连续发生，却不能互相替代。

时间还会改变业务事实本身。新 `DocumentVersion` 进入以后，Knowledge 判断哪些 Generation 与 Readiness 需要重算；Domain 判断已有 Evidence、Finding 或 WorkProduct 是否过期、需要复核或产生新版本。系统保留旧成果曾经为何成立，同时允许新材料改变“现在应该相信什么”。

这种版本化比覆盖旧记录更重要。法律工作需要解释历史判断，而不是只保存今天最后一次计算结果。

### A8. 复杂度必须在测量中证明收益

Zuno 的目标不是把所有任务都送进最强的 Agent Runtime。一个架构如果只能不断增加模块、Agent 和状态机，却没有能力退回简单方案，最终会把研究灵活性变成长期维护成本。

简单法律问答的 baseline 仍然是受控 RAG。Generic Host 已经能满足 UI、会话和通用工作流时，可以继续使用 Generic Host + Legal Backend。Native Runtime 只有在任务确实需要长期计划、等待、恢复和正式接纳语义时才进入主路径。

GraphRAG 与 Hybrid Retrieval 比较；长期 Memory 与无长期 Memory 比较；Reflection、Specialist、多模型路由和更强模型都需要与更简单方案做对照。Observability 负责说明一次执行发生了什么，Evaluation 负责判断多出来的复杂度有没有带来可重复、可归因的质量、恢复正确性、时延、成本或人工负担收益。

同样的原则适用于基础设施。合理起点是**模块化 Python 后端**，再按资源特征拆分 Knowledge、Model、Tool、Eval 等 Worker。只有独立扩缩容、Secret 隔离、特殊网络出口、更小故障半径、不同部署生命周期或合规边界形成真实约束时，某个逻辑边界才升级成**独立网络服务**。

PostgreSQL、Object Store、Queue、Secret Manager、OpenTelemetry、Checkpointer、模型 SDK 和身份系统优先复用成熟能力。Zuno 应该自己定义的是这些基础设施无法替它决定的业务语义：什么结果正式成立，什么材料足以支持当前任务，哪个外部动作可以安全重试，哪个决定需要人来承担权威。

架构因此必须允许自己缩小。某项复杂机制长期无法在 Evaluation 中证明收益时，关闭它、回到 baseline 或恢复共进程部署都属于正常演进，而不是架构失败。

### A9. 从目标架构进入实施

这份总体架构冻结的是事实 Authority、跨边界因果和恢复顺序，不冻结数据库、框架、SDK 或部署技术。实施一个责任域时，顺序应该先从“谁拥有事实、什么记录能够证明完成、故障后先相信谁”开始，再进入表结构、API、事务、队列和 Worker。

下面这些关系构成实施不能破坏的骨架：

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

设计与实施之间保持这个方向：先说明系统应该保护什么，再选择最简单的实现；实现结果通过 Evidence 验证、缩小或修正 Target Architecture。已有代码目录、框架 Feature 或单次 Demo 都不能反过来成为新的事实 Authority。

### A10. 研究校准

外部研究只用于验证设计方向，不证明 Zuno 已经实现或验证了相应能力。与本架构关系最直接的研究主要集中在三类问题：Agentic RAG 的多步规划与动态检索，高风险 AI 的 provenance 与审计，以及 Human-in-the-loop 系统中机器建议和人类权威的边界。

这些工作共同支持一个方向：高风险 AI 需要保留来源、版本、过程、人类决定和可恢复的执行记录，并对复杂 Agent 机制进行真实任务评测。Zuno 的具体 Owner、Receipt 和恢复顺序仍然来自项目自己的法律业务约束；是否值得在真实场景长期保留，则要由后续 Evaluation 和工程 Evidence 回答。

## Part B — Engineering / Agent Reference（工程 / Agent 参考）

Part B 是总体架构的机器可消费索引。它压缩 Part A 已经解释过的设计，不重新定义模块内部字段、最终 enum、数据库表或 Provider API。局部细节仍以 [`docs/modules/`](../modules/README.md) 和 ADR 为准。

### B1. Scope / Global Invariants

1. Target Architecture 固定为 9 个逻辑责任域；逻辑责任域不等于网络服务。
2. `Research Artifact != Capability != Provider != Qualified Provider != Formal Business Fact`。
3. `KnowledgeGeneration lifecycle != task-level ReadinessDecision`。
4. `EvidenceCandidate != Evidence`。
5. `CitationLineage != WorkProductCitationBinding`。
6. Runtime Checkpoint != Domain Commit != Tool Effect != Publication truth。
7. Formal Admission 只有在 Domain mutation 与 matching `AdmissionReceipt` 成立后才构成正式法律业务完成证明。
8. Action Proposal != `PreparedAction` != ToolAttempt != `EffectReceipt`；Outcome Unknown 不得降级成普通 Failed。
9. `Retry != Replan != Reconcile`。
10. AuthorizationDecision、ApprovalDecision、HumanDecision 由不同 Owner 产生，语义不能互换。
11. 新的受保护动作必须消费当前有效安全事实；旧授权不成为长期任务的永久票据。
12. Telemetry / Trace / Eval 解释和评测系统，不升级成 Domain、Knowledge、Security 或 Effect Authority。
13. 跨 Domain Store、Runtime Checkpointer、Tool Effect Store、Security Store 默认不做全局 2PC；恢复依赖 Owner Fact + causation refs。
14. Cancellation 停止未来工作，不全局回滚已经成立的 Domain fact 或已经发生/可能发生的现实 Effect。
15. 简单法律问答保持受控 RAG baseline；Native Runtime、GraphRAG、Reflection、Memory、Specialist、独立服务都必须由测量证明收益。
16. Target 文档不证明 Current 实现；实现资格只来自 Code / Migration / Test / Trace / Eval / runtime Evidence。

### B2. Authority / Ownership Matrix

| Owner | Authoritative facts | Consumes but does not own | Canonical module |
|---|---|---|---|
| 01 Application & Integration | 产品入口、Matter/Scope 组合、Publication / Delivery 语义 | Domain、Knowledge、Security、RunOutcome、Effect refs | [`01`](../modules/01-application-integration.md) |
| 02 Legal Domain & Work Product | Matter / DocumentVersion canonical identity、Claim、Evidence、Finding、HumanDecision、WorkProduct、DomainVersion、AdmissionReceipt、WorkProductCitationBinding | Candidate、Readiness、Runtime、Effect、Security refs | [`02`](../modules/02-legal-domain-work-product.md) |
| 03 Knowledge & Evidence | KnowledgeGeneration、Serving eligibility、ReadinessDecision、EvidenceCandidate、RetrievalResult、CitationLineage | DocumentVersion canonical ref、Security decision | [`03`](../modules/03-knowledge-evidence.md) |
| 04 Agent Runtime & Control | AgentRun、PlanVersion、StepRun、Checkpoint、Ready/Join/Barrier、Retry/Replan/Reconcile control、RunOutcome | Domain Receipt、Knowledge、Capability、Model、Effect、Security facts | [`04`](../modules/04-agent-runtime-control.md) |
| 05 Capability & Skill | Capability semantics/version、Provider conformance、task qualification | Model/Knowledge inputs、Domain admission result | [`05`](../modules/05-capability-skill.md) |
| 06 Tool Runtime & Effects | ToolVersion effect semantics、PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt、RetrySafety | Authorization/Approval、Plan、Domain refs | [`06`](../modules/06-tool-runtime-effects.md) |
| 07 Model Gateway | Model role resolution、Provider eligibility、ModelAttempt、usage/cost truth | Capability quality、Security egress decision、Domain result | [`07`](../modules/07-model-gateway.md) |
| 08 Security & Governance | SecurityEpoch / PolicyVersion、AuthorizationDecision、ApprovalDecision、ModelEgressDecision、AuditRequirement、lifecycle policy decision | Domain HumanDecision、Effect truth、Store enforcement facts | [`08`](../modules/08-security-governance.md) |
| 09 Observability & Evaluation | Telemetry、Eval run、experiment result、quality evidence | 所有业务 Authority refs | [`09`](../modules/09-observability-evaluation.md) |
| Platform / Infrastructure | DB/Object Store/Queue/Checkpointer/CAS/Lease/Fencing/Clock/Backup/Network/Secret Delivery 的物理原语事实 | 所有业务语义 | shared infrastructure |

### B3. Cross-boundary Contract Map

| Boundary | Producer / Authority | Consumer | Minimum durable causation |
|---|---|---|---|
| DocumentVersion -> KnowledgeGeneration | 02 -> 03 | 03/04/01 | stable DocumentVersion refs + generation identity + processing spec |
| KnowledgeGeneration -> ReadinessDecision | 03 | 01/04；必要时 02 admission eligibility | generation + task Scope + requirements + current security refs + coverage/missing requirements |
| Retrieval -> EvidenceCandidate / CitationLineage | 03 | 04/05/02/01 direct QA | source DocumentVersion + stable location + generation/retrieval identity |
| Research -> Capability | 05 | 04/01 | CapabilityVersion + semantics + Provider qualification refs |
| Capability/Runtime -> Model | 04/05 -> 07 | 04/05 | Model Role + policy/budget constraints -> ModelAttempt + usage refs |
| Candidate -> Formal Admission | 04/05/03 -> 02 | 04/01 | candidate/source/version/security/human causation -> DomainVersion + AdmissionReceipt |
| Runtime -> External Effect | 04/05 -> 06 | 04/02/01 | PreparedAction + action hash + ToolVersion + security/approval/audit refs |
| External send -> Effect truth | 06 | 04/02/01 | ToolAttempt + external correlation -> EffectReceipt or ReconciliationReceipt |
| Protected action -> Security decision | caller -> 08 | 02/03/04/05/06/07/01 | principal/scope/resource/action/purpose + SecurityEpoch -> typed decision ref |
| Runtime -> Publication / Delivery | 04/02/06/08 -> 01 | user/host/external boundary | RunOutcome + Domain/Effect/Security refs；01 保持自己的交付事实 |

### B4. Canonical Execution Profiles

**Profile A — Simple controlled QA**

```text
01 request/scope
→ 08 current authorization
→ 02 DocumentVersion refs
→ 03 ReadinessDecision
→ 03 retrieval + CitationLineage
→ optional 07 model call
→ answer policy / publication gate
→ 01 response
```

不要求 Native Runtime、Formal Admission 或外部 Effect；业务约束允许时继续保持这条短路径。

**Profile B — Complex legal analysis**

```text
01 Task
→ 04 AgentRun + immutable PlanVersion
→ 03 Readiness / EvidenceCandidate
→ 05 Capability + optional 07 Model Gateway
→ 04 Step Acceptance / Join / Replan when needed
→ 02 Formal Admission
→ matching AdmissionReceipt
→ 04 RunOutcome
→ 01 publication / delivery
```

**Profile C — Real-world side effect**

```text
04/05 Action Proposal
→ 06 PreparedAction
→ 08 current Authorization / Approval / Audit gates
→ durable ToolAttempt before dangerous send
→ external operation
→ confirmed: EffectReceipt
→ outcome unknown: Reconcile -> ReconciliationReceipt
→ 04 resumes from typed effect result
→ 02/01 consume effect ref when business flow requires
```

### B5. State / Lifecycle Families

本节只冻结跨模块状态语义，不冻结最终 enum 名称。

```text
KnowledgeGeneration:
DECLARED -> PROCESSING -> STAGED/BUILT -> SERVING -> STALE/SUPERSEDED -> REBUILDING

Domain:
Candidate -> Formal Admission -> DomainVersion + AdmissionReceipt
Current valid -> REVIEW_REQUIRED / STALE / SUPERSEDED when new causation invalidates assumptions

Runtime:
AgentRun: CREATED -> PLANNING -> RUNNING -> WAITING_* -> COMPLETED / FAILED / CANCELLED / ABSTAINED
PlanVersion: DRAFT -> ACTIVATED -> SUPERSEDED; ACTIVATED immutable
StepRun: PENDING -> READY -> DISPATCHED -> RUNNING -> ACCEPTED / RETRYABLE_FAILURE / REPLAN_REQUIRED / WAITING / TERMINAL_FAILURE

Effect:
PreparedAction -> ToolAttempt
UNCONFIRMED -> CONFIRMED_EXECUTED / CONFIRMED_NOT_EXECUTED / OUTCOME_UNKNOWN
OUTCOME_UNKNOWN -> RECONCILING -> CONFIRMED_EXECUTED / CONFIRMED_NOT_EXECUTED / MANUAL_RECONCILIATION

Security:
PolicyVersion/SecurityEpoch evolves independently
Authorization/Approval may ALLOW/GRANT and later EXPIRE/REVOKE/SUPERSEDE for future protected actions
```

### B6. Completion Proof / Non-proof

| Question | Completion proof | Explicit non-proof |
|---|---|---|
| 当前任务知识是否够用 | matching `ReadinessDecision` bound to generation + Scope + requirements + current security refs | upload complete、OCR item success、index write、generation build alone |
| 正式法律结果是否成立 | Domain commit + matching `AdmissionReceipt` + applicable DomainVersion | Runtime Step completed、Model 2xx、Candidate existence、Checkpoint |
| Runtime 是否可以推进 | valid active PlanVersion + Step/Join/Barrier state + required external Owner facts | Domain success alone、old Checkpoint alone |
| 外部动作是否发生 | `EffectReceipt` or conclusive `ReconciliationReceipt` | HTTP timeout、transport success、ToolAttempt terminal state alone |
| 新受保护动作是否允许 | current matching Authorization/Approval/Audit/egress/secret facts as required | old ALLOW、historical approval with changed action hash、system-internal caller identity |
| 正式引用历史是否可解释 | `WorkProductCitationBinding` + stable DocumentVersion/location refs | current retriever rank、chunk/vector/graph node id alone |
| 复杂机制是否值得保留 | reproducible Eval / Evidence against simpler baseline | framework feature existence、single demo、research popularity |

### B7. Failure Taxonomy / Recovery Order

恢复顺序统一为：

```text
1. Identify the fact class that is in doubt
2. Query the authoritative Owner fact
3. Compare causation / version / freshness
4. Re-consume current Security eligibility before new protected work
5. Repair Runtime / Cache / Projection / Delivery state
6. Retry, Replan or Reconcile only after the fact is classified
```

关键故障窗口：

| Failure window | Wrong recovery | Required recovery anchor |
|---|---|---|
| Domain committed, Runtime Checkpoint not written | replay Formal Admission from Checkpoint | query matching AdmissionReceipt / DomainVersion; repair Runtime projection |
| Checkpoint says step completed, AdmissionReceipt absent | declare business success | deny formal completion; query 02 causation and re-enter valid admission path |
| external request timed out after possible send | map timeout to Failed and Blind Retry | PreparedAction + ToolAttempt + external correlation -> Reconcile |
| new DocumentVersion arrives during long run | continue old Plan silently | 03 recomputes knowledge eligibility; 02 invalidates/reviews affected facts; 04 Replan if assumptions changed |
| SecurityEpoch changes during wait/retry/resume | reuse old authorization | obtain new current decision before protected use |
| old Plan branch returns late | merge because computation succeeded | compare PlanVersion/input refs; reject stale or require reevaluation |
| cancellation after Domain/Effect success | roll back everything | stop future work; preserve existing Owner facts; compensate only through explicit new business action |

### B8. Retry / Replan / Reconcile / Idempotency

**Retry** requires Plan assumptions、inputs、Capability/Tool semantics、security、budget and external-world assumptions to remain valid. Attempt identity remains stable enough to prevent accidental double accounting or duplicate logical work.

**Replan** creates a new immutable PlanVersion when evidence、requirements、Capability/Tool semantics、budget or other planning assumptions changed. It does not mutate an already activated plan in place.

**Reconcile** belongs to uncertain external Effect truth. 06 resolves Outcome Unknown through remote query、business key、idempotency status or human reconciliation. 04 waits; it does not infer the answer from transport state.

Idempotency namespace is boundary-specific. Domain admission identity、Runtime attempt identity、Tool action identity、Model attempt identity、Publication/Delivery identity are not one global key.

### B9. Version / Freshness / Causation Bindings

| Fact | Must bind to | Freshness owner |
|---|---|---|
| KnowledgeGeneration | DocumentVersion set + processing spec + generation identity | 03 |
| ReadinessDecision | generation + task Scope + requirements + security/policy refs | 03 |
| EvidenceCandidate | DocumentVersion + stable location + generation/retrieval refs | 03 |
| WorkProductCitationBinding | formal WorkProduct/Domain version + stable DocumentVersion/location | 02 |
| PlanVersion | AgentRun + planning causation; immutable after activation | 04 |
| Capability output | CapabilityVersion + Provider/qualification refs + input versions | 05 |
| ModelAttempt | role/resolved Provider/model version + policy/budget refs | 07 |
| PreparedAction | ToolVersion + canonical action content/hash + target + run/plan/step causation | 06 |
| ApprovalDecision | action identity/hash + ToolVersion + policy epoch + expiry | 08 |
| AdmissionReceipt | normalized business input + expected DomainVersion + causation refs | 02 |
| Eval result | dataset/scenario/config/version refs required for reproducibility | 09 |

新的版本不会静默改写旧历史。Owner 判断旧事实是否仍 current、需要 review、stale、superseded 或重新执行。

### B10. Security / Approval / Human Authority

```text
AuthorizationDecision: 当前 principal 是否可执行某类受保护动作
ApprovalDecision: 某个具体高风险动作是否已获得治理批准
HumanDecision: 专业人员是否接受、修改或拒绝法律业务结论
```

三者不能互相替代。

- protected read / retrieval -> current 08 decision before use；
- model egress -> current ModelEgressDecision / provider eligibility；
- Secret -> ref/lease only，Secret Material 不进入普通 Prompt/Checkpoint/Trace/Receipt；
- high-risk Tool -> Authorization + action-bound Approval + required durable Audit before dangerous send；
- Formal Admission -> consume current applicable security facts，专业 HumanDecision 仍由 02 Domain 保存；
- resume / retry / replan / reconcile -> 新的受保护访问重新授权。

### B11. Persistence / Transaction Boundaries

| Store / boundary | Owns durable truth | Must not be promoted into |
|---|---|---|
| 02 Domain store | Canonical Domain + AdmissionReceipt + formal citation binding | Runtime checkpoint |
| 03 Knowledge store/index metadata | generation / manifest / serving / readiness / lineage facts | formal Domain fact |
| 04 Checkpointer/runtime store | control progress / plan / step / interrupt state | Domain or Effect truth |
| 06 Effect store | PreparedAction / Attempt / Effect / Reconciliation facts | Security policy or Domain admission |
| 08 security/audit boundary | policy/decision/approval/audit facts | HumanDecision or Effect truth |
| 09 telemetry/eval store | observations and experiment evidence | any business Authority |
| Platform primitives | physical durability / lease / fencing / queue / clock facts | business completion proof |

跨 Store 默认不依赖 2PC。需要跨边界一致性时，用稳定 identity、causation ref、receipt、owner query、recovery/reconciliation 收敛。

### B12. Build / Buy / Extend / Delete Conditions

**Prefer Buy / Reuse**：PostgreSQL、Object Store、Queue、Secret Manager、OpenTelemetry、Checkpointer、模型 SDK、身份系统、成熟 Policy Engine / Provider primitives。

**Zuno Owns**：Formal Admission、Domain authority、task-level Readiness semantics、Capability professional semantics、Runtime control semantics、Effect confirmation/reconciliation semantics、Security business policy mapping、Eval criteria for Zuno task quality。

**Extend only when measured constraints appear**：独立 Worker/Service、Native Runtime、GraphRAG、Reflection、Memory、Specialist、多模型路由、更强模型。

**Delete / simplify when**：复杂机制不能相对 baseline 提供可重复收益；独立服务没有独立扩缩容/隔离/故障半径/网络/生命周期需求；Generic Host 已经覆盖所需通用能力；简单 QA 不需要长期状态、Formal Admission 或现实 Effect。

### B13. Current / Target / Evidence / Unknown

**Target**：本文 A/B 描述的跨模块 Authority、边界、恢复和复杂度治理语义。

**Current**：只能由 [`docs/evidence/`](../evidence/README.md) 中与当前代码 SHA、Migration、Test、Trace、Eval、runtime evidence 对应的材料证明。总体架构文档本身不升级任何能力为 Current。

**Evidence**：模块文档 B13 指向当前可用的具体证据；需要判断某个 Target 是否已经落地时，优先读取对应 Module B13，再读取 evidence 原文和代码。

**Unknown / Measurement Needed**：Production Readiness、完整 fault-injection coverage、真实法院/业务环境收益、复杂机制 A/B baseline、性能与成本边界、部署拆分必要性，都不能从 Target Design 推导。

`implementation_authorization: NO` 仍然成立；文档完整不等于允许按未冻结 Detail 直接实现。

### B14. Machine Navigation / Source Precedence

机器或 Agent 回答架构问题时按以下优先级读取：

```text
Current Code / Test / Runtime Evidence
> canonical docs/architecture + docs/modules
> accepted ADR
> historical Red/Blue / maintenance history
> docs/research and external research
> speculation
```

定位规则：

- “为什么存在 / 为什么这样分” -> Part A；
- “谁拥有这个事实” -> Part B B2 + 对应 Module B2/B4；
- “跨边界传什么” -> Part B B3 + Module B5；
- “怎样证明完成” -> Part B B6 + Module C1；
- “崩溃后先查什么” -> Part B B7/B11 + Module B8/B9/C4；
- “版本或晚到结果怎样处理” -> Part B B9 + Module C2/C3；
- “权限/Approval/HumanDecision 谁说了算” -> Part B B10 + 08/02；
- “是否已经实现” -> Module B13 + [`docs/evidence/`](../evidence/README.md)；
- “字段/API/Migration” -> Module B14 / ADR / implementation artifacts，不从 Overall Architecture 猜测。

Part A 与 Part B 维护同一套事实。A 可以重写叙事顺序，B 可以提高检索密度；任何修改都不得让两个 Part 在 Owner、Authority、Completion Proof、Recovery、Security 或 Current/Target 上出现两套答案。