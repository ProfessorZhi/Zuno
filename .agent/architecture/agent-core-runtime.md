# Agent Core Runtime V2

updated: 2026-07-12  
status: normative-target-module-architecture  
owner: Agent Core / Planning & Control  
formal_path: `docs/architecture/agent-core-runtime.md`  
agent_mirror: `.agent/architecture/agent-core-runtime.md`

> 本文是 Zuno Agent Core / Planning & Control 的实施级专题架构规范。它细化 `docs/architecture/architecture.md` 的 Agent Core 章节，直接约束后续代码所有权、LangGraph 拓扑、Domain Contract、PostgreSQL 表、Alembic Migration、事务边界、测试和完成证据。
>
> 本文描述 **Target**，不是 Current。当前已实现能力、Gap、Blocked 和 Measurement 仍以 `docs/architecture/production-readiness.md` 为事实源。

---

# 0. 文档同步与使用规则

- `docs/architecture/agent-core-runtime.md` 是正式模块专题文档；
- `.agent/architecture/agent-core-runtime.md` 是 Agent 工作区镜像；
- 两份文件必须保持字节级一致；
- 不得只修改 `.agent` 镜像；
- 本文不得把类名、表名、Docker 依赖或测试替身描述为已经生产完成；
- 后续 Program 必须引用本文的 Requirement ID，并给出 migration、test、eval、rollback 和 completion evidence；
- 若本文与总架构发生冲突，必须在同一 Program 中修正总架构，而不是维护两套互相竞争的 Controller 设计。

本文包含四类内容：

```text
Target Specification
    最终应实现的架构和 Contract

Current Baseline
    当前仓库已经存在、可以复用的基础

Migration Program
    从 Current 迁移到 Target 的顺序

Completion Evidence
    什么证据能够把 Target 写成 Current
```

---

# 1. 模块定位

Agent Core 是 Zuno 唯一的在线任务控制器，基于 LangGraph 将用户目标转化为可恢复、可观测、受预算和安全约束的执行过程。

Agent Core 负责：

```text
Runtime Request 校验
Execution Context Snapshot
Task Analysis
Runtime / Answer Policy 解析
Plan DAG 创建、验证、激活和版本化
默认最大化安全并行
Step 内 ReAct 循环
Observation 归一化
Acceptance Evaluation
Step / Final Reflection
PlanPatch / Replan
Interrupt / Resume
Cancellation / Deadline
RunOutcome
Reflexion Candidate Bridge
Runtime Event / Trace 关联
```

Agent Core 不负责：

```text
直接解析 PDF、DOCX、PPTX、XLSX 或图片
直接操作 Milvus、Neo4j、BM25
直接调用具体模型厂商 SDK
直接执行 Shell、浏览器、邮件或外部 API
直接写长期 Memory
直接实现合同、代码、研究或数据分析领域规则
直接绕过 Security 决定用户能否访问知识
```

模块协作：

```text
Agent Core
├── Model Gateway
├── Memory & Context
├── Knowledge / Agentic GraphRAG
├── Input / Document Ingestion
├── Capability / Skill
├── Tool Runtime
├── Security
├── Artifact Store
└── Observability & Eval
```

所有跨模块调用必须使用 typed Port 和 Contract。

---

# 2. 核心设计原则

## 2.1 LangGraph 是控制流引擎，不是业务数据库

LangGraph 负责：

```text
节点执行
条件路由
循环
动态 fan-out / fan-in
Interrupt / Resume
Checkpoint
子图组合
```

PostgreSQL 负责：

```text
AgentRun
ExecutionContextSnapshot
Plan / PlanVersion / PlanPatch
DispatchGroup
StepRun / ActionRun / Observation
Acceptance / Reflection / Failure
Interrupt / ExternalJobHandle
GroundedAnswer / RunOutcome
RuntimeEvent / Outbox
```

Graph State 只保存恢复控制流所需的 ID、Ref 和小型路由结果，不复制完整领域对象。

## 2.2 Single Controller

Zuno 默认只存在一个产品主 Controller。复杂任务依靠 Plan DAG、并行调度、ReAct 和 Replan 完成，不默认建设产品级 Multi-Agent Runtime。

## 2.3 五种 Agent 机制是嵌套关系

```text
Plan-and-Execute
    管理整个任务

ReAct
    管理一个 PlanStep 内部的动作循环

Reflection
    判断 Step 或最终结果是否达标

Replan
    修改剩余计划并创建新 PlanVersion

Reflexion
    生成跨任务经验候选并交给 Memory Governance
```

它们不是五个平级 Strategy，也不是五个独立 Agent。

## 2.4 所有任务都有 Plan

简单任务使用 Deterministic Single-Step Plan，不能通过 `direct_answer` 绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。

## 2.5 Plan 是 DAG

Plan 的执行顺序由依赖、JoinPolicy、资源约束和安全策略决定。`sequence_no` 只用于 UI 稳定排序，不表示真实执行顺序。

## 2.6 默认最大化安全并行

满足以下条件的 Ready Step 默认并行：

```text
不存在未满足依赖
不存在共享写资源冲突
不存在高风险不可逆副作用
并发配额允许
预算能够预留
Security Gate 允许
```

只有依赖、资源、安全、副作用、预算或 Provider 限流要求时才退化为串行。

## 2.7 模型只提出结构化建议

模型可以生成：

```text
PlanDraft
ActionDecision
ReflectionProposal
PlanPatchDraft
```

模型不能直接：

```text
更新数据库状态
激活 PlanVersion
执行未审批 Tool
修改已完成 Step
绕过权限
提交长期 Memory
```

所有模型输出必须经过确定性 Schema、Policy、Security 和 Budget Guard。

## 2.8 不保存隐藏思维链

系统只保存：

```text
决策摘要
选择的 Action
预期 Observation
失败事实
验证结果
可复用经验
```

不得保存模型隐藏推理链。

---

# 3. Requirement IDs

保留总架构已有 Requirement，并新增 V2 约束：

```text
ARCH-AGENT-001  LangGraph 是唯一产品主 Controller。
ARCH-AGENT-002  Plan、ReAct、Reflection、Replan、Reflexion 在同一 Runtime 协作。
ARCH-AGENT-003  Runtime State 可序列化、可版本化、可恢复。
ARCH-AGENT-004  所有循环受统一 RuntimeBudget 控制。
ARCH-AGENT-005  Completion 与 Workspace Task 共用同一 Runtime。
ARCH-AGENT-006  Interrupt / Resume 跨进程可恢复。
ARCH-AGENT-007  大对象只保存 Ref。
ARCH-AGENT-008  每个节点产生 RuntimeEvent 和 Trace Span。

ARCH-AGENT-009  所有任务都必须创建 Plan，包括简单任务。
ARCH-AGENT-010  Plan 必须表达为 DAG，并默认最大化安全并行。
ARCH-AGENT-011  PlanVersion 激活后不可变，Replan 必须创建新版本。
ARCH-AGENT-012  PlanStepDefinition、StepRun 和 ActionRun 必须分离。
ARCH-AGENT-013  每个 AgentRun 必须固定 ExecutionContextSnapshot。
ARCH-AGENT-014  知识任务必须固定 KnowledgeSnapshot，不得静默混用索引版本。
ARCH-AGENT-015  Grounded Completion 必须通过 AnswerPolicy。
ARCH-AGENT-016  Fan-out 必须通过持久化 DispatchGroup、DispatchItem 和 JoinResult 管理。
ARCH-AGENT-017  副作用 Action 必须声明 ReplayPolicy 和 IdempotencyPolicy。
ARCH-AGENT-018  RunOutcome 必须区分 COMPLETED、PARTIAL、ABSTAINED、REFUSED、BLOCKED、FAILED、CANCELLED。
ARCH-AGENT-019  Cancellation、Deadline、Budget 和 Security 必须传播到所有分支。
ARCH-AGENT-020  Ingestion、Tool Job、用户输入和审批等待必须使用统一 Interrupt Contract。
ARCH-AGENT-021  Graph State 只保存控制 Ref，领域事实存入 PostgreSQL / Object Store。
ARCH-AGENT-022  Acceptance Evaluation、Step Reflection 和 Final Reflection 必须分离。
ARCH-AGENT-023  Planner、Scheduler、Replan、Reflection 和 Finalization 必须产生可审计决策摘要。
ARCH-AGENT-024  并行 Replan 必须经过 Replan Barrier，不能覆盖仍在执行的 PlanVersion。
ARCH-AGENT-025  PostgreSQL 是 Agent Runtime 结构化事实源；LangGraph Checkpointer 只保存图控制状态。
ARCH-AGENT-026  所有跨模块 Port 必须使用明确输入输出类型，生产实现不得使用 Any 或 None 代替必需依赖。
ARCH-AGENT-027  所有外部执行必须明确成功、失败或 UNKNOWN，不得把未知副作用结果自动重试为失败。
ARCH-AGENT-028  所有领域写入和跨模块事件发布必须使用事务 + Outbox。
```

---

# 4. 代码分层与依赖方向

目标分层：

```text
Contracts
    ↓
Domain
    ↓
Application Services
    ↓
LangGraph Orchestration
    ↓
Ports
    ↓
Adapters / PostgreSQL
```

约束：

```text
Graph Node 不直接写 SQL
Domain 不导入 LangGraph
Application 不导入 FastAPI
Port 不返回 Any
ORM Row 不直接作为 Graph State
外部 API 调用不放在数据库事务内
```

## 4.1 目标目录

