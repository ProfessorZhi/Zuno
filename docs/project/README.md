<!--
status: canonical-project-narrative
canonical_question: Zuno 为什么存在、为什么值得建设、与通用平台相比多承担什么责任、项目怎样发展、参与者做过什么、哪些事实今天可以相信？
owner: Project Documentation Owner
source_boundary: 历史事实来自已确认项目回忆与公开背景；产品定位来自已接受 Target Architecture；Current 必须回到 docs/evidence；不得用今天的设计反写历史，也不得把设计差异写成已测优势
-->

# Zuno 项目：将智慧司法研究转化为可验证的法律智能工作系统

Zuno 是南京大学软件学院 LIPLAB 智慧司法研究与工程化背景下的法律智能 Agent 平台，面向天津法院智慧平台相关场景。项目的长期目标不是再做一个能够生成法律文本的聊天入口，而是把案件材料、课题组研究成果、基础模型、专业人员判断和外围业务系统连接成一条可以持续运行、复核、评价和恢复的法律工作链。

这个定位决定了 Zuno 不能靠“用了 Agent”“用了 GraphRAG”或“模型更强”证明价值。Conversation、普通 Workflow、MCP、RAG、Checkpointer、Subagent、Tracing 等能力正在快速成为成熟平台基础设施；能 Buy / Reuse 的部分应该继续复用。Zuno 真正值得长期 Own 的，是通用平台不会替法律业务决定的语义：材料和证据怎样保持版本与来源，研究成果怎样变成有资格的专业能力，机器候选何时可以进入正式业务历史，现实副作用怎样在网络不确定性下恢复，以及哪些复杂机制真的改善专业工作。

外部研究已经反复指出法律 AI 中存在检索错配、材料覆盖不足、模型幻觉、错误引用、自动化偏见、不可追溯输出和责任归属等问题。相关领域证据整理在 [`docs/research/legal-ai-domain-problem-evidence.md`](../research/legal-ai-domain-problem-evidence.md)。这些研究只能说明领域约束客观存在，不能反向证明历史 Zuno 已经逐项遇到、解决了同样问题。

Zuno 自己的历史必须保持更严格的边界。当前能够确认系统经历过 Internal Demo、客户侧 / 智慧法院项目组 Demo、法院侧人员测试和 Pilot Validation；客户侧 Demo 曾留下“回答质量还需要提高”的反馈。现有材料仍不足以判断当时的质量问题究竟来自 Prompt、Retrieval、Model、Memory、Tool、引用还是数据处理，也没有恢复完整 Bad Case、前后指标或正式验收。今天的 Target Architecture 不能用来补写当时的原因。

## 项目真正要解决的是研究能力进入长期法律工作的条件

简单法律问答不需要 Zuno 的全部复杂度。用户只问“合同第 8 条约定了什么”时，权限检查、材料读取、受控检索、稳定引用和一次模型调用已经可能满足要求。真正改变系统性质的是任务开始承担长期专业责任以后出现的一组约束。

**材料不是静态知识库。** 一宗事项可能包含起诉状、答辩材料、合同、补充协议、扫描附件、聊天记录和后续补交证据。文件上传成功只说明材料到达；OCR、解析和索引完成也只说明某种派生知识生成。系统还需要判断当前任务依赖的关键材料是否齐全，以及缺失部分会不会改变结论。

**普通 Top-K 不能证明“全案没有”。** Retriever 找到若干片段，只能证明这次查询看到了这些内容；它不能证明关键材料没有遗漏。Zuno 因此需要稳定 DocumentVersion、KnowledgeGeneration、任务级 Readiness 和可追溯 Citation，而不是把 Knowledge 简化成一个向量库。

**模型输出保持候选性质，直到专业责任真正建立。** 检索、研究模型、LLM 和规则都可以生成事件、证据、法律分析和事实候选；需要长期保存、继续流转或交付的内容仍然要经过材料版本、专业规则和必要人审形成正式 WorkProduct。机器计算成功和业务正式成立是两个时间点。

**正式结果必须能解释形成依据。** 几周以后，系统需要回答使用了哪版材料、哪些来源支持了哪些主张、模型当时返回什么、专业人员改了什么、为什么最终采用这一版，以及后来什么变化使旧结论需要复核。新的证据可以让旧结论失去当前适用性，但不能覆盖已经发生过的判断和交付历史。

