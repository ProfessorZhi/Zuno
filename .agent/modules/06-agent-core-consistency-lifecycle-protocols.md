# 06 Agent Core / Planning & Control：一致性与生命周期协议

updated: 2026-07-12  
status: normative-target-consistency-protocols  
module_number: 06  
formal_path: `docs/modules/06-agent-core-consistency-lifecycle-protocols.md`  
agent_mirror: `.agent/modules/06-agent-core-consistency-lifecycle-protocols.md`  
parent_design: `docs/modules/06-agent-core-planning-control.md`  
control_protocols: `docs/modules/06-agent-core-control-protocols.md`

> 本文补齐 Agent Core Target 中跨阶段、跨存储和跨模块最容易产生歧义的八组协议：TaskContract 与 GoalVersion、控制命令仲裁、Domain/Checkpoint 一致性、ResultValidity、Event/Outbox、Artifact 生命周期、Orphan Reconciliation 和时间语义。
>
> 本文只描述理想 Target，不讨论当前实现或具体迁移计划。

---

# 1. TaskContract、GoalVersion 与 Objective

## 1.1 为什么不能只有 goal_summary

用户可能追加材料、修改约束、改变输出格式或改变核心目标。如果所有变化都覆盖同一个 goal_summary，系统无法判断原 Plan 针对哪个目标、已完成 Step 是否仍有效、新消息是 Resume、Replan 还是新任务，以及 PARTIAL 到底完成了什么。

## 1.2 TaskContract

```text
TaskContract
    task_contract_id
    run_id
    workspace_id
    requester_identity
    initial_request_ref
    active_goal_version_id
    contract_version
    status
    created_at
```

TaskContract 是一个 Run 的目标聚合根，不保存隐藏思维链。

## 1.3 GoalVersion

```text
GoalVersion
    goal_version_id
    task_contract_id
    version_no
    parent_goal_version_id
    change_type
    change_reason
    objective_refs
    user_constraint_refs
    output_requirement_refs
    completion_policy_ref
    content_hash
    status
    created_by
    created_at
    activated_at
    superseded_at
```

状态：

```text
PROPOSED
VALIDATING
ACTIVE
SUPERSEDED
REJECTED
INVALIDATED
```

同一 TaskContract 同时最多一个 ACTIVE GoalVersion。

## 1.4 ObjectiveDefinition 与 ObjectiveOutcome

```text
ObjectiveDefinition
    objective_id
    goal_version_id
    logical_objective_id
    title
    description
    criticality
    acceptance_contract
    required_evidence
    parent_objective_id
    sequence_no
```

Criticality：REQUIRED、IMPORTANT、OPTIONAL。

```text
ObjectiveOutcome
    objective_outcome_id
    run_id
    goal_version_id
    objective_id
    status
    satisfied_by_refs
    missing_requirements
    failure_refs
    result_validity
    created_at
```

Outcome 状态：SATISFIED、PARTIALLY_SATISFIED、UNSATISFIED、SKIPPED、REFUSED、INVALIDATED。

RunOutcome 的 completed/incomplete objectives 必须引用 ObjectiveOutcome，不得只保存自由文本。

## 1.5 用户输入分类

```text
SUPPLEMENTAL_INPUT
CLARIFICATION_RESPONSE
CONSTRAINT_CHANGE
OUTPUT_CONTRACT_CHANGE
OBJECTIVE_CHANGE
CANCELLATION_REQUEST
NEW_TASK
```

- SUPPLEMENTAL_INPUT：增加材料，不改变目标结构；
- CLARIFICATION_RESPONSE：解决已有 Interrupt；
- CONSTRAINT_CHANGE：修改时间、来源、安全或业务约束；
- OUTPUT_CONTRACT_CHANGE：改变格式、渠道或 Artifact 类型；
- OBJECTIVE_CHANGE：新增、删除或改变核心 Objective；
- NEW_TASK：与当前 Run 无法保持因果连续性，应创建新 Run。

Constraint、Output Contract 或 Objective 的实质变化创建新 GoalVersion，并要求 Replan。

## 1.6 GoalVersion 与 PlanVersion

```text
GoalVersion 1
├── PlanVersion 1
└── PlanVersion 2

GoalVersion 2
└── PlanVersion 3
```

