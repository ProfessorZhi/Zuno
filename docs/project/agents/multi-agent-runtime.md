# Multi-Agent Runtime：Agent 怎样协作而不复制业务代码？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 多个 Agent Profile 如何共享 Domain、Capability、Knowledge、Security 和 Eval，而不形成自治社会？
owner: Multi-Agent Runtime Owner
replaces: docs/project/modules/06-agent-core-planning-control.md 中的多 Agent 旧描述（Superseded）

## Part A — Architecture Narrative

### Multi-Agent 的真实定位

Multi-Agent 不是默认的自治社会，也不是每个角色一套法律业务代码。它是一种受 Coordinator、Plan、Budget、Permission、Review 和 Eval 约束的执行拓扑。角色的差异来自 Role、Skill、Knowledge Scope、Capability Binding、Tool Permission、Memory Policy 和 Model Policy；Domain Kernel 与专业 Capability Contract 仍然共享。

它解决的问题是：一个复杂案件既需要独立的证据、争议和法律研究视角，又不能让多个控制者争夺同一个 Run 或让每个角色复制一套法律事实逻辑。

### Target Scenario：受控并行协作

这是 Target Scenario，不是历史事实：

Coordinator 根据一个复杂 Matter 创建 Plan，先分派 Evidence Worker、Dispute Worker 和 Legal Research Worker。每个 Worker 使用自己的 Scope 和能力绑定，返回 BranchResultRef、EvidenceRequirement 或 ReplanRequest。Reducer/Join 等待必需分支，检查 DomainVersion 是否一致，再根据冲突或证据缺口触发 Reflection/Join Review。最后只生成 Proposal，交给 Domain Owner Admission；Coordinator 仍然是唯一的 Run Control Authority。

### Levels 与选择边界

目标等级只定义 L0 Single Agent、L1 Role Pipeline、L2 Ephemeral Worker、L3 Specialized Domain Agent、L4 Persistent Agent Team。L0-L2 应优先覆盖大多数场景；L3 需要稳定角色、权限和专业能力边界；L4 需要独立 SLA、资源池、发布生命周期和安全证据。设计不设更高自治等级，也不把 Agent Society 作为目标或默认 Future。

### 责任和非责任

Coordinator 拥有 Dispatch、Join、Budget、Replan 和最终 RunOutcome；Worker 只拥有自己的 Step Result 和 Proposal；Domain Owner 拥有 Canonical State；Knowledge、Security、Tool 和 Eval 维持各自边界。Multi-Agent 不负责复制法律算法、直接写 Domain、共享未经授权的 Memory 或自行扩张权限。

### 失败故事与简单替代

Evidence Worker 超时，Join 必须区分可选分支和必需分支；分支发现新 EvidenceRequirement，Coordinator 需决定补充 Step 或 Replan；两个分支基于不同 DomainVersion，则不能直接合并；分支请求外部 Tool，必须回到 Security/Tool Gate。一个强 Agent 加 parallel tools 或 L1 Role Pipeline 可能已足够，只有受控并行能改善证据充分性、时延或复核质量才保留更高等级。

### Current / Target / Gap

Current 只由代码、测试和运行证据证明；Target 是同一 Runtime Service 中的 Profile/Worker 模型，优先 L0-L2，必要时支持 L3-L4；Hypothesis 是受控并行可改善复杂案件任务；Gap 是角色消融、Join 正确性、共享 DomainVersion、成本、恢复和独立 SLA 证据。

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
