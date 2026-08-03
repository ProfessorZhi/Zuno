# 10 Observability & Eval

updated: 2026-08-04
status: normative-target-module-architecture
architecture_generation: v2
module_number: 10
formal_path: `docs/modules/10-observability-eval.md`

> 本文是 Zuno 第 10 个逻辑模块——Observability & Eval——的唯一正式 Target 架构主设计。
>
> Architecture v2 增加 Evidence-Driven Agentic GraphRAG 的全过程 Trace、证据评价、Probe 信息增益、冲突处理、拒答和知识质量诊断评测。存在 Trace 或 Eval Runner 不等于质量已经证明。
>
> 本次只升级 Target 文档，不修改当前 Program、PHASE01–PHASE22、业务代码、Migration 或生产状态。

---

# Part I：定位、目标与边界

## 1. 模块定位

Observability & Eval 是 Zuno 的运行证据、质量测量和发布门禁模块。它负责把跨模块事件关联为可查询 Trace，把 Trace 与固定数据集转化为 EvalResult，并对版本、模型、Prompt、检索策略和发布候选给出可复现的质量证据。

它解决：

```text
一次 AgentRun 为什么成功或失败无法解释
模型、检索、Tool、Memory、Security 和 Queue 日志彼此分裂
最终答案变好，但无法归因于 Graph、Rerank、更多预算或模型升级
只有平均分，没有 Failure Bucket 和高风险用例
Evidence 相关但不支持 Claim，仍被当成正确召回
Community、Local 和原文同源，却被重复计算
Probe 轮次增加成本，但没有衡量信息增益
无答案问题被迫回答，或者可回答问题被过度拒答
架构、Runner 或测试文件存在，却被误报为 quality proven
```

## 2. 目标

1. 为每个 Command、Run、Plan、Step、KnowledgeQuery、ModelInvocation、Tool Effect 和 Approval 建立统一 Correlation。
2. Trace 记录可审计事实，不保存隐藏思维链。
3. Eval 区分检索、Evidence、Claim、Answer、Control、Safety、Recovery 和 Cost。
4. 固定 Benchmark 可比较版本并支持消融。
5. Release Gate 只消费可复现证据，不消费“感觉更好”。
6. 对 Evidence-Driven Agentic GraphRAG 评估 Route、Assessment、Conflict、Probe、Stop 和 Diagnosis。
7. 质量结论带环境、Commit、配置、数据集、模型和时间范围。

## 3. 非目标

- 不拥有业务模块领域状态；
- 不替代 Security Audit；
- 不记录隐藏 CoT；
- 不因为单次 LLM Judge 高分就宣布上线；
- 不让 Eval 修改 RunOutcome；
- 不用线上点击率直接代替 Ground Truth；
- 不把 Derived Evidence 数量当成独立证据数量；
- 不把 `KNOWLEDGE_QUALITY_SUSPECTED` 自动升级为故障事实。

## 4. Ownership

Observability & Eval owns：

```text
TraceRecord
Span / Event Projection
Metric Definition and Projection
EvalDataset
EvalCase
EvalRun
EvalResult
FailureBucket
BenchmarkProfile
ExperimentComparison
ReleaseGateDefinition
ReleaseGateResult
QualityClaim
KnowledgeDiagnosisEvaluation
```

业务模块 owns 原始领域事实并发出 typed events。Module 10 不反向写入 AgentRun、Evidence、Tool Effect 或 Authorization。

---

# Part II：Trace 架构

## 5. 统一关联标识

每个事件至少包含：

```yaml
TraceEnvelope:
  event_id: string
  event_type: string
  occurred_at: datetime
  tenant_id: string
  workspace_id: string
  correlation_id: string
  causation_id: string | null
  command_ref: string | null
  agent_run_ref: string | null
  plan_version_ref: string | null
  step_run_ref: string | null
  knowledge_query_run_ref: string | null
  model_invocation_ref: string | null
  tool_attempt_ref: string | null
  security_epoch_ref: string | null
  source_module: string
  payload_schema_version: string
  redaction_policy_ref: string
  payload_ref: string
```

Trace Payload 必须最小化、脱敏、版本化。正文、Secret、未授权 Evidence 和完整 Tool 输出通过受控 Artifact 引用，不直接复制到 Event。

## 6. Agent Core Trace

至少覆盖：

```text
command_accepted
agent_run_created
plan_version_proposed
plan_version_validated
plan_version_activated
step_became_ready
step_dispatched
step_action_started/completed
step_acceptance_recorded
step_reflection_triggered
join_evaluated
replan_proposed
replan_barrier_entered
plan_version_superseded
final_gate_started/completed
run_outcome_committed
```

