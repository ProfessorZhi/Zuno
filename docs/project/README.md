<!--
status: canonical-project-narrative
canonical_question: Zuno 为什么存在、为什么值得建设、与通用平台相比多承担什么责任、项目怎样发展、参与者做过什么、哪些事实今天可以相信？
owner: Project Documentation Owner
source_boundary: 历史事实来自已确认项目回忆与公开背景；产品定位来自已接受 Target Architecture；Current 必须回到 docs/evidence；不得用今天的设计反写历史，也不得把设计差异写成已测优势
-->

# Zuno 项目：将智慧司法研究转化为可验证的法律智能工作系统

Zuno 是南京大学软件学院 LIPLAB 智慧司法研究与工程化背景下的法律智能 Agent 平台，面向天津法院智慧平台相关场景。项目的长期目标不是再提供一个能够生成法律文本的聊天入口，而是把案件材料、课题组研究成果、基础模型、专业人员判断和业务系统连接成一条可以持续运行、复核、评价和恢复的法律工作链。

这个定位决定了 Zuno 的价值不能只用“模型效果更好”或“Agent 更复杂”来解释。大模型、RAG、Tool Calling、长周期 Agent、Subagent、沙箱和通用工作流都在快速成为成熟平台提供的基础能力。真正需要长期建设的是另一层：**如何把已有法律智能研究转化为稳定的专业能力，如何证明这些能力适合当前任务，如何让 Agent 在案件工作中正确调用它们，以及如何把专业人员的最终判断和后续反馈重新转化为下一轮研究与工程证据。**

外部研究已经反复说明法律 AI 面临检索错配、材料覆盖不足、模型幻觉、错误引用、自动化偏见、不可追溯输出和责任归属等问题。相关领域证据整理在 [`docs/research/legal-ai-domain-problem-evidence.md`](../research/legal-ai-domain-problem-evidence.md)。这些研究只能说明领域约束客观存在，不能证明历史 Zuno 已经逐项遇到或解决了同样问题。

Zuno 自己的项目历史需要保持更严格的范围。当前能够确认系统经历过 Internal Demo、客户侧 / 智慧法院项目组 Demo、法院侧人员测试和 Pilot Validation；客户侧 Demo 曾留下“回答质量还需要提高”的反馈。现有材料仍不足以判断当时的质量问题究竟来自 Prompt、Retrieval、Model、Memory、Tool、引用还是数据处理，也没有恢复完整 Bad Case 和前后指标。今天的 Target Architecture 不能被用来反写当年的根因。

## 项目要解决的是研究能力进入长期法律工作的产品化条件

简单法律问答并不需要 Zuno 的全部复杂度。用户只问“合同第 8 条约定了什么”时，权限检查、材料读取、受控检索、引用和一次模型生成已经可能满足要求。真正改变系统性质的是任务开始承担长期专业责任以后出现的一组约束。

**材料不是静态知识库，而是持续变化的案件事实来源。** 一个事项可能同时包含起诉状、答辩材料、合同、补充协议、扫描附件、聊天记录和后续补交证据。文件上传成功只能证明材料到达；OCR、解析和索引完成也只能证明某种派生知识已经生成。系统还需要判断当前问题依赖的关键材料是否齐全，以及缺失部分是否可能改变结论。

这也是普通 RAG 的边界。Retriever 返回 Top-K，只能证明这次查询找到了这些内容，不能证明重要材料没有遗漏，更不能把 retrieval miss 写成“全案不存在”。法律文档之间结构相似，来源文档错配本身就是已被研究观察到的风险。Zuno 因此需要稳定材料身份、版本、来源、任务级就绪和可追溯引用，而不是把 Knowledge 简化成一个向量库。

**模型输出需要保持候选性质，直到专业责任真正建立。** 法律 AI 的错误经常具有高度可读性：事实表达流畅、引用格式正确，却可能引用错误案例、遗漏关键条件或把局部证据写成确定事实。检索、研究模型、LLM 和规则系统都可以生成候选事实、事件、证据和法律分析，但长期保存和继续流转的工作成果仍需要专业规则和必要的人审。

**正式结果必须能够解释形成依据。** 如果系统只保存最后一段答案，几周以后很难回答它使用了哪版材料、哪些来源支持了哪些主张、模型当时返回了什么、专业人员修改了什么、为什么最终采用这一版。新的证据进入以后，旧结论可以失去当前适用性，但历史上已经发生的判断和交付不能被覆盖。项目因此需要同时维护 Provenance、版本、人工决定和结果生命周期。

