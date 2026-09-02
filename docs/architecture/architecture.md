# Zuno 目标架构

Zuno 面向的不是一次模型调用，而是一段可以持续运行、被人工复核、在材料变化后重新判断，并且能够在故障后恢复的法律工作过程。

这类系统最容易出错的地方，往往不在模型本身。材料可能有多个版本，知识索引可能只完成了一部分，模型输出可能只是候选意见，人工决定可能改变结论，运行任务可能在提交以后崩溃，外部系统也可能在请求超时以后已经真实执行了动作。只要这些状态被压成同一个 `success`，系统就会在恢复、审计和责任归属上失去依据。

本文定义 Zuno 的 **Target Architecture**。它回答系统理想状态下应该怎样划分责任、怎样组织长期任务、怎样保存事实以及怎样恢复。代码、数据库表、Provider、部署规模和生产资格不在本文证明范围内；这些内容分别由 [`docs/modules/`](../modules/README.md)、[`docs/decisions/`](../decisions/README.md) 和 [`docs/evidence/`](../evidence/README.md) 继续细化。

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

## 1. 从法律问答到法律工作

简单法律问答并不需要复杂架构。用户询问“合同第 8 条写了什么”时，系统只需要确认访问范围，找到对应材料，生成带引用的回答，再决定是否可以展示。受控 RAG、普通应用服务和一次模型调用已经能够很好地完成这类任务。

复杂法律工作增加了时间和状态。一个事项可能包含起诉状、答辩材料、合同、扫描附件和后续补交证据；其中一些材料尚未完成 OCR，一些刚刚换了版本。系统会进行检索、事件抽取、冲突识别、类案分析和法律适用判断，专业人员可能接受、修改或拒绝这些结果。任务运行期间还可能发生权限变化、模型失败、服务重启和外部系统超时。

因此，复杂任务需要保存的不只是最终文本。系统还要能够解释：当时用了哪一版材料，哪些结果只是机器候选，哪些已经成为正式法律工作成果，谁做过专业判断，旧结果为什么失效，外部动作到底有没有发生，以及重启以后应该从哪一份记录继续。

Zuno 的复杂度从这些问题产生。简单任务仍然走简单路径；只有任务跨越材料版本、长期状态、人工判断、正式业务提交或现实副作用时，才引入更强的领域与运行机制。

## 2. 总体模型

Zuno 的总体架构可以从四个关注面理解。这四个关注面只是阅读上的组织方式，真正的事实权威仍然归属于后文的九个逻辑责任域。

**业务与产品**处理外部请求和正式法律工作成果。外部系统通过 Application & Integration 进入 Zuno；长期法律事实由 Legal Domain & Work Product 保存。一个回答能否发布、一个 WorkProduct 是否正式成立、一个旧版本是否已经失效，都属于这一侧的问题。

**知识与智能**负责把材料转化为可以被任务使用的知识，再把研究算法、检索和模型组织成专业能力。Knowledge & Evidence 管理材料版本、可重建的知识派生和任务级就绪判断；Capability & Skill 定义稳定的专业能力；Model Gateway 管理模型调用和 Provider 选择。

**执行与现实动作**负责长任务怎样继续，以及系统怎样安全地改变现实世界。Agent Runtime & Control 维护计划、步骤、等待、并行、预算和恢复；Tool Runtime & Effects 负责外部副作用的动作身份、执行结果和对账。

**信任与验证**贯穿其他责任域。Security & Governance 决定当前动作是否仍被允许、是否需要审批、数据能否外发以及哪些审计必须先持久化；Observability & Evaluation 记录可观测信息，并通过实验判断系统是否正确、是否值得保持当前复杂度。

这些责任域共同运行在 Platform / Infrastructure 提供的持久化、队列、对象存储、时钟、租约、Secret 交付和网络能力之上。Platform 提供技术原语，却不拥有法律业务成功、运行成功或外部副作用成功。

## 3. 一项任务怎样穿过系统

理解整体架构，最直接的方法是看一项复杂法律任务怎样从材料进入到正式成果。

