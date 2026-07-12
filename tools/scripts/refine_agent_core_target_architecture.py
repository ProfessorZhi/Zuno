from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / "docs/modules/06-agent-core-planning-control.md"
MIRROR = ROOT / ".agent/modules/06-agent-core-planning-control.md"
VERIFIER = ROOT / "tools/scripts/verify_agent_core_target_protocols.py"
TESTS = ROOT / "tests/repo/test_agent_core_target_protocols.py"
AGENT_SYSTEM_VERIFIER = ROOT / ".agent/scripts/verify_agent_system.py"
MARKER = "# Part V：领域模型、状态转换与决策闭环"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def expanded_envelope() -> str:
    return """```text
contract_name
contract_version
contract_bundle_version
message_id
correlation_id
causation_id
tenant_id
workspace_id
run_id
step_run_id
producer
consumer
security_context_ref
authorization_decision_ref
data_classification
created_at
payload
payload_schema_hash
```"""


def part_v() -> str:
    return r'''# Part V：领域模型、状态转换与决策闭环

本 Part 是跨章节 Schema、状态转换、Policy 和持久化闭环的规范性事实源。Part I–IV 用于解释问题、流程和实现表面；Part VI–VII 定义详细控制与一致性协议。发生重复或表述冲突时，按以下顺序解释：

```text
Part V 的对象分类、状态转换、Policy 与存储映射
→ Part VI 的控制协议
→ Part VII 的一致性与生命周期协议
→ Part I–IV 的说明性概览
```

任何冲突必须在同一轮文档修改中消除，不能让 Program 或实现自行选择解释。

## 29. 领域对象分类与存储闭环

### 29.1 对象类型

| 类型 | 对象 | 规则 |
| --- | --- | --- |
| Aggregate Root | `TaskContract`、`AgentRun`、`PlanVersion`、`StepRun`、`PreparedAction`、`ArtifactVersion`、`Publication` | 通过 Application Service 和 Repository 修改；拥有独立并发与不变量边界 |
| Entity | `GoalVersion`、`ObjectiveDefinition`、`ObjectiveOutcome`、`ActionRun`、`Interrupt`、`DispatchGroup`、`DispatchItem`、`FinalCandidate`、`DeliveryReceipt` | 生命周期从属于明确 Aggregate，不允许跨 Aggregate 隐式写入 |
| Immutable Result | `Observation`、`AcceptanceResult`、`ReflectionResult`、`BranchResultRef`、`JoinOutcome`、`ControlDecision`、`RunOutcome` | 提交后不可原地改写；更正创建新版本或 Correction Record |
| Value Object / Policy Snapshot | `DependencyRule`、`ActivationCondition`、`JoinPolicy`、`ResourceClaim`、`EffectivePolicySnapshot`、`ResultValidityRecord` | 必须版本化、可哈希、可审计；不得隐藏可执行代码 |
| Infrastructure Record | `DomainCommitMarker`、`RecoveryWatermark`、`OutboxEvent`、`ReconciliationRecord`、`IdempotencyClaim`、Lease | 记录恢复和交付事实，不冒充业务结果 |

不是每个名称都需要独立 Repository。是否建表由本节 Storage Mapping 决定，Codex 不得仅根据类名自行拆表。

### 29.2 Storage Mapping

| 对象 | Owner | 持久化形式 | 目标表 / 载体 | 关键约束 |
| --- | --- | --- | --- | --- |
| `TaskContract` | Agent Core | Relational Aggregate | `agent_task_contracts` | 一个 Run 一个有效 Contract |
| `GoalVersion` | Agent Core | Relational Entity | `agent_goal_versions` | 同一 Contract 最多一个 ACTIVE |
| `ObjectiveDefinition` | Agent Core | Relational Entity | `agent_objectives` | `logical_objective_id` 跨版本可追踪 |
| `ObjectiveOutcome` | Agent Core | Relational Immutable Result | `agent_objective_outcomes` | RunOutcome 必须引用，不得只写自由文本 |
| `EffectivePolicySnapshot` | Agent Core | JSONB Snapshot + Hash | `agent_effective_policy_snapshots` | Run 创建时冻结 |
| `RunCommand` | Agent Core | Ordered Command Journal | `agent_run_commands` | `UNIQUE(run_id, command_sequence_no)` |
| `ControlDecision` | Agent Core | Immutable Result | `agent_control_decisions` | 引用 Command 与 applied generation |
| `ResourceClaim` | Agent Core | Relational Lease/Claim | `agent_resource_claims` | Canonical Resource ID + Access Mode |
| `PlanPatchOperation` | Agent Core | Relational Operation | `agent_plan_patch_operations` | 只生成新 PlanVersion，不原地改 Active Plan |
| `DomainCommitMarker` | Agent Core | Relational Infrastructure Record | `agent_domain_commit_markers` | `UNIQUE(run_id, domain_generation)` |
| `RecoveryWatermark` | Agent Core | Relational Projection | `agent_recovery_watermarks` | 每个 Run 单行条件更新 |
| `ArtifactCandidate` | Agent Core | Metadata + Object Ref | `agent_artifact_candidates` | 未验证草稿不得发布 |
| `PublicationArtifactBinding` | Agent Core | Relational Binding | `agent_publication_artifact_bindings` | Publication 与 ArtifactVersion 多对多 |
| `PublicationCorrectionDecision` | Agent Core | Immutable Decision | `agent_publication_correction_decisions` | 不覆盖原 Publication / Receipt |
| `BudgetConsumption` | Agent Core | Append-only Ledger | `agent_budget_consumptions` | Usage 可延迟结算但不可丢失 |
| `BudgetAdjustment` | Agent Core | Append-only Ledger | `agent_budget_adjustments` | 必须有 reason 和 causation |
| `BudgetSettlement` | Agent Core | Immutable Result | `agent_budget_settlements` | Run 终局前或后台 Reconcile 完成 |
| 大型 Observation / Artifact | 对应事实 Owner | Immutable Object | Object Store + content hash | 数据库只保存 Ref、Hash 和 Metadata |

没有列为独立表的 `DependencyRule`、`ActivationCondition`、`JoinPolicy`、`CompletionPolicy` 和 Acceptance Check Definition，可以作为其 Aggregate 的版本化 JSONB Snapshot；一旦需要独立查询、外键引用或局部更新，必须先通过 ADR 改变存储决策。

## 30. 状态转换协议

### 30.1 通用 Transition Record

每次状态转换必须产生结构化 Transition Record：

```text
transition_id
aggregate_type
aggregate_id
from_status
to_status
trigger_type
trigger_ref
guard_result_ref
reason_code
controller_epoch
execution_epoch
policy_snapshot_ref
domain_generation
occurred_at
trace_id
```

状态转换必须由确定性 Guard 执行。模型只能建议 `reason` 或下一步，不得提交状态。

### 30.2 AgentRun Transition Matrix

| From | Trigger | Guard | To | 同事务事实 |
| --- | --- | --- | --- | --- |
| `CREATED` | `START_VALIDATION` | RuntimeRequest 已幂等提交 | `VALIDATING_INPUT` | RunTransition + Event |
| `VALIDATING_INPUT` | `INPUT_VALID` | TaskContract 可构造 | `BUILDING_CONTEXT` | TaskContract + GoalVersion |
| `VALIDATING_INPUT` | `INPUT_INVALID` | 不可 Repair | `FAILED` | Failure + RunOutcome |
| `BUILDING_CONTEXT` | `CONTEXT_READY` | Snapshot 完整且 Security 有效 | `PLANNING` | ExecutionContextSnapshot |
| `PLANNING` | `PLAN_PROPOSED` | Planner Budget 未耗尽 | `VALIDATING_PLAN` | Proposed PlanVersion |
| `VALIDATING_PLAN` | `PLAN_ACCEPTED` | DAG、Capability、Budget、Security、Acceptance 全部合法 | `READY` | Active PlanVersion + ActivationEvent |
| `VALIDATING_PLAN` | `PLAN_REJECTED` | Repair/Replan 预算耗尽 | `FAILED` 或 `ABSTAINED` | Failure + Outcome |
| `READY` | `SCHEDULE_TICK` | Admission 允许 | `RUNNING` | Dispatch Commit |
| `RUNNING` | `WAIT_REQUIRED` | 存在有效 Interrupt / External Job / Resource Wait | `WAITING_CONDITION` | Interrupt/Handle + Event |
| `WAITING_CONDITION` | `VALID_SIGNAL` | Signal 鉴权、幂等、未过期 | `RUNNING` | SignalConsumption + ControlDecision |
| `RUNNING` | `REPLAN_REQUIRED` | 原计划结构或假设失效 | `REPLANNING` | ReplanBarrier |
| `REPLANNING` | `PLAN_ACTIVATED` | 新 PlanVersion 原子激活 | `RUNNING` | Plan switch + ReadySet generation |
| `RUNNING` | `OBJECTIVES_READY` | REQUIRED Objective 可进入 Finalization | `FINALIZING` | FinalCandidate seed |
| `FINALIZING` | `FINAL_GATE_PASS` | Evidence、Citation、Security、Validity、Artifact 全通过 | `PUBLISHING` | ArtifactVersion + PREPARED Publication |
| `FINALIZING` | `FINAL_GATE_ABSTAIN` | 证据或能力不足 | `ABSTAINED` | RunOutcome |
| `FINALIZING` | `FINAL_GATE_REFUSE` | Policy / Security 要求拒绝 | `REFUSED` | RunOutcome |
| `PUBLISHING` | `DELIVERY_CONFIRMED` | Receipt 幂等且 Publication Gate 仍有效 | `COMPLETED` 或 `PARTIAL` | Receipt + Publication + RunOutcome |
| 任意非终态 | `SECURITY_REVOKE` | 撤权影响继续执行 | `CANCELLING`、`REFUSED` 或 `BLOCKED` | ControlDecision + AuditEvent |
| 任意非终态 | `CANCEL` | 命令合法 | `CANCELLING` | CancellationBarrier |
| `CANCELLING` | `DRAIN_COMPLETE` | 不可中断副作用已完成或 Reconcile | `CANCELLED` 或 `PARTIAL` | RunOutcome + BudgetSettlement |
| `WAITING_CONDITION` | `EXPIRE` | Deadline / Interrupt / Approval 到期且无替代路径 | `EXPIRED` | Failure + RunOutcome |

`PUBLISHING` 失败不自动等于 Run `FAILED`：可恢复渠道故障保持 `PUBLISHING` 并由 PublicationReconciler 处理；明确不可恢复且没有其他渠道时，依据 AnswerPolicy 进入 `PARTIAL`、`BLOCKED` 或 `FAILED`。

### 30.3 聚合投影规则

```text
存在未解决 ActionOutcome=UNKNOWN
    → StepRun 不得 COMPLETED
    → Final Gate 不得 PASS

所有 REQUIRED ObjectiveOutcome=SATISFIED
且 Final Gate=PASS
且 Publication 已确认或 Policy 明确无需发布
    → AgentRun=COMPLETED

至少一个 REQUIRED Objective SATISFIED
且未完成部分已披露
且 AnswerPolicy 允许 Partial
    → AgentRun=PARTIAL

Active PlanVersion 的所有可达 Step 已终止
但 REQUIRED Objective 未满足
    → Retry / Fallback / Replan / Abstain / Fail，不能直接 COMPLETED
```

### 30.4 非法转换与终态不可变

必须拒绝：`COMPLETED → RUNNING`、`CANCELLED → PUBLISHING`、`SUPERSEDED PlanVersion → ACTIVE`、`OBSOLETE StepRun → RUNNING`、无新 Attempt 的 `FAILED Publication → PUBLISHED`。

终态后允许新增 AuditEvent、Metric、ReconciliationRecord 和 PublicationCorrectionDecision；禁止覆盖原 GoalVersion、PlanVersion、RunOutcome、DeliveryReceipt 和历史 Event。

## 31. Action 生命周期与对账结果

Action 的执行生命周期和业务结果是两个正交维度：

```text
ActionLifecycleStatus
    PROPOSED
    VALIDATING
    PREPARED
    WAITING_APPROVAL
    CLAIMED
    EXECUTING
    RECONCILING
    TERMINAL

ActionOutcome
    SUCCEEDED
    FAILED
    NOT_EXECUTED
    CANCELLED
    UNKNOWN
    HUMAN_REQUIRED
```

`RECONCILING` 表示正在确认外部事实，不是业务结果。Reconciler 必须提交明确 `ActionOutcome`；仍无法确认时为 `UNKNOWN` 或 `HUMAN_REQUIRED`，不得使用含义模糊的 `RECONCILED` 代替结果。

## 32. RunCommand 与 ControlDecision

### 32.1 RunCommand

```text
command_id
run_id
command_sequence_no
command_type
producer
producer_authority
payload_ref
idempotency_key
correlation_id
causation_id
expected_controller_epoch
security_epoch
policy_snapshot_ref
observed_at
received_at
status
applied_domain_generation
```

`command_sequence_no` 由 PostgreSQL 在同一 `run_id` 范围分配并形成唯一约束；命令顺序不得依赖 Worker 本地时间或 `observed_at`。Command 已提交但 Controller 崩溃时，由新 Controller 从最后 `applied_domain_generation` 继续。

### 32.2 ControlDecision

```text
control_decision_id
run_id
command_id
command_sequence_no
decision_type
reason_code
previous_state
next_state
selected_plan_version_id
selected_interrupt_refs
policy_snapshot_ref
controller_epoch
applied_domain_generation
created_at
```

ControlDecision 是不可变 Result；重复 Command 返回原 Decision，不再次修改领域状态。

## 33. Effective Policy Snapshot

Policy 解析顺序：

```text
System Default
→ Tenant Policy
→ Workspace Policy
→ User Policy
→ Task Policy
→ Security Override
→ Runtime Emergency Override
```

解析结果必须保存不可变 `EffectivePolicySnapshot`：

```text
effective_policy_snapshot_id
run_id
system_policy_version
tenant_policy_version
workspace_policy_version
user_policy_version
task_policy_version
security_override_version
runtime_override_version
resolved_policy
resolution_trace
content_hash
created_at
```

`RuntimePolicy` 至少包含 planning_mode、parallelism_mode、reflection_mode、replan_mode、recovery_mode、publication_mode、max_plan_versions、max_step_attempts、max_action_attempts、max_react_iterations 和 max_finalization_cycles。

`AcceptancePolicy` 至少包含 required_checks、evaluator_types、output_schema、evidence_threshold、citation_threshold、confidence_threshold、failure_disposition 和 reflection_trigger。

`ReflectionPolicy` 至少包含 trigger_conditions、model_role、budget_limit、max_iterations 和 allowed_decisions。模型不得自行决定绕过 Reflection Policy。

## 34. ResourceClaim 与 PlanPatch Algebra

### 34.1 ResourceClaim

```text
resource_claim_id
run_id
step_run_id
resource_type
canonical_resource_id
access_mode
scope
quantity
lease_duration
renewal_policy
acquisition_order
preemptible
claim_token
fencing_epoch
```

Access Mode：`READ_SHARED`、`WRITE_EXCLUSIVE`、`APPEND_SERIALIZED`、`CAPACITY_SHARED`、`NON_PREEMPTIBLE`。

多资源 Claim 必须按 `(resource_type, canonical_resource_id, acquisition_order)` 固定顺序获取；部分获取失败时释放已获取 Claim。父子资源冲突、Deadlock、Priority Inversion、Lease Renewal 和 Replan 后 Claim 转移必须由 Resource Policy 明确处理。

### 34.2 PlanPatchOperation

```text
ADD_STEP
REMOVE_STEP
REPLACE_STEP
REWIRE_DEPENDENCY
CHANGE_ACTIVATION_CONDITION
CHANGE_JOIN_POLICY
CHANGE_ACCEPTANCE_POLICY
CHANGE_CAPABILITY_BINDING
CHANGE_BUDGET_ALLOCATION
CHANGE_TERMINAL_DELIVERABLE
```

每个 Operation 保存 operation_id、operation_type、target_logical_id、before_hash、after_definition_ref、reason_code、affected_objective_refs、invalidated_result_refs 和 reusable_result_refs。

PlanPatch 只能生成新 PlanVersion；不能原地修改 Active PlanVersion。已提交副作用不能被 Patch 当作未发生，旧结果复用必须重新检查 GoalVersion、ResultValidity、Security Scope、Knowledge Snapshot 和 Output Contract。

## 35. Failure Decision Matrix

| FailureClass | Retry | Repair | Fallback | Replan | Reconcile | Human | 默认 Run 处置 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `TRANSIENT_INFRASTRUCTURE` | 有限 | 否 | 可选 | 否 | 否 | 否 | WAIT / FAILED |
| `RATE_LIMIT` | 有限退避 | 否 | 是 | 否 | 否 | 否 | WAIT / FAILED |
| `TIMEOUT` | 条件性 | 条件性 | 是 | 条件性 | 副作用时必须 | 条件性 | WAIT / FAILED |
| `CONTRACT_VIOLATION` | 否 | 是 | 条件性 | 条件性 | 否 | 否 | FAILED |
| `INVALID_MODEL_OUTPUT` | 有限 | 是 | 是 | 条件性 | 否 | 否 | FAILED |
| `CAPABILITY_UNAVAILABLE` | 否 | 否 | 是 | 是 | 否 | 否 | PARTIAL / FAILED |
| `SECURITY_BLOCK` | 否 | 否 | 否 | 否 | 否 | 条件性 | REFUSED / BLOCKED |
| `APPROVAL_DENIED` | 否 | 否 | 条件性 | 条件性 | 否 | 否 | PARTIAL / REFUSED |
| `BUDGET_EXHAUSTED` | 否 | 否 | 条件性 | 条件性 | 否 | 否 | PARTIAL / ABSTAINED |
| `UNKNOWN_SIDE_EFFECT` | 否 | 否 | 否 | 否 | 必须 | 条件性 | BLOCKED |
| `DATA_STALE` | 否 | 否 | 是 | 是 | 否 | 否 | PARTIAL / ABSTAINED |
| `PLAN_INVALID` | 否 | 是 | 否 | 是 | 否 | 否 | FAILED |
| `NO_PROGRESS` | 否 | 条件性 | 条件性 | 有限 | 否 | 条件性 | ABSTAINED / FAILED |

项目 Policy 可以收紧默认值；放宽安全、副作用或证据相关默认值必须经过 Security/Architecture 审批并版本化审计。

## 36. Budget Ledger

Budget 不是可覆盖计数器，而是可审计 Ledger：

```text
BudgetEstimate
BudgetReservation
BudgetConsumption
BudgetAdjustment
BudgetSettlement
```

关键不变量：

```text
available = limit + adjustments - reserved - consumed
reserved 不得小于零
并行 Dispatch 先 Reservation，防止超卖
Provider Usage 延迟返回时先保存 provisional consumption，再结算差额
失败调用是否计费以 Provider Receipt 为准
取消释放未消费 Reservation，但不回滚已发生 Consumption
Reservation 到期由 Reconciler 释放
所有金额保存 currency、scale 和 provider pricing version
```

RunOutcome 必须引用最终 BudgetSettlement；无法及时获得 Provider Usage 时允许先进入终态，但必须标记 `SETTLEMENT_PENDING` 并由后台 Reconciler 完成，不得丢失账务责任。

## 37. Publication Ownership 与企业 Contract Envelope

### 37.1 Publication Ownership

```text
PublicationIntent / PublicationRecord
    Owner：Agent Core

ChannelDelivery
    Owner：Product Surface

DeliveryReceipt
    Producer：Product Surface 或渠道 Adapter
    Consumer：Agent Core

ClientRendered / UserRead
    Owner：Product Surface
```

`PUBLISHED` 只表示渠道返回可验证 DeliveryReceipt，不表示用户已经阅读或客户端已经成功渲染。

ArtifactVersion 的生命周期状态仅允许 `DRAFT`、`VALIDATING`、`VALID`、`INVALID`、`SUPERSEDED`；发布、撤回和渠道失败属于 Publication，不写回 ArtifactVersion 生命周期。

### 37.2 Contract Envelope

所有跨模块请求、响应和事件必须带：

```text
contract_name
contract_version
contract_bundle_version
message_id
correlation_id
causation_id
tenant_id
workspace_id
run_id
step_run_id
producer
consumer
security_context_ref
authorization_decision_ref
data_classification
created_at
payload
payload_schema_hash
```

消费者必须独立验证 tenant、workspace、security context 和 contract version，不能只通过 `run_id` 反查后默认可信。

## 38. Requirement Enforcement Matrix

每个 001–080 Requirement 必须有一条 `RequirementControl`：

```text
requirement_id
category
owner
enforcement_type
enforcement_ref
failure_code
test_ids
evidence_types
status
```

测试和证据命名采用稳定规则：Requirement `NNN` 对应测试前缀 `AG-NNN-*`，运行证据键 `EV-AG-NNN`。Program 可以增加多个测试，但不得缺失基础映射。

| Requirement 范围 | Category | 最低 Enforcement | 最低测试 | 运行证据 |
| --- | --- | --- | --- | --- |
| 001–010 | FOUNDATION / PLAN | Schema、Plan Validator、Unique Constraint | Unit + Integration | PlanValidation / Activation Event |
| 011–020 | EXECUTION / QUALITY | Step Guard、Acceptance、Decision Guard | Unit + Integration + E2E | StepTransition / Acceptance Record |
| 021–032 | RECOVERY / SECURITY | Idempotency、Fencing、Security Gate | Integration + Fault | Rejected Write / Reconciliation Record |
| 033–043 | CONTROL / DAG | State Guard、DAG Validator、Barrier | Unit + Integration + Fault | Transition / Barrier Event |
| 044–050 | INTERRUPT / SIDE_EFFECT / FINAL | Signal Guard、PreparedAction、Receipt | Integration + Fault + E2E | SignalConsumption / DeliveryReceipt |
| 051–060 | FAILURE / BUDGET / OWNERSHIP | Decision Matrix、Ledger、Port Boundary | Unit + Integration | FailureDecision / BudgetSettlement |
| 061–070 | GOAL / COMMAND / CONSISTENCY | Version Constraint、Command Journal、Generation Guard | Integration + Fault | ControlDecision / DomainCommitMarker |
| 071–080 | VALIDITY / EVENT / ARTIFACT / TIME | Validity Gate、Outbox、Artifact Validation、Clock Guard | Integration + Fault + E2E | ValidityRecord / OutboxReceipt / AuditEvent |

高风险 Requirement（Fencing、Approval、UNKNOWN、副作用、Security、Publication、Recovery）必须有 Fault Test。状态机 Requirement 必须同时覆盖合法和非法转换。

---
'''


