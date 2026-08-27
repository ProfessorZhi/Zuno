# Zuno 总体 Target 架构

Zuno 面向智慧司法和法律专业工作，目标是把材料、证据、专业分析、人工判断、正式工作成果和受控外部动作组织成一条可追溯、可复核、可恢复的工作链。它不是为了“做 Agent”而给普通 RAG 叠加更多框架，而是解决复杂法律任务里几个普通问答系统很难长期回答的问题：依据的是哪一版材料，结论为什么成立，新证据出现后旧结果是否仍有效，人工判断怎样进入正式结果，系统崩溃后哪些业务事实已经真正提交，以及外部动作到底有没有发生。

简单问题应该保持简单。对“合同第 8 条写了什么”这类任务，通用宿主加受控检索完全可能已经足够；只有当多材料版本、长期领域状态、人工复核、恢复或现实副作用确实带来额外要求时，Zuno 才引入更重的领域和运行机制。复杂度必须由任务和测量证明，而不是由架构图证明。

本文记录 **Target（目标架构）**，不把文档中的对象、Contract（契约）或状态自动写成 Current（当前实现），也不把 Pilot 写成 Production。Part A 面向人类读者解释问题、流程、边界和失败；Part B 面向实现、测试和审查给出精确 Ownership（事实所有权）、Contract、状态、恢复和持久化规则。项目故事见 [`docs/project/project.md`](../project/project.md)，Current 证据见 [`docs/evidence/`](../evidence/)，模块详细设计见 [`docs/modules/`](../modules/README.md)，架构审查历史见 [`docs/maintenance/history/red-blue/`](../maintenance/history/red-blue/README.md)。History 解释架构如何演进，但不重新拥有当前 Target 或 Current。

<!--
updated: 2026-08-16
status: normative-target
architecture_state: ACCEPTED_TARGET
architecture_revision: COMPLETED
architecture_revision_sha: 7ce987f5d747395d4926622f42ac4f0013bc53ed
canonical_revision_gate: PASS
overall_architecture_state: ROUND_02_FROZEN
target_logical_module_count: 9
final_module_count: 9
platform_infrastructure: RESPONSIBILITY_LAYER
context_provider: OPTIONAL
module_decomposition_gate: OPEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_human_narrative: DEEPENED
module_detail_freeze: NOT_YET
implementation_authorization: NO
observability_architecture: OTEL_COMPATIBLE
langsmith_role: PREFERRED_AGENT_TRACE_AND_EVAL_PROVIDER
canonical_question: Zuno 如何把法律领域状态、证据、执行控制、安全和可验证交付组合成可恢复且可替换的 Target？
owner: Cross-cutting Architecture Owner
acceptance_scope: Round 02 Main Judgment 的 Canonical Revision；九模块已达到 Deep Design V2 / Cross-Module Consistency，并完成 Human-first 叙事深化；字段级 Detail Freeze、实现、测量和外部资格尚未完成
readability_state: HUMAN_FIRST_PART_A_AND_PART_B
canonical_taxonomy: docs/architecture/ 仅保存总体架构四文件；模块设计由 docs/modules/ 负责；项目事实由 docs/project/ 负责
current_state_source: docs/project/project.md 和 docs/evidence/
review_history_source: docs/maintenance/history/red-blue/
decision_sources: docs/decisions/0003-wave1-cross-module-contract-freeze.md、0005-official-langgraph-postgres-checkpointer.md、0007-reuse-first-provider-boundary.md、0008-legal-domain-kernel-and-host-boundary.md、0012-evidence-gated-physical-service-split.md、0013-round-02-responsibility-taxonomy.md、0014-round-02-cross-boundary-authority-and-recovery.md
-->

## Part A — Architecture Narrative

**先抓住整篇的主线，而不是先记九个模块。** Zuno 的架构成长可以压缩成七步：从普通 RAG / Generic Host 出发；发现机器计算结果不能直接成为业务事实；把材料版本、知识派生和正式领域状态分开；让长任务拥有可恢复控制；让权限在长任务中持续生效；让现实副作用拥有独立 Effect truth；最后用 Evaluation 决定 GraphRAG、Memory、Reflection、Native Runtime 等复杂度是否值得保留。九个责任域只是这些矛盾最后稳定下来的 Ownership 边界。

### 1. Zuno 真正要保护的不是一次回答，而是一条长期可解释的法律工作链

简单法律问答的目标通常很直接：确认用户能看哪些材料，找到相关原文，再生成一个有引用的回答。如果任务到这里就结束，那么受控检索、模型调用和普通应用服务已经足够，继续引入复杂运行时、长期状态和多种恢复机制反而会增加成本。

Zuno 面对的更难问题出现在工作持续更久、参与者更多、结果会被正式采用以后。同一个事项可能同时存在多版合同、扫描件、补充材料和后续证据；模型可以提出事实和结论，但专业人员可能接受、修改或拒绝；成果已经交付后还会出现新证据；任务可能运行几十分钟，中途发生权限变化、模型失败、服务崩溃或外部系统超时。此时系统不能只回答“模型最后说了什么”，还必须回答“依据哪一版材料、什么已经正式成立、什么只是候选、谁批准了什么、失败以后应该从哪个事实恢复”。

因此 Zuno 的总体设计从一个核心判断出发：**对简单任务保持简单；只有当长期事实、专业责任、失败恢复或现实副作用真正出现时，才引入相应复杂度。** 架构的目标不是让所有请求走最长路径，而是让每类任务只承担它实际需要的责任。

当前总体 Target 已由 Round 02 冻结为 **9 个 Target Logical Modules**。这里的九个模块是逻辑责任与事实 Ownership 边界，不是九个必须独立部署的物理服务。

### 2. 最简单的方案是什么，以及它为什么在复杂任务里开始失效

最简单的方案是一个通用 Agent Host 加法律知识库：Host 负责会话和工作流，知识库负责检索，模型负责生成，必要时再调用几个 Tool。对大量低风险、短生命周期任务，这个方案完全合理，而且 Zuno 不应该因为自己拥有更多模块就否认它的价值。

问题出在几个边界一旦同时出现，通用“消息 + Workflow 状态”不再足够。文件上传成功不能证明关键附件已经 OCR；检索命中不能证明候选内容已经成为正式证据；Workflow completed 不能证明领域事务已经提交；HTTP timeout 不能证明外部动作没有发生；用户十分钟前拥有权限也不能证明下一次模型外发仍然允许。把这些差异都压成一个 `success` 或一张共享状态表，会让恢复和审计失去可靠依据。

所以 Zuno 不是从“需要九个模块”开始设计，而是从这些无法被一个通用状态统一表达的问题，逐步推导出不同事实必须拥有不同权威边界。

### 3. 先区分四种经常被误写成同一个“成功”的事实

第一种是**计算成功**：检索、模型或专业算法产生了一个结果。第二种是**运行成功**：一次受控执行已经完成当前 Step 或 Run。第三种是**业务正式成立**：法律领域 Owner 已经接受结果并留下耐久版本。第四种是**现实动作已经发生**：外围系统确实产生了副作用。

这四种成功可以处在同一条因果链里，但不能互相冒充。一个模型返回 200 可能仍被专业语义拒绝；一个 Runtime Step completed 可能仍缺少正式提交证明；一个 POST timeout 可能对应远端已经成功；一个 WorkProduct 已经正式存在，也可能因为新证据而不再适合继续发布。

架构的第一层深度不是增加更多状态，而是承认这些事实的权威来源不同，并让恢复逻辑始终回到最强的 Owner fact。

---

**阶段二：从“系统算出了什么”转向“业务世界承认什么”。** 前三节只说明通用状态为什么不够；真正让系统开始拥有专业边界的，是承认计算成功、运行成功、正式业务成立和现实效果发生不是同一种事实。

### 4. 模型、检索和专业能力为什么都先产生候选

机器产生的信息天然有不确定性：材料可能过期，检索可能只覆盖部分范围，模型可能理解错误，专业算法可能只适用于某类案件。把“算出来了”直接写成正式业务事实，会让后续的人机复核、版本演进和责任追踪全部失去边界。

因此 Zuno 先把机器结果看成候选。检索可以产生证据候选，专业能力可以产生结论建议，模型可以产生计划或动作建议；只有相应业务 Owner 在满足证据、版本、安全和人工要求以后，才允许更强事实成立。工程术语只是对这个概念的压缩：`EvidenceCandidate != Evidence`。

