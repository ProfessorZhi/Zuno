# 06 Agent Core / Planning & Control

updated: 2026-07-12  
status: normative-target-module-design  
module_number: 06  
formal_path: `docs/modules/06-agent-core-planning-control.md`  
agent_mirror: `.agent/modules/06-agent-core-planning-control.md`

> 本文是 Zuno 第 06 个逻辑模块——Agent Core / Planning & Control——的正式实施级设计文档。
>
> 本文描述 **Target**，不是 Current。当前完成度、Gap、Blocked 和 Measurement 仍以 `docs/architecture/production-readiness.md` 为事实源。

---

# 1. 模块定位

Agent Core 是 Zuno 唯一的在线任务控制器。它基于 LangGraph，把用户目标转换成可规划、可并行、可恢复、可审计、受预算和安全约束的执行过程。

一句话定义：

> Agent Core 是领域无关的 Single Controller Runtime，通过 Plan DAG、动态 fan-out/fan-in、Step 内 ReAct、Reflection、Replan 和 Reflexion，统一协调 Model、Knowledge、Memory、Capability、Tool、Input 与 Security。

Agent Core 面向：

```text
企业知识库问答
复杂研究与报告
多文档分析
代码理解、修改、测试与修复
数据分析和产物生成
外部工具与企业流程
需要审批、等待和恢复的长任务
```

它不绑定合同分析或任何单一业务场景。领域差异由 Skill、Capability、Knowledge 与 Tool 模块提供。

---

# 2. Owner 边界

## 2.1 Agent Core 负责

```text
Runtime Request 校验
ExecutionContextSnapshot
Task Analysis
Complexity Classification
RuntimePolicy / AnswerPolicy 解析
Plan DAG 创建、验证、激活和版本化
默认最大化安全并行
Step 内 ReAct 控制循环
Action 校验与分发
Observation 归一化
Acceptance Evaluation
Step Reflection / Final Reflection
PlanPatch / Replan
Interrupt / Resume
Cancellation / Deadline
RunOutcome
Reflexion Candidate Bridge
RuntimeEvent / Trace 关联
```

## 2.2 Agent Core 不负责

```text
直接解析 PDF、DOCX、PPTX、XLSX 或图片
直接操作 Milvus、Neo4j、BM25
直接调用具体模型厂商 SDK
直接执行 Shell、浏览器、邮件或第三方 API
直接写入长期 Memory
直接决定用户是否有权访问某份知识
直接实现领域业务规则
直接保存大型文件、完整日志或检索 Payload
```

## 2.3 跨模块协作

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

所有跨模块调用必须使用 typed Port 与 Contract。

---

# 3. 核心架构原则

## 3.1 LangGraph 是控制流引擎

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

Graph State 只保存 ID、Ref 和小型路由结果，不复制完整领域对象。

## 3.2 Single Controller

Zuno 默认只有一个产品级 Controller。复杂任务通过 Plan DAG、并行调度、ReAct 和 Replan 完成，不默认建设产品级 Multi-Agent Runtime。

## 3.3 五种 Agent 机制是嵌套关系

```text
Plan-and-Execute
    管理整个任务

ReAct
    管理单个 PlanStep 内部的动作循环

Reflection
    判断 Step 或最终结果是否达标

Replan
    修改剩余计划并创建新 PlanVersion

Reflexion
    提交跨任务经验候选给 Memory Governance
```

## 3.4 所有任务都有 Plan

简单问题也必须创建 Deterministic Single-Step Plan，不能通过 `direct_answer` 绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。

## 3.5 Plan 是 DAG

Plan 的真实顺序由：

```text
Dependencies
JoinPolicy
Resource Constraints
Concurrency Policy
Security Policy
```

决定。`sequence_no` 只用于 UI 稳定排序。

## 3.6 默认最大化安全并行

无依赖、无资源冲突、无高风险副作用、预算和配额允许的 Ready Step 默认并行。

只有以下情况退化为串行：

```text
存在数据依赖
共享可变资源
不可逆副作用
Provider / Workspace 并发限制
预算不足
Security 要求互斥
Replan / Finalize 控制操作
```

