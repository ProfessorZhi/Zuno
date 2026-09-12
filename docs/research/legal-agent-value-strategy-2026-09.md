# Zuno 法律智能产品化战略：从研究成果到可验证 Agent 系统

> status: research-strategy
> last_verified: 2026-09-12
> canonical_truth: no
> current_implementation_evidence: not-implied

Zuno 的长期价值不应建立在“拥有一个更复杂的 Agent Runtime”上。2025—2026 年，长周期 Agent、工具调用、沙箱、Subagent、持久会话、Context Management、MCP 与多 Agent 编排正在快速成为通用基础设施。OpenAI Agents API、Anthropic Managed Agents、Claude Agent SDK、Google ADK 等产品已经把这些能力向标准化和托管化推进。继续把主要研发投入放在 Generic Agent Harness，差异化会随着基础模型和平台进步而不断缩小。

Zuno 更有价值的方向，是把葛季栋 / LIPLAB 已有的法律智能研究转化成一套可被真实案件工作持续使用、校验和演进的专业能力体系。Agent 在其中承担任务组织、动态检索、工具选择、并行研究、上下文管理与恢复；法律专业中间结构、正式工作成果、评价标准和人工责任仍由 Zuno 自己定义。

从产品形态看，更合适的目标不是 Autonomous Judge，也不是通用 Chatbot，而是一个**可验证的案件研究与审理辅助工作空间**。系统把大量非结构化案件材料逐步转化为事件、争议焦点、证据关系、法律依据、类案与待核实问题；Agent 围绕这些结构组织研究；专业人员在明确来源和不确定性的前提下复核并形成正式工作成果。

## 葛季栋团队的研究资产应怎样进入产品

现有研究最重要的共同特征，是它们都在尝试把法律文本从“原始文档”转换成更接近专业判断的结构。产品化时应保留这种结构，而不是只保留某个模型的最终预测。

**案件事件与争议结构。** `Judicial Intelligent Assistant System: Extracting Events from Chinese Divorce Cases to Detect Disputes for the Judge` 将案件材料中的重点事件抽取、事件共指对齐与双方冲突识别连接起来。它最自然的产品化结果不是一个“离婚案件 Agent”，而是案件级事件时间线、争议焦点矩阵和冲突事实集合。具体模型可以被更强 LLM 或未来模型替换，事件、当事方、时间、来源、冲突关系这些专业结构应保持稳定。

**事实与法律依据之间的细粒度关系。** `Learning Fine-grained Fact-Article Correspondence in Legal Cases` 的价值不只是提高法条推荐指标，而是把“某条法律依据为什么与案件相关”落实到具体事实。进入 Zuno 后，这类关系可以成为 Fact–Article Map：每个法律主张能够追到支持它的事实和来源，每个关键事实也可以看到候选法律依据。它直接支撑引用解释、法律研究和后续人工复核。

**法条候选与可解释排序。** `Statute recommendation: Re-ranking statutes by modeling case-statute relation with interpretable hand-crafted features` 以及相关 statute recommendation 工作，可以转化为法律依据检索 Capability。Agent 不应把模型推荐的 Top-1 法条直接写进最终意见，而应把它作为可解释候选，再结合现行有效性、案件事实、专业规则与人工判断完成确认。

**复杂案件数据与能力边界。** `CMDL: A Large-Scale Chinese Multi-Defendant Legal Judgment Prediction Dataset` 的产品意义不应局限于训练一个判决预测器。多被告案件天然包含事实归属、行为关系、责任区分和整体案件级一致性问题。CMDL 可以帮助 Zuno 建立复杂案件 Task Class 与 case-level Eval，检验一个 Provider 在简单单主体案例上表现良好以后，是否仍有资格处理多主体复杂事项。

**法律大模型能力分层。** `LawBench` 将法律能力拆成知识记忆、理解与应用三个认知层，并覆盖多类任务。这种结构非常适合转化为 Zuno 的 Capability Qualification：新模型进入系统时不再只有“总体分数”，而是形成按任务类别划分的能力画像。事件抽取强、法条应用弱的模型可以只服务前者；一个新模型也不需要因为某项能力提高就自动替代所有旧 Provider。

