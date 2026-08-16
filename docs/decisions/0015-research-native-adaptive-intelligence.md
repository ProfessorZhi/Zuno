# ADR 0015：Research-Native Adaptive Intelligence

status: accepted-target
decision_date: 2026-08-16
scope: Zuno Target Architecture；02 / 03 / 04 / 05 / 06 / 07 / 08 / 09 与 Optional Context / Memory Provider Boundary
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
refines: ADR-0006、ADR-0007；不改变 ADR-0013 九模块 taxonomy、ADR-0014 authority / recovery 和 ADR-0008 七对象 Legal Domain Kernel
canonical_question: Zuno 怎样把智慧司法研究成果与 Agent / Retrieval / Memory / Tool 的先进论文机制变成可组合、可替换、可验证的产品能力，而不是论文代码、开源组件和模型的堆砌？

## Context

Zuno 的项目价值之一，是把 LIPLAB / 智慧司法研究资产工程化为长期可组合能力。但“论文里有一个算法”与“产品里有一个可依赖能力”之间存在明显鸿沟：研究代码通常针对固定数据集、固定案由和实验环境；通用 Agent 论文往往追求 benchmark success，却不负责法律材料版本、正式 Evidence / Finding、持续授权、现实副作用、崩溃恢复和人工准入。

另一方面，如果 Architecture 只强调 Ownership、Receipt、Recovery，而不吸收 Retrieval、Memory、Planning、Tool Use 和法律信息抽取近年的有效机制，Zuno 又会变成一套控制语义很完整、算法层却过于保守的平台。

本 ADR 因此选择第三条路：

> **研究机制进入 Zuno，但先被拆成稳定语义、受界算法 Primitive、可替换 Provider 和可重复 Eval；论文系统本身、论文指标和开源产品都不直接获得业务 Authority。**

## Research evidence boundary

本 ADR 使用研究论文回答“哪些机制值得进入 Target 候选”，不使用论文替 Zuno 声明 Current 或质量收益。

本轮高相关研究包括：

- Zhang, Li, Sheng, Ge & Luo (2024), *Judicial intelligent assistant system: Extracting events from Chinese divorce cases to detect disputes for the judge*, DOI `10.1111/exsy.13540`：TRL（Two-Round Labeling）事件抽取 → Event Alignment → Conflict Detection → Dispute Detection；其公开实验提供了离婚案件专项研究基线和明确局限。
- Zheng et al. (2024), DOI `10.1002/asi.24971`：多文档 QA 的 iterative decompose-solve-renewal 支持依赖感知的多跳拆解，而非一次性独立 subquery。
- Vuthoo et al. (2026), DOI `10.1111/exsy.70267`：法律合同 RAG 研究综述支持不同 RAG 复杂度对应不同任务 / 成本，不应 Always-On Agentic RAG。
- Santra et al. (2025), DOI `10.1002/widm.70021`：支持 sparse / dense / hybrid / rerank / self-reflective retrieval 的模块化组合。
- Guo & Han (2026), DOI `10.1049/csy2.70037`：其 adaptive routing 结果支持按 query complexity 调整 retrieval strategy 的方向。
- Huang et al. (2025), DOI `10.1002/sys.70012`：支持 GraphRAG 在关系密集问题上的条件价值，同时不支持“图一定全面优于 Hybrid”这种外推。
- Li & Wu (2025), DOI `10.1002/sdr.70008`：记忆中的 relevance / recency / importance 与 Prompt control 风险支持 typed memory policy 和受控 promotion。
- Lee & Park (2026), DOI `10.1002/sd.70942`：Agentic AI survey 支持 dynamic planning、working / long-term memory、tool feedback，同时强调 Reflection / ToT / retrieval 的资源成本。
- Bhat et al. (2025), DOI `10.1002/adrr.202500072`：closed-loop execution feedback 与 hierarchical planning 支持从真实执行状态驱动 replan，而不是 open-loop 盲跑。
- Xu et al. (2026), DOI `10.1002/advs.202524273`：propose-verify、tool-grounded evidence、domain constraint 和 uncertainty triage 支持模型建议 + 外部验证的企业 Agent 形态。
- Liu et al. (2024), DOI `10.1111/cgf.15093`：LLM 结构化工具输出仍需 format validation。
- Li et al. (2026), DOI `10.1049/itr2.70178`：Safety Shield 对 LLM candidate action 做显式过滤的思路支持 Tool / Security 的 deterministic guard。