```text
src/backend/zuno/agent/
├── contracts/
│   ├── common.py
│   ├── requests.py
│   ├── policy.py
│   ├── planning.py
│   ├── execution.py
│   ├── reflection.py
│   ├── interrupt.py
│   ├── outcome.py
│   └── events.py
│
└── runtime/
    ├── service.py
    ├── composition.py
    ├── settings.py
    │
    ├── domain/
    │   ├── run.py
    │   ├── plan.py
    │   ├── step.py
    │   ├── action.py
    │   ├── observation.py
    │   ├── dispatch.py
    │   ├── reflection.py
    │   ├── failure.py
    │   ├── outcome.py
    │   └── errors.py
    │
    ├── application/
    │   ├── run_service.py
    │   ├── snapshot_service.py
    │   ├── planning_service.py
    │   ├── scheduling_service.py
    │   ├── step_execution_service.py
    │   ├── reflection_service.py
    │   ├── replan_service.py
    │   ├── finalization_service.py
    │   ├── interrupt_service.py
    │   ├── recovery_service.py
    │   └── cancellation_service.py
    │
    ├── graph/
    │   ├── run/
    │   │   ├── state.py
    │   │   ├── nodes.py
    │   │   ├── routing.py
    │   │   └── builder.py
    │   └── step/
    │       ├── state.py
    │       ├── nodes.py
    │       ├── routing.py
    │       └── builder.py
    │
    ├── planning/
    │   ├── analyzer.py
    │   ├── complexity.py
    │   ├── policy_resolver.py
    │   ├── router.py
    │   ├── normalizer.py
    │   ├── validator.py
    │   ├── repair.py
    │   └── planners/
    │       ├── deterministic.py
    │       ├── skill.py
    │       └── model.py
    │
    ├── scheduling/
    │   ├── readiness.py
    │   ├── selector.py
    │   ├── join.py
    │   ├── concurrency.py
    │   ├── resource_leases.py
    │   └── budget_reservations.py
    │
    ├── execution/
    │   ├── action_decider.py
    │   ├── action_validator.py
    │   ├── executor_registry.py
    │   └── executors/
    │       ├── model.py
    │       ├── retrieval.py
    │       ├── tool.py
    │       ├── ingestion.py
    │       └── interaction.py
    │
    ├── reflection/
    │   ├── acceptance.py
    │   ├── deterministic.py
    │   ├── critic.py
    │   └── decision_guard.py
    │
    ├── replan/
    │   ├── context.py
    │   ├── generator.py
    │   ├── validator.py
    │   ├── barrier.py
    │   └── applier.py
    │
    ├── ports/
    │   ├── model.py
    │   ├── knowledge.py
    │   ├── ingestion.py
    │   ├── memory.py
    │   ├── capability.py
    │   ├── tool.py
    │   ├── security.py
    │   ├── artifact.py
    │   ├── trace.py
    │   └── system.py
    │
    └── persistence/
        ├── unit_of_work.py
        ├── repositories.py
        └── postgres/
            ├── base.py
            ├── models.py
            ├── mappings.py
            ├── repositories.py
            └── unit_of_work.py
```

迁移期间保留 `zuno.agent.contracts` 的旧导出，通过 package `__init__.py` 提供 compatibility facade。

---

# 5. Contract、Domain 和 ORM 分离

## 5.1 Contract Model

跨模块传输使用 frozen Pydantic Model：

```python
class KnowledgeSnapshotRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    knowledge_space_id: str
    knowledge_version_id: str
    document_set_version: str
    bm25_index_version: str | None = None
    vector_index_version: str | None = None
    graph_index_version: str | None = None
```

## 5.2 Domain Model

Domain 负责状态机和业务规则，不依赖数据库和 LangGraph：

```python
@dataclass
class StepRun:
    step_run_id: UUID
    step_definition_id: UUID
    attempt_no: int
    status: StepRunStatus
    lock_version: int

    def start(self) -> None:
        if self.status is not StepRunStatus.QUEUED:
            raise InvalidTransition(...)
        self.status = StepRunStatus.RUNNING
        self.lock_version += 1
```

## 5.3 ORM Model

ORM 只负责持久化映射，通过 Mapper 转换为 Domain，不在 Graph 或 Port 中暴露 SQLAlchemy Row。

---

# 6. Runtime 状态机

## 6.1 AgentRun

```text
CREATED
→ RUNNING
→ WAITING
→ RUNNING
→ CANCELLING
→ CANCELLED

RUNNING / WAITING
→ COMPLETED
→ PARTIAL
→ ABSTAINED
→ REFUSED
→ BLOCKED
→ FAILED
```

`status` 表示生命周期，`phase` 表示当前阶段：

```text
INITIALIZING
RESOLVING_CONTEXT
PLANNING
EXECUTING
REPLANNING
FINALIZING
TERMINAL
```

## 6.2 PlanVersion

```text
DRAFT
→ VALIDATING
→ ACTIVE
→ SUPERSEDED

DRAFT / VALIDATING
→ REJECTED
```

一个 Plan 同时只能有一个 ACTIVE PlanVersion。

## 6.3 StepRun

```text
QUEUED
→ RUNNING
→ WAITING
→ RUNNING
→ COMPLETED
→ FAILED
→ BLOCKED
→ CANCELLED
```

失败重试必须创建新的 StepRun attempt，不得把失败记录改回 RUNNING。

## 6.4 ActionRun

```text
PROPOSED
→ VALIDATED
→ WAITING_APPROVAL
→ EXECUTING
→ SUCCEEDED
→ FAILED
→ UNKNOWN
→ CANCELLED
```

`UNKNOWN` 表示外部副作用结果无法确认，必须 Reconcile 或人工确认，不能直接自动重试。

## 6.5 DispatchGroup

```text
CREATED
→ DISPATCHED
→ COLLECTING
→ SATISFIED
→ PARTIAL
→ FAILED
→ CANCELLED
```

## 6.6 PlanPatch

```text
DRAFT
→ VALIDATING
→ VALIDATED
→ APPLIED

DRAFT / VALIDATING
→ REJECTED

VALIDATED
→ STALE
```

## 6.7 Interrupt

```text
PENDING
→ RESOLVED
→ EXPIRED
→ CANCELLED
```

---

# 7. 双层 LangGraph

```text
AgentRunGraph
└── StepExecutionGraph
```

## 7.1 AgentRunGraph

```text
START
→ initialize_run
→ input_gate
→ resolve_authorization
→ resolve_execution_snapshot
→ check_input_readiness
   ├── wait_ingestion → interrupt
   └── ready
→ build_context
→ analyze_task
→ resolve_runtime_policy
→ create_plan
→ normalize_plan
→ validate_plan
   ├── repair_plan
   └── activate_plan_version
→ schedule_ready_steps
→ create_dispatch_group
→ dynamic fan-out
   ├── StepExecutionGraph A
   ├── StepExecutionGraph B
   └── StepExecutionGraph C
→ collect_branch_results
→ evaluate_join
   ├── CONTINUE_PLAN
   ├── RETRY_BRANCHES
   ├── PARTIAL_CONTINUE
   ├── REPLAN
   ├── WAIT
   └── TERMINATE
→ schedule_ready_steps
→ final_synthesis
→ extract_claims
→ bind_claims_and_citations
→ answer_policy_gate
→ final_reflection
   ├── PASS
   ├── REWRITE
   ├── RETRIEVE_MORE
   ├── REPLAN
   ├── ASK_USER
   ├── ABSTAIN
   └── REFUSE
→ finalize_run_outcome
→ build_reflexion_candidate
→ post_turn_commit
→ END
```

## 7.2 StepExecutionGraph

```text
START
→ load_step_definition
→ resolve_step_inputs
→ acquire_resource_leases
→ reserve_budget
→ preflight_gate
→ decide_action
→ validate_action
→ execute_action
→ normalize_observation
→ persist_action_and_observation
→ evaluate_acceptance
→ decide_step_progress
   ├── CONTINUE_REACT → decide_action
   ├── RETRY_ACTION → execute_action
   ├── COMPLETE → complete_step
   ├── RETRY_STEP → finish_attempt
   ├── REPLAN → return_to_run_graph
   ├── WAIT_USER → interrupt
   ├── WAIT_APPROVAL → interrupt
   ├── WAIT_EXTERNAL → interrupt
   └── FAIL / BLOCK / ABSTAIN → finish_attempt
```

简单 Step 可以只执行一次 Action；复杂 Step 才运行多轮 ReAct。

---

# 8. LangGraph State Contract

使用轻量 `TypedDict`。并行分支结果必须使用幂等 Reducer，不能简单 `operator.add` 造成恢复后重复。

```python
class AgentRunGraphState(TypedDict, total=False):
    schema_version: str

    run_id: str
    task_id: str
    thread_id: str
    workspace_id: str
    trace_id: str

    phase: str
    execution_snapshot_id: str | None
    active_plan_id: str | None
    active_plan_version_id: str | None

    dispatch_group_id: str | None
    dispatch_item_refs: list[str]
    branch_results: Annotated[list[BranchResultRef], merge_branch_results]

    pending_interrupt_id: str | None
    latest_reflection_id: str | None
    final_answer_ref: str | None
    outcome_ref: str | None
    terminal_status: str | None
```

Step 子图使用独立 State：

```python
class StepGraphState(TypedDict, total=False):
    run_id: str
    workspace_id: str
    trace_id: str
    execution_snapshot_id: str
    dispatch_group_id: str
    step_run_id: str

    step_definition_id: str
    resolved_input_ref: str | None
    action_round: int
    latest_action_run_id: str | None
    latest_observation_id: str | None
    latest_acceptance_result_id: str | None
    decision: str | None
    output_ref: str | None
    failure_ref: str | None
    terminal_status: str | None
```

State 禁止保存：

```text
完整 Plan
完整 ContextPack
完整 Observation
完整检索结果
完整模型 Prompt
工具 stdout / stderr
文件正文
```

---

# 9. ExecutionContextSnapshot

每次 AgentRun 开始时固定：