## 3.7 模型只产生提案

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
绕过权限
修改已完成 Step
提交长期 Memory
```

## 3.8 不保存隐藏思维链

系统只保存：

```text
决策摘要
选择的 Action
预期 Observation
失败事实
验收结果
可复用经验
```

---

# 4. Requirement IDs

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
ARCH-AGENT-024  并行 Replan 必须经过 Replan Barrier。
ARCH-AGENT-025  PostgreSQL 是 Agent Runtime 结构化事实源；LangGraph Checkpointer 只保存图控制状态。
ARCH-AGENT-026  所有跨模块 Port 必须使用明确输入输出类型。
ARCH-AGENT-027  外部执行必须明确成功、失败或 UNKNOWN。
ARCH-AGENT-028  领域写入与跨模块事件发布必须使用事务 + Outbox。
```

---

# 5. 代码分层

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

依赖规则：

```text
Graph Node 不直接写 SQL
Domain 不导入 LangGraph
Application 不导入 FastAPI
Port 不返回 Any
ORM Row 不直接作为 Graph State
外部 API 调用不放在数据库事务内
```

## 5.1 目标目录

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
    ├── graph/
    │   ├── run/{state.py,nodes.py,routing.py,builder.py}
    │   └── step/{state.py,nodes.py,routing.py,builder.py}
    ├── planning/
    │   ├── analyzer.py
    │   ├── complexity.py
    │   ├── policy_resolver.py
    │   ├── router.py
    │   ├── normalizer.py
    │   ├── validator.py
    │   ├── repair.py
    │   └── planners/{deterministic.py,skill.py,model.py}
    ├── scheduling/
    │   ├── readiness.py
    │   ├── selector.py
    │   ├── join.py
    │   ├── concurrency.py
    │   ├── resource_leases.py
    │   └── budget_reservations.py
    ├── execution/
    │   ├── action_decider.py
    │   ├── action_validator.py
    │   ├── executor_registry.py
    │   └── executors/{model.py,retrieval.py,tool.py,ingestion.py,interaction.py}
    ├── reflection/
    │   ├── acceptance.py
    │   ├── deterministic.py
    │   ├── critic.py
    │   └── decision_guard.py
    ├── replan/
    │   ├── context.py
    │   ├── generator.py
    │   ├── validator.py
    │   ├── barrier.py
    │   └── applier.py
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
    └── persistence/
        ├── unit_of_work.py
        ├── repositories.py
        └── postgres/{base.py,models.py,mappings.py,repositories.py,unit_of_work.py}
