# Memory & Information Extraction QA

> Architecture Verification Corpus；不是 canonical architecture。答案只从正式 Target 架构文档重生成。

### Interview Drill Chain 21：Q233–Q267

从任务理解进入信息抽取，再进入记忆治理、时态、来源、安全、召回和评测。

## Q233 为什么需要 TaskUnderstandingSnapshot？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: TaskUnderstandingSnapshot、Memory、Agent Core
- architecture_refs:
  - docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么需要 TaskUnderstandingSnapshot？

### 他真正想考什么

是否把用户输入理解、规划和记忆写入区分开。

### 30 秒回答

它把自然语言输入规范化为可审计的目标、约束、上下文需求和未解决歧义，作为 Planning 的输入；它不是 Memory，也不是授权结论。

### 深挖回答

模型只提出 Proposal，Agent Core 在引用解析和边界校验后提交 Snapshot。

### 可能继续追问

1. Snapshot 至少包含哪些字段？
2. 未解决歧义由谁处理？

### Architecture Evidence

- docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q234 TaskUnderstandingSnapshot 至少描述什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Task Contract、Context Need、Risk
- architecture_refs:
  - docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

TaskUnderstandingSnapshot 至少描述什么？

### 他真正想考什么

是否能把任务理解落到字段。

### 30 秒回答

包括 Task Type、Target/Entity、Goal、Constraint、Output Requirement、Context/Knowledge/Memory Need、Potential Action Need、Risk/Assurance、Language Context 和 Unresolved Ambiguity。

### 深挖回答

字段分别服务计划、检索、记忆召回、动作准备和人工澄清；不保存隐藏思维链，也不自行推断权限。

### 可能继续追问

1. 为什么要记录 Memory Need？
2. 哪些变化触发新 GoalVersion？

### Architecture Evidence

- docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q235 TaskUnderstandingProposal 与 Snapshot 有什么区别？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Proposal、Deterministic Validation、Owner
- architecture_refs:
  - docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

TaskUnderstandingProposal 与 Snapshot 有什么区别？

### 他真正想考什么

是否坚持模型提议、确定性 Owner 提交。

### 30 秒回答

Proposal 是理解假设；Snapshot 是 Agent Core 完成引用解析、歧义和边界校验后提交的任务理解事实。

### 深挖回答

Proposal 不能直接驱动计划或扩大权限；歧义未解决时应 Clarify 或等待用户。

### 可能继续追问

1. 为什么不让模型直接输出 TaskContract？
2. 这与 MemoryCandidate 有何共同原则？

### Architecture Evidence

- docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q236 “供应商第三版合同”如何被理解？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Legal Reference Resolution、Review、Redline
- architecture_refs:
  - docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot
  - docs/project/architecture/architecture.md — § 8.3.1 从输入理解到 Memory Context 的统一链
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

“看供应商第三版合同，重点责任限制有没有按上次改，没改给建议”如何被理解？

### 他真正想考什么

是否能把自然语言引用解析成可执行但不越权的目标。

### 30 秒回答

快照应解析 Vendor A/Contract V3、Liability 主题、上次 Review/Redline、当前合同加上次 Finding/Playbook/相关 Memory，输出 Finding 与 Redline，并要求证据绑定和人工审阅。

### 深挖回答

Matter、Contract、Tenant、Workspace 和 Epoch 由各自 Owner 确认；模型不能自行选择跨事项对象。

### 可能继续追问

1. 两个合同都叫第三版怎么办？
2. 上次 Review 被撤销后还能直接使用吗？

### Architecture Evidence

- docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot
- docs/project/architecture/architecture.md — § 8.3.1 从输入理解到 Memory Context 的统一链

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q237 未解决的任务歧义应该怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Ambiguity、Clarification、User Input
- architecture_refs:
  - docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

未解决的任务歧义应该怎么办？

### 他真正想考什么

是否避免模型静默猜测目标或授权。

### 30 秒回答

保留 Unresolved Ambiguity，进入用户澄清或受治理的 Clarification；不能把猜测写成 Snapshot，更不能据此执行高风险动作。

### 深挖回答

目标、约束或输出契约实质变化才创建新 GoalVersion；普通补充材料不应制造新目标。

### 可能继续追问

1. 什么是 Supplemental Input？
2. 为什么不能用旧 Memory 自动补全？