```python
class ExecutionContextSnapshot(BaseModel):
    snapshot_id: UUID
    run_id: UUID

    authorization_context_ref: str
    authorization_policy_version: str
    security_epoch: int

    runtime_policy_ref: UUID
    answer_policy_ref: UUID
    model_policy_ref: str

    knowledge_snapshot_refs: list[KnowledgeSnapshotRef]
    skill_version_refs: list[str]
    capability_catalog_version: str
    prompt_bundle_version: str

    created_at: datetime
```

默认一个 Run 使用同一个 Snapshot。显式刷新时创建新 SnapshotVersion 并写 RuntimeEvent。

权限采用：

```text
正向权限范围固定
+
实时撤销永远优先
```

Snapshot 不能绕过用户被移出 Workspace、文档紧急撤销或 Security Epoch 变化。

---

# 10. RuntimePolicy 与 AnswerPolicy

RuntimePolicy 决定怎样执行：

```python
class RuntimePolicy(BaseModel):
    planning_mode: Literal["deterministic", "skill", "model"]
    react_policy: Literal["single_action", "dynamic"]
    step_reflection_policy: Literal["none", "critical", "every_step"]
    final_reflection_policy: Literal["deterministic", "critic", "strict"]
    replan_policy: Literal["disabled", "on_failure", "on_material_change"]
    reflexion_policy: Literal["disabled", "meaningful_outcome"]

    concurrency_policy_ref: str
    budget_policy_ref: str
    cancellation_policy_ref: str
    retrieval_policy_ref: str | None
    tool_policy_ref: str | None
    approval_policy_ref: str | None
```

AnswerPolicy 决定什么条件下允许输出：

```python
class AnswerPolicy(BaseModel):
    grounding_mode: Literal["none", "optional", "required", "strict"]
    minimum_evidence_count: int
    minimum_evidence_coverage: float
    minimum_authority_level: str | None

    citation_required: bool
    source_span_required: bool
    allow_model_prior: bool
    allow_partial_answer: bool

    disclose_missing_information: bool
    disclose_conflicting_evidence: bool
    disclose_stale_sources: bool

    insufficient_evidence_action: Literal["partial", "ask_user", "abstain", "fail"]
```

企业知识问答默认：

```text
grounding_mode = strict
allow_model_prior = false
citation_required = true
source_span_required = true
insufficient_evidence_action = abstain
```

---

# 11. Planner Pipeline

```text
TaskAnalyzer
→ ComplexityClassifier
→ RuntimePolicyResolver
→ PlannerRouter
→ DeterministicPlanner / SkillPlanner / ModelPlanner
→ PlanNormalizer
→ PlanValidator
→ PlanRepair
→ PlanRepository
```

## 11.1 Planner 选择

```text
确定性规则可解决
→ DeterministicPlanner

匹配稳定 Skill Template
→ SkillPlanner

开放式、多目标、动态任务
→ ModelPlanner
```

## 11.2 Validator Rules

```text
SchemaRule
DuplicateStepRule
DependencyExistsRule
AcyclicGraphRule
GoalCoverageRule
StepGranularityRule
CapabilityExistsRule
InputOutputCompatibilityRule
SecurityPolicyRule
BudgetRule
ParallelSafetyRule
JoinPolicyRule
```

独立规则可并行运行。PlanRepair 最多两轮，仍不合法时使用 Safe Minimal Plan、Ask User 或 Abstain。

---

# 12. Plan Domain Model

## 12.1 Plan

```python
class Plan:
    plan_id: UUID
    run_id: UUID
    current_version_id: UUID | None
    status: PlanStatus
    version_count: int
    replan_count: int
    lock_version: int
```

## 12.2 PlanVersion

```python
class PlanVersion:
    plan_version_id: UUID
    plan_id: UUID
    version_no: int
    base_version_id: UUID | None
    source_patch_id: UUID | None
    goal_summary: str
    assumptions: list[str]
    status: PlanVersionStatus
    content_hash: str
```

激活后不可修改。

## 12.3 PlanStepDefinition

```python
class PlanStepDefinition(BaseModel):
    step_definition_id: UUID
    plan_version_id: UUID
    logical_step_id: str
    origin_step_definition_id: UUID | None

    title: str
    objective: str
    action_type: ActionType

    input_contract: list[StepInputSpec]
    output_contract: StepOutputContract
    acceptance_criteria: list[AcceptanceCriterion]
    evidence_requirements: list[EvidenceRequirement]

    allowed_capabilities: list[str]
    retrieval_policy_ref: str | None
    tool_policy_ref: str | None
    model_role: str | None

    retry_policy: RetryPolicy
    budget: StepBudget
    concurrency_policy: ConcurrencyPolicy
    replay_policy: ReplayPolicy

    execution_disposition: ExecutionDisposition
    satisfied_by_step_run_id: UUID | None
    optional: bool
    priority: int
```

PlanStepDefinition 不保存 status、attempt、Observation 或 Failure。

---

# 13. 默认并行调度

## 13.1 Ready Step 条件

```text
属于 ACTIVE PlanVersion
execution_disposition = EXECUTE
所有 HARD Dependency 已满足
不存在成功 StepRun
不存在有效运行 Lease
Capability 可用
预算能够预留
资源锁能够获得
Security Gate 允许
Deadline 未到期
Run 未取消
```

## 13.2 SchedulingDecision

```python
class SchedulingDecision(BaseModel):
    ready_step_ids: list[UUID]
    selected_step_ids: list[UUID]
    deferred_steps: list[DeferredStep]
    budget_reservations: list[BudgetReservationRequest]
    resource_lease_requests: list[ResourceLeaseRequest]
    decision_summary: str
```

Scheduler 选择“最大安全集合”，不是无条件选择所有 Ready Step。

## 13.3 DispatchGroup

```python
class DispatchGroup:
    dispatch_group_id: UUID
    run_id: UUID
    plan_version_id: UUID
    scheduler_round: int
    join_policy: JoinPolicy
    branch_failure_policy: BranchFailurePolicy
    quorum: int | None
    expected_branch_count: int
    completed_branch_count: int
    succeeded_branch_count: int
    failed_branch_count: int
    cancelled_branch_count: int
    status: DispatchStatus
```

DispatchGroup、DispatchItem、StepRun、BudgetReservation、ResourceLease 必须在一个 PostgreSQL 事务中创建。提交成功后才能执行 LangGraph `Send`。

## 13.4 JoinPolicy

```text
ALL_SUCCESS
ALL_TERMINAL
ANY_SUCCESS
QUORUM
BEST_EFFORT
```

## 13.5 BranchFailurePolicy

```text
CONTINUE_SIBLINGS
CANCEL_SIBLINGS
FAIL_FAST
JOIN_THEN_REPLAN
JOIN_THEN_REFLECT
```

---

# 14. Resource Lease 与 Budget Reservation

## 14.1 ResourceLease

```python
class ResourceRequirement(BaseModel):
    resource_key: str
    access_mode: Literal["read", "write", "exclusive"]
```

示例：

```text
repo:zuno
file:/workspace/src/runtime.py
sandbox:run-123
database:customer-prod
```

多个 READ 可共享；WRITE 与 EXCLUSIVE 互斥。

## 14.2 BudgetReservation

并行调度前预留：

```text
Token
Cost
Model Call
Tool Call
Retrieval Round
Wall-clock Deadline
```

完成后按真实消耗结算并释放剩余预算。未成功预留预算的 Step 不得启动。

---

# 15. ReAct Action Runtime

## 15.1 ActionDecision

```python
class ActionDecision(BaseModel):
    action_kind: ActionKind
    capability_id: str | None
    arguments_ref: str | None
    decision_summary: str
    expected_observation: str
    completion_claimed: bool
```

ActionKind：

```text
MODEL
RETRIEVE
TOOL
SUBMIT_INGESTION
ASK_USER
REQUEST_APPROVAL
WAIT_EXTERNAL
COMPLETE_STEP
FAIL_STEP
```

## 15.2 Action Guard

执行前必须经过：

```text
Schema Validation
Capability Validation
Security Validation
Budget Validation
Approval Validation
Replay Policy Validation
Resource Lease Validation
```

## 15.3 ActionExecutorRegistry

```python
class ActionExecutor(Protocol):
    async def execute(self, command: ExecuteActionCommand) -> ExecuteActionResult: ...
```

注册表映射 ActionKind 到 Model、Retrieval、Tool、Ingestion 或 Interaction Executor。

## 15.4 幂等键

```text
sha256(run_id + step_run_id + action_round + decision_hash)
```

Core 幂等不能替代 Tool Runtime 自己的 ToolExecutionClaim。

---

# 16. Observation、Acceptance 与 Reflection

## 16.1 Observation

```python
class Observation(BaseModel):
    observation_id: UUID
    run_id: UUID
    step_run_id: UUID
    action_run_id: UUID
    kind: str
    status: str
    source_type: str
    source_ref: str | None
    summary: str
    payload_ref: str | None
    evidence_refs: list[str]
    citation_refs: list[str]
    failure_ref: UUID | None
```

大型结果进入 Object Store。

## 16.2 AcceptanceCriterion

```text
SCHEMA_VALID
OUTPUT_EXISTS
EVIDENCE_COUNT
EVIDENCE_COVERAGE
CITATION_COVERAGE
SOURCE_AUTHORITY
SOURCE_FRESHNESS
TEST_PASS_RATE
TOOL_STATUS
ARTIFACT_EXISTS
SECURITY_ALLOWED
CUSTOM
```

Evaluator：

```text
DETERMINISTIC
MODEL_CRITIC
EXTERNAL
HUMAN
```

## 16.3 Step Reflection

```text
PASS
CONTINUE_REACT
RETRY_ACTION
RETRY_STEP
RETRIEVE_MORE
REPLAN
WAIT_USER
WAIT_APPROVAL
WAIT_EXTERNAL
BLOCK
ABSTAIN
```

模型 Critic 的建议必须通过 ReflectionDecisionGuard，不能绕过 RetryPolicy、ToolPolicy、SecurityPolicy 或 Budget。

