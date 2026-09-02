# Zuno 总体 Target 架构

Zuno 的总体架构围绕一个问题展开：当法律工作从一次问答变成持续数十分钟甚至更久的专业任务时，系统怎样保证材料、分析、人工判断、正式成果和外部动作始终有清楚的来源与恢复依据。

简单问题不需要复杂架构。用户只想查询一条合同原文时，受控检索和一次模型生成通常已经足够。只有当同一事项包含多版材料、长期业务状态、人工复核、权限变化、系统崩溃或现实副作用时，Zuno 才逐步引入更强的领域和运行机制。架构复杂度来自这些具体约束，而不是来自框图本身。

本文描述 Target（目标架构）。对象、Contract（契约）和状态出现在文档中，不代表它们已经全部成为 Current（当前实现）；历史 Pilot 也不等于 Production。项目背景与真实经历见 [`docs/project/project.md`](../project/project.md)，Current 证据见 [`docs/evidence/`](../evidence/)，模块内部设计见 [`docs/modules/`](../modules/README.md)，历史架构审查见 [`docs/maintenance/history/red-blue/`](../maintenance/history/red-blue/README.md)。

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

### 1. 从一次法律问答到长期法律工作

先看一个简单任务。用户询问“合同第 8 条写了什么”，系统确认访问权限，检索对应材料，再生成带引用的回答。只要任务到这里结束，普通应用服务、受控 RAG 和模型调用已经能够很好地完成工作。

复杂法律任务的性质不同。一个事项可能同时包含起诉材料、答辩材料、合同、补充协议、扫描附件和后续证据；模型可以提出事实和结论，但专业人员可能接受、修改或拒绝；成果交付以后还可能出现新材料；整个任务运行期间又可能发生权限变化、模型失败、服务重启或外部系统超时。

这时系统要保存的已经不只是“最后一段回答”。它必须能够说明依据的是哪一版材料，哪些内容只是机器候选，哪些已经成为正式业务事实，谁做过人工判断，旧成果为什么进入复核，以及故障发生后应该相信哪一份耐久记录。

Zuno 因而保留两种尺度：简单任务继续走短路径；涉及版本、人工判断、长期状态或现实副作用的任务，才进入更强的事实边界和恢复机制。

### 2. 最简单的系统，以及它开始失效的地方

一个自然的起点是“通用 Agent Host + 法律知识库”。Host 负责会话和工作流，知识库负责检索，模型负责生成，需要时再调用若干 Tool。对于低风险、短生命周期任务，这个方案完全合理，而且应该优先复用。

困难出现在几种状态被压成同一个 `success` 以后。文件上传成功，不代表关键附件已经完成 OCR；向量写入成功，不代表当前任务已经具备完整知识；模型返回 200，不代表结论已经被专业业务接受；Workflow completed，也不代表正式领域事务已经提交。

外部动作更加危险。一个 POST 请求超时，可能是远端没有执行，也可能是远端已经成功但响应丢失。入口鉴权同样不是永久通行证：十分钟前允许访问，不代表十分钟后新的模型外发或高风险 Tool 仍然允许。

这些差异把问题指向了状态和权威：不同事实有不同的生命周期，也需要不同的耐久记录来证明。Zuno 后面的责任划分都从这条约束展开。

### 3. 四种不能混在一起的“成功”

在一条完整任务链中，至少存在四种不同的成功。

第一种是**计算成功**：检索、模型或专业算法得到了结果。第二种是**运行成功**：某个 Step 或整次 Run 按控制逻辑执行完成。第三种是**业务正式成立**：法律领域接受了某个事实或工作成果，并留下了耐久版本。第四种是**现实动作发生**：外围系统确实执行了提交、创建、发送或其他副作用。

四种成功前后相连，但每一种都需要自己的证明。模型返回结果，仍可能被专业规则拒绝；Runtime 认为 Step completed，仍可能缺少正式业务提交；一个正式 WorkProduct 已经存在，后来又可能因为新证据而失效；HTTP timeout 更不能直接证明远端动作失败。

