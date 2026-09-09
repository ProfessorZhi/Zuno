# 04 Agent Runtime & Control（智能体运行与控制） — Engineering Reference

human_source: README.md
overall_architecture: ../../architecture/reference.md
current_evidence: ../../evidence/

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

**Current**：[`current-runtime-baseline.md`](../../evidence/current-runtime-baseline.md) 证明主运行链、checkpoint、interrupt、cancel/restart、duplicate claim、unknown Effect reconcile 等有限行为；[`current-test-baseline.md`](../../evidence/current-test-baseline.md) 有 selected canonical tests，但 Full CI / benchmark 未运行。

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