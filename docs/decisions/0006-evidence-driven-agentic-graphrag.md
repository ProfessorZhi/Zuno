# ADR 0006：Evidence-Driven Agentic GraphRAG Decision Architecture

status: accepted-target
updated: 2026-08-04
decision_scope: Architecture v2 Target

## Context

Zuno 既有 Agentic GraphRAG Target 已具备 RetrievalPlan、RetrievalRound、EvidenceLedger、EvidenceFrontier、CorrectiveRetrievalDecision 和 KnowledgeControlProposal 等基础概念，但控制中心仍容易被理解为“动态选择 Retriever”。

企业知识任务的主要风险并不是缺少更多 Retriever，而是：

- 召回内容相关但不支持关键 Claim；
- 原文、Graph Local 和 Community Summary 同源却被重复计票；
- 新旧版本、不同主体和不同时间范围产生冲突；
- GraphPath 缺少 SourceSpan；
- 首轮缺证后只扩大 Top-K；
- 模型将部分支持写成确定事实；
- 没找到知识、检索漏召回、解析失败、索引故障和权限限制无法区分；
- 系统为了最短路径在证据不足时提前回答，或为了“深入”无条件运行全部 Retriever。

因此需要把 Target 从 retrieval-centric routing 升级为 Evidence-Driven Agentic GraphRAG。

## Decision

Zuno Architecture v2 采用：

```text
Broad Evidence Discovery
+
Evidence Deliberation
+
Claim-level Evidence State
+
Targeted Evidence Probe
+
Safe Stop and Diagnosis
```

### 1. 两阶段、两个闭环

阶段一：有边界的多路径首轮证据发现。

阶段二：Evidence Eligibility、语义关系、Claim 状态、冲突、答案风险和动态补证。

闭环：

```text
Evidence Discovery Loop
Retrieve → Normalize → Eligibility → Assess → Merge

Claim / Answer Deliberation Loop
Claim → Evidence Support → Risk → Probe → Revised Claim
```

### 2. 固定图与动态对象

继续使用固定 `KnowledgeRetrievalGraph`。模型不得动态改写节点或边。

动态内容只存在于：

- InitialEvidenceCollectionPlan；
- RetrievalRound / Action / Attempt；
- EvidenceAssessment；
- EvidenceReasoningGraphVersion；
- ClaimEvidenceState；
- EvidenceProbe；
- EvidenceSetVerdict。

### 3. Knowledge Graph + Evidence Reasoning Graph

Knowledge Graph 表达 Entity、Relation、Community、Document、Text Unit。

Evidence Reasoning Graph 表达 Claim、Evidence、Source、DocumentVersion、GraphPath、CommunitySummary 之间的：

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

### 4. 不采用简单多数投票

Evidence 不按“支持数量”简单投票。必须考虑：

- Eligibility；
- Directness；
- Authority；
- Temporal Validity；
- Applicability；
- Citation；
- Source Family；
- Derivation Depth；
- Conflict；
- Claim Impact。

原文、Graph Local 与 Community Summary 若同源，只能算一个 Source Family。

### 5. 模型只产生 Proposal

模型可产生：

- Evidence Relation Proposal；
- Conflict Classification Proposal；
- Applicability Proposal；
- Claim Hypothesis Proposal；
- Probe Proposal；
- Provisional Synthesis Proposal。

确定性代码验证 Evidence ID、授权、SourceSpan、版本、lineage、Schema、Budget 和允许动作。模型不能提交最终 Evidence 状态。

### 6. 冲突和低质量证据保留

`CONFLICTING`、`QUALIFYING`、`DUPLICATE`、`DERIVED` 和 `REJECTED_LOW_QUALITY` 不进入最终严格 Context，但保留在 EvidenceLedger 中用于审计、去重、诊断和 Eval。

### 7. STANDARD / DEEP

STANDARD 默认 BM25 + Vector，并允许一次 Focused Citation Repair。

DEEP 允许按 EvidenceGoal、Capability、Security、Budget 和预计信息增益启用 Graph Local、Global、DRIFT、Structured、Temporal、Authority 和 Source-scoped Route。

DEEP 不等于全部 Retriever 无条件运行。

### 8. 动态补证

Probe 选择以关键 Claim 的 Answer Impact、Uncertainty、Expected Information Gain、预计 Evidence Quality、Cost、Latency、Risk 和 Redundancy 为依据。

Retry、Repair、Fallback、Probe 与 Replan 必须分开。Knowledge 只能提议 Replan，Agent Core 才能创建和激活新 PlanVersion。

### 9. Outcome

支持：

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

Knowledge 不发布最终答案。Agent Core 决定 Ask User、External Evidence、Replan、Partial、Abstain 或 Finalize。

### 10. Knowledge Health 只是诊断 Signal

证据不足不等于知识库故障。`KnowledgeHealthSignal` 必须由 Ingestion、KnowledgeVersion、Infrastructure、Observability 或人工调查进一步确认，才能成为运维事实。

### 11. 保持 Single Controller

Evidence Deliberation 是 Module 03 内层受治理闭环，不是自治 Multi-Agent Runtime。一次 AgentRun 的任务级控制权仍只属于 Module 06 Agent Core。

### 12. 版本与实施边界

本 ADR 是 `accepted-target`：

- 不修改当前 Program；
- 不修改 PHASE01–PHASE22；
- 不授权业务代码、Migration 或 Runtime 实现；
- Architecture v2 的实现 Program 必须在 PHASE22 收口后另行确认。

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

### D. 单一 Quality Score

优点：实现简单。

拒绝：会覆盖 ACL、版本、SourceSpan、Authority、Applicability 和 Conflict 等不可折叠维度。

### E. 每个 Retriever 一个 Agent

优点：概念上可并行自治。

拒绝：增加多份 Context、通信、状态冲突、重复工作和评测难度，不符合 Single Controller 原则。

### F. 模型直接判断最终 Evidence

优点：实现快。

拒绝：模型可能引用不存在或未授权 Evidence，无法替代确定性门禁和领域 Ownership。

## Consequences

正面：

- 回答质量目标从“相关 Chunk”提升到“Claim 证据充分性”；
- GraphRAG 的 Local、Global、DRIFT 能按问题和缺口使用；
- 冲突、版本、适用范围和同源证据可以显式治理；
- 支持动态补证和安全无据拒答；
- 可分别测量 Route、Evidence、Probe、Stop 和 Diagnosis。

代价：

- 领域对象、状态和 Trace 增加；
- 需要 Evidence 标注和 Claim 级 Eval；
- 模型 Critic 需要校准；
- 多轮检索带来成本和延迟；
- 恢复、幂等、late result 和 generation 语义更复杂。

## Validation Strategy

至少比较：

```text
Vector-only RAG
BM25 + Vector Hybrid
Fixed GraphRAG
Agentic Routing
Evidence-Driven Agentic GraphRAG
```

按精确事实、语义 FAQ、实体关系、多跳、全局主题、新旧版本、冲突、无答案和权限受限分层报告。

关键指标：

- Gold Evidence Recall；
- Strict Evidence Yield；
- Independent Source Counting Accuracy；
- Claim Coverage；
- Strict Citation Coverage；
- Unsupported Claim Rate；
- Conflict Disclosure Accuracy；
- Probe Information Gain；
- Answer Stability；
- Abstention Precision / Recall；
- Knowledge Diagnosis Precision；
- Cost / latency。

Target 变为 Current 必须具备代码、Migration、单元和集成测试、Fault Injection、E2E、Trace、固定 Benchmark、Eval 和 Release Gate。文档合并本身只证明 `design available`。