论文年代、作者、实验数据属于外部 Research Evidence。它们进入代码前仍需原文、可复现实验、License / Dataset 和 Zuno 自有 Eval 再验证。

## Decision 1：形成 Research-to-Capability 主干

任何研究成果、论文模型、专利算法、Notebook、Prompt、GitHub Demo 或外部算法服务，默认经过：

```text
Research Artifact
→ Reproduction / Source Verification
→ Capability Semantics
→ CapabilityVersion
→ ProviderBinding
→ Conformance
→ Domain Eval
→ Eligibility
→ Runtime Planning
→ Proposal / Candidate
→ Human / Domain Admission when required
```

05 Capability & Skill 拥有专业语义与 Provider eligibility。研究代码“能运行”只证明 Provider spike，不证明 Capability quality；论文指标只证明特定实验条件下的研究结果。

当 Provider 换成 LLM、规则、专门 encoder 或研究模型，而输入、输出、证据要求、failure semantics 和 uncertainty contract 不变时，可以保持同一 CapabilityVersion；如果专业承诺发生变化，必须创建新的 CapabilityVersion。

## Decision 2：建立法律认知旗舰链，但不扩大 Canonical Domain Kernel

Zuno Target 把可组合法律认知链表达为：

```text
DocumentVersion + task scope
→ Knowledge Readiness
→ Legal Event / Fact Candidate Extraction
→ Event Coreference / Alignment
→ Contradiction / Entailment / Unknown
→ DisputeCandidate / IssueCandidate
→ Adaptive Evidence Retrieval
→ Similar-case / Statute / Rule Candidate
→ Fact–Rule / Evidence Applicability Analysis
→ FindingProposal
→ HumanDecision when required
→ Formal Admission
→ WorkProduct
```

`EventCandidate`、`AlignmentCandidate`、`ConflictCandidate`、`DisputeCandidate`、`IssueCandidate` 等默认属于 05 output / 03 projection / runtime intermediate，不因为名字有法律含义就进入 ADR-0008 七对象 Canonical Kernel。

只有当某个对象证明需要独立长期身份、业务生命周期、正式版本、失效传播和专业人工准入时，才允许提出 Domain Kernel 变更；那将是新的 Architecture Gap，而不是本 ADR 自动扩容。

## Decision 3：把 JIA / TRL 拆成 Capability Family，而不是复制旧系统

Zhang et al. (2024) 的 JIA 研究对 Zuno 最有价值的不是 TensorFlow / BiLSTM-CRF 本身，而是三个稳定算法思想：

1. 法律任务先定义可解释 Event Schema；
2. 针对多个事件共享 trigger / argument 的场景，用 Two-Round Labeling 降低直接大标签空间的稀疏性；
3. Event Extraction 后继续做 Alignment 和 Conflict Detection，争议焦点不是一段文本分类的黑盒结果。

因此 05 定义至少以下 Capability family candidate：

```text
LEGAL_EVENT_EXTRACTION
LEGAL_EVENT_ALIGNMENT
LEGAL_CONFLICT_DETECTION
LEGAL_DISPUTE_CANDIDATE_DETECTION
```

其中 `LEGAL_EVENT_EXTRACTION` 可以有：

```text
TRL_REFERENCE_PROVIDER
LEGAL_ENCODER_PROVIDER
LLM_STRUCTURED_EXTRACTION_PROVIDER
HYBRID_EVENT_EXTRACTION_PROVIDER
```

`TRL_REFERENCE_PROVIDER` 的作用是保留可复现实验基线和 shared-argument handling 语义，不意味着 2024 年具体模型永远是 production winner。

Hybrid Provider 可以吸收：candidate trigger / event-type detection、受 Event Schema 约束的结构化抽取、TRL-style shared argument normalization、规则化 Money / Polarity / Time 等字段校验、稳定 SourceSpan 回绑和不确定性输出。

Event Alignment / Conflict 不应退化为单个 LLM Prompt。确定性字段（主体、时间、金额、DocumentVersion、Polarity 等）优先规则 / typed comparison；语义冲突再交给 NLI / model proposal。最终输出仍是 Candidate。

论文报告的 F1、冲突检测和用户节时结果只记为 Research Baseline，不写成 Zuno Current 性能。

## Decision 4：03 升级为 Adaptive Multi-Route Retrieval，而不是“一个 GraphRAG”

详细约束由 ADR-0006 拥有。本 ADR 固化跨模块位置：