外部请求首先进入 Application & Integration。这里确定 Matter、用户上下文、任务范围和产品入口，同时组合当前授权、知识就绪以及必要的能力资格。简单问答在这一层就可以进入短路径：检索材料、调用模型、检查引用和发布条件，然后结束。

复杂分析会进入 Runtime。Runtime 根据任务目标形成计划，把检索、专业 Capability、模型和人工等待组织成步骤。Knowledge 提供当前材料和候选证据；Capability 执行事件抽取、冲突识别或其他专业算法；Model Gateway 负责选择符合质量、预算和数据政策的模型。它们产生的是计算结果和候选结论，而不是正式法律事实。

当某个结果需要进入长期业务状态时，Legal Domain 接管判断。Domain 根据材料版本、专业规则、必要的人审和安全条件决定是否接受候选，并生成新的正式版本。正式成果拥有稳定引用，能够回到当时使用的材料，而不是依赖今天的向量索引或图节点。

如果任务还要向外围系统提交、创建或发送内容，Runtime 不直接把模型结果发送出去。Tool Runtime 先固定动作身份和内容，再在当前授权、必要审批和审计条件成立后执行。远端结果确认以后形成可持久化的 Effect 事实；如果网络超时导致结果未知，任务进入对账，而不是盲目重试。

最后，Application 根据正式领域事实决定发布和交付；Observability 记录整条时间线，Evaluation 则把这次执行作为后续质量、成本和恢复评测的输入。

这条流程不是固定流水线。简单问答可以跳过 Runtime、Formal Admission 和 Effect；只有真正需要长期状态的结果才进入 Domain；只有现实副作用才进入 Tool Runtime。架构提供的是可组合边界，而不是要求每个请求经过九个模块。

## 4. 九个逻辑责任域

### 01 Application & Integration

Application & Integration 是 Zuno 与外部世界之间的产品边界。它接收请求，确定 Matter 和 Scope，把内部权威事实组合成调用、发布、交付和失效通知语义，并负责与法院系统、Generic Host 或其他上层产品集成。

它不重新计算 Domain、Knowledge 或 Security 的结论。它的职责是把这些结论组合成稳定的产品行为。例如，Domain 已经宣布 WorkProduct 失效，Application 可以负责通知外部消费者；通知暂时失败不会让失效事实重新变成有效。

### 02 Legal Domain & Work Product

Legal Domain 保存 Zuno 最重要的一类长期事实：哪些材料、Evidence、Finding、HumanDecision 和 WorkProduct 已经正式成立，以及它们怎样随新证据产生新版本或失效。

模型、检索和专业算法可以向 Domain 提出候选，但只有 Domain 能把候选转成正式法律业务事实。这个边界把“机器认为可能成立”和“业务正式接受”分开，也使人工复核和历史审计拥有稳定位置。

### 03 Knowledge & Evidence

Knowledge & Evidence 把正式材料转化成任务可使用的知识。原始材料需要稳定版本；OCR、切分、Embedding、图结构和检索索引属于可重建派生；当前任务是否已经具备足够覆盖范围，则是另一层判断。

因此，知识系统同时关心材料身份、知识生成版本和任务级就绪状态。检索得到的 EvidenceCandidate 和 CitationLineage 可以被后续业务使用，但它们仍然属于候选与检索解释，不能自动升级成正式 Evidence 或 WorkProduct 的历史引用。

### 04 Agent Runtime & Control

Runtime 管理长任务的控制状态。它保存任务计划、步骤、依赖、并行、等待、预算、取消和恢复，使任务不会因为进程重启而失去“原来准备做什么”。

复杂任务可以并发执行多个专业步骤，但全局控制采用 Single Controller 收敛。计划在激活后保持版本稳定；任务结构需要改变时生成新的 PlanVersion，使已经派出的工作仍然拥有明确的因果归属。

Runtime 负责“怎样继续执行”，不拥有正式法律业务事实。一个 Step completed 只说明控制过程完成到某个位置，不能替 Domain 宣布正式结果已经成立。

### 05 Capability & Skill

