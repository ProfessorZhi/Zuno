# 04 Agent Runtime & Control（智能体运行与控制）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块解决的是“长任务怎样继续”，不是“让很多 Agent 自己商量”

复杂法律任务可能包含材料检查、检索、专业分析、并行比较、人工等待、外部 Tool 和正式提交。真正困难的不是把这些步骤串起来一次跑通，而是在材料变化、权限变化、部分失败、进程重启和晚到结果同时存在时，仍然知道下一步应该做什么。

04 因此拥有运行控制，而不是所有业务事实。它负责一次 Run 的计划、Step、并行、等待、预算、取消、重规划和 Checkpoint；Domain、Knowledge、Security 和 Effect 仍由各自 Owner 决定更强事实。

### 最简单的 while-loop Agent 为什么难以恢复

最简单 Agent 可以不断把当前上下文交给模型，让模型决定下一步 Tool，直到输出 final answer。短任务和低风险实验完全可以这样实现。

长任务中，这种隐式控制状态很难回答：模型崩溃前已经决定了什么；两个并行 Specialist 的结果属于哪个计划版本；新证据进入后旧任务还能不能接受；外部动作 timeout 后该不该再次执行。把所有历史都塞进 message list，也无法自然得到稳定的并发和恢复语义。

### Single Controller 为什么是控制权约束，不是“只有一个模型”

Zuno Target 采用 `Single Controller`：只有一个控制面有权激活计划版本、接受 Step 结果、决定 Retry / Replan、管理 Budget 和发出 cancel。专业执行单元仍然可以并行，甚至可以由不同模型或 Capability 实现。

这样做不是否定 Multi-Agent，而是避免多个自治 Agent 同时修改全局计划。执行可以多写，控制必须单写，才能让计划演进和恢复拥有唯一因果顺序。

### 为什么需要三层 Graph，而不是把所有动态性塞进 LangGraph 拓扑

长期运行既需要一个稳定宿主生命周期，也需要任务级动态计划，还需要单个 Step 内稳定执行边界。Target 因此保持 `Fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph`。

外层 RunGraph 管启动、恢复、终止等稳定阶段；Plan DAG 表达某个任务当前真正的动态依赖；StepExecutionGraph 管一个 Step 内部的执行、验收和必要的模型 / Capability 调用。这样动态计划不会要求每次 Replan 都重建宿主拓扑。

### 为什么 PlanVersion 激活后不能原地修改

计划一旦开始派发，就已经有 Worker、模型和外部调用绑定到它。如果在原对象上修改 Step、参数或依赖，晚到结果会失去“我当时基于什么计划计算”的身份。

因此保持 `PlanVersion immutable after activation`。需要改变计划时创建新版本，并明确哪些旧工作可以继续、哪些结果必须重新验收。不可变版本保护的是因果，不是为了增加版本号。

### Ready Step 为什么不能只看“前驱 completed”

一个 Step 是否能执行，不只取决于拓扑前驱结束。它还可能需要当前材料版本仍有效、Capability / Model 当前有资格、预算充足、权限仍允许，以及输入没有因为 Replan 变旧。

所以 Ready 判断本质上是多个 Owner facts 的组合。04 可以消费这些事实形成控制决定，却不能缓存一次 READY 后永久复用。

### 并行和 Join 为什么最容易暴露控制语义问题

并行 Specialist 可以提高吞吐或覆盖，但不同分支可能失败、取消、晚到，甚至属于已经被替换的旧 Plan。Join 不能只数“收到几个结果”，还要确认每个结果是否属于当前 barrier、是否通过 Step acceptance、是否满足最小证据和质量要求。

因此并行是控制优化，不是业务真相。一个分支计算成功，如果输入版本或 Plan 已过期，仍然可能被拒绝或重新评估。

### Step 执行成功为什么不等于业务完成

Runtime 可以验证 schema、Capability acceptance、模型结果和控制条件，但 Formal Admission-required Step 只有拿到 Domain 的匹配 Receipt 才能被视为正式业务提交完成。

这个边界避免 Checkpoint 抢走 Domain 权威。04 保存“我已经观察到并接受哪个 Owner fact”，而不是自己创造更强成功。

### Retry != Replan != Reconcile