**功能测试与失败模式。** `LJPCheck` 对 Zuno 的价值甚至高于“再增加一个法律 Benchmark”。它把软件工程中的功能测试思想带入法律 AI，说明 headline accuracy 不足以证明模型适合真实场景。Zuno 应沿用这一思想，把公平性、反事实一致性、事实扰动、复杂主体、引用可靠性、材料缺失、权限变化和恢复行为组织成长期 Regression Suite。模型升级、Prompt 调整、Retriever 更换或 Agent Harness 更新，都必须通过同一组功能测试，而不是只看平均分是否提高。

葛季栋团队早期在工作流、软件过程与协同方面的研究，可以提供长期任务、过程演化和恢复的概念背景，但没有证据表明今天 Zuno 的 `PlanVersion`、`Single Controller` 或某一 Runtime Contract 直接源自这些论文。产品叙事应保留这种边界。

## Agent 技术应放大研究能力，而不是覆盖研究能力

最新 Agent 技术最值得 Zuno 引入的部分，不是“更多 Agent 数量”，而是动态研究、上下文管理、工具标准化、长任务执行、受控并行和严格评价。

### Agentic Retrieval：从一次 Top-K 变成有目标的研究过程

传统 RAG 在请求开始时一次性检索若干 chunk，再把它们全部塞给模型。法律问题经常需要先识别争议焦点，再决定查哪些材料、法律依据和类案；新的检索结果还可能改变后续检索方向。

Agentic RAG 因此适合成为 Zuno 的默认复杂研究模式：Agent 先形成研究计划，再按问题缺口调用案件材料检索、法条检索、类案检索、事实—法条对应和证据关系查询工具；每轮读取结果以后检查覆盖是否充分，再决定继续检索、缩小范围或停止。2026 年针对韩国律师资格考试的 Agentic RAG 研究显示，迭代式法律工具调用可以显著优于 Naive RAG，但收益强烈依赖模型是否真正善于使用工具。这个结果对 Zuno 的直接启示是：**工具存在不等于模型具备使用资格，Agentic Search 也必须进入 Provider Qualification。**

### Context Engineering：案件知识保持在外部结构，模型按需读取

法律案件的材料规模、运行时长和历史版本都不适合依靠一个不断增长的 Context Window。当前 Agent 工程已经从 Prompt Engineering 转向 Context Engineering：把上下文视为有限资源，保留高信号内容，其余信息通过稳定引用和工具按需读取。

Zuno 应让模型看到“当前任务需要的最小充分上下文”，而不是“案件里所有可能相关的东西”。案件材料、事件时间线、争议焦点、证据候选、法条候选、人工决策和运行计划都应保存在外部持久结构中，模型通过引用、查询和专业工具 Just-in-Time 获取。长任务中的阶段性结论写成结构化 Artifact，而不是依靠 Conversation History 记住全部过程。

这也决定 Memory 的定位：Zuno 的高价值 Memory 不是无限保存聊天，而是保留对后续法律工作真正有用的结构化事实、用户决定、开放问题和任务进度。原始材料仍由材料系统管理，正式法律事实仍由 Domain 管理，Agent Memory 只保存有明确用途的工作上下文。

### Multi-Agent：只用于高价值、可并行的研究，不做常驻角色戏剧

多 Agent 在开放式研究和广度搜索上有明显价值，因为独立 Subagent 可以拥有各自 Context，分别搜索不同法律问题、法域、证据类别或类案，然后由主 Agent 汇总。Anthropic 的生产研究系统也表明，多 Agent 最适合高价值、信息量大、能够并行探索的任务，同时成本显著高于单 Agent；依赖关系强、必须共享大量上下文的任务并不适合简单拆成多个 Agent。