Capability & Skill 把研究成果、规则、模型和外部服务整理成稳定的专业能力。例如“事件抽取”是一项能力，它可以先由研究模型实现，后来换成规则系统、LLM 或外部服务。

上层依赖的是能力的输入、输出、版本和资格条件，而不是具体 Provider 的类名。Provider 可以替换，Capability 的专业语义保持稳定。新研究成果进入系统时，先通过 Conformance 和 Evaluation 证明自己满足能力要求，再获得任务资格。

### 06 Tool Runtime & Effects

Tool Runtime 负责改变现实世界的动作。只读查询通常可以重试，但创建记录、提交材料、发送通知或触发流程可能产生不可逆副作用。

因此，动作发送前先固定身份和内容；执行后保存真实尝试；远端确认以后形成 EffectReceipt。如果请求超时，系统把结果视为 Unknown，并通过稳定 operation identity 或业务唯一键确认过去到底发生了什么。这个过程就是 Reconcile。

### 07 Model Gateway

Model Gateway 把模型变成受控依赖。Runtime 和 Capability 不直接绑定某个具体 Provider，而是提出模型角色、质量、上下文、数据政策、时延和预算要求，由 Gateway 选择当前合格的模型并记录真实调用、用量和成本。

模型调用成功只证明一次计算完成。专业质量、业务接纳和答案发布仍由对应责任域判断。

### 08 Security & Governance

Security & Governance 持续回答“下一次受保护动作现在是否仍然允许”。长任务可能持续几十分钟，期间用户权限、Matter 归属、数据密级、模型外发政策、Approval 和 Secret 版本都可能变化，因此入口鉴权不能成为整个任务的永久通行证。

授权、审批和专业人工判断属于不同责任。Authorization 表示当前身份和上下文能否做某类动作；Approval 表示某个具体高风险动作已经获批；HumanDecision 表示专业人员是否接受法律结论。三种决定可以发生在同一个流程中，但不能互相替代。

### 09 Observability & Evaluation

Observability 解释系统发生了什么。Trace、Metric 和日志把不同模块的行为关联起来，帮助定位错误和分析性能。

Evaluation 回答另一个问题：这个设计是否值得保留。GraphRAG、长期 Memory、Reflection、Specialist、多模型路由和 Native Runtime 都需要与更简单 baseline 比较。如果额外复杂度没有稳定带来质量、恢复、成本或人工负担收益，它就应该被关闭、缩小或删除。

Telemetry 本身不是业务权威。Trace 丢失不能改变已经发生的 Domain Commit 或外部 Effect；关键审计也不能因为普通 Telemetry 看起来完整就被认为已经满足。

## 5. 事实、版本与权威

Zuno 的核心设计不是某个框架，而是不同事实拥有不同生命周期和权威来源。

| 事实类型 | 主要责任 | 典型内容 | 是否可以重建 |
| --- | --- | --- | --- |
| 正式材料 | Legal Domain | Matter、DocumentVersion | 不能随意重建 |
| 知识派生 | Knowledge | OCR、Chunk、Embedding、Graph、KnowledgeGeneration | 可以从正式材料重建 |
| 机器候选 | Knowledge / Capability / Model | EvidenceCandidate、Proposal、Observation | 可以重新计算，但结果可能变化 |
| 正式法律事实 | Legal Domain | Evidence、Finding、HumanDecision、WorkProduct | 必须保留版本和历史依据 |
| 运行控制 | Runtime | Run、PlanVersion、Step、Checkpoint | 可恢复，但不能替代 Domain truth |
| 外部副作用 | Tool Runtime | PreparedAction、Attempt、Effect、Reconciliation | 必须依据现实结果确认 |
| 安全决定 | Security | Authorization、Approval、Policy Epoch | 有有效期，需要重新判断 |
| 观测投影 | Observability | Trace、Metric、Eval Input | 可以丢失或重建，不拥有业务 truth |

这套划分解决了几个长期系统最容易混淆的问题。

