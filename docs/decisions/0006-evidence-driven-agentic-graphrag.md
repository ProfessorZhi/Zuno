# ADR 0006：Evidence-Driven Conditional Retrieval Decision Architecture

status: accepted-target
updated: 2026-08-16
decision_scope: Module 03 Knowledge & Evidence + Module 04 Agent Runtime & Control + Module 05 Capability & Skill
canonical_term: Conditional Evidence Retrieval
terminology_note: Agentic GraphRAG remains a historical / strategy label in this ADR, not Zuno's product identity or an Always-On execution rule.
refinement_note: 2026-08-16 refinement aligns this ADR with the frozen nine-module taxonomy and adds adaptive multi-route retrieval, dependency-aware multi-hop decomposition and bounded evidence-gain control. It does not authorize implementation.

## Context

Zuno 既有 Evidence Retrieval Target 已具备 RetrievalPlan、RetrievalRound、EvidenceLedger、EvidenceFrontier、CorrectiveRetrievalDecision 和 KnowledgeControlProposal 等基础概念，但控制中心仍容易被理解为“动态选择 Retriever”。

企业法律知识任务的主要风险并不是缺少更多 Retriever，而是：

- 召回内容相关但不支持关键 Claim；
- 原文、Graph Local 和 Community Summary 同源却被重复计票；
- 新旧版本、不同主体和不同时间范围产生冲突；
- GraphPath 缺少稳定 SourceSpan；
- 首轮缺证后只扩大 Top-K，而没有判断究竟缺的是哪类证据；
- 一个复杂问题被一次性拆成互相独立的子问题，后续子问题没有消费前序答案与新发现；
- 模型将部分支持写成确定事实；
- 没找到知识、检索漏召回、解析失败、索引故障和权限限制无法区分；
- 系统为了最短路径在证据不足时提前回答，或为了“深入”无条件运行全部 Retriever。

因此 Target 不是“GraphRAG 比 Vector RAG 更先进”，而是把检索升级为 **Adaptive Legal Retrieval（自适应法律检索）+ Evidence Deliberation（证据审议）**：先判断问题需要什么，再在授权、版本、预算和可解释边界内选择最小充分检索路径，并用证据增益和充分性决定继续、修复、扩大、转图、转结构化查询或停止。

## Research basis and interpretation

本 ADR 吸收论文机制，但论文结果只是设计依据，不是 Zuno Current 质量证明。

- Zheng et al. (2024), *Decompose-Solve-Renewal for Multi-Document QA*, DOI `10.1002/asi.24971`：支持复杂多文档问题采用依赖感知的迭代分解，而不是一次性独立拆题。
- Vuthoo et al. (2026), legal-contract RAG survey, DOI `10.1111/exsy.70267`：支持 Naive / Advanced / Modular / Agentic RAG 具有不同成本与适用范围，不能把最复杂路径设为默认。
- Santra et al. (2025), RAG survey, DOI `10.1002/widm.70021`：支持 sparse、dense、hybrid、reranking 和 self-reflective retrieval 作为可组合机制。
- Guo & Han (2026), DOI `10.1049/csy2.70037`：其 adaptive routing 结果支持“按 query complexity 选择检索策略”这一方向，但不能外推为 Zuno 的已测收益。
- Huang et al. (2025), DOI `10.1002/sys.70012`：其 GraphRAG 结果支持关系密集问题中图增强的潜在价值，同时也提醒收益并非所有维度、所有 Query Class 都成立。

研究机制进入 Zuno 时必须经过本 ADR、ADR-0007 和 ADR-0015 的 Provider / Eval Gate；任何论文中的平均指标都不能替代 Zuno 自己的法律数据、延迟、成本和错误分布测量。

## Decision

Zuno 采用：

```text
Query Understanding
+
Bounded Multi-Route Evidence Discovery
+
Fusion / Rerank
+
Claim-level Evidence Deliberation
+
Dependency-aware Targeted Probe
+
Safe Stop and Diagnosis
```

### 1. QueryClass 与 RetrievalIntent 先于 Retriever

03 不把“是否调用 Milvus / BM25 / Graph”作为第一层决策。先建立面向本次任务的 `RetrievalIntent`，至少能表达以下 Query Class：

```text
EXACT_TERM
SEMANTIC
HYBRID
MULTI_HOP
RELATIONAL
GLOBAL_CORPUS
CONFLICT_ANALYSIS
LEGAL_APPLICABILITY
SOURCE_SCOPED
TEMPORAL
```