### Architecture Evidence

- docs/project/modules/06-agent-core-planning-control.md — § 1.5.1 用户到底想完成什么：TaskUnderstandingSnapshot

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q238 为什么信息抽取和 Memory Write 必须分开？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Information Extraction、Memory Write、Governance
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.2 为什么抽取出一个事实后不能直接写进长期记忆？
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么信息抽取和 Memory Write 必须分开？

### 他真正想考什么

是否理解观察、候选和长期事实的不同信任级别。

### 30 秒回答

抽取只回答来源观察到了什么，写入还要判断价值、权限、范围、时间、冲突、来源和保留策略。

### 深挖回答

必须经过 Source Pin、Security、Schema、Entity、Temporal、Provenance 和 Uncertainty Validation，再进入 StructuredObservation 与 Capture Governance。

### 可能继续追问

1. 哪些步骤适合弱模型？
2. 什么结果只留在 Session？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.2 为什么抽取出一个事实后不能直接写进长期记忆？

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q239 StructuredObservation 是什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: StructuredObservation、Session、Candidate
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.3 结构化观察：写入前的中间事实层
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

StructuredObservation 是什么？

### 他真正想考什么

是否识别长期记忆写入前的中间层。

### 30 秒回答

它是经过 Schema、来源和安全校验的结构化观察，不是 Active MemoryVersion；它服务 Session Continuity、Long-term Capture 和 Context Construction。

### 深挖回答

它仍需 Capture Policy 和 Governance 才能形成长期候选，不能被当作企业知识、授权或最终法律结论。

### 可能继续追问

1. 它和 Knowledge Entity 有何边界？
2. 它能否直接进入 Context？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.3 结构化观察：写入前的中间事实层

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q240 StructuredObservation 支持哪些类型？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Observation Schema、Event、Opinion、Correction
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.3 结构化观察：写入前的中间事实层
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

StructuredObservation 支持哪些类型？

### 他真正想考什么

是否区分事实、事件、意见、承诺和纠正。

### 30 秒回答

包括 ENTITY_FACT、EVENT、RELATION、PREFERENCE、CONSTRAINT、DECISION、COMMITMENT、TODO、OPINION 和 CORRECTION。

### 深挖回答

类型决定后续 Capture、冲突和时态处理；“方案可以”是 OPINION，不应自动变成正式批准的 DECISION。

### 可能继续追问

1. 为什么需要 CORRECTION？
2. TODO 与 Commitment 的边界是什么？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.3 结构化观察：写入前的中间事实层

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q241 信息抽取的规范链是什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Extraction Pipeline、Provenance、Temporal
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.2 为什么抽取出一个事实后不能直接写进长期记忆？
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

信息抽取的规范链是什么？

### 他真正想考什么

是否能说出输入、校验、来源和不确定性。

### 30 秒回答

Source Fact 经 Source Range/Version Pin 和 Security Pre-filter 后，经过 ExtractionProposal、Schema、Entity、Temporal、Provenance、Confidence/Uncertainty Validation，形成 StructuredObservation。

### 深挖回答

来源绑定缺失、时间不能规范化或 Scope 无法确定时，不能进入长期候选。

### 可能继续追问

1. 哪些环节必须确定性？
2. 抽取失败是否等于整个 Review 失败？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.2 为什么抽取出一个事实后不能直接写进长期记忆？

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q242 为什么普通抽取不默认使用最强模型？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L5
- interview_probability: MEDIUM
- resume_trigger: Model Role、Cost、Extraction
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 10.2 记忆抽取的三个实现层次
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么普通抽取不默认使用最强模型？

### 他真正想考什么

是否能把模型选择与任务复杂度、成本和可验证性绑定。

### 30 秒回答

普通字段和事件可由弱模型提出，复杂关系、跨段冲突和歧义才升级强模型；确定性组件始终负责边界和提交。

### 深挖回答

强模型也只能提出 Proposal，不能获得 Governance、授权或 Version 提交权。

### 可能继续追问

1. 什么情况算复杂关系？
2. 强模型输出如何评测？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 10.2 记忆抽取的三个实现层次

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q243 哪些抽取步骤必须确定性？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Deterministic Component、Hash、Scope
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.2 为什么抽取出一个事实后不能直接写进长期记忆？
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

哪些抽取步骤必须确定性？

