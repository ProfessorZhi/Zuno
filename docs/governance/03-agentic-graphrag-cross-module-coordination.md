# Agentic GraphRAG 跨模块协调建议（临时）

updated: 2026-07-14  
status: temporary-cross-module-coordination-proposal  
owner_module: 03 Knowledge / Agentic GraphRAG  
formal_target: `docs/modules/03-knowledge-agentic-graphrag.md`  
removal_condition: 06、10 及共享 Contract Registry 已吸收确认内容后删除本文

> 本文不是 06 Agent Core、10 Observability & Eval 或其他模块的正式 Target 架构，不得覆盖这些模块现有规范。
>
> 本文用于主线程协调 03 Agentic GraphRAG 与相邻模块的 Contract、Ownership、状态与评测要求。协调完成后，确认内容应进入相应模块正式文档、ADR 或共享 Contract Registry；随后删除本文，使 03 最终只保留 `docs/modules/03-knowledge-agentic-graphrag.md` 作为本模块正式设计文档。

## 1. 协调目标

03 的 Target 设计要求形成两层闭环：

```text
06 Agent Core outer loop
    是否、何时、为什么检索
    Evidence Goal、Plan Step、Task Budget、Replan 与 Finalization

03 Knowledge inner loop
    Query Strategy、Retriever Route、Graph Route、Evidence Evaluation、
    Corrective Retrieval 与 Knowledge Step 内停止
```

同时 10 必须能够回答：

```text
Agentic 控制是否比固定 RAG 有增量价值
Graph 是否比 Agentic Text RAG 有增量价值
回答正确性、引用、Unsupported Claim、成本和延迟是否改善
哪些题型改善，哪些题型退化
```

## 2. 对 06 Agent Core 的建议

### 2.1 增加 RetrievalNeedDecision

Agent Core 在创建 Knowledge Step 前提交：

```yaml
RetrievalNeedDecision:
  decision_id: string
  run_id: string
  plan_version_id: string
  step_run_id: string
  decision: NOT_NEEDED | RETRIEVE_NOW | RETRIEVE_AFTER_DEPENDENCY | ASK_USER_FIRST | RETRIEVAL_FORBIDDEN
  reason_codes: [string]
  evidence_requirement_refs: [string]
  requested_profile_ceiling: STANDARD | DEEP
  authorized_scope_ref: string
  retrieval_budget_ref: string
  decision_hash: string
```

强制语义：

1. 所有回答仍必须经过 Plan、Trace、Budget、AnswerPolicy、Final Gate 和 RunOutcome。
2. `NOT_NEEDED` 只表示 Knowledge Step 不创建，不表示绕过 Plan。
3. Model 可以提出 Retrieval Need Proposal，但 Runtime 提交最终 Decision。
4. `RETRIEVAL_FORBIDDEN` 必须绑定 Security / Policy 原因。
5. Evidence Requirement 不得仅存在于 Prompt。

### 2.2 Knowledge Step 输入

建议在 06 的 Step input contract 中加入：

```text
KnowledgeQueryRequest
EvidenceRequirement[]
AuthorizedKnowledgeScope ref
RetrievalBudget ref
Knowledge Profile ceiling
AnswerPolicy ref
ExecutionContextSnapshot ref
```

Agent Core 不应只传：

```text
query string
knowledge_ids
retrieval_mode
```

### 2.3 Knowledge Observation 映射

03 返回：

```text
KnowledgeRetrievalOutcome
SelectedEvidenceBundle ref
EvidenceVerdict ref
KnowledgeControlProposal ref
```

06 应映射为 Step Observation，而不是直接把 Retriever raw result 作为模型上下文。

### 2.4 Corrective Retrieval 与 Replan

建议冻结：

```text
03 Corrective Retrieval
    Query / Retriever / Graph / Citation 路径改变；
    Evidence Goal 和 Knowledge Step 结构不变。

06 Replan
    Goal、依赖、能力、数据源、用户输入或任务结构改变；
    创建新 PlanVersion，经过 Replan Barrier。
```

03 提交 `REPLAN_REQUIRED` 只是一项 Proposal。06 必须决定：

```text
ACCEPT_REPLAN_PROPOSAL
REJECT_AND_ABSTAIN
ASK_USER
USE_PARTIAL_EVIDENCE
```

### 2.5 Budget 委托

06 拥有总 Budget Ledger，建议为 Knowledge Step 创建受限子预算：

```yaml
KnowledgeBudgetDelegation:
  task_budget_ref: string
  retrieval_budget_ref: string
  max_rounds: int
  max_actions: int
  max_parallel_actions: int
  max_graph_hops: int
  max_model_calls: int
  max_cost: number
  deadline_at: datetime
```