---

# 17. Replan 与并行屏障

Replan 流程：

```text
Reflection.REPLAN
→ ReplanRequest
→ ReplanBarrier
→ 等待或取消不再安全的并行分支
→ ReplanContextBuilder
→ PlanPatchGenerator
→ PlanPatchValidator
→ PlanPatchApplier
→ PlanVersion N+1
```

ReplanBarrierPolicy：

```text
WAIT_ALL
DRAIN_SAFE_READ_ONLY
CANCEL_OBSOLETE
```

Patch Operation：

```text
ADD_STEP
REMOVE_PENDING_STEP
REPLACE_PENDING_STEP
ADD_DEPENDENCY
REMOVE_DEPENDENCY
CHANGE_POLICY
CHANGE_ACCEPTANCE
REALLOCATE_BUDGET
CHANGE_JOIN_POLICY
CHANGE_RESOURCE_REQUIREMENT
```

应用 Patch 时必须验证：

```text
patch.base_version_id == plan.current_version_id
```

否则 Patch 标记 STALE。

已完成 Step 通过：

```text
execution_disposition = REUSE_COMPLETED
satisfied_by_step_run_id = previous successful StepRun
```

复用，不重新执行。

---

# 18. Knowledge、Ingestion 与 AnswerPolicy

## 18.1 KnowledgeSnapshot

每次知识查询必须携带：

```text
workspace_id
authorization_context_ref
security_epoch
knowledge_snapshot_ref
```

不得静默切换 BM25、Vector 或 Graph Index Version。

## 18.2 Knowledge Failure

```text
KNOWLEDGE_MISS
RETRIEVAL_MISS
PARSING_MISS
INDEX_STALE
INDEX_INCOMPATIBLE
PERMISSION_FILTERED
EVIDENCE_INSUFFICIENT
EVIDENCE_CONFLICT
SOURCE_SPAN_MISSING
```

Core 路由必须区分：

```text
RETRIEVAL_MISS       → Query Rewrite / 换 Retriever
KNOWLEDGE_MISS       → 披露知识缺口
PARSING_MISS         → 提交重新解析并等待
INDEX_STALE          → 等待或 Block
PERMISSION_FILTERED  → 停止，禁止绕过
EVIDENCE_CONFLICT    → 冲突分析并披露
SOURCE_SPAN_MISSING  → strict citation 不通过
```

## 18.3 Ingestion Wait

Core 只通过 IngestionPort 提交和查询任务：

```text
SUBMIT_INGESTION
→ ExternalJobHandle
→ WAIT_EXTERNAL
→ LangGraph interrupt
→ DocumentReady / KnowledgeVersionReady
→ resume original node
```

Core 不直接调用 Parser。

## 18.4 Finalization

```text
收集有效 Step Output
→ Grounded Synthesis
→ Claim Extraction
→ Claim-Evidence Binding
→ Citation Binding
→ AnswerPolicy Gate
→ Final Reflection
→ RunOutcome
```

---

# 19. Interrupt、Resume、Replay 与 Cancellation

## 19.1 Interrupt

`interrupt()` 节点必须幂等。恢复会从该节点开头重新执行，因此不可逆副作用必须放在 Interrupt 之后的独立节点。

## 19.2 ReplayPolicy

```text
PURE
READ_ONLY_SNAPSHOT
IDEMPOTENT_WRITE
COMPENSATABLE_WRITE
NON_REPLAYABLE
```

```text
PURE                 → 可重算
READ_ONLY_SNAPSHOT   → 固定 Snapshot 后可重放
IDEMPOTENT_WRITE     → 相同幂等键重放
COMPENSATABLE_WRITE  → 先 Reconcile
NON_REPLAYABLE       → 人工确认
```

## 19.3 Cancellation

```text
Run → CANCELLING
停止新调度
取消 QUEUED StepRun
请求取消 RUNNING Action
释放 BudgetReservation
释放 ResourceLease
等待不可中断副作用收口
汇总 DispatchGroup
RunOutcome → CANCELLED / PARTIAL
```

Deadline 使用相同传播路径，但可按 AnswerPolicy 返回 PARTIAL 或 BLOCKED。

---

# 20. Port 设计

生产 Port 不得使用 `Any`，必需依赖不得为 `None`。

```python
class ModelGatewayPort(Protocol):
    async def invoke(self, request: ModelInvocationRequest) -> ModelInvocationResult: ...

class KnowledgeQueryPort(Protocol):
    async def retrieve(self, request: KnowledgeQueryRequest) -> KnowledgeQueryResult: ...

class IngestionPort(Protocol):
    async def submit(self, request: SubmitIngestionRequest) -> ExternalJobHandle: ...
    async def get_status(self, job_id: str) -> ExternalJobStatus: ...
    async def cancel(self, job_id: str) -> None: ...

class ToolRuntimePort(Protocol):
    async def prepare(self, request: PrepareToolExecutionRequest) -> PreparedToolExecution: ...
    async def execute(self, request: ExecutePreparedToolRequest) -> ToolExecutionResult: ...
    async def reconcile(self, execution_id: str) -> ToolExecutionResult: ...
```

测试环境使用 Fake Port，不使用 `None`。

---

# 21. Repository 与 Unit of Work

拆除大而全的 `AgentRunStore` 目标接口，改为：

```text
AgentRunRepository
ExecutionSnapshotRepository
PolicySnapshotRepository
PlanRepository
PlanPatchRepository
DispatchRepository
StepRunRepository
ActionRunRepository
ObservationRepository
AcceptanceRepository
ReflectionRepository
FailureRepository
InterruptRepository
OutcomeRepository
RuntimeEventRepository
OutboxRepository
```

Unit of Work：

```python
class AgentUnitOfWork(Protocol):
    runs: AgentRunRepository
    snapshots: ExecutionSnapshotRepository
    plans: PlanRepository
    patches: PlanPatchRepository
    dispatches: DispatchRepository
    steps: StepRunRepository
    actions: ActionRunRepository
    observations: ObservationRepository
    acceptances: AcceptanceRepository
    reflections: ReflectionRepository
    failures: FailureRepository
    interrupts: InterruptRepository
    outcomes: OutcomeRepository
    events: RuntimeEventRepository
    outbox: OutboxRepository

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

Application Service 管理事务；Graph Node 只调用 Service 并返回小型 State Patch。

---

# 22. PostgreSQL 总体设计

## 22.1 Schema

```text
agent_runtime
    Zuno Agent Core 领域事实

langgraph_checkpoint
    LangGraph Checkpointer vendor-owned tables
```

Zuno Alembic 只创建 `langgraph_checkpoint` Schema；具体 Checkpointer 表由锁定版本的 `AsyncPostgresSaver.setup()` 管理，避免复制 vendor DDL。

## 22.2 类型约定

```text
Agent Core 自有 ID       UUID，由应用生成
跨模块 ID / Ref          TEXT，保留 Owner 原始语义
时间                     TIMESTAMPTZ
计数                     INTEGER / BIGINT
金额                     NUMERIC(18, 6)
Token                    BIGINT
不可变小型配置快照       JSONB
大型 Payload             Object Store Ref
状态                     VARCHAR + CHECK，暂不使用 PostgreSQL ENUM
```

不使用 PostgreSQL ENUM 的原因：状态扩展和滚动升级更容易采用 expand/contract。

## 22.3 通用字段

高频领域表至少包含：

```text
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
trace_id TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

可更新表增加：

```text
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0
```

审计事实默认使用 `ON DELETE RESTRICT`。任务删除采用 archive / revoke，不级联删除运行历史。

---

# 23. PostgreSQL 表清单

```text
agent_runs
agent_execution_context_snapshots
agent_knowledge_snapshot_refs
agent_runtime_policy_snapshots
agent_answer_policy_snapshots

agent_plans
agent_plan_versions
agent_plan_steps
agent_plan_step_dependencies
agent_step_acceptance_criteria
agent_plan_patches
agent_plan_patch_operations
agent_replan_barriers

agent_dispatch_groups
agent_dispatch_items
agent_step_runs
agent_resource_leases
agent_budget_reservations

agent_action_runs
agent_observations
agent_acceptance_results
agent_reflection_results
agent_failures

agent_interrupts
agent_external_job_handles

agent_grounded_answers
agent_claims
agent_claim_evidence_bindings
agent_run_outcomes

agent_runtime_events
agent_outbox_events
```

---

# 24. 精确表结构

以下为目标逻辑 DDL。实际 Alembic 使用 SQLAlchemy Core 创建，命名必须与本文一致。

## 24.1 agent_runs

```sql
CREATE TABLE agent_runtime.agent_runs (
    run_id UUID PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    client_request_id TEXT NOT NULL,

    goal_ref TEXT NOT NULL,
    goal_summary TEXT NOT NULL,

    status VARCHAR(32) NOT NULL,
    phase VARCHAR(32) NOT NULL,

    execution_snapshot_id UUID NULL,
    active_plan_id UUID NULL,
    active_plan_version_id UUID NULL,
    pending_interrupt_id UUID NULL,
    outcome_id UUID NULL,
    latest_failure_id UUID NULL,

    scheduler_round INTEGER NOT NULL DEFAULT 0,
    model_call_count INTEGER NOT NULL DEFAULT 0,
    tool_call_count INTEGER NOT NULL DEFAULT 0,
    retrieval_round_count INTEGER NOT NULL DEFAULT 0,
    input_tokens BIGINT NOT NULL DEFAULT 0,
    output_tokens BIGINT NOT NULL DEFAULT 0,
    cost_total NUMERIC(18, 6) NOT NULL DEFAULT 0,

    deadline_at TIMESTAMPTZ NULL,
    cancel_requested_at TIMESTAMPTZ NULL,
    cancel_reason TEXT NULL,

    lock_version INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ NULL,

    CONSTRAINT uq_agent_runs_workspace_client
        UNIQUE (workspace_id, client_request_id),
    CONSTRAINT ck_agent_runs_status
        CHECK (status IN (
            'created', 'running', 'waiting', 'cancelling',
            'completed', 'partial', 'abstained', 'refused',
            'blocked', 'failed', 'cancelled'
        )),
    CONSTRAINT ck_agent_runs_phase
        CHECK (phase IN (
            'initializing', 'resolving_context', 'planning',
            'executing', 'replanning', 'finalizing', 'terminal'
        ))
);
```