def refine_document() -> str:
    text = FORMAL.read_text(encoding="utf-8")
    if MARKER in text:
        return text

    text = text.replace(
        "未来 Program 必须以本文及配套规范为目标约束。",
        "未来 Program 必须以本文为目标约束。",
    )
    text = replace_once(
        text,
        "任何 Program 或实现不得自行改变本文已经确认的架构原则。本文不包含 Current Baseline、具体迁移阶段或 Cutover 步骤。\n\n---",
        """任何 Program 或实现不得自行改变本文已经确认的架构原则。本文不包含 Current Baseline、具体迁移阶段或 Cutover 步骤。

### 0.1 文档内部规范层级

Part I–IV 是问题、流程和实现表面的说明性视图；Part V–VII 是字段、状态、Policy、持久化与恢复的规范性视图；Part VIII 定义 Requirement、测试和完成证据。说明性视图不得覆盖规范性 Contract。

---""",
        "document precedence",
    )
    text = text.replace("# Part III：状态、恢复与一致性", "# Part III：状态、恢复与一致性概览")
    text = text.replace("# Part IV：目标 Contract 与实施规格", "# Part IV：目标实现表面与规范索引")

    old_objects = """TaskContract
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
ReconciliationRecord"""
    new_objects = """TaskContract
GoalVersion
ObjectiveDefinition
ObjectiveOutcome
ExecutionContextSnapshot
EffectivePolicySnapshot
AgentRun
RunCommand
ControlDecision
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
ResourceClaim
BranchResultRef
ReductionAttempt
JoinAttempt
PlanPatch
PlanPatchOperation
ReplanBarrier
Interrupt
SignalConsumption
PreparedAction
ApprovalDecision
IdempotencyClaim
DomainCommitMarker
RecoveryWatermark
ResultValidityRecord
FinalCandidate
ArtifactCandidate
ArtifactVersion
ArtifactValidation
Publication
PublicationArtifactBinding
PublicationCorrectionDecision
DeliveryReceipt
RunOutcome
BudgetConsumption
BudgetAdjustment
BudgetSettlement
DomainEvent
RuntimeEvent
OutboxEvent
ReconciliationRecord"""
    text = replace_once(text, old_objects, new_objects, "domain object list")

    text = text.replace(
        "├── agent_objectives\n├── agent_runs",
        "├── agent_objectives\n├── agent_objective_outcomes\n├── agent_runs\n├── agent_run_commands\n├── agent_control_decisions",
    )
    text = text.replace(
        "├── agent_runtime_policy_snapshots\n└── agent_answer_policy_snapshots",
        "├── agent_runtime_policy_snapshots\n├── agent_answer_policy_snapshots\n└── agent_effective_policy_snapshots",
    )
    text = text.replace(
        "├── agent_resource_leases\n└── agent_budget_reservations",
        "├── agent_resource_leases\n├── agent_resource_claims\n├── agent_budget_reservations\n├── agent_budget_consumptions\n├── agent_budget_adjustments\n└── agent_budget_settlements",
    )
    text = text.replace(
        "├── agent_final_candidates\n├── agent_claims",
        "├── agent_final_candidates\n├── agent_artifact_candidates\n├── agent_claims",
    )
    text = text.replace(
        "├── agent_artifact_validations\n├── agent_publications",
        "├── agent_artifact_validations\n├── agent_publications\n├── agent_publication_artifact_bindings\n├── agent_publication_correction_decisions",
    )
    text = text.replace(
        "Validity and Eventing\n├── agent_result_validity",
        "Consistency, Validity and Eventing\n├── agent_domain_commit_markers\n├── agent_recovery_watermarks\n├── agent_result_validity",
    )

    old_action = """### 5.2 ActionRun

```text
PROPOSED
VALIDATING
PREPARED
WAITING_APPROVAL
CLAIMED
EXECUTING
SUCCEEDED
FAILED
UNKNOWN
RECONCILING
RECONCILED
CANCELLED
```

Action 进入 SUCCEEDED 需要外部结果和本地领域事实均提交；响应丢失时进入 UNKNOWN。"""
    new_action = """### 5.2 ActionRun

Action 使用正交的生命周期和结果：

```text
ActionLifecycleStatus
    PROPOSED
    VALIDATING
    PREPARED
    WAITING_APPROVAL
    CLAIMED
    EXECUTING
    RECONCILING
    TERMINAL

ActionOutcome
    SUCCEEDED
    FAILED
    NOT_EXECUTED
    CANCELLED
    UNKNOWN
    HUMAN_REQUIRED
```

进入 `TERMINAL / SUCCEEDED` 需要外部结果和本地领域事实均提交；响应丢失时 Outcome 为 `UNKNOWN` 并进入 `RECONCILING`。对账完成后必须提交明确 Outcome，不能只写含义模糊的 `RECONCILED`。"""
    text = replace_once(text, old_action, new_action, "ActionRun semantics")

    text = text.replace(
        "状态：DRAFT、VALIDATING、VALID、INVALID、SUPERSEDED、PUBLISHED、WITHDRAWN。",
        "生命周期状态：DRAFT、VALIDATING、VALID、INVALID、SUPERSEDED。发布和撤回属于 Publication 状态，不写回 ArtifactVersion 生命周期。",
    )
    text = text.replace(
        "查询外部事实，提交 SUCCEEDED、FAILED、RECONCILED 或 HUMAN_REQUIRED。",
        "查询外部事实，提交 ActionOutcome=SUCCEEDED、FAILED、NOT_EXECUTED、UNKNOWN 或 HUMAN_REQUIRED；生命周期进入 TERMINAL 或保持 RECONCILING。",
    )

    old_command = """command_id
run_id
command_type
producer
producer_authority
payload_ref
idempotency_key
observed_at
received_at
expected_controller_epoch
status"""
    new_command = """command_id
run_id
command_sequence_no
command_type
producer
producer_authority
payload_ref
idempotency_key
correlation_id
causation_id
observed_at
received_at
expected_controller_epoch
security_epoch
policy_snapshot_ref
status
applied_domain_generation"""
    text = replace_once(text, old_command, new_command, "RunCommand fields")

    simple_envelope = """```text
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
```"""
    text = text.replace(simple_envelope, expanded_envelope())

    text = text.replace(
        "本文完成后只可声明 design available、contract-complete 和 program-ready，不得仅凭文档声明 implementation available、quality proven 或 production ready。",
        "本文通过语义验证后可声明 design available、internally consistent、contract-complete、implementation-spec-complete 和 program-ready；不得仅凭文档声明 implementation available、quality proven 或 production ready。",
    )

    text = replace_once(
        text,
        "# Part VI：规范性控制协议",
        part_v() + "\n# Part VI：规范性控制协议",
        "Part V insertion",
    )
    return text