### 他真正想考什么

是否知道模型不能拥有系统边界。

### 30 秒回答

Schema、日期、ID、Scope、Hash、Source Binding、Permission、Dedup 和状态迁移必须由确定性组件校验。

### 深挖回答

模型可以提供实体或关系候选，但不能决定 Tenant、权限、覆盖旧版本或删除传播是否完成。

### 可能继续追问

1. Entity Resolution 为什么不能完全交给模型？
2. Hash 在 Provenance 中证明什么？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.2 为什么抽取出一个事实后不能直接写进长期记忆？

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q244 02、03、05 和领域 Profile 如何分工？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Ownership、Ingestion、Knowledge、Memory
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.2 为什么抽取出一个事实后不能直接写进长期记忆？
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § Knowledge 与 Memory 为什么不能互相冒充
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

02、03、05 和领域 Profile 如何分工？

### 他真正想考什么

是否会因为“抽取”这个词新增重复模块。

### 30 秒回答

02 负责文档结构和 SourceSpan，03 负责 Knowledge Entity/Relation/Evidence，05 负责 StructuredObservation 与 Memory Governance，领域 Profile 只提供规则，不新增独立抽取模块。

### 深挖回答

06 还拥有 TaskUnderstandingSnapshot；每个 Owner 只提交自己的事实，消费者通过 Contract 引用。

### 可能继续追问

1. ToolObservation 进入 Memory 由谁先过滤？
2. Legal Clause Extraction 属于哪个边界？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.2 为什么抽取出一个事实后不能直接写进长期记忆？
- docs/project/modules/03-knowledge-agentic-graphrag.md — § Knowledge 与 Memory 为什么不能互相冒充

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q245 occurred_at、observed_at 和 recorded_at 有什么区别？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Temporal Semantics、Event、Observation
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.4 Event、Semantic Fact 和时间不是同一个概念
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

occurred_at、observed_at 和 recorded_at 有什么区别？

### 他真正想考什么

是否把事件发生、系统获知和写入时间混为一谈。

### 30 秒回答

occurred_at 是事件实际发生时间，observed_at 是系统获知时间，recorded_at 是 Observation 或 Memory 提交时间；三者可能不同。

### 深挖回答

法律和历史场景必须保留差异，以支持 As-of 查询、冲突判断和来源审计。

### 可能继续追问

1. valid_from/valid_to 表达什么？
2. 相对日期如何持久化？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.4 Event、Semantic Fact 和时间不是同一个概念

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q246 Event 和 Semantic Fact 如何配合？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Event、Semantic Memory、Validity
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.4 Event、Semantic Fact 和时间不是同一个概念
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Event 和 Semantic Fact 如何配合？

### 他真正想考什么

是否理解事件是变化证据，语义事实是带有效期的状态表达。

### 30 秒回答

Event 记录发生了什么，Semantic Fact 表示谓词在 Scope 和有效时间内成立；新事件可以产生新 Fact 版本，但不能抹掉旧事件。

### 深挖回答

Event 不等于 Episodic Memory，事件经历也必须经过 Capture 和 Governance 才能长期复用。

### 可能继续追问

1. 同一事实的两个来源如何处理？
2. 什么情况应进入 Conflict？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.4 Event、Semantic Fact 和时间不是同一个概念

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q247 “离开南京 A、现在杭州 B”如何写入？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Temporal Succession、Supersede、Employer
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.4 Event、Semantic Fact 和时间不是同一个概念
  - docs/project/modules/05-memory-context.md — § 27.2 MemoryVersion 的失效与处置状态必须区分
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

“离开南京 A、现在杭州 B”如何写入？

### 他真正想考什么

是否会错误覆盖历史事实。

### 30 秒回答

抽取离开 A 和加入 B 两个事件，按约 2026-07 规范化；A 的 Fact 设置 valid_to，B 创建新的 valid_from，保留旧版本和 lineage。

### 深挖回答

用户在 8 月 11 日说出它只决定 observed_at，不把观察时间误当发生时间；历史 Review 仍可读取 A。

### 可能继续追问

1. “现在在杭州”能否推断已离开 A？
2. 不同来源时间冲突怎么办？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.4 Event、Semantic Fact 和时间不是同一个概念
- docs/project/modules/05-memory-context.md — § 27.2 MemoryVersion 的失效与处置状态必须区分

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q248 Memory Capture Policy 看哪些因素？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Capture Policy、Utility、Sensitivity
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.5 Memory Capture Policy 决定观察的去向
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Memory Capture Policy 看哪些因素？