索引：

```sql
CREATE INDEX ix_agent_runs_workspace_status_updated
    ON agent_runtime.agent_runs (workspace_id, status, updated_at DESC);

CREATE INDEX ix_agent_runs_thread_created
    ON agent_runtime.agent_runs (thread_id, created_at DESC);

CREATE INDEX ix_agent_runs_deadline_active
    ON agent_runtime.agent_runs (deadline_at)
    WHERE status IN ('created', 'running', 'waiting', 'cancelling');
```

## 24.2 agent_execution_context_snapshots

```text
snapshot_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL FK agent_runs
snapshot_version INTEGER NOT NULL
authorization_context_ref TEXT NOT NULL
authorization_policy_version TEXT NOT NULL
security_epoch BIGINT NOT NULL
runtime_policy_snapshot_id UUID NOT NULL
answer_policy_snapshot_id UUID NOT NULL
model_policy_ref TEXT NOT NULL
capability_catalog_version TEXT NOT NULL
prompt_bundle_version TEXT NOT NULL
skill_version_refs_json JSONB NOT NULL
content_hash TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(run_id, snapshot_version)
UNIQUE(run_id, content_hash)
```

## 24.3 agent_knowledge_snapshot_refs

```text
knowledge_snapshot_ref_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
execution_snapshot_id UUID NOT NULL
knowledge_space_id TEXT NOT NULL
knowledge_version_id TEXT NOT NULL
document_set_version TEXT NOT NULL
bm25_index_version TEXT NULL
vector_index_version TEXT NULL
graph_index_version TEXT NULL
effective_at TIMESTAMPTZ NOT NULL
status VARCHAR(24) NOT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(execution_snapshot_id, knowledge_space_id)
```

## 24.4 Policy Snapshot Tables

`agent_runtime_policy_snapshots`：

```text
runtime_policy_snapshot_id UUID PK
workspace_id TEXT NOT NULL
policy_version TEXT NOT NULL
policy_json JSONB NOT NULL
content_hash TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL
UNIQUE(workspace_id, content_hash)
```

`agent_answer_policy_snapshots` 同结构，使用 `answer_policy_snapshot_id`。

Policy Snapshot 写入后不可修改。

## 24.5 agent_plans

```text
plan_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL FK agent_runs
status VARCHAR(24) NOT NULL
current_version_id UUID NULL
version_count INTEGER NOT NULL DEFAULT 0
replan_count INTEGER NOT NULL DEFAULT 0
lock_version INTEGER NOT NULL DEFAULT 0
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL

UNIQUE(run_id)
CHECK(status IN ('created', 'active', 'replanning', 'completed', 'failed', 'cancelled'))
```

## 24.6 agent_plan_versions

```text
plan_version_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL FK agent_plans
version_no INTEGER NOT NULL
base_version_id UUID NULL FK agent_plan_versions
source_patch_id UUID NULL
status VARCHAR(24) NOT NULL
planner_type VARCHAR(24) NOT NULL
planner_model_call_ref TEXT NULL
goal_summary TEXT NOT NULL
assumptions_json JSONB NOT NULL
planning_context_ref TEXT NULL
content_hash TEXT NOT NULL
activation_reason TEXT NULL
created_at TIMESTAMPTZ NOT NULL
activated_at TIMESTAMPTZ NULL
superseded_at TIMESTAMPTZ NULL

UNIQUE(plan_id, version_no)
UNIQUE(plan_id, content_hash)
```

部分唯一索引：

```sql
CREATE UNIQUE INDEX uq_agent_plan_versions_one_active
    ON agent_runtime.agent_plan_versions (plan_id)
    WHERE status = 'active';
```

## 24.7 agent_plan_steps

```text
step_definition_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL
plan_version_id UUID NOT NULL FK agent_plan_versions
logical_step_id TEXT NOT NULL
origin_step_definition_id UUID NULL
sequence_no INTEGER NOT NULL
title TEXT NOT NULL
objective TEXT NOT NULL
action_type VARCHAR(32) NOT NULL
input_contract_json JSONB NOT NULL
output_contract_json JSONB NOT NULL
evidence_requirements_json JSONB NOT NULL
allowed_capabilities_json JSONB NOT NULL
retrieval_policy_ref TEXT NULL
tool_policy_ref TEXT NULL
model_role TEXT NULL
retry_policy_json JSONB NOT NULL
budget_json JSONB NOT NULL
concurrency_policy_json JSONB NOT NULL
replay_policy_json JSONB NOT NULL
execution_disposition VARCHAR(24) NOT NULL
satisfied_by_step_run_id UUID NULL
optional BOOLEAN NOT NULL DEFAULT FALSE
priority INTEGER NOT NULL DEFAULT 100
content_hash TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(plan_version_id, logical_step_id)
UNIQUE(plan_version_id, sequence_no)
```

PlanStepDefinition 激活后不可更新。

## 24.8 agent_plan_step_dependencies

```text
dependency_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_version_id UUID NOT NULL
step_definition_id UUID NOT NULL
requires_step_definition_id UUID NOT NULL
dependency_type VARCHAR(16) NOT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(plan_version_id, step_definition_id, requires_step_definition_id)
CHECK(step_definition_id <> requires_step_definition_id)
CHECK(dependency_type IN ('hard', 'soft'))
```

DAG 无环由 PlanValidator 保证；数据库约束只能阻止自依赖和重复边。

## 24.9 agent_step_acceptance_criteria

```text
criterion_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_version_id UUID NOT NULL
step_definition_id UUID NOT NULL
criterion_order INTEGER NOT NULL
criterion_type VARCHAR(40) NOT NULL
operator VARCHAR(24) NOT NULL
expected_value_json JSONB NULL
evaluator_type VARCHAR(24) NOT NULL
required BOOLEAN NOT NULL DEFAULT TRUE
config_json JSONB NOT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(step_definition_id, criterion_order)
```

## 24.10 agent_plan_patches

```text
patch_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL
base_version_id UUID NOT NULL
status VARCHAR(24) NOT NULL
trigger_type VARCHAR(40) NOT NULL
trigger_ref TEXT NOT NULL
reason TEXT NOT NULL
created_by VARCHAR(24) NOT NULL
model_call_ref TEXT NULL
validated_at TIMESTAMPTZ NULL
applied_version_id UUID NULL
failure_id UUID NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0

CHECK(status IN ('draft', 'validating', 'validated', 'applied', 'rejected', 'stale'))
```

## 24.11 agent_plan_patch_operations

```text
operation_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
patch_id UUID NOT NULL
operation_order INTEGER NOT NULL
operation_type VARCHAR(40) NOT NULL
target_logical_step_id TEXT NULL
payload_json JSONB NOT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(patch_id, operation_order)
```

## 24.12 agent_replan_barriers

```text
barrier_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL
base_version_id UUID NOT NULL
policy VARCHAR(32) NOT NULL
status VARCHAR(24) NOT NULL
requested_by_ref TEXT NOT NULL
active_branch_count INTEGER NOT NULL
safe_branch_count INTEGER NOT NULL
cancel_requested_count INTEGER NOT NULL
created_at TIMESTAMPTZ NOT NULL
satisfied_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0

UNIQUE(plan_id) WHERE status IN ('created', 'draining')
```

部分唯一约束通过 partial unique index 实现。

## 24.13 agent_dispatch_groups

```text
dispatch_group_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_version_id UUID NOT NULL
scheduler_round INTEGER NOT NULL
join_policy VARCHAR(24) NOT NULL
branch_failure_policy VARCHAR(32) NOT NULL
quorum INTEGER NULL
expected_branch_count INTEGER NOT NULL
completed_branch_count INTEGER NOT NULL DEFAULT 0
succeeded_branch_count INTEGER NOT NULL DEFAULT 0
failed_branch_count INTEGER NOT NULL DEFAULT 0
cancelled_branch_count INTEGER NOT NULL DEFAULT 0
status VARCHAR(24) NOT NULL
decision_summary TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL
dispatched_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0

UNIQUE(run_id, scheduler_round)
```

## 24.14 agent_dispatch_items

```text
dispatch_item_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
dispatch_group_id UUID NOT NULL
step_definition_id UUID NOT NULL
step_run_id UUID NOT NULL
branch_no INTEGER NOT NULL
status VARCHAR(24) NOT NULL
result_ref TEXT NULL
failure_id UUID NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL

UNIQUE(dispatch_group_id, branch_no)
UNIQUE(dispatch_group_id, step_definition_id)
UNIQUE(step_run_id)
```

## 24.15 agent_step_runs

```text
step_run_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL
plan_version_id UUID NOT NULL
step_definition_id UUID NOT NULL
logical_step_id TEXT NOT NULL
dispatch_group_id UUID NOT NULL
attempt_no INTEGER NOT NULL
status VARCHAR(24) NOT NULL
resolved_input_ref TEXT NULL
output_ref TEXT NULL
acceptance_summary_json JSONB NOT NULL
failure_id UUID NULL
budget_reservation_id UUID NULL
worker_id TEXT NULL
lease_token TEXT NULL
lease_expires_at TIMESTAMPTZ NULL
idempotency_key TEXT NOT NULL
elapsed_ms BIGINT NOT NULL DEFAULT 0
model_call_count INTEGER NOT NULL DEFAULT 0
tool_call_count INTEGER NOT NULL DEFAULT 0
retrieval_round_count INTEGER NOT NULL DEFAULT 0
input_tokens BIGINT NOT NULL DEFAULT 0
output_tokens BIGINT NOT NULL DEFAULT 0
cost_total NUMERIC(18, 6) NOT NULL DEFAULT 0
started_at TIMESTAMPTZ NULL
finished_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0

UNIQUE(step_definition_id, attempt_no)
UNIQUE(idempotency_key)
```