```

迁移期间通过 `zuno.agent.contracts.__init__` 保持旧 Import 兼容。

---

# 6. Contract、Domain 与 ORM

## 6.1 Contract Model

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

## 6.2 Domain Model

Domain 负责状态转移：

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

## 6.3 ORM Model

ORM 只负责数据库映射，由 Mapper 转换为 Domain，不在 Graph、API 或 Port 中直接暴露。

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

---

# 8. Graph State

Run State：

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

Step State：

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

禁止放入 State：完整 Plan、完整 ContextPack、完整检索结果、模型 Prompt、工具日志和文件正文。

---

# 9. Runtime 状态机

## 9.1 AgentRun

```text
CREATED → RUNNING ↔ WAITING
RUNNING / WAITING → CANCELLING → CANCELLED
RUNNING / WAITING → COMPLETED | PARTIAL | ABSTAINED | REFUSED | BLOCKED | FAILED
```

Phase：

```text
INITIALIZING
RESOLVING_CONTEXT
PLANNING
EXECUTING
REPLANNING
FINALIZING
TERMINAL
```

## 9.2 PlanVersion

```text
DRAFT → VALIDATING → ACTIVE → SUPERSEDED
DRAFT / VALIDATING → REJECTED
```

## 9.3 StepRun

```text
QUEUED → RUNNING ↔ WAITING
RUNNING → COMPLETED | FAILED | BLOCKED | CANCELLED
```

重试创建新 attempt，不复活失败 StepRun。

## 9.4 ActionRun

```text
PROPOSED → VALIDATED → WAITING_APPROVAL → EXECUTING
EXECUTING → SUCCEEDED | FAILED | UNKNOWN | CANCELLED
```

UNKNOWN 必须 Reconcile 或人工确认。

---

# 10. ExecutionContextSnapshot

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

原则：

```text
初始正向权限范围固定
实时撤销永远优先
```

显式刷新知识或策略时创建新 Snapshot Version，不能原地覆盖。

---

# 11. RuntimePolicy 与 AnswerPolicy

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

AnswerPolicy 决定什么时候允许回答：

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

企业知识问答默认：strict grounding、禁止 model prior、必须 Citation 与 SourceSpan、证据不足时 Abstain。

---

# 12. Planner Pipeline

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

Validator：

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

PlanRepair 最多两轮；仍失败时使用 Safe Minimal Plan、Ask User 或 Abstain。

---

# 13. Plan Domain

## 13.1 Plan

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

## 13.2 PlanVersion

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

## 13.3 PlanStepDefinition

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

# 14. 默认并行 Scheduler

Ready 条件：

```text
属于 ACTIVE PlanVersion
execution_disposition = EXECUTE
所有 HARD Dependency 已满足
不存在成功 StepRun
不存在有效运行 Lease
Capability 可用
预算可预留
资源锁可获取
Security Gate 允许
Deadline 未到期
Run 未取消
```

Scheduler 输出最大安全集合，而非所有 Ready Step。

## 14.1 DispatchGroup

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

JoinPolicy：

```text
ALL_SUCCESS
ALL_TERMINAL
ANY_SUCCESS
QUORUM
BEST_EFFORT
```

BranchFailurePolicy：

```text
CONTINUE_SIBLINGS
CANCEL_SIBLINGS
FAIL_FAST
JOIN_THEN_REPLAN
JOIN_THEN_REFLECT
```

DispatchGroup、DispatchItem、StepRun、BudgetReservation 和 ResourceLease 在同一事务中创建，提交后才能 LangGraph `Send`。

---

# 15. ResourceLease 与 BudgetReservation

ResourceRequirement：

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

BudgetReservation 预留：Token、Cost、Model Call、Tool Call、Retrieval Round、Deadline。完成后按真实消耗结算。

---

# 16. ReAct Action Runtime

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

ActionDecision：

```python
class ActionDecision(BaseModel):
    action_kind: ActionKind
    capability_id: str | None
    arguments_ref: str | None
    decision_summary: str
    expected_observation: str
    completion_claimed: bool
```

执行前经过：Schema、Capability、Security、Budget、Approval、Replay、Resource Lease Validation。

Action 幂等键：

```text
sha256(run_id + step_run_id + action_round + decision_hash)
```

Core 幂等不替代 Tool Runtime 幂等。

---

# 17. Observation、Acceptance 与 Reflection

Observation 只保存摘要和 Ref，大型 Payload 进 Object Store。

AcceptanceCriterion：

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

Step Reflection：

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

模型 Critic 的提案必须通过 ReflectionDecisionGuard。

---

# 18. Replan 与 PlanVersion

```text
Reflection.REPLAN
→ ReplanRequest
→ ReplanBarrier
→ 等待或取消不再安全的并行分支
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

Patch 必须满足：

```text
patch.base_version_id == plan.current_version_id
```

已完成 Step 通过 `REUSE_COMPLETED + satisfied_by_step_run_id` 复用。

---

# 19. Knowledge 与 Ingestion 协作

每次知识查询必须携带：

```text
workspace_id
authorization_context_ref
security_epoch
knowledge_snapshot_ref
```

Knowledge Failure：

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

Ingestion Wait：

```text
SUBMIT_INGESTION
→ ExternalJobHandle
→ WAIT_EXTERNAL
→ interrupt
→ DocumentReady / KnowledgeVersionReady
→ resume
```

Core 不直接调用 Parser。

---

# 20. Interrupt、Replay 与 Cancellation

Interrupt 节点必须幂等；不可逆副作用必须放在 Interrupt 后的独立节点。

ReplayMode：

```text
PURE
READ_ONLY_SNAPSHOT
IDEMPOTENT_WRITE
COMPENSATABLE_WRITE
NON_REPLAYABLE
```

