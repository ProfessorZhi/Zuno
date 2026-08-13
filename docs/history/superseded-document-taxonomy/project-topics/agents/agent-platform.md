# Agent Platform：怎样计划、执行和组合能力？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Agent 如何在单一控制权下计划、并行执行、恢复、复核并提交领域 Proposal？
owner: Agent Runtime Owner
replaces: docs/project/modules/06-agent-core-planning-control.md、07-capability-skill.md（Superseded）

## Part A — Architecture Narrative

### 为什么需要 Agent Runtime

复杂法律任务不是一次 Retrieve → Model → Answer。系统可能需要拆分证据要求、并行检索、识别冲突、调用法律能力、等待人工决定，并在材料或权限变化后重新规划。Runtime 的价值是控制这些步骤的顺序、预算、恢复和最终 Gate；它不因为调用了模型就拥有法律事实。

### Target Scenario：一次复杂任务的生命周期

这是 Target Scenario，不是历史事实：

Coordinator 接收 Matter Snapshot 和任务，创建不可变 PlanVersion。Plan Activation 先确认权限、预算和 EvidenceRequirement，再调度并行 Step Execution：Evidence Step、Dispute Step 和 Legal Research Step。各分支返回 BranchResultRef；Reducer/Join 检查是否满足证据门，必要时触发 Reflection 或 Replan，随后生成 FactProposal、ConflictProposal 或 FindingProposal。Domain Owner 决定是否 Admission，Review 结束后 Runtime 只记录 RunOutcome。

### Single Controller 的含义

Single Controller 不等于 Single-thread，也不等于没有并行。它表示只有一个 Control Authority 负责 Plan Activation、Budget、Approval、Replan、Final Gate 和 RunOutcome；并行发生在 Step Execution 和受控 Worker 中。这样可以避免多个 Coordinator 争夺同一个 Run 的 authority，同时仍允许独立检索和法律研究并行。

### 三层执行模型

Fixed AgentRunGraph 提供可观测的运行骨架；Dynamic Plan DAG 表达任务依赖、EvidenceRequirement 和 Replan；Fixed StepExecutionGraph 约束单个 Step 的 Action → Observation → Decision 循环。三层分开后，Graph 控制可以替换，业务 Domain State 仍由 Domain Owner 保存。

### 五种机制各自解决不同问题

Plan-and-Execute 处理任务分解和依赖；ReAct 处理一个 Step 内的 Action/Observation；Reflection 判断结果是否满足质量或证据门；Replan 改变任务结构或前提；Reflexion 只产生可审查的事后经验候选。Retry 是对同一输入的受控重试，Replan 是输入、依赖或假设改变后的新 Plan，二者不能混写。

### 失败、取舍与反转

模型超时、工具 outcome_unknown、Evidence 不足、DomainVersion 改变或预算耗尽都可能阻止 Run。Runtime 必须让失败显式传播，不能将空答案视为成功；如果并行分支看到不同 DomainVersion，Join 不能用到达顺序强行拼接，而要等待版本屏障后的局部重跑或 Replan。LangGraph 可以提供 Durable Execution，但 Plain Python、State Machine、Pi 或其他 Provider 也可以实现同一 Contract。若 A/B/C 证明 WorkBuddy + Legal Backend 已经获得同样的质量、恢复和效率，Native Runtime 应被缩减或删除。

### Current / Target / Gap

Current 只由仓库代码、测试、Trace 或实际运行证明；Target 是 Python Agent Runtime、Single Controller、可组合 Profile 和可替换 Orchestration Provider；Hypothesis 是 Domain-aware Planning、State Reuse 和 Evidence Gate 带来额外收益；Gap 是恢复、预算、并发、模型调用、人工暂停和 Native Runtime Benchmark。

## Part B — Detailed Architecture Specification

### Runtime Contract

输入是 RunId、MatterId、Task、DomainSnapshot、PlanVersion、SecurityEpoch、Budget、Capability Binding 和 Knowledge Scope；输出是 StepResult、Proposal Reference、RunOutcome、Checkpoint Reference 或 typed failure。Runtime 不直接写 FactVersion、FindingVersion、HumanDecision 或 WorkProduct。

### State and control

AgentRun、PlanVersion、StepRun、DispatchGroup、Branch、Reducer、Interrupt、BudgetLedger、Checkpoint 和 ResumePosition 属于 Runtime Owner。PlanVersion 激活后不可变；Replan 创建新版本并记录原因；Checkpoint 只保存控制状态、可恢复输入引用和 Provider Receipt，不保存隐藏思维链或 Canonical Fact。

### Replan barrier and recovery

Coordinator 只有在确认当前 DomainVersion、权限 Epoch 和外部 Effect 状态后，才能把旧 Plan 标记为 stale。已经完成且没有受影响的只读分支可以复用；依赖新版本或存在未知副作用的分支必须重读 Snapshot、局部重跑或进入 reconciliation。新 Plan 继承剩余 Budget，但不会继承旧 Plan 的执行权；Final Gate 只接受当前 PlanVersion 的结果引用。

### Failure propagation and retry

Failure 分类至少包括 transient_provider、timeout_unknown、version_conflict、permission_revoked、evidence_insufficient、budget_exceeded、cancelled 和 unrecoverable。只有同一输入、无外部副作用或已有幂等保证的 transient work 才可 retry；version、evidence 或 permission 改变时必须 replan、review 或 fail closed。

### HITL、security and observability

Interrupt 绑定 Run、PlanVersion、DomainVersion、SecurityEpoch、review request 和 expiry。Resume 前重新读取 Domain、权限和 Evidence；审计保存可见决策、步骤、版本、receipt、错误和人工决定，不保存隐藏思维链。每个 Step 关联 Trace、Model/Capability Provider、Tool Call、Token/Time Budget 和结果引用。

### Provider boundary and testing

LangGraph 只作为 Runtime orchestration Provider；它不能承载普通 CRUD 或 Canonical Domain Fact。替换测试需要比较 resume、interrupt、parallel join、replan、idempotency、recovery 和 observability。Target 的质量、效率和成本收益必须由匹配预算的 A/B/C 评测证明。