```text
Query Understanding
→ QueryClass / RetrievalIntent
→ Bounded parallel routes
   ├─ lexical / BM25
   ├─ dense semantic
   ├─ metadata / source-scoped
   ├─ entity / fact
   ├─ graph / multi-hop
   └─ temporal / authority / global when justified
→ RRF / calibrated fusion
→ rerank
→ EvidenceCandidate normalization
→ Evidence Sufficiency / Gain
→ stop / focused probe / dependency-aware decomposition
```

GraphRAG、HippoRAG-like associative graph retrieval、community/global synthesis 等都是 Provider / strategy family，不是产品 Identity。Graph route 只有在关系、多跳或 global corpus Query Class 的对照 Eval 中稳定获益时才获得 Eligibility。

复杂多文档问题吸收 DSRC-style iterative decomposition：后续 subquestion 允许根据前序 Evidence 和 accepted intermediate state 更新；独立子问题才最大化并行。

`EvidenceGain`、重复率、独立 SourceFamily、关键 Claim coverage、成本 / deadline 共同决定是否继续下一轮。Agentic Retrieval 必须有 stop condition。

## Decision 5：Optional Memory 升级为 Typed Memory Control Plane

Memory 不成为第十模块。ADR-0007 拥有详细 Provider 边界，本 ADR 固化与 Runtime / Security / Eval 的协同。

```text
Working Context        → 04 runtime scoped
Episodic Memory        → structured past task episodes
Semantic Memory        → validated reusable context
Procedural Memory      → validated reusable strategy / experience
Context Archive        → external provider may organize large history
```

写入路径：

```text
Run / Human Feedback / Final Reflection
→ MemoryCandidate
→ Source + Scope + Security + Freshness
→ Conflict / Duplicate / Supersession
→ MemoryWriteDecision
→ Provider
```

召回按 relevance + recency + importance + scope / task fit 等可审计 feature 排序，但结果只是 `ContextCandidate`。任何法律事实主张仍回 03 / 02 证据路径验证。

OpenViking、Graphiti、Mem0、LangMem 等只作为 Conditional Provider / baseline candidate，不在文档阶段宣布“最优解”。Provider 对比至少需要 accuracy / stale-memory error / context pollution / latency / token / cost / security / license / exit path。

## Decision 6：04 增加 Plan Quality Gate 和分层计划

LLM Planner 的输出不能因为 schema 合法就激活。Target 在 PlanVersion 激活前增加三层 progressive gate：

```text
Planner Proposal
→ Structure Gate
→ Feasibility Gate
→ Usefulness / Utility Gate
→ ACTIVATE immutable PlanVersion
```

### Structure Gate

检查 DAG、Step identity、dependency、输入 / 输出 ref、无环性、join、side-effect declaration、required capability 等结构可解析性。

### Feasibility Gate

检查 Readiness、Capability Eligibility、Tool Availability、Security、Budget、Quota、resource conflict、exclusive resource、side-effect precondition 和执行器能力边界。

### Usefulness / Utility Gate

检查每个 Step 是否对任务目标、Evidence Gap 或必要 WorkProduct 有明确贡献；如果一个 Step 只是重复检索、重复 Reflection 或昂贵图搜索而没有预期信息增益，可以在激活前删除 / 合并。

这种 `structure → feasibility → usefulness` 分层吸收了 task-planning 文献中对 LLM plan validity 的 progressive checks；它是工程 Guard，不要求模型自己给自己打分。

复杂法律计划进一步允许：

```text
Goal
→ Phase
→ Step
→ Action
```

Phase 可以用法律任务语义组织，例如 Issue / Evidence / Rule / Application / Synthesis，但这只是 Plan Template，不建立自治 Manager Agent。

## Decision 7：Execution Feedback 驱动 Retry / Replan，而不是 open-loop 规划

04 每个 Step 的 Observation 由真实 owner fact、Capability output、Tool receipt、Knowledge assessment 或 typed provider error形成。

```text
execution/provider failed but plan assumption valid → Retry / verified fallback
capability/input/dependency assumption invalid       → Replan
external effect reality unknown                     → Reconcile
quality / evidence acceptance failed                 → Step Reflection / focused probe / Replan
```

Replan 从尚未完成的剩余任务开始，已提交 Domain fact、已确认 Effect 和 accepted Step output 不因新 PlanVersion 被“重跑抹掉”。Bhat et al. (2025) 的 closed-loop feedback 研究支持利用执行错误修正后续计划这一方向；Zuno 进一步用 Owner Fact / Receipt 约束反馈可信度。

