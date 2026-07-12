from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / "docs/modules/06-agent-core-planning-control.md"
MIRROR = ROOT / ".agent/modules/06-agent-core-planning-control.md"
VERIFIER = ROOT / "tools/scripts/verify_agent_core_target_protocols.py"
TESTS = ROOT / "tests/repo/test_agent_core_target_protocols.py"
AGENT_SYSTEM = ROOT / ".agent/scripts/verify_agent_system.py"
SECTION_MARKER = "## 39. 完整子状态机 Transition Matrix"
PART_VI = "# Part VI：规范性控制协议"


ENFORCEMENTS = [
    "SingleControllerGuard", "MechanismLayerRouter", "RuntimeStateSchemaValidator", "BudgetDeadlineGuard",
    "RuntimeContractGateway", "InterruptResumeAdapter", "LargePayloadRefGuard", "RuntimeTraceEmitter",
    "PlanRequiredGuard", "PlanDagValidator", "PlanVersionImmutabilityGuard", "DefinitionRunResultSchema",
    "ExecutionContextSnapshotGuard", "KnowledgeSnapshotGuard", "FinalGateGuard", "DispatchCommitGuard",
    "SideEffectPolicyValidator", "RunOutcomeSchemaValidator", "ControlPropagationGuard", "InterruptContractValidator",
    "GraphStateRefValidator", "QualityLayerGuard", "StepAcceptanceGuard", "ReplanBarrierGuard",
    "DomainCheckpointBoundaryGuard", "TypedPortSchemaValidator", "ActionOutcomeGuard", "DomainOutboxTransaction",
    "ModelRoleRouter", "StepFeasibilityValidator", "ModelEscalationPolicy", "BranchResultFencingGuard",
    "InvariantRegistry", "StateMachineTransitionGuard", "ActivePlanUniqueConstraint", "DependencyActivationValidator",
    "StepStatusDispositionValidityGuard", "PlanLivenessDetector", "JoinPolicyReducer", "DispatchCommitBeforeSend",
    "EpochConditionalWrite", "ReducerIdempotencyKey", "ReplanVersionSwitch", "MultiInterruptRegistry",
    "SignalConsumptionGuard", "PreparedActionProtocol", "UnknownActionReconcileGuard", "FinalOutputGate",
    "FinalizationSeparationGuard", "PublicationReceiptProtocol", "FailureDecisionTable", "MechanismDecisionAudit",
    "BudgetLedgerGuard", "AdmissionFairnessScheduler", "NoProgressDetector", "OwnershipBoundaryGuard",
    "ContractEnvelopeValidator", "VersionBundlePinning", "PersistenceTierGuard", "RequirementEvidenceRegistry",
    "TaskGoalVersionGuard", "PlanGoalBindingGuard", "ObjectiveOutcomeProjection", "InputClassificationGuard",
    "OrderedCommandJournal", "CommandPrecedenceResolver", "ControlDecisionAudit", "GenerationWatermarkGuard",
    "CheckpointDomainGenerationGuard", "RecoveryRuleEngine", "ResultValidityGuard", "ValidityPropagationEngine",
    "PublicationValidityGate", "EventCategoryGuard", "OrderedOutboxDelivery", "ArtifactVersionValidation",
    "PublicationCorrectionAudit", "ReconcilerCoverageRegistry", "ReconcilerClaimFencingGuard", "TimeSemanticsGuard",
]

HIGH_RISK = {
    4, 6, 15, 17, 19, 24, 25, 27, 28, 32, 35, 38, 40, 41, 42, 43, 44, 45, 46, 47,
    48, 49, 50, 53, 54, 55, 56, 57, 58, 59, 65, 66, 67, 68, 69, 70, 71, 72, 73,
    75, 76, 77, 78, 79, 80,
}
E2E_IDS = {5, 6, 9, 10, 15, 16, 18, 20, 24, 30, 39, 43, 44, 46, 48, 49, 50, 54, 61, 63, 64, 73, 76, 77, 78}


def owner_for(requirement_id: int) -> str:
    if requirement_id in {29, 30, 31}:
        return "Model Gateway + Agent Core"
    if requirement_id in {15, 18, 22, 23, 48, 49, 51, 52, 55, 60, 63, 71, 72, 73}:
        return "Quality / Finalization"
    if requirement_id in {17, 27, 46, 47, 50}:
        return "Side Effect / Publication"
    if requirement_id in {4, 19, 31, 53, 54, 55}:
        return "Budget / Scheduling"
    if requirement_id in {3, 7, 21, 25, 28, 32, 41, 42, 59, 68, 69, 70, 74, 75, 78, 79, 80}:
        return "Persistence / Recovery"
    if requirement_id in {9, 10, 11, 12, 13, 14, 16, 24, 35, 36, 37, 38, 39, 40, 43, 62}:
        return "Planning / Scheduling"
    if requirement_id in {5, 26, 56, 57, 58}:
        return "Contract Governance"
    return "Agent Core Controller"