PlanVersion 必须绑定明确 GoalVersion，旧 GoalVersion 的 Plan 不得重新激活。

---

# 2. 控制命令仲裁与 Policy Precedence

## 2.1 为什么需要统一仲裁

并行 Run 可能同时收到用户取消、安全撤权、审批通过、Tool 回执、Deadline、ReplanRequest、Budget Exhaustion 和 Final Gate 决策。如果不同服务直接写 Run 状态，会产生终态竞争和已取消任务继续发布等问题。

## 2.2 RunCommand

```text
command_id
run_id
command_type
producer
producer_authority
payload_ref
idempotency_key
observed_at
received_at
expected_controller_epoch
status
```

CommandType：

```text
SECURITY_REVOKE
CANCEL
EXPIRE
SIDE_EFFECT_RECONCILE
SIGNAL_RECEIVED
APPROVAL_DECIDED
BUDGET_LIMIT_REACHED
REPLAN_REQUESTED
QUALITY_DECISION
SCHEDULE_TICK
```

状态：RECEIVED、VALIDATED、APPLIED、REJECTED、OBSOLETE、DUPLICATE。

## 2.3 Per-run 串行控制通道

同一 Run 的命令必须由 Single Controller 按 command_sequence_no 串行处理：

```text
接收 Command
→ 幂等校验
→ 权限与 Epoch 校验
→ 排序与仲裁
→ 生成 ControlDecision
→ 领域事务中应用
→ 记录 Event / Outbox
```

其他模块不得直接修改 Run 终态。

## 2.4 默认优先级

```text
1. SECURITY_REVOKE
2. CANCEL
3. EXPIRE / DEADLINE
4. SIDE_EFFECT_RECONCILE
5. SIGNAL_RECEIVED / APPROVAL_DECIDED
6. BUDGET_LIMIT_REACHED
7. REPLAN_REQUESTED
8. QUALITY_DECISION
9. SCHEDULE_TICK
```

原则：Security fail-closed；Cancellation 不抹掉已发生副作用；Deadline 不跳过 UNKNOWN Reconcile；Approval 不能覆盖之后的 Security Revocation；Replan 不能覆盖更高优先级终止命令；Quality Decision 不得绕过 Budget、Security 或 Cancellation。

## 2.5 竞态示例

审批与撤权同时到达：Security 优先，Approval 标记 OBSOLETE，PreparedAction 不执行。

取消与 Tool 成功回执同时到达：先确认副作用事实，ActionRun=SUCCEEDED，然后 Run 进入 CANCELLING，停止后续工作，Outcome 为 CANCELLED 或 PARTIAL。

Deadline 与 Publication 成功同时发生：DeliveryReceipt 事实不能回滚，RunOutcome 记录超期警告，不重复发送。

## 2.6 ControlDecision

```text
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
created_at
```

---

# 3. Domain Store 与 LangGraph Checkpoint 一致性

## 3.1 边界

```text
Domain Store
    保存已发生的业务事实、领域状态和审计记录。

LangGraph Checkpointer
    保存图从哪个节点、Channel 和 Pending Send/Interrupt 继续。
```

两者不能使用分布式事务假装原子，必须使用可恢复的一致性协议。

## 3.2 Generation

每个 AgentRun 保存 domain_generation 和 checkpoint_generation。每次改变控制流依赖的领域事实时，domain_generation 单调递增。

Checkpoint 保存：

```text
run_id
domain_generation
checkpoint_generation
graph_schema_version
state_schema_version
node_ref
channel_state_hash
created_at
```

## 3.3 Control Commit Protocol

```text
1. 校验 controller_epoch
2. PostgreSQL 事务提交领域事实
3. 递增 domain_generation
4. 写 DomainCommitMarker
5. COMMIT
6. Checkpointer 写入引用该 domain_generation 的图状态
7. 成功后更新 checkpoint_generation / receipt
```

外部副作用只能在所需 Domain Commit 已完成后启动。

## 3.4 崩溃矩阵

Domain Commit 成功、Checkpoint 失败：Domain Generation > Checkpoint Generation，PostgreSQL 事实有效，Recovery 从领域事实重建控制状态并写新 Checkpoint。