### 他真正想考什么

是否知道长期记忆不是“模型觉得有用就保存”。

### 30 秒回答

看显式请求、Future Utility、稳定性、Authority、可重建性、敏感度、Scope、预期寿命、冲突风险和 Retention Policy。

### 深挖回答

这些因素共同决定留在 Session、创建 Candidate、只保留引用、拒绝存储、要求确认还是安全阻断。

### 可能继续追问

1. “未来可能有用”为什么不够？
2. Knowledge 正文是否应复制进 Memory？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.5 Memory Capture Policy 决定观察的去向

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q249 Capture Policy 的六种结果如何解释？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: KEEP_SESSION_ONLY、CREATE_CANDIDATE、Security
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.5 Memory Capture Policy 决定观察的去向
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Capture Policy 的六种结果如何解释？

### 他真正想考什么

是否能把策略落成可观测结果。

### 30 秒回答

结果是 KEEP_SESSION_ONLY、CREATE_CANDIDATE、REFERENCE_ONLY、DO_NOT_STORE、REQUIRE_CONFIRMATION 和 SECURITY_BLOCKED。

### 深挖回答

CREATE_CANDIDATE 仍要经过写入门、治理和版本提交，不等于已有 Active Memory。

### 可能继续追问

1. REQUIRE_CONFIRMATION 与 Governance 有何关系？
2. SECURITY_BLOCKED 能否进入普通 Context？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.5 Memory Capture Policy 决定观察的去向

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q250 显式要求“记住”是否一定能写入长期 Memory？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Explicit User Request、Consent、Security
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.5 Memory Capture Policy 决定观察的去向
  - docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

显式要求“记住”是否一定能写入长期 Memory？

### 他真正想考什么

是否把用户意图误当成绕过安全和保留策略的授权。

### 30 秒回答

不是。显式请求是重要信号，但仍需 Scope、Sensitivity、Consent、Retention、Conflict 和 Security Epoch 校验。

### 深挖回答

用户不能要求跨 Tenant 保存、绕过删除政策，或把不可信文档指令升级成 Procedural Memory。

### 可能继续追问

1. 用户同意与组织策略冲突谁收紧？
2. 失败原因是否应可解释？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.5 Memory Capture Policy 决定观察的去向
- docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q251 Event、Episodic、Semantic、Procedural 如何区分？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Memory Kinds、Event、Procedural
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 5.4 Event、Semantic Fact 和时间不是同一个概念
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Event、Episodic、Semantic、Procedural 如何区分？

### 他真正想考什么

是否把事件语义和长期内容类型混为一套枚举。

### 30 秒回答

Event 是源事实的发生语义；Episodic 记经历，Semantic 记带范围和有效期的事实，Procedural 记经治理的策略提示。

### 深挖回答

Event 本身不等于长期 Memory；三种长期类型都须经过 Candidate、Governance 和 Version。

### 可能继续追问

1. 一次失败经验能否直接成为 Procedural？
2. Semantic Fact 的旧版本是否删除？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 5.4 Event、Semantic Fact 和时间不是同一个概念

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q252 为什么需要 MemoryWriteDecision？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: MemoryWriteDecision、Governance、Version
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27.1 MemoryWriteDecision：Governance 到 Version 的正式门
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么需要 MemoryWriteDecision？

### 他真正想考什么

是否能把治理通过和版本提交连接起来。

### 30 秒回答

它是 MemoryCandidate 到 MemoryVersion 的显式写入门，记录决定、理由、Policy、Epoch、Scope、Conflict、Dedup、Authority 和 Temporal 结果。

### 深挖回答

CREATE_VERSION 只允许创建不可变 Version，不代表 Projection、Activation 或 Serving 已完成。

### 可能继续追问

1. MemoryGovernanceDecision 与它是否重复？
2. 模型能否作为最终 reviewer？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27.1 MemoryWriteDecision：Governance 到 Version 的正式门

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q253 MemoryWriteDecision 必须记录哪些证据？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Decision Record、Epoch、Conflict
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27.1 MemoryWriteDecision：Governance 到 Version 的正式门
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