文件上传以后，系统拥有的是一个材料版本；OCR 和向量完成以后，拥有的是一代知识派生；只有当当前任务需要的材料已经达到足够覆盖范围时，才得到 ReadinessDecision。`KnowledgeGeneration lifecycle != task-level ReadinessDecision`。

检索命中以后得到的是候选证据；只有经过领域规则和必要的人审，才可能成为正式 Evidence。`EvidenceCandidate != Evidence`。检索时保存的 CitationLineage 解释系统当时如何找到候选，而正式 WorkProduct 的引用需要绑定不可变 DocumentVersion 和稳定位置。`CitationLineage != WorkProductCitationBinding`。

Runtime Checkpoint 记录控制进度；Domain 记录正式业务事实。它们可以引用同一个 Run 和 Step，却不能互相冒充完成证明。正式 Domain mutation 需要自己的耐久因果证明，工程上使用 AdmissionReceipt 表达。

## 6. 长任务的控制与恢复

长任务必须把计划从模型上下文中拿出来。计划一旦只存在于一次 LLM 对话里，服务重启以后就无法可靠知道哪些步骤已经完成、哪些仍在等待、哪些结果已经晚到。

Runtime 因此维护显式 PlanVersion。简单任务可以是一条确定性的单步计划，复杂任务才需要动态 DAG。计划描述依赖、并行、预算和等待；执行者可以很多，但全局计划只有一个逻辑控制者负责激活新版本和接受步骤结果。

失败以后，系统首先判断“不确定性发生在哪一层”。

**Retry** 适用于原输入、权限和计划仍然有效，只是某次计算暂时失败的情况，例如模型服务短暂返回 503。

**Replan** 适用于任务假设已经变化，例如新材料进入、旧事实失效、Capability 不再可用或原计划不再满足目标。此时继续重复旧步骤没有意义，Runtime 创建新的计划版本。

**Reconcile** 适用于现实结果未知。系统已经向外部服务发送请求，但没有收到响应，无法判断动作有没有真实发生。此时必须先查询现实状态，再决定是否继续。

三者可以概括为 `Retry != Replan != Reconcile`。

一个关键故障窗口能够说明为什么 Domain 和 Runtime 必须分开。假设正式 WorkProduct 已经在 Domain transaction 中成功提交，但进程在写下一次 Checkpoint 之前崩溃。重启以后，旧 Checkpoint 仍然显示步骤没有完成。如果 Runtime 直接重跑，就可能重复提交正式结果。

正确的恢复顺序是先查询 Domain 的耐久事实。如果匹配当前 Run、Plan 和 Step 的 AdmissionReceipt 已经存在，系统先承认正式提交已经发生，再修复 Runtime 的控制状态。恢复从更强的 Owner Fact 开始，然后修复 Projection 和 Checkpoint。

取消也遵循同样原则。Cancel 停止未来还能停止的工作，不回滚已经成立的 Domain fact，也不能抹掉已经确认的外部 Effect。补偿必须形成新的显式动作。

## 7. 知识、能力与模型

法律知识系统需要长期面对两个变化：材料会变，算法也会变。架构把二者分开处理。

材料变化通过 DocumentVersion 和 KnowledgeGeneration 管理。新的材料版本进入以后，旧知识派生可以继续服务历史结果，新 generation 在完成校验以后再成为当前 serving 版本。任务级 Readiness 根据当前 Scope 判断是否足够，而不是简单读取“索引构建完成”。

检索策略保持可替换。Keyword、Vector、Hybrid Retrieval 和 GraphRAG 都只是不同查询类型下的技术选择。普通文本问题如果 Hybrid Retrieval 已经足够，就没有必要为所有请求构建图检索；只有关系型、多跳或跨文档推理确实得到稳定收益时，GraphRAG 才值得进入默认路径。

研究能力通过 Capability 边界进入系统。论文模型、规则系统、LLM、MCP Tool 或外部 API 都可以实现某项专业能力，但它们首先要满足稳定 Contract 和版本要求，再通过 Conformance 与 Evaluation 获得资格。研究 Artifact 本身不会直接变成业务 Authority。