Checkpoint 写成功、Domain Commit 失败：Checkpoint 引用不存在的 Generation，标记 INVALID_AHEAD，回退到最后合法 Domain Generation。

Dispatch Commit 成功、Send 前崩溃：DispatchItem=COMMITTED/UNSENT，DispatchReconciler 重放 Send，Worker 使用 execution_epoch 和 idempotency 去重。

External Action 成功、Observation Commit 失败：ActionRun/IdempotencyClaim=UNKNOWN，先 Reconcile 外部 Receipt，不能直接再次执行。

## 3.5 RecoveryWatermark

```text
RecoveryWatermark
    run_id
    last_valid_domain_generation
    last_valid_checkpoint_generation
    last_reconciled_event_sequence
    updated_at
```

恢复完成前，Run 不进入正常 Scheduling。

## 3.6 禁止

```text
仅根据 Graph Node 判断副作用是否执行
把完整领域对象复制进 Checkpoint 作为第二事实源
Checkpoint 失败后继续下一个副作用
忽略 Generation 差异
用模型猜测恢复位置
```

---

# 4. ResultValidity 与污染传播

## 4.1 状态

```text
VALID
STALE
REVOKED
TAINTED
SUPERSEDED
UNKNOWN_VALIDITY
```

- VALID：当前 Snapshot、权限、Contract 和 Policy 下可用；
- STALE：来源或 Snapshot 过期；
- REVOKED：权限、来源或政策明确撤销；
- TAINTED：依赖了无效或冲突未解决的上游；
- SUPERSEDED：有更新版本取代；
- UNKNOWN_VALIDITY：无法确认，高风险场景 fail-closed。

## 4.2 ResultValidityRecord

```text
validity_record_id
subject_type
subject_id
status
reason_code
source_change_ref
security_epoch
knowledge_snapshot_ref
policy_version
valid_from
valid_until
supersedes_record_id
created_at
```

## 4.3 污染传播

```text
Evidence
→ Observation
→ StepResult
→ BranchResult
→ JoinResult
→ FinalCandidate
→ ArtifactVersion
→ Publication
```

REVOKED 上游默认使依赖结果 TAINTED；STALE 是否传播由 AnswerPolicy 决定；SUPERSEDED 不影响历史审计，但禁止新 Publication 引用旧版本；UNKNOWN_VALIDITY 在 Strict Grounded 场景不可发布。

## 4.4 撤权时点

Final Gate 前：标记结果 TAINTED，重新计算 Objective Coverage，触发重新检索、Replan、Partial 或 Abstain。

Final Gate 后、Publication 前：Publication Gate 重新校验 ResultValidity，TAINTED/REVOKED 时禁止发布并使 Candidate INVALIDATED。

Publication 后：创建 PublicationCorrectionDecision，根据渠道能力选择 WITHDRAW、REPLACE、ANNOTATE 或 NOTIFY，保留原 Publication 与 Receipt 审计事实。

## 4.5 Result Reuse

Reuse 前重新检查 ResultValidity、Security Scope、GoalVersion、KnowledgeSnapshot、Artifact 可访问性、Evidence 和 Output Contract。

---

# 5. Domain Event、Outbox 与交付语义

## 5.1 事件分类

```text
DomainEvent
RuntimeProgressEvent
AuditEvent
IntegrationEvent
PublicationEvent
```

Trace Span 和 Metric 不是 Domain Event。

## 5.2 Event Envelope

```text
event_id
event_type
event_version
run_id
workspace_id
sequence_no
correlation_id
causation_id
producer
occurred_at
recorded_at
payload_ref
payload_schema_hash
security_classification
```

## 5.3 排序与投递

```text
Outbox 提供 at-least-once delivery
同一 run_id 内按 sequence_no 有序
跨 Run 不保证全局顺序
消费者按 event_id 幂等
事件可以重复但不能丢失已提交领域事实
```

## 5.4 Outbox 状态

```text
PENDING
CLAIMED
PUBLISHED
RETRY_SCHEDULED
DEAD_LETTER
```

字段：outbox_event_id、event_id、partition_key、status、claim_token、claimed_at、claim_expires_at、attempt_count、next_attempt_at、published_at、last_failure_ref。

