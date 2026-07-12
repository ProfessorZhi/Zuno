# 06 Agent Core / Planning & Control

updated: 2026-07-12  
status: normative-target-module-design  
module_number: 06  
formal_path: `docs/modules/06-agent-core-planning-control.md`  
agent_mirror: `.agent/modules/06-agent-core-planning-control.md`

> 本文是 Zuno 第 06 个逻辑模块——Agent Core / Planning & Control——的正式 Target 架构主设计。
>
> 本文只描述理想目标架构，不包含当前实现事实或具体迁移计划。Current 与 Gap 由 `docs/status/production-readiness.md` 维护；未来 Program 必须以本文及配套规范为目标约束。

## 0. 文档集与规范优先级

Agent Core Target 由三份正式文档共同构成：

```text
docs/modules/06-agent-core-planning-control.md
    主设计：问题、概念架构、完整运行流程、模块边界、目标代码和持久化规格。

docs/modules/06-agent-core-control-protocols.md
    控制协议：不变量、状态机、DAG、并发、Interrupt、Signal、副作用、Finalization、Failure 与 Budget。

docs/modules/06-agent-core-consistency-lifecycle-protocols.md
    一致性协议：TaskContract、命令仲裁、Domain/Checkpoint、ResultValidity、Event、Artifact、Reconciler 与时间语义。
```

规范优先级：

```text
全局架构原则
→ Agent Core 规范性协议
→ 本主设计的流程与实施规格
→ 后续 Program 与代码
```

若本文与两份规范性协议冲突，以规范性协议为准，并必须在同一轮文档变更中消除冲突。

---

# Part I：定位与概念架构

# 1. 为什么需要 Agent Core

企业级 Agent 不能只依赖一个模型循环决定下一步。任务涉及多目标、并行、审批、外部副作用、长时间等待和恢复后，单循环会出现：

```text
目标和约束只存在于上下文中
计划结构不稳定，无法可靠并行
模型返回结果，但系统无法证明 Step 合格
失败后无法区分 Retry、Repair、Fallback 与 Replan
并行分支竞争共享状态或提交晚到结果
审批、权限、预算和副作用可能被绕过
重启后无法确认外部操作是否已经发生
最终文本已经发送，但质量门和审计事实尚未提交
```

一句话定义：

> Agent Core 是 Zuno 的 Single Controller Agent Runtime。它使用固定 AgentRunGraph 管理生命周期，以动态 Plan DAG 表达任务结构，并在固定 StepExecutionGraph 内执行受控 ReAct；模型产生 Proposal，Runtime、Policy 和各事实 Owner 决定领域状态与外部执行。

# 2. Zuno 是 Agent，Graph 是控制系统

Zuno 的产品形态是 Agent，因为它围绕目标形成动态闭环：

```text
理解目标
→ 形成计划
→ 选择行动
→ 观察环境
→ 判断质量
→ Retry / Repair / Replan
→ 完成、部分完成、拒绝或主动放弃
```

固定 Graph 不是 Agent 的替代品，而是防止动态智能绕过治理。

```text
固定 AgentRunGraph
    生命周期、状态、预算、安全、恢复、发布与终局。

动态 Plan DAG
    Objective、Step、依赖、条件、并行、Join 和完成标准。

固定 StepExecutionGraph
    Action Proposal、Validation、Execution、Observation、Evaluation、Acceptance 与 Reflection。
```

# 3. 模块职责

Agent Core 负责：

```text
Runtime Request 与 TaskContract 校验
GoalVersion、Objective 和输出要求管理
ExecutionContextSnapshot
Task Analysis 与 Complexity Classification
RuntimePolicy / AnswerPolicy 解析
Plan 创建、验证、激活和版本化
ReadySet、Admission、Budget、资源冲突和安全并行调度
Step 内 ReAct
Action Proposal 校验和跨模块调度
Observation 归一化
Action Evaluation 与 Step Acceptance
Step / Join / Final Reflection 与 Decision Guard
Retry、Repair、Fallback、Replan 与 Replan Barrier
多 Interrupt、Signal、Resume 与外部等待
Cancellation、Deadline 与控制命令仲裁
FinalCandidate、Final Gate、Publication 与 RunOutcome
Reflexion Candidate Bridge
Domain Event、Runtime Progress、Trace 与审计关联
崩溃恢复、Orphan Reconciliation 和幂等控制
```