Scheduler 查询索引：

```sql
CREATE INDEX ix_agent_step_runs_run_status
    ON agent_runtime.agent_step_runs (run_id, status, created_at);

CREATE INDEX ix_agent_step_runs_lease_expiry
    ON agent_runtime.agent_step_runs (lease_expires_at)
    WHERE status IN ('queued', 'running', 'waiting');
```

## 24.16 agent_resource_leases

```text
resource_lease_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
resource_key TEXT NOT NULL
access_mode VARCHAR(16) NOT NULL
status VARCHAR(16) NOT NULL
lease_token TEXT NOT NULL
acquired_at TIMESTAMPTZ NOT NULL
expires_at TIMESTAMPTZ NOT NULL
released_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(step_run_id, resource_key)
UNIQUE(lease_token)
```

同一 `resource_key` 的读写互斥不能只靠普通唯一约束。第一版由 `pg_advisory_xact_lock(hashtextextended(resource_key, 0))` 加事务内冲突查询实现；未来规模化后可引入独立 Lease Service。

## 24.17 agent_budget_reservations

```text
budget_reservation_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
status VARCHAR(16) NOT NULL
reserved_input_tokens BIGINT NOT NULL DEFAULT 0
reserved_output_tokens BIGINT NOT NULL DEFAULT 0
reserved_cost NUMERIC(18, 6) NOT NULL DEFAULT 0
reserved_model_calls INTEGER NOT NULL DEFAULT 0
reserved_tool_calls INTEGER NOT NULL DEFAULT 0
reserved_retrieval_rounds INTEGER NOT NULL DEFAULT 0
used_input_tokens BIGINT NOT NULL DEFAULT 0
used_output_tokens BIGINT NOT NULL DEFAULT 0
used_cost NUMERIC(18, 6) NOT NULL DEFAULT 0
used_model_calls INTEGER NOT NULL DEFAULT 0
used_tool_calls INTEGER NOT NULL DEFAULT 0
used_retrieval_rounds INTEGER NOT NULL DEFAULT 0
created_at TIMESTAMPTZ NOT NULL
settled_at TIMESTAMPTZ NULL
released_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0

UNIQUE(step_run_id)
```

## 24.18 agent_action_runs

```text
action_run_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
action_round INTEGER NOT NULL
action_kind VARCHAR(32) NOT NULL
capability_id TEXT NULL
decision_summary TEXT NOT NULL
expected_observation TEXT NOT NULL
arguments_ref TEXT NULL
arguments_preview_json JSONB NOT NULL
replay_mode VARCHAR(32) NOT NULL
side_effect_class VARCHAR(32) NOT NULL
status VARCHAR(24) NOT NULL
idempotency_key TEXT NOT NULL
model_call_ref TEXT NULL
retrieval_run_ref TEXT NULL
tool_execution_ref TEXT NULL
ingestion_job_ref TEXT NULL
approval_ref TEXT NULL
observation_id UUID NULL
failure_id UUID NULL
retry_of_action_run_id UUID NULL
input_tokens BIGINT NOT NULL DEFAULT 0
output_tokens BIGINT NOT NULL DEFAULT 0
cost_total NUMERIC(18, 6) NOT NULL DEFAULT 0
started_at TIMESTAMPTZ NULL
finished_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0

UNIQUE(step_run_id, action_round)
UNIQUE(idempotency_key)
```

## 24.19 agent_observations

Append-only：

```text
observation_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
action_run_id UUID NOT NULL
kind VARCHAR(40) NOT NULL
status VARCHAR(24) NOT NULL
source_type VARCHAR(32) NOT NULL
source_ref TEXT NULL
summary TEXT NOT NULL
payload_ref TEXT NULL
payload_preview_json JSONB NOT NULL
evidence_refs_json JSONB NOT NULL
citation_refs_json JSONB NOT NULL
failure_id UUID NULL
trace_span_ref TEXT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(action_run_id)
```

## 24.20 agent_acceptance_results

Append-only：

```text
acceptance_result_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
criterion_id UUID NOT NULL
passed BOOLEAN NOT NULL
actual_value_json JSONB NULL
evaluator_type VARCHAR(24) NOT NULL
evaluator_ref TEXT NULL
reason TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(step_run_id, criterion_id)
```

## 24.21 agent_reflection_results

```text
reflection_result_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
scope VARCHAR(16) NOT NULL
step_run_id UUID NULL
decision VARCHAR(32) NOT NULL
reason TEXT NOT NULL
failure_bucket VARCHAR(64) NULL
unsupported_claim_refs_json JSONB NOT NULL
missing_evidence_json JSONB NOT NULL
violated_constraints_json JSONB NOT NULL
suggested_actions_json JSONB NOT NULL
confidence NUMERIC(5, 4) NULL
critic_model_call_ref TEXT NULL
decision_guard_json JSONB NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

## 24.22 agent_failures

Append-only：

```text
failure_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NULL
action_run_id UUID NULL
category VARCHAR(32) NOT NULL
code VARCHAR(64) NOT NULL
retryable BOOLEAN NOT NULL
replan_recommended BOOLEAN NOT NULL
user_visible BOOLEAN NOT NULL
message TEXT NOT NULL
details_ref TEXT NULL
source_module TEXT NOT NULL
source_ref TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

索引：

```text
(run_id, created_at)
(workspace_id, category, code, created_at DESC)
```

## 24.23 agent_interrupts

```text
interrupt_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NULL
action_run_id UUID NULL
kind VARCHAR(32) NOT NULL
status VARCHAR(16) NOT NULL
request_payload_json JSONB NOT NULL
response_schema_json JSONB NOT NULL
response_payload_json JSONB NULL
client_request_id TEXT NULL
created_at TIMESTAMPTZ NOT NULL
resolved_at TIMESTAMPTZ NULL
expires_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0

UNIQUE(run_id) WHERE status = 'pending'
UNIQUE(workspace_id, client_request_id) WHERE client_request_id IS NOT NULL
```

## 24.24 agent_external_job_handles

```text
external_job_handle_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NULL
action_run_id UUID NULL
owner_module VARCHAR(32) NOT NULL
external_job_id TEXT NOT NULL
job_kind VARCHAR(32) NOT NULL
status VARCHAR(24) NOT NULL
result_ref TEXT NULL
failure_id UUID NULL
submitted_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0

UNIQUE(owner_module, external_job_id)
```

## 24.25 Grounded Answer Tables

`agent_grounded_answers`：

```text
grounded_answer_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
answer_ref TEXT NOT NULL
answer_policy_snapshot_id UUID NOT NULL
status VARCHAR(24) NOT NULL
claim_count INTEGER NOT NULL
supported_claim_count INTEGER NOT NULL
unsupported_claim_count INTEGER NOT NULL
citation_count INTEGER NOT NULL
evidence_coverage NUMERIC(5, 4) NOT NULL
created_at TIMESTAMPTZ NOT NULL
UNIQUE(run_id)
```

`agent_claims`：

```text
claim_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
grounded_answer_id UUID NOT NULL
claim_order INTEGER NOT NULL
claim_text_ref TEXT NOT NULL
claim_summary TEXT NOT NULL
support_status VARCHAR(24) NOT NULL
created_at TIMESTAMPTZ NOT NULL
UNIQUE(grounded_answer_id, claim_order)
```

`agent_claim_evidence_bindings`：

```text
binding_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
claim_id UUID NOT NULL
evidence_id TEXT NOT NULL
citation_id TEXT NULL
source_span_ref TEXT NULL
binding_status VARCHAR(24) NOT NULL
binding_score NUMERIC(7, 6) NULL
created_at TIMESTAMPTZ NOT NULL
UNIQUE(claim_id, evidence_id)
```

## 24.26 agent_run_outcomes

```text
outcome_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
status VARCHAR(24) NOT NULL
completion_scope VARCHAR(24) NOT NULL
completed_goal_ids_json JSONB NOT NULL
incomplete_goal_ids_json JSONB NOT NULL
answer_ref TEXT NULL
artifact_refs_json JSONB NOT NULL
evidence_verdict_ref TEXT NULL
failure_id UUID NULL
user_visible_summary TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL

UNIQUE(run_id)
```

## 24.27 agent_runtime_events

Append-only：

```text
event_id UUID PRIMARY KEY
sequence_no BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
trace_id TEXT NOT NULL
event_type VARCHAR(64) NOT NULL
aggregate_type VARCHAR(32) NOT NULL
aggregate_id TEXT NOT NULL
payload_json JSONB NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

索引：

```sql
CREATE INDEX ix_agent_runtime_events_run_sequence
    ON agent_runtime.agent_runtime_events (run_id, sequence_no);

CREATE INDEX ix_agent_runtime_events_workspace_type_time
    ON agent_runtime.agent_runtime_events
       (workspace_id, event_type, created_at DESC);
```

## 24.28 agent_outbox_events

```text
event_id UUID PK
aggregate_type VARCHAR(32) NOT NULL
aggregate_id TEXT NOT NULL
workspace_id TEXT NOT NULL
run_id UUID NULL
topic TEXT NOT NULL
payload_json JSONB NOT NULL
headers_json JSONB NOT NULL
created_at TIMESTAMPTZ NOT NULL
available_at TIMESTAMPTZ NOT NULL
published_at TIMESTAMPTZ NULL
attempt_count INTEGER NOT NULL DEFAULT 0
last_error TEXT NULL
lock_version INTEGER NOT NULL DEFAULT 0
```

索引：

```sql
CREATE INDEX ix_agent_outbox_unpublished
    ON agent_runtime.agent_outbox_events (available_at, created_at)
    WHERE published_at IS NULL;