Model Gateway 使用同样思路管理模型。模型角色和具体 Provider 解耦，使 Planner、Extractor、Reranker 或 Reviewer 可以根据质量、预算、时延和数据政策选择不同模型。Provider 可用、当前允许和质量合格是不同条件。

长期 Memory 不是一级业务事实。Working Context 可以服务当前 Run；Long-term Memory 只有在 Evaluation 证明它对特定任务有稳定价值，而且数据生命周期和权限边界明确以后才启用。它可以由 Generic Host、OpenViking 或其他 Provider 提供，不改变 Domain、Knowledge 和 Runtime 的权威划分。

## 8. 安全、人工判断与现实副作用

高风险 AI 系统的安全不能只放在 HTTP 入口。一个长任务可能在开始时拥有权限，十分钟后用户角色发生变化；也可能在等待人工审批期间数据外发政策发生变化。

因此，每次跨越新的受保护边界时都重新消费当前 Security Decision：读取敏感材料、向模型发送数据、获取 Secret、执行高风险 Tool、提交正式业务结果，都使用当时有效的身份、Matter、Policy Epoch 和数据规则。

专业人工判断和安全审批分开。专业人员接受一个 Finding，说明它在业务上可以成立；审批某个外部动作，说明这个动作当前被允许执行。两种人工行为需要不同记录、不同权限和不同恢复语义。

外部副作用执行前，还要先建立可重建的责任链：准备执行什么动作、为什么允许、是否需要审批、关键审计是否已经耐久化。动作执行以后，EffectReceipt 或 ReconciliationReceipt 说明现实结果。普通 Trace 可以帮助理解过程，但不能替代这些关键事实。

这套设计的目标不是让每一次模型调用都变成沉重审批，而是把高风险控制放在真正跨越业务边界的位置。只读、低风险任务保持短路径；正式提交、敏感数据外发和不可逆动作才承担更严格的安全成本。

## 9. 部署与基础设施

九个逻辑责任域不是九个微服务。逻辑边界首先回答“谁负责哪类事实”，物理部署回答“代码和资源应该放在哪里”。两者的变化速度不同。

Zuno 的合理起点是模块化 Python 后端，加上按工作负载拆分的 Worker。知识构建、模型调用、Tool 执行和 Eval 具有不同资源特征，可以拥有独立队列、并发限制和 Worker pool，但这不要求每个逻辑 Owner 都拥有独立数据库或网络服务。

Platform / Infrastructure 提供 PostgreSQL、Object Store、Queue、Checkpointer、CAS、Lease、Fencing、Clock、Backup/Restore、Network 和 Secret Delivery 等基础能力。它们是物理原语，不拥有 Domain Success、Knowledge Success、Runtime Success 或 Effect Success。

只有当真实约束出现以后，逻辑边界才升级成独立网络服务。例如某一部分需要独立扩缩容、Secret 隔离、特殊网络出口、更小故障半径、不同部署生命周期或单独合规边界。没有这些证据时，共进程和共享基础设施通常更简单。

这种部署方式也保留了 Generic Host 的位置。Zuno 可以嵌入现有产品，也可以作为 Legal Backend 被通用 Host 调用；只有复杂任务确实需要更强控制时，Native Runtime 才成为主路径。

## 10. 观测、评测与架构演进

Observability 和 Evaluation 服务不同目的。Observability 回答系统发生了什么：一次任务经过哪些步骤、在哪里失败、消耗多少时间和资源。Evaluation 回答设计是否值得存在：更复杂的检索、模型、Runtime 或 Agent 结构有没有带来可重复的收益。

评测从 baseline 开始。简单 RAG 是复杂检索的 baseline；Generic Host + Legal Backend 是 Native Runtime 的 baseline；单一专业 Agent 是 Specialist / Multi-Agent 的 baseline。复杂方案只有在质量、恢复正确性、时延、成本或人工负担上产生稳定、可归因的增益，才应该成为长期默认设计。

因此，架构中的复杂机制都需要退出条件。GraphRAG 无法证明增益时回到 Hybrid Retrieval；Long-term Memory 没有带来稳定改善时保持关闭；强模型无法解释额外成本时回退到更轻模型；物理服务拆分没有独立隔离或吞吐证据时继续共进程。

