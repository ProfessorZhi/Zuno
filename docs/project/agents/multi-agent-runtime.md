# Multi-Agent Runtime：Agent 怎样协作而不复制业务代码？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 多个 Agent Profile 如何共享 Domain、Capability、Knowledge、Security 和 Eval，而不形成自治社会？
owner: Multi-Agent Runtime Owner
replaces: docs/project/modules/06-agent-core-planning-control.md 中的多 Agent 旧描述（Superseded）

## Part A — Architecture Narrative

### 为什么一个 Agent 有时不够

复杂案件的证据整理、争议识别和法律检索往往可以并行，但并行不等于把三个“聪明角色”放在一起自由对话。真正需要解决的是：这些工作能否使用各自的资料范围和工具权限，又能否在同一个案件版本上汇合。若每个角色都能修改事实或重新规划整个 Run，协调本身会比分析更难。

### 一个受控并行的目标场景

以下是 Target Scenario，不是历史事实。Coordinator 为一个 Matter 建立 Plan，把证据整理、争议识别和法律研究分派给三个短生命周期 Worker。每个 Worker 使用自己的 Knowledge Scope 和 Capability Binding，返回候选证据、EvidenceRequirement 或 ReplanRequest。Join 等待必需分支，先检查它们是否基于同一个 DomainVersion，再决定合并、局部重跑还是重新规划。即使三个分支都成功，最终也只能提交 Proposal；共享的 Domain Kernel 仍由 Domain Owner Admission 形成 Canonical State。

这里保留单一 Coordinator 是一种克制。若两个控制者都能激活 Plan、决定 Replan 或结束 Run，我们还要设计控制者之间的一致性协议，把任务执行升级成分布式共识问题。当前没有这样的产品需求，所以并行只发生在受控 Step 和 Worker 层，Run Control Authority 仍然只有一个。

### 选择等级，而不是追求更多 Agent

L0 Single Agent、L1 Role Pipeline 和 L2 Ephemeral Worker 应覆盖大多数任务。L3 Specialized Domain Agent 只有在角色、权限和能力边界稳定后才有意义；L4 Persistent Agent Team 还需要独立 SLA、资源池、发布生命周期和安全证据。我们不把更高自治等级当作默认 Future，因为它们会放大记忆污染、授权和恢复成本。

### 失败路径决定是否保留并行

如果 Evidence Worker 超时，Join 不能只等到一个时间点再把空结果当成功；它要知道该分支是必需还是可选。如果某个分支发现新的证据要求，Coordinator 可能需要补一个 Step；如果两个分支分别基于 DomainVersion V12 和 V13，它们不能直接拼成一个 Finding。重试也不是无条件的：已经请求外部工具的分支必须先经过 Tool/Security 对账。一个强 Agent 加 parallel tools 或 L1 Pipeline 可能更便宜，只有受控并行确实改善证据充分性、时延或复核质量，才值得保留更高等级。

仓库和测试能够证明的只是部分执行表面；Current 并没有证明一个完整的生产 Agent Team。同一 Runtime Service 中的 Profile/Worker 是 Target，L0-L2 是优先路径。并行带来收益是 Hypothesis，Join 正确性、共享 DomainVersion、恢复、成本和独立 SLA 仍是 Gap。

这也是为什么我们把更高等级留在可逆的设计空间，而不是把它当成默认部署形态。

Runtime 仍然需要记录每个 Worker 的输入版本和权限上下文，才能在恢复时说明哪个结果可以继续使用。

这项约束属于 Target Contract；仓库当前没有因此产生 Production Evidence。

## Part B — Detailed Architecture Specification

### Delegation Contract

Coordinator 发送 DispatchGroup/DispatchItem，包含 RunId、PlanVersion、DomainSnapshot、DomainVersion、WorkerProfile、KnowledgeScope、CapabilityBinding、PermissionScope、Budget 和 Idempotency Key。Worker 输出 BranchResultRef、Proposal、EvidenceRequirement、blocked、failed 或 ReplanRequest，不直接提交 Canonical Domain State。

### Join、Reducer 与版本

Reducer 只合并 typed BranchResultRef；Join 维护 required/optional branch、completion、timeout、failure 和 input DomainVersion。发现版本不一致时返回 domain_version_conflict，要求重读 Snapshot、Replan 或 Human Review。Join 完成不等于 Finding accepted。

### Retry、Replan 与资源

Transient Step 可以在同一输入下 bounded retry；新证据、权限变化、预算变化或新依赖要求使用 Replan。Worker Profile 默认在 Agent Runtime Service 内运行；只有独立 deployment、SLA、安全边界或资源池有证据时才拆成物理服务。每个分支受并发、Token、Time、Tool 和 Queue Budget 限制。

### Security、Memory 与 Audit

Dispatch 不能提升权限；每个 Worker 使用 downscoped SecurityEpoch、Matter Scope 和 Knowledge Scope。Memory 只能作为受策略约束的 Context，不能变成 Canonical Fact。Audit 保存分派、输入版本、结果引用、失败、重试、Join 和人工决定；不保存隐藏思维链。

### Evaluation and reversal

至少比较 L0 Single Agent、L1/L2 controlled workers 与更高等级；固定模型、语料、工具和预算，测 Evidence Sufficiency、Conflict/Dispute、Latency、Cost、Recovery 和 Reviewer Acceptance。若 parallel tools 已达到相同结果，删除额外 Worker；若角色独立化没有 SLA、资源或安全证据，不拆成服务。