恢复从事实类型开始：先确认当前问题属于计算、运行、领域还是外部效果，再读取拥有那类事实的耐久记录。

### 4. 机器结果首先是候选

机器生成的信息天然带有不确定性。材料可能过期，检索可能只覆盖部分范围，模型可能理解错误，专业算法也可能只适用于某些案件类型。让机器输出直接覆盖正式业务状态，会使人工复核、版本演进和责任追踪失去边界。

Zuno 因此把检索结果、模型判断和专业算法输出先视为候选。检索可以提出证据候选，Capability 可以提出专业分析结果，模型可以提出计划、结论或动作建议；只有在材料版本、证据条件、安全要求和必要的人审都满足以后，正式业务事实才成立。

工程上，这个区别被压缩成一些对象名称，例如 `EvidenceCandidate` 与 `Evidence`。前者表示“机器认为可能有用”，后者表示“业务已经正式接受”。对象名称只是把这层语义压缩成工程接口。

引用也有同样的区别。检索引用解释这一次为什么找到某段内容；正式 WorkProduct 的引用则要保存当时真正采用的不可变材料版本和稳定位置。索引可以重建，历史成果的依据不能跟着重建结果漂移。

### 5. 按事实权威划分责任

如果只按照 FastAPI、PostgreSQL、LangGraph、Milvus、Neo4j、LLM 和 Worker 来画系统，可以知道组件在哪里，却很难在故障时回答“谁说了算”。

同样写进 PostgreSQL 的两类数据，可能拥有完全不同的意义。Runtime Checkpoint 记录任务执行到哪里，Domain State 记录哪些法律事实已经正式成立；二者使用相同的存储技术，并不意味着一个能够替代另一个。

Zuno 因此优先按照事实权威划分责任：谁有资格创建某类事实，谁能让它失效，谁能证明它完成，系统崩溃以后应该先读谁的耐久记录。这里所说的 Ownership，不是代码目录的归属，而是业务事实最终由谁确认。

九个逻辑责任域由此形成：它们先固定长期语义边界，部署形态另行决定。

### 6. 材料、知识派生与正式业务事实

一份正式材料进入系统以后，首先需要稳定的版本身份。系统随后可以围绕这份材料生成 OCR、切分、向量、图结构和其他检索视图。这些内容属于派生知识：算法升级以后可以重建，必要时也可以全部重新生成。

正式业务事实采用另一套生命周期。某份 WorkProduct 在历史上引用了合同 v2，那么以后即使切分器、Embedding 或图索引全部升级，这份历史成果仍然必须能够回到当时使用的合同 v2 和稳定位置。

知识处理还要回答任务是否可用。一代索引“构建完成”只描述知识派生自身的状态；具体任务还要检查它需要的材料和覆盖范围。九十八份材料已经完成处理，剩下两份却可能恰好决定核心争议。于是系统必须同时描述材料版本、派生知识的生成状态，以及面向具体任务的知识就绪判断。

工程上，这三类概念分别落在 `DocumentVersion`、`KnowledgeGeneration` 和 task-level `ReadinessDecision` 上。它们分开以后，系统既可以大胆重建检索表示，又不会把“知识库看起来健康”误写成“任何任务都已经 Ready”。

### 7. 领域状态与运行状态

复杂任务需要运行状态：计划进行到哪里，哪些步骤完成，哪些分支仍在等待，预算还剩多少。法律业务也需要正式状态：哪些 Evidence、Finding 和 WorkProduct 已经成立，哪些版本已经失效，哪些人工决定已经记录。

这两类状态会互相引用，却回答不同问题。最典型的故障发生在 Domain transaction 已经成功提交，但 Runtime 还没来得及写下一次 Checkpoint 时。进程此时崩溃，重启以后只相信 Checkpoint，就可能认为业务步骤尚未完成并再次提交。