Agent Core 不负责：

```text
文档解析或 OCR
直接访问 Milvus、Neo4j 或 BM25 内部实现
直接调用模型厂商 SDK
直接执行 Shell、浏览器、邮件或第三方 API
直接批准权限或副作用
直接写长期 Memory
直接修改 Knowledge、Security、Tool、Model 或 Eval 的领域事实
保存大型 Payload、完整凭证或隐藏思维链
```

# 4. Cross-module Ownership

```text
Product Surface        RuntimeRequest、用户交互与展示渠道
Input / Ingestion      文档处理任务与摄取状态
Knowledge              RetrievalRound、Evidence、CitationLineage
Model Gateway          ModelInvocation、Usage、Provider Failure
Memory & Context       ContextPack、MemoryCandidate、Memory Commit
Capability / Skill     CapabilityDefinition、SkillDefinition
Tool Runtime           ToolExecution、External Effect、Reconcile
Security               Authorization、Approval Policy、Revocation
Observability & Eval   Trace、Metric、Eval Result
Infrastructure         Checkpoint、Lease、Transaction、Object Store
Agent Core             Run、Goal、Plan、Step、Dispatch、Decision、Outcome
```

Agent Core 是编排者，不冒充其他模块的事实 Owner。

---

# Part II：智能机制与运行流程

# 5. 五种机制

```text
Plan-and-Execute
    管理整个任务的目标、依赖、并行和完成条件。

ReAct
    管理单个 Step 内 Action 与 Observation 的动态循环。

Reflection
    判断 Action、Step、Join 或最终结果是否合格。

Replan
    目标、假设、依赖或能力边界实质变化时创建新 PlanVersion。

Reflexion
    Run 结束后生成可治理经验候选，不直接写长期 Memory。
```

# 6. 所有任务都必须有 Plan

简单任务使用 Deterministic Single-Step Plan，复杂任务使用动态 DAG Plan。不存在绕过以下治理的正式回答路径：

```text
Plan
Trace
Budget
AnswerPolicy
Final Gate
Publication
RunOutcome
```

# 7. TaskContract 与 GoalVersion

```text
TaskContract
├── GoalVersion
│   ├── ObjectiveDefinition[]
│   ├── UserConstraint[]
│   ├── OutputRequirement[]
│   └── CompletionPolicy
└── Conversation / Workspace / Security Context Refs
```

用户追加信息必须分类为：

```text
SUPPLEMENTAL_INPUT
CLARIFICATION_RESPONSE
CONSTRAINT_CHANGE
OUTPUT_CONTRACT_CHANGE
OBJECTIVE_CHANGE
CANCELLATION_REQUEST
NEW_TASK
```

实质目标、约束或输出 Contract 变化创建新 GoalVersion 并触发 Replan；普通补充输入只解决 Interrupt。

# 8. Planner Pipeline

```text
TaskAnalyzer
→ ComplexityClassifier
→ RuntimePolicyResolver
→ PlannerRouter
→ DeterministicPlanner / SkillPlanner / ModelPlanner
→ PlanNormalizer
→ PlanValidator
→ PlanRepair
→ PlanVersion Activation
```

PlanValidator 至少检查：

```text
Schema
Goal Coverage 与 Objective Traceability
Step ID 唯一
DAG 无环与可达性
DependencyRule 与 ActivationCondition
输入输出兼容
Capability 可满足
Security 可执行
Budget 可分配
并行资源冲突
JoinPolicy 完整
Acceptance 可测试
Terminal Deliverable 存在
```

模型 Planner、Repair 和 Critic 只产生 Proposal。

# 9. Plan DAG

每个 StepDefinition 必须包含：

```text
Objective
Input / Output Contract
DependencyRule
ActivationCondition
AcceptancePolicy
Required Evidence
Allowed Capability / Tool / Model Role
Retry / Repair / Fallback Policy
Reflection Policy
Budget / Deadline
Resource Claims
Side-effect Class
Join Relationship
```