Cancellation：

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

---

# 21. Port 与 Runtime Facade

生产 Port 必须强类型：

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

Product/API 只调用：

```python
class AgentRuntimeService:
    async def start(self, command: StartAgentRunCommand) -> StartAgentRunResult: ...
    async def resume(self, command: ResumeAgentRunCommand) -> StartAgentRunResult: ...
    async def cancel(self, command: CancelAgentRunCommand) -> None: ...
    async def get_snapshot(self, run_id: UUID, workspace_id: str) -> AgentRunSnapshot: ...
    async def stream(self, run_id: UUID, workspace_id: str) -> AsyncIterator[RuntimeEnvelope]: ...
```

---

# 22. Repository 与 UnitOfWork

Repository：

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

Repository 不自行 commit；UnitOfWork 统一 commit / rollback。Append-only 表不提供 update API。

---

# 23. PostgreSQL Schema

```text
agent_runtime
    Agent Core 领域事实

langgraph_checkpoint
    LangGraph Checkpointer 表
```

类型约定：

```text
Core 自有 ID       UUID，应用生成
跨模块 ID / Ref    TEXT
时间               TIMESTAMPTZ
金额               NUMERIC(18,6)
Token              BIGINT
小型不可变配置     JSONB
大型 Payload       Object Store Ref
状态               VARCHAR + CHECK
```

所有高频表包含 `workspace_id`、`run_id`、`created_at`；可更新表增加 `updated_at` 与 `lock_version`。

---

# 24. PostgreSQL 表结构

## 24.1 Run 与 Snapshot

### agent_runs

关键字段：

```text
run_id UUID PK
workspace_id TEXT NOT NULL
task_id TEXT NOT NULL
thread_id TEXT NOT NULL
user_id TEXT NOT NULL
trace_id TEXT NOT NULL
client_request_id TEXT NOT NULL
goal_ref TEXT NOT NULL
goal_summary TEXT NOT NULL
status VARCHAR(32) NOT NULL
phase VARCHAR(32) NOT NULL
execution_snapshot_id UUID NULL
active_plan_id UUID NULL
active_plan_version_id UUID NULL
pending_interrupt_id UUID NULL
outcome_id UUID NULL
latest_failure_id UUID NULL
scheduler_round INTEGER NOT NULL DEFAULT 0
model_call_count INTEGER NOT NULL DEFAULT 0
tool_call_count INTEGER NOT NULL DEFAULT 0
retrieval_round_count INTEGER NOT NULL DEFAULT 0
input_tokens BIGINT NOT NULL DEFAULT 0
output_tokens BIGINT NOT NULL DEFAULT 0
cost_total NUMERIC(18,6) NOT NULL DEFAULT 0
deadline_at TIMESTAMPTZ NULL
cancel_requested_at TIMESTAMPTZ NULL
cancel_reason TEXT NULL
lock_version INTEGER NOT NULL DEFAULT 0
created_at / started_at / updated_at / finished_at
```

约束：

```text
UNIQUE(workspace_id, client_request_id)
CHECK status
CHECK phase
INDEX(workspace_id, status, updated_at DESC)
INDEX(thread_id, created_at DESC)
partial INDEX(deadline_at) for active runs
```

### agent_execution_context_snapshots

```text
snapshot_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
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

### agent_knowledge_snapshot_refs

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

### agent_runtime_policy_snapshots / agent_answer_policy_snapshots

```text
snapshot_id UUID PK
workspace_id TEXT NOT NULL
policy_version TEXT NOT NULL
policy_json JSONB NOT NULL
content_hash TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL
UNIQUE(workspace_id, content_hash)
```

## 24.2 Plan Definition

### agent_plans

```text
plan_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL UNIQUE
status VARCHAR(24) NOT NULL
current_version_id UUID NULL
version_count INTEGER NOT NULL DEFAULT 0
replan_count INTEGER NOT NULL DEFAULT 0
lock_version INTEGER NOT NULL DEFAULT 0
created_at / updated_at
```

### agent_plan_versions

```text
plan_version_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL
version_no INTEGER NOT NULL
base_version_id UUID NULL
source_patch_id UUID NULL
status VARCHAR(24) NOT NULL
planner_type VARCHAR(24) NOT NULL
planner_model_call_ref TEXT NULL
goal_summary TEXT NOT NULL
assumptions_json JSONB NOT NULL
planning_context_ref TEXT NULL
content_hash TEXT NOT NULL
activation_reason TEXT NULL
created_at / activated_at / superseded_at
UNIQUE(plan_id, version_no)
UNIQUE(plan_id, content_hash)
partial UNIQUE(plan_id) WHERE status='active'
```

### agent_plan_steps

```text
step_definition_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL
plan_version_id UUID NOT NULL
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