Checkpoint 写成 completed 时，能够证明的是控制进度；正式业务事务是否提交，仍由 Domain 的耐久事实证明。

因此，正式业务提交需要留下独立的耐久证明。Zuno 用 `AdmissionReceipt` 表达这一类提交因果：指定的 run、plan 和 step 确实导致了某个正式 DomainVersion。恢复时先查 Domain 是否已经完成，再修复 Runtime，而不是让运行检查点覆盖业务事实。

### 8. 长任务的计划与控制

当一个任务包含多个依赖步骤、并行执行、人工等待和工具调用时，控制过程不能只存在于模型的上下文中。否则服务重启以后，系统连“原来准备做什么”都无法可靠恢复。

Zuno 的原生 Runtime 因此显式保存计划。简单任务仍然可以是一条确定性的单步计划；复杂任务才使用动态 DAG。计划表达依赖、并行、等待、预算和下一步动作。正式业务权威仍然留在对应的 Domain Owner。

一旦某个 PlanVersion 被激活，它保持不可变，使已经派发出去的工作拥有稳定的因果归属。需要改变任务结构时创建新的计划版本，而不是在旧计划上原地修改。

控制权保持单写者。一个 AgentRun 可以并行执行多个专业 Step，也可以使用 Specialist Agent 或 Subgraph，但计划激活、Step acceptance、预算、Replan 和 cancel 最终由 Single Controller 收敛。并行负责扩大执行能力；全局计划仍由一个控制者收敛。

### 9. 三种不同的恢复动作

“失败以后再试一次”只适用于一部分问题。Zuno 把 Retry、Replan 和 Reconcile 分开，是因为它们面对的是三种不同的不确定性。

如果模型服务暂时返回 503，但输入、权限和执行计划都没有变化，再执行同一个步骤通常是合理的，这属于 **Retry**。

如果新材料进入、Tool schema 改变、Capability 不再可用，或者旧计划依赖的事实已经失效，继续执行原步骤没有意义。这时应该形成新的计划版本，也就是 **Replan**。

还有一种情况更危险：系统已经向外围系统发送请求，但在收到响应以前连接中断。我们不知道过去的动作到底有没有发生。此时首先要确认现实状态，而不是再次发送，这属于 **Reconcile**。

所以：

`Retry != Replan != Reconcile`

这个区分决定了系统下一步是否可以自动行动，也构成了故障恢复的基本语言。

### 10. 长任务中的持续授权

一次 HTTP 请求通常在入口完成鉴权，但长任务可能持续几十分钟，中间等待人工、读取新的材料、调用多个模型和 Tool。期间用户权限、事项归属、数据密级、模型外发政策、审批状态和凭证版本都可能发生变化。

因此，“任务开始时允许”不能变成后续所有动作的永久通行证。每当系统再次跨越一个受保护边界，例如读取新的敏感材料、把数据发送给模型、获取 Secret、执行高风险 Tool 或提交正式业务结果，都需要消费当前有效的安全决定。

过去已经合法发生的动作仍然是历史事实；安全变化影响的是未来能不能继续。这种时间边界使系统既能保留历史，又不会因为旧授权缓存而继续扩大风险。

Authorization、Approval 和 HumanDecision 也必须分开。有权执行某类动作、某个具体高风险动作已经获批、专业人员接受某个法律结论，是三种不同责任。

### 11. 外部副作用与现实结果

内部计算可以重算，现实副作用往往不能撤回。向外围法院系统创建记录、提交材料或触发流程时，本地网络状态并不能代表远端业务状态。

Zuno 因此在发送以前先形成稳定的动作身份和内容，工程上称为 `PreparedAction`。实际调用形成 `ToolAttempt`；确认远端动作以后保存 `EffectReceipt`。如果结果未知，就沿 operation id、业务唯一键或稳定 idempotency identity 查询过去到底发生了什么，并形成 `ReconciliationReceipt`。