## Decision 8：Reflection / Alternative Search 必须受预算与风险触发

Reflection 仍按已有原则触发，而不是每 Step 都调用强模型。

允许 high-risk / ambiguous critical decision 使用 bounded alternative search：最多少量候选 plan / hypothesis，经 deterministic checks 和 Critic 比较后选择。不得默认全任务 Tree-of-Thought 搜索。

原因不仅是成本；无界自反思还会放大错误上下文和不可复现性。09 必须单独测量 Reflection 带来的质量增益、token、latency 和错误修复率。

## Decision 9：06 Tool Runtime 采用 Propose–Verify–Execute–Observe

MCP / Function Calling 只解决工具描述、schema 和 transport 的一部分。现实副作用继续由 06 / 08 的现有语义保护。

```text
Model / Capability ActionProposal
→ PreparedAction
→ Schema Validation
→ Semantic / Domain Constraint Validation
→ ActionHash
→ Authorization / Approval freshness
→ Mandatory Audit when required
→ ToolAttempt
→ Execute
→ typed Observation / EffectReceipt
→ Reconcile if outcome unknown
```

在 PreparedAction 后新增概念性 `Action Validator / Safety Shield`：检查 schema、业务参数、target resource、side-effect class、idempotency / reconciliation capability、security epoch、approval action hash 和 budget。它是确定性 / 可测试 Guard 的优先位置；模型不能自己宣布“安全”。

工具循环受 `max_action_attempts`、consecutive tool-call cap、deadline、budget 和 repeated-failure escalation 控制。连续失败不能无限 ReAct；达到阈值后进入 Step Reflection、Replan、Human Review 或 Abort。

外部 HTTP 2xx、transport success、schema-valid response、Effect confirmed 仍是四种不同事实。

## Decision 10：07 Model Gateway 继续 Role-first，不把“法律模型”变成 Authority

法律专用模型、通用强模型、本地模型都只能作为 Model Provider。07 仍以 TASK_ANALYZER、PLANNER、PLAN_REPAIR、EXECUTOR_FAST、EXECUTOR_REASONING、QUERY_REWRITER、EXTRACTOR、CRITIC、SYNTHESIZER、FINAL_CRITIC 等 Role 做 qualification。

Research Provider 可以在 `LEGAL_EVENT_EXTRACTION` 等 Capability 内使用专门 encoder / legal LLM，但模型版本、Prompt / structured-output spec、security egress、cost、quality evidence 都必须可追溯。

模型隐藏 Chain-of-Thought 不进入长期 Contract、Domain Evidence 或 Memory。需要审计时保存结构化 rationale summary、evidence refs、decision / validation result 和 model-attempt refs。

## Decision 11：08 把 Research / Memory / Retrieval 全部纳入持续安全门禁

新增算法复杂度不能绕过既有安全边界：

- Query Rewrite / Graph Expansion 不能扩大未授权 Scope；
- Memory recall 必须重新检查 tenant / Matter / user / purpose / lifecycle；
- 外部 Model 只能得到最小充分 Context，并消费当前 egress policy；
- Research Provider / OSS 需要 supply-chain、license、deployment、data-egress review；
- cached retrieval / memory / model output 在 SecurityEpoch 变化后重新验证 current eligibility；
- Action Validator 不能替代 08 Authorization / Approval owner。

## Decision 12：09 负责证明每个复杂算法值得留下

任何新复杂度都需要对照组，而不是“论文先进所以 Adopt”。至少建立以下 Eval Families：

### Retrieval ablation

```text
BM25-only
Dense-only
Hybrid
Hybrid + RRF / Rerank
Adaptive multi-route
Adaptive + conditional graph / multi-hop
Always-On graph
```

### Memory ablation

```text
No long-term memory
Working context only
Typed episodic
Typed episodic + semantic / procedural
External context provider enabled
```

### Legal Capability ablation

```text
TRL / research baseline
modern encoder baseline
LLM structured extractor
hybrid provider
```

Event Extraction 不只看 F1，还看 SourceSpan correctness、shared-argument correctness、cross-case generalization、unsupported inference 和 human correction。Conflict / Dispute 看 alignment precision / recall、conflict precision / recall 和 downstream reviewer utility。

### Planning / control ablation

