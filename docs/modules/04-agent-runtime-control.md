# 04 Agent Runtime & Control（智能体运行与控制）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块解决的不是“怎么让模型多调用几次”

简单法律问答并不需要复杂 Runtime。用户问合同第 8 条写了什么，03 能确认材料就绪并检索到稳定来源，07 受控生成，01 就可以返回。只有任务需要多步骤依赖、并行分支、人工暂停、外部效果、恢复或重规划时，自有 Runtime 才有价值。

04 真正解决的是：**当任务需要持续执行，而且事实、能力、权限和外部世界会在执行期间变化时，系统怎样知道下一步该做什么、哪些结果仍有效、失败后怎样继续而不重复做错事。**

### 为什么所有 Native Runtime 任务都必须有 Plan

统一 Runtime 的危险捷径是给简单任务保留 `direct_answer`，复杂任务才进入 Plan。这样最简单的路径反而绕过 Trace、Budget、AnswerPolicy 和 RunOutcome，长期会形成两套语义。

因此只要进入 Native Runtime，就必须有 Plan：简单任务是 Deterministic Single-Step Plan（确定性单步计划），复杂任务是 Dynamic DAG Plan（动态有向无环图计划）。这让每个运行都拥有统一的 causation、预算、状态、恢复和结果资格。

### 为什么使用 Single Controller，而不是默认自治 Multi-Agent

Zuno 产品可以有多个专业 Agent，但单次任务的控制权默认只有一个 Single Controller。它负责 PlanVersion、Ready Step、并行、Join、Retry / Replan / Reconcile、Budget 和 RunOutcome。

Specialist Agent / Subgraph 可以作为某个 Step 的执行实现，返回 Proposal / Observation / BranchResult，却不能自己激活 PlanVersion、提交 Domain、批准权限、绕过预算或决定最终发布。这样既能复用多 Agent 专业分工，又不建设一套产品级自治 Multi-Agent Runtime。

### 三层结构为什么比“一个大图”更容易控制

目标结构是：

```text
Fixed AgentRunGraph
+ dynamic Plan DAG
+ fixed StepExecutionGraph
```

AgentRunGraph 管理运行生命周期、计划、重规划、最终综合和终止；Plan DAG 表达这次任务具体有哪些 Step 与依赖；StepExecutionGraph 固定单个 Step 如何执行 ReAct、工具 / 模型 / Capability 调用、Action Evaluation、Step Acceptance 和必要 Reflection。

这样任务结构可以动态变化，但安全、评测和恢复机制不会因为 Planner 每次生成不同图代码而漂移。

### Planner 为什么不能生成执行器做不到的巨大 Step

Planner 必须知道 05 Capability 的 task class、输入规模、Evidence requirement、成本和 side-effect 边界。否则“分析全部材料并给最终结论”虽然语义上像一步，工程上却无法局部验收、并行、重试或定位失败。

一个 Step 的边界应该满足：输入明确、依赖明确、执行器有能力完成、结果能够验收、失败能够分类。Planner 负责结构，Capability / Model 负责在这个结构内执行。

### Ready Step 为什么不能只看 DAG 依赖

依赖都完成，并不意味着 Step 可以立刻并行。它还要检查输入版本、资源冲突、同一现实资源写入、副作用、Budget、Provider quota、Security Gate 和排他资源。

所以 Zuno 的原则是“最大化安全并行”，不是“最大化并发数”。读取不同材料、互不写共享资源的纯分析可以并行；写同一资源、不可逆 Effect、Replan、Final Synthesis 默认串行。

### Send / Reducer 为什么适合并行，但不是业务正确性证明

LangGraph 的 `Send` 适合动态 fan-out / map-reduce，Reducer 适合把并行结果合并进共享状态；Checkpointer 还能保存 super-step 与 pending writes。Zuno 优先复用这些原语，而不是先自建分布式调度器。

但框架能并行并不意味着业务上可以并行。04 在创建 DispatchGroup / DispatchItem 之前仍要做资源、副作用、预算和安全门禁；Reducer 也必须幂等，不能让晚到旧分支覆盖新 Plan。

### ReAct 为什么只属于一个 Step 内部

Plan-and-Execute 管理任务级目标、依赖和并行；ReAct 负责单个 Step 内“Action → Observation → 下一 Action”。如果 ReAct 可以任意新增全局任务、修改其他 Step 依赖或直接发布最终答案，它就会成为第二个 Planner。