同样，检索阶段的引用解释“为什么当前命中了这段材料”，正式工作成果保存的引用则解释“当时正式采用了哪一版材料和稳定位置”。两者生命周期不同，所以保持 `CitationLineage != WorkProductCitationBinding`。

### 5. 为什么按“事实谁负责”切架构，而不是按技术栈切

如果按 FastAPI、PostgreSQL、LangGraph、Milvus、Neo4j、LLM、Worker 来画系统，很容易知道组件在哪里，却很难在故障时回答“谁说了算”。同样存进 PostgreSQL 的两行数据，可能一个是正式领域版本，另一个只是运行检查点；同样由模型产生的两个结果，可能一个只是 Proposal，另一个经过人工和领域事务后已经成为正式事实。

Zuno 因此优先按照 Authority（权威）和 Ownership（事实所有权）拆责任：谁可以创建事实，谁可以让它失效，谁能证明它完成，崩溃以后应该先读谁的耐久记录。技术栈是实现选择，事实权威才是长期架构边界。

这也意味着九个逻辑责任域不等于九个进程。它们可以先共处模块化 Python 后端，只有独立扩缩容、安全隔离、部署生命周期或故障半径出现明确证据时才拆物理服务。架构不能因为“微服务看起来更专业”就提前制造网络边界。

---

**阶段三：一旦候选和正式事实分开，就必须回答“这些事实分别由谁负责”。** 这一步不再讨论某个模型或数据库，而是开始建立材料、知识、领域和控制状态之间的 Authority 边界。

### 6. 材料、知识派生和正式业务事实为什么必须分三层

一份正式材料首先需要稳定版本身份。随后系统可以围绕这份材料生成 OCR、切分、向量、图结构和其他检索视图。这些派生数据可以因为算法升级而重建，但历史业务结果不能跟着索引重建而改变。

更重要的是，“这一代知识已经构建完成”和“当前任务可以安全使用它”仍然不是一回事。某一代索引可能总体构建成功，但当前任务要求的关键附件缺失；也可能材料齐全，但当前权限或用途不允许读取。因此必须保持 `KnowledgeGeneration lifecycle != task-level ReadinessDecision`。

这个边界使系统可以大胆重建可派生知识，同时保护正式 DocumentVersion、Evidence 和 WorkProduct 的长期身份。它也让“知识库健康”不再被错误解释为“任何任务都已经 READY”。

### 7. 领域状态和运行状态为什么不能合成一张万能状态表

Runtime Control State（运行控制状态）需要知道计划执行到哪里、哪些 Step 完成、哪些分支仍在等待；Domain State（领域状态）则需要知道哪些法律事实和工作成果已经正式成立。这两套状态会互相引用，但它们回答的是不同问题。

最关键的故障窗口发生在领域事务已经提交，而 Runtime Checkpoint 还没来得及更新。此时如果恢复只相信 Checkpoint，系统可能再次提交同一正式结果；反过来，Checkpoint 标成 completed 也不能凭空证明领域事务真的成功。

所以正式提交必须留下独立的耐久证明。工程上把这类证明表达为 `AdmissionReceipt`。恢复时先确认 Domain 是否已经完成，再修复 Runtime projection，而不是让控制状态覆盖业务事实。

---

**阶段四：事实边界稳定以后，问题才轮到“任务怎样跑很久还能继续”。** Runtime 负责把工作推进下去，但不能因为自己拥有 Plan 和 Checkpoint，就顺手升级成 Domain、Security 或 Effect 的权威。

### 8. 一次任务为什么需要受控计划，但计划不能成为新的业务权威

复杂任务需要显式表示依赖、并行和等待，否则“模型接下来想做什么”会变成无法恢复的隐式状态。Zuno 原生 Runtime 因此使用受控 Plan；简单原生运行仍可以是确定性单步计划，复杂运行再使用动态 DAG。

但 Plan 只拥有控制语义。它可以决定下一步执行哪个专业能力、什么时候等待、什么时候重规划，却不能自己宣布 Evidence 正式成立，也不能批准安全动作。计划版本一旦激活保持不可变，是为了让已经派发的工作有稳定因果归属，而不是为了把 Runtime 设计成第二个 Domain。

控制权集中在 `Single Controller`，专业执行可以并行，但最终的计划激活、Step acceptance、Budget、Replan 和 cancel 由一个控制面收敛。这样 Specialist 可以扩展能力，而不会各自修改全局计划形成多写者竞态。

### 9. Retry、Replan 和 Reconcile 为什么必须是三个词

很多 Agent 系统把失败统一处理成“再试一次”。这对纯计算的暂时故障有用，却会在计划假设失效或现实结果未知时制造错误。

`Retry != Replan != Reconcile`。模型临时 503，而输入和计划仍然有效，可以 Retry；Tool schema、材料版本或任务假设已经改变，应该 Replan；外部 POST 已经发出但超时，现实世界可能成功也可能失败，必须 Reconcile。三者分别解决“同一动作再执行”“换一个动作计划”“先确认过去到底发生了什么”。

这个区分是恢复闭环的核心。如果架构只保留一个通用 retry loop，就无法同时保护计算正确性和现实副作用安全。

---

**阶段五：长任务还会跨越时间，因此“开始时允许”不能变成永久通行证。** 材料访问、模型外发、Secret、正式提交和现实动作都必须在真正产生新风险的门点重新消费当前安全事实。

### 10. 权限为什么不是请求入口的一次布尔判断

长任务可能运行几十分钟，中途等待人工、切换材料、调用多个模型和 Tool。期间用户权限、事项归属、数据密级、Provider 外发政策、审批状态和凭证版本都可能变化。

所以安全判断发生在每一个新的受保护边界：再次读取材料、向模型外发、获取 Secret、执行高风险 Tool、正式准入结果。早先合法发生的动作保持历史事实，但旧的 allow 不能自动成为未来动作的永久通行证。

这也是为什么 Authorization、Approval 和 HumanDecision 必须分开：有没有权执行、某个高风险动作是否被批准、专业人员是否接受法律业务结果，是三种不同责任。

---

**阶段六：当执行越过进程边界进入现实世界，恢复问题发生了质变。** 内部计算失败可以重算，外部动作 timeout 却可能已经成功；从这里开始，架构必须区分控制进度和现实 Effect truth。

### 11. 现实副作用为什么需要比普通函数调用更强的模型

纯计算失败通常可以重新执行，但现实动作可能无法撤回。向外围法院系统创建记录、提交材料或触发流程时，本地网络错误不能告诉我们远端是否已经执行。

因此执行前先形成稳定动作身份和待执行内容，工程上称为 `PreparedAction`；执行后保存能够证明现实效果的 `EffectReceipt`。如果发送后结果未知，就沿稳定动作身份查询远端、使用业务唯一键确认或进入人工对账，而不是把 timeout 简化成 Failed 后盲目 Retry。

高风险动作还可能要求在执行前留下耐久审计证明。普通 Trace 可以丢失或采样，所以需要独立的 `AuditPersistenceReceipt` 来证明强制审计边界真的落盘。Telemetry 解释发生了什么，但不能倒推当时满足了安全前置条件。

### 12. 九个责任域不是九段必须依次经过的流水线

九个责任域描述的是“某类事实最终由谁负责”，不是要求每个请求都走完九站。简单问答可以跳过 Runtime、Tool Effect 和 Formal Admission；复杂分析才逐步引入计划、专业能力和领域准入；现实副作用任务才需要 Effect Control 与更强审批。

这种设计让简单路径保持短，同时让复杂路径在需要时拥有恢复闭环。下面九个责任域只概括长期职责，具体状态和 Contract 下沉到模块 Part B。

#### 01 Application & Integration（应用与集成）

把外部请求、Scope、结果发布和交付组织成稳定产品语义。它消费其他 Owner 的权威事实，但不能因为离用户最近就重新定义安全、知识或 Domain truth。

#### 02 Legal Domain & Work Product（法律领域与工作成果）

拥有正式、长期、可审计的法律业务事实和工作成果。机器候选、运行完成或外部 ACK 都不能替代它的正式准入。

#### 03 Knowledge & Evidence（知识与证据）

围绕正式材料版本维护可重建知识派生、任务级知识就绪和检索候选。它帮助系统找到依据，但不把候选直接升级为正式证据。

#### 04 Agent Runtime & Control（智能体运行与控制）

拥有一次复杂任务怎样继续执行：计划、Step、并行、等待、预算、取消、重规划和检查点。它控制过程，不接管正式业务事实。