这套结构避免了一个常见错误：把 timeout 直接写成 Failed，然后盲目重试。对只读查询，这种做法可能只是浪费一次调用；对创建、支付、提交、发送等副作用，它可能制造重复现实动作。

高风险动作还可能要求在执行前证明强制审计已经耐久化。普通 Trace 可以采样或丢失，所以 Zuno 把必要的审计持久化和普通 Telemetry 分开。

### 12. 九个逻辑责任域

到这里，九个责任域已经可以从问题本身自然得到。

**01 Application & Integration** 负责外部请求、Scope、结果发布、交付和失效通知，把多个内部 Owner 的事实组合成产品语义。

**02 Legal Domain & Work Product** 负责长期、正式、可审计的法律业务事实，包括 Evidence、Finding、HumanDecision 和 WorkProduct，以及正式准入与失效。

**03 Knowledge & Evidence** 围绕正式材料版本维护可重建知识派生、任务级就绪判断、检索候选和引用来源。

**04 Agent Runtime & Control** 负责复杂任务怎样继续执行，包括 Plan、Step、并行、等待、预算、取消、重规划和 Checkpoint。

**05 Capability & Skill** 把研究模型、算法、规则和外部服务整理成稳定、版本化、可替换的专业能力。

**06 Tool Runtime & Effects** 负责现实副作用的准备、尝试、确认、幂等和对账。

**07 Model Gateway** 把模型调用收敛成受控依赖，按照角色、质量资格、数据政策、预算和 Provider 状态选择模型，并记录真实调用和成本。

**08 Security & Governance** 负责授权、审批、Secret 使用、数据生命周期和强制审计要求，并在长任务中持续判断下一步是否仍允许。

**09 Observability & Evaluation** 一方面解释系统发生了什么，另一方面通过可复现实验判断复杂机制是否值得保留。

这些责任域描述的是事实归属，不是固定的调用顺序，也不是部署拓扑。

从业务角度看，它们共同回答的是一组连续问题：外部请求怎样进入系统，哪些材料能够被当前任务使用，机器怎样产生候选，专业结果怎样正式成立，长任务怎样继续，研究能力怎样被选择，模型怎样受控调用，现实动作怎样确认，最后又怎样解释整个过程。把这些问题分别交给明确责任域以后，单个模块就不需要通过读取其他模块的内部状态来猜测更强事实。

这也是为什么模块之间更适合交换 Decision、Receipt、Version 和 Reference，而不是共享一张“万能状态表”。前者明确告诉消费者某个 Owner 真正承诺了什么，后者很容易让每个调用方按照自己的理解解释同一个字段。

### 13. 三类任务路径

同一套边界并不意味着所有任务拥有同样复杂度。

简单问答从请求和 Scope 开始，检查授权和知识就绪，检索材料，调用模型生成并校验引用，最后由应用层决定是否发布。它完全可以绕开动态计划、正式领域准入和 Tool Effect。

复杂分析在同样的材料基础上增加显式 Plan、专业 Capability、并行和人工复核。机器中间结果可以很多，但只有真正要成为正式法律工作成果的内容才进入 Domain Admission。

带现实副作用的任务则再增加 Effect Control。模型或 Capability 可以提出动作建议，却不能直接发送；动作必须先经过安全、审批、审计和幂等准备，再由 Tool Runtime 记录真实尝试与结果。

这三条路径共享事实边界，却根据任务风险逐步增加机制。

### 14. 一个关键崩溃窗口的恢复

仍然回到那个复杂案件。系统已经完成专业分析，Domain transaction 成功提交正式 WorkProduct，但 Runtime 在写下一次 Checkpoint 以前进程崩溃。

重启以后，旧 Checkpoint 可能仍然显示这一步尚未完成。如果直接按照控制状态重跑，就可能产生重复正式提交。