def verifier_source() -> str:
    return '''from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/06-agent-core-planning-control.md"
MIRROR = REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
AGENTS = REPO_ROOT / "AGENTS.md"
SYSTEM_YAML = REPO_ROOT / ".agent/system.yaml"

REMOVED_PATHS = [
    REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md",
    REPO_ROOT / "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
    REPO_ROOT / ".agent/modules/06-agent-core-control-protocols.md",
    REPO_ROOT / ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
]

REQUIRED_PARTS = [
    "# Part I：定位与概念架构",
    "# Part II：智能机制与运行流程",
    "# Part III：状态、恢复与一致性概览",
    "# Part IV：目标实现表面与规范索引",
    "# Part V：领域模型、状态转换与决策闭环",
    "# Part VI：规范性控制协议",
    "# Part VII：一致性与生命周期协议",
    "# Part VIII：验证与完成证据",
]

REQUIRED_TERMS = [
    "Single Controller Agent Runtime",
    "AgentRunGraph",
    "StepExecutionGraph",
    "TaskContract",
    "GoalVersion",
    "EffectivePolicySnapshot",
    "ActionLifecycleStatus",
    "ActionOutcome",
    "command_sequence_no",
    "ResourceClaim",
    "PlanPatchOperation",
    "BudgetSettlement",
    "Requirement Enforcement Matrix",
    "Transition Matrix",
    "pending_interrupt_refs",
    "WAITING_CONDITION",
    "CANCELLING",
    "PreparedAction",
    "RecoveryWatermark",
    "ResultValidity",
    "RunOrphanReconciler",
    "prepare_publication",
    "DeliveryReceipt",
    "PostgreSQL",
    "本文是 Agent Core / Planning & Control 模块唯一的正式 Target 架构文档",
    ".agent/programs/",
]

REQUIRED_TABLES = [
    "agent_objective_outcomes",
    "agent_run_commands",
    "agent_control_decisions",
    "agent_effective_policy_snapshots",
    "agent_resource_claims",
    "agent_domain_commit_markers",
    "agent_recovery_watermarks",
    "agent_artifact_candidates",
    "agent_publication_artifact_bindings",
    "agent_publication_correction_decisions",
    "agent_budget_consumptions",
    "agent_budget_adjustments",
    "agent_budget_settlements",
]

FORBIDDEN_TERMS = [
    "# 35. Current Baseline",
    "# 36. 实现阶段",
    "pending_interrupt_id: str | None",
    "同一 Run 默认只允许一个 PENDING Interrupt",
    "Agent Core Target 由三份正式文档共同构成",
    "未来 Program 必须以本文及配套规范为目标约束",
    "状态：DRAFT、VALIDATING、VALID、INVALID、SUPERSEDED、PUBLISHED、WITHDRAWN。",
    "SUCCEEDED\\nFAILED\\nUNKNOWN\\nRECONCILING\\nRECONCILED",
]

OBJECT_TABLE_PAIRS = {
    "ObjectiveOutcome": "agent_objective_outcomes",
    "RunCommand": "agent_run_commands",
    "ControlDecision": "agent_control_decisions",
    "EffectivePolicySnapshot": "agent_effective_policy_snapshots",
    "ResourceClaim": "agent_resource_claims",
    "DomainCommitMarker": "agent_domain_commit_markers",
    "RecoveryWatermark": "agent_recovery_watermarks",
    "ArtifactCandidate": "agent_artifact_candidates",
    "PublicationArtifactBinding": "agent_publication_artifact_bindings",
    "PublicationCorrectionDecision": "agent_publication_correction_decisions",
    "BudgetConsumption": "agent_budget_consumptions",
    "BudgetAdjustment": "agent_budget_adjustments",
    "BudgetSettlement": "agent_budget_settlements",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX, AGENTS, SYSTEM_YAML]:
        if not path.exists():
            errors.append(f"missing Agent Core target path: {path.relative_to(REPO_ROOT)}")
    for path in REMOVED_PATHS:
        if path.exists():
            errors.append(f"retired split Agent Core document still exists: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Agent Core formal document and mirror must be byte-identical")

    if "status: normative-target-module-architecture" not in formal:
        errors.append("Agent Core document must declare normative-target-module-architecture")

    positions: list[int] = []
    for part in REQUIRED_PARTS:
        if formal.count(part) != 1:
            errors.append(f"Agent Core document must contain part exactly once: {part}")
        else:
            positions.append(formal.index(part))
    if positions and positions != sorted(positions):
        errors.append("Agent Core document parts are not in canonical order I through VIII")

    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Agent Core document missing required term: {term}")
    for table in REQUIRED_TABLES:
        if table not in formal:
            errors.append(f"Agent Core document missing target table: {table}")
    for term in FORBIDDEN_TERMS:
        if term in formal:
            errors.append(f"Agent Core document contains obsolete or conflicting contract: {term}")

    for object_name, table_name in OBJECT_TABLE_PAIRS.items():
        if object_name not in formal or table_name not in formal:
            errors.append(f"Agent Core object/storage mapping incomplete: {object_name} -> {table_name}")

    for transition in [
        "VALIDATING_INPUT` | `INPUT_INVALID",
        "RUNNING` | `REPLAN_REQUIRED",
        "FINALIZING` | `FINAL_GATE_PASS",
        "PUBLISHING` | `DELIVERY_CONFIRMED",
        "CANCELLING` | `DRAIN_COMPLETE",
    ]:
        if transition not in formal:
            errors.append(f"AgentRun Transition Matrix missing transition: {transition}")

    for policy_term in [
        "System Default",
        "Tenant Policy",
        "Security Override",
        "Runtime Emergency Override",
        "AcceptancePolicy",
        "ReflectionPolicy",
    ]:
        if policy_term not in formal:
            errors.append(f"Agent Core Policy Contract missing term: {policy_term}")

    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\\d{3})", formal)]
    if sorted(ids) != list(range(1, 81)):
        errors.append("Agent Core document must define ARCH-AGENT-001 through ARCH-AGENT-080 exactly once")

    for index_name, content in {
        "docs/modules/README.md": _read(DOCS_INDEX),
        ".agent/modules/README.md": _read(AGENT_INDEX),
        "AGENTS.md": _read(AGENTS),
        ".agent/system.yaml": _read(SYSTEM_YAML),
    }.items():
        if "06-agent-core-planning-control.md" not in content:
            errors.append(f"{index_name} does not route to the unified Agent Core target document")
        for retired in [
            "06-agent-core-control-protocols.md",
            "06-agent-core-consistency-lifecycle-protocols.md",
        ]:
            if retired in content:
                errors.append(f"{index_name} still references retired split document: {retired}")

    if ".agent/programs" not in formal or ".agent/programs" not in _read(DOCS_INDEX):
        errors.append("Target architecture and execution Program boundary is not explicit")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("refined Agent Core target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def tests_source() -> str:
    return '''from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_agent_core_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/06-agent-core-planning-control.md"
