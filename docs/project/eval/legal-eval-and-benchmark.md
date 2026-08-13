# Legal Eval & Benchmark：怎样证明做得对？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 如何公平测量法律质量、效率和架构复杂度收益？
owner: Eval / Observability Owner
replaces: docs/project/modules/10-observability-eval.md（Superseded）

## Part A — Architecture Narrative

### 我们到底要证明什么

评测不是为架构已经正确寻找分数，而是要区分六个可被证伪的命题：Legal Capability 是否有价值，Legal Backend 是否比 Generic Host 更有价值，Native Runtime 是否带来额外收益，Graph 是否比 Hybrid 更有效，Multi-Agent 是否比更简单拓扑更好，Service Boundary 是否改善隔离或吞吐。一个 LLM Judge 分数不能同时回答这些问题。

### Target Scenario：控制变量比较

这是 Target Scenario，不是历史事实：

同一批案件材料、同一基础模型、同一外部工具、相近 Prompt/Skill、同一 Token/Time Budget 下，运行 A Generic Host、B Host + Zuno Legal Capabilities、C Zuno Native Runtime。每个 Variant 处理相同 QueryClass，保留 Evidence、Citation、Conflict、Applicability、Reviewer Decision、Latency、Token、Cost 和 Trace。只有这样，C 相对 B 的收益才可能归因于 Domain State、EvidenceRequirement、Staleness 或 Review 对账。

### 任务质量和工程效率

法律用户关心 Evidence Sufficiency、Citation Correctness、Unsupported Claim、Conflict/Dispute、Fact–Article、Applicability、Reviewer Acceptance 和 Task Completion。工程上还要看 Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls、Retry/Recovery 和 Domain State Reuse。Quality、Efficiency、Security 和 Complexity 必须同时报告，不能用一个综合分隐藏失败。

评测边界是：固定输入与预算，改变一个架构变量，记录结果、失败和成本，再把结论限制在该数据切片和协议内；评测不拥有产品或 Domain 状态。

Happy Path 是：冻结 DatasetVersion → 运行 Variant → 保存 RawResult/Trace → Reviewer/Metric → Comparison → Release Decision。

### 责任和非责任

Eval Owner 拥有 DatasetVersion、CaseSetHash、EvaluationRun、RawResult、Metric、Comparison、FailureClass 和 ReleaseDecision。评测不拥有 Domain Finding，不把历史 Demo 当成数据集，不把 LLM Judge 当作唯一裁判，也不把 blocked、unavailable 或 incomparable 折成零分。

### 失败、取舍与反转

数据切片、分母、Reviewer 标准或模型预算不一致会让比较失真；只测最终文本会漏掉引用错误、恢复失败和成本上升。评测基础设施和人工标注成本很高，但没有它就无法证明复杂度值得存在。若 C≈B>A，应保留 Legal Backend、缩减 Native Runtime；若 C≈B≈A，删除未证明的复杂度；若 Graph、Multi-Agent 或服务拆分无增益，分别退回更简单方案。

### Current / Target / Gap

Current 只有已执行的 Eval、Trace 和报告才成立；Target 是可复现 A/B/C、Graph Kill、Multi-Agent Ablation 和 Service Evidence；Hypothesis 是 Domain/Evidence/Runtime 的因果链可测；Gap 是 Court QA、Reviewer Protocol、重复运行、统计不确定性、成本和真实部署指标。

## Part B — Detailed Architecture Specification

### Evaluation Run Contract

EvaluationRun 固定 DatasetVersion、CaseSetHash、Variant、Model、Prompt/Skill、Capability、Tool/Provider、Token/Time Budget、QueryClass、Random Seed、Retrieval Rounds 和 Reviewer Protocol。RawResult、Metric、FailureClass、Comparison、Artifact 和 ReleaseDecision 分开保存；每条结果引用 Trace 和 Evidence Lineage。

### A/B/C and ablation

| Variant | 固定项 | 变化项 |
|---|---|---|
| A | Model、Raw Corpus、Tools、Prompt/Skill、预算 | Generic Host |
| B | A 的全部固定项 | Host + Zuno Legal Capabilities |
| C | A/B 的全部固定项和同一能力 | Native Runtime + first-class Domain State |

Graph Ablation 比较 Fixed Vector、Fixed Hybrid、Always Graph、Agentic RAG 和 Conditional Graph；Multi-Agent Ablation 比较 Single Agent、Role Pipeline、Ephemeral Worker 和 Specialized Agent；Service Ablation 比较模块化 Worker 与独立服务的隔离、吞吐和运维代价。

### Metrics and denominator

Quality 包括 Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict/Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance 和 Task Completion。Efficiency 包括 Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls、Retry、Recovery、State Reuse。BLOCKED、UNAVAILABLE、INCOMPARABLE 必须单独报告，不能变成零分或 PASS。

### Reviewer、统计与发布门

数据集版本、分层切片、参考答案、Reviewer Agreement、重复运行和置信区间必须可追溯。Release Gate 至少检查数据完整、引用正确、Unsupported Claim、严重失败、安全证据、预算和可复现性；Gate 通过也只证明指定协议，不等于 Production Ready。

### Evidence and implementation gap

公开论文和官方代码只作为 PUBLIC_CONTEXT，不能推出 Zuno 已集成或复现。真实 Court QA、标注、Reviewer、A/B/C 结果、故障和成本证据缺失时，Runtime、Graph、Multi-Agent 和服务收益都保持 Hypothesis。