## 7. Evidence-Driven Agentic GraphRAG Trace

至少覆盖：

```text
evidence_goal_interpreted
initial_collection_plan_created
retrieval_action_admitted
retrieval_action_rejected
retriever_attempt_started
retriever_attempt_completed
candidate_evidence_normalized
provenance_bound
eligibility_decision_recorded
semantic_assessment_requested
semantic_assessment_recorded
evidence_classified
evidence_lineage_bound
evidence_reasoning_graph_version_created
claim_hypothesis_created
claim_evidence_state_updated
provisional_answer_created
answer_risk_reviewed
probe_candidate_created
probe_decision_recorded
probe_round_started/completed
evidence_set_verdict_recorded
selected_evidence_bundle_created
insufficient_evidence_outcome_created
knowledge_health_signal_created
```

每个 RetrievalRound 必须能回答：

- 为什么选择这些 Route；
- 哪些 Route 被 Policy / Budget / Security 拒绝；
- 收到多少候选；
- 多少通过 Eligibility；
- 多少严格接受、辅助、冲突、限定、重复、派生、拒绝或排除；
- 新增多少独立 Source Family；
- 哪些 Claim 状态发生变化；
- 为什么继续或停止。

## 8. Model Gateway Trace

```text
model_invocation_created
model_route_selected
model_attempt_started/failed/completed
model_fallback_selected
model_output_schema_validated
model_output_reference_validation_failed
model_usage_settled
```

不记录隐藏思维链。可记录结构化 Proposal、Reason Code、模型版本、PromptVersion、输入 Hash、输出 Hash 和 Usage。

## 9. Tool 与 Security Trace

Tool：

```text
action_proposed
canonical_args_built
security_gate_evaluated
approval_requested/resolved
prepared_tool_action_created
tool_attempt_started/completed
effect_marked_unknown
effect_reconciled
compensation_proposed/completed
```

Security：

```text
authorization_evaluated
security_epoch_changed
disclosure_decision_recorded
credential_lease_issued/revoked
output_disclosure_checked
```

Audit 与 Trace 相关但不等同：Audit 关注谁在何时对受控资源做了什么；Trace 关注一次运行如何流转。二者共享关联 ID，但保留不同 Retention 和访问策略。

---

# Part III：Metric 与 SLO

## 10. 运行指标

- Run throughput；
- Run / Step success、partial、abstain、failure、cancel rate；
- p50 / p95 / p99 latency；
- queue wait；
- worker utilization；
- retry / replan / reflection rate；
- checkpoint recovery rate；
- duplicate dispatch suppression；
- unknown effect and reconciliation duration；
- tenant fairness；
- budget admission rejection。

## 11. Model 指标

- latency by role / task type / provider；
- token and cost；
- schema validity；
- reference validity；
- weak-to-strong upgrade rate；
- fallback rate；
- 429 / overload / timeout；
- PromptVersion regression；
- Evidence Critic calibration；
- Critic disagreement。

## 12. Knowledge 检索指标

```text
Initial Evidence Diversity
Retriever Candidate Yield
Strict Evidence Yield
Gold Evidence Recall@K
MRR / nDCG
Fusion Gold Drop Rate
Reranker Gold Demotion Rate
Unnecessary Graph Invocation Rate
Unnecessary Global Search Rate
```

## 13. Evidence 指标

```text
Evidence Relevance Precision
Entailment Classification Accuracy
Contradiction Classification Accuracy
Applicability Classification Accuracy
Citation Eligibility Accuracy
Independent Source Counting Accuracy
Derived Evidence Ratio
Duplicate Evidence Ratio
Supersedes Resolution Accuracy
Conflict Discovery Rate
Conflict Resolution Rate
Strict Citation Coverage
```

## 14. Probe 与停止指标

```text
Probe Selection Accuracy
Probe Information Gain
No-progress Probe Rate
Average Rounds to Stable Answer
Marginal Evidence Gain by Round
Answer Stability
Budget Exhaustion Rate
Low-gain Stop Precision
Unnecessary Probe Rate
```

信息增益不能只用“多了多少 Chunk”。至少观察：

- 新独立 Source Family；
- Claim Verdict 变化；
- Citation Gap 关闭；
- Critical Conflict 解决；
- Answer Risk 降低；
- Provisional Answer 稳定性提高。

## 15. Answer 与安全指标

```text
Claim Coverage
Faithfulness
Unsupported Claim Rate
Conditional Claim Precision
Conflict Disclosure Accuracy
Citation Precision / Recall
Answerability Accuracy
Abstention Precision / Recall
Authorization Leakage Rate
Prompt Injection Success Rate
Tool Safety Gate Bypass Rate
```

## 16. 知识诊断指标