**研究原型与长期业务之间存在明确的工程转化层。** 论文通常证明某种方法在特定数据集和评价指标下有效；真实系统还必须处理稳定输入输出、Provider 替换、任务适用范围、权限、失败语义、恢复、成本和持续评价。Zuno 的重要职责之一，就是把“一个研究 Artifact”转换成“一个业务系统可以长期依赖的专业 Capability”，再决定哪个具体模型、规则或外部服务目前有资格实现它。

**长周期任务不能由最后一次模型调用代表。** 多材料分析可能持续几十分钟甚至跨越多次人工等待。期间会出现新材料、旧计算晚到、模型限流、服务重启、权限变化和计划调整。运行进度需要持久化和恢复，但 Runtime 的 `completed` 不能替代法律工作成果已经正式成立这一事实。

**一旦系统改变外部世界，网络错误会变成业务不确定性。** POST timeout 只说明本地没有拿到确定响应，远端可能尚未执行，也可能已经成功。如果按普通计算错误直接 Retry，就可能制造第二次业务动作。Zuno 因此需要把外部 Action、Attempt、现实结果和后续 Reconciliation 单独管理。

这些约束共同限定了 Zuno 的产品边界。普通 RAG 足以解决的任务继续保持简单；只有当任务跨越材料版本、专业判断、长期运行、正式结果和现实副作用时，更强的领域状态和恢复机制才有建设价值。

## 葛季栋 / LIPLAB 的研究资产应成为专业能力层，而不是论文展示区

Zuno 与一般法律 Agent 项目最有潜力形成差异的地方，不是框架选择，而是南京大学团队已经积累了一批能够描述法律问题内部结构的研究成果。它们不应以“论文模型 Demo”的形式彼此孤立，而应被工程化为案件工作空间中的稳定专业能力。

`Judicial intelligent assistant system: Extracting events from Chinese divorce cases to detect disputes for the judge` 将重点事件抽取、事件共指对齐和双方冲突识别连接起来。它说明法律材料可以从长文本逐步转化为事件、参与方、时间和冲突关系。Zuno 可以把这类能力进一步抽象成案件事件时间线和争议焦点结构。未来即使底层从传统模型换成更强 LLM，这些专业对象仍然成立。

`Learning Fine-grained Fact-Article Correspondence in Legal Cases` 的工程价值也不应停留在一个推荐指标。细粒度事实—法条对应可以成为案件分析中的 Fact–Article Map：一条法律依据对应哪些具体事实，一个关键事实又可能关联哪些法律规则。它既能提高检索的针对性，也为专业人员解释“为什么引用这条法律依据”提供结构化基础。

`Statute recommendation: Re-ranking statutes by modeling case-statute relation with interpretable hand-crafted features` 及相关法条推荐研究，可以形成独立的法律依据候选 Capability。Agent 可以调用它缩小检索范围，但推荐结果保持候选性质，还需要结合现行有效性、案件事实、适用条件和人工判断。

`LawBench` 的价值更适合进入模型与 Provider 的资格体系。它将法律能力拆成知识记忆、理解和应用三个层次，并覆盖多类任务。Zuno 因此没有必要寻找一个“全局最强模型”，而可以为不同 Task Class 建立能力画像：某个 Provider 可能适合信息抽取，但并不适合复杂法律适用；另一个模型可能适合法律研究，却因为数据外发政策不能服务某类案件。

`LJPCheck` 提供了更重要的方法论：一个模型在公开数据集上拥有高 Accuracy / F1，并不意味着真实法律行为已经可靠。功能测试可以暴露 headline metric 看不到的脆弱性。Zuno 应把这种思想扩展为长期 Regression Suite，对事实扰动、复杂主体、引用可靠性、材料缺失、权限变化和 Agent 恢复行为进行持续验证。

`CMDL` 则提醒系统不要用简单单主体任务代表复杂案件。多被告案件涉及事实归属、行为关系、责任区分和 case-level 一致性。它可以成为复杂 Task Class 和案件级评价的重要研究资产，而不是直接支持“自动判决”的产品宣传。

这些研究成果最终应该沿统一路径进入产品：

```text
Research Problem
→ Research Artifact / Dataset / Evaluation Method
→ Stable Legal Capability
→ Provider
→ Task-Class Qualification
→ Agent Tool / Skill
→ Human-reviewed WorkProduct
→ Production Feedback / Regression
```

中间任何一跳都不能靠论文分数自动成立。更完整的研究—产品转化方案见 [`docs/research/legal-agent-value-strategy-2026-09.md`](../research/legal-agent-value-strategy-2026-09.md)。