def category_for(requirement_id: int) -> str:
    if requirement_id <= 8:
        return "FOUNDATION"
    if requirement_id <= 17:
        return "PLANNING_EXECUTION"
    if requirement_id <= 24:
        return "CONTROL_QUALITY"
    if requirement_id <= 32:
        return "PERSISTENCE_MODEL_DISPATCH"
    if requirement_id <= 43:
        return "STATE_DAG_SCHEDULING"
    if requirement_id <= 50:
        return "INTERRUPT_SIDE_EFFECT_FINAL"
    if requirement_id <= 60:
        return "FAILURE_BUDGET_GOVERNANCE"
    if requirement_id <= 70:
        return "GOAL_COMMAND_CONSISTENCY"
    return "VALIDITY_EVENT_ARTIFACT_TIME"


def requirement_controls() -> str:
    rows = [
        "| Control ID | Category | Owner | Enforcement Ref | Failure Code | Required Tests | Runtime Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for requirement_id, enforcement in enumerate(ENFORCEMENTS, start=1):
        tests = [f"AG-{requirement_id:03d}-UT", f"AG-{requirement_id:03d}-IT"]
        if requirement_id in HIGH_RISK:
            tests.append(f"AG-{requirement_id:03d}-FT")
        if requirement_id in E2E_IDS:
            tests.append(f"AG-{requirement_id:03d}-E2E")
        rows.append(
            "| "
            f"`RC-AG-{requirement_id:03d}` | {category_for(requirement_id)} | {owner_for(requirement_id)} | "
            f"`{enforcement}` | `AG{requirement_id:03d}_VIOLATION` | "
            f"`{', '.join(tests)}` | `EV-AG-{requirement_id:03d}` |"
        )
    return "\n".join(rows)


def p0_p1_sections() -> str:
    return r'''## 39. 完整子状态机 Transition Matrix

AgentRun 的聚合矩阵之外，PlanVersion、StepRun、Action、Interrupt 和 Publication 必须使用独立 Transition Guard。所有转换都写 Transition Record，禁止通过直接 ORM 赋值绕过 Guard。

### 39.1 PlanVersion

| From | Trigger | Guard | To | 原子事实 |
| --- | --- | --- | --- | --- |
| `PROPOSED` | `VALIDATE_PLAN` | Proposal Schema 完整 | `VALIDATING` | ValidationAttempt |
| `VALIDATING` | `VALIDATION_PASS` | DAG、Capability、Budget、Security、Acceptance 全通过 | `ACTIVE` | 激活新版本、Supersede 旧版本、递增 Generation |
| `VALIDATING` | `VALIDATION_REJECT` | Repair 不允许或预算耗尽 | `REJECTED` | ValidationFailure |
| `PROPOSED/VALIDATING` | `GOAL_SUPERSEDED` | GoalVersion 已非 ACTIVE | `INVALIDATED` | InvalidationRecord |
| `ACTIVE` | `NEW_PLAN_ACTIVATED` | Replan Barrier 完成 | `SUPERSEDED` | PlanSwitchRecord |
| `ACTIVE` | `PLAN_SETTLED` | 所有可达 Step 终止且无需 Replan | `COMPLETED` | PlanCompletionRecord |
| `ACTIVE` | `SECURITY_OR_CONTRACT_INVALIDATED` | 继续执行不再合法 | `INVALIDATED` | ControlDecision |

`REJECTED`、`SUPERSEDED`、`COMPLETED` 和 `INVALIDATED` 均为该 PlanVersion 的终态。旧版本不得重新激活。

### 39.2 StepRun Attempt

| From | Trigger | Guard | To | 语义 |
| --- | --- | --- | --- | --- |
| `QUEUED` | `CLAIM_STEP` | Plan ACTIVE、Epoch、Budget、Resource 合法 | `CLAIMED` | 获取 Claim 与 execution_epoch |
| `CLAIMED` | `START_EXECUTION` | Claim 未过期 | `RUNNING` | 记录 started_at |
| `RUNNING` | `WAIT_REQUIRED` | 有持久化 Interrupt/ExternalHandle | `WAITING_CONDITION` | 当前 Attempt 暂停 |
| `WAITING_CONDITION` | `VALID_RESUME` | Goal、Plan、Security、Claim 仍兼容 | `RUNNING` | 同一 Attempt 恢复 |
| `WAITING_CONDITION` | `RESUME_REQUIRES_NEW_ATTEMPT` | Lease、输入或执行上下文已变化 | `OBSOLETE` | 创建 successor StepRun |
| `RUNNING` | `ACCEPTED_RESULT` | Output、Acceptance、Evidence、Validity 全通过 | `COMPLETED` | 不可变 Step Result |
| `RUNNING` | `EXECUTION_FAILED` | 失败事实已提交 | `FAILED` | FailureRecord |
| `FAILED` | `RETRY_DECIDED` | Retry Policy、Budget、Deadline 允许 | `RETRY_SCHEDULED` | 当前 Attempt 终止并创建新 StepRun |
| `RUNNING` | `OUTCOME_UNKNOWN` | 外部事实不可确认 | `UNKNOWN` | 禁止完成与盲目重试 |
| `QUEUED/CLAIMED/WAITING_CONDITION` | `PLAN_SUPERSEDED` | 不再复用 | `OBSOLETE` | Replan Disposition |
| `RUNNING` | `CANCEL_SETTLED` | 可取消且无 UNKNOWN 副作用 | `CANCELLED` | CancellationRecord |

`RETRY_SCHEDULED` 不允许原行回到 `QUEUED`；Retry 必须创建 `attempt_no + 1` 的新 StepRun。`UNKNOWN` 只有在 Reconciliation 提交明确事实后，才允许创建后继 Attempt 或终结 Step。

### 39.3 ActionLifecycleStatus × ActionOutcome

| Lifecycle | 允许 Outcome | 禁止行为 |
| --- | --- | --- |
| `PROPOSED/VALIDATING/PREPARED/WAITING_APPROVAL/CLAIMED` | 空或 `NOT_EXECUTED` | 声称外部成功 |
| `EXECUTING` | 空或 `UNKNOWN` | 直接创建第二次执行 |
| `RECONCILING` | `UNKNOWN` 或 `HUMAN_REQUIRED` | 盲目 Retry |
| `TERMINAL` | `SUCCEEDED`、`FAILED`、`NOT_EXECUTED`、`CANCELLED`、`HUMAN_REQUIRED` | Outcome 为空或继续执行 |

`TERMINAL / SUCCEEDED` 必须同时引用外部 Receipt 和本地 Observation Commit；`HUMAN_REQUIRED` 必须使 StepRun 进入 `WAITING_CONDITION` 或 `BLOCKED`，由 Policy 决定，不得隐式完成。

### 39.4 Interrupt

| From | Trigger | Guard | To |
| --- | --- | --- | --- |
| — | `CREATE_INTERRUPT` | Payload、Schema、Scope、Expiry 合法 | `PENDING` |
| `PENDING` | `VALID_SIGNAL` | 鉴权、幂等、未过期、目标仍有效 | `RESOLVED` |
| `PENDING` | `EXPIRE` | database_now >= expires_at | `EXPIRED` |
| `PENDING` | `RUN_CANCELLED` | Cancellation 生效 | `CANCELLED` |
| `PENDING` | `PLAN_SUPERSEDED` | Step 不再可达 | `OBSOLETE` |

任何非 `PENDING` Interrupt 收到 Signal，只能返回原消费结果或 `STALE_SIGNAL`，不得推进状态。

### 39.5 Publication 与 PublicationAttempt

| From | Trigger | Guard | To |
| --- | --- | --- | --- |
| — | `PREPARE_PUBLICATION` | FinalCandidate 固定、Artifact VALID | `PREPARED` |
| `PREPARED` | `VALIDATE_PUBLICATION` | ResultValidity、Security、Recipient Scope 合法 | `VALIDATING` |
| `VALIDATING` | `APPROVE_PUBLICATION` | Gate 全通过 | `APPROVED` |
| `APPROVED` | `START_DELIVERY` | Idempotency Claim 成功 | `PUBLISHING` |
| `PUBLISHING` | `RECEIPT_CONFIRMED` | Receipt 与 Idempotency Key 匹配 | `PUBLISHED` |
| `PUBLISHING` | `DELIVERY_FAILED` | 外部明确失败 | `FAILED` |
| `PUBLISHED` | `CORRECTION_REPLACE` | 新 Publication 已准备 | `SUPERSEDED` |
| `PUBLISHED` | `CORRECTION_WITHDRAW` | 渠道支持撤回且审批通过 | `WITHDRAWN` |

可重试渠道错误创建新的 `PublicationAttempt`，但保留同一 Publication 和 Idempotency Key；不得把原 `FAILED` Attempt 原地改成成功。Correction 创建新 Decision 和可选新 Publication，不覆盖原 Receipt。

## 40. Final Gate 路由与 RunOutcome Contract

### 40.1 Final Gate Routing

| Gate Result | 下一控制节点 | 版本与边界 |
| --- | --- | --- |
| `PASS` | `ArtifactValidation → Publication` | 固定当前 FinalCandidateVersion |
| `REWRITE` | `FinalSynthesis` | 创建新 FinalCandidateVersion |
| `RETRIEVE_MORE` | `SupplementalRetrieval` | 仅预声明补充边可在同一 Plan；结构变化必须 Replan |
| `REPLAN` | `ReplanBarrier` | 创建新 PlanVersion |
| `PARTIAL` | `PartialDisclosureGate` | 创建披露未完成项的新 CandidateVersion |
| `ABSTAIN` | `OutcomeCommit` | RunOutcome=`ABSTAINED` |
| `REFUSE` | `RefusalRenderer → OutcomeCommit` | RunOutcome=`REFUSED` |
| `BLOCK` | `OutcomeCommit` | RunOutcome=`BLOCKED` |
| `FAIL` | `FailureFinalizer → OutcomeCommit` | RunOutcome=`FAILED` |

Finalization 受独立 Budget 和循环上限控制：

```text
max_final_candidate_versions
max_rewrite_cycles
max_retrieve_more_cycles
max_final_reflection_cycles
finalization_token_budget
finalization_cost_budget
```

达到上限后必须确定性进入 `PARTIAL`、`ABSTAIN`、`REFUSE`、`BLOCK` 或 `FAIL`，禁止无限 Rewrite / Retrieve / Reflection。

### 40.2 RunOutcome

```text
run_outcome_id
run_id
outcome_version
status
task_contract_id
goal_version_id
plan_version_id
objective_outcome_refs
completed_objective_refs
incomplete_objective_refs
failure_refs
evidence_summary_ref
artifact_version_refs
publication_refs
security_summary_ref
budget_settlement_ref
partial_disclosure
abstention_reason
refusal_reason
correction_of_outcome_id
created_at
```

RunOutcome 提交后不可覆盖。事实更正创建 `OutcomeCorrection` 或新的 `outcome_version`，原 Outcome、Publication 和 Receipt 永久保留审计。Run 业务终态与延迟 Budget Settlement 可以分开：Settlement 未完成时保存 `SETTLEMENT_PENDING`，但不得改变已经提交的业务结论。

## 41. LangGraph Adapter Contract

LangGraph 是控制执行框架，不是领域事实 Owner。Zuno 通过 `LangGraphAdapter` 隔离框架语义，Domain 和 Application Service 不导入 LangGraph 类型。

### 41.1 GraphBundle 与线程映射

```text
GraphBundle
    graph_bundle_id
    graph_name
    graph_schema_version
    state_schema_version
    node_contract_version
    supported_langgraph_version_range
    source_commit_sha
    content_hash
    status
    created_at

run_id 1:1 maps to thread_id
thread_id = stable opaque UUID/hash, length < 255
checkpoint namespace:
    zuno/run/{run_id}
    zuno/run/{run_id}/step/{step_run_id}
```

同一 Run 的 Resume 必须使用同一 `thread_id`。新 `thread_id` 表示新 Thread，不能作为原 Run 的恢复。跨 Run 数据必须通过 Domain Store 或受治理 Store，不通过 Checkpoint namespace 隐式共享。

### 41.2 Interrupt Node Rules

```text
每个 Node invocation 最多调用一次 interrupt()
Resume 从包含 interrupt() 的 Node 开头重新执行
interrupt() 前的领域写入必须幂等
interrupt() 前禁止未持有 IdempotencyClaim 的外部副作用
Resume 后重新读取 PreparedAction、Approval、Policy、Security Epoch 和 ResultValidity
Node 本地变量不是恢复事实
多 Interrupt Resume 必须按 interrupt_id 映射响应
```

禁止在同一 Node 内使用 `while True + interrupt()` 反复提问；无效输入写回状态后通过条件边重新进入 Node。

### 41.3 Retry、Timeout 与 Error Handler 分层

| 层 | 允许范围 | 禁止 |
| --- | --- | --- |
| LangGraph Node Retry | 纯计算、只读且幂等、无领域 Attempt 语义的瞬时失败 | Tool 副作用、Action/Step 业务 Retry |
| LangGraph Timeout | Async Node 单 Attempt 的 run/idle timeout | 将 Timeout 自动等同于领域失败终态 |
| LangGraph Error Handler | 转换为 FailureProposal、RunCommand 或确定性路由 | 直接修改领域终态、自动 Compensation |
| Zuno Action Retry | 创建新 Action Attempt，记录 Usage、Budget、Idempotency | 复用旧 execution_epoch 执行 |
| Zuno Step Retry | 创建新 StepRun Attempt | 原 StepRun 回到 QUEUED |
| Zuno Replan | 新 PlanVersion | 伪装成 Retry |

Adapter 必须显式关闭副作用 Node 的框架自动 Retry。Node Timeout 产生结构化技术 Failure，由 Zuno Policy 决定 Retry、Reconcile、Fallback 或 Replan。框架 Error Handler 只有在框架 Retry 耗尽后运行，但它只能产生 Proposal/Command。

### 41.4 Infrastructure Drain

基础设施滚动升级、缩容或进程退出使用 `InfrastructureDrainProtocol`，不等于用户 Cancellation：

```text
停止新的 Superstep / Dispatch
允许不可中断 Node 到安全边界
写 DrainMarker 和最新合法 Checkpoint
释放 Controller / Worker Lease
不改变 AgentRun 业务终态
恢复时使用原 thread_id、GraphBundle 与 Generation 校验
```

无法在 Drain Deadline 前到达安全边界时，标记 Recovery Required；不得把进程终止冒充 `CANCELLED`。

### 41.5 Streaming Projection

LangGraph 原始 `values`、`updates`、`tasks`、`debug` 和完整消息流仅供受控内部诊断。Product Surface 只能消费 Zuno 投影：

```text
RunStreamEvent
    stream_event_id
    run_id
    sequence_no
    projection_type
    content_ref
    provisional
    retracts_event_ids
    interrupt_refs
    checkpoint_ref
    security_classification
    created_at

ProjectionType
    PROGRESS
    SAFE_PROVISIONAL_CONTENT
    INTERRUPT
    PUBLICATION
    RETRACTION
```

禁止流出完整 Graph State、Prompt、凭证、隐藏思维链、未脱敏 Observation 或未授权并行分支内容。断线恢复按 `sequence_no`，Provisional Content 必须可撤回，正式结果只由 PublicationProjection 表示。

### 41.6 Checkpoint Retention 与框架参考

Checkpoint 是 thread-scoped 控制状态，必须配置 Retention、Pruning 和 Legal Hold：终态 Run 保留最近合法 Checkpoint、关键 Interrupt/Publication Checkpoint 和 Hash；调试 Checkpoint 按 Policy 到期删除；Domain Audit 不随 Checkpoint 删除。

框架适配依据官方文档，并由 Program 固定实际依赖版本：

- [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangGraph Fault tolerance](https://docs.langchain.com/oss/python/langgraph/fault-tolerance)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
- [LangGraph Backward compatibility](https://docs.langchain.com/oss/python/langgraph/backward-compatibility)

## 42. ModelCapabilityProfile 与 StepFeasibility

`ModelCapabilityProfile` 的事实 Owner 是 Model Gateway；Agent Core 在 Plan Validation 时读取不可变 Profile Snapshot，不自行猜测模型能力。

```text
ModelCapabilityProfile
    profile_id
    model_role
    model_ref
    supported_input_modalities
    supported_output_contracts
    structured_output_reliability
    tool_calling_support
    context_window
    reasoning_class
    latency_class
    cost_class
    data_residency
    security_classification
    max_step_complexity
    profile_version
    valid_from
```

```text
StepFeasibilityDecision
    feasibility_decision_id
    plan_version_id
    step_definition_id
    executable
    selected_model_role
    capability_profile_ref
    fallback_profile_refs
    estimated_context_tokens
    estimated_cost
    complexity_score
    unmet_requirements
    reason_codes
    created_at
```

Plan Validator 必须拒绝：单 Step 超过执行器复杂度上限、没有模型支持输出 Contract、数据等级与模型安全/驻留不兼容、预计 Context 超出窗口、预算不支持、必要 Tool Calling 或输入模态不存在。Planner 只能根据可用 Profile 生成 Step；Profile 变化不原地修改 Active Plan，必要时触发 Replan。

## 43. Resource Conflict Matrix

| Existing Claim | Requested Claim | 默认结果 |
| --- | --- | --- |
| `READ_SHARED` | `READ_SHARED` | 允许 |
| `READ_SHARED` | `WRITE_EXCLUSIVE` | 等待或拒绝 |
| `WRITE_EXCLUSIVE` | 任意同资源 Claim | 等待或拒绝 |
| `APPEND_SERIALIZED` | `APPEND_SERIALIZED` | 按数据库序列串行 |
| `CAPACITY_SHARED` | `CAPACITY_SHARED` | 容量足够时允许并原子扣减 |
| `NON_PREEMPTIBLE` | 任意冲突 Claim | 等待，不抢占 |

资源 ID 必须规范化并支持层级冲突，例如 Account > Mailbox > Message。父资源 `WRITE_EXCLUSIVE` 与任意子资源冲突；子资源 Claim 是否阻止父资源请求由 Hierarchy Policy 确定。多资源固定排序获取，部分成功必须释放；等待超过阈值产生 `RESOURCE_STARVATION`，Priority Inversion 通过 Priority Inheritance 或拒绝升级解决，不能无限等待。

## 44. Replay、Recovery、Reexecution 与 Simulation Fork

```text
CONTROL_REPLAY
    从已提交 Domain Fact 与 Event 重建 Graph 控制状态。
    禁止重新调用模型、检索、Tool 或外部副作用。

RECOVERY
    修复 Domain/Checkpoint/Dispatch/Receipt 不一致并恢复原 Run。
    必须使用 Generation、Fencing 和 ReconciliationRecord。

REEXECUTION
    创建新的 StepRun / ActionRun Attempt。
    使用新 execution_epoch、Budget Reservation 和必要 IdempotencyClaim。

SIMULATION_FORK
    从历史 Snapshot 创建新 Run 和新 thread_id。
    默认禁止外部副作用，不能修改原 Run。
```

任何“Replay”命令必须显式声明 mode；不允许用 CONTROL_REPLAY 名义重新执行历史副作用。Time-travel 调试默认只读；执行型 Fork 必须创建新 Run、重新授权并重新预算。

## 45. Graph、State 与长运行版本升级

LangGraph 对恢复中的 Thread 使用当前部署 Graph 代码，因此 Zuno 必须显式治理兼容性：

```text
Run 创建时固定 graph_bundle_id、graph_schema_version、state_schema_version、flow_version
新增 State 字段必须 Optional / 有默认值
Node 或 State 字段重命名采用 add → dual support → drain → remove
存在停在旧 Node 的 Thread 时禁止删除该 Node
破坏性升级需要 StateMigrator 和 Migration Test
副作用 EXECUTING / UNKNOWN 的 Run 默认禁止跨 Bundle Migration
未知 Bundle / State Version → BLOCKED，不猜测恢复
```

部署策略二选一并由 Program 明确：

```text
PINNED_BUNDLE
    保留旧 GraphBundle 直到关联 Run 全部终止。

COMPATIBLE_LATEST
    新代码保持旧 Checkpoint 技术与业务兼容，按 flow_version 分支。
```

`StateMigrationRecord` 保存 run_id、from/to bundle、from/to state version、migration_id、before/after hash、status、failure_ref、approved_by 和 created_at。迁移失败不得修改原 Checkpoint，必须可回滚到最后合法 Generation。

## 46. 逐条 Requirement Control Registry

以下 80 条 Control 与 Part VIII 的 80 条 Requirement 一一对应；每个 Control 都有稳定 Owner、Enforcement、Failure Code、Test ID 和 Evidence Key。Program 可以增加测试，但不得删除基础映射。

''' + requirement_controls() + r'''

## 47. 架构完成与 Program 入口门槛

生成 Agent Core 实现 Program 前必须满足：

```text
所有子状态机有合法/非法转换测试要求
Final Gate 每个输出有唯一确定路由
RunOutcome、Correction 与 Budget Settlement 边界明确
LangGraph Adapter 不绕过领域 Retry、Interrupt、Security 和 Publication
ModelCapabilityProfile 能产生确定性 StepFeasibilityDecision
每个 Requirement 存在 RC-AG、Test ID 与 Evidence Key
正式文档与 Agent 镜像字节级一致
```

这些条件只证明 Target 可实施；代码、Migration、故障注入、E2E、Trace、Eval 完成前仍不得声明 implementation available 或 production ready。

---
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def update_document() -> str:
    text = FORMAL.read_text(encoding="utf-8")
    if SECTION_MARKER not in text:
        text = replace_once(text, PART_VI, p0_p1_sections() + "\n" + PART_VI, "P0/P1 insertion")

    text = text.replace(
        "ExecutionContextSnapshot\nEffectivePolicySnapshot\nAgentRun",
        "ExecutionContextSnapshot\nEffectivePolicySnapshot\nGraphBundle\nModelCapabilityProfileRef\nStepFeasibilityDecision\nRunStreamEvent\nStateMigrationRecord\nAgentRun",
        1,
    )
    text = text.replace(
        "DeliveryReceipt\nRunOutcome\nBudgetConsumption",
        "DeliveryReceipt\nRunOutcome\nOutcomeCorrection\nBudgetConsumption",
        1,
    )
    text = text.replace(
        "├── agent_step_acceptance_criteria",
        "├── agent_step_acceptance_criteria\n├── agent_step_feasibility_decisions\n└── agent_graph_bundles",
        1,
    )
    text = text.replace(
        "├── agent_delivery_receipts\n└── agent_run_outcomes",
        "├── agent_delivery_receipts\n├── agent_run_outcomes\n└── agent_outcome_corrections",
        1,
    )
    text = text.replace(
        "├── agent_runtime_events\n└── agent_outbox_events",
        "├── agent_runtime_events\n├── agent_run_stream_events\n├── agent_state_migration_records\n└── agent_outbox_events",
        1,
    )
    text = text.replace(
        "├── graph/run/{state,nodes,routing,builder}.py\n    ├── graph/step/{state,nodes,routing,builder}.py",
        "├── graph/run/{state,nodes,routing,builder}.py\n    ├── graph/step/{state,nodes,routing,builder}.py\n    ├── graph/adapter/{bundle,checkpoint,interrupt,retry,streaming,upgrade}.py",
        1,
    )
    text = text.replace(
        "├── planning/{analyzer,validator,repair,planners/}",
        "├── planning/{analyzer,validator,repair,capability_profile,feasibility,planners/}",
        1,
    )

    old_control = """ControlDecision
    control_decision_id
    run_id
    command_refs
    selected_command_id
    precedence_rule
    from_status
    to_status
    actions
    rejected_command_refs
    controller_epoch
    domain_generation
    created_at"""
    new_control = """ControlDecision
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
    created_at"""
    if old_control in text:
        text = text.replace(old_control, new_control, 1)

    text = text.replace(
        "状态：CLAIMED、EXECUTING、SUCCEEDED、FAILED、UNKNOWN、RECONCILED。",
        "状态：CLAIMED、EXECUTING、SUCCEEDED、FAILED、UNKNOWN、CLOSED。`CLOSED` 只表示 Claim 生命周期关闭，Action 业务结果仍以 ActionOutcome 为准。",
        1,
    )
    return text


def update_verifier() -> None:
    text = VERIFIER.read_text(encoding="utf-8")
    required_anchor = '    "Transition Matrix",\n'
    required_additions = '''    "PlanVersion Transition Matrix",
    "Final Gate Routing",
    "RunOutcome Contract",
    "LangGraph Adapter Contract",
    "InfrastructureDrainProtocol",
    "RunStreamEvent",
    "ModelCapabilityProfile",
    "StepFeasibilityDecision",
    "Resource Conflict Matrix",
    "CONTROL_REPLAY",
    "SIMULATION_FORK",
    "StateMigrationRecord",
    "逐条 Requirement Control Registry",
'''
    if '    "LangGraph Adapter Contract",\n' not in text:
        text = replace_once(text, required_anchor, required_anchor + required_additions, "verifier required terms")

    table_anchor = '    "agent_budget_settlements",\n'
    table_additions = '''    "agent_step_feasibility_decisions",
    "agent_graph_bundles",
    "agent_run_stream_events",
    "agent_state_migration_records",
    "agent_outcome_corrections",
'''
    if '    "agent_step_feasibility_decisions",\n' not in text:
        text = replace_once(text, table_anchor, table_anchor + table_additions, "verifier required tables")

    forbidden_anchor = '    "SUCCEEDED\\nFAILED\\nUNKNOWN\\nRECONCILING\\nRECONCILED",\n'
    forbidden_addition = '    "状态：CLAIMED、EXECUTING、SUCCEEDED、FAILED、UNKNOWN、RECONCILED。",\n'
    if forbidden_addition not in text:
        text = replace_once(text, forbidden_anchor, forbidden_anchor + forbidden_addition, "verifier forbidden terms")

    check_anchor = '''    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\\d{3})", formal)]
    if sorted(ids) != list(range(1, 81)):
        errors.append("Agent Core document must define ARCH-AGENT-001 through ARCH-AGENT-080 exactly once")