依赖类型：

```text
ALL_SUCCESS
ALL_TERMINAL
ANY_SUCCESS
OPTIONAL_INPUT
QUORUM
```

Disposition：

```text
EXECUTE
REUSE_COMPLETED
SKIP_CONDITION_FALSE
SKIP_OPTIONAL
BLOCKED_DEPENDENCY
BLOCKED_SECURITY
BLOCKED_BUDGET
OBSOLETE_BY_REPLAN
CANCELLED_BY_RUN
```

JoinPolicy：

```text
ALL_REQUIRED
BEST_EFFORT
QUORUM
FIRST_VALID
ANY_SUCCESS
CUSTOM_DETERMINISTIC
```

# 10. AgentRunGraph

```text
START
→ initialize_run
→ validate_runtime_request
→ create_or_resolve_task_contract
→ resolve_authorization
→ create_execution_context_snapshot
→ check_input_readiness
→ build_context
→ analyze_task
→ resolve_runtime_and_answer_policy
→ create_plan_proposal
→ normalize_and_validate_plan
→ activate_plan_version
→ controller_loop
```

Controller Loop：

```text
arbitrate_control_commands
→ reconcile_domain_and_checkpoint_generation
→ reconcile_expired_or_orphaned_facts
→ calculate_ready_set
→ evaluate_liveness
→ reserve_budget_and_resources
→ commit_dispatch
→ dynamic_send_step_workers
→ collect_branch_results
→ reduce_branch_results
→ evaluate_join
→ continue / wait / retry / replan / finalize
```

Finalization：

```text
final_synthesis
→ create_final_candidate
→ extract_claims
→ bind_claims_evidence_and_citations
→ final_gate
→ maybe_final_reflection
→ prepare_artifact_versions
→ prepare_publication
→ publish
→ confirm_delivery
→ commit_run_outcome
→ build_reflexion_candidate
→ END
```

一个 Run 可以同时存在多个 Pending Interrupt：

```text
USER_INPUT
APPROVAL
EXTERNAL_JOB
INGESTION_COMPLETION
SECURITY_REVIEW
MANUAL_RECONCILIATION
RESOURCE_AVAILABLE
```

# 11. StepExecutionGraph

```text
START
→ load_step_definition
→ verify_plan_and_execution_epoch
→ resolve_step_inputs
→ acquire_resource_claims
→ confirm_budget_reservation
→ preflight_security_gate
→ decide_action_proposal
→ validate_action
→ prepare_side_effect_if_needed
→ await_approval_if_needed
→ claim_idempotency
→ execute_action
→ normalize_observation
→ persist_action_observation_and_usage
→ evaluate_action
→ evaluate_acceptance
→ maybe_step_reflection
→ decide_step_progress
```

Step Progress：

```text
CONTINUE_REACT
RETRY_ACTION
REPAIR_PARAMETERS
FALLBACK_CAPABILITY
ESCALATE_MODEL
COMPLETE
RETRY_STEP
REQUEST_REPLAN
WAIT_SIGNAL
BLOCK
ABSTAIN
FAIL
```

外部副作用统一遵循：

```text
Proposal
→ Prepare
→ Validate
→ Authorize
→ Approve
→ Claim
→ Execute
→ Observe
→ Reconcile
→ Commit Outcome
```

# 12. 并行与 Dispatch

Scheduler 依次检查：

```text
Active PlanVersion
Dependency 与 Condition
输入可用性
Security
Capability
资源冲突
副作用串行要求
Budget Reservation
Provider Quota
Workspace Fair Share
Deadline 和 Critical Path
Execution Claim
Dispatch Commit
```

Dispatch 必须先持久化再 Send：

```text
BEGIN
创建 DispatchGroup
创建 DispatchItem
创建 StepRun
预留 Budget
获取 Resource Claim
记录 DispatchCommittedEvent
COMMIT

COMMIT 后才允许 Send
```

Worker 只返回不可变 BranchResultRef，不直接修改共享 Run 状态。

# 13. Reflection、Retry 与 Replan