Retry 适用于同一动作假设仍然成立，只是遇到暂时故障，例如模型 503。Replan 适用于计划假设已经失效，例如新材料改变依赖、Tool schema 更新或某条路线长期不可用。

Reconcile 解决的是过去现实动作结果未知，例如 POST 已经发出但 timeout。04 可以暂停等待 06 对账，却不能用 Replan 或 Retry 把未知现实效果覆盖掉。三种机制分开，控制面才能对失败做正确分类。

### Replan Barrier 为什么需要一个清楚的切换点

新 PlanVersion 产生以后，旧计划可能还有并行任务在运行。如果 Controller 一边接受旧结果一边按新计划派发，而没有稳定 barrier，就会产生“半个旧计划 + 半个新计划”的混合状态。

`Replan Barrier` 表达一个控制切换边界：哪些旧工作允许完成、哪些应取消、哪些 late result 需要重新验收，以及新计划从哪个因果点开始。它保护计划版本之间的可解释性，而不是要求停止所有在途工作。

### Late Result 为什么既不能一律丢，也不能一律收

旧 Plan 的纯计算结果如果输入版本仍然相同，也许仍有价值；如果材料、权限或业务预期已经变化，直接接受就会污染新计划。现实 Effect 更不能因为 branch stale 就被否认，因为远端动作可能已经发生。

所以 late result 需要按结果类型重新验收：纯计算检查 causation / freshness；正式 Domain 结果查询 Owner Receipt；现实 Effect 继续由 06 确认。是否“晚”只是时间事实，不自动决定业务资格。

### Checkpoint 为什么是恢复工具而不是业务数据库

Checkpoint 保存控制面为了恢复需要的 Run / Plan / Step 状态，使进程重启后不必从头重算。但它可以比 Domain、Effect 或 Security 的权威事实更旧。

恢复时先读取相应 Owner durable fact，再修复 Checkpoint projection。尤其 Domain commit 已成功但 Checkpoint 失败时，不能因为控制状态落后就重复正式提交。

### Interrupt / Resume 为什么必须带新鲜度检查

人工等待可能持续数小时甚至数天。恢复时，原 Plan、材料、Capability 版本、SecurityEpoch 和 Approval 都可能变化。

因此 resume 不是“从暂停行下一行继续”。Controller 要重新判断仍然适用的条件；无效 Approval 重新申请，过期输入触发 Replan，需要正式提交的结果重新检查 expected DomainVersion。

### Lease 和 Fencing 为什么只解决 Controller 所有权，不解决业务正确性

如果进程崩溃，另一个 Worker 可能接管 Run。Lease / fencing 可以防止两个 Controller 同时写控制状态，但它不能证明某个 Tool Effect 没有发生，也不能替 Domain 判定正式事务。

这类机制应当保持窄：只保护 Runtime 控制面的单写者语义。跨 Owner 的业务完成仍依赖 Receipt、版本和对应恢复规则。

### Budget 和取消为什么也是控制事实

模型、检索和 Tool 重试都会消耗时间与资源。Budget 让 Controller 能决定继续、降级、Replan 或 abstain，而不是让每个 Provider 自己无限 fallback。

取消同样只停止未来还能安全停止的工作。已经提交的 Domain、已确认的 Effect 和已发生的模型 Usage 仍然是真实历史，Controller 不能通过把 Run 标成 CANCELLED 来改写它们。

### 为什么 Runtime 应优先复用框架而不是自研宿主能力

LangGraph 等框架已经提供图执行、checkpoint、interrupt 等通用原语，Zuno 应优先复用。自定义层只应该承担通用框架不会替法律项目拥有的 PlanVersion、formal admission acceptance、Effect reconciliation 和安全新鲜度等专业语义。

如果 Generic Host + Zuno Legal Backend 已经能满足长期状态和恢复要求，Native Runtime 应缩小甚至退出主路径。自研 Runtime 的价值必须由复杂任务恢复、可控性或成本收益证明。

### Controller 为什么要把“决定”和“执行”分离

如果 Planner 一生成下一步就直接执行，模型决策和现实动作之间没有稳定验收点。Zuno 更倾向于让 Controller 先形成计划/Step 意图，再由执行层调用 Capability、Model 或 Tool，结果回到 Controller 验收。