03 只能 Reserve / Settle 该子预算，不能提高上限。

### 2.6 Signal 与取消

06 应将以下控制信号传播至 03：

```text
RUN_CANCEL
STEP_CANCEL
DEADLINE_UPDATED
SECURITY_REAUTH_REQUIRED
BUDGET_REVOKED
USER_CONSTRAINT_CHANGED
```

用户约束实质变化时，旧 Knowledge Run 的结果必须按 generation / taint 规则处理。

### 2.7 Final Gate

06 Final Gate 不应仅检查“有引用”，还应消费：

```text
EvidenceVerdict
requirement coverage
citation completeness
unresolved conflict
temporal validity
abstention proposal
```

最终答案不得把 `AUXILIARY_ONLY` Graph Evidence 当作 strict citation。

## 3. 对 10 Observability & Eval 的建议

### 3.1 增加 Knowledge typed event mapping

建议 10 的 retrieval event contract 至少覆盖：

```text
KnowledgeQueryRequested
KnowledgeSnapshotPinned
RetrievalProfileResolved
RetrievalRoundPlanned
RetrieverAttemptStarted / Completed / Failed
GraphRouteDecided
EvidenceCommitted
EvidenceQualityEvaluated
CorrectiveRetrievalDecided
RetrievalStopped
KnowledgeControlProposalEmitted
KnowledgeRetrievalOutcomeCommitted
```

事件需要的关联字段：

```text
run_id
plan_version_id
step_run_id
knowledge_query_run_id
round_id
attempt_id
knowledge_space_id
knowledge_snapshot_ref
requested_profile
effective_profile
authorization_decision_ref
security_epoch_ref
budget delta ref
reason codes
trace_id
```

### 3.2 不记录隐藏推理

可观测性只记录：

```text
结构化决策
reason codes
输入/输出引用
状态转换
预算和耗时
Evidence requirement coverage
```

不得记录：

```text
隐藏 Chain-of-Thought
完整 Prompt
完整文档正文
未经脱敏的用户或企业数据
Provider credential
```

### 3.3 Required Eval Profiles

建议将当前 profile 集扩展并精确定义：

```text
standard_rag
    单轮 BM25 + Vector baseline。

fixed_graphrag
    固定 Graph route / 固定 Pipeline，用于隔离 Graph 能力收益。

agentic_text_rag
    多轮、纠正和动态路由，但禁用 Graph。

agentic_graphrag
    Agentic 控制 + Graph 按需启用。

agentic_graphrag_external_evidence（可选）
    允许受治理的外部 Tool Step。
```

当前已有 `standard_rag / deep_graphrag / agentic_graphrag` 时，应通过版本化 ProfileDefinition 迁移，不能只重命名历史结果。

### 3.4 Comparability 维度

BenchmarkComparison 必须固定：

```text
dataset_version
case_set_hash
corpus_manifest
knowledge_snapshot
security scope
runtime policy
retrieval profile
graph/index version
model routing policy
judge policy
metric definition
sampling policy
answer/citation policy
```

任何关键维度不兼容时输出 `INCOMPARABLE`，不得计算 Release Gate Pass。

### 3.5 题型分层

至少使用：

```text
simple_fact
exact_clause
single_document
multi_document
multi_hop_relation
global_theme
temporal_version
conflicting_evidence
no_answer
permission_filtered
stale_index
citation_repair
```

聚合指标必须同时提供总体和题型切片。总体平均提升不能掩盖简单事实明显退化。

### 3.6 过程指标

建议新增：

```text
Retrieval Need Precision / Recall
Profile Routing Accuracy
Retriever Selection Gain
Graph Routing Precision / Recall
Evidence Requirement Coverage
Citation Eligibility Accuracy
Corrective Action Success Rate
Novel Evidence Gain per Round
No-progress Round Rate
Premature Stop Rate
Over-retrieval Rate
Fallback / Proposal Accuracy
```

这些指标需要 03 事件字段完整，否则必须 `UNAVAILABLE`，不能推断。

### 3.7 最终质量指标

```text
Answer Correctness
Answer Completeness
Groundedness
Citation Correctness
Citation Completeness
Unsupported Claim Rate
Conflict Disclosure Accuracy
Temporal Validity
Abstention Accuracy
```

效率指标：

```text
P50 / P95 latency
Retriever and Graph calls
Model calls / tokens
Cost per correct answer
Cost per grounded answer
Timeout / failure / fallback rate
```

### 3.8 实验设计

建议三阶段：

```text
Offline fixed benchmark
→ Shadow run
→ Canary / A-B
```

Shadow Run 中旧系统仍正式回答，Agentic 候选后台运行并生成可比 artifact。