#### 05 Capability & Skill（专业能力与技能）

把研究模型、算法、规则和外部 Provider 整理成稳定、版本化、可替换的专业能力语义，使 Runtime 依赖“能做什么”而不是绑定“由哪个实现做”。

#### 06 Tool Runtime & Effects（工具运行与外部效果）

保护现实副作用：动作准备、执行尝试、结果确认、幂等和对账。它负责 Zuno 能证明的 Effect truth，但不冒充远端系统内部最终业务状态。

#### 07 Model Gateway（模型网关）

把模型调用集中为受控依赖：按角色、质量资格、数据政策、预算和 Provider 状态路由，并记录真实调用和用量，而不是成为所有 Prompt 和业务语义的 God Layer。

#### 08 Security & Governance（安全与治理）

持续回答“当前主体现在还能不能执行下一步”，并拥有授权、审批、安全策略、Secret 使用、强制审计要求和生命周期决策。

#### 09 Observability & Evaluation（可观测性与评测）

一方面帮助解释系统刚才发生了什么，另一方面用可复现实验判断复杂机制是否真的值得保留。它测量 Owner facts，不替代 Owner facts。

### 13. 三条任务路径怎样使用同一套边界而不共享同样复杂度

简单问答从请求和 Scope 开始，检查当前授权与知识就绪，检索材料，调用模型生成并校验引用，然后由应用层决定是否发布。它不需要为了“统一架构”强制进入动态规划。

复杂分析在同样的入口和材料基础上增加显式 Plan、专业 Capability、并行与人工复核；只有最终需要成为正式法律工作成果的内容才进入 Domain Admission。机器中间结果可以大量产生，但正式事实的入口保持窄而可审计。

现实动作则在分析之外增加 Effect Control。模型或 Capability 可以提出 Action Proposal，但不能直接发送；动作必须经过安全、审批、审计和幂等准备，再由 Tool Runtime 记录实际尝试与结果。三条路径共享事实边界，却按风险逐级增加机制。

### 14. 一个最关键的崩溃窗口怎样恢复

假设复杂分析已经生成正式 WorkProduct，Domain transaction 成功提交，但 Runtime 在写下一次 Checkpoint 前进程崩溃。重启后仅看 Checkpoint 会误以为 Step 尚未完成，直接重跑可能重复提交。

正确恢复顺序是先查询 Domain Owner 的匹配 `AdmissionReceipt` 和版本事实。如果正式提交已经存在，就把它作为更强事实，再修复 Runtime 的 Step acceptance / Checkpoint；如果只有 Checkpoint completed 却找不到正式 Receipt，则 Runtime 不能把自己标记成业务完成。

这个例子解释了 Zuno 为什么反复强调“Owner fact first, projection second”。Cache、Trace、Checkpoint、Dashboard 都可以帮助定位，但不能覆盖拥有更强业务语义的耐久事实。

### 15. 新证据为什么会让历史结果“需要复核”，而不是把历史改写掉

法律工作不是静态问答。新材料进入以后，旧 Finding 或 WorkProduct 可能不再适合继续使用，但它们作为“当时基于那些材料产生过的历史版本”仍然存在。

因此 Zuno 不删除过去来伪装一致，而是保留依赖关系并形成新的失效事实。Domain 负责判断正式成果是否 stale，Application 负责把失效通知交付给消费者；外部消费者离线不会阻止 Domain truth 立即变化。

这种设计让历史可审计、当前有效性可查询，也避免每次新增材料都全量重跑所有结果。未来是否重评应沿依赖范围有界传播。

### 16. 研究算法和开源框架为什么只能作为 Provider 或可删除机制进入

Zuno 来自智慧司法研究背景，因此会使用事件抽取、冲突识别、类案检索、GraphRAG、Memory、Reflection 等能力。但“论文里有效”“框架支持”都不能直接推出“Zuno 必须永久拥有”。

研究成果先被整理成稳定专业语义，再由一个或多个版本化 Provider 实现，通过 Conformance 与任务级 Eval 决定当前资格。这样旧论文算法、新 LLM、规则实现和外部服务可以在同一 Capability 语义下比较，而 Runtime 不需要绑定某个具体实现。

Graph、长期 Memory、复杂 Planner、强模型路由和 Specialist 都应保留 simpler baseline。收益不稳定时应该缩小或删除，而不是因为已经实现就获得永久架构地位。

### 17. 物理部署为什么必须晚于逻辑 Ownership

九个责任域首先解决“谁拥有事实”，不是“部署几个服务”。默认实现可以是模块化后端加按工作负载拆分的 Worker：知识构建、模型调用、Tool 执行和 Eval 的扩缩容需求不同，但不要求每个逻辑 Owner 都拥有独立进程和数据库。

判断一个逻辑责任域**为什么必须独立服务**，必须回到 Secret isolation、独立吞吐、故障半径、网络出口、合规边界或部署生命周期等证据。只有这些条件形成明确收益时，才值得把某个边界提升为独立网络服务；服务拆分是一种成本很高的优化，需要被问题证明。

跨 Owner 的一致性也不通过“把所有东西放进同一分布式事务”解决。每个 Owner 在自己的事务边界内保证事实，跨 Owner 通过版本、Receipt、幂等身份和恢复顺序收敛。

---

**阶段七：最后一个问题不是“还能再加什么机制”，而是“哪些复杂度值得活下来”。** 到这里架构已经能表达长期事实、恢复和安全，但 GraphRAG、Memory、Reflection、Multi-Agent 或 Native Runtime 仍然只能通过可比较 Evidence 获得长期资格。

### 18. 一项复杂机制什么时候应该主动删除

如果简单 RAG 已经满足目标任务，就不需要 Native Runtime；如果 Hybrid Retrieval 已经覆盖某类 query，就不需要 GraphRAG；如果通用 Host + Zuno Legal Backend 已经能够保护正式状态和恢复，就不需要复制一套完整宿主；如果一个模块没有独立扩缩容或安全隔离证据，也不需要拆成微服务。

删除条件不是架构的附录，而是架构质量的一部分。每增加一个状态机、Provider、缓存、图存储、Agent 层或服务边界，都应该能回答它保护了什么约束、增加了什么故障面、测量不到收益时怎么退回更简单方案。

09 的 Evaluation 因此不仅用于证明“功能有效”，还应该主动做 ablation 和 kill test，帮助团队决定哪些复杂度不值得长期维护。

### 19. 架构真正困难的是“时间”，不是把模块框画出来

很多系统图在静态时刻都看起来合理：材料在知识库里，Agent 在运行，结果最后进入数据库。真正让边界暴露价值的是时间。材料版本会变化，权限会撤销，模型和 Capability 会升级，旧 Plan 的并行结果会晚到，外部 Effect 会在本地不知道的时候已经发生。系统如果只描述“现在有哪些对象”，而不描述“一个事实在什么条件下还能继续被使用”，架构仍然是不完整的。

因此 Zuno 的多个版本号并不是为了追求形式化。DocumentVersion 保护材料身份，KnowledgeGeneration 保护可重建派生，PlanVersion 保护运行因果，Capability / Model version 保护计算语义，SecurityEpoch 保护授权新鲜度，DomainVersion 保护正式业务演进。它们不是一个全局大版本，因为这些事实变化的原因和 Owner 不同；强行统一版本反而会制造不必要耦合。

一个结果能否被继续使用，本质上取决于它的 causation 还是否成立。旧模型结果并不因为“旧”就必然无效；如果输入材料、专业语义和当前安全条件都没有改变，它可能仍可接受。反过来，一个刚算完的结果，如果依据的 Plan 或权限已经失效，也可能马上没有资格进入当前路径。时间新鲜度因此是按语义判断，不是简单比较 timestamp。

### 20. 跨模块一致性为什么不用一个超级事务解决

面对多个 Owner，最直觉的做法是希望“所有状态一次原子提交”，这样看起来不会不一致。但 Zuno 横跨数据库、索引、模型 Provider、外围法院系统和观测系统，其中很多参与者根本不能加入同一个数据库事务。为了追求全局原子性引入分布式 2PC，也不能让已经发出的外部 POST 回滚。

更可实现的策略是让每个 Owner 在自己的事务边界内保存足够强的事实，再通过 Receipt、版本和幂等身份形成可恢复因果。跨边界短暂不一致允许存在，但必须知道哪一个事实更权威、怎样最终收敛。例如 Domain 已提交而 Checkpoint 落后时，以 Domain Receipt 修复 Runtime；Effect 已确认而 Delivery projection 落后时，以 Effect truth 修复交付状态。

