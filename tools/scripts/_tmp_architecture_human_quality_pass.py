from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def replace_between(path: str, start: str, end: str, replacement: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if start not in text or end not in text:
        raise RuntimeError(f"cannot locate replacement boundary in {path}")
    left, tail = text.split(start, 1)
    _, right = tail.split(end, 1)
    target.write_text(left + start + "\n\n" + replacement.strip() + "\n\n" + end + right, encoding="utf-8")


ARCHITECTURE_PART_A = r'''
### 1. Zuno 真正要保护的不是一次回答，而是一条长期可解释的法律工作链

简单法律问答的目标通常很直接：确认用户能看哪些材料，找到相关原文，再生成一个有引用的回答。如果任务到这里就结束，那么受控检索、模型调用和普通应用服务已经足够，继续引入复杂运行时、长期状态和多种恢复机制反而会增加成本。

Zuno 面对的更难问题出现在工作持续更久、参与者更多、结果会被正式采用以后。同一个事项可能同时存在多版合同、扫描件、补充材料和后续证据；模型可以提出事实和结论，但专业人员可能接受、修改或拒绝；成果已经交付后还会出现新证据；任务可能运行几十分钟，中途发生权限变化、模型失败、服务崩溃或外部系统超时。此时系统不能只回答“模型最后说了什么”，还必须回答“依据哪一版材料、什么已经正式成立、什么只是候选、谁批准了什么、失败以后应该从哪个事实恢复”。

因此 Zuno 的总体设计从一个核心判断出发：**对简单任务保持简单；只有当长期事实、专业责任、失败恢复或现实副作用真正出现时，才引入相应复杂度。** 架构的目标不是让所有请求走最长路径，而是让每类任务只承担它实际需要的责任。

### 2. 最简单的方案是什么，以及它为什么在复杂任务里开始失效

最简单的方案是一个通用 Agent Host 加法律知识库：Host 负责会话和工作流，知识库负责检索，模型负责生成，必要时再调用几个 Tool。对大量低风险、短生命周期任务，这个方案完全合理，而且 Zuno 不应该因为自己拥有更多模块就否认它的价值。

问题出在几个边界一旦同时出现，通用“消息 + Workflow 状态”不再足够。文件上传成功不能证明关键附件已经 OCR；检索命中不能证明候选内容已经成为正式证据；Workflow completed 不能证明领域事务已经提交；HTTP timeout 不能证明外部动作没有发生；用户十分钟前拥有权限也不能证明下一次模型外发仍然允许。把这些差异都压成一个 `success` 或一张共享状态表，会让恢复和审计失去可靠依据。

所以 Zuno 不是从“需要九个模块”开始设计，而是从这些无法被一个通用状态统一表达的问题，逐步推导出不同事实必须拥有不同权威边界。

### 3. 先区分四种经常被误写成同一个“成功”的事实

第一种是**计算成功**：检索、模型或专业算法产生了一个结果。第二种是**运行成功**：一次受控执行已经完成当前 Step 或 Run。第三种是**业务正式成立**：法律领域 Owner 已经接受结果并留下耐久版本。第四种是**现实动作已经发生**：外围系统确实产生了副作用。

这四种成功可以处在同一条因果链里，但不能互相冒充。一个模型返回 200 可能仍被专业语义拒绝；一个 Runtime Step completed 可能仍缺少正式提交证明；一个 POST timeout 可能对应远端已经成功；一个 WorkProduct 已经正式存在，也可能因为新证据而不再适合继续发布。

架构的第一层深度不是增加更多状态，而是承认这些事实的权威来源不同，并让恢复逻辑始终回到最强的 Owner fact。

### 4. 模型、检索和专业能力为什么都先产生候选

机器产生的信息天然有不确定性：材料可能过期，检索可能只覆盖部分范围，模型可能理解错误，专业算法可能只适用于某类案件。把“算出来了”直接写成正式业务事实，会让后续的人机复核、版本演进和责任追踪全部失去边界。

因此 Zuno 先把机器结果看成候选。检索可以产生证据候选，专业能力可以产生结论建议，模型可以产生计划或动作建议；只有相应业务 Owner 在满足证据、版本、安全和人工要求以后，才允许更强事实成立。工程术语只是对这个概念的压缩：`EvidenceCandidate != Evidence`。

同样，检索阶段的引用解释“为什么当前命中了这段材料”，正式工作成果保存的引用则解释“当时正式采用了哪一版材料和稳定位置”。两者生命周期不同，所以保持 `CitationLineage != WorkProductCitationBinding`。

### 5. 为什么按“事实谁负责”切架构，而不是按技术栈切

如果按 FastAPI、PostgreSQL、LangGraph、Milvus、Neo4j、LLM、Worker 来画系统，很容易知道组件在哪里，却很难在故障时回答“谁说了算”。同样存进 PostgreSQL 的两行数据，可能一个是正式领域版本，另一个只是运行检查点；同样由模型产生的两个结果，可能一个只是 Proposal，另一个经过人工和领域事务后已经成为正式事实。

Zuno 因此优先按照 Authority（权威）和 Ownership（事实所有权）拆责任：谁可以创建事实，谁可以让它失效，谁能证明它完成，崩溃以后应该先读谁的耐久记录。技术栈是实现选择，事实权威才是长期架构边界。

这也意味着九个逻辑责任域不等于九个进程。它们可以先共处模块化 Python 后端，只有独立扩缩容、安全隔离、部署生命周期或故障半径出现明确证据时才拆物理服务。架构不能因为“微服务看起来更专业”就提前制造网络边界。

### 6. 材料、知识派生和正式业务事实为什么必须分三层

一份正式材料首先需要稳定版本身份。随后系统可以围绕这份材料生成 OCR、切分、向量、图结构和其他检索视图。这些派生数据可以因为算法升级而重建，但历史业务结果不能跟着索引重建而改变。

更重要的是，“这一代知识已经构建完成”和“当前任务可以安全使用它”仍然不是一回事。某一代索引可能总体构建成功，但当前任务要求的关键附件缺失；也可能材料齐全，但当前权限或用途不允许读取。因此必须保持 `KnowledgeGeneration lifecycle != task-level ReadinessDecision`。

这个边界使系统可以大胆重建可派生知识，同时保护正式 DocumentVersion、Evidence 和 WorkProduct 的长期身份。它也让“知识库健康”不再被错误解释为“任何任务都已经 READY”。

### 7. 领域状态和运行状态为什么不能合成一张万能状态表

Runtime 需要知道计划执行到哪里、哪些 Step 完成、哪些分支仍在等待；Domain 则需要知道哪些法律事实和工作成果已经正式成立。这两套状态会互相引用，但它们回答的是不同问题。

最关键的故障窗口发生在领域事务已经提交，而 Runtime Checkpoint 还没来得及更新。此时如果恢复只相信 Checkpoint，系统可能再次提交同一正式结果；反过来，Checkpoint 标成 completed 也不能凭空证明领域事务真的成功。

所以正式提交必须留下独立的耐久证明。工程上把这类证明表达为 `AdmissionReceipt`。恢复时先确认 Domain 是否已经完成，再修复 Runtime projection，而不是让控制状态覆盖业务事实。

### 8. 一次任务为什么需要受控计划，但计划不能成为新的业务权威

复杂任务需要显式表示依赖、并行和等待，否则“模型接下来想做什么”会变成无法恢复的隐式状态。Zuno 原生 Runtime 因此使用受控 Plan；简单原生运行仍可以是确定性单步计划，复杂运行再使用动态 DAG。

但 Plan 只拥有控制语义。它可以决定下一步执行哪个专业能力、什么时候等待、什么时候重规划，却不能自己宣布 Evidence 正式成立，也不能批准安全动作。计划版本一旦激活保持不可变，是为了让已经派发的工作有稳定因果归属，而不是为了把 Runtime 设计成第二个 Domain。

控制权集中在 `Single Controller`，专业执行可以并行，但最终的计划激活、Step acceptance、Budget、Replan 和 cancel 由一个控制面收敛。这样 Specialist 可以扩展能力，而不会各自修改全局计划形成多写者竞态。

### 9. Retry、Replan 和 Reconcile 为什么必须是三个词

很多 Agent 系统把失败统一处理成“再试一次”。这对纯计算的暂时故障有用，却会在计划假设失效或现实结果未知时制造错误。

`Retry != Replan != Reconcile`。模型临时 503，而输入和计划仍然有效，可以 Retry；Tool schema、材料版本或任务假设已经改变，应该 Replan；外部 POST 已经发出但超时，现实世界可能成功也可能失败，必须 Reconcile。三者分别解决“同一动作再执行”“换一个动作计划”“先确认过去到底发生了什么”。

这个区分是恢复闭环的核心。如果架构只保留一个通用 retry loop，就无法同时保护计算正确性和现实副作用安全。

### 10. 权限为什么不是请求入口的一次布尔判断

长任务可能运行几十分钟，中途等待人工、切换材料、调用多个模型和 Tool。期间用户权限、事项归属、数据密级、Provider 外发政策、审批状态和凭证版本都可能变化。

所以安全判断发生在每一个新的受保护边界：再次读取材料、向模型外发、获取 Secret、执行高风险 Tool、正式准入结果。早先合法发生的动作保持历史事实，但旧的 allow 不能自动成为未来动作的永久通行证。

这也是为什么 Authorization、Approval 和 HumanDecision 必须分开：有没有权执行、某个高风险动作是否被批准、专业人员是否接受法律业务结果，是三种不同责任。

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

只有 Secret isolation、独立吞吐、故障半径、网络出口、合规边界或部署生命周期形成明确证据时，才值得把某个边界提升为独立网络服务。服务拆分是一种成本很高的优化，需要被问题证明。

跨 Owner 的一致性也不通过“把所有东西放进同一分布式事务”解决。每个 Owner 在自己的事务边界内保证事实，跨 Owner 通过版本、Receipt、幂等身份和恢复顺序收敛。

### 18. 一项复杂机制什么时候应该主动删除

如果简单 RAG 已经满足目标任务，就不需要 Native Runtime；如果 Hybrid Retrieval 已经覆盖某类 query，就不需要 GraphRAG；如果通用 Host + Zuno Legal Backend 已经能够保护正式状态和恢复，就不需要复制一套完整宿主；如果一个模块没有独立扩缩容或安全隔离证据，也不需要拆成微服务。

删除条件不是架构的附录，而是架构质量的一部分。每增加一个状态机、Provider、缓存、图存储、Agent 层或服务边界，都应该能回答它保护了什么约束、增加了什么故障面、测量不到收益时怎么退回更简单方案。

09 的 Evaluation 因此不仅用于证明“功能有效”，还应该主动做 ablation 和 kill test，帮助团队决定哪些复杂度不值得长期维护。

### 19. Current、Target、Evidence 和 Unknown 必须始终分开

本文描述的是 Target Architecture。九模块 Responsibility Taxonomy、Formal Admission、Single Controller、Knowledge / Domain 权威、Effect recovery 和安全门禁已经作为目标设计接受，但这不等于对应代码、表、Migration、Provider、HA 或生产流程已经存在。

Current 只能由代码、测试、Migration、Trace、Eval 或真实运行证据证明。Pilot Validation 也不等于 Production；没有容量、DR、安全资格和运行证据，就不能从完整设计反推出生产成熟度。

项目为什么存在以及历史上做过什么，回到 `docs/project/project.md`；当前实现证据回到 `docs/evidence/`；精确模块 Contract、状态和 crash window 回到 Part B / Part C。Unknown 应保持 Unknown，不用更漂亮的架构文字填补证据空缺。

### 20. 读完整体架构后应该留下什么

如果只记住九个模块名，这篇架构文档就失败了。更重要的是记住几个设计判断：简单任务保持简单；机器结果先是候选；正式业务事实、运行控制、知识派生和现实效果分别由对应 Owner 负责；失败恢复先找最强耐久事实；权限在新的受保护动作前重新判断；复杂机制必须能被测量，也必须能被删除。

这些原则决定了 Zuno 如何在法律专业性、Agent 灵活性和工程可恢复性之间划边界。具体对象名、字段、枚举和事务细节可以继续演进，只要它们没有破坏这些已经接受的 Authority 与因果关系。
'''


MODULE_01 = r'''
### 这个模块首先解决“外部产品看到什么”，而不是“谁离用户近谁就拥有一切”

Zuno 可以被自己的 Web 页面、法院已有系统、通用 Agent Host、批处理任务或 API 客户端调用。外部调用方真正需要的是稳定产品语义：我提交了什么任务、当前能不能执行、结果是否可发布、正式成果是否仍有效、交付有没有完成。它没有必要理解九个责任域内部的所有状态机。

最容易出现的设计错误，是因为 Application 最靠近用户，就把授权、知识、Runtime、Domain 和外部 Effect 的状态全部复制成本地 `status`。短期看调用方便，长期却会出现两个模块都声称自己知道“真正状态”。所以 01 的价值不是成为万能业务层，而是把其他 Owner 已经成立的事实组合成对外一致的产品行为。

### 最简单的入口层为什么很快会遇到边界问题

最简单实现可以是一个 Controller：收到请求，调用几个服务，最后返回 `success=true`。简单同步问答完全可以这样工作。

当任务变成长流程以后，同一个 `success` 会同时混入“请求受理”“运行结束”“正式结果提交”“结果允许发布”“外部消费者已经看到”等不同含义。网络重试还可能重复启动任务，权限变化可能让旧结果失去发布资格，外部系统离线又会让交付状态与业务有效性分离。入口层如果不承认这些差异，就会把内部复杂性藏进一组越来越不可解释的布尔字段。

### 负责组合，不负责重新发明事实

01 的核心约束是：**负责组合，不负责重新发明事实**。它可以形成产品层的调用决定和发布决定，但这些决定必须引用当前授权、知识就绪、运行结果、正式准入或 Effect 回执，而不是重新计算另一套安全或业务真相。

例如，03 判断当前 Scope 只有部分关键材料可用，01 可以据此提示用户缩小范围、等待或拒绝完整分析；它不能为了“用户体验”把 PARTIAL 改写成 READY。04 表示 Run completed 时，01 也不能顺手推断正式 WorkProduct 已经存在。

### Scope 为什么必须先于 Agent 和模型

“帮我分析这个案件”不是一个足够稳定的系统输入。系统至少要知道事项、材料范围、目标结果和可信调用主体，否则后续授权、知识就绪、检索和正式准入都无法解释自己的适用范围。

01 因此先把外部输入归一化为稳定任务上下文。Scope 不足时应该请求补充，不让模型猜“用户大概指哪些材料”。如果用户后来扩大或缩小范围，这不是一个 UI 小变化，而是新的任务条件，下游 Readiness 和 Authorization 需要按新范围重新判断。

### 外部身份声明为什么不能直接升级成权限

Host 可以传 user id、tenant、role 或 matter，但这些字段只是 assertion。可信 principal 必须来自受验证会话、可信 Host assertion 或受控目录，再由 08 判断这个主体当前能做什么。

Application Adapter 可以负责认证协议和字段映射，却不能因为某个 Header 写着 `role=admin` 就提高权限。把“谁在请求”和“他现在能做什么”分开，才能让系统在多 Host、后台 Worker 和长任务恢复时仍保持一致安全语义。

### 简单问答为什么应该保持短路径

用户问“合同第 8 条写了什么”，如果 Scope 清楚、当前授权允许、所需材料已经就绪，系统只需要检索稳定原文、受控调用模型、校验引用和当前发布资格。

这类路径没有必要为了统一技术栈先构造动态 DAG。01 可以直接组合 08 的授权、03 的知识与引用、07 的模型结果，再形成 Zuno 侧普通答案发布决定。架构拥有 Runtime，不代表每个请求都必须使用 Runtime。

### 复杂任务为什么需要显式 Invocation，而不是一个巨大 if/else

复杂任务可能需要等待知识、进入 Native Runtime、调用专业能力、等待人工或最终产生正式 WorkProduct。入口层需要把这些条件组合成稳定的调用生命周期，让重复请求、取消、查询状态和结果交付都能引用同一次逻辑调用。

工程上可以把这个产品层决定表达为 InvocationDecision，但关键概念不是名字，而是：01 只决定“这次请求应走哪条产品路径”，不能替 03 重新判断知识资格，也不能替 08 判断授权，更不能替 02 正式准入。

### 四种“完成”为什么必须明确分开

外部 API 最容易把多个层次压成一个成功值，但 Zuno 必须保持：

```text
Run completed
!=
Domain admitted
!=
Answer publishable
!=
Consumer displayed
```

Runtime 完成说明控制流程结束；Domain admitted 说明正式法律业务事实成立；Answer publishable 说明 Zuno 当前允许把普通答案发布出去；Consumer displayed 则是外部 Host 自己的 UI 或采用事实。01 可以把这些事实组合给调用方，但不能让一个层次的完成替代另一个层次。

### 普通答案和正式 WorkProduct 为什么不能共用同一条发布权威

普通问答通常不需要进入正式领域状态。只要当前授权、材料就绪、引用和 AnswerPolicy 满足要求，01 可以形成普通答案发布决定。

正式 WorkProduct 不一样。它代表长期业务成果，必须先由 02 完成 Formal Admission，并拥有匹配的领域版本和准入证明。01 负责把正式版本发布或交付，但不能把 Runtime Draft 或模型文本包装成正式成果。

### Agent Version = 产品能力 / 配置版本

产品需要知道“当前这个 Agent 产品表面提供什么能力和默认配置”，这与某一次运行内部的计划版本不是同一个概念。Agent Version 可以绑定产品能力、Prompt / policy profile、默认 Runtime 策略和支持的任务类型。

PlanVersion 则属于 04 某一次具体运行。Agent 产品升级后，新请求可以使用新 Agent Version，正在运行的旧任务仍按自己已经绑定的版本解释；不能因为产品升级就在后台把旧 Plan 原地改掉。

### 新证据出现以后，为什么“失效”和“通知成功”必须分开

假设 WorkProduct V5 已经交付给法院系统，下午新 Evidence 进入后，02 判断 V5 需要复核。这个业务失效事实应该立即成立，不应等待外部系统在线。

01 的责任是把失效事实可靠地传播给已经接收 V5 的消费者，并提供 pull validity 查询。外部通知失败只表示传播仍在重试，不会把 Domain 中的 stale 重新变成 current。这样业务有效性不会被网络可用性绑架。

### 为什么 Push 和 Pull 都有价值

Push 能降低失效传播延迟，但消费者可能离线、队列可能积压、网络可能失败。如果系统只依赖 Push，就无法保证外部在真正使用成果时知道当前有效性。

因此 Target 同时保留 Pull validity。使用正式成果前，消费者可以查询当前版本状态。Push 负责尽快通知，Pull 负责最终可检查性，两者都只是传播机制，不改变 02 的业务真相。

### Delivery 为什么需要独立身份

同一个 WorkProduct 可以交付给多个外部系统，同一个目标也可能因为网络错误重复发送。如果只拿 WorkProduct id 当幂等 key，就无法区分“给 A”和“给 B”，也无法判断一次重试是否仍然是同一个逻辑交付。

01 因此需要稳定 Delivery identity，把目标、业务对象版本和 payload / contract 版本绑定起来。它保护的是产品交付语义，不意味着所有 Delivery 都由 01 自己执行现实副作用。

### 为什么有副作用的 Delivery 要交给 06

返回一个 HTTP response 和“在远端创建一条正式记录”不是同一种交付。后者会改变现实世界，一旦 timeout 就可能出现结果未知。

01 仍然拥有产品侧 Delivery 生命周期，但具体副作用要通过 06 的 Effect Control。01 消费 06 的执行和对账事实更新交付 observation，而不是自己写一个无限 retry loop 去猜远端到底发生了什么。

### Consumer Ack 为什么只能叫 Observation

远端返回 `ack=true` 最多证明 Zuno 观察到对方接收了请求或消息。它不一定证明远端内部业务流程已经最终采用，也不代表对方 UI 已经展示。

所以 01 可以保存 acknowledgement observation 和 remote correlation，却不能把外部系统内部 adoption truth 收编成本地事实。边界清楚以后，集成协议可以演进，而 Zuno 不需要控制远端实现才能保持自身一致。

### 重复请求为什么不应该启动第二个复杂 Run

浏览器重试、移动网络抖动和 API Gateway timeout 都可能让同一个逻辑请求重复到达。入口如果每次都新建 Run，会把一个用户动作放大成多个 Agent 运行，甚至重复正式交付。

request identity、logical invocation 和下游 Run identity 应分开。相同幂等身份和相同 canonical task input 可以返回已有 invocation；相同 key 却对应不同 task hash 应明确冲突。这样客户端在“提交成功但响应丢失”后可以安全重试。

### 取消为什么只是停止还能停止的未来工作

用户点击取消时，01 可以请求 04 停止未来计划工作，也可以停止尚未发出的 Delivery。但已经提交的 Domain transaction、已经确认的现实 Effect 或已经发送的外部消息不会因为本地 flag 自动消失。

因此取消响应要表达真实边界，例如“停止请求已接受，但已有不可撤销事实仍然存在”。如果业务需要补偿，补偿应该作为新的受控动作执行，而不是回写旧历史伪装成从未发生。

### Host Adapter、Backpressure 和 Contract Version 为什么属于产品边界

不同 Host 的字段、认证和同步 / 异步协议可以由 Adapter 转换，但 Adapter 只能解决兼容，不得改变 READY / PARTIAL、Draft / Formal、Authorization / Approval 等业务含义。

当 Runtime queue、知识构建、模型配额或外围系统过载时，01 也应该把背压显式暴露为 queued、deferred、rate-limited 等产品语义，而不是无限受理后统一超时。外部 Contract 需要版本化，使旧消费者不会把新状态按旧含义解析。

### 什么时候这个模块应该更简单

如果 Zuno 只作为内部库被一个单体应用调用，没有多 Host、异步交付、失效传播或复杂任务受理，那么 01 完全可以保持成很薄的 application layer。稳定产品语义不要求独立微服务，也不要求大型 Integration Platform。

只有外部协议、交付可靠性、Host 生命周期或吞吐隔离出现明确需求时，才值得增加 Adapter、Outbox、Queue 或独立部署。复杂度由集成问题驱动，不由“Application 模块应该很完整”驱动。

### 当前、目标与缺口

Current 只能回到 `docs/evidence/` 判断；这篇文档完整描述产品边界并不代表 Request ledger、Delivery store、Outbox、Host adapter 或 AgentVersion registry 已经实现。

Target 是让 01 稳定承担请求归一化、产品路径组合、普通答案发布、正式成果交付和失效传播，同时坚持消费其他 Owner facts 而不重新发明它们。Gap 仍包括字段级 Contract、实现、真实 Host 行为、吞吐与交付可靠性测量，以及哪些场景真正需要独立部署。
'''


MODULE_02 = r'''
### 这个模块回答的是“什么才算正式法律业务事实”

模型可以生成事实摘要、争议点和法律结论，检索可以找到相关材料，Runtime 可以把一条复杂流程跑完，但这些成功都不能自动说明法律业务已经正式接受了某个结果。正式结果需要长期存在、可追溯、可版本化，也需要在人机协作和新证据进入以后仍然解释得清楚。

02 的职责因此不是“保存模型输出”，而是拥有正式领域状态：哪些材料版本属于当前事项，哪些候选被接纳为证据，哪些结论经过了怎样的人工判断，最终工作成果引用了什么，以及新事实出现以后哪些历史成果需要复核。

### 最简单的“把最终答案存进数据库”为什么不够

最简单方案是把最终模型文本写进一张 result 表。对一次性 Demo 这可能完全够用，因为系统只需要展示最后输出。

长期业务一旦出现，单条文本无法回答：这个结论依赖哪份材料的哪个版本；模型建议是否被人工修改；后来新增证据后旧结果是否仍有效；系统崩溃时这次正式提交到底成功没有。为了恢复方便继续给 result 表加几十个状态字段，最终只会得到一张无法说明权威边界的万能表。

### 候选和正式事实必须有一道清楚的门

检索和模型先产生候选，是因为机器结果可能错、材料可能不完整、权限和专业判断也可能变化。正式 Evidence 必须由 Domain Owner 在满足业务约束后接纳，而不能因为 Retriever 命中就直接写入长期事实。

这个差异用工程术语可以写成：

```text
EvidenceCandidate（证据候选）
    ≠
Evidence（正式证据）
```

术语不是重点，重点是正式业务世界只接受经过明确准入的事实，机器计算成功本身没有这种权威。

### 为什么需要一组很小但稳定的领域对象

法律工作长期需要追踪的不是所有中间 DTO，而是少量具有业务身份的对象：事项、材料版本、主张、正式证据、正式结论、人工业务决定和工作成果。它们构成 Target 的七对象 Legal Domain Kernel。

七对象不是为了“领域建模漂亮”，而是为了让长期事实有稳定身份和版本。OCR chunk、embedding、模型 response、Runtime Step 都可以大量变化，却不应该取代这些正式业务对象的身份。

### Formal Admission 为什么必须留下耐久证明

当 Runtime 或 Capability 产生一个需要进入正式领域的结果时，Domain 不能只返回 `200 OK` 然后期待调用方记住成功。最危险的窗口是 Domain transaction 已经提交，而调用方在更新 Checkpoint 前崩溃。

所以正式提交必须同时得到可重放查询的因果证明。系统恢复时，以 `DomainVersion + matching AdmissionReceipt` 判断这次正式提交是否真的发生，再修复 Runtime。Receipt 不是日志装饰，而是跨故障窗口判断完成的耐久锚点。

### 为什么 DomainVersion 不能被 Runtime 的 completed 覆盖

Runtime 的任务是控制执行，Domain 的任务是维护业务事实。一个 Step 可以完成纯计算却不需要正式提交；另一个 Step 可能业务事务已提交但 Runtime 还没更新。

如果双方共享一个 `completed`，崩溃后就无法判断哪种完成更强。DomainVersion 记录正式业务世界的演进，Runtime Checkpoint 记录控制进度。它们通过 causation refs 关联，但谁也不能冒充对方。

### WorkProduct 为什么不能只保存最终文本

正式工作成果要能在未来解释“当时为什么这样写”。因此除了版本化正文，还需要保存它真正采用的 Evidence、Finding、HumanDecision 和材料位置。

这里的引用不是“当前重新检索可能找到什么”，而是历史成果在提交时真实绑定了什么。工程上把这种稳定历史依据表达为 `WorkProductCitationBinding`，它的生命周期跟工作成果走，而不是跟当前检索索引走。

### 检索引用为什么不能直接成为正式成果引用

Retriever 的 CitationLineage 解释当前候选从哪里来，索引重建、切分策略或 reranker 升级都可能改变它。正式工作成果却必须在几年后仍能回到当时采用的不可变材料版本和稳定位置。

因此 CitationLineage 可以帮助 Formal Admission 构造正式引用，但不能直接被当成长期业务 binding。正式化过程必须校验材料版本、位置和当前业务 Scope，再由 02 保存历史身份。

### 人工业务决定和安全审批为什么必须分开

专业人员可能接受、修改或拒绝一个 Finding，这属于法律业务判断；安全治理可能要求另一位有权限的人批准一次高风险外部动作，这属于安全审批。二者即使都发生在“人点按钮”的 UI 上，语义仍然不同。

所以必须保持 `HumanDecision（人工业务决定）和 ApprovalDecision（安全审批决定）` 的 Owner 分离。一个专家认可结论，不代表允许把它发送到外围系统；一个管理员批准发送，也不代表模型结论已经成为正式法律事实。

### 新证据出现以后为什么要保留历史而不是覆盖旧结果

假设 WorkProduct V3 基于当时全部正式 Evidence 生成，后来新增一份关键补充协议。V3 作为历史成果仍然真实存在，但当前继续使用它可能已经不合适。

02 因此需要记录依赖关系，并在新事实影响旧结论时形成 invalidation / stale 事实。系统不是把 V3 删除，也不是偷偷把 V3 内容改成新版本，而是明确“当时的版本存在；现在需要复核”。这同时保护审计和当前有效性。

### 为什么失效传播应该有界而不是一律全案重跑

一个事项新增材料不一定影响全部 Finding。只要正式对象保存了足够依赖关系，就可以沿 Evidence → Finding → WorkProduct 的因果边界判断哪些结果可能受到影响。

这使系统可以把重评限制在真实依赖范围内。过度精细的依赖图也会增加维护成本，所以 Target 只要求能够解释重要正式关系，不为了理论完美把所有模型 token 和中间变量都升级成领域对象。

### 并发正式提交为什么不能靠“最后写入者获胜”

多人协作、后台 Agent 和异步恢复可能同时尝试更新同一个 Matter。如果两个提交都基于旧 DomainVersion，却无条件覆盖对方，就会丢失人工判断或正式证据。

因此正式准入需要 expected version / CAS 一类并发条件，冲突时重新读取当前 Domain facts 再判断。这里保护的是业务版本因果，不是为了追求分布式锁本身。

### 幂等为什么必须绑定 canonical 业务输入

客户端或 Runtime 崩溃重试时，同一次 Formal Admission 应能安全识别；但只比较一个字符串 key 不够，因为同 key 如果携带不同 canonical input，继续返回旧结果会隐藏业务冲突。

所以 Admission 的幂等身份必须和规范化业务输入、预期版本和重要 causation 绑定。相同逻辑提交可以返回既有 Receipt，不同业务内容复用同 key 应显式失败。

### 崩溃恢复为什么先读 Domain 而不是先重放 Agent

最重要的恢复原则是：先确认更强的业务事实是否已经存在，再决定控制流程要不要继续。Domain commit 成功而 Checkpoint 失败时，重放 Agent 可能重复正式提交；Checkpoint completed 而 Domain Receipt 不存在时，也不能因为控制状态漂亮就宣布业务完成。

因此恢复查询以 DomainVersion 和 matching Receipt 为锚点，Runtime 再修自己的 projection。这个顺序让 Domain 成为正式业务权威，而不是让 Checkpointer 在故障时意外升级成业务数据库。

### 02 不应该拥有什么

02 不负责 OCR、embedding、索引 serving，也不负责决定下一步 Agent Plan，更不负责模型路由和外部 Tool Effect。把这些职责收进 Domain 会让正式状态和可重建技术状态混在一起。

Domain 可以引用 Knowledge、Runtime、Capability、Security 和 Effect 产生的事实，但只在需要形成正式法律结果时接管。保持入口窄，才能让正式状态长期稳定而外围技术自由演进。

### 什么时候领域模型应该更简单

如果产品只是一次性问答，没有正式工作成果、人工业务决定、版本历史和长期失效语义，那么完整七对象 Kernel 可能没有必要。一个更轻的 answer record 完全可能足够。

只有当系统需要把结果作为长期业务事实保存、复核、追责和继续演进时，Domain Kernel 才值得存在。即使存在，也不应为了“DDD 完整”增加没有稳定业务身份的对象。

### 当前、目标与缺口

Current 只能由现有代码、Migration、Test 和运行证据证明。完整 Target 文档不表示七对象表结构、Admission transaction、依赖传播或并发控制已经全部实现。

Target 已明确正式事实由 02 拥有，机器候选与正式事实分离，Formal Admission 以版本和 Receipt 形成恢复锚点，WorkProduct 保存稳定历史引用。Gap 仍包括字段级冻结、真实并发与崩溃测试、Migration 设计、失效传播测量，以及这些机制在真实法院工作流中的实际成本和收益。
'''


MODULE_03 = r'''
### 这个模块先解决一个反直觉问题：文件到了，不代表任务已经能用

用户上传一百份材料，接口全部返回成功，并不能说明“请基于全部材料分析争议”这个任务已经准备好。两份关键扫描附件可能还没 OCR，某一版材料可能刚被替换，索引可能只完成部分写入，当前用户也可能没有权限读取其中一部分。

03 因此不是一个“向量数据库封装层”。它负责把正式材料版本变成可重建知识派生，并针对具体任务判断当前范围到底可不可用；检索只在这个基础上产生有来源的候选，而不是把命中结果直接升级为法律事实。

### 最简单的一份文件一个向量索引为什么会失效

最简单方案是文件上传后立即切分、embedding、写向量库，然后用“索引里有数据”表示准备完成。对单文件 Demo 这通常可行。

真实材料处理中，OCR、解析、chunk、embedding、图构建和元数据写入可能分别成功或失败；算法升级还会要求重建索引。如果把向量库当前内容当成正式材料身份，重建时历史引用会漂移；如果把任意子步骤成功当成 READY，系统会在关键材料缺失时输出看似完整的答案。

### 正式材料、知识派生和任务就绪为什么是三层

DocumentVersion 是 02 拥有的正式业务材料身份。03 围绕它建立 KnowledgeGeneration：某一组解析、OCR、切分、embedding、图和其他派生视图的可重建版本。具体任务再结合 Scope、所需能力和当前安全条件形成 ReadinessDecision。

三层分开以后，材料历史不会随着索引重建而漂移，派生算法可以升级，任务也不会因为“总体构建完成”就自动获得完整使用资格。

### KnowledgeGeneration lifecycle != task-level ReadinessDecision

KnowledgeGeneration 的生命周期回答“这一代派生知识构建到什么程度、是否经过验证、是否可以 serving”；ReadinessDecision 回答“针对这一次任务要求，现在是否有足够且被允许的知识可用”。

一个 generation 可以 serving，但某个任务需要的关键附件不在覆盖范围，因此仍然 BLOCKED；反过来，一个简单单文档问题可能只需要 generation 中已准备好的那一小部分。把两者合并，会让系统不是过度等待，就是在覆盖不足时误报 READY。

### 为什么部分完成必须显式，而不能假装成功

知识构建天然是多阶段异步流程。九十八份材料完成、两份关键附件失败时，系统最危险的行为不是报错，而是静默把九十八份当成“全量知识”。

Readiness 应该显式表达 READY、PARTIAL、BLOCKED 一类业务含义，并解释缺什么、覆盖什么。上层可以据此等待、缩小 Scope 或向用户说明限制，但不能把 PARTIAL 通过 Prompt 包装成完整分析。

### 检索命中为什么仍然只是候选

检索系统的任务是提高找到相关材料的概率，而不是拥有正式法律事实。它可以返回片段、来源、分数、关系和证据候选，但最终是否被法律业务采用由 02 决定。

因此保持 `EvidenceCandidate != formal Evidence`。这个边界允许 03 自由升级 embedding、reranker、GraphRAG 或 query rewrite，而不会让算法变更直接修改长期领域事实。

### CitationLineage 为什么只解释“怎么找到的”

检索结果需要知道来自哪一版材料、哪个位置、哪条检索路线和处理版本，才能调试“为什么找到这一段”。这些信息构成当前检索 lineage。

正式 WorkProduct 的历史引用则需要在未来稳定回到当时采用的材料版本和位置。索引可以重建，正式引用不能漂移，所以必须保持 `CitationLineage != WorkProductCitationBinding`。03 提供候选来源，02 在正式准入时保存长期 binding。

### 为什么一条 Retrieval Pipeline 不应该处理所有问题

精确条款定位、语义相似问题、实体关系问题和跨文档多跳分析的最佳检索方式不同。如果所有 query 都强制走最复杂 GraphRAG，简单问题会付出不必要延迟和故障面；如果所有 query 都只做向量 Top-K，复杂关系又可能覆盖不足。

Target 因此采用按 QueryClass 选择路线的思路：lexical / BM25、dense、metadata/source scoped、entity/fact、graph/multi-hop 可以按需要组合，再做融合和 rerank。重点是根据任务选择最小充分路线，而不是把“路由越多”当成先进性。

### 多路检索以后为什么还需要停止条件

Agentic Retrieval 很容易陷入“再搜一次也许更好”。如果没有停止条件，一次问题会不断 query rewrite、graph traversal、rerank 和模型判断，成本上升却没有可解释收益。

所以复杂检索需要观察新增证据是否真的增加覆盖，当前证据是否已经足以支持任务，以及继续检索还能解决什么缺口。EvidenceGain / Sufficiency 是对这种概念的工程化表达，核心是让“继续找”有因果理由。

### GraphRAG 为什么只能是条件能力

图结构对跨文档实体关系、事件链和多跳问题可能有价值，但图构建本身带来抽取误差、存储成本、新鲜度问题和额外查询延迟。不是所有法律问题都需要图。

因此 GraphRAG 必须和更简单 Hybrid Retrieval 做同语料、同模型、可比预算的对照。只有特定 query class 稳定获益时才扩大使用；否则保持按需路线，甚至删除图路径。

### 新材料进入时为什么不能原地修改 serving 索引

如果正在 serving 的 generation 被后台 Worker 一边查询一边原地改写，读者很难知道某次检索到底使用了哪个完整版本。部分写入失败还可能把不完整新数据暴露给在线任务。

更稳妥的概念是构建新的 generation，验证 Manifest 和覆盖以后再原子切换 ServingPointer。旧 generation 可以在策略允许的时间内保留用于历史解释或回滚，可重建数据最终再按生命周期清理。

### Worker 重试为什么不能让部分写入变成“已激活”

OCR 或 embedding Worker 失败可以按处理项重试，但某个子任务成功不代表整代知识可 serving。Activation 必须依赖 generation-level validation，而不是最后一个 Worker 的“成功回调”。

这样 Worker 可以横向扩展和至少一次执行，重复处理由 item identity / CAS 等机制吸收；无论重试多少次，都不能跳过完整性判断直接修改 serving truth。

### Cache 为什么只能优化派生数据

检索 cache、embedding cache 和解析 cache 都能显著降低成本，但 Cache 失效不应该改变正式材料和业务成果。cache key 需要绑定真正影响结果的材料版本、处理版本、查询配置和必要安全 Scope。

缓存命中仍然要通过当前授权和任务新鲜度判断。它加速的是 Projection / Derived Knowledge，不是产生永久授权或正式 Evidence。

### 权限变化为什么会让“之前算好的知识”暂时不可用

材料派生数据可能在技术上仍然存在，但用户权限或模型外发政策变化后，新的读取和检索不能因为 cache / generation 已经构建就继续复用旧 allow。

03 消费当前 Security decision 决定哪些内容可以返回。安全变化通常不要求立刻物理重建所有索引，但必须影响新的受保护访问和 Readiness；历史合法处理事实与未来是否允许继续使用要分开。

### Knowledge stale 和 Domain stale 为什么属于不同 Owner

材料或处理版本变化后，旧索引可能需要重建，这是 Knowledge 层的新鲜度问题；新的正式 Evidence 进入后，旧 Finding / WorkProduct 是否需要复核，则是 Domain 问题。

所以保持：`stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02`。03 可以通知上层旧 generation 不再适合新任务，却不能直接把正式 WorkProduct 改成 stale；02 根据正式依赖关系决定业务失效。

### 什么时候 03 应该更简单

如果语料小、全部是干净文本、没有多版本、没有 OCR 和复杂 Scope，一个版本化的 lexical / dense index 可能已经足够。此时不需要 Graph Store、多路 Planner 或复杂 generation orchestrator。

Knowledge 架构的复杂度应由材料规模、处理异步性、版本重建和 query 类型驱动。能够删掉 GraphRAG、减少 Route、合并 Worker 或不用独立 serving service，都是正常架构优化。

### 当前、目标与缺口

Current 是否已有完整 generation、serving pointer、readiness、multi-route retrieval 或 graph path，必须回到代码、测试和 Eval 证据判断；Target 文档不能把设计写成已实现。

Target 已明确正式 DocumentVersion、可重建 KnowledgeGeneration、任务级 Readiness 和检索候选的边界，并要求复杂检索有 simpler baseline 和停止条件。Gap 仍包括字段冻结、真实材料覆盖测量、部分失败与切换测试、Graph / multi-route 的边际收益、容量成本和安全隔离实现。
'''


MODULE_04 = r'''
### 这个模块解决的是“长任务怎样继续”，不是“让很多 Agent 自己商量”

复杂法律任务可能包含材料检查、检索、专业分析、并行比较、人工等待、外部 Tool 和正式提交。真正困难的不是把这些步骤串起来一次跑通，而是在材料变化、权限变化、部分失败、进程重启和晚到结果同时存在时，仍然知道下一步应该做什么。

04 因此拥有运行控制，而不是所有业务事实。它负责一次 Run 的计划、Step、并行、等待、预算、取消、重规划和 Checkpoint；Domain、Knowledge、Security 和 Effect 仍由各自 Owner 决定更强事实。

### 最简单的 while-loop Agent 为什么难以恢复

最简单 Agent 可以不断把当前上下文交给模型，让模型决定下一步 Tool，直到输出 final answer。短任务和低风险实验完全可以这样实现。

长任务中，这种隐式控制状态很难回答：模型崩溃前已经决定了什么；两个并行 Specialist 的结果属于哪个计划版本；新证据进入后旧任务还能不能接受；外部动作 timeout 后该不该再次执行。把所有历史都塞进 message list，也无法自然得到稳定的并发和恢复语义。

### Single Controller 为什么是控制权约束，不是“只有一个模型”

Zuno Target 采用 `Single Controller`：只有一个控制面有权激活计划版本、接受 Step 结果、决定 Retry / Replan、管理 Budget 和发出 cancel。专业执行单元仍然可以并行，甚至可以由不同模型或 Capability 实现。

这样做不是否定 Multi-Agent，而是避免多个自治 Agent 同时修改全局计划。执行可以多写，控制必须单写，才能让计划演进和恢复拥有唯一因果顺序。

### 为什么需要三层 Graph，而不是把所有动态性塞进 LangGraph 拓扑

长期运行既需要一个稳定宿主生命周期，也需要任务级动态计划，还需要单个 Step 内稳定执行边界。Target 因此保持 `Fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph`。

外层 RunGraph 管启动、恢复、终止等稳定阶段；Plan DAG 表达某个任务当前真正的动态依赖；StepExecutionGraph 管一个 Step 内部的执行、验收和必要的模型 / Capability 调用。这样动态计划不会要求每次 Replan 都重建宿主拓扑。

### 为什么 PlanVersion 激活后不能原地修改

计划一旦开始派发，就已经有 Worker、模型和外部调用绑定到它。如果在原对象上修改 Step、参数或依赖，晚到结果会失去“我当时基于什么计划计算”的身份。

因此保持 `PlanVersion immutable after activation`。需要改变计划时创建新版本，并明确哪些旧工作可以继续、哪些结果必须重新验收。不可变版本保护的是因果，不是为了增加版本号。

### Ready Step 为什么不能只看“前驱 completed”

一个 Step 是否能执行，不只取决于拓扑前驱结束。它还可能需要当前材料版本仍有效、Capability / Model 当前有资格、预算充足、权限仍允许，以及输入没有因为 Replan 变旧。

所以 Ready 判断本质上是多个 Owner facts 的组合。04 可以消费这些事实形成控制决定，却不能缓存一次 READY 后永久复用。

### 并行和 Join 为什么最容易暴露控制语义问题

并行 Specialist 可以提高吞吐或覆盖，但不同分支可能失败、取消、晚到，甚至属于已经被替换的旧 Plan。Join 不能只数“收到几个结果”，还要确认每个结果是否属于当前 barrier、是否通过 Step acceptance、是否满足最小证据和质量要求。

因此并行是控制优化，不是业务真相。一个分支计算成功，如果输入版本或 Plan 已过期，仍然可能被拒绝或重新评估。

### Step 执行成功为什么不等于业务完成

Runtime 可以验证 schema、Capability acceptance、模型结果和控制条件，但 Formal Admission-required Step 只有拿到 Domain 的匹配 Receipt 才能被视为正式业务提交完成。

这个边界避免 Checkpoint 抢走 Domain 权威。04 保存“我已经观察到并接受哪个 Owner fact”，而不是自己创造更强成功。

### Retry != Replan != Reconcile

Retry 适用于同一动作假设仍然成立，只是遇到暂时故障，例如模型 503。Replan 适用于计划假设已经失效，例如新材料改变依赖、Tool schema 更新或某条路线长期不可用。

Reconcile 解决的是过去现实动作结果未知，例如 POST 已经发出但 timeout。04 可以暂停等待 06 对账，却不能用 Replan 或 Retry 把未知现实效果覆盖掉。三种机制分开，控制面才能对失败做正确分类。

### Replan Barrier 为什么需要一个清楚的切换点

新 PlanVersion 产生以后，旧计划可能还有并行任务在运行。如果 Controller 一边接受旧结果一边按新计划派发，而没有稳定 barrier，就会产生“半个旧计划 + 半个新计划”的混合状态。

`Replan Barrier` 表达一个控制切换边界：哪些旧工作允许完成、哪些应取消、哪些 late result 需要重新验收，以及新计划从哪个因果点开始。它保护计划版本之间的可解释性，而不是要求停止所有在途工作。

### Late Result 为什么既不能一律丢，也不能一律收

旧 Plan 的纯计算结果如果输入版本仍然相同，也许仍有价值；如果材料、权限或业务预期已经变化，直接接受就会污染新计划。现实 Effect 更不能因为 branch stale 就被否认，因为远端动作可能已经发生。

所以 late result 需要按结果类型重新验收：纯计算检查 causation / freshness；正式 Domain 结果查询 Owner Receipt；现实 Effect 继续由 06 确认。是否“晚”只是时间事实，不自动决定业务资格。

### Checkpoint 为什么是恢复工具而不是业务数据库

Checkpoint 保存控制面为了恢复需要的 Run / Plan / Step 状态，使进程重启后不必从头重算。但它可以比 Domain、Effect 或 Security 的权威事实更旧。

恢复时先读取相应 Owner durable fact，再修复 Checkpoint projection。尤其 Domain commit 已成功但 Checkpoint 失败时，不能因为控制状态落后就重复正式提交。

### Interrupt / Resume 为什么必须带新鲜度检查

人工等待可能持续数小时甚至数天。恢复时，原 Plan、材料、Capability 版本、SecurityEpoch 和 Approval 都可能变化。

因此 resume 不是“从暂停行下一行继续”。Controller 要重新判断仍然适用的条件；无效 Approval 重新申请，过期输入触发 Replan，需要正式提交的结果重新检查 expected DomainVersion。

### Lease 和 Fencing 为什么只解决 Controller 所有权，不解决业务正确性

如果进程崩溃，另一个 Worker 可能接管 Run。Lease / fencing 可以防止两个 Controller 同时写控制状态，但它不能证明某个 Tool Effect 没有发生，也不能替 Domain 判定正式事务。

这类机制应当保持窄：只保护 Runtime 控制面的单写者语义。跨 Owner 的业务完成仍依赖 Receipt、版本和对应恢复规则。

### Budget 和取消为什么也是控制事实

模型、检索和 Tool 重试都会消耗时间与资源。Budget 让 Controller 能决定继续、降级、Replan 或 abstain，而不是让每个 Provider 自己无限 fallback。

取消同样只停止未来还能安全停止的工作。已经提交的 Domain、已确认的 Effect 和已发生的模型 Usage 仍然是真实历史，Controller 不能通过把 Run 标成 CANCELLED 来改写它们。

### 为什么 Runtime 应优先复用框架而不是自研宿主能力

LangGraph 等框架已经提供图执行、checkpoint、interrupt 等通用原语，Zuno 应优先复用。自定义层只应该承担通用框架不会替法律项目拥有的 PlanVersion、formal admission acceptance、Effect reconciliation 和安全新鲜度等专业语义。

如果 Generic Host + Zuno Legal Backend 已经能满足长期状态和恢复要求，Native Runtime 应缩小甚至退出主路径。自研 Runtime 的价值必须由复杂任务恢复、可控性或成本收益证明。

### 当前、目标与缺口

Current 是否已有完整 PlanVersion、parallel join、Replan Barrier、interrupt freshness、lease/fencing 和 crash recovery，需要回到代码与测试证据判断；文档中的 Target 不能当成实现清单。

Target 已明确 Single Controller、三层 Graph、不可变计划版本、Retry/Replan/Reconcile 分离和 Owner-fact-first recovery。Gap 仍包括字段级冻结、并行/晚到 fault injection、真实 Checkpointer 语义、Budget / takeover 测试，以及 Native Runtime 相对更简单 Host 方案是否有稳定收益。
'''


MODULE_05 = r'''
### 这个模块解决的是“专业能力怎样成为产品契约”，不是“把所有算法包装成 Tool”

Zuno 会使用事件抽取、事件对齐、争议识别、证据分析、类案检索、法条推荐和其他法律算法。这些能力可能来自课题组研究、规则代码、传统模型、新 LLM 或外部服务。直接让 Runtime 依赖某个脚本或 Provider，短期最省事，长期却会把业务语义和实现版本绑死。

05 的职责是把“能完成什么专业任务”稳定下来，再允许不同 Provider 去实现。Runtime 调用的是专业能力语义，Eval 判断当前实现是否合格，Domain 决定输出能否成为正式事实。

### 最简单的 provider.call() 为什么会慢慢失去边界

一个研究模型刚接入时，最简单方案是写一个 Python wrapper：传入文本，返回 JSON。只要 Demo 跑通，看起来已经是 Skill。

随着模型升级、输入材料类型变化、多个 Provider 共存，问题就出现了：不同实现对“事件”定义是否一致；失败返回空数组是“没有事件”还是“模型故障”；新版字段是否兼容旧调用方；某个 Provider 技术可调用是否意味着质量足够。没有稳定能力语义，Runtime 只能不断理解每个实现的特殊情况。

### Capability = 稳定专业语义

Capability 的核心不是类名，而是一份专业承诺：输入是什么业务含义，输出表达什么，哪些情况算成功、拒绝、不可判定或需要 Review，以及结果可以被哪些后续流程消费。

实现可以变化，但同一 CapabilityVersion 下的语义必须稳定。真正改变专业含义时创建新版本，而不是在旧接口后面偷偷改变“同一个字段是什么意思”。

### Provider 为什么必须和 Capability 分开

一个 Capability 可以由课题组旧模型、现代 LLM、规则系统或外部服务实现。把 Provider identity 从能力语义中分离，Runtime 才能根据当前资格选择实现，而不把业务代码绑定到某个框架或模型家族。

Provider 变化可以是部署、性能或模型升级；Capability 版本变化则表示专业契约变化。两类版本分开以后，回放和 Eval 才能解释质量变化来自哪里。

### Provider Conformance != task quality

Conformance 回答“这个 Provider 是否遵守 Capability 契约”：字段、错误语义、版本、必要来源和行为边界是否一致。它是接入门槛，不是专业质量证明。

所以必须保持 `Provider Conformance != task quality`。一个 Provider 可以完全符合 schema，却在复杂案件上准确率很差；反过来，一个研究脚本可能某项 benchmark 很强，却没有稳定错误语义，不适合直接进入生产调用路径。

### provider execution failure 和 capability semantic drift 为什么是两类故障

Provider 超时、依赖 503、GPU 不可用，属于实现执行失败；如果同一个版本突然改变事件边界、字段含义或输出约束，则属于能力语义漂移，不能通过普通 Retry 掩盖。

```text
provider execution failure
!=
capability semantic drift
```

前者可以 fallback 或 retry，后者应该阻断资格、触发版本升级或重新验证。把两类失败都叫“调用失败”，会让系统在语义已经不可信时继续切换重试。

### Eligibility 为什么不是“服务健康”

Provider 健康只说明技术上能调用。某次任务能否使用，还取决于 CapabilityVersion、Conformance、质量基线、数据限制、当前材料类型和任务风险。

Eligibility 是这些条件的任务级组合。它防止“API 是绿的”被误解成“这个实现适合当前法律任务”。Runtime 可以消费资格，却不应该自己重新实现专业评测逻辑。

### Invocation 为什么需要绑定版本和输入身份

专业输出需要能解释“由哪个 CapabilityVersion、哪个 ProviderVersion、基于哪些材料和参数产生”。否则模型升级后出现质量变化，系统无法重放或归因。

Invocation identity 还帮助处理重复执行和 cache。它不应该和 Runtime Step id 合并，因为同一个 Step 可能多次尝试不同 Provider，而同一 Capability 也可能被不同 Run 调用。

### Fallback 为什么必须保护专业语义

Provider A 不可用时切到 B 看起来只是可用性优化，但 B 必须满足同一 Capability 的最低语义和质量要求。否则“fallback 成功”可能只是换成了一个会返回 JSON、却不适合当前任务的实现。

因此 fallback 候选来自当前资格集合，而不是所有技术兼容 Provider。没有合格实现时，正确结果可能是让 Runtime Replan、进入 Review 或明确 abstain，而不是无限降低标准。

### Cache 为什么不能把专业输出变成永久事实

某些确定性或高重复能力可以缓存，但 cache identity 需要绑定输入版本、Capability / Provider 版本、配置和必要安全 Scope。材料或专业语义变化后，旧结果不能静默复用。

更重要的是，缓存命中只表示“可以复用一次专业计算结果”，仍然不等于 Domain 正式接受。Formal Admission 的业务资格继续由 02 判断。

### Capability、Model 和 Tool 为什么不能混成一个抽象

LLM 是一种计算 Provider，Tool 可能产生现实副作用，Capability 则是专业业务语义。三者有交集，但失败和权威不同。

一个专业能力可以内部调用模型，也可以产生一个 Action Proposal；模型调用事实由 07 记录，现实执行由 06 控制，05 只保证专业输出满足自己的契约。把三者统一成万能 Tool，会让预算、安全、Effect 和专业质量边界互相污染。

### 研究成果怎样进入 Capability，而不是直接进入架构

研究论文或课题组算法首先证明某个局部问题可能可解，不自动证明它已经是稳定产品能力。进入 Zuno 前，需要明确语义、版本、来源、Provider 接口、Conformance 和 Eval。

这样事件抽取、事件对齐、冲突识别等研究资产可以保留学术价值，又不会因为“是我们自己的模型”就跳过产品化门槛。新的 LLM Provider 也可以在同一专业语义下与旧模型公平比较。

### 为什么强模型不能成为所有 Capability 的默认答案

LLM 可以快速覆盖很多专业任务，但成本、延迟、可复现性和结构化稳定性并不总优于专门模型、规则或检索算法。能力层应该允许不同实现按任务价值竞争。

复杂开放判断可能值得更强推理模型，稳定抽取可能更适合小模型或规则。选择依据应该是 Eval 和业务约束，而不是“最新模型能力更强”的抽象印象。

### Provider 退出为什么必须是正常路径

如果某个外部服务停服、研究模型不再维护或质量下降，系统应该能撤销它的 Eligibility，而不要求重写 Runtime 和 Domain。Provider exit 是可替换架构真正成立的测试。

同样，加入新 Provider 也不应该自动获得资格。先证明 Conformance，再证明相应任务质量，最后进入可用集合。

### 什么时候 05 应该更简单

如果系统只有少量稳定内部函数，没有多个实现、版本演进和独立质量门槛，那么 Capability 层可以非常薄，甚至只是清晰的 Python Protocol 和测试集合。

只有研究资产多、Provider 经常变化、需要独立评测和跨 Runtime 复用时，才值得增加 registry、eligibility 和更完整生命周期。能力管理不能为了“平台化”而自我膨胀。

### 当前、目标与缺口

Current 已有哪些 Capability、Provider、Conformance test 和真实 Eval，必须回到代码和证据；Target 中列出的研究能力 family 不等于它们全部已经产品化或达到质量门槛。

Target 已明确专业语义与 Provider 解耦、Conformance 与质量分开、fallback 受资格约束，以及 Capability 输出仍是 Proposal。Gap 包括字段级版本策略、真实 Provider 兼容、任务级 Eval、cache/fallback 故障测试和哪些研究资产真正值得长期维护。
'''


MODULE_06 = r'''
### 这个模块从一个最危险的问题开始：HTTP 超时以后，现实世界到底发生了什么

调用一个纯函数 timeout，通常重新计算就行；调用外围法院系统创建记录、提交材料或触发流程时，timeout 只说明本地没有拿到确定响应。远端可能没执行，也可能已经执行成功，只是响应丢了。

06 的存在，就是为了不把“网络调用状态”伪装成“现实效果状态”。它负责把一个准备执行的现实动作稳定下来，记录实际尝试，在结果未知时对账，并为上层提供能够证明当前 Effect truth 的耐久事实。

### 最简单的 try/except + Retry 为什么会制造重复副作用

常见实现是 `try POST; except timeout: retry`。如果第一次请求其实已经在远端成功，第二次就可能重复创建、重复提交或重复通知。

对只读、天然幂等操作这不是大问题；对高风险副作用，这是架构错误。系统必须先知道“这是不是同一个逻辑动作”“远端是否支持幂等”“第一次发送后是否可能已经生效”，再决定能不能重新执行。

### Transport Success 不等于 Effect Success

HTTP 200 只证明传输层观察到了一个成功响应，不必然证明远端业务效果已经满足 Zuno 期待；HTTP timeout 也不证明业务失败。

因此必须保持 `Transport Success 不等于 Effect Success`。06 记录尝试和远端证据，再把能够确认的现实效果表达成更强 Receipt，而不是让 status code 直接成为业务真相。

### 为什么先“准备动作”，再真的发送

模型或 Capability 产生的 Action Proposal 还可能缺少稳定参数、当前授权、审批、幂等身份和审计要求。直接把模型输出传进 SDK，会让“模型建议”和“系统决定执行”没有清楚边界。

Target 使用 Propose–Verify–Execute–Observe：先把动作规范化，校验目标、关键参数、ToolVersion、EffectClass、当前安全和恢复能力；通过后才形成稳定的 `PreparedAction`，随后进入真实 send boundary。

### PreparedAction 保护的是什么

PreparedAction 不是为了增加 DTO，而是冻结“系统这次究竟准备让现实世界发生什么”。如果 Replan 后参数或目标变化，就应该形成新的逻辑动作，而不是继续沿用旧审批和旧幂等身份。

稳定 action identity 使系统能把多次网络 Attempt 识别为同一个现实意图，也让审批、审计和后续 Reconcile 都能绑定同一件事。

### 幂等为什么既看 key，也看动作内容

只保存 idempotency key 会有一个危险漏洞：调用方误用同一个 key，却传入不同目标或参数，系统如果直接返回第一次结果，就会把业务冲突隐藏成成功。

因此 `same key + different action hash 必须拒绝`。同一个逻辑动作可以安全重放查询或返回既有结果，不同动作复用同一身份必须显式冲突。

### Send Boundary 为什么是恢复设计的关键切点

真正把请求交给远端之前，系统还能确定“现实动作尚未发生”；一旦越过 send boundary，进程崩溃或网络断开就可能失去确定结果。

因此发送前需要先耐久保存足够的 PreparedAction / Attempt identity 和必要安全证明。这样即使进程在发送后立即崩溃，恢复也知道应该对账哪个现实动作，而不是只能猜要不要重试。

### Outcome Unknown（结果未知）不得映射为普通 Failed

发送以后 timeout、连接断开或 Worker crash，都可能让本地无法判断远端结果。这种状态不是“失败”，而是证据不足。

所以 `Outcome Unknown（结果未知）不得映射为普通 Failed`。只要现实结果仍然未知，系统就不能自动开启一个全新的同类副作用；先进入 Reconciliation，确认 CONFIRMED、NOT_EXECUTED 或需要人工处理。

### Reconcile 到底在做什么

Reconcile 的目标不是“再执行一次”，而是查询过去的动作。优先使用远端幂等键、业务唯一键、查询 API、回执号或外部 correlation 确认结果；没有可靠机器接口时进入人工对账。

确认成功后形成 `EffectReceipt`；确认未执行后，才可能根据当前权限和计划决定是否再次执行；长期无法确认时保持未知并升级人工，而不是为了让流程结束强行选择成功或失败。

### Retry Safety 为什么必须按操作分类

GET、纯计算、远端原生幂等 PUT、带业务唯一键的创建、不可查询的高风险 POST，其安全重试条件完全不同。统一“最多重试三次”不能表达这些差异。

06 应根据 Tool operation 的 EffectClass、远端幂等能力、是否越过 send boundary 和当前结果证据决定 RetrySafe。这个分类属于 Tool/Effect 语义，不应该由通用 HTTP Client 猜。

### Authorization、Approval 和 Audit 为什么在执行前重新检查

动作从 Proposal 到真正发送之间可能等待很久，期间权限、Approval 有效期、SecurityEpoch 或审计策略都可能变化。旧 allow 不能成为永久通行证。

执行前 06 消费 08 的当前安全决定。高风险动作如果要求 `MANDATORY_BEFORE_EFFECT`，必须先确认耐久审计回执存在；普通 Trace 写成功不能替代这个前置条件。

### Compensation 为什么不是“把旧 Receipt 改成失败”

某些现实效果可以通过反向业务动作补偿，例如撤销一条可撤销记录。但补偿本身也是新的现实动作，可能失败、需要审批，也需要独立审计。

所以历史 EffectReceipt 保持“当时确实发生”，Compensation 形成新的 action / effect 因果链。修改旧历史来假装没发生，会破坏审计和恢复。

### Crash Window 为什么要围绕耐久事实设计

执行前 crash，可以根据已保存 PreparedAction 决定是否仍要发送；发送后未记结果 crash，需要 Reconcile；远端结果已确认但本地 Receipt 写失败，也要利用远端 correlation 恢复。

这些窗口说明 06 的状态不是为了“状态机完整”，而是为了让每一个不可逆边界都有可恢复锚点。没有锚点的状态名称再多也没有意义。

### Delivery 和 Tool Effect 为什么要协作而不是合并

01 负责产品交付生命周期，但某些 Delivery 本质上会在远端产生副作用。这时 01 不应该自己猜发送结果，而是把现实动作交给 06。

06 只返回 Effect truth 和对账事实，01 再更新 Delivery observation。这样“产品需要交付什么”和“现实世界实际发生什么”保持两个清楚 Owner。

### 模型为什么只能提出动作，不能批准自己

模型可以根据任务提出“应该调用某个 Tool”，但它不能决定自己是否有权限、审批是否有效或审计是否完成。否则 Prompt Injection 或模型错误会直接升级成现实副作用。

确定性 Tool schema、semantic validator、安全策略、Approval 和 send boundary 共同构成执行门。模型能力越强，这些边界越需要保持独立。

### 什么时候 06 可以很薄

如果 Tool 全部是只读、纯计算或远端明确提供强幂等和可查询结果，Effect Control 可以非常简单，甚至主要复用现成 SDK 和 retry policy。

只有不可逆副作用、结果未知、合规审批和外部系统弱一致性真正出现时，PreparedAction、Receipt 和 Reconciliation 才值得承担复杂度。不能因为“Tool Runtime 是模块”就给所有 GET 请求套完整 Saga。

### 当前、目标与缺口

Current 是否已经实现 durable PreparedAction、send boundary、action hash、remote reconciliation 和强制审计集成，必须由代码和 fault-injection 证明；Target 文字不能代替运行证据。

Target 已明确 Proposal/Effect 分离、结果未知不可盲重试、幂等身份绑定动作内容、现实结果通过 Receipt / Reconciliation 收敛。Gap 包括具体 Tool 分类、远端幂等能力证据、crash-window 测试、人工对账流程、补偿策略和真实外围系统行为。
'''


MODULE_07 = r'''
### 这个模块解决的是“模型怎样成为受控依赖”，不是“所有 AI 逻辑都放到网关”

Zuno 会在规划、改写、抽取、专业分析、批评和综合等位置调用模型。如果每个模块直接使用不同 Provider SDK，短期最方便，长期却无法统一解释为什么选这个模型、当前数据能不能外发、失败以后能不能切换、实际花了多少预算，以及取消后是否仍产生费用。

07 因此统一的是调用边界和事实：上层表达自己需要哪类模型能力和约束，Gateway 选择当前合格 Provider / Model，记录真实 Attempt 与 Usage，再把 typed result 返回调用方。具体业务 Prompt 和专业语义仍属于使用它的模块。

### 最简单的“每个模块自己调 SDK”为什么会失控

Provider SDK 接入通常只有几十行代码，所以一开始分散调用看起来没有问题。随着模型数量增加，每个模块都会自己实现 timeout、fallback、token 统计、地域限制和 Secret 处理，最后相同问题出现多套答案。

更危险的是业务代码开始直接写某个模型名。模型升级或 Provider 下线时，Planner、Extractor 和 Query Rewriter 都要一起改，模型能力和业务语义产生不必要耦合。

### Model Role 与具体 Provider / Model 解耦

Planner 需要复杂规划能力，Query Rewriter 更关心速度和成本，Extractor 关心结构化输出。上层真正依赖的是任务角色，而不是某个厂商的 SKU。

因此保持 `Model Role 与具体 Provider / Model 解耦`。Role 是稳定语义，实际 Provider / Model 由当前资格、数据政策、预算、延迟和质量要求选择。这样模型供应变化不会迫使业务代码重新定义自己的职责。

### Provider technically available 为什么远远不等于当前能用

API health 绿色只证明技术可调用。当前材料可能因为地域、合同或数据分类禁止外发；某个模型可能没通过当前 Role 的质量基线；预算或配额也可能已经不足。

所以必须保持：

```text
Provider technically available != currently permitted != quality qualified
```

07 只能在安全允许和质量合格的集合中做路由。Fallback 也不能以“API 兼容”为理由越过这些门槛。

### 为什么模型输出永远先是 Proposal

模型即使结构正确、置信度很高，也不能自己修改 Domain、批准权限、激活高风险 Tool 或把长期 Memory 写成正式事实。模型适合产生建议、抽取、判断和 Critique，不拥有这些更强业务权威。

07 只证明“这次模型调用发生了什么、返回了什么”。结果是否满足专业语义由 05 / 04 验收，是否进入正式 Domain 由 02 决定，是否允许现实执行由 08 / 06 决定。

### 为什么调用成功要和上层成功保持距离

Provider 返回 200 和合法 JSON，只说明 transport / model attempt 成功。Capability 可能认为内容不满足专业契约，Runtime Step 可能拒绝，Domain 更可能因为证据不足不准入。

所以保持：`Gateway 调用成功 != Runtime Step accepted != Domain admitted != Answer published`。07 越是稳定地记录自己的事实，越不需要假装拥有更强成功。

### 强模型和弱模型为什么应该按任务价值分配

复杂规划、关键 Reflection 或高风险综合可能从更强推理模型获益；Query Rewrite、分类、格式转换和简单抽取通常更适合快而便宜的模型。

这不是固定的“模型等级表”。09 应通过 Role 级 Eval 证明升级是否带来足够收益；如果质量没有明显改善，贵模型不应因为品牌或参数规模自动成为默认。

### Routing 为什么要同时看质量、安全、预算和延迟

单纯按价格最低路由会牺牲质量，单纯按 benchmark 最高路由会忽略数据政策和成本。Gateway 的路由是多约束选择：当前 Role 需要什么、哪些 Provider 被允许、哪些已经通过资格、预算和 deadline 是否还能承担。

RoutingDecision 只是对这些约束的调用层组合。08 仍然拥有数据外发和 Credential policy，09 仍然拥有长期 Eval，07 不应重新发明它们。

### Retry 和 Fallback 为什么必须有边界

模型 503、连接抖动或格式暂时错误，可以做有限 Retry；某个 Provider 长时间不可用时，可以切换到当前同样合格的 fallback。

但 fallback 不是无限降低质量的逃生通道。没有满足 Role 最低要求的替代模型时，正确结果可能是让上层 Replan、Review 或 abstain。Budget、deadline 和安全约束始终限制失败链的放大。

### Budget / Quota 为什么要累计整个失败链

如果每次 Retry 或 fallback 都重新拿一份预算，一次坏请求可以悄悄消耗多倍 token 和费用。实际发生过的 Provider 调用都应该计入 Usage，即使最终结果没有被采用。

07 记录 reservation / estimate / settled usage，04 用这些事实更新 Run Budget。成本事实不会因为 Step 后来失败而消失。

### Cancellation 为什么不能只记录一个本地 flag

调用方请求取消时，Provider 可能已经完成、正在生成，也可能根本不支持可靠取消。`CANCEL_REQUESTED` 只说明本地意图，不能推断费用为零或远端停止。

Gateway 应区分 provider-confirmed cancelled、completed-before-cancel 和 cancel / billing unknown，并在需要时继续 settlement。取消控制未来等待，不改写已经发生的资源事实。

### Timeout 后启动 fallback 为什么会产生竞态

Provider A timeout 后启动 B，A 的响应可能稍后到达。如果系统只保存“最终模型结果”，就会丢失 A 的真实调用和费用，也无法解释两个结果谁先产生。

每次实际调用保持独立 Attempt identity 和 Usage。04 / 05 决定晚到结果当前是否仍有资格被接受，07 只保证调用历史不被覆盖。

### Prompt ownership 为什么不应该全部归 Gateway

Gateway 统一 transport、provider formatting、通用 safety wrapper 和 request schema，但 Planner Prompt 的业务语义属于 04，专业抽取 Prompt 属于 05，对外回答 Prompt 可能属于产品或相应 Capability。

把所有 Prompt 收进 Gateway 会让它成为 God Repository，也让业务语义和 Provider adapter 混在一起。统一调用不等于统一拥有所有 Prompt。

### Structured output 为什么需要两层校验

07 可以检查 JSON、schema 和 Provider structured-output 协议是否满足；但字段完整不代表专业内容正确。05 / 04 还需要做语义验收。

把 transport/schema success 与 semantic success 分开以后，Gateway 可以稳定解决 Provider 差异，而不会把法律专业规则塞进 SDK Adapter。

### Cache 为什么默认不能假设模型调用幂等

同一 prompt 在模型版本、temperature、provider backend 或时间变化时可能返回不同结果。只有调用方明确允许、任务对差异可接受时，才适合缓存或 duplicate suppression。

cache identity 需要绑定 Role、模型版本、prompt/input hash、generation config、schema 和必要安全 Scope。缓存复用后，上层仍然要做当前业务新鲜度判断。

### Secret 和业务数据为什么是两种不同治理问题

API Key 是 Secret，Prompt 中的案件材料是受保护业务数据。Secret 应通过受控引用和短期 Lease 使用，不能进入 Prompt、普通日志或 Checkpoint；业务数据能否外发则由 08 的数据政策决定。

07 消费 Credential ref 和 egress decision，执行允许的模型调用。它不能因为 Provider fallback 方便就扩大外发范围。

### 为什么 Model Gateway 默认不需要独立微服务

把 Provider SDK 集中到一个逻辑边界，不自动要求增加一次网络跳转。默认可以作为模块化 backend / worker 中的 adapter 和 service 实现。

只有 Secret isolation、独立吞吐扩缩、网络出口、合规边界或部署生命周期出现明确证据时，才值得拆成服务。逻辑统一比服务数量更重要。

### 当前、目标与缺口

Current 到底有哪些 Provider、Role routing、usage settlement、cancel semantics 和 qualification evidence，需要回到代码、配置和 Eval；Target 中的完整机制不代表已经实现。

Target 已明确 Role/Provider 解耦、安全与质量双门、受控 fallback、真实 Usage 和 proposal-only 边界。Gap 包括字段级路由策略、Provider 行为测试、真实成本/延迟数据、质量 qualification、取消结算和是否存在独立服务拆分证据。
'''


MODULE_08 = r'''
### 这个模块保护的不是“用户是否登录”，而是“下一步现在还能不能做”

复杂法律任务可能持续几十分钟，中间等待人工、检索多批材料、调用多个模型、重规划并执行外部动作。期间用户权限、事项归属、数据密级、模型外发政策、审批状态和凭证版本都可能变化。

如果安全只在请求入口做一次 `allowed=true`，后台 Worker 会把这次结果当成永久通行证。08 因此拥有持续安全判断：当前主体在当前时刻，针对当前资源和用途，是否还能执行下一次受保护动作。

### 最简单的“登录 + RBAC”为什么覆盖不了长任务

登录和基础角色控制非常重要，但它们只能确认一个会话和粗粒度权限。任务开始后，资源版本、Matter scope、purpose、政策和审批都可能变化。

例如用户开始时能读附件 A，十分钟后管理员撤销权限。已经合法完成的历史读取仍然发生过，但下一次从索引恢复正文、向模型外发或执行依赖 A 的 Tool 时，都必须重新检查当前条件。

### Continuous Authorization（持续授权）到底意味着什么

`Continuous Authorization（持续授权）` 不是不停轮询一个布尔值，而是在新的受保护边界到来时重新消费当前安全事实。材料读取、模型外发、Secret 使用、现实 Tool Effect 和 Formal Admission 都是典型门点。

这样权限变化控制未来动作，不试图改写过去。系统也不需要为每个 token 做远端鉴权，只需要在真正产生新的安全风险时有明确检查点。

### 为什么三种“人点同意”必须拆开

有没有权限执行某动作，是 Authorization；一个具体高风险动作是否得到规定人员批准，是 Approval；专业人员是否接受、修改或拒绝法律业务结论，是 HumanDecision。

所以保持 `AuthorizationDecision、ApprovalDecision、HumanDecision 三者 Owner 与语义不同`。同一个 UI 可以呈现三种按钮，但架构不能因为交互相似就让它们拥有相同后果。

### Approval 为什么必须绑定具体动作而不是 Step 编号

如果只记录“Step 17 已批准”，Replan 后 Step 17 的目标、参数、ToolVersion 或 EffectClass 可能已经改变。继续复用旧批准就会变成“人批准 A，系统执行 B”。

Approval 应绑定稳定 action identity / hash、目标、关键参数摘要、版本和 SecurityEpoch。会影响现实或安全语义的内容变化后，旧 Approval 失效并重新申请。

### 模型外发为什么由安全策略决定，不由 Model Gateway 决定

07 能判断 Provider 技术可用、模型质量合格和当前预算允许，却不能自己决定一份法律材料是否可以发往某个 Provider / region。

数据分类、事项范围、用途、地域和合同政策由 08 形成 egress decision。07 只能在允许集合里路由；fallback 不能成为绕过数据政策的理由。

### Secret 为什么只传引用和短期 Lease

API Key、数据库凭证和外部法院系统令牌如果为了恢复方便写进 Prompt、Checkpoint 或普通日志，会把一次受控使用变成长期泄露面。

Target 让执行模块消费 SecretRef / CredentialVersionRef / LeaseRef 一类受控引用。恢复保存“当时使用了哪个受控凭证版本和用途”，不保存秘密明文。

### Mandatory Audit 为什么和普通 Trace 不是一回事

某些高风险现实动作要求在执行前就证明谁发起、基于什么授权、谁批准、准备执行什么。普通 Trace 可能被采样、网络失败或晚到，不能承担这种前置合规证明。

如果策略要求 `MANDATORY_BEFORE_EFFECT`，必须先获得耐久 `AuditPersistenceReceipt`，06 才能继续发送。事后补一个 OTel / LangSmith span 不能倒推当时已经满足强制审计。

### Prompt Injection 为什么不能靠“更聪明的模型”解决

材料正文可能包含恶意指令，模型也可能生成越权 Action Proposal。安全不能依赖模型“自己知道不能做”。

03 控制可读材料，07 控制模型外发，04 不允许模型绕过 Plan / Budget，08 决定授权与审批，06 在真实副作用前再次验证动作。多层确定性门禁使模型输出保持 Proposal，而不是权限来源。

### 数据生命周期为什么不能只有 deleted=true

法律数据可能同时受到用户删除请求、Retention、Legal Hold、索引召回限制和物理清除流程影响。“不能再被检索”与“底层所有字节已经物理删除”不是同一个事实。

所以保持 `Retention != Recall Eligibility != Physical Purge Completion`。08 决定当前生命周期政策，各 Store 执行自己的义务并产生 enforcement fact；任何单个 Store 都不能替整个系统宣布全局删除完成。

### 为什么跨 Store 删除不应该追求一个巨大 2PC

领域库、索引、对象存储、缓存、Checkpointer 和外部 Provider 不在同一事务系统里。强行做全局原子删除不仅成本高，也无法让外部系统真正参与本地 2PC。

更合理的方式是政策先确定，各 Store 按自己的事务边界执行并记录结果，治理层根据这些事实收敛。局部失败保持可见并重试，而不是用一个 `deleted=true` 掩盖未完成部分。

### 安全服务不可用时为什么高风险路径默认 fail closed

授权引擎不可用、SecurityEpoch 无法确认、Approval 不可验证、Secret Lease 获取失败或强制审计不能落盘时，高风险动作缺少必要前提。

因此受保护材料、模型外发、Secret、Tool Effect 和 Formal Admission 默认 fail closed 或进入人工复核。低风险诊断是否允许降级必须由显式策略定义，不能由每个模块临时选择 fail open。

### 撤权发生在不同时间点为什么结果不同

如果撤权发生在模型或 Tool 发送前，后续动作应被阻断；如果请求已经发出，撤权不能把已经外发的数据“收回来”，也不能把已经发生的现实 Effect 改写成未发生。

晚到结果在继续使用、发布或正式准入前仍要重新检查当前条件。持续授权控制未来使用，不修改过去已经真实发生的历史。

### SecurityEpoch 为什么是新鲜度边界

策略决定需要知道自己基于哪一版安全规则。SecurityEpoch 让消费者识别旧 allow 是否仍适用于新的受保护动作。

它不要求全系统共享一个巨大配置事务，只要求安全决定稳定绑定政策版本，并让新的门点能判断语义相关的政策是否已经变化。

### Decision Cache 为什么不能变成永久 Capability Token

高频访问为了性能可以缓存 AuthorizationDecision，但 cache 只能降低评估成本，不能延长权限寿命。只按 user id 缓存 allow，很容易在 Matter、resource version 或策略变化后继续误放行后台任务。

cache key 和 expiry 必须覆盖真正影响安全语义的条件，并受 SecurityEpoch 约束。新的受保护动作仍然要判断缓存决定是否仍适用。

### 多租户隔离为什么必须跟着资源引用走

只在 HTTP session 保存 tenant 不够，因为后台 Worker、异步恢复和 Cache 经常脱离原请求上下文。材料、Domain object、PreparedAction、Model request 和 Delivery 都要能证明属于哪个受保护 Scope。

可以跨模块传播 opaque scope ref，避免把敏感 tenant / matter 名称塞进普通 Trace。隔离是业务和安全事实，不是日志标签。

### 什么时候 08 应该更简单

低风险内部工具如果没有多租户、敏感外发、现实副作用和复杂数据生命周期，安全层可以主要复用成熟身份系统、RBAC 和 Secret Manager，不需要自造完整 Policy Platform。

Zuno 只应保留法律业务真正需要的持续授权、动作审批、外发政策和生命周期语义。Policy Engine、Secret infrastructure 和身份目录能买就买，08 负责的是权威边界，不是重复实现基础设施。

### 当前、目标与缺口

Current 是否已有 Policy Engine、SecurityEpoch、Approval binding、Secret Lease、durable audit 和 per-store lifecycle enforcement，必须由代码和安全测试证明；Target 设计不能冒充实施完成。

Target 已明确持续授权、Authorization/Approval/HumanDecision 分离、强制审计前置、外发决策和生命周期语义。Gap 包括策略语言、真实身份集成、撤权延迟、Decision Cache 性能、安全 fault injection、Legal Hold / purge 实现和生产合规证据。
'''


MODULE_09 = r'''
### 这个模块其实在回答两个不同问题：发生了什么，以及这样做值不值得

系统出故障时，工程师需要沿一次请求找到相关 Run、检索、模型、Capability、Tool、Domain 和 Delivery；架构演进时，团队又需要判断 GraphRAG、Reflection、Native Runtime 或强模型是否真的提高质量。

Observability 负责解释系统发生了什么，Evaluation 负责判断结果好不好、复杂度是否值得保留。两者共享版本、关联和数据治理，但不能因为都“看数据”就混成一个 Dashboard。

### 最简单的“Trace 里有完整链路，所以 Trace 就是真相”为什么危险

Trace 非常适合关联调用，但它可能被采样、Exporter 失败、网络中断或 redaction 删除内容。如果恢复和业务判断依赖 Trace，观测系统故障会反过来破坏业务正确性。

因此保持：

```text
Telemetry != Durable Audit != Business Truth
```

02、06、08 等 Owner 保存自己的耐久事实，09 引用它们解释时间线。漂亮 span 不能替代 AdmissionReceipt、EffectReceipt 或安全审计证明。

### 事故调查为什么应该先问 Owner Fact

用户报告“系统重复提交了两次”，第一步不是统计 Trace 里有几个 HTTP span，而是查询 06 的逻辑动作、Attempt、EffectReceipt 和 Reconciliation，确认现实世界到底发生了几个效果。

随后再用 Runtime Plan、Security decision、Delivery 和 Trace 对齐时间线。Observability 的价值是帮助解释“为什么发生”，不是自己裁决“业务事实是什么”。

### Correlation 为什么重要，但不能成为万能业务 ID

九个责任域各自拥有事实，如果没有稳定 correlation，就很难回答某次模型调用属于哪个 Step、产生哪个 Capability output、最后是否正式进入 Domain。

系统可以传播 request / run / step / action / admission 等 opaque refs 做定位，但 correlation id 不能自动成为幂等 key、授权 token 或业务主键。关联帮助查询，不产生权威。

### OpenTelemetry Baggage 为什么要保持最小化

Baggage 会跨进程广泛传播，如果把 tenant 名称、案件名称、用户 PII、材料正文或授权内容直接塞进去，诊断便利会扩大敏感数据暴露面。

默认只传播最小 opaque identity，在可信边界回查 Owner fact。尤其 `Secret NEVER EXPORT`。必要业务文本只有在策略允许、完成 redaction 且确实有诊断价值时才进入受控 Telemetry。

### Sampling 为什么只能影响观测细节

高吞吐系统不可能永久保存每一个成功 span，Sampling 是合理成本控制。可以提高 error / high-risk task 采样率，降低普通成功请求采样。

但 Sampling 不能决定 Domain、Effect、Authorization 或 Mandatory Audit 是否存在。关闭 tracing 不能让系统失去恢复能力，也不能让安全证明消失。

### Eval Dataset 为什么必须版本化

今天一百个 case，明天修改二十个标签，如果两次分数直接比较，就无法判断变化来自模型还是数据集。Dataset 本身也是实验输入。

DatasetVersion 需要稳定 case identity、材料 refs、任务类别、标签 / expected evidence、annotation provenance 和数据政策。数据集变化产生新版本，保证实验结果可解释。

### 训练暴露为什么必须和测试集分开

Prompt tuning、few-shot、模型训练或人工调参如果已经看过某些 case，这些样本就不能在不说明的情况下继续充当独立 test。

Eval 需要记录 split 和 exposure provenance。真实法院材料受数据政策限制时，也不能偷偷换成合成数据后仍然声称“真实法院质量已验证”；测量范围必须明确。

### LLM Judge 为什么只能处理适合模型判断的问题

引用是否存在、JSON 是否合法、action hash 是否一致、重复 Effect 是否发生，都应该优先使用 deterministic checker。开放式法律论证、适用性和表达质量才更适合 LLM Judge。

Judge 自身也有模型、Prompt 和漂移问题，因此 JudgeVersion 需要进入 Eval config，并用人工金标准校准。Judge 不可靠时结果应标记 blocked / unreliable，而不是为了持续产分数而假装可信。

### PASS、FAIL 和 BLOCKED 为什么必须严格区分

PASS 表示在冻结 Dataset、配置、样本数和阈值下真正达标；FAIL 表示评测有效执行但结果不达标；BLOCKED 表示根本没有资格判断，例如没有样本、凭证缺失、Judge 不可用或 baseline 不可比。

当前正式 benchmark 在证据不足时应明确 `MEASUREMENT_BLOCKED`。Blocked 不是较轻的 Fail，更不能默认为 Pass。

### 为什么 Critical Failure 可以否决漂亮平均分

法律场景里，越权读取、重复高风险 Effect、正式引用无法回溯、stale WorkProduct 被错误发布等问题不能被高平均准确率抵消。

Release Evaluation 因此既看 aggregate metrics，也看 critical failure taxonomy。平均分很好但触发定义中的关键安全/正确性违规，发布资格仍然可以 Fail。

### 为什么要同时评质量、恢复、延迟和成本

Agent 复杂度常常在最终准确率以外付出代价：Retry 放大、P95 延迟、人工介入、token 和 Provider 费用。一个方案提高一点准确率，却让成本和恢复失败面翻倍，未必值得保留。

评测因此需要把 evidence sufficiency、citation correctness、unsupported claim、reviewer acceptance、recovery correctness、duplicate effect、Replan rate、reconcile duration、latency、token 和 cost 放在同一实验解释里。

### 为什么指标必须按 Task Class 分层

简单条文定位、跨文档争议分析、带现实副作用的任务目标不同。把它们混成一个“Agent Success Rate”，会让简单题数量掩盖复杂路径问题。

每个 EvalCase 应绑定 task class、difficulty / risk profile 和实际执行路径。这样才能回答 GraphRAG 是否只对某类 query 有价值，Native Runtime 是否只在长任务恢复上有收益。

### Evaluation 为什么应该主动帮助删除复杂度

团队已经实现的功能很容易获得沉没成本保护：有 GraphRAG 就只展示 GraphRAG 的分数，有 Reflection 就只证明它“能跑”。

09 应主动设计 baseline、ablation 和 kill test：GraphRAG vs Hybrid Retrieval、Memory on/off、Reflection on/off、Generic Host + Legal Backend vs Native Runtime。在尽量相同语料、模型和预算下比较真实边际收益。

### Provider-neutral Observability 为什么重要

Target 采用 OpenTelemetry / OTLP-compatible contract，让 LangSmith 可以作为 Agent / LLM Trace 与 Eval 的 preferred Provider，但核心运行和审计不能依赖单一 SaaS。

更换 OTel backend 或未来其他观测 Provider 时，稳定 correlation、redaction 和 semantic convention 不应改变业务 Owner。Provider 可替换才说明观测层没有绑架运行架构。

### Telemetry Provider outage 为什么不应该阻断普通业务

如果 Trace exporter 故障，09 可以 buffer / retry 或丢弃低优先级 telemetry；02 / 06 / 08 的耐久事实继续成立，普通业务不应因为 Dashboard 暂时不可用就全部停止。

只有安全策略明确要求的 Mandatory Audit 走独立 durable boundary。Tracing 可用性和合规审计可用性必须分开。

### Release Evidence 为什么不等于 Production Readiness

一组 Eval PASS 只能说明它覆盖的 Dataset、配置、commit 和 profile 达到门槛。生产成熟度还需要容量、HA / DR、安全 qualification、恢复演练、外部依赖和运维证据。

09 可以形成 ReleaseEvaluationEvidence，但不能单独宣布整个系统 production ready。测量越严谨，越应该明确它没有覆盖什么。

### 当前、目标与缺口

Current 到底有哪些 Trace、Metric、Dataset、Judge、release gate 和真实 benchmark，必须回到证据；没有样本或 Provider 条件时保持 BLOCKED，而不是从 Target 推断质量。

Target 已明确 Telemetry 与业务真相分离、Dataset / Eval 版本化、deterministic checker 优先、复杂度 kill test 和 provider-neutral observability。Gap 包括真实基准数据、Judge 校准、生产 telemetry 成本、隐私 redaction 验证、恢复与 Effect fault injection，以及复杂机制是否真正值得保留。
'''


ARCH_README = r'''# Zuno 总体架构文档

`docs/architecture/` 是 Zuno 唯一的总体架构入口。第一次阅读这里时，不需要先理解全部 Contract、状态机或内部对象；先回答三个问题：**Zuno 为什么需要比普通 RAG 多承担一些责任、这些责任为什么必须分开、系统失败以后靠什么事实恢复。**

如果还不知道项目为什么存在，先读 [`../project/project.md`](../project/project.md)。如果已经理解项目背景，直接进入 [`architecture.md`](architecture.md) 的 Part A。要追某一个责任域，再进入 [`../modules/README.md`](../modules/README.md) 和对应模块 Part A。

## 四个文件分别负责什么

`docs/architecture/` 只保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

- `architecture.md`：唯一总体 Target Architecture 正文。Part A 解释概念设计和因果，Part B 保存跨模块精确工程约束。
- `architecture-views.md`：总体 Mermaid 图源，用图帮助理解，不拥有第二套架构事实。
- `architecture.html`：图形展示入口，消费同一份 Mermaid 源。
- `README.md`：告诉读者从哪里开始、当前设计处在哪个治理阶段，以及怎样区分 Target 和 Current。

不得创建第五个总体架构文件，也不得建立 `.agent/architecture/` 或 `.agent/modules/` 镜像。一个设计只保留一套 Canonical Truth。

## 先理解一个最重要的边界

Zuno 不是“把九个模块都串起来才算一次请求”。简单法律问答可以只做当前授权、知识就绪、检索、模型和发布；复杂分析才需要显式 Runtime、专业 Capability 和正式 Domain Admission；只有现实副作用任务才需要 Effect Control、Approval 和 Reconciliation。

九个模块首先是**事实 Ownership 和失败恢复边界**，不是九个微服务。默认可以运行在模块化 Python 后端和按工作负载拆分的 Worker 中。只有独立吞吐、安全隔离、部署生命周期或故障半径有证据时，才按 ADR-0012 考虑物理拆分。

## Part A 为什么允许很长

Part A 不是 Executive Summary，也不是删掉几个字段后的 Part B。复杂架构要把问题、最简单方案、失败反例、概念边界、恢复、替代方案和 Trade-off 讲清楚，本来就可能需要较长篇幅。

新的 [`../governance/architecture-narrative-quality-standard.md`](../governance/architecture-narrative-quality-standard.md) 明确要求：长度来自概念设计和因果推导，而不是 Object / State / Contract 名称数量。术语用于压缩已经理解的概念，不能代替解释；推荐推理链不是固定标题模板。

因此阅读 Part A 时，应该先记住“为什么这样设计”，再去 Part B 查 `AdmissionReceipt`、`PlanVersion`、`PreparedAction` 等精确对象。

## 当前 Target 的核心思想

总体设计把机器候选、正式业务事实、知识派生、运行控制、现实副作用和安全决定分开，让每一种更强事实都拥有明确 Owner。恢复时先找最强 durable owner fact，再修复 Checkpoint、Cache、Delivery 或 Telemetry projection。

复杂度继续受 Evidence Gate。Native Runtime、GraphRAG、Long-term Memory、Specialist / Multi-Agent、强模型路由和物理服务拆分都不是“有了就永久保留”的能力；09 必须通过 baseline、ablation 和 kill test 证明边际收益。

研究成果也按同样原则进入架构。ADR-0015 接受的是 Research Artifact → stable Capability semantics → versioned Provider → Conformance / Eval → Eligibility → Runtime use 的路径，而不是因为某篇论文、某个开源框架或某项课题组成果存在，就反向制造 Zuno 的业务需求。

## Current、Target、Future 和 Evidence 怎么读

`architecture.md` 与九篇模块主要描述 **Target**。Target 设计完整，不代表代码、数据库、Provider、HA / DR 或生产流程已经存在。

判断 **Current** 必须回到 [`../evidence/`](../evidence/)。Pilot Validation 不等于 Production，设计差异也不等于已经测出优势。没有真实 Eval、容量、恢复演练或安全资格时，应保留 Unknown / Measurement Needed。

历史 Red / Blue 记录解释设计怎样形成，但不重新拥有当前事实。当前阶段先做文档质量提升，不需要为了历史问题机械扩展架构。

## 九模块当前治理状态

```text
overall_architecture: ROUND_02_FROZEN
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

`Detail Design Candidate V1` 表示模块已经有足够精度进入冻结前审查，不表示字段、表、enum、Migration、API、服务拆分或实现已经冻结。下一道架构门仍然是 Module Detail Freeze Review；冻结也不自动产生 Implementation Authorization。

## 推荐阅读顺序

第一次建立 mental model：

```text
../project/project.md
→ architecture.md Part A
→ ../modules/README.md
→ 目标模块 Part A
```

需要实施或审查时再进入：

```text
architecture.md Part B
→ 目标模块 Part B / Part C
→ 相关 ADR
→ docs/evidence/
→ docs/governance/
```

如果读完 Part A 只能记住几十个内部名词，却说不清为什么需要这些边界，应该优先修正文档，而不是继续增加 Contract。

## 维护原则

总体架构负责跨模块 Authority 与 Target 整合；模块文档只能细化已接受边界，不能局部改变九模块 Owner、Canonical Legal Kernel、Formal Admission、Knowledge / Domain authority、Retry / Replan / Reconcile、安全政策或 Effect truth。

跨层语义变化才修改 `architecture.md` 或 ADR；模块内部精度下沉到 `../modules/`；Current 证据进入 `../evidence/`；项目历史和 Ownership 叙事进入 `../project/`。图形变化同步 `architecture-views.md` 与 `architecture.html`。

常用验证：

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```
'''


MODULES_README_PREFIX = r'''# Zuno 模块架构

九个模块首先是一张**责任地图**：当一次法律任务跨越材料、模型、专业分析、正式结果、现实副作用和外部交付时，哪一类事实由谁最终负责，失败以后先相信谁。它们不是九段固定流水线，也不是九个微服务。

第一次阅读本目录，不需要先记 `AdmissionReceipt`、`PlanVersion`、`PreparedAction` 等内部对象。先理解三条任务路径和九个责任域为什么存在；真正实施时再进入每篇 Part B / Part C 查精确 Contract、状态和 Crash Window。

## 先用三条任务路径建立 mental model

### 简单法律问答

用户问“合同第 8 条写了什么”时，最短合理路径是：明确 Scope，检查当前授权，确认所需材料已经就绪，检索原文和稳定引用，受控调用模型，最后检查答案是否可以发布。

这条路径不默认需要 Native Runtime、Dynamic DAG、Multi-Agent、Long-term Memory 或 GraphRAG。通用 Host 如果遵守同样的安全、知识和发布边界，也完全可以承担会话和 UI。

### 复杂法律分析

多材料争议分析开始需要显式控制：系统先确认材料版本和知识覆盖，再由 Runtime 组织多步依赖、并行专业能力和必要人工复核。检索和模型产生的内容仍然只是候选，只有需要成为长期法律业务事实的结果才进入 02 Formal Admission。

这里最重要的不是“经过多少 Agent”，而是运行控制、专业计算和正式业务事实始终保持三个边界。Runtime 可以完成任务，但不能替 Domain 宣布正式结果。

### 带现实副作用的任务

如果系统要向外围法院系统提交结果，问题从“算得对不对”增加到“现实世界到底发生了什么”。动作发送前要重新确认授权、必要审批、幂等和强制审计；发送后 timeout 时先对账，禁止因为本地没有响应就盲重试。

06 负责现实 Effect truth，01 负责产品交付语义，08 负责当前是否允许。三个模块协作，但互不冒充对方的完成事实。

## 九个责任域分别为什么存在

| 编号 | 责任域 | 用一句人话说明它保护什么 | 文档 |
| --- | --- | --- | --- |
| 01 | Application & Integration | 把内部权威事实组合成稳定请求、发布、交付和失效传播语义 | [01](01-application-integration.md) |
| 02 | Legal Domain & Work Product | 决定什么最终成为正式、长期、可审计的法律业务事实 | [02](02-legal-domain-work-product.md) |
| 03 | Knowledge & Evidence | 区分正式材料、可重建知识派生、任务就绪和检索候选 | [03](03-knowledge-evidence.md) |
| 04 | Agent Runtime & Control | 控制长任务怎样计划、并行、暂停、重规划和恢复 | [04](04-agent-runtime-control.md) |
| 05 | Capability & Skill | 把研究算法和 Provider 变成稳定、版本化、可替换的专业能力 | [05](05-capability-skill.md) |
| 06 | Tool Runtime & Effects | 在现实副作用发生前后保护动作身份、结果确认和对账 | [06](06-tool-runtime-effects.md) |
| 07 | Model Gateway | 把模型调用变成受质量、安全、预算和用量约束的依赖 | [07](07-model-gateway.md) |
| 08 | Security & Governance | 持续回答下一次受保护动作现在是否仍被允许 | [08](08-security-governance.md) |
| 09 | Observability & Evaluation | 解释系统发生了什么，并验证复杂度是否值得保留 | [09](09-observability-evaluation.md) |

这些责任域按事实 Ownership 切分，不按技术栈切分。默认可以共处模块化 Python 后端；只有吞吐、安全隔离、故障半径或部署生命周期出现证据时才拆物理服务。

## Part A、Part B、Part C 应该怎么读

Part A 可以很长，它负责把概念设计讲透：问题是什么、最简单方案为什么不够、边界如何推导、典型失败怎样恢复、替代方案和删除条件是什么。长度应该来自推理，而不是名词密度。

Part B 把已经理解的设计精确化成 Owner、Contract、状态、事务、幂等、持久化和 Detail Freeze Candidate；Part C 再检查这些语义跨模块以后，完成证明、版本、新鲜度、取消、晚到和恢复是否仍然一致。

如果一个对象名必须先读 Part B 才知道它为什么存在，Part A 应补概念解释；反过来，如果 Part A 开始连续枚举字段、enum 和 crash-window 表格，则应该下沉到 Part B。

## 当前模块设计状态

```text
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

**9/9 Detail Design Candidate 只表示 Target Design 已达到冻结前可审查粒度。** Current、实现、质量和生产资格继续回到 `docs/evidence/`；`DETAIL DESIGN CANDIDATE V1 AVAILABLE` 不等于 `Module Detail Freeze Review` 已通过。

## 为什么下面还保留大量 Reference

从下一节开始，本 README 转入跨模块 Reference：事实 Ownership、Completion Proof、Cancellation、Late Result、Idempotency、Recovery 和横向系统设计。它们用于整体一致性审查，不要求第一次阅读全部记住。

'''


def main() -> None:
    replace_between(
        "docs/architecture/architecture.md",
        "## Part A — Architecture Narrative",
        "## Part B — Detailed Architecture Specification",
        ARCHITECTURE_PART_A,
    )

    modules = {
        "docs/modules/01-application-integration.md": MODULE_01,
        "docs/modules/02-legal-domain-work-product.md": MODULE_02,
        "docs/modules/03-knowledge-evidence.md": MODULE_03,
        "docs/modules/04-agent-runtime-control.md": MODULE_04,
        "docs/modules/05-capability-skill.md": MODULE_05,
        "docs/modules/06-tool-runtime-effects.md": MODULE_06,
        "docs/modules/07-model-gateway.md": MODULE_07,
        "docs/modules/08-security-governance.md": MODULE_08,
        "docs/modules/09-observability-evaluation.md": MODULE_09,
    }
    for path, narrative in modules.items():
        replace_between(
            path,
            "## Part A — Human Narrative",
            "## Part B — Engineering / Agent Reference",
            narrative,
        )

    (ROOT / "docs/architecture/README.md").write_text(ARCH_README.strip() + "\n", encoding="utf-8")

    modules_readme = ROOT / "docs/modules/README.md"
    text = modules_readme.read_text(encoding="utf-8")
    marker = "## 九模块最重要的事实所有权"
    if marker not in text:
        raise RuntimeError("cannot locate modules README reference boundary")
    _, suffix = text.split(marker, 1)
    modules_readme.write_text(
        MODULES_README_PREFIX.strip() + "\n\n" + marker + suffix,
        encoding="utf-8",
    )

    # The script is intentionally temporary; the workflow also removes its own file.
    Path(__file__).unlink()


if __name__ == "__main__":
    main()