```text
Knowledge Absent Diagnosis Precision
Retrieval Miss Diagnosis Precision
Parsing Failure Diagnosis Precision
Index Failure Diagnosis Precision
Graph Grounding Diagnosis Precision
Version Governance Diagnosis Precision
Authorization-limited Diagnosis Precision
False Operational Alert Rate
```

`KnowledgeHealthSignal` 只有被 Ingestion、Infrastructure、KnowledgeVersion 验证或人工调查确认后，才能形成健康事件 Ground Truth。

---

# Part IV：Eval 体系

## 17. Eval 层级

### 17.1 Component Eval

评测单模块：

- Query Rewrite；
- Entity Linking；
- Retriever；
- Fusion；
- Rerank；
- Evidence Relation；
- Conflict Classification；
- Probe Proposal；
- Citation Check；
- Tool Argument；
- Structured Output。

### 17.2 Trajectory Eval

评测过程：

- Plan 是否合理；
- 是否选择正确能力；
- 是否无意义循环；
- 是否在失败后恢复；
- 是否过早停止；
- 是否不必要调用 Graph / Global / 强模型；
- 是否遵守 Budget、Security 和 Approval。

### 17.3 End-to-End Eval

评测最终任务完成、答案、引用、成本、延迟和安全。

### 17.4 Fault Eval

注入：

- Provider 429 / timeout；
- Retriever unavailable；
- Queue duplicate；
- Worker crash；
- Checkpoint mismatch；
- Security Epoch change；
- Tool UNKNOWN Effect；
- stale Snapshot；
- invalid model JSON；
- late result。

## 18. EvalDataset

```yaml
EvalDataset:
  dataset_id: string
  name: string
  domain: string
  version: string
  task_types: [string]
  data_classification: string
  source_manifest_ref: string
  split_manifest_ref: string
  annotation_policy_ref: string
  license_ref: string | null
  status: DRAFT | REVIEWED | FROZEN | RETIRED
```

固定后不可原地改样本。修订创建新版本。

## 19. EvalCase

```yaml
EvalCase:
  case_id: string
  dataset_ref: string
  input_ref: string
  expected_outcome: ANSWER | PARTIAL | ABSTAIN | ASK_USER | REPLAN
  gold_claim_refs: [string]
  gold_evidence_refs: [string]
  acceptable_evidence_family_refs: [string]
  conflict_refs: [string]
  security_context_ref: string
  budget_profile_ref: string
  grading_policy_ref: string
```

无答案、冲突、权限受限和知识质量异常必须进入数据集，不只评测可回答问题。

## 20. Evidence Deliberation 专项数据集

至少包含：

- 简单事实，Hybrid 已充分；
- 关系问题，Graph Local 有增益；
- 全局主题，Community / Global 有增益；
- DRIFT 才能补足的递归问题；
- Community 与 Local 同源；
- GraphPath 缺 SourceSpan；
- 新旧版本冲突；
- 适用主体不同；
- 权威来源与非权威来源冲突；
- 无知识；
- 检索漏召回；
- 解析失败；
- 索引不可用；
- 权限限制；
- 连续 Probe 无增益。

## 21. BenchmarkProfile

```yaml
BenchmarkProfile:
  benchmark_profile_id: string
  dataset_refs: [string]
  environment_ref: string
  code_commit_sha: string
  model_route_policy_version: string
  prompt_version_set_ref: string
  retrieval_policy_version: string
  knowledge_snapshot_refs: [string]
  security_policy_version: string
  budget_profile_ref: string
  repetitions: int
  random_seed_policy: string
```

缺少 Commit、环境、数据集、模型、Prompt、Snapshot 和预算时，不构成可复现 Benchmark。

---

# Part V：实验、消融与 Release Gate

## 22. Agentic GraphRAG Baseline

至少比较：

```text
B0 Vector-only RAG
B1 BM25 + Vector Hybrid
B2 Fixed GraphRAG
B3 Agentic Routing
B4 Quality-first Evidence-Driven Agentic GraphRAG
```

按问题类型分别报告。可能出现：

- 简单 FAQ：B1 与 B4 接近，但 B4 成本更高；
- 关系问题：Graph Local 提升 Evidence Coverage；
- 全局问题：Global 有增益但成本高；
- 冲突问题：Evidence Reasoning 提升 Conflict Disclosure；
- 无答案问题：B4 提升 Abstention Accuracy。

只有真实结果才能填写结论，文档不预设胜负。

## 23. 消融

必须能单独关闭：

- Query Rewrite；
- Graph Local；
- Graph Global；
- DRIFT；
- Rerank；
- Evidence Critic；
- Source Family 去重；
- Targeted Probe；
- Answer Risk Review；
- Final Reflection。