分类可以由 deterministic rule、轻模型或强模型 Proposal 产生，但最终 Route 必须经过 Scope、Authorization、KnowledgeGeneration、Budget、Capability Availability 和任务完整性校验。Query Rewrite 只能改变表达，不能偷偷扩大 Matter / DocumentVersion Scope 或权限。

### 2. 两阶段、两个闭环

阶段一是有边界的多路径首轮证据发现：根据 QueryClass 只启用预计有边际价值的 Route。

阶段二是 Evidence Eligibility、语义关系、Claim 状态、冲突、答案风险和动态补证。

闭环：

```text
Evidence Discovery Loop
Route → Retrieve → Normalize → Fuse → Rerank → Eligibility → Assess → Merge

Claim / Answer Deliberation Loop
Claim → Evidence Support → Gap / Risk → Probe → Revised Claim State
```

### 3. 多路检索可以并行，但不是“全部 Retriever 全开”

Target Route Family 至少允许：

- BM25 / exact lexical route：案号、法条号、主体名、金额、术语和确定短语；
- Dense semantic route：语义改写、同义表达和隐式条款；
- Metadata / source-scoped route：按 Matter、DocumentVersion、文档类型、时间、主体等过滤；
- Entity / Fact route：消费已验证的结构化候选或专业 Capability 输出；
- Graph route：关系、多跳、时间链和跨文档实体 / 事件问题；
- Global / community route：只对真正需要跨语料总体主题或社区概览的任务启用；
- Temporal / authority route：当时间有效性或来源层级是核心条件时启用。

03 可以在安全并行条件满足时并行发出多个 Route，但 Route 集合必须由 RetrievalPlan 明确记录。`DEEP` 不是全部路径无条件运行。

### 4. Fusion 与 Rerank 是独立层

不同 Route 的原始 score 不得直接比较。Target 允许 Reciprocal Rank Fusion（RRF，倒数排名融合）或经过校准的 fusion 形成候选集，再由 reranker 对问题—候选关系做二阶段排序。

Fusion 不能把同一 Source Family 的 BM25 命中、向量命中、Graph Local 和 Summary 当成四份独立证据。去重与 lineage 必须先于 Claim-level independent-source counting。

Reranker success 只证明排序步骤执行成功，不证明候选具有法律 Evidence 资格。

### 5. 复杂多文档问题使用依赖感知的迭代分解

对 MULTI_HOP / RELATIONAL / CONFLICT_ANALYSIS 任务，不默认一次生成 N 个互相独立的 subquery。Target 采用 DSRC-like 的工程化思想：

```text
Complex Question
→ choose next unresolved sub-question
→ retrieve / solve with current evidence
→ update intermediate structured state
→ renew remaining questions / dependencies
→ continue until sufficient or bounded stop
```

这里的“solve”只能形成 intermediate proposal / observation；后续子问题可以引用已经接受的中间结果和 Evidence refs，但不能把未验证模型文本当作新事实。

如果新的中间证据改变原问题结构，03 只能产生 Retrieval / Knowledge proposal；需要改变任务 Plan DAG 时由 04 创建新的 PlanVersion。

### 6. EvidenceGain 与 EvidenceSufficiency 控制是否继续

每轮 Retrieval 不只看 Top-K 是否非空，还要回答：

- 关键 Claim 的 evidence coverage 是否增加；
- 是否找到了新的独立 Source Family；
- 是否降低了关键冲突或不确定性；
- 新候选是否只是重复或更低质量派生；
- 缺口是信息不足、权限受限、材料未就绪，还是检索策略错误；
- 继续一轮的预计价值是否值得其 token、延迟和成本。

因此每轮形成 `EvidenceGainAssessment` / 等价 Target fact。低增益、重复度过高或预算不足时应停止，而不是让 Agentic Retrieval 自循环。

### 7. Self-RAG / Corrective-RAG 思想只吸收“受界评估”，不复制无限自反思

Zuno 可以吸收 self-reflective / corrective retrieval 的核心思想：在生成前后判断当前证据是否相关、充分、冲突或需要补证。

但 Reflection 只能在明确触发条件下运行，例如关键 Claim 缺证、证据冲突、引用无法回源或首次 Probe 低增益。每次调用都受 `max_rounds`、retrieval budget、token / cost / deadline 和 duplicate-ratio 约束。不能把“模型觉得再搜一次”当成无限续期条件。