这是一种“可恢复一致性”而不是“所有东西永远同步一致”。代价是系统必须认真设计 recovery order；收益是故障不会因为一处 projection 失败就迫使已经成立的业务事实回滚，也不会依赖所有外部系统同时在线。

### 21. 为什么每个边界都要回答 Non-proof，而不只回答 Success

架构文档通常喜欢定义成功条件，却较少明确“什么看起来像成功，但其实不能证明更强事实”。Zuno 特别强调 Non-proof，是因为跨层误判经常发生在这里：Provider 200 不是专业质量证明，Capability success 不是 Domain admission，Checkpoint completed 不是正式提交，HTTP 200 不是所有远端业务流程完成，Trace exported 也不是强制审计已经满足。

把 Non-proof 写清楚，可以防止相邻模块为了方便不断升级自己的状态语义。每个 Owner 只承诺自己真正能证明的事情，上层需要更强结论时必须消费对应更强 Receipt / Decision。这种克制看起来增加了一些查询和对象，却大幅降低“一个 success 被整个系统误用”的风险。

同理，失败也不能统一成一个 ERROR。计算失败、输入过期、计划失效、安全拒绝、结果未知和人工待处理需要不同恢复方式。分类的目的不是做一张漂亮 taxonomy，而是决定系统下一步是否允许自动行动。

### 22. 性能优化为什么必须服从 Authority，而不是反过来

缓存、异步 Worker、批处理、并行、预取和多级索引都能提高性能，但它们经常把请求从原始 HTTP 上下文中分离。如果架构只在入口保存 tenant、权限或版本，后台优化越多，越容易丢掉原本保护正确性的上下文。

所以性能机制只能优化已有语义：Cache 可以加速派生结果，但不能延长授权寿命；并行可以提高 Capability 吞吐，但不能产生多个 Controller；异步 Delivery 可以解耦外部系统，但不能推迟 Domain invalidation；Read Replica 可以扩展查询，但不能让旧 projection 覆盖 Owner write truth。

这条原则给性能优化一个清楚边界：先证明优化不改变 Authority 和 causation，再讨论吞吐和延迟。必要时宁愿多一次当前安全检查或 Owner query，也不把一次旧决定变成永久 token。

### 23. Build / Buy / Extend / Defer 为什么要逐层判断

Zuno 不应该因为是研究型项目就默认自研所有基础设施。身份认证、Secret Manager、PostgreSQL、OpenTelemetry、通用 Checkpointer、消息队列和模型 SDK 都应优先复用成熟能力。项目真正需要自己拥有的是法律业务语义以及这些通用组件之间无法替代的 Authority 边界。

判断是否自研时先问最简单成熟方案能不能满足约束。如果能，Buy / Adopt；如果只缺一个法律语义薄层，Extend；如果当前没有真实需求或 Evidence，Defer。只有现成方案在正式状态、恢复、隔离或专业质量上存在明确缺口，而且这个缺口长期属于 Zuno 责任，才值得 Build。

这个原则同样适用于 Agent 框架。LangGraph 可以承担执行原语，但不自动拥有 Formal Admission；通用 Host 可以承担会话和 UI，但不自动拥有法律 Domain；Graph database 可以实现一种 Projection，但不自动证明 GraphRAG 值得保留。框架是能力来源，不是架构因果来源。

### 24. 降级为什么不能只有“换弱模型继续回答”

高可用并不意味着任何情况下都必须给出完整答案。真正合理的降级取决于缺失的是什么。如果强模型不可用但当前任务允许低成本模型且质量基线仍满足，可以路由降级；如果 Graph 路径不可用而 Hybrid Retrieval 对当前 query class 足够，可以退回简单检索。

但关键材料缺失时，正确降级可能是缩小 Scope；权限无法确认时是 fail closed；现实 Effect outcome unknown 时是等待 Reconcile；Judge 不可用时是 Evaluation BLOCKED。把所有降级都实现成“尽量生成一段文本”会把可用性优化变成正确性破坏。

因此每个模块都应定义自己能够安全降低的能力和不能越过的 floor。系统的韧性来自知道什么时候可以少做，而不是永远假装什么都能做。

### 25. 为什么 Evidence 不只是测试通过，还要能影响架构删除决定

代码测试可以证明某个 Contract 当前按预期工作，却不能证明这个 Contract 值得长期存在。复杂机制的保留需要另一类 Evidence：它是否在目标任务上改善了质量、恢复、延迟、成本或人工负担，并且收益是否超过维护复杂度。

例如 GraphRAG 的正确实现只能证明图检索“能工作”；只有对照实验才能证明它比更简单的 Hybrid Retrieval 有边际价值。Native Runtime 的 crash recovery 测试证明机制正确，但还需要和 Generic Host + Legal Backend 比较，才能知道是否值得承担长期自研宿主成本。

因此 Zuno 的架构不是单向“不断建设”。09 的评测应能够导致保留、缩小、替换或删除。一个设计能主动定义自己的退出条件，通常比“永远有理由继续加功能”更成熟。

### 26. 一个架构边界是否成立，最终要看它能不能减少错误的“推断”

复杂系统最危险的 bug 往往不是某个函数算错，而是 A 模块看到 B 模块的一个状态后，推断出了它其实没有资格知道的结论：看到索引构建完成就推断任务 READY，看到 Step completed 就推断 Domain 已提交，看到 HTTP timeout 就推断 Effect 失败，看到旧 Authorization allow 就推断未来仍允许。

因此 Zuno 的边界设计可以用一个很朴素的问题验收：**这个模块对外暴露的事实，是否足够让消费者做正确判断，同时又没有诱导它推断更强事实？** 如果一个 Contract 经常需要消费者“顺便猜一下”，说明 Owner 或 completion proof 仍然不够清楚；如果每个消费者都复制同样判断逻辑，则应该把判断收回真正的 Authority。

这也是为什么文档质量本身属于架构质量。读者如果必须依赖内部名词和隐含惯例才能知道谁说了算，工程实现更容易重复同样误判。Human Narrative 先把因果讲清，Engineering Reference 再冻结精确语义，两层共同减少错误推断，而不是让术语数量成为复杂度的遮羞布。

另一个验收方法是做“删除测试”：暂时拿掉某个边界，看看错误推断是否重新出现。如果删除独立 Domain authority 后 Runtime completed 就被迫承担正式业务含义，说明该边界确有必要；如果拿掉某个额外层后所有重要不变量仍然能被更简单组件保护，就应该质疑这层复杂度。边界的价值必须表现为减少真实歧义、故障或责任冲突，而不是让架构图更对称。

### 27. 什么必须稳定，什么应该允许替换

架构最容易走向两个极端：要么所有东西都被称为“可替换”，最后没有任何稳定责任；要么把当前框架、数据库和对象结构全部写成不可改变的架构事实，导致任何升级都要重新设计系统。Zuno 需要稳定的是语义不变量，不是今天的实现形态。

必须稳定的包括：机器结果先是候选，正式业务事实由 Domain Owner 准入；Runtime Checkpoint 不能单独证明 Domain Commit；现实结果未知不能被 blind retry；授权在新的受保护动作前重新判断；每个更强事实都有明确完成证明和恢复顺序。这些不变量如果变化，通常意味着真正的 Architecture Revision。

应该允许替换的包括 Provider、模型、检索算法、Checkpointer 实现、Queue、Cache、ORM、表结构和大部分物理部署。替换它们时，如果上层仍然可以依赖同一个 Owner、同一种完成语义和同一条恢复链，说明抽象边界是健康的；如果换一个 SDK 就必须重新解释“什么算正式成功”，说明实现细节已经泄漏进 Authority。

这也是 Detail Freeze 应该克制的原因：冻结足以保证跨模块正确性的字段和约束，而不是把所有当前实现偏好永久写进 Contract。

### 28. 架构演进为什么要设计迁移，而不能只设计最终状态

Target 架构最终长什么样只是问题的一半。真实系统升级时，旧 Run 可能仍在执行，旧 WorkProduct 仍要被审计，旧 Provider 版本仍被历史记录引用，数据库也不可能在一个瞬间让所有数据和消费者同时切换。