正确的恢复顺序是先查询 Domain Owner 的耐久事实和匹配的 `AdmissionReceipt`。如果正式提交已经存在，就把它作为更强的事实，再修复 Runtime 的 Step acceptance 和 Checkpoint；只有在确认正式提交不存在时，Runtime 才考虑重新执行后续动作。

这个例子体现了一条贯穿 Zuno 的原则：**先恢复拥有业务权威的事实，再修复缓存、检查点和其他派生状态。**

### 15. 新证据与历史成果

法律工作会随着新材料继续变化。旧 WorkProduct 在产生时可能完全合理，但新证据进入以后，它可能不再适合继续发布或引用。

Zuno 不通过删除旧版本来制造“始终一致”的假象。旧版本仍然记录当时基于哪些材料和判断产生；新的材料变化形成新的领域事实，并沿依赖关系决定哪些 Finding 或 WorkProduct 进入 stale / review-required。

这使系统同时保留两种能力：历史版本仍可审计，当前有效性又能被单独查询。后续重评也可以沿依赖范围有界传播，而不是每次材料变化都无条件全案重跑。

Application 负责把失效变化交付给外部消费者，但外部系统离线不能阻止 Domain truth 立即发生变化。业务事实和通知状态仍然是两件事。

### 16. 研究能力与可替换实现

Zuno 来自智慧司法研究背景，因此会使用事件抽取、冲突识别、类案检索、GraphRAG、Memory、Reflection 等能力。研究积累很重要，但论文或框架本身不应该成为运行时长期依赖的接口。

一个专业能力可能先由论文模型实现，后来换成规则系统、LLM 或外部服务。对上层来说，真正应该稳定的是“事件抽取需要什么输入、返回什么结果、在什么条件下合格”，而不是某个具体类名。

因此，研究成果先进入稳定的 Capability 语义，再由一个或多个版本化 Provider 实现，通过 Conformance 和 Eval 判断是否具备当前任务资格。这样实现可以迭代，Runtime 不需要随着论文模型或 SDK 一起改写业务语义。

同样，GraphRAG、长期 Memory、Reflection 和 Specialist 都应该保留更简单的 baseline。它们必须在特定任务上证明边际收益，而不是因为已经实现就获得永久地位。

### 17. 逻辑边界与物理部署

九个逻辑责任域首先回答“谁负责哪类事实”，并不要求九个独立服务。默认物理形态完全可以是模块化 Python 后端，加上根据工作负载需要拆出的 Worker。

知识构建、模型调用、Tool 执行和 Eval 的资源特征不同，因此可以拥有不同的 Worker pool、并发限制和队列；这仍然不意味着每个逻辑 Owner 都必须拥有独立进程和数据库。

只有当 Secret isolation、独立吞吐、故障半径、网络出口、合规边界或部署生命周期形成明确需求时，才值得把某个逻辑边界提升成独立网络服务。

物理拆分是成本很高的优化。逻辑 Ownership 先稳定，服务边界再由规模和安全证据决定。

### 18. 复杂度的退出机制

复杂机制需要同时写清引入条件和退出条件。

如果简单 RAG 已经满足目标任务，就不需要 Native Runtime；如果 Hybrid Retrieval 已经覆盖某类 query，就没有必要默认启用 GraphRAG；如果通用 Host + Zuno Legal Backend 已经能够保护正式状态和恢复，就不需要复制完整宿主；如果一个逻辑模块没有独立扩缩容或安全隔离需求，也没有必要拆成微服务。

每增加一个状态机、Provider、缓存、图存储、Agent 层或服务边界，都会增加维护成本和新的故障面。因此评测不仅用于证明“功能能工作”，还要帮助团队判断它是否值得长期保留。

Zuno 在业务约束成立时增加机制；证据消失时退回更简单的方案。