### 8. Knowledge Graph + Evidence Reasoning Graph 分开

Knowledge Graph 表达 Entity、Relation、Community、Document、Text Unit 等可重建知识投影。

Evidence Reasoning Graph 表达 Claim、EvidenceCandidate、Source、DocumentVersion、GraphPath、CommunitySummary 之间的：

```text
SUPPORTS
PARTIAL_SUPPORT
CONTRADICTS
QUALIFIES
SUPERSEDES
DUPLICATES
DERIVED_FROM
SUMMARIZES
APPLIES_TO
DOES_NOT_APPLY_TO
INSUFFICIENT_FOR
```

它仍然是 Knowledge Projection / reasoning projection，不是 02 的 Canonical Legal Domain。

### 9. EvidenceCandidate != Evidence

03 只能产生 `EvidenceCandidate`、`CitationLineage`、readiness / retrieval facts 和 assessment。正式 `Evidence` 仍由 02 Legal Domain & Work Product 拥有。

模型可产生：

- Evidence Relation Proposal；
- Conflict Classification Proposal；
- Applicability Proposal；
- Claim Hypothesis Proposal；
- Probe Proposal；
- Provisional Synthesis Proposal。

确定性代码验证 candidate ID、授权、SourceSpan、DocumentVersion、KnowledgeGeneration、lineage、Schema、Budget 和允许动作。模型不能提交最终 Evidence 或 Domain fact。

### 10. 葛季栋 / LIPLAB 研究输出作为结构化检索信号，不直接升级为 Domain fact

ADR-0015 将 JIA / TRL 的法律事件抽取、事件对齐和冲突检测拆成 05 的可版本化 Capability family。03 可以消费这些能力产生的 `EventCandidate`、`AlignmentCandidate`、`ConflictCandidate`、`DisputeCandidate` 作为 Entity / Fact / Graph Route 的结构化检索信号。

这些 Candidate 必须绑定 DocumentVersion、稳定 SourceSpan、CapabilityVersion / ProviderVersion 和 uncertainty。它们可以帮助多跳检索和 Conflict Analysis，但不能因为“来自研究算法”就自动成为 02 的 Evidence / Finding。

### 11. 冲突和低质量证据保留

`CONFLICTING`、`QUALIFYING`、`DUPLICATE`、`DERIVED` 和 `REJECTED_LOW_QUALITY` 不进入最终严格 Context，但保留在 EvidenceLedger / assessment projection 中用于审计、去重、诊断和 Eval。

### 12. STANDARD / DEEP 是成本档位，不是质量标签

STANDARD 默认优先使用 lexical + dense hybrid，并允许一次受界 citation repair / focused probe。

DEEP 允许按 EvidenceGoal、QueryClass、Capability、Security、Budget 和预计信息增益启用 Graph Local、Global、Structured、Temporal、Authority 和 Source-scoped Route。

DEEP 只有在测量上证明对对应 Query Class 有稳定边际收益时才获得 Eligibility；它不能仅因“更复杂”被认为质量更高。

### 13. Retry、Repair、Probe、Fallback 与 Replan 分开

- Retry：同一路径计划仍正确，仅一次执行失败；
- Repair：引用、参数或局部表达可在不改变任务假设时修复；
- Probe：为明确 Evidence Gap 发起新的有目标检索；
- Fallback：切换到经过验证且语义等价的 Retrieval Provider；
- Replan：任务结构、依赖、关键假设或能力边界改变，由 04 创建新 PlanVersion。

03 不自行激活 PlanVersion。

### 14. Outcome

03 至少需要向上层表达：

```text
SUFFICIENT_EVIDENCE
PARTIAL_EVIDENCE
CONFLICTING_EVIDENCE
NO_SUITABLE_EVIDENCE
AUTHORIZED_EVIDENCE_UNAVAILABLE
KNOWLEDGE_QUALITY_SUSPECTED
FAILED
CANCELLED
```

Knowledge 不发布最终答案。04 / 01 根据任务类型决定 Ask User、External Evidence、Replan、Partial、Abstain 或进入后续 Synthesis / Publication。

### 15. CitationLineage 必须记录“为什么走了这条路”

每轮必须可追溯：QueryClass、rewrite / decomposition version、route set、provider version、KnowledgeGeneration、filter / scope、fusion / rerank config、candidate rank、EvidenceGain、stop reason 和必要安全 refs。