这种设计使 Zuno 可以吸收研究成果，却不会随着研究热点不断膨胀。新论文、新模型和新框架先进入 Research 和 Capability 评估，再决定是否改变 Target。实现技术可以持续变化，事实权威和恢复语义保持稳定。

## 11. 实施时必须保持的架构不变量

后续实现可以替换框架、数据库细节、Provider 和部署方式，但下面这些关系构成 Zuno 的长期骨架：

- 机器结果先作为候选，正式法律事实由 Legal Domain 接纳。
- 正式引用绑定不可变材料版本和稳定位置，不依赖当前索引 identity。
- KnowledgeGeneration 描述知识派生生命周期，ReadinessDecision 描述当前任务是否可用。
- Runtime Checkpoint 证明控制进度，不能单独证明 Domain Commit。
- Formal Admission 需要独立耐久的 AdmissionReceipt 作为因果证明。
- 外部结果 Unknown 时先 Reconcile，禁止把网络超时直接解释成业务失败后盲目重试。
- 新的受保护动作重新消费当前安全决定；旧授权不会自动永久有效。
- Authorization、Approval 和 HumanDecision 分别承担访问、安全审批和专业判断责任。
- Telemetry 与 Eval 可以解释和评测系统，但不拥有 Domain、Security 或 Effect truth。
- 九个责任域是逻辑 Ownership，不等于九个进程、数据库或网络服务。
- 简单任务保持简单；更复杂的机制必须通过 Evaluation 证明自己值得存在。

模块设计、状态机和 Contract 应当从这些不变量继续细化，而不是反过来改变它们。一个实现如果需要把机器候选直接写入正式 Domain、让 Runtime 自己宣布业务提交成功，或者在外部结果未知时依靠盲重试维持流程，那么它已经偏离了总体架构。

## 12. 从架构进入实施

总体架构冻结的是责任和语义，不冻结实现技术。实施顺序应该从 Owner 和完成证明开始，再进入数据模型、接口、事务、队列和部署。

九个责任域的详细设计位于 [`docs/modules/`](../modules/README.md)。跨模块长期约束由 [`docs/decisions/`](../decisions/README.md) 记录。研究依据和可替换能力进入 [`docs/research/`](../research/README.md)。代码、测试、故障注入、性能和生产资格只有在 [`docs/evidence/`](../evidence/README.md) 中出现真实证据以后，才能从 Target 升级为 Current。

这使设计和实施保持单向关系：先确定系统应该保护什么，再选择怎样实现；实现结果再通过 Evidence 反过来验证、缩小或修正 Target，而不是让某个框架或已有代码目录决定架构。

## 研究依据

Zuno 的具体责任边界来自项目自身业务约束，外部研究只用于验证设计方向，不构成 Zuno 已实现或已验证的证据。与本架构最相关的研究包括：

- *Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG*（2025，arXiv:2501.09136）：总结 Agentic RAG 在规划、动态检索和多步任务中的作用，也指出扩展性、伦理和真实部署仍是主要挑战。
- *Hybrid Retrieval-Augmented Generation Agent for Trustworthy Legal Question Answering in Judicial Forensics*（2025，arXiv:2511.01668）：在法律 QA 中强调 retrieval-first、人工复核和知识持续更新，对高风险领域中的候选结果、人审和 provenance 设计具有参考价值。
- *What Information is Required for Explainable AI? A Provenance-based Research Agenda and Future Challenges*（2020，CIC）：从 provenance 角度讨论高风险 AI 决策需要保存哪些来源、过程和责任信息。
- *Interpretable AI/ML for High-stakes Tasks with Human-in-the-loop: Critical Review and Future Trends*（2024）：强调高风险 AI 中人类判断、解释和责任边界的重要性。

这些研究支持“可追溯、可复核、有人类权威、能够区分计算与正式决定”的总体方向；Zuno 是否在真实法律任务上取得足够收益，仍需要后续 Evaluation 和工程 Evidence 证明。