这种分离允许在派发前检查 Budget、Security、Capability eligibility 和输入 freshness，也允许执行并行而控制单写。模型可以提出更聪明的计划，但不能跳过确定性的安全与业务门。

它还使记录更清楚：计划说明当时为什么要做，Attempt 说明实际做了什么，Acceptance 说明结果为什么被当前计划接纳。三者混在一个 message stream 中时，很难在故障后重建因果。

### Dynamic Plan 为什么不等于“每一步都让 LLM 重规划”

动态意味着计划在证据变化或失败时可以形成新版本，并不意味着每执行一个 Step 都必须调用 Planner。稳定任务完全可以一次生成 DAG 后按确定性调度；只有已知假设失效时才值得 Replan。

过度规划会增加 token、延迟和行为漂移，也会让简单失败被模型放大成新路线。Controller 应尽量用确定性规则处理 ready queue、join、retry budget 和明显错误，把 LLM Planner 留给真正需要语义重构的情况。

这让 Agentic 不等于不可预测：动态性集中在少数明确决策点，其余控制语义保持可测试。

### 并行度为什么受正确性和资源双重约束

DAG 中多个 Step ready 并不表示应该无限同时执行。模型配额、数据库连接、外部 Tool 限流和同一事项的并发业务约束都可能限制实际 dispatch。

Controller 可以按 task priority、budget 和 provider capacity 做调度，但不得为了吞吐改变依赖语义。需要相同 Domain snapshot 的多个分支在提交前仍要接受版本冲突检查；会产生同一现实 Effect 的分支更不能只靠队列并发限制保证幂等。

因此 scheduler 优化的是“何时执行已经合法的工作”，不负责重新定义“哪些工作彼此可以并发”。

### 恢复为什么不能简单重放全部 Node

通用 workflow replay 常假设节点是纯函数或安全幂等。Zuno 的 Step 可能已经提交 Domain 或越过外部 send boundary，盲 replay 会重复业务事实或副作用。

恢复时先按 Step 类型确认外部 durable owner fact：纯计算可以依 checkpoint / input 重算；正式提交先查 AdmissionReceipt；现实动作先查 Effect / Reconciliation；等待人工则重新检查 Approval 和 Security freshness。然后 Controller 才决定 projection 修复或继续运行。

这使 Checkpointer 从“唯一恢复真相”回到合适位置：它保存控制状态，但更强的业务事实优先。

### Runtime 的复杂度什么时候应该退回普通 Workflow

如果任务没有动态依赖、长时间等待、正式 Domain commit 或现实副作用，一个普通同步 service / DAG engine 就可能足够。Native Runtime 不应因为已经存在就接管所有请求。

只有当 Replan、late result、multi-owner recovery、长任务 take-over 等机制在真实 task class 上频繁出现，并且通用 Host 很难以薄适配层满足时，Native Runtime 才值得保留完整复杂度。

这也是 04 最重要的删除条件：如果 B 方案——Generic Host + Zuno Legal Backend——已经提供同等正确性和更低维护成本，就应缩小 C 方案，而不是把“自研运行时”当项目身份的一部分。

### 当前、目标与缺口

Current 是否已有完整 PlanVersion、parallel join、Replan Barrier、interrupt freshness、lease/fencing 和 crash recovery，需要回到代码与测试证据判断；文档中的 Target 不能当成实现清单。

Target 已明确 Single Controller、三层 Graph、不可变计划版本、Retry/Replan/Reconcile 分离和 Owner-fact-first recovery。Gap 仍包括字段级冻结、并行/晚到 fault injection、真实 Checkpointer 语义、Budget / takeover 测试，以及 Native Runtime 相对更简单 Host 方案是否有稳定收益。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. Native Runtime entrant always has a Plan：simple = deterministic single-step；complex = dynamic DAG。
2. 不允许 `direct_answer` 绕过 Plan / Trace / Budget / AnswerPolicy / RunOutcome。
3. Fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph。
4. Single Controller 是默认控制权模型。
5. PlanVersion immutable after activation；Replan 创建新版本。
6. Ready Step 通过 dependency / input / resource / effect / budget / quota / security 全部门禁后才可并行。
7. Action always evaluated；Step always accepted；Reflection triggered, not universal。
8. Retry != Replan != Reconcile。
9. Formal Admission-required Step 没有 matching AdmissionReceipt 不得完成。
10. Runtime Checkpoint != Domain Commit != Tool Effect != Publication truth。
11. Resume / Retry / Replan 的新受保护访问重新授权。
12. Specialist / Subgraph 不获得更高权限。
13. Native Runtime remains measurement-gated。