Publisher 使用 `FOR UPDATE SKIP LOCKED` Claim。Claim 到期后可重新抢占，旧 Publisher 的提交通过 claim_token 拒绝。超过最大 Attempt 进入 DEAD_LETTER，并触发告警和人工处置。

消费者必须按 event_id 幂等，不把 RuntimeProgressEvent 当成完成事实，不基于重复消息累计业务计数。

Integration Event 发出前按消费者执行最小化和脱敏；任何 Event 不保存隐藏思维链或不必要凭证。

---

# 6. Artifact 生命周期

## 6.1 ArtifactCandidate

```text
artifact_candidate_id
run_id
final_candidate_id
artifact_type
content_ref
content_hash
schema_version
created_by
created_at
```

Candidate 是未验证草稿，不能作为正式版本。

## 6.2 ArtifactVersion

```text
artifact_version_id
artifact_logical_id
version_no
source_candidate_id
content_ref
content_hash
format
status
result_validity
created_at
superseded_at
```

状态：DRAFT、VALIDATING、VALID、INVALID、SUPERSEDED、PUBLISHED、WITHDRAWN。

## 6.3 ArtifactValidation

```text
artifact_validation_id
artifact_version_id
validator_type
contract_version
checks
status
failure_refs
created_at
```

检查包括 Schema/MIME、内容完整性、引用与 SourceSpan、敏感信息、安全范围、格式可打开性、公式/图表/代码测试。

Rewrite 创建新 ArtifactVersion，不覆盖旧版本。历史版本保留审计，新 Publication 只能绑定 VALID 且未 SUPERSEDED 的版本。

## 6.4 Publication Binding

```text
Publication
└── PublicationArtifactBinding[]
    ├── artifact_version_id
    ├── channel_representation
    └── delivery_ref
```

同一个 ArtifactVersion 可发布到多个渠道，但每个 Publication 有独立 Idempotency Key 和 DeliveryReceipt。

## 6.5 Retention

RetentionPolicy 区分 Draft、Invalid、Published、Withdrawn、Security-sensitive Artifact 和 Debug Bundle。删除 Object Store Payload 前保留 Hash、Metadata、审计和 Tombstone。

---

# 7. Orphan Recovery 与后台 Reconciler

## 7.1 通用 Contract

```text
reconciler_name
scan_predicate
claim_scope
claim_token
fencing_epoch
batch_size
retry_policy
human_escalation_policy
metric_names
```

通用流程：扫描候选 → Claim → 重读最新事实 → 校验 Fencing → 幂等修复 → 提交 ReconciliationRecord → 释放 Claim。

## 7.2 Reconciler

```text
RunOrphanReconciler
    非终态 Run 长时间无 Controller Heartbeat；接管、恢复或 Block。

DispatchReconciler
    Dispatch 已提交但未 Send，或 Send 后无 Worker Claim；重放或过期取消。

StepLeaseReconciler
    Step Lease 过期；安全时重新 Claim，有副作用风险时进入 UNKNOWN。

UnknownActionReconciler
    查询外部事实，提交 SUCCEEDED、FAILED、RECONCILED 或 HUMAN_REQUIRED。

InterruptExpiryReconciler
    PENDING Interrupt 到期；重新请求、Replan、Block 或 Run EXPIRED。

PublicationReconciler
    PUBLISHING 无 Receipt；查询渠道状态、确认后重试或人工核对。

OutboxReconciler
    Claim 过期、Attempt 超限或 DEAD_LETTER；重新 Claim、告警或人工处置。

BudgetReservationReconciler
    Run/Step 已终止但 Reservation 未释放；结算并释放剩余 Budget。
```

## 7.3 ReconciliationRecord

```text
reconciliation_id
subject_type
subject_id
reconciler_name
before_state
action
after_state
claim_token
fencing_epoch
failure_ref
created_at
```

---

# 8. 时间语义

## 8.1 时间类型

```text
Business Timestamp
    持久化领域事实时间，统一 UTC。

Deadline / Expiry
    绝对 UTC 时间。

Duration
    使用进程 monotonic clock 测量。

Lease Time
    以数据库时间为权威。

Display Time
    按用户时区展示，不参与内部比较。
```

Lease、Claim、Expiry 和 Deadline 的持久化比较使用数据库时间，不依赖 Worker 本地时钟。

## 8.2 Clock Skew