```text
Action Evaluation       每个 Action 都执行，确定性优先
Step Acceptance         每个 Step 都执行
Step Reflection         失败、冲突、关键决策或重复失败时触发
Join Evaluation         每个 Join 都执行
Join Reflection         部分失败、冲突或 ReplanRequest 时触发
Final Gate              所有任务必经
Final Reflection        复杂、严格 Grounded 或高风险任务触发
```

```text
Retry                   目标和计划结构不变
Parameter Repair        调整参数、Query 或 Prompt
Executor Escalation     弱模型升级为强模型角色
Capability Fallback     更换能力但保持 Output Contract
Step Repair             改变 Step 内执行方法
Replan                   修改剩余结构并创建新 PlanVersion
```

Replan Barrier：

```text
禁止旧 Plan 新建 Dispatch
CANCEL_SAFE 分支请求取消
DRAIN_REQUIRED 分支允许完成但不保证复用
NON_INTERRUPTIBLE 副作用必须完成并 Reconcile
收集已提交结果
创建并验证新 PlanVersion
原子切换 Active PlanVersion
重新计算 ReadySet
```

# 14. Finalization 与 Publication

```text
FinalCandidate
→ FinalGateResult
→ ArtifactVersion
→ Publication
→ DeliveryReceipt
→ RunOutcome
```

Final Gate 前不得把 Candidate 当作正式答案发布。流式输出分为 Progress Stream、Policy 允许的 Provisional Content 和 Transactional Final Publication。

# 15. Cancellation 与控制命令

所有控制命令进入 per-run 串行仲裁。默认优先级：

```text
Security Revocation
→ Cancellation
→ Deadline / Expiration
→ Unknown Side-effect Reconciliation
→ Approval / Signal
→ Budget
→ Replan
→ Quality Decision
→ Normal Scheduling
```

取消流程：

```text
Run → CANCELLING
停止新 Dispatch
取消 QUEUED / CLAIMED StepRun
请求取消可中断 Action
释放未消费 Budget 和 Lease
等待或 Reconcile 不可中断副作用
提交 CANCELLED 或 PARTIAL Outcome
```

---

# Part III：状态、恢复与一致性

# 16. 核心状态模型

规范性状态以 `06-agent-core-control-protocols.md` 为唯一事实源：

```text
AgentRun
PlanVersion
StepRun
ActionRun
Publication
```

`WAITING_CONDITION` 是非终态；`BLOCKED` 是终态；取消必须经过 `CANCELLING`。

# 17. Graph State

```python
class AgentRunGraphState(TypedDict, total=False):
    schema_version: str
    run_id: str
    thread_id: str
    trace_id: str
    phase: str
    domain_generation: int
    checkpoint_generation: int
    controller_epoch: int
    task_contract_id: str
    active_goal_version_id: str
    execution_snapshot_id: str
    active_plan_version_id: str
    current_dispatch_group_id: str | None
    pending_interrupt_refs: list[str]
    branch_result_refs: list[str]
    latest_control_decision_ref: str | None
    final_candidate_ref: str | None
    publication_ref: str | None
    outcome_ref: str | None
```

```python
class StepGraphState(TypedDict, total=False):
    run_id: str
    step_run_id: str
    step_definition_id: str
    plan_version_id: str
    controller_epoch: int
    execution_epoch: int
    resolved_input_ref: str | None
    latest_action_run_id: str | None
    latest_observation_ref: str | None
    latest_acceptance_ref: str | None
    latest_reflection_ref: str | None
    pending_interrupt_refs: list[str]
    output_ref: str | None
    failure_ref: str | None
```

Graph State 禁止保存完整 Plan、Context、Prompt、Observation Payload、检索结果、Artifact 或隐藏思维链。

# 18. Domain Store 与 Checkpointer

```text
PostgreSQL Domain Store
    可审计领域事实与状态转换。

LangGraph Checkpointer
    Graph Node、Channel、Pending Send、Interrupt Cursor 和 Reducer 控制状态。

Object Store
    大型不可变 Payload、Artifact 和调试包。
```

一致性原则：