### B2 Responsibility / Ownership

**Owns**：AgentRun、Plan / PlanVersion、StepDefinition / StepRun、dependency / Ready relation、DispatchGroup / DispatchItem、Branch / Join control、BudgetState、Action Evaluation、Step Acceptance、Reflection trigger、Retry / Replan / Reconcile control、Interrupt / Resume、Checkpoint recovery、RunOutcome。

**Does not own**：Domain / AdmissionReceipt；Knowledge Readiness / EvidenceCandidate；Capability semantics；Tool Effect；Model provider / usage；Authorization / Approval；Publication；long-term Memory truth。

### B3 Upstream / Downstream

上游接收 01 Task / Scope / AgentVersion，03 Readiness / Evidence refs，05 Capability metadata / output，07 Model result / usage，08 Authorization / SecurityEpoch，06 Effect / Reconciliation receipts，02 Domain / AdmissionReceipt。

下游调度 03 / 05 / 07 / 06；必要时请求 02 Formal Admission；向 01 返回 RunOutcome；向 09 输出 runtime telemetry refs。

### B4 Authoritative Facts / Core Objects

AgentRun、PlanVersion、StepDefinition、StepRun、DependencyEdge、DispatchGroup、DispatchItem、BranchResultRef、JoinPolicy、BudgetState、InterruptRecord、ControlDecision、RetryAttempt、ReplanRequest、ReplanBarrier、CheckpointRef、RunOutcome、Specialist / SubgraphExecutionRef。

### B5 Cross-boundary Contracts

Runtime 只消费 / 产生稳定 refs：Task / AgentVersion from 01；Readiness / Evidence from 03；CapabilityVersion / output from 05；Model attempt / usage from 07；Authorization / Approval from 08；PreparedAction / Effect from 06；AdmissionReceipt / DomainVersion from 02；RunOutcome to 01。

### B6 Normal Flow

```text
Task Analyze
→ deterministic single-step or Dynamic DAG
→ DRAFT PlanVersion
→ PLAN_REPAIR if needed
→ activate immutable PlanVersion
→ calculate Ready Steps
→ dependency/input/resource/effect/budget/quota/security gates
→ DispatchGroup / LangGraph Send
→ fixed StepExecutionGraph
→ ReAct Action / Observation
→ Action Evaluation
→ Step Acceptance
→ conditional Step Reflection
→ Join Evaluation / Join Reflection
→ Retry / Replan Barrier / wait Reconcile as required
→ Final Synthesis
→ Final Gate / optional Final Reflection
→ Formal Admission when required
→ verify matching AdmissionReceipt
→ RunOutcome
```

### B7 State / Lifecycle

```text
AgentRun: CREATED → PLANNING → RUNNING → WAITING_INPUT / WAITING_APPROVAL / WAITING_RECONCILIATION → COMPLETED / FAILED / CANCELLED / ABSTAINED
PlanVersion: DRAFT → ACTIVATED → SUPERSEDED; ACTIVATED immutable
StepRun: PENDING → READY → DISPATCHED → RUNNING → ACCEPTED / RETRYABLE_FAILURE / REPLAN_REQUIRED / WAITING / TERMINAL_FAILURE
Replan: TRIGGERED → BARRIER → NEW_PLAN_CREATED → ACTIVATED
Branch: IN_FLIGHT → ARRIVED → ACCEPTED / REJECTED_STALE / REEVALUATION_REQUIRED
```

最终 enum 名称可调整，但语义和 Guard 不得压缩丢失。

### B8 Failure Taxonomy

