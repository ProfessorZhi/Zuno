# 04 Agent Runtime & Control（智能体运行与控制）

<!-- status: design-skeleton; implementation: not-authorized; native-runtime: measurement-gated -->

## Part A — Human Narrative

### 为什么复杂任务需要运行控制

简单问答没有必要启动一套复杂 Agent Runtime：确认材料和权限、检索原文、生成带依据的答案并检查即可。运行控制真正有价值的场景，是任务需要跨多个步骤、等待人工、并行调用能力、在失败后继续，或者因为材料和能力变化而调整剩余计划。

这个模块解决的是“这次任务现在应该做什么、做到哪里、失败后怎样继续”，不是“法律世界最终承认什么”。

### 一个复杂任务怎样被控制

进入 Zuno Native Agent Runtime（原生智能体运行时）的任务都要有 Plan（计划）。简单但仍进入原生运行时的任务使用 Deterministic Single-Step Plan（确定性单步计划）；复杂任务使用 Dynamic DAG Plan（动态有向无环计划）。

总体形态保持：固定 AgentRunGraph 管理整次运行，动态 Plan DAG 表达任务依赖，固定 StepExecutionGraph 管理单个步骤。Plan-and-Execute 负责目标、依赖和并行；ReAct 用在单个 Step 内的行动与观察；Reflection 只在质量风险触发时调用；Replan 在原计划假设失效时创建新的剩余计划；任务结束后的 Reflexion 只能产生长期经验候选，不能直接写入长期记忆。

### 并行不是越多越好

Ready Step 只有在依赖、输入、资源冲突、副作用、预算、配额和安全门禁都允许时才并行。数据依赖、同一资源写入、不可逆副作用、排他资源、重规划和最终综合默认串行。

每个 Action 都需要 Evaluation，每个 Step 都需要 Acceptance；但不是每一步都调用模型反思。证据冲突、关键决策、重复失败、高风险或并行结果冲突时，才触发更强的 Step / Join Reflection。

### 重试、重规划和对账为什么分开

模型 503 但计划仍正确，是 Retry（重试）；工具或能力语义变化导致原来的参数和依赖已经不成立，是 Replan（重规划）；外部请求已经发出但现实结果未知，是 Reconcile（对账恢复）。

把三者混在一起会产生非常危险的行为：把计划错误当成临时故障会无限重试，把外部未知结果当失败重试可能重复产生副作用。

### 运行状态和领域状态怎样分开

AgentRun、PlanVersion、Step、Branch、Budget、Interrupt 和 Checkpoint 属于运行控制状态。PlanVersion 激活后不可变；重规划创建新版本，并行中的重规划需要先建立 barrier，避免旧分支继续污染新计划。

正式领域结果仍由法律领域提交。如果某个 Step 的完成条件要求 Formal Admission（正式准入），没有匹配的正式准入回执，运行时不能宣布该 Step 正式完成。PostgreSQL 保存领域事实，LangGraph Checkpointer 保存图控制状态，两者通过耐久回执对账，而不是共享一个“总状态”。

### Single Controller 与多智能体的边界

Zuno 采用 Single Controller（单控制器）作为产品运行时原则，不默认建设自治的 Multi-Agent Runtime。Specialist Agent（专家智能体）或子图可以作为某个计划步骤出现，也可以在安全条件允许时并行，但它们只能返回候选、证据、观察或建议，不能直接提交领域事实、批准权限、绕过预算或执行未审批副作用。

### 为什么这个模块仍然是条件能力

总体架构允许复杂任务使用原生运行时，但它是否比“通用宿主 + 法律后端”真正更有价值仍要通过 A/B/C 对照测量。模块边界已经定义，Native Runtime 本身仍是 measurement-gated：如果真实任务证明普通 Host 足够，就应该缩小甚至删除自有运行时，而不是为了架构完整保留。

### 当前、目标与缺口

Current Runtime Baseline 已证明 AgentRunApplicationService → AgentRuntimeService → AgentRunStore / checkpoint → Agent Core graph 的主路径，以及持久化失败、approval interrupt、duplicate claim、cancel、restart、unknown effect reconcile 等有限语义。正式四 Profile runtime、真实 HA/fencing/takeover、完整 benchmark 和生产恢复仍未建立。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：Single Controller、AgentRun、Plan / PlanVersion、Step / StepRun、Branch、Budget control、parallel dispatch/join、Retry / Replan / Reconcile control、Interrupt / Resume、Checkpoint-based recovery、RunOutcome。

**Does not own**：Canonical Domain State、Authorization / Approval、Tool Effect truth、Capability semantics、Model provider policy、long-term Memory truth。

### B2 Core Control Invariants

- Native Runtime entrant always has a Plan.
- Simple = deterministic single-step；Complex = dynamic DAG.
- PlanVersion immutable after activation；Replan creates a new version.
- Ready Step 并行前检查 dependency / input / resource / effect / budget / quota / security。
- Replan 与 Final Synthesis 默认串行。
- Formal Admission-required Step 必须消费 matching AdmissionReceipt 才能正式完成。
- Specialist outputs are proposals / observations / evidence refs, not canonical commits.

### B3 Inputs / Outputs

输入：task goal / scope、domain / knowledge references、capability availability、model eligibility、security decisions、tool receipts、human interrupt result、budget / quota。

输出：PlanVersion、Step dispatch、ControlDecision、RunOutcome、checkpoint、proposal / evidence references、对下游的受控调用。

### B4 State / Lifecycle

至少覆盖 Run、PlanVersion、StepRun、Branch/Join、Interrupt、Budget、ControlDecision 和 Checkpoint。具体 enum 在模块深设计时冻结，但必须能表达 active plan version、terminal run outcome、stale branch / late result、retry attempt、replan barrier 和 reconciliation wait。

### B5 Failure / Recovery / Idempotency

Retry：计划仍成立，仅执行失败。

Replan：依赖、能力、假设或结构已失效。

Reconcile：外部现实结果未知。

Restart：从 checkpointer 恢复控制状态，再用 Domain / Effect / Audit receipts 对账。Late branch 必须带原 PlanVersion / causation identity，不能覆盖新版本。

### B6 Security / Persistence / Observability

受保护的材料读取、模型外发、工具执行和正式准入前重新检查当前安全决定。Checkpointer 只保存控制状态；正式领域事实、外部效果和关键审计保持各自耐久边界。Trace 记录 run/step correlation，但不替代 Receipt。

### B7 Current / Target / Gap

Current 见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md)。Target 是上面的 Single Controller + Plan/Step 控制模型。Gap：A/B/C benchmark、复杂并行 fault test、HA/fencing/takeover、真实四 Profile runtime、formal admission recovery E2E。

### B8 Code / Database / Migration Constraints

不因模块存在就要求独立服务或独立数据库。优先使用 LangGraph 原生 checkpoint / interrupt / subgraph / reducer 等机制，只有证据表明不足时才引入自定义调度、锁或分布式协调。