因此 StepExecutionGraph 的 ReAct 只在当前 Step Contract、预算和允许的 Capability / Tool 范围内循环。发现任务结构假设失效时，返回 `REPLAN_REQUIRED` 给 Controller。

### Action Evaluation 和 Step Acceptance 为什么都需要

Tool / Model 一次返回合法结果，只证明 Action 有输出；一个 Step 是否完成还要判断整体目标、证据充分性、schema、冲突和安全条件。

每个 Action 都 Evaluation，每个 Step 都 Acceptance。模型级 Reflection 不需要每步都调用，而在 Acceptance 失败、证据冲突、关键决策、重复失败、高风险或 Join 部分失败时触发。

### Retry、Replan、Reconcile 为什么必须分开

Retry 表示计划仍正确，只是一次执行暂时失败；Replan 表示原计划结构、依赖、材料、能力或安全可行性假设已经失效；Reconcile 表示现实副作用可能已经发生，但结果未知。

```text
Retry != Replan != Reconcile
```

把三者混成“失败后再试”，会让模型 503 和新证据到来走同一条路，也会让外部 POST timeout 被盲重试。

### PlanVersion 为什么激活后不可修改

如果运行中直接修改当前 Plan 的 Step / 依赖，已经派发的分支就不知道自己属于哪个结构，Checkpoint 也很难解释。目标规则是 **PlanVersion immutable after activation**。

Planner / PLAN_REPAIR 可以修改尚未激活的 DRAFT；一旦激活，任何结构性变化都创建新 PlanVersion。旧版本继续保留用于 causation 和晚到结果判断。

### PLAN_REPAIR 和 Replan 为什么不是一回事

PLAN_REPAIR 发生在计划草案激活前，用来修复环、缺少依赖、Step 过大、引用不存在 Capability 等结构问题。此时旧计划还没有成为执行事实。

Replan 发生在 ACTIVE Plan 执行后，因为新 Evidence、Capability drift、Tool schema、预算或安全变化使剩余计划不再正确。Replan 必须创建新 PlanVersion，并处理旧分支和旧结果。

### Replan Barrier 为什么是并行任务的关键

多个分支并行时，如果一个分支发现新事实需要 Replan，而其他分支仍继续派发，很容易出现新旧计划交叉执行。Replan Barrier 的作用是停止旧 Plan 的新 dispatch，等待 / 标记正在运行分支，再创建并激活新 PlanVersion。

**Replan Barrier** 不要求粗暴等待所有远端 Effect；已经发出的 Effect 由 06 继续 Reconcile。Barrier 管的是控制权，不否认现实世界已经发生的事。

### 晚到分支为什么不能一律丢弃

纯计算分支晚到后，如果 PlanVersion 或输入已经失效，可以拒绝当前使用；但它可能仍是有价值的观察，需要重新验收。现实 Effect 分支更不能因“旧计划”就被丢弃，EffectReceipt 仍是真实事实。

所以 late result 规则是重新检查 causation、PlanVersion、input version、Knowledge / Capability / Tool / Model refs、SecurityEpoch 和目标模块资格，再决定 accept / reject-stale / reevaluate / Replan。

### Interrupt / Resume 为什么会让节点幂等变得重要

LangGraph 官方文档说明，`interrupt()` 暂停后恢复时会从触发 interrupt 的节点开头重新执行，而不是从代码行继续。因此 interrupt 前执行的代码可能再次运行。

所以副作用不能随便放在 interrupt 前；纯数据库 upsert 要幂等，高风险现实 Effect 应拆到 06 的可恢复动作边界。Checkpointer 能保存控制状态，但不会替我们自动获得外部 exactly-once。

### Checkpoint 为什么不是业务事实

LangGraph persistence 能保存 thread / checkpoint / pending writes，并帮助故障恢复。它非常适合 Runtime Control State，却不能证明 Domain 已正式提交、Tool Effect 已发生、安全审批已成立或结果已发布。

04 恢复时先加载 Checkpoint，再查询 02 AdmissionReceipt、06 Effect / Reconciliation、08 当前 Authorization 等 Owner facts，修复自己的 Control State，而不是用 Checkpoint 覆盖它们。

### Cancel 为什么不是全局回滚