这种退出机制还可以反过来约束设计阶段。一个新组件如果只能回答“它能做什么”，却回答不了“没有它会发生什么错误”“更简单方案在哪里失败”“什么测量结果出现时可以删掉它”，那么它还没有获得成为长期架构边界的资格。把删除条件和引入条件放在一起讨论，可以防止研究型项目因为不断接触新框架而自然膨胀。

**时间是架构的一部分。**

静态架构图只能说明某一时刻有哪些对象。真实系统的问题往往来自时间：材料会升级，权限会撤销，模型和 Capability 会换版本，旧计划的并行结果可能晚到，外部 Effect 也可能在本地不知道的时候已经发生。

因此 Zuno 使用多个版本并不是为了形式化。`DocumentVersion` 保护材料身份，`KnowledgeGeneration` 保护可重建知识派生，`PlanVersion` 保护运行因果，Capability / Model version 保护计算语义，Security Epoch 保护授权新鲜度，DomainVersion 保护正式业务演进。

这些版本不能粗暴合并成一个全局版本号，因为它们变化的原因和 Owner 不同。一个旧模型结果并不因为“时间旧”就必然无效；如果材料、专业语义和安全条件都没变化，它可能仍然可用。反过来，一个刚刚算完的结果，如果所依赖的材料或权限已经变化，也可能立即失去进入正式路径的资格。

### 20. 跨模块的一致性与恢复

Zuno 横跨数据库、索引、模型 Provider、外围系统和观测系统。很多参与者无法加入同一个数据库事务，已经发出的外部请求也无法通过 2PC 回滚，因此跨模块恢复不能依赖一个全局原子提交。

更现实的策略是让每个 Owner 在自己的事务边界内保存足够强的事实，再通过版本、Receipt 和稳定幂等身份形成可恢复的因果关系。

于是，跨模块短暂不一致是允许的，但恢复顺序必须明确。Domain 已经提交、Checkpoint 落后，就以 Domain Receipt 修复 Runtime；Effect 已确认、交付 Projection 落后，就以 Effect truth 修复交付状态；知识生成部分失败，则不移动 Serving 指针。

这形成了**可恢复一致性**：系统允许短暂不同步，但每一种不同步都有明确的事实来源和修复顺序。

**成功不能证明更强的事实。**

跨层错误常常来自过度解释：一层的成功被消费者当成了更强的事实。

Provider 200 只说明一次调用返回成功，不能证明专业质量；Capability 执行成功不能证明 Domain 已经正式接纳；Checkpoint completed 不能证明业务事务已经提交；HTTP 200 也不能证明远端后续业务流程全部完成；Trace exported 更不能证明强制审计要求已经满足。

因此，每个边界除了说明“我能证明什么”，还要明确“我不能证明什么”。工程上有时把后一类约束称为 Non-proof，但正文里更重要的是理解边界本身：消费者只能使用 Owner 真正承诺的事实，不能顺便猜一个更强结论。

失败也同样不能统一成一个 ERROR。计算失败、输入过期、计划失效、安全拒绝、结果未知和人工待处理需要不同的后续动作。

**性能优化不能改变事实语义。**

缓存、并行、批处理、异步 Worker、预取和 Read Replica 都可以提高性能，但优化不能改变原来的事实边界。

Cache 可以保存派生结果，却不能延长授权寿命；并行执行可以提高 Capability 吞吐，却不能制造多个 Controller；异步 Delivery 可以让外部系统离线时继续工作，却不能推迟 Domain 中的失效事实；Read Replica 可以扩展查询，却不能让旧 Projection 覆盖 Owner 的写入事实。

后台任务越多，越需要显式携带 tenant、Matter、版本和安全上下文。否则系统为了提高吞吐，把请求从原始 HTTP 上下文中分离以后，反而会丢掉原来保护正确性的条件。

性能优化先保持 Authority 和因果关系，再讨论吞吐和延迟。只要优化改变了“谁说了算”或“结果基于什么”，它就已经越过了原来的架构边界。

**基础设施复用与自研边界。**