这些信息用于诊断与复现 Retrieval 决策，但仍不能替代 02 `WorkProductCitationBinding` 的历史正式引用。

### 16. Knowledge Health 只是诊断 Signal

证据不足不等于知识库故障。`KnowledgeHealthSignal` 必须由 Ingestion、KnowledgeGeneration、Infrastructure、Observability 或人工调查进一步确认，才能成为运维事实。

### 17. 保持 Single Controller

Evidence Deliberation 是 03 内层受治理闭环，不是自治 Multi-Agent Runtime。一次 AgentRun 的任务级控制权仍只属于 04 Agent Runtime & Control。

## Alternatives

### A. 固定 Hybrid / GraphRAG Pipeline

优点：简单、低风险、易测量。

拒绝作为统一 Target：无法根据 Claim Gap、冲突和 Evidence State 动态补证，容易过检或漏检。

### B. 只增加 Retriever Router

优点：比固定 Pipeline 灵活。

拒绝作为最终控制中心：只回答“走哪条路径”，不能回答 Evidence 是否支持 Claim、是否同源、是否冲突以及是否需要补证。

### C. 所有 Retriever 全开

优点：首轮覆盖看似更高。

拒绝：成本、延迟、噪声和重复度失控，且无法证明每条路径有边际价值。

### D. 一次性 Query Decomposition

优点：实现容易，并行度高。

拒绝作为复杂多文档默认：后续问题可能依赖前序证据，一次性拆分容易固定错误假设。只有依赖独立且可并行的子问题才使用一次性分解。

### E. 单一 Quality Score

优点：实现简单。

拒绝：会覆盖 ACL、版本、SourceSpan、Authority、Applicability、Conflict 和 independence 等不可折叠维度。

### F. 每个 Retriever 一个 Agent

优点：概念上可并行自治。

拒绝：增加多份 Context、通信、状态冲突、重复工作和评测难度，不符合 Single Controller 原则。

### G. 模型直接判断最终 Evidence

优点：实现快。

拒绝：模型可能引用不存在、陈旧或未授权 Candidate，无法替代确定性门禁和 02 Ownership。

## Consequences

正面：

- 回答质量目标从“相关 Chunk”提升到“Claim 证据充分性”；
- lexical / dense / structured / graph 能按 Query Class 和缺口组合；
- 多文档问题可以根据中间结果动态更新剩余检索问题；
- Graph Retrieval 能按关系 / 多跳 / global corpus 场景使用，而不是 Always-On；
- 冲突、版本、适用范围和同源证据可以显式治理；
- 支持动态补证和安全无据拒答；
- 可分别测量 Route、Fusion、Rerank、Evidence、Probe、Stop 和 Diagnosis。

代价：

- RetrievalPlan、Round、assessment 和 Trace 增加；
- 需要 Evidence 标注和 Claim 级 Eval；
- 多路融合与多轮检索带来成本和延迟；
- Graph / structured projection 的 rebuild 与 freshness 语义更复杂；
- 错误的 QueryClass 或 decomposition 会形成新的失败面，因此必须保留 simple baseline 和 kill test。

## Validation Strategy

至少比较：

```text
Vector-only RAG
BM25-only / lexical baseline
BM25 + Vector Hybrid
Hybrid + RRF / Rerank
Always-On Graph Retrieval
Adaptive Retrieval without Graph
Adaptive Retrieval + conditional Graph / multi-hop
```

按精确事实、语义 FAQ、实体关系、多跳、多文档依赖、全局主题、新旧版本、冲突、法律适用、无答案和权限受限分层报告。

关键指标至少包括：

- Gold Evidence Recall / Recall@K；
- MRR / nDCG（适用时）；
- Strict Evidence Yield；
- Independent Source Counting Accuracy；
- Claim Coverage；
- Strict Citation Coverage；
- Unsupported Claim Rate；
- Conflict Disclosure Accuracy；
- Probe Information Gain / Evidence Gain；
- Retrieval Round Count / Duplicate Ratio；
- Answer Stability；
- Abstention Precision / Recall；
- Knowledge Diagnosis Precision；
- Cost / latency / token。

研究论文指标只作为 Benchmark 设计参考。Target 变为 Current 必须具备代码、Migration（如需要）、单元和集成测试、Fault Injection、E2E、Trace、固定 Benchmark、Eval 和 Release Gate。文档合并本身只证明 `design available`。