### agent_plan_step_dependencies

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
```

### agent_step_acceptance_criteria

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

## 24.3 Replan

```text
agent_plan_patches
agent_plan_patch_operations
agent_replan_barriers
```

关键约束：Patch 带 `base_version_id`；同一 Plan 只能有一个未完成 Barrier；Patch Operation 按 `operation_order` 唯一排序。

## 24.4 Parallel Scheduling

### agent_dispatch_groups

```text
dispatch_group_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_version_id UUID NOT NULL
scheduler_round INTEGER NOT NULL
join_policy VARCHAR(24) NOT NULL
branch_failure_policy VARCHAR(32) NOT NULL
quorum INTEGER NULL
expected / completed / succeeded / failed / cancelled counts
status VARCHAR(24) NOT NULL
decision_summary TEXT NOT NULL
created_at / dispatched_at / completed_at / updated_at
lock_version INTEGER NOT NULL DEFAULT 0
UNIQUE(run_id, scheduler_round)
```

### agent_dispatch_items

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
created_at / updated_at
UNIQUE(dispatch_group_id, branch_no)
UNIQUE(dispatch_group_id, step_definition_id)
UNIQUE(step_run_id)
```

### agent_step_runs

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
model/tool/retrieval counters
input/output tokens
cost_total NUMERIC(18,6)
started_at / finished_at / created_at / updated_at
lock_version INTEGER NOT NULL DEFAULT 0
UNIQUE(step_definition_id, attempt_no)
UNIQUE(idempotency_key)
```

### agent_resource_leases

```text
resource_lease_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
resource_key TEXT NOT NULL
access_mode VARCHAR(16) NOT NULL
status VARCHAR(16) NOT NULL
lease_token TEXT NOT NULL
acquired_at / expires_at / released_at / created_at
UNIQUE(step_run_id, resource_key)
UNIQUE(lease_token)
```

### agent_budget_reservations

```text
budget_reservation_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL UNIQUE
status VARCHAR(16) NOT NULL
reserved_* counters
used_* counters
created_at / settled_at / released_at / updated_at
lock_version INTEGER NOT NULL DEFAULT 0
```

## 24.5 Execution Facts

### agent_action_runs

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
model_call_ref / retrieval_run_ref / tool_execution_ref / ingestion_job_ref
approval_ref TEXT NULL
observation_id UUID NULL
failure_id UUID NULL
retry_of_action_run_id UUID NULL
usage counters
started_at / finished_at / created_at / updated_at
lock_version INTEGER NOT NULL DEFAULT 0
UNIQUE(step_run_id, action_round)
UNIQUE(idempotency_key)
```

### agent_observations

Append-only，一条 Action 对应一条归一化 Observation：