'''
    extended_check = check_anchor + '''
    controls = [int(value) for value in re.findall(r"RC-AG-(\\d{3})", formal)]
    if sorted(controls) != list(range(1, 81)):
        errors.append("Agent Core document must map RC-AG-001 through RC-AG-080 exactly once")

    for matrix in [
        "### 39.1 PlanVersion",
        "### 39.2 StepRun Attempt",
        "### 39.3 ActionLifecycleStatus × ActionOutcome",
        "### 39.4 Interrupt",
        "### 39.5 Publication 与 PublicationAttempt",
    ]:
        if matrix not in formal:
            errors.append(f"Agent Core document missing state matrix: {matrix}")

    for route in [
        "`PASS` | `ArtifactValidation → Publication`",
        "`REWRITE` | `FinalSynthesis`",
        "`RETRIEVE_MORE` | `SupplementalRetrieval`",
        "`REPLAN` | `ReplanBarrier`",
        "`ABSTAIN` | `OutcomeCommit`",
    ]:
        if route not in formal:
            errors.append(f"Final Gate routing missing: {route}")

    for adapter_term in [
        "每个 Node invocation 最多调用一次 interrupt()",
        "Resume 从包含 interrupt() 的 Node 开头重新执行",
        "LangGraph Node Retry",
        "Infrastructure Drain",
        "thread_id = stable opaque UUID/hash, length < 255",
        "Checkpoint Retention",
    ]:
        if adapter_term not in formal:
            errors.append(f"LangGraph Adapter Contract missing: {adapter_term}")