MIRROR = REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_agent_core_target_protocols", VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Agent Core target verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_refined_agent_core_target_contract() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_only_one_agent_core_target_document_exists() -> None:
    assert FORMAL.exists()
    assert MIRROR.exists()
    for relative in [
        "docs/modules/06-agent-core-control-protocols.md",
        "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
        ".agent/modules/06-agent-core-control-protocols.md",
        ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
    ]:
        assert not (REPO_ROOT / relative).exists()


def test_document_parts_are_complete_and_ordered() -> None:
    content = _content()
    parts = [
        "# Part I：定位与概念架构",
        "# Part II：智能机制与运行流程",
        "# Part III：状态、恢复与一致性概览",
        "# Part IV：目标实现表面与规范索引",
        "# Part V：领域模型、状态转换与决策闭环",
        "# Part VI：规范性控制协议",
        "# Part VII：一致性与生命周期协议",
        "# Part VIII：验证与完成证据",
    ]
    positions = [content.index(part) for part in parts]
    assert positions == sorted(positions)
    assert all(content.count(part) == 1 for part in parts)


def test_unified_document_covers_all_requirements_once() -> None:
    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\\d{3})", _content())]
    assert sorted(ids) == list(range(1, 81))


def test_target_only_and_program_separated() -> None:
    content = _content()
    assert "唯一的正式 Target 架构文档" in content
    assert ".agent/programs/" in content
    assert "Current Baseline" not in content
    assert "具体迁移阶段" in content
    assert "未来 Program 必须以本文及配套规范" not in content