```

---

# 25. 外键与删除策略

- 所有 Core 自有 UUID 关系使用 Foreign Key；
- 跨模块 Ref 使用 TEXT，不建立跨模块数据库 FK；
- `agent_runs`、Plan、Step、Action、Observation、Outcome 等审计链使用 `ON DELETE RESTRICT`；
- 不允许通过删除 Run 级联删除审计事实；
- 产品删除使用：

```text
archive
revoke
retention expiry
approved physical purge
```

- 物理清理必须产生 Audit Event。

为避免循环 FK，`agent_runs.active_plan_id`、`active_plan_version_id`、`pending_interrupt_id`、`outcome_id`、`latest_failure_id` 在基础表创建后通过后续 Alembic Revision 添加 FK。

---

# 26. 并发控制与关键 SQL

## 26.1 乐观锁

所有可更新聚合使用：

```sql
UPDATE ...
SET status = :status,
    lock_version = lock_version + 1,
    updated_at = now()
WHERE id = :id
  AND lock_version = :expected_lock_version;
```

`rowcount != 1` 返回 `OPTIMISTIC_LOCK_CONFLICT`。

## 26.2 Scheduler 事务锁

调度开始时：

```text
SELECT agent_run FOR UPDATE
SELECT agent_plan FOR UPDATE
验证 ACTIVE PlanVersion
```

Ready Step 查询使用 `NOT EXISTS` 验证依赖，不通过可变 `step.status` 判断。

示意：

```sql
SELECT s.step_definition_id
FROM agent_runtime.agent_plan_steps s
WHERE s.plan_version_id = :active_plan_version_id
  AND s.execution_disposition = 'execute'
  AND NOT EXISTS (
      SELECT 1
      FROM agent_runtime.agent_step_runs sr
      WHERE sr.step_definition_id = s.step_definition_id
        AND sr.status = 'completed'
  )
  AND NOT EXISTS (
      SELECT 1
      FROM agent_runtime.agent_plan_step_dependencies d
      WHERE d.step_definition_id = s.step_definition_id
        AND d.dependency_type = 'hard'
        AND NOT EXISTS (
            SELECT 1
            FROM agent_runtime.agent_step_runs dep_run
            WHERE dep_run.step_definition_id = d.requires_step_definition_id
              AND dep_run.status = 'completed'
        )
  )
ORDER BY s.priority ASC, s.sequence_no ASC;
```

多 API Replica 抢占 Outbox、Lease Reconcile 或后台任务时使用 `FOR UPDATE SKIP LOCKED`。同一个 AgentRun 的 LangGraph 主控制流仍通过 `thread_id = run_id` 和 Run 行锁保证单控制器语义。

## 26.3 Resource Lock

第一版事务内：

```sql
SELECT pg_advisory_xact_lock(hashtextextended(:resource_key, 0));
```

然后查询未过期冲突 Lease。不能依赖应用内 Python Lock。

---

# 27. 事务边界

## 27.1 创建 Run

```text
BEGIN
幂等检查 workspace_id + client_request_id
创建 agent_runs
写 RUN_CREATED RuntimeEvent
写 Outbox
COMMIT
```

## 27.2 创建和激活 Plan

模型 Planner、Validator、Repair 在事务外执行。

```text
BEGIN
锁定 Run
创建 Plan
创建 PlanVersion
创建 PlanStepDefinition
创建 Dependency
创建 AcceptanceCriterion
PlanVersion → ACTIVE
Plan.current_version_id 更新
Run.active_plan_id / version_id 更新
写 RuntimeEvent / Outbox
COMMIT
```

## 27.3 创建 Dispatch

```text
BEGIN
锁定 Run 和 Plan
计算 Ready Step
选择最大安全集合
创建 DispatchGroup / DispatchItem
创建 StepRun
预留 Budget
获取 ResourceLease
写 RuntimeEvent
COMMIT

COMMIT 后执行 LangGraph Send
```

## 27.4 外部 Action

```text
事务 A：创建 ActionRun(PROPOSED / EXECUTING) → COMMIT
事务外：调用 Model / Knowledge / Tool / Ingestion
事务 B：写 Observation、更新 ActionRun、结算 Budget、写 Event → COMMIT
```

不得在数据库事务中等待模型或 Tool。

## 27.5 应用 PlanPatch

```text
BEGIN
锁定 Plan
验证 base_version == current_version
验证 ReplanBarrier satisfied
创建 PlanVersion N+1
复制 / 修改 Step Snapshot
旧版本 → SUPERSEDED
新版本 → ACTIVE
Patch → APPLIED
更新 Plan.current_version_id
写 RuntimeEvent / Outbox
COMMIT
```

## 27.6 Resume

```text
BEGIN
锁定 Interrupt
验证 workspace / user / client_request_id
写 response
Interrupt → RESOLVED
Run → RUNNING
写 RuntimeEvent
COMMIT

使用相同 thread_id 执行 Command(resume=...)
```

---

# 28. LangGraph PostgreSQL Checkpointer

- 使用锁定版本的 `AsyncPostgresSaver`；
- `thread_id = run_id`；
- Step 子图通过稳定 namespace 或 subgraph checkpoint 语义隔离；
- 应用启动时在 lifespan 中初始化 Checkpointer；
- 首次部署运行 `setup()`；
- Checkpointer 数据不是 Agent Domain 事实源；
- Checkpoint 写失败时，不执行下一副作用 Action，Run 标记 BLOCKED；
- Checkpoint 序列化必须使用受限类型，不允许任意对象反序列化；
- Checkpointer 升级必须锁定 `langgraph-checkpoint-postgres` 版本并执行兼容测试。

---

# 29. Alembic 目录与命名

建议：

```text
src/backend/zuno/infrastructure/database/
├── base.py
├── naming.py
├── session.py
└── migrations/
    ├── env.py
    ├── script.py.mako
    └── versions/
```

命名约定：

```python
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
```

Alembic `target_metadata` 必须只包含正式 ORM metadata，不从测试替身动态导入模型。

---

# 30. Alembic Migration 计划

每个 Revision 只完成一个稳定边界，禁止创建一个几千行不可回滚的大迁移。

## Revision ACR-001：Schema Foundation

```text
create schema agent_runtime
create schema langgraph_checkpoint
create naming convention baseline
create required extension only if deployment policy approves
```

应用生成 UUID，不强制依赖 `gen_random_uuid()`。

## Revision ACR-002：Run and Policy Snapshots

```text
agent_runs
agent_runtime_policy_snapshots
agent_answer_policy_snapshots
agent_execution_context_snapshots
agent_knowledge_snapshot_refs
基础索引和 CHECK
```

先不添加 `agent_runs` 到后续表的循环 FK。

## Revision ACR-003：Plan Definition

```text
agent_plans
agent_plan_versions
agent_plan_steps
agent_plan_step_dependencies
agent_step_acceptance_criteria
partial unique active version index
```

## Revision ACR-004：Scheduling Runtime

```text
agent_dispatch_groups
agent_step_runs
agent_dispatch_items
agent_resource_leases
agent_budget_reservations
```

创建顺序需避免 DispatchItem 与 StepRun 循环 FK；先建表，再在 revision 尾部添加一侧 FK。

## Revision ACR-005：Action and Evaluation Facts

```text
agent_failures
agent_action_runs
agent_observations
agent_acceptance_results
agent_reflection_results
```

Observation、Acceptance、Reflection、Failure 定义为 append-only Repository。

## Revision ACR-006：Replan

```text
agent_plan_patches
agent_plan_patch_operations
agent_replan_barriers
补充 PlanVersion.source_patch_id FK
```

## Revision ACR-007：Interrupt and External Job

```text
agent_interrupts
agent_external_job_handles
pending interrupt partial unique index
```

## Revision ACR-008：Grounded Answer and Outcome

```text
agent_grounded_answers
agent_claims
agent_claim_evidence_bindings
agent_run_outcomes
```

## Revision ACR-009：Events and Outbox

```text
agent_runtime_events
agent_outbox_events
identity sequence
unpublished partial index
```

## Revision ACR-010：Deferred Foreign Keys

添加：

```text
agent_runs.execution_snapshot_id
agent_runs.active_plan_id
agent_runs.active_plan_version_id
agent_runs.pending_interrupt_id
agent_runs.outcome_id
agent_runs.latest_failure_id
agent_plans.current_version_id
agent_plan_versions.source_patch_id
agent_plan_steps.satisfied_by_step_run_id
agent_action_runs.observation_id
```

所有 FK 使用明确名称和 `ON DELETE RESTRICT`。

## Revision ACR-011：Optional RLS Foundation

P1 后开启，不作为第一轮 Blocker：

```text
enable row level security
workspace_id session setting policy
service role bypass policy
migration / admin role policy
```

在启用前必须有 Connection Pool reset 测试，防止 Workspace session setting 泄漏。

---

# 31. Migration 编写规则

## 31.1 Expand / Contract

生产迁移遵循：

```text
先添加 nullable / 新表
发布兼容代码
后台 backfill
验证完整性
再添加 NOT NULL / 删除旧路径
```

不得在一个 Release 同时新增新字段并删除旧字段。

## 31.2 大表索引

已有大表新增索引使用：

```text
CREATE INDEX CONCURRENTLY
```

Alembic 使用 `autocommit_block()`。初始空库创建可使用普通索引。

## 31.3 Backfill

- Alembic 负责 Schema；
- 大规模业务数据迁移使用可恢复的独立 Backfill Job；
- Backfill 保存 cursor、processed_count、failure_count；
- Backfill 必须可重入；
- 完成后运行 verification query，再收紧约束。

## 31.4 Downgrade

生产环境默认不依赖破坏性 downgrade。回滚策略：

```text
回滚应用版本
保留向前兼容 Schema
修复后继续 forward migration
```

仅对尚未写入生产事实的新表允许安全 downgrade。

## 31.5 SQLite 到 PostgreSQL

SQLite 数据迁移不是 Alembic `upgrade()` 的职责。

使用独立 Migration Program：

```text
冻结旧 Store 写入或开启 dual-write
导出 SQLite Snapshot
转换 UUID / 时间 / JSON
导入 PostgreSQL staging
校验 counts / hashes / relationships
切换 read path
观察期
关闭旧写入
归档 SQLite
```

不得声称一个 Alembic revision 能直接完成跨数据库在线迁移。

---

# 32. SQLAlchemy Repository 规则

- 所有 Repository 接收 AsyncSession；
- Repository 不自行 commit；
- UnitOfWork 统一 commit / rollback；
- Domain Mapper 与 ORM 分离；
- 更新必须携带 `lock_version`；
- 所有查询强制 `workspace_id`；
- 跨 Workspace 未命中返回 NotFound，不泄露对象存在；
- append-only 表不提供 update API；
- JSONB 只保存不可拆的小型 Contract，不保存可高频过滤的状态字段；
- 查询热点字段必须是独立列。

---

# 33. Composition Root

生产组装：

```python
@dataclass(frozen=True)
class RuntimePorts:
    model_gateway: ModelGatewayPort
    knowledge: KnowledgeQueryPort
    ingestion: IngestionPort
    memory: MemoryPort
    capability_catalog: CapabilityCatalogPort
    tool_runtime: ToolRuntimePort
    security: SecurityPort
    artifact_store: ArtifactStorePort
    trace_sink: TraceSinkPort
    clock: ClockPort
    id_generator: IdGeneratorPort