| 失败 | Detection | Runtime control | Recovery anchor |
| --- | --- | --- | --- |
| model 503 / rate limit | 07 | bounded Retry | ModelAttempt / Budget |
| Step schema / acceptance fail | 04 / 05 | repair / Retry / Reflection | Step input/output |
| evidence conflict | 03/05/04 | more retrieval / Join Reflection / Replan | evidence refs |
| Capability semantic drift | 05 | Replan | CapabilityVersion |
| Tool semantic drift | 06 | Replan | ToolVersion |
| budget / quota exhausted | 04/07 | cheaper plan / abstain | Budget / Usage |
| Security revoked | 08 | pause / stop / permitted Replan | SecurityEpoch |
| parallel partial failure | 04 | selective Retry / Join policy | Branch / StepRun |
| late old-plan branch | 04 | reject / reevaluate | PlanVersion / input refs |
| checkpoint write failure | 04/Platform | resume prior durable point + owner facts | checkpoint + receipts |
| Domain committed / checkpoint failed | 02+04 | repair from AdmissionReceipt | matching Receipt |
| checkpoint complete / Receipt absent | 04+02 | formal completion denied | causation query |
| external Effect unknown | 06 | WAITING_RECONCILIATION | Effect/Reconcile refs |
| controller takeover ambiguity | 04/Platform | fencing / lease protocol | checkpoint + lease + receipts |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Retry 只在 Plan、依赖、输入、Capability / Tool semantics、安全和预算假设仍成立时。每次执行 Attempt 有稳定 identity，Usage 不重置。

Replan 创建新 immutable PlanVersion，并通过 Replan Barrier。Reconcile 由 06 解决现实 Effect；04 只进入等待控制状态。

Recovery = load Checkpoint / pending writes → query matching external Owner facts → refresh current security / eligibility before new dispatch → repair Runtime state。Runtime identity 与 Domain / Tool / Model / Delivery 幂等 namespace 分离。

### B10 Security / Approval / Audit

受保护读取、模型外发、Secret、Tool Effect、Formal Admission 前消费当前 08 决定。Resume / Retry / Replan 不继承过期授权。Budget / Security / Approval / AnswerPolicy 不允许模型绕过。

Specialist / Subgraph 继承父任务的 scope、budget、security constraints；不能独立提升权限。

### B11 Persistence / Transaction Boundaries

LangGraph Checkpointer 保存 Runtime Control State；02 PostgreSQL 保存 Canonical Domain + AdmissionReceipt；06 保存 Effect；08 / audit boundary 保存安全事实。默认不做跨 Store 2PC。

官方 LangGraph persistence 文档说明 Checkpointer 以 thread/checkpoint 保存 graph state，并在 super-step 内支持 pending writes；interrupt 文档说明恢复会重跑触发 interrupt 的 node；subgraph 文档区分 inherited / per-thread / stateless persistence。Zuno 将这些作为 Runtime primitive，而不是业务 truth。

参考官方文档：<https://docs.langchain.com/oss/python/langgraph/persistence>、<https://docs.langchain.com/oss/python/langgraph/interrupts>、<https://docs.langchain.com/oss/python/langgraph/use-graph-api>、<https://docs.langchain.com/oss/python/langgraph/use-subgraphs>。

### B12 Observability / Evaluation

Trace 至少关联 run、plan、step、branch/join、action、CapabilityVersion、ModelAttempt、KnowledgeGeneration、ToolAttempt、SecurityEpoch、AdmissionReceipt、Budget/Usage、RunOutcome。Telemetry 不拥有这些 facts。

关键 Eval：completion、Step acceptance、Retry amplification、Replan rate、parallel efficiency、late-branch rejection、interrupt duration、recovery correctness、cost / latency、A/B/C Runtime necessity。

### B13 Current / Target / Gap / Evidence