def test_agent_core_mirror_is_byte_identical() -> None:
    assert MIRROR.read_bytes() == FORMAL.read_bytes()


def test_domain_objects_have_storage_decisions() -> None:
    content = _content()
    for object_name, table_name in {
        "ObjectiveOutcome": "agent_objective_outcomes",
        "RunCommand": "agent_run_commands",
        "ControlDecision": "agent_control_decisions",
        "EffectivePolicySnapshot": "agent_effective_policy_snapshots",
        "ResourceClaim": "agent_resource_claims",
        "DomainCommitMarker": "agent_domain_commit_markers",
        "RecoveryWatermark": "agent_recovery_watermarks",
        "ArtifactCandidate": "agent_artifact_candidates",
        "PublicationArtifactBinding": "agent_publication_artifact_bindings",
        "PublicationCorrectionDecision": "agent_publication_correction_decisions",
        "BudgetSettlement": "agent_budget_settlements",
    }.items():
        assert object_name in content
        assert table_name in content


def test_action_artifact_and_command_semantics_are_unambiguous() -> None:
    content = _content()
    assert "ActionLifecycleStatus" in content
    assert "ActionOutcome" in content
    assert "command_sequence_no" in content
    assert "RECONCILED` 代替结果" in content
    assert "发布和撤回属于 Publication 状态" in content
    assert "状态：DRAFT、VALIDATING、VALID、INVALID、SUPERSEDED、PUBLISHED、WITHDRAWN。" not in content