@dataclass(frozen=True)
class RuntimeServices:
    run: RunService
    snapshot: ExecutionSnapshotService
    planning: PlanningService
    scheduling: SchedulingService
    step_execution: StepExecutionService
    reflection: ReflectionService
    replan: ReplanService
    finalization: FinalizationService
    interrupt: InterruptService
    recovery: RecoveryService
    cancellation: CancellationService
```

生产环境缺少必需 Port 时应用启动失败。测试使用 Fake Port。

---

# 34. Runtime Facade

Product/API 只调用：

```python
class AgentRuntimeService:
    async def start(self, command: StartAgentRunCommand) -> StartAgentRunResult: ...
    async def resume(self, command: ResumeAgentRunCommand) -> StartAgentRunResult: ...
    async def cancel(self, command: CancelAgentRunCommand) -> None: ...
    async def get_snapshot(self, run_id: UUID, workspace_id: str) -> AgentRunSnapshot: ...
    async def stream(self, run_id: UUID, workspace_id: str) -> AsyncIterator[RuntimeEnvelope]: ...
```

FastAPI Endpoint 不直接调用 Planner、Repository 或 Graph Node。

---

# 35. RuntimeEvent 与 Trace 分离

Domain Event：

```text
RUN_CREATED
EXECUTION_SNAPSHOT_RESOLVED
PLAN_ACTIVATED
DISPATCH_CREATED
STEP_STARTED
STEP_COMPLETED
STEP_FAILED
REPLAN_REQUESTED
PLAN_VERSION_ACTIVATED
INTERRUPT_CREATED
RUN_FINALIZED
```

Trace Span：

```text
node_start / node_end
model_call
retrieval_round
fusion_stage
tool_call
acceptance_check
routing_decision
```

Domain Event 保存 PostgreSQL 事实；高频 Trace 写 Local Trace Store，并可脱敏发送 LangSmith-compatible sink。

---

# 36. 测试规格

## 36.1 Domain Unit

```text
AgentRun transition
StepRun transition
Action UNKNOWN outcome
PlanVersion immutability
PlanPatch stale detection
JoinPolicy
ResourceLease conflict
Budget settlement
ReflectionDecisionGuard
```

## 36.2 PostgreSQL Integration

```text
Plan activation atomicity
one ACTIVE PlanVersion partial unique constraint
Dispatch creation transaction
Action idempotency
Interrupt response idempotency
Optimistic lock conflict
Outbox publication claim
Resource advisory lock
Workspace isolation
```

## 36.3 LangGraph Integration

```text
single-step deterministic plan
parallel Send fan-out
fan-in reducer idempotency
parallel branch failure
parallel interrupt
resume exact node
step subgraph checkpoint
replan barrier
```

## 36.4 Fault Injection

```text
进程在 Tool 成功后、Observation 写入前崩溃
进程在 DispatchGroup 创建事务中崩溃
进程在 PlanPatch 应用事务中崩溃
Checkpoint 写失败
Worker Lease 过期
RabbitMQ Outbox 重复投递
Security Epoch 在 Run 中变化
```

## 36.5 E2E

```text
简单问答创建单步骤 Plan
复杂研究任务真实并行
检索不足触发 Replan
附件解析等待并 Resume
审批后副作用 exactly-once
Partial RunOutcome
Abstain on insufficient evidence
Cancellation propagation
```

---

# 37. Current Baseline

当前仓库已有：

```text
LangGraph StateGraph 主图骨架
SQLiteAgentRunStore
Strategy / Plan-and-Execute baseline
单次 ReAct step executor baseline
Reflection / Replan / Grounded Synthesis baseline
Tool approval / resume / idempotency baseline
Corrective retrieval / EvidenceLedger baseline
Memory pre/post commit 和 Reflexion Candidate baseline
Completion / Workspace task API baseline
```

当前仍不等于 Target 完成：

```text
SQLite 不是目标 PostgreSQL Runtime Store
AgentRunStore 尚未拆成 Repository + UnitOfWork
Protocol 仍存在 Any / optional dependency
PlanStepDefinition 与 StepRun 尚未完全分离
ReAct 尚不是完整多轮 StepGraph
Replan 尚未使用不可变 PlanVersion + PlanPatch
并行 DispatchGroup 尚未作为真实领域事实
Resume 尚未完全使用 PostgreSQL Checkpointer 原生游标语义
P0 benchmark 仍需 measured proof
```

---

# 38. Migration Program

## Phase 1：Contract Package 与 Typed Port

```text
拆分 contracts.py
保留 compatibility exports
替换 Any Protocol
为现有 Model / Knowledge / Tool 编写 Adapter
```

## Phase 2：Domain 与 Repository

```text
建立 Domain 状态机
拆分 AgentRunStore
实现 UnitOfWork
保留 LegacyAgentRunStoreAdapter
```

## Phase 3：PostgreSQL Schema

按 ACR-001 至 ACR-010 建表，先完成 Run、Plan、Step、Action、Observation 和 Event 主链。

## Phase 4：Graph State V2

```text
最小 State
ExecutionContextSnapshot
所有任务创建 Plan
消除 direct_answer 旁路
```

## Phase 5：真实 StepExecutionGraph

```text
ActionDecision
ActionRun
Observation
Acceptance
Step Reflection
多轮 ReAct
```

## Phase 6：Parallel Scheduler

```text
DispatchGroup
DispatchItem
BudgetReservation
ResourceLease
Send fan-out
JoinResult
```

## Phase 7：PlanVersion Replan

```text
PlanPatch
ReplanBarrier
new immutable PlanVersion
completed output reuse
```

## Phase 8：PostgreSQL Checkpointer

```text
AsyncPostgresSaver
Interrupt / Command(resume)
restart recovery
unknown side-effect reconciliation
```

## Phase 9：Outcome、Cancellation 与 AnswerPolicy

```text
PARTIAL / ABSTAINED / BLOCKED
Cancellation propagation
Deadline
Grounded Answer tables
```

## Phase 10：Cutover 与旧路径清理

```text
dual-run / shadow verification
SQLite export and PostgreSQL import
Product read cutover
legacy adapter removal
architecture Current update
```

---

# 39. Completion Evidence

Agent Core V2 只有在以下证据真实存在时才能标记 completed：

```text
真实 compiled LangGraph RunGraph + StepGraph
PostgreSQL Agent Runtime Store
AsyncPostgresSaver restart recovery
所有简单任务创建 Plan
至少两个独立 Step 真实并行
DispatchGroup 在重启后恢复
Step 内真实多轮 ReAct
Acceptance 改变路由
Replan 创建新 PlanVersion
已完成 Step 跨版本复用
KnowledgeSnapshot 固定
Ingestion Wait Interrupt / Resume
Approval 后副作用不重复
AnswerPolicy 阻止无证据回答
RunOutcome 返回 PARTIAL / ABSTAINED
Cancellation 传播到并行分支
Trace 关联 Run、Plan、Dispatch、Step、Action、Evidence、Outcome
PostgreSQL migration upgrade test
Schema verification test
fixed benchmark 不低于 release gate
```

禁止仅凭以下内容宣称完成：

```text
类或表存在
Docker Compose 声明 PostgreSQL
Mock Test 通过
SQLite 行为近似
架构文档写了 Target
只跑通 happy path
```

---

# 40. 最终冻结结论

Agent Core V2 的最终实现模型是：

```text
LangGraph Single Controller
+ ExecutionContextSnapshot
+ Plan DAG
+ 默认安全并行
+ Step ReAct Subgraph
+ Acceptance / Reflection
+ PlanPatch / Immutable PlanVersion
+ KnowledgeSnapshot / AnswerPolicy
+ Interrupt / Resume / Replay
+ Cancellation / Deadline
+ PostgreSQL Domain Facts
+ LangGraph PostgreSQL Checkpointer
+ RuntimeEvent / Trace / Outbox
+ Precise RunOutcome
```

该设计面向通用企业知识助手和复杂任务执行，不绑定合同分析、代码修复或研究报告等单一场景；领域差异由 Skill、Capability、Knowledge 和 Tool 模块提供，Agent Core 只负责统一规划与控制。