Zuno 因此不应默认建设永久存在的“律师 Agent、证据 Agent、法条 Agent、审判 Agent”角色。更合理的是临时 Subagent：当一个案件包含三个相对独立的争议焦点时，主 Agent 可以并行创建三个研究任务；当需要在不同法律来源中做广度搜索时，再按来源拆分。输出以结构化 Artifact 写回案件工作空间，Subagent 完成后即可释放。

多 Agent 的启用条件应进入预算与 Evaluation。若单 Agent + 并行 Tool Call 已经达到相同质量，则没有理由承担额外 Token、协调和失败面。

### Planner / Worker / Verifier：把自由探索限制在可验证边界内

长周期 Agent 的一个成熟趋势，是把任务规划、执行和验证分开。Zuno 可以采用轻量的 Planner–Worker–Verifier 模式，但这里的 Verifier 不应成为“另一个模型说同意”，而应优先使用可验证结构：引用是否真实存在、材料版本是否一致、法条是否当前有效、结论是否有支持证据、要求的人工判断是否完成、外部动作是否已经确认。

只有无法用确定规则评价的开放式专业质量，才交给模型 Judge 和人工 Reviewer。这样可以把 Agent 的自由度保留在研究和组织阶段，把正式业务边界保持在可审计规则和专业人员手中。

### Managed Harness / MCP / A2A：作为基础设施，不作为 Zuno 差异化

2026 年通用 Agent 平台正在提供长会话、自动 Context Compression、Subagent、沙箱、持久 Session、工具路由与恢复。Zuno 应把这些能力视为 Buy / Adopt 候选。只要通用 Harness 能满足可靠性和数据安全要求，就不应为了“自研 Agent”重复建设。

MCP 适合成为专业工具和数据查询的标准接口。案件材料检索、法条查询、类案检索、研究模型、内部知识库和允许的外围系统都可以通过明确权限的 Tool Surface 暴露。A2A 更适合未来确实需要与外部独立 Agent 系统协作时使用，不应因为协议流行就提前把内部模块改造成 Agent-to-Agent 网络。

### Containment：模型越强，越需要缩小可执行边界

Agent 能力提高以后，风险不只来自“模型会不会犯错”，还来自错误动作的影响范围。对法院相关数据和现实业务系统，Zuno 应优先使用沙箱、网络出口控制、最小权限、只读工具、Secret 隔离和高风险动作人工确认来限制 Blast Radius。模型 Prompt 和分类器属于辅助防线，不能代替环境层权限。

这意味着 Tool Runtime & Effects 的长期价值会随着 Agent 变强而增加，而不是减少：Agent 可以越来越自主地研究，但改变现实世界的能力必须比研究能力受到更严格的约束。

## 最有价值的产品形态：案件研究与审理辅助工作空间

研究资产与 Agent 技术结合以后，Zuno 可以围绕一个稳定的 Matter / Case Workspace 组织用户体验。这里的 Workspace 是产品视图，不自动引入新的 Domain Authority。

专业人员打开一个案件时，首先看到的不是聊天框，而是逐步形成的案件结构：材料清单及加工状态、事件时间线、当事方陈述之间的冲突、争议焦点、证据支持与反驳关系、事实—法条映射、候选法律依据、类案和仍未覆盖的问题。Agent 可以接受自然语言任务，但它操作的是这些专业结构。

例如“分析双方关于付款义务的主要争议并形成审查意见”可以被拆成：确认相关材料是否完整；抽取付款相关事件和主体；定位双方冲突陈述；检索支持每个陈述的证据；建立事实—法条候选关系；检索相关法条和类案；识别仍缺乏证据或法律依据的主张；形成带来源的候选分析；交给专业人员复核。人工修改以后形成正式 WorkProduct，后续新材料进入时只重新检查受影响的部分。

这种产品形态有三个重要优势。

第一，研究成果不会因为基础模型升级而失去价值。旧事件抽取模型可以被新 LLM 替换，但案件事件结构、争议焦点、事实—法条关系和 Eval 仍然存在。