```text
Domain Generation 是权威提交序列
Checkpoint 只能引用已提交的 Domain Generation
Domain > Checkpoint 时从领域事实重建控制状态
Checkpoint > Domain 时回退到最后合法 Generation
```

# 19. Result Validity

```text
VALID
STALE
REVOKED
TAINTED
SUPERSEDED
UNKNOWN_VALIDITY
```

污染传播：

```text
Evidence REVOKED
→ Observation TAINTED
→ StepResult TAINTED
→ JoinResult TAINTED
→ FinalCandidate TAINTED
→ Publication 被阻止、撤回或创建更正版本
```

# 20. Event、Outbox 与 Trace

```text
DomainEvent
RuntimeProgressEvent
AuditEvent
IntegrationEvent
PublicationEvent
```

```text
Outbox at-least-once
同一 run_id 内 sequence_no 有序
跨 Run 不保证顺序
消费者按 event_id 幂等
事件带 contract_version 和 payload_schema_hash
敏感字段在 Integration Event 前脱敏
```

# 21. Orphan Recovery

```text
RunOrphanReconciler
DispatchReconciler
StepLeaseReconciler
UnknownActionReconciler
InterruptExpiryReconciler
PublicationReconciler
OutboxReconciler
BudgetReservationReconciler
```

每个 Reconciler 使用 Claim、Fencing 和 Idempotency，并定义人工介入条件。

# 22. 时间语义

```text
持久化时间统一 UTC
Deadline 和 Expiry 使用绝对时间
进程内耗时使用 monotonic clock
Lease 到期以数据库时间为准
用户时区只用于展示
Clock Skew 超阈值时拒绝 Lease-sensitive 操作
等待是否消耗 Wall-clock Budget 由 BudgetPolicy 明确声明
```

---

# Part IV：目标 Contract 与实施规格

# 23. 主要领域对象

```text
TaskContract
GoalVersion
ObjectiveDefinition
ObjectiveOutcome
ExecutionContextSnapshot
AgentRun
Plan
PlanVersion
PlanStepDefinition
DependencyRule
ActivationCondition
StepRun
ActionRun
Observation
AcceptanceResult
ReflectionResult
DispatchGroup
DispatchItem
BranchResultRef
ReductionAttempt
JoinAttempt
PlanPatch
ReplanBarrier
Interrupt
SignalConsumption
PreparedAction
ApprovalDecision
IdempotencyClaim
ResultValidityRecord
FinalCandidate
ArtifactVersion
ArtifactValidation
Publication
DeliveryReceipt
RunOutcome
RuntimeEvent
OutboxEvent
ReconciliationRecord
```

# 24. Typed Ports

```text
ModelGatewayPort
KnowledgeQueryPort
ContextAssemblyPort
CapabilityResolutionPort
IngestionPort
ToolExecutionPort
SecurityDecisionPort
ArtifactPort
PublicationPort
CheckpointPort
ObservationSinkPort
```

Port 不暴露其他模块内部 Repository、数据库 Session 或 Provider SDK。

# 25. 目标代码目录

```text
src/backend/zuno/agent/
├── contracts/{task,policy,planning,execution,interrupt,side_effect,publication,outcome,events}.py
└── runtime/
    ├── domain/{task_contract,run,plan,step,action,dispatch,interrupt,signal,prepared_action,approval,idempotency,result_validity,artifact,publication,failure,outcome}.py
    ├── application/{run,task_contract,planning,scheduling,step_execution,reflection,replan,signal,side_effect,reconciliation,finalization,publication,command_arbitration,recovery,cancellation}_service.py
    ├── graph/run/{state,nodes,routing,builder}.py
    ├── graph/step/{state,nodes,routing,builder}.py
    ├── planning/{analyzer,validator,repair,planners/}
    ├── scheduling/{readiness,liveness,admission,selector,fencing,reduction,join}.py
    ├── execution/{action_decider,action_validator,executor_registry,executors/}
    ├── finalization/{candidate,claims,gate,artifact,publication}.py
    ├── recovery/{generation,reconcilers,replay}.py
    ├── persistence/{repositories,uow,outbox,event_sequence}.py
    └── ports/
```