因此兼容性首先是时间问题。新版本可以服务新请求，旧运行继续按自己已经绑定的 Plan、Capability、Model 或 Contract 解释；可重建 Projection 可以 backfill 或重建，但历史 Domain / Effect / Audit fact 不能因为迁移方便被改写。需要切换 Owner 存储时，也不能长期双写出两套都声称权威的事实源。

安全的迁移更像：先让新实现能够读取和解释旧事实，再建立可验证的新写路径，必要时重建非权威 Projection，最后在完成证明和恢复演练都成立后切换流量。迁移成功的定义不是“新代码部署了”，而是旧任务能恢复、历史结果能解释、失败时知道回到哪个 Authority。

这个原则同样限制物理服务拆分。把一个模块搬到独立服务，如果需要一段迁移期，就必须保持逻辑 Owner 不变；网络拓扑变化不能创造第二个业务真相。

### 29. 过载和局部故障为什么不能升级成错误业务事实

系统在高负载下最容易为了维持绿色指标而模糊边界：Queue 满了仍无限受理，Policy 服务不可用时沿用旧 allow，模型超时后把任务标成业务失败，Telemetry 丢失后认为动作没有发生。这些做法把容量问题升级成正确性问题。

Zuno 更希望每个责任域定义自己的安全降级和背压。知识构建拥塞可以让新 generation 排队，但不能污染当前已验证 serving；模型容量不足可以等待、换合格候选或明确降级，却不能偷偷放宽质量和外发政策；安全事实不可确认时高风险路径 fail closed；Effect outcome unknown 时进入 Reconcile 而不是为了释放队列强行写 Failed。

隔离的目标也不是“每个模块一个服务”，而是防止一个工作负载把另一个责任域的正确性拖垮。批量 OCR、Eval、模型调用和在线 validity query 的资源特征不同，可以先通过 Worker pool、quota、priority 和 admission control 隔离；只有证据证明进程级隔离不够，再考虑网络服务。

可用性因此不是任何时候都生成结果，而是在压力下仍能区分：哪些事情可以晚一点做，哪些可以少做，哪些必须停止，哪些事实即使系统很忙也绝不能猜。

### 30. Current、Target、Evidence 和 Unknown 必须始终分开

本文描述的是 Target Architecture。九模块 Responsibility Taxonomy、Formal Admission、Single Controller、Knowledge / Domain 权威、Effect recovery 和安全门禁已经作为目标设计接受，但这不等于对应代码、表、Migration、Provider、HA 或生产流程已经存在。

Current 只能由代码、测试、Migration、Trace、Eval 或真实运行证据证明。Pilot Validation 也不等于 Production；没有容量、DR、安全资格和运行证据，就不能从完整设计反推出生产成熟度。

项目为什么存在以及历史上做过什么，回到 `docs/project/project.md`；当前实现证据回到 `docs/evidence/`；精确模块 Contract、状态和 crash window 回到 Part B / Part C。Unknown 应保持 Unknown，不用更漂亮的架构文字填补证据空缺。

### 31. 读完整体架构后应该留下什么

如果只记住九个模块名，这篇架构文档就失败了。更重要的是记住几个设计判断：简单任务保持简单；机器结果先是候选；正式业务事实、运行控制、知识派生和现实效果分别由对应 Owner 负责；失败恢复先找最强耐久事实；权限在新的受保护动作前重新判断；复杂机制必须能被测量，也必须能被删除。

这些原则决定了 Zuno 如何在法律专业性、Agent 灵活性和工程可恢复性之间划边界。具体对象名、字段、枚举和事务细节可以继续演进，只要它们没有破坏这些已经接受的 Authority 与因果关系。

## Part B — Detailed Architecture Specification

Part B 是 Part A 的工程参考。它不能增加 Part A 没有解释过的重大决策；模块内部字段、ORM、表和最终 enum 继续由 `docs/modules/` 的逐模块 Deep Design 冻结。

### B1 Scope and Global Invariants

1. Logical Responsibility 不等于 Process、Container、Database、Worker、Network Service 或 Team。
2. Domain State、Runtime Control State、Knowledge Projection、Optional Context、External Effect State、Security / Audit Fact 和 Telemetry Projection 拥有不同 Owner。
3. Model、Capability、Retrieval、Memory、Specialist 和 Runtime 只能产生 Proposal / Candidate / Observation / Reference；不能直接提交 Canonical Domain State。
4. Simple QA 可以由 Generic Host / direct path 完成，不强制进入 Zuno Native Agent Runtime。
5. 进入 Native Runtime 的任务必须有 Plan：Deterministic Single-Step Plan 或 Dynamic DAG Plan；不得通过 direct_answer 绕过 Plan / Trace / Budget / AnswerPolicy / RunOutcome。
6. `Retry != Replan != Reconcile`；外部 Outcome Unknown 禁止 Blind Retry。
7. Formal Admission 的完成必须有匹配 AdmissionReceipt；Checkpoint 不能单独证明 Domain Commit。
8. `EvidenceCandidate != Evidence`；`CitationLineage != WorkProductCitationBinding`。
9. `KnowledgeGeneration lifecycle != task-level ReadinessDecision`；Index write success != Serving activation != task READY。
10. Current 只能由代码、Migration、Test、Trace、Eval 或真实运行证据证明；文档完整度不是 Current 证据。
11. Network Service Split 必须由 Evidence Gate 门控；默认物理起点是 Modular Python Backend + Independent Workers where justified。
12. Telemetry 不能替代 Durable Audit、Domain Receipt、Security Decision 或 Tool Effect Receipt。

### B2 Responsibility / Ownership Map

| Fact / State | Authoritative Owner | 其他边界只能怎样消费 |
| --- | --- | --- |
| Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct | 02 Legal Domain & Work Product | Snapshot、Reference、Admission Input |
| Formal Admission、AdmissionReceipt、WorkProductCitationBinding、Domain invalidation truth | 02 | 04 用 Receipt 恢复；01 负责通知 |
| KnowledgeGeneration、processing / manifest / serving semantics | 03 Knowledge & Evidence | 读取 generation / coverage references |
| task-level ReadinessDecision、EvidenceCandidate、RetrievalResult、CitationLineage | 03 | 01 / 04 / 05 / 02 消费，不重算 Owner fact |
| AgentRun、PlanVersion、StepRun、Dispatch / Join、Budget、Interrupt、Checkpoint、RunOutcome | 04 Agent Runtime & Control | 其他模块返回事实 / Receipt，不接管 Control State |
| CapabilityRequirement、CapabilityVersion、ProviderConformance、专业 Proposal | 05 Capability & Skill | 04 选择 / 调度；02 决定正式接纳 |
| PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt | 06 Tool Runtime & Effects | 08 决定 policy；Runtime / Domain 消费 confirmed outcome |
| Model role routing、attempt、Quota、Usage / Cost | 07 Model Gateway | 09 评测；08 控制 egress / credential policy |
| AuthorizationDecision、SecurityEpoch、ApprovalDecision、EffectiveLifecycleDecision、Audit Requirement | 08 Security & Governance | 各边界执行并保存自己的 enforcement fact |
| Durable Audit Persistence Fact | 对应耐久执行边界，在 08 requirement 下 | 以 AuditPersistenceReceipt 被消费 |
| Trace、Metric、Eval Dataset、Evaluation Result、Release Evaluation | 09 Observability & Evaluation | 诊断 / 评测，不改变业务 Truth |
| External task composition、Zuno-side answer publication、delivery、invalidation delivery、consumer ack observation | 01 Application & Integration | 不重算 Domain / Security / Knowledge facts |
| Physical durability primitive | Platform / Infrastructure | Storage / Queue / Worker / lease 等 primitive receipt |

### B3 Cross-boundary Contracts

本节只记录总体层真正跨责任域的 Contract。模块内部私有 DTO、helper、ORM 字段和最终表结构不在这里冻结。

#### InvocationDecision

- Purpose：组合当前请求是否允许进入 Zuno 某条执行路径。
- Producer / Owner：01 Application & Integration。
- Consumer：Host、direct QA path、04 Runtime。
- Input / Output：request + Scope + AuthorizationDecision + ReadinessDecision + applicable capability / model eligibility + optional runtime gate → allow / wait / reject / review 类决定。
- Versioning：绑定 request identity、相关 Domain / Knowledge / Security refs。
- Validation：01 只组合 Owner facts，不重新计算它们。
- Failure Semantics：底层事实缺失或冲突时 fail closed / wait / review。
- Idempotency / Replay：同一 invocation identity 可识别重放。
- Security Requirements：消费当前 Security Epoch。
- Persistence Requirement：保存足以解释组合决定的引用或 Receipt；具体形态由 01 Deep Design 冻结。
- Observability Requirement：记录决定来源，不把组合结果伪装成底层 Truth。
- Evidence：Host / invocation integration tests。