**研究原型与长期业务之间存在工程转化层。** 论文在特定数据集和指标上有效，不代表真实系统已经具备稳定 Contract、Provider 替换、任务适用范围、权限、失败语义、恢复和成本控制。Zuno 的重要职责之一，是把 Research Artifact 转成稳定 Capability，再用 Conformance、Evaluation 和 Eligibility 决定某个模型、规则或服务当前是否有资格实现它。

**长周期任务不能由最后一次模型调用代表。** 多材料分析可能持续几十分钟，甚至跨越人工等待。期间会有新材料、旧计算晚到、模型限流、权限变化和计划调整。Runtime 需要恢复执行，但它的 `completed` 不能替法律业务宣布正式结果已经成立。

**现实副作用把网络错误变成业务不确定性。** POST timeout 只说明本地没有拿到确定响应，远端可能没执行，也可能已经成功。Blind Retry 可能制造第二次业务动作，所以外部 Action、Attempt、Effect 和 Reconciliation 必须与普通计算失败分开。

这些约束共同限定了 Zuno 的产品边界。普通 RAG / 固定 Workflow 足够的任务继续保持简单；只有跨越材料版本、长期运行、专业判断、正式结果和现实副作用以后，更强的状态和恢复机制才有价值。

## 研究资产应成为专业能力层，而不是论文展示区

LIPLAB 已积累事件抽取、事件对齐、冲突识别、法条推荐、事实—法条对应、法律模型评测和复杂案件建模等研究成果。长期产品价值不在于“每篇论文包一个 Tool”，而在于把这些成果抽象成稳定专业能力，并允许底层 Provider 替换。

事件抽取与事件对齐可以支撑案件时间线；双方陈述冲突可以支撑争议焦点研究；事实—法条对应和法条推荐可以形成法律依据候选及其事实解释。它们首先是 Knowledge projection / Candidate，只有在业务长期采用并需要版本、人工判断和有效性语义时才进入正式 Domain。

LawBench、LJPCheck、CMDL 等研究资产更适合作为 Qualification / Regression 的上游。公开 Benchmark 分数可以帮助拆 Task Class 和 failure taxonomy，却不能直接替真实法院任务给出 Production qualification。

研究成果进入产品更接近这条路径：

```text
Research Problem
→ Research Artifact / Dataset / Evaluation Method
→ Stable Legal Capability
→ Provider
→ Task-Class Qualification
→ Agent Tool / Skill / Workflow
→ Human-reviewed WorkProduct
→ Governed Feedback / Regression
```

中间任何一跳都不能靠论文分数自动成立。更完整的研究—产品转化方案见 [`docs/research/legal-agent-value-strategy-2026-09.md`](../research/legal-agent-value-strategy-2026-09.md)。

## Agent 技术负责组织执行，不负责成为法律 Authority

Agentic Retrieval、Context Engineering、Subagent、Memory 和 Multi-Agent 都服务于“这次任务怎样执行得更好”。案件材料、专业候选、HumanDecision、正式 WorkProduct 和现实 Effect 继续保存在各自 Owner 边界中，模型上下文只在当前任务需要时组装。这样 Agent Harness、模型和并行策略可以替换，而不会把长期法律事实绑在某一代运行框架上。

这些机制也不因为已经实现就获得长期保留权。简单 Workflow 或 Generic Host 已经满足任务时继续复用；只有真实任务暴露了稳定缺口，而且 Evaluation 能证明新增机制带来足够收益时，才扩大 Context / Memory / Specialist / Native Runtime 等复杂度。具体的 Memory Authority、版本漂移、恢复顺序和复杂度退出条件由 [Overall Architecture](../architecture/architecture.md) 统一解释，这里只保留它们对产品定位的影响。

这个边界还决定了 Zuno 的产品身份。用户长期维护的是 Matter、材料、候选结构、专业判断和正式成果，不是某一次 Agent 对话或某一代 Harness 的内部状态。聊天可以换成任务面板，Generic Host 可以换成 Native Runtime，模型和 Retriever 也可以更新；只要这些长期对象和业务语义保持稳定，产品就不需要随着执行框架迁移全部案件历史。

## 更有价值的产品形态是可验证的案件研究工作空间