def test_policy_failure_budget_and_requirement_closure() -> None:
    content = _content()
    for term in [
        "Effective Policy Snapshot",
        "Failure Decision Matrix",
        "Budget Ledger",
        "Requirement Enforcement Matrix",
        "AG-NNN-*",
        "EV-AG-NNN",
    ]:
        assert term in content
'''


def update_agent_system_verifier() -> None:
    text = AGENT_SYSTEM_VERIFIER.read_text(encoding="utf-8")
    old = '''            "ResultValidity",
            "RunOrphanReconciler",
            "prepare_publication",
            "ARCH-AGENT-080",
            "PostgreSQL",'''
    new = '''            "ResultValidity",
            "RunOrphanReconciler",
            "prepare_publication",
            "EffectivePolicySnapshot",
            "ActionOutcome",
            "Requirement Enforcement Matrix",
            "ARCH-AGENT-080",
            "PostgreSQL",'''
    if old not in text:
        raise RuntimeError("Agent System verifier Agent Core phrase block not found")
    AGENT_SYSTEM_VERIFIER.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def main() -> None:
    refined = refine_document()
    FORMAL.write_text(refined.rstrip() + "\n", encoding="utf-8", newline="\n")
    MIRROR.write_text(refined.rstrip() + "\n", encoding="utf-8", newline="\n")
    VERIFIER.write_text(verifier_source(), encoding="utf-8", newline="\n")
    TESTS.write_text(tests_source(), encoding="utf-8", newline="\n")
    update_agent_system_verifier()
    print("Agent Core target architecture refined and synchronized.")


if __name__ == "__main__":
    main()