#### AnswerPublicationDecision

- Purpose：判断普通回答是否具备发布资格。
- Producer / Owner：Zuno 自己发布时为 01；外部 Host 最终展示时，Host 拥有最终 UI / publication truth。
- Consumer：Zuno response surface / external Host。
- Input / Output：typed result + citation / eligibility evidence + policy refs → publish / draft / review / reject 类决定。
- Versioning：绑定 answer / source / policy refs。
- Validation：引用、资格和当前发布权限可检查。
- Failure Semantics：不满足要求时不静默发布正式答案。
- Idempotency / Replay：Delivery 使用独立 delivery identity。
- Security Requirements：遵守当前 publication / redaction policy。
- Persistence Requirement：Zuno-side publication / delivery fact 可恢复。
- Observability Requirement：区分 Zuno decision 与外部 Host display。
- Evidence：Publication / Host Integration Tests。

#### ReadinessDecision

- Purpose：回答某次任务能否基于指定 DocumentVersion、Serving KnowledgeGeneration 和当前要求安全工作。
- Producer / Owner：03 Knowledge & Evidence。
- Consumer：01 / 04；必要时 02 admission eligibility 消费引用。
- Input / Output：DocumentVersion refs + serving generation + task Scope + minimum processing / retrieval requirements + current Authorization / Security refs → READY / PARTIAL / BLOCKED 类语义 + coverage / missing refs。
- Versioning：绑定 generation、scope、requirements 和 policy refs。
- Validation：source version、generation eligibility、coverage、required capability、security 均可追溯。
- Failure Semantics：PARTIAL 必须显式携带覆盖范围；不能冒充 full-scope READY。
- Idempotency / Replay：相同输入可重算；generation / policy / scope 变化后重新评估。
- Security Requirements：当前授权是输入。
- Persistence Requirement：关键 generation / serving facts耐久；decision 本身持久策略由 03 详细设计冻结。
- Observability Requirement：记录 decision identity / coverage / missing reason，敏感正文最小化。
- Evidence：Partial Knowledge / stale generation / security revocation tests。

#### EvidenceCandidate / CitationLineage

- Purpose：把当前允许范围中的证据候选及其检索来源送到 01 / 02 / 04 / 05。
- Producer / Owner：03 Knowledge & Evidence。
- Consumer：direct QA、02 Domain Admission、04 Runtime、05 Capability。
- Input / Output：task query / scope + serving generation → candidate refs + stable source DocumentVersion / location + retrieval lineage。
- Versioning：绑定 DocumentVersion、KnowledgeGeneration、retrieval identity。
- Validation：stale generation、scope mismatch、unauthorized source 不得静默作为合法候选。
- Failure Semantics：zero evidence、insufficient evidence、partial coverage、provider failure 必须区分。
- Idempotency / Replay：检索可重放，但重放结果不改写过去正式引用。
- Security Requirements：检索和外发遵守当前授权 / egress policy。
- Persistence Requirement：必要 lineage / source refs 可耐久保存；不把完整 ranking trace 自动升级为 Domain fact。
- Observability Requirement：记录策略、candidate count、lineage completeness。
- Evidence：Citation Provenance / retrieval integration tests。

#### WorkProductCitationBinding

- Purpose：保存正式 WorkProductVersion 当时实际采用的不可变材料位置。
- Producer / Owner：02 Legal Domain & Work Product。
- Consumer：Review、Audit、01 Delivery、后续 staleness analysis。
- Input / Output：DocumentVersion + immutable source reference / hash + stable location / span + source representation identity / hash + necessary excerpt / evidence hash + optional CitationLineage ref → durable binding。
- Versioning：绑定 WorkProductVersion，不被新 Index / Chunk / Graph 覆盖。
- Validation：能够回到原始不可变表示。
- Failure Semantics：正式成果需要的 binding 不完整时不得 Formal Admit。
- Idempotency / Replay：同一 WorkProductVersion + binding identity 幂等。
- Security Requirements：按材料访问 / redaction policy 展示。
- Persistence Requirement：Domain durable boundary。
- Observability Requirement：Trace 只记录 binding identity / completeness，不导出敏感全文。
- Evidence：Source replacement / historical citation tests。

#### AdmissionReceipt

- Purpose：证明 `StepRun → Proposal → Formal Admission → resulting DomainVersion` 的因果链。
- Producer / Owner：02 Domain Admission boundary。
- Consumer：04 Runtime、Recovery、Audit / Review。
- Input / Output：run identity + PlanVersion + StepRun identity + proposal / admission identity + idempotency identity + expected prior DomainVersion → resulting DomainVersion receipt。
- Versioning：绑定唯一 resulting DomainVersion 和预期前置版本。
- Validation：Domain mutation 与 Receipt 在同一 Domain transactional durability boundary。
- Failure Semantics：缺匹配 Receipt 时，04 不能宣布要求 Formal Admission 的 Step 完成。
- Idempotency / Replay：同一 identity 重放返回既有合法结果；同 key 不同输入冲突失败。
- Security Requirements：提交时消费当前 AuthorizationDecision 和必要 HumanDecision / Approval refs。
- Persistence Requirement：Domain durable boundary，不得只在 Checkpoint / Trace。
- Observability Requirement：Trace 引用 Receipt，不替代 Receipt。
- Evidence：Admission causation / crash recovery tests。

#### WorkProductInvalidationFact / InvalidationDeliveryFact / ConsumerAcknowledgementObservation

- Purpose：分别表示正式成果失效、失效通知交付和消费者确认观测。
- Producer / Owner：WorkProductInvalidationFact 归 02；DeliveryFact 与 AckObservation 归 01。
- Consumer：Host、法院系统、Review、current-validity query、04 targeted reevaluation。
- Input / Output：canonical dependency change → invalidation；delivery attempt → delivery fact；consumer response → acknowledgement observation。
- Versioning：每个 WorkProductVersion / delivery identity 独立。
- Validation：不能用单个 `WorkProduct.status` 代替三类事实。
- Failure Semantics：Domain stale 不等待 Consumer 在线；delivery 可重试；Ack unknown 不代表远端已知。
- Idempotency / Replay：invalidations / delivery identity 幂等。
- Security Requirements：通知遵守当前 consumer scope / redaction。
- Persistence Requirement：各 Owner 在自己的 durable boundary 持久化。
- Observability Requirement：Telemetry 清楚区分 Truth、Delivery 和 Observation。
- Evidence：Invalidation / delivery / offline consumer fault tests。

#### AuthorizationDecision / ApprovalDecision / EffectiveLifecycleDecision

- Purpose：分别回答当前访问是否允许、高风险动作是否获批、数据生命周期政策是什么。
- Producer / Owner：08 Security & Governance。
- Consumer：01、02、03、04、06、07、Context Provider、Platform Stores。
- Input / Output：principal + tenant / Matter / Scope + Policy Epoch + action / data risk → typed security / approval / lifecycle decision。
- Versioning：绑定 Security Epoch / policy version / action identity when applicable。
- Validation：新的受保护访问重新消费当前决定；Approval 必须绑定具体 action hash / scope。
- Failure Semantics：deny / pause / review；policy unknown 时 fail closed。
- Idempotency / Replay：稳定 decision identity；Retry / Resume / Replan 不能沿用已失效决定。
- Security Requirements：Secret 和敏感 policy material 不进入普通 Prompt / Trace。
- Persistence Requirement：高风险 Approval、Lifecycle policy refs 和必要 Audit facts 可审计。
- Observability Requirement：只输出脱敏 reason / identity refs。
- Evidence：Revoked Permission、Approval binding、Lifecycle tests。

#### PreparedAction / ToolAttempt / EffectReceipt / ReconciliationReceipt

