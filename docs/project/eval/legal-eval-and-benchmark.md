# Legal Eval & Benchmark：怎样证明做得对？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 如何公平测量法律质量、效率和架构复杂度收益？
owner: Eval / Observability Owner
replaces: docs/project/modules/10-observability-eval.md（Superseded）

## Part A — Architecture Narrative

### 评测要回答哪一个问题

评测最容易犯的错误，是把一个总分当成架构证明。我们真正想知道的是：Legal Capability 是否有增益，Legal Backend 是否比 Generic Host 更好，Native Runtime 是否比 Host + Backend 多带来价值，Graph、Multi-Agent 和服务拆分是否值得它们的成本。这些是不同的假设，必须有不同的对照和失败解释。

### 一个可复现的目标比较

以下是 Target Scenario，不是历史事实。用同一批案件材料、基础模型、外部工具、相近 Prompt/Skill 和 Token/Time Budget，运行 A Generic Host、B Host + Zuno Legal Capabilities、C Zuno Native Runtime。三者处理同一 QueryClass，留下证据、引用、冲突、适用性、Reviewer Decision、Latency、Token、Cost 和 Trace。只有在这些变量被控制后，C 相对 B 的差异才可能归因于 Domain State、EvidenceRequirement 或 Staleness，而不是更大的预算。

### 结果怎么被解释

法律质量至少要看 Evidence Sufficiency、Citation Correctness、Unsupported Claim、Conflict/Dispute、Fact–Article、Applicability、Reviewer Acceptance 和 Task Completion；工程成本还包括 Latency、Token、Model Calls、Retrieval Rounds、Tool Calls、Retry/Recovery 和 Domain State Reuse。某个变体如果因为服务不可用而没有结果，不能把它折成零分再宣称质量差；它应该保留为 blocked 或 incomparable。

评测的正常路径是冻结 DatasetVersion，运行变体，保存 RawResult 和 Trace，再由 Reviewer 与 Metric 形成 Comparison。Eval Owner 拥有这些评测事实，但不拥有产品 Finding，也不把历史 Demo 自动当作数据集。人工标注和重复运行确实昂贵，却是判断复杂度是否值得保留的必要成本；如果某个变体因 Provider outage 或权限阻断没有结果，它必须保留阻塞原因，不能被悄悄放进失败分母。

失败时，最危险的不是一次分数偏低，而是比较条件悄悄变化：数据切片不同、Reviewer 标准不同、模型预算不同，或者只看最终文本而漏掉引用和恢复错误。若 C≈B>A，应保留 Legal Backend 并缩减 Native Runtime；若 C≈B≈A，就删除未经证明的复杂度。Graph、Multi-Agent 和 Service Boundary 也必须接受各自的消融测试。

已执行的 Eval、Trace 和报告才构成 Current；可复现 A/B/C、Graph Kill、Multi-Agent Ablation 和 Service Evidence 是 Target。因果链能否测出增益是 Hypothesis，Court QA、Reviewer Protocol、重复运行、统计不确定性、成本和真实部署指标仍是 Gap。

评测结论只对协议覆盖的任务切片负责；它不会替项目或 Domain Owner 代替业务决策。

每次比较都应保留原始输入、失败分类和预算记录，使后来的人能够复核我们究竟比较了什么。

没有这些记录，分数再高也只能算一次不可复现的观察。

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

### Attribution and fault evidence

一次 Run 的 retry、fallback、replan、人工暂停和恢复都要在 Trace 中区分 Attempt 与最终 Task。比较 Native Runtime、Graph、Memory 或服务拆分时，必须固定模型、语料、工具、预算和 Reviewer Protocol，并分别报告缺失 Span、阻塞 Run、不可比样本和故障注入覆盖。只有结果可归因时，才允许把复杂度写成 Measured；否则保持 Hypothesis 或 Measurement Gap。

### Reviewer、统计与发布门

数据集版本、分层切片、参考答案、Reviewer Agreement、重复运行和置信区间必须可追溯。Release Gate 至少检查数据完整、引用正确、Unsupported Claim、严重失败、安全证据、预算和可复现性；Gate 通过也只证明指定协议，不等于 Production Ready。

### Evidence and implementation gap

公开论文和官方代码只作为 PUBLIC_CONTEXT，不能推出 Zuno 已集成或复现。真实 Court QA、标注、Reviewer、A/B/C 结果、故障和成本证据缺失时，Runtime、Graph、Multi-Agent 和服务收益都保持 Hypothesis。