Cancel 的最小语义是停止未来还能停止的派发和计算。已经提交的 Domain transaction 不消失；已经确认的 Effect 不撤销；in-flight Effect 结果未知时继续 Reconcile；已产生的 Model Usage 由 07 结算。

如果业务真的需要撤销现实动作，要创建新的补偿动作，并重新经过安全和 Effect Control，而不是修改旧 Receipt。

### Budget 为什么是 Runtime 控制状态，而不只是模型网关的一张账单

07 可以准确记录一次模型调用用了多少 Token、多少钱，也可以做 Provider quota reservation，但“这次任务还剩多少执行空间、下一条 Ready Step 还能不能派发、失败以后应该继续重试还是缩小计划”属于 04 的控制问题。BudgetState 因此必须聚合已经发生的 Model Usage、Tool / Capability 成本、剩余 Step 的估算，以及当前任务自己的预算和 deadline，而不是每次调用前只问模型网关“余额够不够”。

这也意味着 Retry、fallback 和 Reflection 都不能获得一份新的隐藏预算。第一次快速模型失败、第二次推理模型成功，两次真实 Usage 都计入同一 Run；并行分支同时消耗预算时，Controller 要在派发前做 reservation 或等价控制，防止每个分支都看到“余额还够”而合计超支。预算不足时可以选择更便宜的已合格路径、缩小尚未承诺的计划、请求人工确认或 Abstain，但不能把已经发生的成本重置，也不能为了“跑完 Plan”绕过安全或质量门禁。

### Controller Takeover 为什么需要 Lease / Fencing，却不意味着先建设分布式锁平台

单 Controller 是逻辑不变量，但生产环境中的进程仍可能崩溃。如果未来需要另一个 Worker 接管同一个 AgentRun，仅靠“看到旧 Controller 心跳没了”并不足够：旧进程可能只是网络分区，恢复后继续 dispatch，于是两个 Controller 同时派发同一个 Step。Target 因此保留 Lease / Fencing（租约 / 栅栏）候选，让每次新的控制权都拥有单调可验证的 takeover identity，旧持有者即使恢复也不能继续产生新的有效 dispatch。

这里要避免把“需要防双派发”扩张成全系统分布式锁。Lease / Fencing 是 Platform 提供给 04 的局部物理原语，只保护真正需要单写者语义的 Run / Dispatch；Domain 并发仍由 02 的事务和版本条件处理，Tool Effect 仍由 06 的幂等与 Reconciliation 处理。当前仓库也没有 HA / takeover 的工程证据，因此这仍是 Detail Candidate：必须先通过进程崩溃、租约过期、旧 Controller 复活和网络分区类 Failure Injection，才能把它升级成 Current，更不能仅凭架构描述宣称高可用。

### Final Synthesis 为什么默认串行

并行分支可以分别分析争议点，但 Final Synthesis 要把已经接受的结果组织成一致输出，因此默认串行。它不能为了“答案更完整”重新发明没有 Evidence 的事实。

Final Gate 检查 AnswerPolicy、引用、预算、结果资格和必要安全条件；复杂 / strict-grounded 任务可以触发模型级 Final Reflection，但 Reflection 仍然只产生质量判断，不能替代 02 Admission、08 Authorization 或 01 Publication。

### 为什么 Native Runtime 仍然是 Measurement-gated

一套设计完整的 Runtime 也可能不值得长期保留。09 需要比较 Generic Host + Legal Skills、Generic Host + Zuno Legal Backend、Native Runtime + first-class Domain State，在质量、恢复、人工介入、成本、时延和开发复杂度上的差异。

如果通用 Host 已经能满足关键恢复和控制需求，Zuno 应缩小自有 Runtime。架构完整不是保留复杂度的理由。

### 当前、目标与缺口

Current Runtime Baseline 证明 `AgentRunApplicationService → AgentRuntimeService → AgentRunStore / checkpoint → Agent Core graph` 主路径，以及 persistence failure、approval interrupt、duplicate claim、cancel、restart、unknown Effect Reconcile 等有限行为。

Target 是 Single Controller + Fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph + safe parallelism + triggered reflection + immutable PlanVersion + durable cross-owner recovery。Gap 包括复杂 DAG fault injection、Replan Barrier、late branch、HA/fencing/takeover、AdmissionReceipt recovery E2E、SecurityEpoch drift、checkpoint schema upgrade、四 Profile runtime、Specialist A/B 和 Native Runtime necessity benchmark。

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