```text
single-step baseline
planner without quality gate
structure + feasibility gate
full structure + feasibility + usefulness gate
reflection always-on vs triggered reflection
```

### Tool safety / recovery

注入 invalid schema、semantic-invalid args、stale approval、timeout-before-send、timeout-after-send、remote duplicate、outcome unknown、reconciliation failure 和 audit outage。

09 报告 PASS / FAIL / BLOCKED；论文 benchmark、Provider benchmark 和 Zuno benchmark 必须分开标记。

## Cross-module ownership summary

| 机制 | Owner / Boundary | 不能做什么 |
| --- | --- | --- |
| Event / Alignment / Conflict semantic contract | 05 | 不直接写 Evidence / Finding |
| Research provider implementation | 05 ProviderBinding | 不因论文指标自动 Eligible |
| Adaptive Retrieval / EvidenceCandidate | 03 | 不发布正式 Evidence / Answer |
| Plan Quality / Replan | 04 | 不重写 Domain / Effect truth |
| Typed Memory policy | Optional Context boundary + 04/08/09 协同 | 不成为第十模块或事实源 |
| Tool Action Validator / Effect recovery | 06 + 08 gate | 不让模型批准自身动作 |
| Model routing / usage | 07 | 不直接成为法律 Authority |
| Security / lifecycle | 08 | 决策成功不等于目标动作已执行 |
| Eval / kill test | 09 | Eval PASS 不等于 Production Ready |
| Formal Evidence / Finding / WorkProduct | 02 | 只接受经过准入的正式事实 |

## Alternatives

### 1. 全部用最新 LLM 替掉研究算法

拒绝。会失去可复现 baseline、领域结构和确定性约束，也无法判断质量提升来自模型规模还是任务设计。

### 2. 把 JIA、OpenViking、GraphRAG 等完整系统直接嵌入

拒绝为默认。完整系统可能拥有自己的 state、memory、domain、security 和 persistence 语义，与 Zuno Owner 冲突。优先拆为 Provider / Primitive。

### 3. 每种新算法建立一个 Agent

拒绝。算法 / retriever / critic 不等于自治 Agent。默认 Single Controller + typed Step / Capability / Provider。

### 4. 为了先进度把 Graph / Memory / Reflection 全部 Always-On

拒绝。复杂度必须按 Query Class、Risk 和 Measurement Gate 条件使用。

### 5. 只保留传统 RAG，不吸收研究机制

不作为 Target。简单 RAG 仍是必须保留的 baseline / fast path，但复杂多文档、冲突、关系和长期任务需要更强候选机制；是否启用由 Eval 决定。

## Consequences

正面：

- 项目可以真实承接 LIPLAB / 葛季栋等研究资产，而不是把论文名字写进简历；
- Zuno 的技术复杂度有业务触发条件和退出条件；
- 传统算法、现代 encoder、LLM 和 OSS 可以在同一 Capability / Provider Contract 下公平比较；
- Retrieval、Memory、Planning、Tool Use 形成一条受控的认知闭环，同时不破坏 Domain / Security / Effect authority；
- 面试与架构审查可以明确解释“为什么用这项技术、什么时候不用、如何证明它值得存在”。

代价：

- Capability / Eval 设计工作明显增加；
- 需要构建更多法律 gold set、failure set 和 human-review evidence；
- 多路检索、typed memory 和 plan quality gate 会增加实现复杂度；
- 研究代码复现与现代化 Provider 需要额外工程工作；
- 如果没有持续 kill test，系统仍可能重新退化成“先进组件堆栈”。

## Implementation gate

本 ADR 只改变 Target Design，不授权 Codex 大规模实现。进入工程实现前至少需要：

1. 对选定 Capability / Contract 逐字段冻结输入、输出、failure、uncertainty、version / causation refs；
2. 对 Retrieval / Memory / Planning / Tool 新机制明确状态转换、Retry / Replan / Reconcile 和 crash window；
3. 对候选 OSS / model provider 做官方文档、源码、license、deployment 和 security review；
4. 先建立 baseline / gold dataset / fault set，再实现复杂 Provider；
5. 每个 implementation task 独立写 Codex specification，不允许 Codex 自行改变九模块 Owner、七对象 Domain Kernel、Formal Admission、Single Controller 或 Provider Proposal 原则。

Target → Current 仍需要代码、Migration（如需要）、Unit / Integration / Fault / E2E、Trace、Eval 和可复现运行证据。