如果 Zuno 只围绕聊天记录组织产品，课题组的大量研究最终仍会被压回一段模型输出。更稳定的产品视图是 Matter / Case Workspace：材料与加工状态、事件时间线、陈述冲突、争议焦点、证据支持/反驳关系、事实—法条候选、尚未解决的问题、机器候选、HumanDecision、正式 WorkProduct 及其当前有效性都可以被持续复核。

Agent 仍然是重要入口。它可以接受“分析双方关于付款义务的争议并形成审查意见”这类开放任务，再围绕 Workspace 结构完成检索、专业能力调用、补证和草稿生成。但它不是唯一产品模型，也不拥有这些结构的最终事实。

这使 Agent Harness、模型和 Retriever 都可以演进。底层框架替换以后，Matter、DocumentVersion、正式 WorkProduct 和 HumanDecision 仍然存在；新的研究模型进入以后，也可以在相同 Task Class 和 Evaluation 下与旧 Provider 对照，而不必重新发明整个产品流程。

## 长期价值来自 Research–Product Feedback Loop

真实案件、法院侧测试和 Pilot 会产生 Bad Case、专业人员修改、未覆盖问题和 Agent Failure Trace。经过数据治理以后，其中一部分可以进入 Evaluation，形成新的 Task Class、Regression 和 baseline。研究团队再根据稳定 failure class 提出新问题，开发新的 Retriever、模型、规则或数据集。

```text
真实法律工作
→ 人工修改 / Bad Case / Failure Trace
→ Task Class + Functional Eval
→ Research Question
→ Research Artifact / New Provider
→ Qualification / Controlled Release
→ 真实法律工作
```

这个闭环比拥有某一个“最强模型”更难复制。基础模型、通用 RAG、Agent Framework 和 MCP 都可以买到；长期积累的法律任务定义、专业结构、专家修正、功能测试、失败数据和资格标准更接近项目真正的工程资产。

这些材料只有被组织成可复查的问题定义以后才会形成资产。一个 Bad Case 至少需要知道任务类别、材料范围、当时输出、专业人员为什么修改或拒绝，以及后来用什么条件判断修复是否成立；否则“用户不满意”“这个模型更好”仍然只是难以复用的经验。Reviewer protocol、Task Class 和 failure taxonomy 的价值正在于把零散反馈变成下一次研究和工程都能使用的共同语言。

这也给研究与产品一个更稳定的分工。研究可以探索新的模型、检索或数据方法，产品侧提供真实约束、失败类别和可接受条件；候选方法只有在同一任务定义下证明收益，才进入 Qualification 或 Controlled Release。产品失败再回到研究问题，而不是让论文指标直接变成产品能力宣称。

产品价值也应回到专业工作结果：关键材料是否更容易被找到，严重遗漏和错误引用是否减少，候选被直接接受、局部修改、完全拒绝或要求补证的比例怎样变化，形成一份 review-ready WorkProduct 需要多少人工步骤，以及这些收益是否覆盖新增 token、latency 和运维复杂度。当前没有足够数据时保持 `Measurement Needed`，不制造漂亮数字。

## 任务复杂度决定需要多少 Zuno

**通用宿主 + 法律 Capability** 适合简单问答、轻量检索和少量专业工具。成熟 Host 继续承担会话、Generic Tool Calling 和基础工作流。

**通用宿主 + Zuno Legal Backend** 适合材料版本、正式工作成果、Provider Qualification、Effect / Security 业务语义已经成为产品要求，但长周期 Agent Runtime 仍可由成熟平台承载的场景。这很可能是长期最经济的主形态之一。

**Zuno Native Runtime + 一等领域状态** 只在动态计划、长等待、复杂恢复、持续授权或领域级并发控制真的成为约束时才值得建设。GraphRAG、Reflection、Long-term Memory、Persistent Multi-Agent 和 Native Runtime 的具体 Build / Buy / Delete 规则由总体架构与 09 Evaluation 负责；Project 只保留这个产品原则：复杂度必须由真实任务和测量结果证明。

这三种形态不是三个互斥产品，也不要求整个部署只能选择其中一种。同一套 Zuno Legal Backend 可以让简单请求走短路径，让复杂案件进入更强的运行控制；外围法院系统也可以继续作为 Host。产品成熟度体现在能根据任务约束选择最小充分路径，而不是把所有请求都强迫进入最复杂的 Agent Runtime。