Zuno 对基础设施采用复用优先原则。身份认证、Secret Manager、PostgreSQL、OpenTelemetry、通用 Checkpointer、消息队列和模型 SDK 都应该优先使用成熟能力。

自研的判断从业务约束出发。成熟方案已经满足要求，就直接 Adopt / Buy；只缺一层法律语义，就在其上 Extend；当前没有真实需求或证据，就 Defer。只有现成方案无法保护正式状态、恢复、安全隔离或专业质量，而且这个缺口长期属于 Zuno 的业务责任时，才值得 Build。

同样的原则适用于 Agent 框架。LangGraph 可以提供 Send、Reducer、Checkpointer 和 Subgraph 等运行原语，却不会自动拥有 Formal Admission；通用 Host 可以提供会话和 UI，却不会自动定义法律 Domain；图数据库可以保存图结构，却不会自动证明 GraphRAG 值得启用。

框架提供能力，业务约束决定架构。

**安全的降级。**

降级策略取决于失败发生在哪一层。

如果强模型不可用，而低成本模型在当前任务上仍满足质量和数据政策，可以降级模型；如果 Graph 路径不可用，而 Hybrid Retrieval 足以支持当前问题，可以退回简单检索。

但关键材料缺失时，正确降级可能是缩小 Scope 或等待；权限无法确认时应该 fail closed；外部 Effect 结果未知时应该等待 Reconcile；正式 Eval 缺少必要数据时应该明确 BLOCKED。

系统韧性包含三种选择：少做、晚做和停止。它们和“继续执行”一样，都是明确的控制结果。

**工程证据与架构取舍。**

测试通过可以证明某个 Contract 按当前设计工作，却不能证明这个 Contract 值得长期存在。复杂机制还需要另一类证据：它是否在目标任务上改善了质量、恢复、成本、时延或人工负担，并且收益是否大于维护复杂度。

GraphRAG 的单元测试只能证明图检索“能工作”；只有和 Hybrid Retrieval 的对照实验才能证明它有边际价值。Native Runtime 的 crash recovery 测试可以证明恢复机制正确，却还要和 Generic Host + Legal Backend 比较，才能判断自研运行时是否值得长期维护。

因此，Evaluation 的结果应当能够导致保留、缩小、替换或删除。评测结果会反过来修改架构：保留、缩小、替换或删除都属于正常演进。

**边界的价值在于减少错误推断。**

很多跨模块 bug 并非计算错误，而是消费者把别人的状态解释得太强。

看到索引构建完成，就推断任务 READY；看到 Step completed，就推断 Domain 已提交；看到 HTTP timeout，就推断 Effect 失败；看到十分钟前的 Authorization allow，就推断现在仍然允许。这些都属于跨边界的错误推断。

因此，一个健康的 Contract 应该让消费者获得完成当前判断所需的事实，同时又不会诱导它升级成更强结论。如果多个消费者都在复制同一段“猜测逻辑”，通常说明这个判断应该收回真正的 Authority。

删除测试也可以用来检查边界价值：拿掉某一层以后，如果系统立即被迫把弱事实当成强事实，这个边界很可能有必要；如果删除以后重要不变量仍能被更简单组件保护，就应该继续质疑这层复杂度。

### 27. 稳定的是语义，不是今天的实现

系统既不能把所有东西都称为“可替换”，也不能把今天的框架和表结构永久冻结成架构事实。

真正需要稳定的是几条语义不变量：机器结果先是候选；正式业务事实由 Domain Owner 准入；Runtime Checkpoint 不能单独证明 Domain Commit；现实结果未知不能盲重试；新的受保护动作需要重新消费当前授权；更强事实必须拥有明确的完成证明和恢复顺序。

应该允许替换的是 Provider、模型、检索算法、Checkpointer 实现、Queue、Cache、ORM、表结构以及大部分物理部署。

如果更换一个 SDK 就需要重新解释“什么算正式成功”，说明实现细节已经泄漏进业务权威；如果替换以后上层仍然可以依赖同样的 Owner 和完成语义，说明边界是健康的。