- Purpose：绑定现实动作、记录执行尝试、保存确认结果，并在结果未知时对账。
- Producer / Owner：06 Tool Runtime & Effects；External System 仍拥有其内部最终现实事实。
- Consumer：04、01、02、08 Audit / Review。
- Input / Output：tool definition + args + Authorization / Approval + idempotency → ToolAttempt → EffectReceipt 或 OUTCOME_UNKNOWN → ReconciliationReceipt。
- Versioning：绑定 action identity / hash、run / StepRun causation 和 idempotency identity。
- Validation：调用前校验 schema、semantics、tool / capability version 和当前安全决定。
- Failure Semantics：明确 transient failure 可 Retry；Outcome Unknown 必须 Reconcile；无法安全确认则 Human Review。
- Idempotency / Replay：副作用必须具备 external idempotency 或 reconciliation path。
- Security Requirements：执行时重新授权，敏感参数不进入普通日志。
- Persistence Requirement：Attempt / Effect / Reconciliation 必须耐久到可恢复。
- Observability Requirement：Telemetry 只引用这些事实。
- Evidence：Duplicate Effect、Timeout、Provider Drift、Reconciliation tests。

#### AuditPersistenceReceipt

- Purpose：证明被 Security policy 要求耐久化的 Audit Fact 已经落盘。
- Producer / Owner：执行该审计耐久化的 persistence boundary；Audit Requirement policy Owner 仍为 08。
- Consumer：08、06、02、09。
- Input / Output：Audit Requirement + source event identity + policy ref → committed / failed Receipt。
- Versioning：绑定 source event / requirement version。
- Validation：`MANDATORY_BEFORE_EFFECT` 类要求在高风险 Effect 前必须 committed。
- Failure Semantics：要求耐久但持久化失败时阻止或按明确 policy 降级；不能用 Telemetry 补齐。
- Idempotency / Replay：按 source event identity 去重。
- Security Requirements：redaction / minimization；Secret NEVER EXPORT。
- Persistence Requirement：Receipt 自身位于 durable boundary。
- Observability Requirement：Trace 可引用但不能替代。
- Evidence：Audit durability / audit-loss tests。

### B4 Domain / Control Objects

**Canonical Domain Kernel（正式领域内核）**第一阶段仅包括：Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct。Event、Conflict、Dispute、LegalIssue、StatuteVersion、LegalElement、ApplicableLaw、SimilarCase 默认是 Proposal / Projection / Derived View / Capability Output。

**Knowledge objects / facts**：KnowledgeGeneration、ProcessingItem / Projection、IndexManifest、Serving Watermark / ServingGeneration、ReadinessDecision、EvidenceCandidate、RetrievalResult、CitationLineage。KnowledgeView 可以作为派生视图概念；是否需要独立持久对象由 03 Deep Design 决定。

**Runtime control objects**：AgentRun、PlanVersion、StepRun、DispatchGroup / DispatchItem 或等价 LangGraph Send / branch identity、BranchResultRef、Budget、Join、Interrupt、Checkpoint、RunOutcome。具体自定义对象只有在 LangGraph 原生 primitive 不足时才引入。

**Tool effect objects**：PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt。

**Optional Context objects**：Session / Working Context、Summary、Preference、Experience Candidate 等，只属于 Context Provider，不得冒充 Domain Object。

### B5 State Machines

#### Formal Admission

```text
Proposal / EvidenceCandidate
→ EligibilityCheck
→ HumanDecision when required
→ Domain Admission
→ Domain mutation + AdmissionReceipt
→ Canonical DomainVersion / WorkProductVersion
```

历史 WorkProductVersion 不 destructive overwrite；新依赖变化通过 review-required / stale + new version 表达。

#### KnowledgeGeneration Lifecycle

```text
DECLARED
→ PROCESSING
→ STAGED / BUILT
→ SERVING
→ STALE / SUPERSEDED
→ REBUILDING when needed

any non-terminal stage → FAILED / PARTIAL_BUILD
```

这里描述一代可重建知识派生。`STAGED / BUILT != SERVING`。

#### Task-level ReadinessDecision

```text
(DocumentVersion refs
 + eligible serving KnowledgeGeneration
 + task Scope
 + minimum processing / retrieval requirements
 + current Security refs)
→ READY / PARTIAL / BLOCKED
```

PARTIAL 必须携带 covered scope / missing requirements。调用方缩小 Scope 后重新计算新的 ReadinessDecision，不能把原 PARTIAL 直接重命名成 READY。

#### Agent Runtime

```text
AgentRun
→ PlanVersion ACTIVE (immutable)
→ READY StepRun(s)
→ Action / Observation / Evaluation
→ Step Acceptance
→ Join / next steps
→ Final Gate / Final Reflection when required
→ RunOutcome
```

Plan assumption invalid → Replan Barrier → new PlanVersion。Late branch result 仍绑定旧 PlanVersion，不能污染新计划或越过 Domain Admission。

#### External Effect

```text
PreparedAction
→ AUTHORIZATION / APPROVAL / mandatory audit when required
→ ToolAttempt
→ SUCCEEDED / FAILED / OUTCOME_UNKNOWN
→ OUTCOME_UNKNOWN: Reconcile
→ CONFIRMED / NOT_EXECUTED / MANUAL_RECONCILIATION
```

### B6 Retry / Replan / Reconcile

| 控制 | 允许条件 | 结果 / 恢复锚点 |
| --- | --- | --- |
| Retry | 执行失败，但计划、依赖、能力、安全和输入假设仍成立 | 同一 Step / item / attempt identity 重试，保留 budget / idempotency |
| Replan | 计划结构、依赖、能力、权限或事实假设失效 | Replan Barrier 后创建新的 immutable PlanVersion |
| Reconcile | External Effect outcome unknown | 查询 operation id、idempotency key、EffectReceipt 或外部事实；禁止 Blind Retry |
| Recovery | Domain / Runtime / Knowledge 等持久边界不一致 | 使用对应 Owner 的 durable facts / Receipt 修复自己的 projection / control state |
| Staleness | canonical evidence / dependency change | 02 标记 formal result stale / review-required，并进行 bounded reevaluation |
| Knowledge rebuild | derived index / generation corruption | 从 DocumentVersion + processing spec + manifest 重建，不改写 historical citation |

### B7 Failure Semantics

统一原则是：**Provider 成功不等于业务成功；Provider 降级也不等于结果仍然有正式资格。**

- Model 503：计划仍正确时 Retry；重复失败可升级模型或由 Critic 判断 Retry / Replan / Abstain。
- Zero evidence / insufficient evidence：03 返回明确知识事实；04 / 05 决定 query rewrite、补检索、Replan 或 Abstain，不能由 Model 编造证据。
- Partial Knowledge：只能缩小 Scope、等待或 BLOCK；不能生成完整 Scope 的正式结果。
- Capability / Tool schema drift：重新解析 capability / tool semantics；计划假设失效则 Replan。
- DomainVersion conflict：02 不覆盖写；调用方读取最新版本后决定 Replan / Human Review。
- Security revoked：后续新的受保护访问 fail closed / pause。
- Audit persistence required but failed：在政策要求下阻止 Effect / Admission 或显式降级；Telemetry 不能补位。
- Consumer offline：不影响 Domain invalidation truth；01 保存 Delivery state 并重试。
- Memory unavailable：不依赖长期 Memory 的任务可以降级；关键业务事实不能依赖 Memory 才能恢复。

### B8 Security / Approval / Audit

所有跨边界受保护操作绑定 tenant、Matter / Scope、principal、Policy / Security Epoch、必要 idempotency / action identity 和 trace correlation ref。

08 是 Authorization、Approval、Model Egress、Tool Permission、Secret / Credential 和 Effective Lifecycle Policy 的唯一政策 Owner。各模块执行当前决定并保存自己的 enforcement fact，不自行放宽 policy。

HumanDecision 属于 02 Domain；ApprovalDecision 属于 08 Security。Approval for Effect 绑定 PreparedAction / action hash，不能用“这个人曾经批准过类似事情”作为重放授权。

Durable Audit 与 Telemetry 分离。OpenTelemetry / LangSmith / 日志丢失不能使 Domain、Approval、Effect、Admission 或 Mandatory Audit Fact 消失。Secret Material 不写入普通 Prompt、普通 Trace、普通 Audit payload、普通 Domain payload 或可被检索的 Knowledge metadata。

### B9 Recovery and Idempotency

恢复使用“各 Owner 的耐久事实”，而不是一个巨大的全局 checkpoint。

关键场景：