'''
    if "controls = [int(value)" not in text:
        text = replace_once(text, check_anchor, extended_check, "verifier semantic checks")

    VERIFIER.write_text(text, encoding="utf-8", newline="\n")


def update_tests() -> None:
    text = TESTS.read_text(encoding="utf-8")
    if "test_all_substate_transition_matrices_are_normative" not in text:
        text += r'''


def test_all_substate_transition_matrices_are_normative() -> None:
    content = _content()
    for heading in [
        "### 39.1 PlanVersion",
        "### 39.2 StepRun Attempt",
        "### 39.3 ActionLifecycleStatus × ActionOutcome",
        "### 39.4 Interrupt",
        "### 39.5 Publication 与 PublicationAttempt",
    ]:
        assert heading in content
    assert "RETRY_SCHEDULED` 不允许原行回到 `QUEUED" in content
    assert "FAILED` Attempt 原地改成成功" in content


def test_final_gate_and_run_outcome_are_closed() -> None:
    content = _content()
    for term in [
        "Final Gate Routing",
        "max_final_candidate_versions",
        "max_retrieve_more_cycles",
        "objective_outcome_refs",
        "budget_settlement_ref",
        "OutcomeCorrection",
    ]:
        assert term in content


def test_langgraph_adapter_boundaries_are_explicit() -> None:
    content = _content()
    for term in [
        "LangGraph Adapter Contract",
        "每个 Node invocation 最多调用一次 interrupt()",
        "Resume 从包含 interrupt() 的 Node 开头重新执行",
        "LangGraph Node Retry",
        "InfrastructureDrainProtocol",
        "RunStreamEvent",
        "Checkpoint Retention",
        "thread_id = stable opaque UUID/hash, length < 255",
    ]:
        assert term in content