MemoryWriteDecision 必须记录哪些证据？

### 他真正想考什么

是否具备可审计和可重放的写入思维。

### 30 秒回答

至少记录 Candidate、Decision、Reason Codes、Policy Version、Security Epoch、Source Scope，以及 Conflict、Dedup、Authority 和 Temporal 的结果引用。

### 深挖回答

这些引用让后续 Revalidation、审计、纠错和 Eval 能解释当时为什么允许或拒绝。

### 可能继续追问

1. Epoch 变化后旧 Decision 是否仍有效？
2. 决策记录能否原地修改？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27.1 MemoryWriteDecision：Governance 到 Version 的正式门

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q254 ConflictType 为什么要分类？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Conflict、Dedup、Temporal
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 24.1 Conflict 不是覆盖
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

ConflictType 为什么要分类？

### 他真正想考什么

是否知道重复、演化、权限冲突和事实矛盾不能用同一个动作处理。

### 30 秒回答

Exact Duplicate 可 Dedup，Temporal Succession 可新版本接替，Authority/Scope Conflict 可能 Quarantine，Direct Contradiction 需要解析或确认。

### 深挖回答

因此先按 ConflictType，再应用 AuthorityRule、TemporalRule 和 ScopeRule；不能用最后写入者覆盖。

### 可能继续追问

1. Near Duplicate 是否一定删除？
2. Preference Change 与企业政策冲突如何处理？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 24.1 Conflict 不是覆盖

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q255 为什么不能背诵 User > Memory > Knowledge？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Authority、Knowledge、Memory
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § Knowledge 与 Memory 为什么不能互相冒充
  - docs/project/modules/05-memory-context.md — § 24.1 Conflict 不是覆盖
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么不能背诵 User > Memory > Knowledge？

### 他真正想考什么

是否按事实类型、权威、时间和范围解决冲突。

### 30 秒回答

当前用户意图可以覆盖旧偏好，但用户 Assertion 不能覆盖有版本的 Playbook；合同当前证据也不能被旧 Memory 概括替代。

### 深挖回答

Knowledge、Memory 和 User Input 有不同 Authority、Freshness、Applicability、Permission 和 Version，必须按 Domain 规则评估。

### 可能继续追问

1. 用户说公司规则已改变时怎么办？
2. Memory 可以保存 Knowledge 的什么内容？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § Knowledge 与 Memory 为什么不能互相冒充
- docs/project/modules/05-memory-context.md — § 24.1 Conflict 不是覆盖

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q256 STALE 和 SUPERSEDED 有什么区别？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Stale、Supersede、Validity
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27.2 MemoryVersion 的失效与处置状态必须区分
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

STALE 和 SUPERSEDED 有什么区别？

### 他真正想考什么

是否能区分可能过时和明确被新版本接替。

### 30 秒回答

STALE 表示需要重新验证、保留历史价值；SUPERSEDED 表示已有明确新版本接替。二者都不能无条件当作当前事实。

### 深挖回答

历史 Review 可引用旧版本，但默认召回必须遵守有效时间、Scope 和当前 Policy。

### 可能继续追问

1. STALE 是否必须删除？
2. valid_to 与 STALE 如何配合？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27.2 MemoryVersion 的失效与处置状态必须区分

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q257 DORMANT 和 DELETED 为什么不能混同？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Dormant、Utility、Privacy Delete
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27.2 MemoryVersion 的失效与处置状态必须区分
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

DORMANT 和 DELETED 为什么不能混同？

### 他真正想考什么

是否理解低 Utility 不等于错误或隐私删除。

### 30 秒回答

DORMANT 只是暂不主动召回，事实仍保留；DELETED 是按隐私、Retention 或法律请求执行删除。

### 深挖回答

DORMANT 可重新评估 Utility；DELETED 必须传播到 Canonical Row、Projection、Cache、Manifest 和可识别派生物。

### 可能继续追问

1. DORMANT 能否被显式查询？
2. Legal Hold 如何影响 DELETED？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27.2 MemoryVersion 的失效与处置状态必须区分

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q258 QUARANTINED 解决什么问题？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Quarantine、Conflict、Security
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27.2 MemoryVersion 的失效与处置状态必须区分
  - docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

QUARANTINED 解决什么问题？

### 他真正想考什么

是否知道不确定内容要隔离，而不是强行接受或删除。