Canary 自动回退条件至少包括：

```text
Unsupported Claim Rate 上升
Citation Coverage 下降
simple_fact non-regression 失败
P95 latency 超标
cost ceiling 超标
timeout / failure rate 超标
```

### 3.9 Release Gate 建议

现有最低阈值不得降低。建议增加：

```text
Simple Fact Answer Correctness non-regression
Graph Incremental Gain on graph-eligible cases > configured minimum
Corrective Action Success Rate > configured minimum
No-progress Round Rate < configured maximum
Abstention Accuracy non-regression
P95 latency and cost within profile SLO
```

阈值数值需要通过独立 Policy / ADR 冻结，不在本临时建议中擅自给出。

## 4. 对 05 Memory & Context 的依赖建议

03 只返回 `SelectedEvidenceBundle`。05 应：

```text
按 Context Budget 组装
保持 CitationLineage
避免重复 SourceSpan
标记冲突与辅助证据
记录 Evidence → Context item 映射
```

05 不应：

```text
重新执行 Retriever
把未选 Candidate 加入 Context
把 AUXILIARY_ONLY 提升为 strict evidence
丢失 KnowledgeSnapshot 与 Security refs
```

回答质量评测需区分：

```text
Retrieval failure
Context assembly failure
Synthesis failure
```

## 5. 对 09 Security 的依赖建议

需要确认：

```text
AuthorizedKnowledgeScope contract
ACL prefilter 的强制字段
Graph 节点/边授权语义
Security Epoch 变化与 taint
原文 Citation disclosure
External model / external search data policy
Knowledge auto-select 的候选范围
```

03 不能自行定义“扩大 scope”。

## 6. 对 04 Model Gateway 的依赖建议

需要为以下 role 提供稳定请求与 structured output：

```text
QUERY_REWRITER
EXTRACTOR
CRITIC
EXECUTOR_FAST
EXECUTOR_REASONING
```

Model Gateway 应返回：

```text
routing decision
attempt
usage / cost
structured output validation
fallback
provider failure
```

Knowledge 只保存 role/slot 与 invocation refs，不保存 Provider Secret。

## 7. 对 11 Infrastructure 的依赖建议

需要确认：

```text
BM25 / Vector / Graph query capability receipts
Index write / visibility / verification receipts
ServingWatermark primitive
Queue / Lease / fencing
Object Store
Outbox / Inbox
Snapshot-compatible read primitive
physical deletion receipt
backup / restore and reconciliation
```

Infrastructure receipt 不等于 Knowledge Acceptance。

## 8. 建议的共享 Contract Registry 条目

主线程确认后，可加入 Registry：

```text
RetrievalNeedDecisionV1               06 → 03
EvidenceRequirementV1                 06 → 03
KnowledgeQueryRequestV1               06 → 03
AuthorizedKnowledgeScopeRefV1         09 → 03
KnowledgeBudgetDelegationV1           06 → 03
KnowledgeRetrievalOutcomeV1           03 → 06
KnowledgeControlProposalV1            03 → 06
SelectedEvidenceBundleV1              03 → 05
KnowledgeRuntimeEventV1               03 → 10
KnowledgeSnapshotRefV1                03 → 05/06/10
```

Registry 冻结前，这些保持 `PROPOSED_TARGET`，不得声称已完成跨模块确认。

## 9. 协调顺序

```text
1. 06 确认 Retrieval Need、Knowledge Step、Budget、Proposal 与 Replan 边界
2. 09 确认 Authorized Scope、Security Epoch 和 disclosure
3. 05 确认 SelectedEvidenceBundle → ContextPack
4. 10 确认 typed events、profile、metrics、comparability 和 Release Gate
5. 04 / 11 确认 Model 与 Infrastructure ports
6. 更新 Cross-module Contract Registry / ADR
7. 各模块正式文档吸收确认内容
8. 删除本文
9. 再生成 Codex Program
```

## 10. 删除本文的验收条件

以下全部满足后删除：

- [ ] 06 正式文档已吸收 RetrievalNeedDecision、Knowledge Step 和 Replan 边界。
- [ ] 10 正式文档已吸收 Agentic GraphRAG Event、Profile 和 Eval 要求。
- [ ] 05、09、04、11 的必要 Contract 已确认或明确延期。
- [ ] 共享 Contract Registry 已标明版本、Owner、Producer、Consumer 和状态。
- [ ] 03 正式文档中的引用与冻结 Contract 一致。
- [ ] 已创建可执行 Program，且 Program 不自行改变架构原则。
- [ ] 仓库搜索不再存在对本文的活跃依赖。

删除后，03 的唯一正式设计文档仍为：

```text
docs/modules/03-knowledge-agentic-graphrag.md
```