def test_model_feasibility_resource_replay_and_upgrade_are_defined() -> None:
    content = _content()
    for term in [
        "ModelCapabilityProfile",
        "StepFeasibilityDecision",
        "Resource Conflict Matrix",
        "CONTROL_REPLAY",
        "SIMULATION_FORK",
        "StateMigrationRecord",
        "PINNED_BUNDLE",
        "COMPATIBLE_LATEST",
    ]:
        assert term in content


def test_every_requirement_has_explicit_control_test_and_evidence() -> None:
    content = _content()
    controls = [int(value) for value in re.findall(r"RC-AG-(\d{3})", content)]
    assert sorted(controls) == list(range(1, 81))
    for requirement_id in range(1, 81):
        assert f"AG-{requirement_id:03d}-UT" in content
        assert f"AG-{requirement_id:03d}-IT" in content
        assert f"EV-AG-{requirement_id:03d}" in content
'''
    TESTS.write_text(text, encoding="utf-8", newline="\n")


def update_agent_system() -> None:
    text = AGENT_SYSTEM.read_text(encoding="utf-8")
    anchor = '''            "Requirement Enforcement Matrix",
            "ARCH-AGENT-080",'''
    replacement = '''            "Requirement Enforcement Matrix",
            "LangGraph Adapter Contract",
            "ModelCapabilityProfile",
            "StepFeasibilityDecision",
            "RC-AG-080",
            "ARCH-AGENT-080",'''
    if "RC-AG-080" not in text:
        text = replace_once(text, anchor, replacement, "Agent System required phrases")
    AGENT_SYSTEM.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    document = update_document()
    FORMAL.write_text(document.rstrip() + "\n", encoding="utf-8", newline="\n")
    MIRROR.write_text(document.rstrip() + "\n", encoding="utf-8", newline="\n")
    update_verifier()
    update_tests()
    update_agent_system()
    print("Agent Core remaining P0/P1 architecture contracts completed.")


if __name__ == "__main__":
    main()