```text
observation_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
action_run_id UUID NOT NULL UNIQUE
kind / status / source_type
source_ref TEXT NULL
summary TEXT NOT NULL
payload_ref TEXT NULL
payload_preview_json JSONB NOT NULL
evidence_refs_json JSONB NOT NULL
citation_refs_json JSONB NOT NULL
failure_id UUID NULL
trace_span_ref TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

### agent_acceptance_results

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

### agent_reflection_results / agent_failures

Reflection 保存 scope、decision、reason、missing evidence、violated constraints、suggested actions、critic ref 和 deterministic guard 结果。Failure 保存 category、code、retryable、replan_recommended、user_visible、source module/ref。

## 24.6 Wait 与 External Job

```text
agent_interrupts
agent_external_job_handles
```

同一 Run 默认只有一个 PENDING Interrupt；Resume 使用 `workspace_id + client_request_id` 幂等。

## 24.7 Grounded Answer 与 Outcome

```text
agent_grounded_answers
agent_claims
agent_claim_evidence_bindings
agent_run_outcomes
```

RunOutcome 状态：

```text
COMPLETED
PARTIAL
ABSTAINED
REFUSED
BLOCKED
FAILED
CANCELLED
```

## 24.8 Event 与 Outbox

```text
agent_runtime_events
agent_outbox_events
```

RuntimeEvent 按 `run_id + sequence_no` 顺序读取；Outbox 通过 partial index 查询 `published_at IS NULL`。

---

# 25. 外键、删除与并发

- Core 自有 UUID 使用 FK；跨模块 Ref 使用 TEXT；
- 审计链使用 `ON DELETE RESTRICT`；
- 删除任务采用 archive / revoke / retention / approved purge；
- 可更新聚合使用 `lock_version` 乐观锁；
- Scheduler 开始时锁定 Run 与 Plan；
- Outbox/Reconciler 使用 `FOR UPDATE SKIP LOCKED`；
- Resource Lock 第一版使用 `pg_advisory_xact_lock(hashtextextended(resource_key, 0))`；
- Ready Step 通过 Dependency 与成功 StepRun 推导，不在 PlanStepDefinition 上维护可变 status。

---

# 26. 事务边界

## 创建 Run

```text
BEGIN
幂等检查
创建 Run
写 RuntimeEvent
写 Outbox
COMMIT
```

## 激活 Plan

Planner / Validator / Repair 在事务外；事务内写 Plan、Version、Step、Dependency、Acceptance，并原子激活。

## 创建 Dispatch

```text
BEGIN
锁定 Run / Plan
选择最大安全集合
创建 DispatchGroup / Item
创建 StepRun
预留 Budget
获取 ResourceLease
写 Event
COMMIT
COMMIT 后 LangGraph Send
```

## 外部 Action

```text
事务 A：创建 ActionRun
事务外：调用外部模块
事务 B：写 Observation、更新状态、结算预算
```

## 应用 PlanPatch

锁定 Plan，验证 base version 与 Barrier，创建新 Version，旧 Version supersede，新 Version activate，写 Event / Outbox。

## Resume

事务内幂等解决 Interrupt；事务外用相同 `thread_id` 执行 `Command(resume=...)`。

---

# 27. LangGraph PostgreSQL Checkpointer

- 使用锁定版本 `AsyncPostgresSaver`；
- `thread_id = run_id`；
- Step 子图使用稳定 namespace；
- lifespan 中初始化；
- 首次部署执行 `setup()`；
- Checkpointer 数据不替代 Domain Store；
- Checkpoint 写失败时不执行下一个副作用 Action；
- Checkpointer 升级必须做兼容和恢复测试。

---

# 28. Alembic Migration 规格

```text
ACR-001  Schema Foundation
ACR-002  Run and Policy Snapshots
ACR-003  Plan Definition
ACR-004  Scheduling Runtime
ACR-005  Action and Evaluation Facts
ACR-006  Replan
ACR-007  Interrupt and External Job
ACR-008  Grounded Answer and Outcome
ACR-009  Events and Outbox
ACR-010  Deferred Foreign Keys
ACR-011  Optional RLS Foundation
```

## 28.1 ACR-001

创建 `agent_runtime` 和 `langgraph_checkpoint` Schema；UUID 由应用生成。

## 28.2 ACR-002

创建 Run、RuntimePolicy、AnswerPolicy、ExecutionContextSnapshot、KnowledgeSnapshotRef。

## 28.3 ACR-003

创建 Plan、PlanVersion、PlanStep、Dependency、Acceptance，以及 one-active-version partial unique index。

## 28.4 ACR-004

创建 DispatchGroup、StepRun、DispatchItem、ResourceLease、BudgetReservation。

## 28.5 ACR-005

创建 Failure、ActionRun、Observation、AcceptanceResult、ReflectionResult。

## 28.6 ACR-006

创建 PlanPatch、PatchOperation、ReplanBarrier。

## 28.7 ACR-007

创建 Interrupt 与 ExternalJobHandle。

## 28.8 ACR-008

创建 GroundedAnswer、Claim、ClaimEvidenceBinding、RunOutcome。

## 28.9 ACR-009

创建 RuntimeEvent、OutboxEvent 和未发布事件 partial index。

## 28.10 ACR-010

添加循环依赖 FK：Run → Snapshot / Plan / Version / Interrupt / Outcome / Failure，Plan → CurrentVersion，Action → Observation。

## 28.11 ACR-011

P1 后启用 RLS；启用前必须验证连接池 session setting reset，防止 Workspace 泄漏。

---

# 29. Migration 规则

```text
Expand
发布兼容代码
可恢复 Backfill
验证
Contract
```

- 大表索引使用 `CREATE INDEX CONCURRENTLY`；
- Alembic 负责 Schema，大规模数据迁移使用独立 Backfill Job；
- 生产回滚以应用回滚 + Forward Fix 为主；
- SQLite → PostgreSQL 使用独立 Migration Program，不塞入 Alembic upgrade；
- 迁移校验包括 row count、hash、关系完整性、抽样回放和双读对比。

---

# 30. Current Baseline 与 Target Gap

当前已有：

```text
LangGraph StateGraph 主图骨架
SQLiteAgentRunStore
Strategy / Plan baseline
单次 ReAct executor baseline
Reflection / Replan / Grounded Synthesis baseline
Tool approval / resume / idempotency baseline
Corrective retrieval / EvidenceLedger baseline
Memory / Reflexion Candidate baseline
Completion / Workspace Task API baseline
```

仍未达到 Target：

```text
PostgreSQL Runtime Store
Repository + UnitOfWork
强类型 Port
PlanStepDefinition / StepRun / ActionRun 完整分离
多轮 StepExecutionGraph
真实 Parallel DispatchGroup
Immutable PlanVersion + PlanPatch
原生 PostgreSQL Checkpointer 恢复
AnswerPolicy / Partial / Abstain 完整闭环
固定 benchmark measured proof
```

---

# 31. 实现阶段

```text
Phase 1  Contract Package 与 Typed Port
Phase 2  Domain 与 Repository / UnitOfWork
Phase 3  PostgreSQL Schema
Phase 4  Graph State V2 与所有任务统一 Plan
Phase 5  StepExecutionGraph 与多轮 ReAct
Phase 6  Parallel Scheduler
Phase 7  PlanVersion Replan
Phase 8  PostgreSQL Checkpointer
Phase 9  Outcome、Cancellation、AnswerPolicy
Phase 10 Cutover 与旧路径清理
```

---

# 32. 测试与完成证据

Domain Unit：状态机、PlanVersion 不可变、Patch stale、Join、Lease、Budget、DecisionGuard。

PostgreSQL Integration：Plan 激活原子性、one-active-version、Dispatch 事务、Action 幂等、Interrupt 幂等、乐观锁、Outbox、Workspace 隔离。

LangGraph Integration：单步骤 Plan、Send fan-out、Reducer 幂等、并行失败、并行 Interrupt、精确 Resume、Step 子图 Checkpoint、Replan Barrier。

Fault Injection：Tool 成功后崩溃、Dispatch 事务中崩溃、Patch 事务中崩溃、Checkpoint 失败、Lease 过期、Outbox 重复、Security Epoch 变化。

E2E：

```text
简单任务创建 Plan
复杂任务至少两个 Step 真实并行
Step 内真实多轮 ReAct
Acceptance 改变路由
Replan 创建新 PlanVersion
已完成 Step 跨版本复用
KnowledgeSnapshot 固定
Ingestion Wait / Resume
审批副作用 exactly-once
AnswerPolicy 阻止无证据回答
PARTIAL / ABSTAINED Outcome
Cancellation 传播到所有分支
```

只有代码、Migration、测试、Eval 和运行证据全部存在后，才能把 Target 写成 Current。

---

# 33. 最终冻结结论

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

该模块负责统一规划与控制，不吞并 Knowledge、Input、Model、Memory、Capability、Tool 或 Security 的 Owner 边界。