## 最新 Agent 技术最适合承担组织与执行，不适合成为法律 Authority

2025—2026 年 Agent 工程正在快速成熟。通用平台已经提供持久 Session、长周期运行、Context Compression、沙箱、Subagent、MCP Tool、Tracing 和 Agent Eval。OpenAI Agents API、Anthropic Managed Agents、Claude Agent SDK 和 Google ADK 都在强化这些基础能力。这意味着 Zuno 应更坚定地复用 Generic Harness，把研发重点放在法律 Task、Capability、Evaluation 和 Formal WorkProduct 上。

复杂法律研究可以利用 Agentic Retrieval。Agent 不再只执行一次 Top-K，而是根据争议焦点形成研究计划，按需调用案件材料查询、法条检索、类案检索、事实—法条对应和证据关系工具；每轮读取结果以后检查覆盖是否充分，再决定继续检索、改变方向或停止。2026 年法律 Agentic RAG 研究进一步说明，工具访问本身并不保证性能提升，模型是否真正会规划和使用这些工具需要单独评价。因此 Tool-use proficiency 应成为 Provider Qualification 的一部分，而不是默认能力。

Context Engineering 同样适合案件工作。模型的 Context Window 不应该成为案件数据库。原始材料、事件时间线、争议焦点、Evidence Candidate、人工判断和运行进度保存在外部结构中，Agent 只在当前步骤按需读取最小充分上下文。长任务产生的阶段性结论写成可引用 Artifact，而不是持续堆入 Conversation History。

Multi-Agent 的使用必须更加克制。并行 Agent 对开放式、可拆分研究很有价值，例如三个相互独立的争议焦点可以分别研究，或者法条、类案和事实来源可以并行搜索。但强依赖共享上下文的工作并不适合简单拆成多个永久角色，而且多 Agent 会显著增加 Token、协调和失败成本。因此 Zuno 更适合使用**临时 Subagent**，而不是建立常驻的“律师 Agent / 证据 Agent / 审判 Agent”角色体系。

Agent 安全也应依靠真实权限边界，而不是只靠 Prompt。法院相关数据和外围系统更适合采用沙箱、网络出口控制、最小权限、只读 Tool、Secret 隔离和高风险动作人工确认。模型越强，能够找到的行动路径越多，Tool Runtime & Effects 的受控边界反而越重要。

## 最有价值的产品形态是可验证的案件研究与审理辅助工作空间

如果 Zuno 继续以聊天框作为主要产品模型，课题组的大量研究成果最终仍会被压缩成一段模型输出。更能发挥研究资产价值的界面应当首先展示**案件结构**，自然语言 Agent 作为操作入口和研究协调者存在。

专业人员进入一个 Matter 时，可以逐步看到材料及加工状态、案件事件时间线、当事方陈述冲突、争议焦点、证据支持/反驳关系、事实—法条映射、候选法律依据、类案以及仍未覆盖的问题。Agent 接受“分析双方关于付款义务的争议并形成审查意见”后，不是直接生成长文，而是围绕这些专业结构完成一系列工作：确认材料是否足够，抽取相关事件，定位冲突陈述，检索支持与反驳证据，建立事实—法条候选关系，检索法律依据和类案，标记仍缺乏支持的主张，再形成带来源的候选分析。

专业人员可以逐项接受、修改或拒绝候选内容。正式采用后形成版本化 WorkProduct。后续新证据进入时，系统优先判断哪些事实、法律依据和结论受到影响，而不是默认整案重新生成。

这种产品形态能把研究成果和 Agent 技术同时转化成长期资产。基础模型升级以后，事件结构、争议焦点、证据关系和 Fact–Article Map 仍然存在；Agent Harness 替换以后，正式 WorkProduct 和人工决策仍然存在；新的研究模型进入以后，也可以在相同任务和 Evaluation 下与旧 Provider 对照，而不是重新发明产品流程。

## 真正的长期价值来自 Research–Product Feedback Loop

课题组和工程产品同时存在的最大优势，不是可以更快接入一篇新论文，而是可以形成稳定的研究—产品闭环。

真实案件、法院侧测试和 Pilot 会产生 Bad Case、专业人员修改、未覆盖问题和 Agent Failure Trace。经过数据治理以后，这些案例进入 Evaluation，形成新的 Task Class、功能测试和 Regression。研究团队由这些失败重新提出问题，开发新的 Retriever、模型、数据集或评测方法。新的 Research Artifact 作为 Provider 进入 Zuno，与当前 baseline 在相同数据、模型预算和业务条件下比较；通过 Qualification 后再进入 Shadow / Canary / 主路径。真实使用继续产生下一轮反馈。