约束：Domain 不导入 LangGraph；Graph Node 不直接写 SQL；Application 不导入 FastAPI；外部调用不放在数据库事务内；ORM Row 不直接作为 Graph State。

# 26. PostgreSQL 目标表

```text
Task and Run
├── agent_task_contracts
├── agent_goal_versions
├── agent_objectives
├── agent_runs
├── agent_execution_context_snapshots
├── agent_runtime_policy_snapshots
└── agent_answer_policy_snapshots

Plan Definition
├── agent_plans
├── agent_plan_versions
├── agent_plan_steps
├── agent_dependency_rules
├── agent_activation_conditions
└── agent_step_acceptance_criteria

Scheduling and Execution
├── agent_dispatch_groups
├── agent_dispatch_items
├── agent_step_runs
├── agent_branch_results
├── agent_reduction_attempts
├── agent_join_attempts
├── agent_resource_leases
└── agent_budget_reservations

Action and Side Effect
├── agent_action_runs
├── agent_observations
├── agent_acceptance_results
├── agent_reflection_results
├── agent_prepared_actions
├── agent_approval_decisions
├── agent_idempotency_claims
└── agent_reconciliation_records

Replan and Wait
├── agent_plan_patches
├── agent_plan_patch_operations
├── agent_replan_barriers
├── agent_interrupts
├── agent_signal_consumptions
└── agent_external_job_handles

Output
├── agent_final_candidates
├── agent_claims
├── agent_claim_evidence_bindings
├── agent_artifact_versions
├── agent_artifact_validations
├── agent_publications
├── agent_delivery_receipts
└── agent_run_outcomes

Validity and Eventing
├── agent_result_validity
├── agent_failures
├── agent_runtime_events
└── agent_outbox_events
```

关键约束：

```text
UNIQUE(workspace_id, client_request_id)
partial UNIQUE(run_id) WHERE PlanVersion.status = ACTIVE
UNIQUE(plan_version_id, logical_step_id)
UNIQUE(step_definition_id, attempt_no)
UNIQUE(idempotency_scope, idempotency_key)
UNIQUE(interrupt_id, signal_id)
UNIQUE(run_id, domain_generation)
UNIQUE(run_id, event_sequence_no)
partial INDEX(agent_interrupts.run_id) WHERE status = PENDING
partial INDEX(agent_outbox_events.created_at) WHERE published_at IS NULL
```

# 27. 事务边界

```text
Run / TaskContract / GoalVersion / RunCreated Event / Outbox
    同一事务提交。

Plan Activation
    验证在事务外；原子切换 Active PlanVersion 并提交 Event。

Dispatch
    DispatchGroup、Item、StepRun、Budget、Resource Claim 和 Event 同事务提交；之后才 Send。

External Action
    事务 A 提交 PreparedAction、ActionRun、IdempotencyClaim；事务外执行；事务 B 提交 Observation 和 Outcome。

Publication
    事务 A 提交 FinalCandidate、Gate、ArtifactVersion 和 PREPARED Publication；事务外发送；事务 B 提交 DeliveryReceipt、PUBLISHED 和 RunOutcome。
```

# 28. Contract Versioning

统一 Envelope：

```text
contract_name
contract_version
message_id
correlation_id
causation_id
run_id
step_run_id
producer
consumer
created_at
payload
payload_schema_hash
```

Run 创建时固定 Runtime、Graph、State、Contract、Prompt、Model Routing、Security 和 Answer Policy 版本。未知安全枚举必须 fail-closed。

---

# Part V：验证与完成证据

# 29. Target 测试矩阵

```text
状态：合法和非法迁移、Active PlanVersion 唯一、GoalVersion、CANCELLING、Epoch Fencing
DAG：依赖模式、Condition、Liveness、Join、Result Reuse
并发：Dispatch 崩溃点、Send 重放、Reducer 幂等、晚到结果、Replan Barrier
信号：多个 Interrupt、重复/乱序/过期 Signal、废弃 Step
副作用：Approval Hash、UNKNOWN、Reconcile、Compensation
一致性：Domain/Checkpoint Generation、RecoveryWatermark、Orphan Reconciler
质量：Evidence/Citation、ResultValidity、Final Gate、Final Reflection
发布：ArtifactVersion、Publication 幂等、DeliveryReceipt、撤回和更正
预算：Reservation、Soft/Hard Limit、公平性、No-progress
时间：数据库时间、Clock Skew、Deadline、Waiting Budget
```