### 30 秒回答

它用于安全、来源、冲突或质量疑点未解决的 Candidate/Version；隔离内容不得进入普通 Context 或影响 Tool 参数。

### 深挖回答

Quarantine 保留调查和审计所需 Provenance，但不代表事实有效，也不等于 Privacy Delete。

### 可能继续追问

1. 什么条件可以 Release？
2. Quarantined Memory 能否被普通召回？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27.2 MemoryVersion 的失效与处置状态必须区分
- docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q259 REVOKED 和 DELETED 的边界是什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Revocation、Delete、Consent
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 41.1 Memory Provenance 与来源失效传播
  - docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

REVOKED 和 DELETED 的边界是什么？

### 他真正想考什么

是否区分不可继续使用和应按政策清除。

### 30 秒回答

REVOKED 表示权限、Consent 或 Policy 不再允许使用；DELETED 表示执行隐私、Retention 或法律请求要求的逻辑/物理清除。

### 深挖回答

两者都停止正常服务，但 Delete 还必须传播到可识别派生 Projection 和 Cache，并受 Legal Hold 约束。

### 可能继续追问

1. Revoke 后历史 Audit 是否删除？
2. Delete 传播失败如何处理？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 41.1 Memory Provenance 与来源失效传播
- docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q260 Memory 的 Provenance 最终要追到哪里？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Provenance、SourceFactRef、Hash
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 41.1 Memory Provenance 与来源失效传播
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Memory 的 Provenance 最终要追到哪里？

### 他真正想考什么

是否能回答这条记忆从哪里来、经过了什么处理。

### 30 秒回答

MemoryVersion → MemoryCandidate → StructuredObservation → SourceFactRef，再回到 ConversationMessage、DocumentVersion/SourceSpan、ToolObservation/EffectReceipt 或 AgentRun/RunOutcome。

### 深挖回答

还要保存 Extraction Model/Policy、Governance Decision、Content Hash、Security Epoch 和 Compression Trace。

### 可能继续追问

1. Vector Index 能否成为 Provenance 事实源？
2. 压缩表示如何回到原文？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 41.1 Memory Provenance 与来源失效传播

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q261 来源被删除后派生 Memory 怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Revalidation、Delete Derived、Privacy
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 41.1 Memory Provenance 与来源失效传播
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

来源被删除后派生 Memory 怎么办？

### 他真正想考什么

是否理解删除传播和派生数据治理。

### 30 秒回答

来源删除、撤销、隔离或 Scope 改变时，派生 Memory 必须进入 Revalidation，结果可能是保持、Stale、Quarantine、Revoke、Delete Derived 或 Supersede。

### 深挖回答

Privacy Delete 不能只删 Canonical Row，还要处理 Vector、Graph、Lexical、Cache、Manifest 和可识别 Context Artifact；流程必须幂等、可审计、可恢复。

### 可能继续追问

1. Legal Hold 会不会阻止删除？
2. Revalidation 期间能否默认召回？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 41.1 Memory Provenance 与来源失效传播

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q262 Knowledge 和 Memory 的核心边界是什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Knowledge、Memory、Authority
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § Knowledge 与 Memory 为什么不能互相冒充
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Knowledge 和 Memory 的核心边界是什么？

### 他真正想考什么

是否知道企业权威内容和历史上下文不是同一事实源。

### 30 秒回答

Knowledge 拥有企业权威内容、版本和 Evidence；Memory 拥有用户、事项、会话和 Agent 的历史上下文，可引用但不能复制或替代 Knowledge。

### 深挖回答

法律场景还要区分 Matter Evidence、Enterprise Policy Evidence 和 Legal Authority Evidence。

### 可能继续追问

1. 用户说法能否覆盖 Playbook？
2. 为什么 Memory 需要 Knowledge Snapshot 引用？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § Knowledge 与 Memory 为什么不能互相冒充

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q263 knowledge_evidence_ref 能解决什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: knowledge_evidence_ref、Snapshot、Revalidation
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § Knowledge 与 Memory 为什么不能互相冒充
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

knowledge_evidence_ref 能解决什么？

### 他真正想考什么

是否用引用保持边界，而不是复制 Knowledge 正文。

### 30 秒回答

它记录过去使用过的 Knowledge Evidence/Snapshot，帮助追溯和重新验证，但不把 Memory 变成法律权威，也不允许脱离权限继续使用。