```text
真实法律工作
→ 人工修改 / Bad Case / Failure Trace
→ Task Class + Functional Eval
→ Research Question
→ Research Artifact / New Model / New Retrieval
→ Provider Qualification
→ Controlled Release
→ 真实法律工作
```

这条闭环比“拥有某一个最强模型”更有持续价值。基础模型、Agent Framework 和通用 RAG 都可以买到；长期积累的法律任务定义、案件专业结构、专家修正、功能测试、失败数据和上线资格标准更难复制。

## 产品价值必须用真实工作结果评价

如果 Zuno 只报告 Accuracy、Recall、LLM Judge 或 Agent Step 数量，项目仍然可能停留在研究 Demo。未来的评价至少需要同时覆盖材料、专业结构、Agent 行为、人工协作和业务结果。

材料层关注关键材料覆盖率、来源错配、引用可定位率、无证据主张和失效法律依据；专业结构层关注事件和争议焦点覆盖、事实—法条对应、证据关系与复杂主体一致性；Agent 层关注任务成功率、工具选择、必要检索覆盖、无效 Tool Call、Token / Cost 和长任务恢复；人工层关注候选内容接受率、修改量、复核时间和严重遗漏；业务层最终关注形成可复核工作成果所需时间、因错误引用或遗漏导致的返工、重复外部动作和历史结果无法解释的事件。

最有价值的指标不是“Agent 做了多少事情”，而是**专业人员是否更快形成高质量、可复核的工作成果，同时系统是否减少严重遗漏、错误引用和不可恢复状态。** 在这些指标没有形成证据以前，任何“价值提升”都应继续写成 Target 或 Measurement Needed。

## 任务复杂度决定需要多少 Zuno

同一套法律责任可以落在不同产品形态，不存在“越原生越高级”的顺序。

**通用宿主 + 法律 Capability** 适合简单问答、轻量检索和少量专业工具。成熟 Agent Host 继续承担会话、页面、Generic Tool Calling 和基础工作流。

**通用宿主 + Zuno Legal Backend** 适合材料版本、案件结构、正式工作成果、Provider Qualification 和 Evaluation 已经成为产品要求，但长周期 Agent Runtime 仍可以由成熟平台承载的场景。这很可能是长期最经济的主形态。

**Zuno Native Runtime + 一等领域状态** 只在动态计划、长等待、复杂恢复、持续授权或领域级并发控制真正成为约束时才值得建设。随着通用 Agent Harness 快速成熟，这一层尤其需要持续接受 Build / Buy 复核。

GraphRAG、Reflection、Persistent Multi-Agent、长期 Memory 和 Native Runtime 都属于 Measurement-gated Complexity。已经实现只能证明代码存在；如果在相同任务、语料、模型和预算下不能持续优于更简单 baseline，就应缩小或删除。

## 项目真实走过的阶段

今天的产品化战略和 Target Architecture 不能用来反写历史。根据目前能够恢复的材料，项目历史更接近一条逐步工程化和验证的路径：

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

**加入项目时，系统已经存在。**

我约在 2026 年 3 月加入。加入时项目已经有代码和一个比较简单的自研前端，因此这不是 Greenfield 项目，项目前期产品方向和第一版系统也不能算作个人成果。历史第一条需求、最早提交、第一版正式产品名称和当时完整技术栈尚未恢复，今天 `main` 的目录与依赖不能自动成为历史版本说明。

**Internal Demo 说明产品链路进入内部验证。**

目前仍缺少该阶段的具体日期、参与人、环境、脚本和每项能力的完成程度，因此不能据此声称已经达到某个准确率或正式质量门槛。

**客户侧 Demo 暴露过回答质量问题。**

当前能够确认的反馈是“回答质量还需要提高”。现有材料不足以把根因直接归结到 Prompt、Retrieval、Model、Memory、Tool、引用或数据处理，也没有恢复前后准确率和完整 Bad Case。外部研究可以帮助我们提出合理的排查框架，却不能替代这段历史本身的取证。

**法院侧测试进入更真实的使用环境。**

实际用户能够暴露专业术语、材料表达、引用习惯、权限和工作流程问题，但测试题数量、参与法院、人员角色、参考答案、Reviewer 协议、环境和性能数据尚未恢复。

**Pilot Validation 仍属于试点。**

目前只能确认项目走到过 Pilot Validation，没有资料支持正式 Production、稳定用户规模、部署 Endpoint、SLA、QPS、Latency、Token、Cost、HA 或 DR。Pilot 最值得继续恢复的是参与人员、任务类型、运行时长、数据外发限制、真实故障、人工兜底和验收条件。