## 下一阶段要关闭的是证据闭环，而不是继续增加模块

当前架构已经能够提出很多“应该如何”的答案，下一阶段最有价值的工作是把其中一部分变成可以复查的工程事实。没有这些闭环，继续增加 Agent 角色、Provider、状态对象或服务，只会让 Target 更完整，却不会让产品更可信。

第一条闭环来自真实质量问题。客户侧曾反馈回答质量仍需提高，但根因和修复指标没有恢复。相比继续增加 Retriever 或模型机制，更有价值的是恢复一两个完整 Bad Case：原始输入与材料范围、错误表现、根因、修复、同 case Regression，以及修复以后能够证明到什么程度。

第二条闭环来自系统故障和恢复。负向 fault probe 只有在后续修复被同类 regression 锁住以后，才真正转化成长期工程知识。具体哪些 failure shape 已经关闭、哪些仍是 Gap，由 [Current Evidence](../evidence/README.md) 维护；Project 只保留“失败 → 修复 → regression → 可复查证据”这条演进方式，不复制 implementation wave。

一个完整闭环还要让后来的人能够重新判断结论：当时输入和环境是什么，失败会造成什么业务后果，哪个 Owner 修复了什么，哪条 regression 锁住了同一窗口，以及这份证据明确没有证明什么。只有这样，项目经验才不会退化成“曾经修过一个 bug”或“某次 CI 绿过”。这也是 Project、Evidence 与 Architecture 分层的实际价值。

第三条闭环决定复杂机制的去留。GraphRAG、Memory、Native Runtime 或 Multi-Agent 应在固定任务、语料、预算和 baseline 下比较收益与新增状态面；没有稳定边际收益就缩小或删除。具体实验设计属于 09 Evaluation，项目层只记录这种复杂度治理会反过来决定产品边界。

第四条闭环是个人与团队事实的可追溯性。对简历和项目复盘最有价值的不是继续扩大“参与过”的范围，而是把一两个个人任务恢复成完整链路：需求从哪里来，接手前是什么状态，自己改了哪些代码或 Contract，测试怎样锁住 bad case，结果能证明到什么程度，哪些部分仍然属于团队或后续 Target。Tool/MCP、GraphRAG retrieval quality、Context/Memory V2 已经有公开提交基础，后续应优先补原始 Issue、Review、历史测试结果或真实运行材料，而不是把今天的总体架构 Ownership 倒推回 2026 年 3 月。

法院侧测试和 Pilot 也需要同样的恢复方法。比“有过 Pilot”更有工程价值的信息，是当时处理什么 Task Class、由什么角色使用、材料和环境怎样准备、失败时谁兜底、结果怎样被复核、什么条件才算可接受。当前缺少这些原始材料，就继续保持 Unknown；以后如果能够恢复，再把它们写回 History，而不是用今天的 benchmark 或架构设计替代。

按这个标准，项目成熟度不由模块数量或 Agent 数量决定，而由团队能否回答三个问题决定：为什么增加这层复杂度，什么证据证明它解决了原问题，以及什么条件出现时应该缩小或删除它。能够保留必要复杂度，也能够有依据地删掉无收益机制，才说明研究原型开始变成可持续产品。

## 项目真实走过的阶段

今天的产品化战略和 Target Architecture 不能反写历史。根据目前能够恢复的材料，项目历史更接近：

```text
已有产品和代码
→ Agent / Memory / Tool 等方向继续开发
→ Internal Demo
→ 客户侧 / 智慧法院项目组 Demo
→ 客户反馈：回答质量需要提高
→ 后续迭代
→ Court-side Testing
→ Pilot Validation
```

**加入项目时，系统已经存在。** 我约在 2026 年 3 月加入，加入时已经有代码和一个比较简单的自研前端，因此不是 Greenfield 项目。项目前期产品方向和第一版系统不能算作个人成果。历史第一条需求、最早提交、第一版正式产品名称和当时完整技术栈尚未恢复，今天 `main` 的目录与依赖不能自动成为历史说明。

**Internal Demo / 客户侧 Demo 说明系统进入过真实验证过程，但不证明正式质量门槛。** 当前只确认客户曾反馈“回答质量还需要提高”。没有材料支持把根因直接归结到 Prompt、Retrieval、Model、Memory、Tool、引用或数据处理，也没有恢复前后准确率。