# 30. Requirement Index

## 30.1 主设计 Requirement

| ID | Requirement |
| --- | --- |
| `ARCH-AGENT-001` | AgentRunGraph 是唯一产品主 Controller |
| `ARCH-AGENT-002` | Plan、ReAct、Reflection、Replan、Reflexion 在同一 Runtime 分层协作 |
| `ARCH-AGENT-003` | Runtime State 必须可序列化、版本化和恢复 |
| `ARCH-AGENT-004` | 所有循环必须受 RuntimeBudget 和 Deadline 控制 |
| `ARCH-AGENT-005` | 所有产品入口复用同一 Agent Runtime Contract |
| `ARCH-AGENT-006` | Interrupt / Signal / Resume 必须跨进程恢复 |
| `ARCH-AGENT-007` | Graph State 和领域表只保存大型内容 Ref |
| `ARCH-AGENT-008` | 每个控制阶段产生 RuntimeEvent 和 Trace Span |
| `ARCH-AGENT-009` | 所有任务都必须创建 Plan |
| `ARCH-AGENT-010` | Plan 表达为 DAG，并默认最大化安全并行 |
| `ARCH-AGENT-011` | PlanVersion 激活后不可变，Replan 创建新版本 |
| `ARCH-AGENT-012` | PlanStepDefinition、StepRun、ActionRun 和 Result 分离 |
| `ARCH-AGENT-013` | 每个 Run 固定 ExecutionContextSnapshot |
| `ARCH-AGENT-014` | 知识任务固定 KnowledgeSnapshot |
| `ARCH-AGENT-015` | Grounded Completion 通过 AnswerPolicy 和 Final Gate |
| `ARCH-AGENT-016` | 动态 Fan-out 通过 DispatchGroup、DispatchItem 和 StepRun 持久化 |
| `ARCH-AGENT-017` | 副作用 Action 声明 Replay、Approval 和 Idempotency Policy |
| `ARCH-AGENT-018` | RunOutcome 精确区分所有终局 |
| `ARCH-AGENT-019` | Cancellation、Deadline、Budget 和 Security 传播到所有分支 |
| `ARCH-AGENT-020` | 所有等待使用统一 Interrupt / Signal Contract |
| `ARCH-AGENT-021` | Graph State 只保存控制 Ref |
| `ARCH-AGENT-022` | 分层质量控制必须分离 |
| `ARCH-AGENT-023` | 每个 Step Acceptance，Critic 按 Trigger 调用 |
| `ARCH-AGENT-024` | 并行 Replan 经过 Replan Barrier |
| `ARCH-AGENT-025` | PostgreSQL 保存领域事实，Checkpointer 保存图控制状态 |
| `ARCH-AGENT-026` | 跨模块 Port 使用明确类型 |
| `ARCH-AGENT-027` | 外部执行明确 SUCCEEDED、FAILED 或 UNKNOWN |
| `ARCH-AGENT-028` | 领域写入与事件发布使用事务 + Outbox |
| `ARCH-AGENT-029` | 模型职责使用独立 Model Role |
| `ARCH-AGENT-030` | Planner 获得 Executor ModelCapabilityProfile |
| `ARCH-AGENT-031` | 模型升级受 RetryPolicy、Risk 和 Budget 控制 |
| `ARCH-AGENT-032` | 并行 Worker 只返回幂等 BranchResultRef |

编号 033–060 由控制协议定义；编号 061–080 由一致性协议定义。验证器确保编号 001 至 080 连续、无重复。

# 31. 完成状态

文档完成后仅可声明：

```text
design available
internally consistent
contract-complete
implementation-spec-complete
program-ready
```

不能仅凭文档声明 implementation available、measurement proven、quality proven 或 production ready。Target 转为 Current 必须具备代码、Migration、测试、故障注入、E2E、Trace、Eval 和可复现运行证据。