第二，Agent 能力可以快速升级而不接管业务 Authority。更强的模型可以更好地规划、检索和组织分析，但正式结果仍然沿相同的人审与业务准入路径形成。

第三，系统天然产生可积累的数据资产。专业人员对候选事实、法条、证据关系和分析建议的接受、修改与拒绝，可以形成经过治理的反馈数据，用于 Regression、Provider Qualification 和后续研究。真正的长期壁垒由此从“某次模型效果”转向“真实法律任务结构 + 专业反馈 + Eval + Provenance”。

## 研究与产品之间应形成闭环，而不是单向技术转移

Zuno 最值得建设的长期机制，是 Research–Product Flywheel。

真实案件和 Pilot 先产生经过脱敏与治理的 Bad Case、人工修改和失败轨迹。Evaluation 将这些案例转化为新的任务集、功能测试和 Regression。研究团队据此判断问题来自材料处理、事件结构、检索、法律知识、模型推理还是 Agent Tool Use，再提出新的算法或数据方法。新的 Research Artifact 进入 Zuno 时先作为 Provider，与现有 baseline 在相同 Task Class 上比较；只有通过 Capability Qualification 才进入主路径。上线以后继续收集真实使用反馈，再回到 Evaluation。

```text
真实案件工作
→ 人工修改 / Bad Case / Failure Trace
→ Task Class + Functional Eval
→ Research Question
→ Research Artifact / New Model / New Retriever
→ Provider Qualification
→ Controlled Release
→ 真实案件工作
```

这条闭环能够最大化课题组与产品团队同时存在的优势。很多商业法律 AI 公司可以购买同样的基础模型和 Agent Framework，但很难复制长期积累的法律任务定义、专家标注、功能测试、失败数据和研究迭代能力。

## 评价体系必须直接对应业务价值

如果产品继续只报告 Accuracy、Recall、LLM Judge 分数或“完成了多少 Agent Step”，很容易再次停留在 Demo。Zuno 应把评价拆成五个层次。

**材料与检索质量**：关键材料覆盖率、Document-level mismatch、引用可定位率、无证据主张率、过期法律依据使用率。

**专业结构质量**：事件抽取与对齐、争议焦点覆盖、事实—法条对应、证据支持/反驳关系、复杂多主体案件一致性。

**Agent 行为质量**：任务成功率、工具选择正确率、必要检索覆盖、无效 Tool Call、平均 Token / Cost、长任务恢复成功率、不同 Trial 的稳定性。

**人工协作质量**：候选事实/法条/分析的接受率、平均修改量、人工复核时间、人工发现的严重遗漏、需要重新研究的比例。

**业务结果**：从材料进入到形成可复核工作成果的时间、因错误引用或材料遗漏导致的返工、外部重复动作、历史结果无法解释的事件数，以及 Pilot 中专业人员愿意持续使用的任务比例。

其中“人工节省多少时间、严重错误是否下降、专业人员是否更愿意采用”比单个模型分数更接近产品价值。没有这些测量，就不能声称 Agent 化或某篇论文的工程化已经实现价值最大化。

## Build / Buy / Extend / Defer

**Buy / Adopt：** Generic Agent Harness、长会话与持久执行、沙箱、MCP transport、基础 Tool Calling、模型 SDK、Queue、PostgreSQL、Object Store、Vector / Graph Store、Identity、Secret Manager、OpenTelemetry、通用 Eval Harness。

**Zuno Own：** 法律 Task Class、案件专业结构、Research Capability Contract、Provider Qualification、材料与证据 Provenance、事实—法条与争议关系、人工决策、正式 WorkProduct、法律任务 Regression Suite、失效传播、现实 Effect 的业务语义。

**Extend：** Agentic Retrieval、Matter-level Context Engineering、Citation / Coverage Verifier、专业 Tool Surface、受控 Subagent、模型路由与成本控制。这些能力应建立在通用 Harness 上，而不是重新发明底层 Agent Loop。