### 深挖回答

Evidence 被替代、撤销、删除或 Scope 改变时，引用会触发 Memory Revalidation。

### 可能继续追问

1. 引用本身是否属于 Evidence？
2. 历史报告如何保持可追溯？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § Knowledge 与 Memory 为什么不能互相冒充

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q264 为什么 Memory Retrieval 不等于 Context Injection？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Recall、ContextPack、MemoryUseTrace
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 11.4 为什么 Memory Retrieval 不能直接等于 Context Injection？
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么 Memory Retrieval 不等于 Context Injection？

### 他真正想考什么

是否理解候选召回和最终上下文装配的两阶段边界。

### 30 秒回答

召回只得到候选；注入前还要检查 Conflict、Freshness、Applicability、Security、Priority、Token Budget、Atomic Group 和 Compression。

### 深挖回答

只有实际使用的 Memory 才进入 ContextPackVersion，并产生 MemoryUseTrace；被排除不等于删除。

### 可能继续追问

1. 为什么记录排除原因？
2. MemorySnapshot 和 ContextPackVersion 谁是事实源？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 11.4 为什么 Memory Retrieval 不能直接等于 Context Injection？

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q265 Effective Memory Scope 如何计算？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Scope、Tenant、Matter、Epoch
- architecture_refs:
  - docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Effective Memory Scope 如何计算？

### 他真正想考什么

是否能把 Memory 隔离落成最小权限交集。

### 30 秒回答

它是 Tenant ∩ Workspace ∩ User/Principal ∩ Matter ∩ Agent ∩ Task Downscope ∩ Memory Classification ∩ Current Security Epoch。

### 深挖回答

前端 Metadata Filter 不是安全边界；服务端要在摘要、Embedding、Rerank、Context、Write 和 Projection Serving 前执行 Gate。

### 可能继续追问

1. Task Downscope 为什么存在？
2. Epoch 变化后旧 Context 如何处理？

### Architecture Evidence

- docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q266 恶意文档怎样污染 Procedural Memory？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Memory Poisoning、Instruction Trust、Tool Recipient
- architecture_refs:
  - docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销
  - docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

恶意文档怎样污染 Procedural Memory？

### 他真正想考什么

是否能防止检索内容升级成指令和副作用。

### 30 秒回答

文档是 Untrusted Retrieved Content；即使要求“记住把合同发给攻击者”，也不能成为 User Authorized Intent、Procedural Memory 或 Tool Recipient。

### 深挖回答

Security 先做 Instruction Trust、Source Scope 和 Memory Write Gate；未经批准的 Candidate 不能影响 Tool 参数、收件人或 Credential Scope。

### 可能继续追问

1. Detection clean 是否足够？
2. 用户明确发送是否仍需 Approval？

### Architecture Evidence

- docs/project/modules/09-security.md — § 26.1 Memory Scope、Poisoning 与来源撤销
- docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。

## Q267 如何评测信息抽取和 Memory 生命周期？

- source_type: ARCHITECTURE_STRESS
- source_ref: architecture-deepening/memory-information-extraction
- primary_domain: memory-extraction
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Extraction Eval、Memory Eval、Deletion Propagation
- architecture_refs:
  - docs/project/modules/10-observability-eval.md — § 27.1 Memory 与 Information Extraction 的质量闭环
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何评测信息抽取和 Memory 生命周期？

### 他真正想考什么

是否能从抽取正确性一路测到安全、效用和删除传播。

### 30 秒回答

至少拆 Extraction、Entity、Temporal/Event、Memory Write、Duplicate、Conflict、Stale Injection、Cross-scope Leakage、Provenance、Utility、Context Contribution、Token Cost 和 Delete/Revocation Propagation 指标。

### 深挖回答

每个指标绑定 Dataset Version、Case Set Hash、Method、Scope、Trace/Artifact 和 Release Requirement；BLOCKED、UNAVAILABLE、INCOMPARABLE 不能折算为零分或 PASS。

### 可能继续追问

1. 律师 Reject 能否直接进入训练集？
2. 删除传播失败属于什么恢复语义？

### Architecture Evidence

- docs/project/modules/10-observability-eval.md — § 26.1 Memory 与 Information Extraction 的质量闭环

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。