### 28. 架构演进必须包含迁移

Target 描述最终想达到的结构，但真实系统不会在一个瞬间切换。旧 Run 可能仍在执行，旧 WorkProduct 仍要被审计，历史记录还会引用旧 Provider 版本，数据库也需要逐步迁移。

安全迁移首先要保证旧事实仍然能够被新系统读取和解释。随后建立可验证的新写路径，对可重建 Projection 做 backfill 或重建，最后在恢复演练和完成证明成立以后再切换流量。

迁移过程中不能长期保留两套都声称权威的事实源。网络拓扑可以变化，逻辑 Owner 不能因为搬服务就被复制成两个业务真相。

迁移成功也不只是“新代码已经部署”，而是旧任务仍能恢复、历史成果仍能解释、故障发生时仍然知道应该相信谁。

### 29. 过载与局部故障

高负载下最危险的行为，是为了让指标保持绿色而模糊业务事实。Queue 满了仍无限受理、Policy 服务不可用就沿用旧 allow、模型超时就把任务写成业务失败、Telemetry 丢失就假设动作没有发生，都会把容量问题升级成正确性问题。

Zuno 更希望各责任域拥有自己的安全背压。知识构建拥塞可以让新的 generation 排队，但不能污染当前 serving；模型容量不足可以等待或切换合格候选，但不能偷偷放宽数据外发政策；安全事实无法确认时高风险路径 fail closed；Effect outcome unknown 时进入 Reconcile，而不是为了释放队列强行写 Failed。

资源隔离也不等于每个模块一个服务。批量 OCR、Eval、模型调用和在线 validity query 可以先通过 Worker pool、quota、priority 和 admission control 隔离，只有这些手段不足时才考虑更重的网络拆分。

### 30. Current、Target、Evidence 与 Unknown

本文描述的是 Target Architecture。九个责任域、Formal Admission、Single Controller、Knowledge / Domain 的权威边界、Effect Recovery 和持续授权都属于已经接受的目标设计，但它们不等于全部代码、表、Migration、Provider、HA 和生产流程已经完成。

Current 只能由今天 `main` 上的代码、Migration、测试、Trace、Eval 或真实运行证明。历史 Pilot 也只能说明项目曾经进入试点，不能替代今天的生产负载、DR、安全资格和运行证据。

Evidence 负责把 Target 中的一项设计逐步升级成 Current，或者证明它没有价值而应该退出。Unknown 则表示目前还没有足够材料回答的问题。

因此，Project、Architecture、Modules 和 Evidence 各自拥有不同问题：Project 解释为什么做以及历史发生过什么；Architecture 解释目标边界；Modules 解释每个责任域内部怎样工作；Evidence 解释今天到底做到了哪里。

### 31. 总体架构留下的几条原则

读完整体架构以后，最值得保留的不是九个模块名称，而是几条可以反复用于判断设计的原则。

简单任务保持简单；机器输出先作为候选；正式业务事实、运行控制、知识派生、安全决定和现实副作用分别由对应的事实 Owner 负责；故障恢复先寻找最强的耐久事实，再修复派生状态；授权在新的受保护动作发生前重新判断；现实结果未知时先对账，不能盲目重试；复杂机制必须能够被测量，也必须允许被删除。

这些原则构成 Zuno 的长期骨架。具体对象名、字段、Provider、数据库和部署方式都可以继续演进，只要它们没有破坏这些已经接受的事实权威和因果关系。

从实现角度看，后续所有模块设计都应该能够回到这些原则。如果某个局部优化要求把机器候选直接写成正式领域状态，或者为了减少一次查询而让旧授权永久有效，这种“优化”实际上已经改变了总体架构；相反，如果只是更换模型、索引、队列或 Checkpointer，而完成证明和恢复顺序保持不变，它通常只是实现层演进。

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