**法院侧测试比内部 Demo 更接近真实工作环境。** 但测试题数量、参与法院、人员角色、参考答案、Reviewer protocol、环境和性能数据仍未恢复。

**Pilot Validation 仍属于试点。** 当前没有资料支持正式 Production、稳定用户规模、部署 Endpoint、SLA、QPS、Latency、Token、Cost、HA 或 DR。Pilot 最值得继续恢复的是任务类型、使用方式、失败、人工兜底和验收条件。

## 团队与个人参与的边界

目前能够恢复的核心研发规模约为 7–8 人。一名学硕学长承担主要技术负责人和任务协调角色，并把我带入项目。现有材料不足以把他定义成 CTO、总架构师或合同负责人，也不足以恢复每个方向的正式 Owner。

团队涉及 Agent、Knowledge / Retrieval、法律智能能力、Memory / Context、Tool Integration、后端、前端、测试和部署等方向。成员会跨越算法、Agent、知识、后端和业务联调边界。

目前可以明确描述的个人参与包括：部分 Agent 开发；Memory 相关第一批重要工作；OpenViking 在 Memory / Context 区域的接入；Tool Calling Strategy 相关开发；以及进入数据库查看或调试实际数据。公开 Git 历史后来还恢复出更具体的 Tool/MCP、GraphRAG retrieval quality 和 Context/Memory V2 个人提交链，但这些都不能扩成“完整 Agent Runtime、整个 GraphRAG、全部 RAG 或整个后端都是个人独立实现”。

今天仓库里的总体架构、九模块文档、ADR 和治理经过后续系统化整理。这能够证明今天对整套 Target Architecture 的理解和维护能力，但不能倒推“2026 年 3 月加入时就是总体架构历史 Owner”。

## 今天能够相信什么

**History** 记录项目为什么出现、经历过什么、谁参与过什么。客户侧 Demo、回答质量反馈、Court-side Testing、Pilot Validation、OpenViking 接入等属于这一层。

**Current** 只表示今天 `main` 能由代码、Migration、Test、Trace、Eval 或真实运行证明的事实。目录和设计文档存在不等于九模块 Target 已实现，更不等于 Production Ready。Current 的具体边界必须回到 [`docs/evidence/`](../evidence/README.md)。

Current Evidence 同时保存正向通过和负向故障，但每条结论都必须绑定具体代码快照、测试形状和适用范围。负向 probe 可以证明某个 Target invariant 当时没有成立；后续同类 regression 转绿，只能关闭被覆盖的故障窗口。main 继续变化以后，旧 baseline 进入 History，最新 Current 由 Evidence 重新推进。Project 不复制每个修复波次，避免项目叙事随着实现节奏不断腐烂。

**Target** 表示今天接受的目标设计和产品方向，例如九个逻辑责任域、Knowledge Readiness、Capability Qualification、Single Controller、Formal Admission、Effect Recovery、Continuous Authorization，以及案件研究工作空间。Target 规定未来实现怎样收敛，不能被用来声称历史 Pilot 已经拥有同样机制。

**Evidence** 回答“这句话凭什么现在可以说”。实现存在、一次测试通过、一个 smoke 结果或一次 Pilot 经历都只能支持各自覆盖的结论；它们不能自动升级成整体质量、普遍收益或 Production Qualification。架构机制是否值得长期保留，还需要 09 Evaluation 在可比较任务、数据和成本条件下建立测量证据。

**Unknown / Measurement Needed** 包括历史第一版正式产品名称、完整法院名单、客户质量问题根因和修复指标、Pilot 真实用户量与运行数据、历史 QPS / Latency / Cost / HA / DR、完整 Production Qualification，以及多数复杂机制在真实法律任务上的增量价值。不知道的事情保持不知道，是项目叙事可信度的一部分。

更严格的事实台账由 [`docs/governance/project-fact-provenance.md`](../governance/project-fact-provenance.md) 维护。总体 Target Architecture 见 [`docs/architecture/architecture.md`](../architecture/architecture.md)，九个责任域见 [`docs/modules/`](../modules/README.md)，实际实现边界继续由 [`docs/evidence/`](../evidence/README.md) 回答。