消融用于判断提升来自架构机制还是更大 Token / Retriever Budget。

## 24. ReleaseGateDefinition

```yaml
ReleaseGateDefinition:
  gate_id: string
  scope: MODEL | PROMPT | RETRIEVAL | KNOWLEDGE_VERSION | AGENT_RUNTIME | TOOL | FULL_RELEASE
  required_benchmark_profiles: [string]
  blocking_metrics: map<string, threshold>
  non_regression_metrics: map<string, threshold>
  safety_requirements: [string]
  recovery_requirements: [string]
  cost_requirements: [string]
  approval_policy_ref: string
  version: int
```

## 25. ReleaseGateResult

```yaml
ReleaseGateResult:
  result_id: string
  gate_ref: string
  candidate_ref: string
  benchmark_run_refs: [string]
  status: PASS | FAIL | BLOCKED | INCONCLUSIVE
  failed_requirements: [string]
  evidence_refs: [string]
  approved_by_refs: [string]
  decided_at: datetime
```

`INCONCLUSIVE` 不能解释为 PASS。

---

# Part VI：数据质量、Judge 与归因

## 26. LLM Judge

LLM Judge 可用于语义评价，但必须：

- 固定 PromptVersion；
- 使用结构化输出；
- 记录模型与参数；
- 与人工标注校准；
- 测量一致性；
- 对高风险结论抽检；
- 不让 Judge 看到未授权 Evidence；
- 不用单一 Judge 决定发布。

## 27. 人工评测

需要明确：

- 标注指南；
- Claim 粒度；
- Evidence Support 定义；
- Conflict / Qualification；
- 不确定性；
- 多人一致性；
- 争议仲裁；
- PII 与权限。

## 28. 归因

每个质量变化必须能关联：

```text
code commit
configuration version
model and provider
prompt version
retrieval policy
knowledge snapshot
security context
budget
dataset version
```

否则只能说“观察到变化”，不能说某架构机制导致提升。

---

# Part VII：告警、保留与访问

## 29. 告警

高优先级：

- Authorization leakage；
- Tool Safety bypass；
- Run terminal state divergence；
- UNKNOWN Effect 长时间未对账；
- Checkpoint / Domain divergence；
- Unsupported Claim 激增；
- Citation 失效；
- Index / Parsing Diagnosis 经确认；
- Release Gate 失败仍被切流。

低优先级：

- Probe 成本上升；
- Graph 无效调用增加；
- Rerank Gold Demotion；
- Weak-to-strong 升级率变化。

## 30. Retention

- Audit 依合规策略长期保存；
- Trace 按环境和数据分类保留；
- 原始 Prompt / Response 需更严格权限和脱敏；
- Eval Artifact 可重现但不得泄漏生产数据；
- Secret 不进入任何 Trace；
- 删除请求需传播到受控 Artifact 与 Projection，但 Audit 按法规保留必要摘要。

---

# Part VIII：Current、Target、Gap 与完成证据

## 31. Current

以代码、测试、状态文档和实际 Trace 为准。本文不因为事件名称、指标定义、Eval Runner 或 Dashboard 存在而声明完整质量评测已经运行。

## 32. Target v2

- 统一 Trace Envelope；
- Evidence Deliberation 全过程事件；
- 检索、Evidence、Claim、Probe、Answer、Diagnosis 分层指标；
- 固定 Benchmark 和消融；
- 可复现 Release Gate；
- 安全、恢复、成本与质量联合判断。

## 33. Future

- 线上 Shadow Eval；
- 更成熟的 Counterfactual Replay；
- 自动 Failure Clustering；
- 但自动化结果仍受人工治理和 Release Gate 约束。

## 34. 测试与验证

必须覆盖：

- 事件 Schema；
- Correlation / Causation；
- Redaction；
- 多租户隔离；
- 重复事件幂等 Projection；
- late / out-of-order event；
- Metric correctness；
- EvalDataset versioning；
- Judge calibration；
- Benchmark reproducibility；
- Release Gate PASS / FAIL / BLOCKED / INCONCLUSIVE；
- Evidence 指标；
- Probe 信息增益；
- Diagnosis Precision；
- Fault Injection Trace 完整性。

## 35. Target 变为 Current 的证据

```text
事件 Contract 与 Migration
Trace Pipeline 与 Projection
Metric 实现
Eval Dataset / Runner
固定 Benchmark 运行结果
人工标注与 Judge 校准
Fault Injection
Dashboard / Alert
Release Gate 记录
文档与镜像同步
```

未具备完整测量、门禁和运行证据时，只能声明 `design available` 或 `measurement blocked/in progress`，不得声明 quality proven 或 production ready。