## 团队与个人参与的边界

目前能够恢复的核心研发规模约为 7–8 人。一名学硕学长承担主要技术负责人和任务协调角色，并把我带入项目。现有材料不足以把他定义成 CTO、总架构师或合同负责人，也不足以恢复每个方向的正式 Owner。

团队涉及 Agent、Knowledge / Retrieval、法律智能能力、Memory / Context、Tool Integration、后端、前端、测试和部署等方向。它更像研究成果工程化过程中形成的小型研发团队，成员会跨越算法、Agent、知识、后端和业务联调边界。

目前能够明确描述的个人参与包括：部分 Agent 开发；Memory 相关的第一批重要工作；OpenViking 在 Memory / Context 区域的接入；Tool Calling Strategy 相关开发；以及进入数据库查看或调试实际数据。开发期间也学习和接触过 LangGraph、GraphRAG，但这些事实不能推出完整 Agent Runtime、整个 GraphRAG、全部 RAG 或整个后端都是个人独立实现。

今天仓库里的总体架构、九模块文档、ADR 和文档治理经过后续系统化整理。这能够证明今天对整套 Target Architecture 的理解和维护能力，但不能倒推“2026 年 3 月加入时就是整套总体架构的历史 Owner”。

## 今天能够相信什么

**History** 记录项目为什么出现、经历过什么、谁参与过什么。客户侧 Demo、回答质量反馈、Pilot Validation、OpenViking 接入等属于这一层。

**Current** 只表示今天 `main` 能由代码、Migration、测试、Trace、Eval 或真实运行证明的事实。当前仓库已经存在 Python 后端、Web / API、Agent、Knowledge / Retrieval、Memory、Capability / Tool、数据库和测试入口，也存在部分运行与观测基础，但目录存在不等于九模块 Target 已完整实现，更不等于 Production Ready。Current 的具体边界必须回到 [`docs/evidence/`](../evidence/README.md)。

**Target** 表示今天接受的目标设计和产品化方向，例如九个逻辑责任域、Knowledge Readiness、Capability Qualification、Single Controller、Formal Admission、Effect Recovery、持续授权，以及本轮研究提出的案件研究与审理辅助工作空间。这些设计规定未来实现应该怎样收敛，却不能被用来声称历史 Pilot 已经拥有同样机制。

**Unknown** 表示目前还没有可靠证据。历史第一版正式产品名称和第一条需求原文、直接合同甲方、完整参与法院名单、历史完整权限模型、每篇论文具体进入哪个产品版本、客户质量问题的根因和修复指标、Pilot 的真实用户量与运行数据、历史 QPS / Latency / Cost / HA / DR，以及个人任务对应的具体 PR、接口、SQL、Bug 和测试闭环，都仍然属于 Unknown。

不知道的事情保持不知道，是项目叙事可信度的一部分。更严格的事实台账由 [`docs/governance/project-fact-provenance.md`](../governance/project-fact-provenance.md) 维护。

今天能够确认的是，Zuno 已经形成一套较完整的 Research-to-Engineering Target：Research Artifact 不直接等于 Capability，Capability 不直接等于某个 Provider，Provider 可用不代表对所有任务 qualified，机器输出成功也不代表正式业务事实成立。真正的产品优势仍然需要统一 Task Class、真实 Bad Case、专业人员评价和长期运行 Evidence 来证明。

下一阶段最有价值的工作，不是继续增加 Agent 术语，而是恢复和建立三个闭环：一到两个真实质量 Bad Case 的输入—根因—修改—回归；一到两个个人工程任务的需求—代码—测试—结果；以及 Pilot 的任务类型—使用方式—失败—人工兜底—验收条件。与此同时，应开始用统一数据集比较 Generic Host + Legal Capability、Generic Host + Zuno Legal Backend 和 Zuno Native Runtime 三种形态，对 Agentic Retrieval、GraphRAG、Memory、Subagent 和 Native Runtime 做消融。只有这样，研究战略才能逐步变成可证实的产品价值。

[`docs/architecture/architecture.md`](../architecture/architecture.md) 继续回答这些约束如何转化为系统责任，[`docs/modules/`](../modules/README.md) 把责任落实到九个逻辑域，[`docs/research/legal-agent-value-strategy-2026-09.md`](../research/legal-agent-value-strategy-2026-09.md) 保存本轮研究与产品化推导，今天实际实现了多少仍由 [`docs/evidence/`](../evidence/README.md) 回答。