**Current**：[`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md) 证明主运行链、checkpoint、interrupt、cancel/restart、duplicate claim、unknown Effect reconcile 等有限行为；[`current-test-baseline.md`](../evidence/current-test-baseline.md) 有 selected canonical tests，但 Full CI / benchmark 未运行。

**Target**：Single Controller + fixed graph shells + dynamic Plan DAG + safe parallelism + triggered reflection + immutable PlanVersion + cross-owner recovery。

**Gap**：复杂 DAG fault injection、Replan Barrier、late branch、HA/fencing/takeover、AdmissionReceipt recovery E2E、SecurityEpoch drift、checkpoint schema upgrade、四 Profile runtime、Specialist benefit 与 A/B/C benchmark。

**状态**：detail design candidate available；runtime necessity / production readiness not established。

### B14 Code / Database / Migration Constraints

- 优先 LangGraph 原生 Send、Reducer、Subgraph、Checkpointer、interrupt / Command resume。
- 不默认引入 Kafka、Kubernetes、自定义分布式调度器、产品级 Multi-Agent Runtime、全局分布式锁或 checkpoint 2PC。
- Runtime state 不成为第二套 Domain database。
- Native Runtime 物理拆分继续受 ADR-0012 和 A/B/C measurement 门控。

#### B14.1 Detail Freeze Candidate：AgentRun / PlanVersion 字段组

`AgentRun` 至少包含 `run_id`、`tenant_id / matter_ref`、`task_ref / invocation_ref`、`agent_definition_version_ref`、`run_state`、`active_plan_version`、`budget_state_ref`、`answer_policy_ref`、`security_context_ref`、`checkpoint_thread_ref`、`created_at / updated_at / terminal_at`、`run_outcome_ref?`。

`PlanVersion` 至少包含 `plan_id / plan_version`、`run_id`、`status`、`planner_role / planner_attempt_ref`、`plan_hash`、`created_from_plan_version?`、`replan_reason?`、`activated_at`、`superseded_at?`。ACTIVATED 后 Step / edge / requirement 集合不可修改。

#### B14.2 Detail Freeze Candidate：Step / Dependency / Dispatch 字段组

`StepDefinition` 至少绑定 `step_id`、PlanVersion、goal / task class、dependency ids、input selectors / version requirements、CapabilityRequirement、allowed Tool / side-effect class、quality / acceptance policy、budget allocation、security requirement、join policy ref。

`StepRun` 至少包含 `step_run_id`、step / plan / run refs、attempt_no、state、resolved input-version set、capability / model / tool refs、started/completed time、acceptance result、failure class、retry / replan decision ref。

DispatchGroup / Item 至少绑定 group identity、PlanVersion、ready-snapshot version、resource / conflict keys、branch identity、dispatch time 和 result ref。

#### B14.3 Detail Freeze Candidate：Ready / Parallel / Join Guard

Ready 判定同时检查：依赖 ACCEPTED；输入版本可用；资源 conflict key 不冲突；不可逆 /同资源写不存在并发危险；Budget / Quota 足够；Security decision 新鲜；Capability / Tool eligibility 可用；Replan Barrier 未激活。

Join 接受晚到结果时重新校验 PlanVersion、Step input set、security freshness、Capability / Tool / Knowledge versions。Reducer 必须幂等，以 branch identity 去重；不得用“最后写入 wins”覆盖已接受结果。

#### B14.4 Detail Freeze Candidate：Reflection / Retry / Replan 决策

ActionEvaluation 每次 Action 都产生 deterministic / typed evaluation ref。StepAcceptance 每个 Step 都必须有。Model Reflection 只在 trigger 条件满足时调用：Acceptance fail、证据冲突、关键决策、重复失败、高风险、Join partial/conflict、复杂 Final Gate。

RetryDecision 至少绑定 failure class、remaining budget、same-plan validity、max attempts / backoff、new attempt identity。ReplanRequest 至少绑定 invalidated assumption / dependency、affected remaining steps、barrier reason、source refs。ReconcileRequest 只引用 06 action/effect，不重发 Tool。

#### B14.5 Detail Freeze Candidate：Checkpoint / Interrupt / Resume

`checkpoint_thread_ref` 与 `run_id` 稳定绑定；每个 Resume 请求绑定 current interrupt identity、resume payload schema/version、principal / security context 和 expected runtime state。重复 resume 使用 resume idempotency identity，旧 interrupt 不得被新的用户输入误消费。

由于 `interrupt()` 恢复会从节点起点重执行，interrupt 前的可见副作用必须幂等，或拆到单独 node / 06 Effect boundary。Pending writes 只用于避免成功 sibling 纯 Runtime work 的无谓重算，不能证明 Domain / Effect。

#### B14.6 Detail Freeze Candidate：Crash / Replan / Takeover Matrix

| Window | 恢复动作 | 禁止 |
| --- | --- | --- |
| Step output 完成但 checkpoint 前崩溃 | 查 pending writes / idempotent re-exec | 假设外部 Effect 未发生 |
| Domain commit 后 checkpoint 失败 | matching AdmissionReceipt 修 Runtime | 重复 Admission |
| Effect 已发出后 controller crash | 06 Reconcile | Tool blind Retry |
| interrupt 后旧 Resume 重放 | interrupt/resume identity 拒绝 | 消费到新 interrupt |
| Replan Barrier 后旧 branch 晚到 | revalidate / reject stale | 写新 Plan state |
| SecurityEpoch 在等待期变化 | next protected action reauthorize | 继承 checkpoint allow |
| controller takeover | lease/fencing + checkpoint + owner facts | 两 Controller 同时 dispatch |

#### B14.7 Detail Freeze Candidate：Schema Evolution / Runtime Upgrade

1. Plan / Step schema 新字段采用兼容读取；paused thread 恢复路径必须测试。
2. 不直接重命名 / 删除旧 checkpoint 可能恢复到的 node 而没有 drain / migration / compatibility adapter。
3. State schema 收紧前验证历史 checkpoints；不能用默认值伪造业务 Owner facts。
4. PlanVersion / Step identity 不因代码部署重新编号。
5. Graph topology migration 必须说明 existing thread 的 old graph version 如何继续、drain 或显式 fail / manual recover。
6. Runtime schema migration 不修改 02 / 06 / 08 durable truth。
7. Specialist subgraph persistence mode 必须固定在版本化配置中，不能部署后静默从 per-invocation 改成 per-thread。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

| 场景 | 必须证明 |
| --- | --- |
| deterministic single-step path | 仍有 Plan/Trace/Budget/Outcome |
| parallel one branch fails | successful sibling 不重复产生副作用 |
| resource conflict | unsafe branches 串行 |
| Retryable model failure | same Plan bounded Retry，Budget 累计 |
| Capability / Tool semantic drift | Replan，不 Retry |
| Replan while branches in-flight | Barrier 阻止旧 Plan 新 dispatch |
| late old-plan branch | freshness guard 拒绝/重评 |
| interrupt node resumes | interrupt 前副作用不重复 |
| Domain commit/checkpoint fail | Receipt repair |
| checkpoint complete/Receipt absent | formal completion denied |
| cancel while Effect in-flight | 06 Reconcile |
| SecurityEpoch changes while waiting | Resume 后重新授权 |
| controller takeover stale lease | fencing 阻止双派发 |
| graph/checkpoint schema upgrade | paused thread 有明确兼容结果 |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

04 只能证明运行控制事实。StepRun ACCEPTED、AgentRun COMPLETED、Checkpoint complete 都不能自动证明 Formal Admission、Effect 或 Publication。Admission-required Step 必须引用 matching AdmissionReceipt；side-effect Step 必须引用 06 Effect / Reconciliation fact。

LangGraph pending writes 是运行持久化优化，不升级成业务 proof。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

每个 dispatch / result 沿 `run → PlanVersion → StepRun / Branch → input-version set → Knowledge / Capability / Tool / Model refs → SecurityEpoch → output/receipt refs` 可追溯。Runtime identities 与 Domain admission、Tool effect、Model attempt、Delivery idempotency 分离。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

`AgentRun=CANCELLED` 只停止未来可取消工作。既有 Admission / Effect / Usage 继续按各自 Owner 解释；late branch 重新验收。新 Evidence / DomainVersion 使计划假设失效时，旧“成功”结果也可能只能 Replan / Review。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
load checkpoint / pending writes
→ validate active PlanVersion / controller lease/fencing
→ query 02 AdmissionReceipt when required
→ query 06 Effect / Reconciliation when required
→ refresh 08 Authorization before new protected action
→ revalidate 03 / 05 / 07 versions and eligibility
→ repair Runtime Control State
→ 09 telemetry
```

至少覆盖 interrupt re-execution、parallel pending writes、cancel-in-flight、Domain/checkpoint mismatch、Replan late branch、SecurityEpoch drift、Capability/Tool drift、takeover/fencing 和 subgraph persistence mode。