**Defer / Measurement-gated：** 常驻 Multi-Agent Team、全局 GraphRAG 默认路径、Reflection Loop、复杂长期 Memory、自研 Generic Native Runtime、A2A 内部微服务化。只有在相同任务和预算下稳定优于简单方案时才保留。

## 建议的产品化次序

第一阶段应聚焦一个能够完整利用既有研究资产、又容易由专业人员验证的高价值工作流。相比“自动判案”，**争议焦点与证据—法律依据审查**更适合作为主切口：风险更低，人工复核天然存在，也能同时利用事件抽取、冲突识别、事实—法条对应、法条推荐和类案检索。

第一版目标不是生成一篇漂亮长文，而是稳定产生案件事件时间线、争议焦点、证据支持矩阵、法律依据候选和未解决问题，并让专业人员能够逐项接受、修改和拒绝。

第二阶段引入 Agentic Research。Agent 围绕已识别争议焦点动态调用法律检索、类案、材料查询和专业 Capability，产生带覆盖说明的研究结果。多 Agent 只在争议焦点或检索方向能够独立并行时启用。

第三阶段建立研究—产品评价闭环。LawBench、LJPCheck、CMDL 与真实 Bad Case 共同形成 Qualification / Regression；新模型和新论文先进入 Shadow / Canary，再决定是否替换当前 Provider。

第四阶段才考虑更强的长期 Agent Runtime、跨系统协作和外部现实动作自动化。届时复杂度应由真实案件量、等待时间、失败恢复和外部集成需求证明，而不是由 Agent 技术趋势推动。

## Evidence Boundary

本文件是 2026-09 的 Research Strategy。它支持产品定位、Build / Buy 判断、研究转化路径和 Measurement Plan，不证明：

- 上述论文已经逐项进入 Zuno Current；
- Matter / Case Workspace 已经实现；
- Agentic RAG、Subagent 或 Managed Agent 已经完成集成；
- 某种 Agent 架构已经在 Zuno 上优于现有 baseline；
- Pilot 已达到 Production；
- 葛季栋团队的论文成果属于任何单个开发者的个人实现。

要把其中任何 Target 升级成 Current，仍然需要代码、Migration、测试、Trace、Eval 或真实运行证据。

## 主要外部依据

- Jidong Ge et al., *Learning Fine-grained Fact-Article Correspondence in Legal Cases*, IEEE/ACM TASLP, 2021.
- Chuanyi Li, Jidong Ge et al., *Statute recommendation: Re-ranking statutes by modeling case-statute relation with interpretable hand-crafted features*, Information Sciences, 2022.
- Yuan Zhang, Chuanyi Li, Yu Sheng, Jidong Ge, Bin Luo, *Judicial intelligent assistant system: Extracting events from Chinese divorce cases to detect disputes for the judge*, Expert Systems, 2024.
- Zhiwei Fei et al., *LawBench: Benchmarking Legal Knowledge of Large Language Models*, EMNLP 2024.
- Yuan Zhang et al., *LJPCheck: Functional Tests for Legal Judgment Prediction*, Findings of ACL 2024.
- Wanhong Huang et al., *CMDL: A Large-Scale Chinese Multi-Defendant Legal Judgment Prediction Dataset*, Findings of ACL 2024.
- Anthropic, *How we built our multi-agent research system*, 2025.
- Anthropic, *Effective context engineering for AI agents*, 2025.
- Anthropic, *Demystifying evals for AI agents*, 2026.
- Anthropic, *Harness design for long-running application development*, 2026.
- Anthropic, *Scaling Managed Agents: Decoupling the brain from the hands*, 2026.
- Anthropic, *How we contain Claude across products*, 2026.
- OpenAI, *The next evolution of the Agents SDK*, 2026; *Introducing the Agents API*, 2026.
- Google, Agent Development Kit / Agent protocol documentation, 2025–2026.
- *Agentic RAG for Legal Question Answering in Civil Law: Evidence From the Korean Bar Examination*, IEEE Access, 2026.