1. **Domain Commit + AdmissionReceipt success；Checkpoint fail**：04 查询匹配 Receipt，修复 Runtime Control State，不重复 Domain commit。
2. **Checkpoint completed；AdmissionReceipt missing**：Formal Admission 未被证明；不能把更高 DomainVersion 自动归因于当前 StepRun。
3. **Knowledge generation partial write**：03 不移动 Serving Watermark；按 generation / processing item identity 重试或重建。
4. **Serving pointer lost / drift**：03 从 durable generation / manifest 恢复合法 Serving；无法确认时 fail closed。
5. **External Effect unknown**：06 使用 action / operation / idempotency identity + Effect / ReconciliationReceipt 对账，不盲 Retry。
6. **Invalidation delivery failed**：01 重试 delivery；02 stale truth 保持不变。
7. **Late branch result**：04 根据 PlanVersion / StepRun causation 丢弃、重评或交 Human；不能覆盖新计划。

幂等原则：同一个稳定 identity + 同一规范化输入重放返回既有合法结果；同 identity 不同输入必须冲突失败。不同模块拥有不同幂等域，不能用一个 request_id 假装解决所有 Domain / Tool / Delivery / Knowledge idempotency。

### B10 Persistence Boundaries

- 02 Domain Store（默认 PostgreSQL）：Canonical Domain State、version、dependency、HumanDecision、WorkProductCitationBinding、AdmissionReceipt。
- 04 Runtime Checkpointer：Graph control / execution state；LangGraph 官方 PostgreSQL Checkpointer 是当前 Target provider 选择之一，但不拥有 Domain truth。
- 03 Knowledge Store / Providers：generation metadata、processing status、manifest、serving pointer、necessary lineage、rebuildable index / graph projection。
- Optional Context Provider：policy-scoped working / session / long-term context。
- 06 Tool persistence：PreparedAction / ToolAttempt / EffectReceipt / ReconciliationReceipt。
- 08 / audit boundaries：Security decision refs、Approval、Lifecycle policy refs、required AuditPersistenceReceipt。
- 09 Observability Store：Trace / Metric / Eval projection。
- Platform / Infrastructure：提供 object store、queue、lease、CAS、clock、backup / restore、network、secret delivery 等物理耐久与运行原语。

关键事务：

```text
expected DomainVersion check
+ canonical Domain mutation
+ matching AdmissionReceipt
+ admission-critical dependency / citation facts when required
= one Domain transactional durability boundary
```

Knowledge Serving activation 是 03 自己的 manifest / pointer 可恢复切换；它不和 02 Domain transaction 或 04 Runtime Checkpoint 做跨 Store 2PC。Queue ACK、Index write、HTTP 2xx、Checkpoint commit 都不能冒充 Domain Success。

### B11 Observability / Evaluation

跨层使用 OTel-compatible Telemetry Contract，至少贯通 request / task、run、PlanVersion、StepRun、knowledge generation、domain version、action identity 和 security epoch 的 correlation refs。09 负责 Projection 和 Evaluation，不拥有业务 truth。

评测至少分两类：

**运行 / 产品复杂度 A/B/C：**

- A：Generic Host + Legal Skills；
- B：Generic Host + Zuno Legal Backend；
- C：Zuno Native Runtime + first-class Domain State。

比较 Citation Correctness、Evidence Sufficiency、Unsupported Claim Rate、Reviewer Acceptance、Applicability Accuracy、Task Completion、Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls、Domain State Reuse Rate 和 recovery / safety behavior。

**模块内部评测：**

- 02：provenance completeness、formal admission correctness、human review、staleness propagation、recovery；
- 03：processing coverage、Readiness correctness、retrieval quality、citation lineage completeness、serving switch / rebuild、GraphRAG query-class gain；
- 04：plan success、retry / replan correctness、parallel join、late branch、budget；
- 06：duplicate effect / timeout / reconciliation；
- 08：revocation、egress、approval binding、lifecycle；
- 09：telemetry loss tolerance、eval reproducibility。

Offline Release Eval 不等于单次任务 Formal Admission 或 Answer Publication eligibility。

### B12 Current / Target / Gap

| 能力 | 架构状态 | Current / Gap 说明 |
| --- | --- | --- |
| 9-module Responsibility Taxonomy | `FROZEN TARGET` | Round 02 已冻结；不等于九模块都已完整实现 |
| 9 Module Design Baseline V1 | `AVAILABLE` | 九篇模块正文已建立；字段级 Detail Freeze 仍 `NOT_YET` |
| 9 Module Deep Design V2 | `AVAILABLE` | 9/9 完成；Cross-Module Consistency V1 与 Human-first 叙事已深化，仍不等于实现 |
| Legal Domain minimal kernel | `ACCEPTED TARGET` | Current 只有有限 mutation / provenance evidence |
| AdmissionReceipt | `ACCEPTED TARGET` | 语义已冻结；完整 DB / fault-recovery 仍未证明 |
| WorkProductCitationBinding | `ACCEPTED TARGET` | 与 Index identity 分离；完整历史替换测试待补 |
| KnowledgeGeneration + task ReadinessDecision | `TARGET / DEEPENING` | Current 有 ingestion / provenance / index 表面；完整 serving / readiness E2E 待证明 |
| Simple QA outside Native Runtime | `ACCEPTED TARGET` | Host / direct integration 仍需可重复验证 |
| Native Runtime | `CONDITIONAL / MEASUREMENT-GATED` | 未证明优于 Generic Host + Legal Backend |
| Long-term Memory | `OPTIONAL / MEASUREMENT-GATED` | 可外置或删除 |
| Specialist / Multi-Agent | `OPTIONAL / MEASUREMENT-GATED` | 默认 Single Controller；优先 parallel steps / subgraphs |
| GraphRAG | `QUERY-CLASS / EVIDENCE-GATED` | 不能因图存储存在就视为默认能力 |
| Security / Tool Effect / Audit full closure | `TARGET WITH PARTIAL CURRENT FOUNDATION` | 需故障注入、E2E 和资格证明 |
| Production Readiness | `NOT ESTABLISHED` | 正式 Benchmark、生产负载、DR / HA / security / operational attestation 未闭合 |

模块 Deep Design 的存在意味着可以继续字段级 Detail Design 与逐模块 Freeze Review；它不授权 Codex 自动实现所有 Target。

### B13 Evidence / Verification

Target 进入 Current 前，按风险需要代码、Migration、Unit / Integration Test、Fault Injection、E2E、Trace / Eval 和真实运行证据。当前可复核入口见 [`docs/evidence/`](../evidence/README.md)。

跨层重点证据包括：

- Simple QA Host Integration；
- Simple RAG vs Legal Backend；
- A/B/C Runtime Kill Test；
- Domain admission causation / crash recovery；
- real PostgreSQL concurrency / CAS；
- Partial Knowledge / Serving switch / stale generation；
- Citation lineage / historical citation replacement；
- new evidence → stale / bounded reevaluation；
- Dynamic Permission Revocation；
- Tool Duplicate Effect / Timeout / Reconciliation；
- Invalidation Delivery with offline Consumer；
- Graph / Memory / Multi-Agent ablation；
- Evidence-gated Service Split。

Architecture Revision 或 Module Design 本身都不是这些实验的结果。

### B14 Code / Database / Migration Constraints

当前总体架构和九模块 Deep Design 已建立，但 **implementation_authorization: NO**。本阶段不因为文档深化自动授权新增 AdmissionReceipt table、完整 Lifecycle Engine、Invalidation Outbox、Tool Runtime 重构、数据库大迁移、Kafka、Kubernetes、Event Sourcing、跨 Store 2PC 或九个网络服务。

`docs/modules/01-*.md` 到 `09-*.md` 已经是当前模块设计正文；后续实现必须读取总体 Part A / B、目标模块 Part A / B / C、相关 ADR 和 Current Evidence。模块 Detail Design 可以进一步冻结字段、enum、transaction、API / schema 和 Migration 约束，但这些冻结必须先通过模块审查，不能从已有类名或数据库表反向推导。

如果模块深化发现必须改变九模块 Owner、Canonical Kernel、Formal Admission causation、Knowledge / Domain authority、Retry / Replan / Reconcile、安全政策 Owner 或物理拆分原则，应停止局部设计并记录 Architecture Gap，而不是在模块文档或代码里悄悄改变 Overall Architecture。

## Architecture Freeze Boundary

当前状态仍是 `ROUND_02_FROZEN`：Overall Target Architecture 和九个 Logical Responsibility Modules 已冻结；Module Decomposition Gate 已打开，九模块 Design Baseline V1 与 Deep Design V2 / Cross-Module Consistency V1 已存在，Human-first Part A 已深化，Module Detail Freeze 仍未完成。实现、Measurement 和 Production Readiness 需要独立授权与证据。
