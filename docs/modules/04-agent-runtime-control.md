# 04 Agent Runtime & Control（智能体运行与控制）

<!-- status: design-skeleton; implementation: not-authorized; native-runtime: measurement-gated -->

## Part A — Human Narrative

### 为什么复杂任务需要运行控制

简单问答没有必要启动一套复杂运行时：确认材料和权限、检索原文、生成带依据的答案并检查即可。运行控制真正有价值的场景，是任务需要跨多个步骤、等待人工、并行调用能力、在失败后继续，或者因为材料和能力变化而调整剩余计划。

这个模块解决的是“这次任务现在应该做什么、做到哪里、失败后怎样继续”，不是“法律世界最终承认什么”。

### 进入原生运行时以后，每个任务都有计划

进入 Zuno Native Agent Runtime（原生智能体运行时）的任务都必须有计划。简单但仍选择进入原生运行时的任务使用 Deterministic Single-Step Plan（确定性单步计划）；复杂任务使用 Dynamic DAG Plan（动态有向无环计划），把目标拆成有依赖关系的步骤。

这不是为了让简单任务变复杂，而是为了保证一旦进入自有运行控制，就不能通过 `direct_answer` 一类捷径绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。简单任务应通过一个很小的确定性计划完成，复杂任务才使用动态计划。

### 计划和步骤怎样工作

固定的 AgentRunGraph 管整次运行，动态计划描述“哪些步骤依赖哪些步骤”，固定的 StepExecutionGraph 管单个步骤内部的执行。Plan-and-Execute 负责整个任务的目标、依赖和并行；ReAct 只处理某个步骤里的行动与观察。

模型反思不是每一步都必须做。每个 Action 都要经过 Evaluation，每个 Step 都要经过 Acceptance；只有证据冲突、关键决策、重复失败、高风险或并行结果冲突时，才触发更强的 Step / Join Reflection。最终综合默认串行，简单任务使用确定性 Final Gate，复杂任务或 Strict Grounded Answer 才使用模型级 Final Reflection。

### 并行不是越多越好

一个步骤只有在依赖已经满足、输入稳定、资源不冲突、副作用可控、预算和配额足够、安全门禁允许时，才成为可安全并行的 Ready Step。

数据依赖、写同一资源、不可逆副作用、排他资源、重规划和最终综合默认串行。实现优先使用 LangGraph 原生的 Send、Reducer、Checkpointer 和 Subgraph 等原语，而不是先建设一套自定义分布式调度系统。

### 重试、重规划和对账为什么分开

模型 503 但计划仍正确，是 Retry（重试）；工具或能力语义变化导致原来的参数和依赖已经不成立，是 Replan（重规划）；外部请求已经发出但现实结果未知，是 Reconcile（对账恢复）。

把三者混在一起会产生危险行为：把计划错误当成临时故障会无限重试，把外部未知结果当成失败重试可能重复产生副作用。

### 计划版本为什么激活后不能改

复杂任务运行期间，旧分支可能还在并行执行。如果直接修改正在使用的计划，系统就无法解释一个结果究竟是基于哪套依赖产生的。因此 PlanVersion 激活后不可变；重规划创建新版本，并行中的重规划必须先经过 Replan Barrier，让旧分支停止获得继续提交新计划结果的资格。

晚到结果仍可以被记录或重新评估，但不能覆盖新计划或绕过当前领域和安全门禁。

### 运行状态和领域状态怎样分开

AgentRun、PlanVersion、StepRun、Branch、Budget、Interrupt 和 Checkpoint 属于运行控制状态。正式领域结果仍由法律领域提交。

如果某个步骤的完成条件要求 Formal Admission（正式准入），没有匹配的正式准入回执，运行时不能宣布该步骤正式完成。PostgreSQL 保存领域事实，LangGraph Checkpointer 保存图控制状态；领域提交成功而检查点失败时用回执修复控制状态，检查点完成而回执缺失时则不能反推正式准入成功。

### Single Controller 与多智能体的边界

Zuno 采用 Single Controller（单控制器）作为产品运行时原则，不默认建设自治的 Multi-Agent Runtime。Specialist Agent（专家智能体）或子图可以作为计划步骤出现，也可以在安全条件允许时并行，但它们只能返回候选、证据、观察或建议。

专家智能体不能直接提交领域事实、批准权限、激活计划版本、绕过预算、执行未审批副作用或直接提交长期记忆。只有确实需要独立跨父任务生命周期时，才有理由考虑独立线程/检查点；普通一次性 Specialist 优先继承父运行时的子图和 Checkpointer。

### 为什么这个模块仍然是条件能力

总体架构允许复杂任务使用原生运行时，但它是否比“通用宿主 + 法律后端”真正更有价值仍要通过 A/B/C 对照测量。如果真实任务证明普通 Host 足够，就应该缩小甚至删除自有运行时，而不是为了架构完整保留。

### 当前、目标与缺口

Current Runtime Baseline 已证明 AgentRunApplicationService → AgentRuntimeService → AgentRunStore / checkpoint → Agent Core graph 的主路径，以及持久化失败、approval interrupt、duplicate claim、cancel、restart、unknown effect reconcile 等有限语义。正式四 Profile runtime、真实 HA/fencing/takeover、复杂并行故障测试、完整 benchmark 和生产恢复仍未建立。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：Single Controller、AgentRun、Plan / PlanVersion、Step / StepRun、Branch、Budget control、parallel dispatch/join、Retry / Replan / Reconcile control、Interrupt / Resume、Checkpoint-based recovery、AnswerPolicy control、RunOutcome。

**Does not own**：Canonical Domain State、Authorization / Approval、Tool Effect truth、Capability semantics、Model provider policy、long-term Memory truth。

### B2 Core Control Invariants

- Native Runtime entrant always has a Plan；no direct-answer bypass of Plan / Trace / Budget / AnswerPolicy / RunOutcome.
- Simple = deterministic single-step；Complex = dynamic DAG.
- PlanVersion immutable after activation；Replan creates a new version.
- Ready Step 并行前检查 dependency / input / resource / effect / budget / quota / security。
- Data dependency / same-resource write / irreversible effect / exclusive resource / Replan / Final Synthesis 默认串行。
- Every Action has Evaluation；every Step has Acceptance；model Reflection is trigger-based.
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

不因模块存在就要求独立服务或独立数据库。优先使用 LangGraph 原生 checkpoint / interrupt / Send / reducer / subgraph 等机制，只有证据表明不足时才引入自定义调度、复杂分布式锁或新的协调协议。