保存 clock_skew_observed_ms 和 clock_skew_threshold_ms。超过阈值时禁止新的 Lease-sensitive 副作用、记录 Audit/Metric、Worker 退出或等待同步，并且不延长已有 Lease。

## 8.3 Deadline

Deadline 是绝对时间，Resume 后不重置：

```text
remaining_time = deadline_at - database_now
```

到期通过 RunCommand EXPIRE 进入统一仲裁。

## 8.4 Waiting 与 Budget

BudgetPolicy 明确：

```text
wall_clock_includes_user_wait
wall_clock_includes_approval_wait
wall_clock_includes_external_job_wait
active_compute_budget
```

默认 Run TTL 包含等待；Active Compute Budget 不包含等待；Approval 和 Signal 有独立 expires_at；Deadline 是否暂停必须由明确产品 Policy 决定。

## 8.5 Event Time

每个事件保存 occurred_at 和 recorded_at。领域排序以同一 Run 的 sequence_no 为准，不使用外部发生时间推断顺序。

---

# 9. Requirement IDs

| ID | Requirement |
| --- | --- |
| `ARCH-AGENT-061` | 每个 Run 必须使用版本化 TaskContract 与 GoalVersion |
| `ARCH-AGENT-062` | PlanVersion 必须绑定明确 GoalVersion |
| `ARCH-AGENT-063` | ObjectiveDefinition 与 ObjectiveOutcome 必须结构化并驱动 PARTIAL |
| `ARCH-AGENT-064` | 用户新输入必须分类为补充、澄清、约束、输出、目标变化或新任务 |
| `ARCH-AGENT-065` | 同一 Run 的控制命令必须经 Single Controller 串行仲裁 |
| `ARCH-AGENT-066` | Security、Cancellation、Deadline、Reconcile、Approval、Budget、Replan 和 Quality 必须有确定优先级 |
| `ARCH-AGENT-067` | 所有 ControlDecision 必须可审计并携带 Epoch 与 Generation |
| `ARCH-AGENT-068` | Domain Store 与 Checkpoint 必须使用 Generation 和 RecoveryWatermark 协调 |
| `ARCH-AGENT-069` | Checkpoint 不得引用未提交 Domain Generation |
| `ARCH-AGENT-070` | Domain/Checkpoint 不一致必须通过确定性 Recovery Rule 修复 |
| `ARCH-AGENT-071` | 所有可复用结果必须有 ResultValidity |
| `ARCH-AGENT-072` | REVOKED、STALE、TAINTED 与 SUPERSEDED 必须按依赖图传播 |
| `ARCH-AGENT-073` | Publication 前必须重新校验 ResultValidity |
| `ARCH-AGENT-074` | Domain、Progress、Audit、Integration 与 Publication Event 必须分离 |
| `ARCH-AGENT-075` | Outbox 必须提供同一 Run 有序的 at-least-once 交付和消费者幂等 |
| `ARCH-AGENT-076` | Artifact 必须使用不可变 Version、Validation、Supersession 和 Publication Binding |
| `ARCH-AGENT-077` | 已发布 Artifact 的撤回、更正与保留必须可审计 |
| `ARCH-AGENT-078` | Run、Dispatch、Step、UNKNOWN Action、Interrupt、Publication、Outbox 和 Budget 必须有 Reconciler |
| `ARCH-AGENT-079` | 所有 Reconciler 必须使用 Claim、Fencing、Idempotency 和人工升级策略 |
| `ARCH-AGENT-080` | Deadline、Expiry、Lease、Duration 与用户时区必须使用明确时间语义 |

---

# 10. 验证与完成证据

至少覆盖：补充输入不创建 GoalVersion；Objective 变化创建 GoalVersion 并 Replan；Security 与 Approval 竞态；Cancel 与 Tool Receipt 竞态；Domain Commit 成功而 Checkpoint 失败；Checkpoint 超前 Domain；Evidence 撤销传播；Final Gate 后撤权阻止 Publication；Artifact Rewrite 创建新 Version；Outbox 重复投递；Claim 过期接管；所有 Reconciler 幂等；数据库时间决定 Lease Expiry；Clock Skew 防护；Resume 不重置 Deadline。

本文完成后仅代表 design available、contract-complete 和 program-ready。
