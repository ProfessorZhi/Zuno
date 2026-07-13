# ADR 0003：Wave 1 跨模块 Contract 与 Infrastructure 物理边界冻结

status: accepted-target-pending-merge
updated: 2026-07-13
baseline_main_sha: `729e439e29deadc101c5687fc47125104e62e2c1`
coordinating_pr: `#17`
reviewed_parallel_prs: `#18 Model Gateway`、`#19 Security`、`#20 Observability & Eval`

> 本 ADR 是 Target 设计决议，不是 Current 或实现证据。它只有合并到 `main` 后才成为正式共享 Target Contract；合并前仍是 Draft PR 中已冻结的设计决议。

## 1. 背景

Wave 1 的 Infrastructure、Model Gateway、Security、Observability & Eval 分别完成了模块 Target 设计，但共享边界仍存在四类风险：

1. 同一事实出现多个 Owner，例如 `PreparedAction`、Audit 和 Secret Lease；
2. 同一概念使用不同字段或失败码，例如 scalar `security_epoch` 与组合 Epoch；
3. Infrastructure 逻辑模块的 Target 目录与当前六层物理 Ownership 冲突；
4. 物理 Receipt 被误当成领域成功，例如 Queue ACK、Audit 持久化或 Provider Transport Receipt。

本 ADR 对这些问题作出最终 Target 决议。各模块后续文档和 Program 不得自行改变；如需改变，必须新增 ADR。

## 1.1 协调决议：服务端权威产品边界

Zuno 产品 Target 不是“每个用户本机运行一套后端”。正式产品形态固定为前后端分离：

```text
Web / Desktop Frontend
→ Server-hosted Product API
→ Security / Agent Core / Knowledge / Memory / Model Gateway / Tool Runtime
→ Infrastructure data and execution services
```

每个自然人或服务主体拥有服务端 `PrincipalAccount`，所有 Tenant、Workspace、OrgUnit、ResourceGrant、Policy、Security Epoch、AgentRun、Knowledge、Memory、Usage 和 Audit 事实由后端权威计算与保存。前端输入、缓存的角色、资源列表和 `allowed` 标志均不可信。

SQLite、本地对象存储、本地 Checkpoint 和 in-process Queue 仅作为 Developer / CI Adapter；它们必须复用同一 typed port，但不构成产品部署 Target，也不能证明多用户隔离、并发、恢复或生产安全。

## 2. 决议一：Infrastructure 是逻辑模块，物理代码归 `zuno/platform/**`

不新增 `src/backend/zuno/infrastructure/` 顶层目录。

第 11 模块的 Target 物理落位为：

```text
src/backend/zuno/platform/
├── database/                 PostgreSQL engine、UoW、transaction、migration primitive
├── storage/                  Object Store、immutable object、hash、commit protocol
├── jobs/                     RabbitMQ/local queue、Inbox/Outbox、worker delivery
├── checkpoint/               LangGraph checkpointer adapter、compatibility、reconciliation
├── coordination/             lease、heartbeat、fencing、clock、capacity reservation
├── data_services/
│   ├── vector/               Milvus/local vector physical adapter
│   ├── graph/                Neo4j/local graph physical adapter
│   ├── lexical/              BM25/Search physical adapter
│   └── cache/                Redis/local bounded cache adapter
├── operations/               backup、restore、PITR、retention、drain、health、reconciler
├── network/                  TLS、egress、proxy、connection drain、partition handling
├── release/                  ReleaseManifest、compatibility、provenance validation
├── security/                 secret delivery/encryption/tenant enforcement primitive
└── observability/            physical telemetry/audit ingest and export primitive
```

领域语义继续归原 Owner：

```text
knowledge/**
    VectorIndexSpec、GraphIndexSpec、LexicalIndexSpec、IndexManifest、KnowledgeVersion、retrieval quality。

memory/**
    Memory index semantics、promotion、retention 和 MemoryVersion。

agent/**
    Run、Plan、Step、ControlDecision、RunOutcome 和 orchestration references。

capability/** / future Tool Runtime owner
    Tool definition、prepared execution、attempt、effect 和 reconcile semantics。

platform/model_gateway/**
    Model routing、call/attempt、quota、usage、provider health semantics。
```

Infrastructure Port 可以位于 `platform/**`，领域模块通过 typed Contract 使用，不能导入 SQLAlchemy Session、RabbitMQ Channel、Milvus Client、Neo4j Driver、Redis Client、Provider SDK 或 Secret Material。

任何未来新增 `platform/*` 目录必须在实现 Program 中同步更新 `docs/governance/repo-ownership-matrix.md`、结构验证器和 import guard。本文冻结目标 Ownership，不声称目录已经存在。

## 3. 决议二：共享 Envelope v1

所有跨模块 Command、Domain Event、Decision、Receipt 和 Projection Input 使用同一最小 Envelope：

```python
class CrossModuleEnvelopeV1(BaseModel):
    contract_name: str
    contract_version: str
    contract_bundle_version: str
    message_id: str
    producer_module: str
    consumer_module: str
    tenant_id: str
    workspace_id: str | None
    run_id: str | None
    step_run_id: str | None
    correlation_id: str
    causation_id: str | None
    idempotency_key: str | None
    aggregate_type: str | None
    aggregate_id: str | None
    aggregate_version: int | None
    expected_generation: int | None
    effective_security_epoch_ref: str | None
    effective_security_epoch_hash: str | None
    principal_context_ref: str | None
    security_context_ref: str | None
    authorization_decision_ref: str | None
    deadline_at: datetime | None
    trace_id: str
    data_classification: str
    redaction_decision_ref: str | None
    audit_requirement_ref: str | None
    occurred_at: datetime
    created_at: datetime
    payload: dict | None
    payload_ref: str | None
    payload_hash: str
    payload_schema_hash: str
```

规则：

- `message_id` 只用于 Envelope 去重；业务幂等使用 `idempotency_key`。
- `contract_bundle_version` 固定一次 Run 或工作流使用的跨模块 Contract 集；`producer_module` 与 `consumer_module` 必须显式。
- `payload` 与 `payload_ref` 至少存在一个；无论使用内联或对象引用，都必须验证 `payload_hash` 与 `payload_schema_hash`。
- `run_id`、`step_run_id` 在非 Agent 流程可为空，但不得用 `trace_id` 代替领域标识。
- `security_epoch` scalar 只作为迁移期别名；正式跨模块字段是 `effective_security_epoch_ref` 和 `effective_security_epoch_hash`。
- 组合 Epoch 的组成值由 Security 保存；Consumer 不自行计算新的 Epoch。
- Unknown Contract Version、Unknown Enum、缺 Tenant、Hash 不匹配、Stale Epoch 和 Generation Conflict 默认 fail-closed 或 quarantine。
- Receipt 只证明其 Canonical Owner 的事实，不自动改变其他模块状态。

## 4. 决议三：Security Epoch、Secret 与 Credential

### 4.1 EffectiveSecurityEpoch

Canonical Owner：Security。

```python
class EffectiveSecurityEpochRefV1(BaseModel):
    effective_security_epoch_ref: str
    tenant_id: str
    workspace_id: str | None
    principal_context_ref: str | None
    resource_scope_ref: str | None
    tenant_epoch: int
    workspace_epoch: int | None
    principal_epoch: int | None
    resource_epoch: int | None
    policy_version_ref: str
    epoch_hash: str
    issued_at: datetime
    expires_at: datetime | None
```

Infrastructure 只提供：

```text
expected epoch hash / generation / fencing 的条件写
权威时钟
持久化和冲突 Receipt
```

统一失败码：

```text
SEC_STALE_EPOCH
SEC_CONTEXT_MISSING
INFRA_CONDITIONAL_WRITE_CONFLICT
```

旧建议名 `SECURITY_EPOCH_STALE`、`SECURITY_CONTEXT_MISSING`、`INFRA_SECURITY_CONDITIONAL_WRITE_CONFLICT` 不再作为新的 Canonical Code。

### 4.2 CredentialVersionRef

Canonical Owner：Security。

```python
class CredentialVersionRefV1(BaseModel):
    credential_version_ref: str
    secret_ref: str
    version_id: str
    tenant_id: str
    workspace_id: str | None
    purpose: str
    consumer_scope_hash: str
    data_classification: str
    revocation_epoch_ref: str
    not_before: datetime
    expires_at: datetime | None
```

### 4.3 SecretLease

Canonical Owner：Infrastructure execution fact；授权语义仍归 Security。

```python
class SecretLeaseV1(BaseModel):
    secret_lease_id: str
    credential_version_ref: str
    consumer_id: str
    purpose: str
    lease_generation: int
    issued_at: datetime
    expires_at: datetime
    delivery_receipt_ref: str
    status: Literal["ACTIVE", "EXPIRED", "REVOKED", "FAILED"]
```

Secret Material 只能通过受控内存/进程通道交付，不得进入数据库普通列、Queue Payload、Checkpoint、Prompt、Trace 或 Audit。

## 5. 决议四：Audit 与 Telemetry 的三层事实

### 5.1 SecurityAuditRequirement

Canonical Owner：Security。

```python
class SecurityAuditRequirementV1(BaseModel):
    audit_requirement_id: str
    event_catalog_id: str
    audit_class: Literal["BEST_EFFORT", "DURABLE", "MANDATORY_BEFORE_EFFECT"]
    data_classification: str
    redaction_profile_ref: str
    retention_policy_ref: str
    legal_hold_policy_ref: str | None
    external_delivery_required: bool
    fail_mode: Literal["DEGRADE", "REJECT", "BLOCK_EFFECT"]
    requirement_hash: str
```

### 5.2 AuditDurabilityRequirement 与 AuditPersistenceReceipt

Canonical Owner：Infrastructure execution facts。

`AuditDurabilityRequirement` 是 `SecurityAuditRequirement` 的不可扩权执行投影，只能保持或加强，不得降低 `audit_class` 或 `fail_mode`。

```python
class AuditPersistenceReceiptV1(BaseModel):
    audit_persistence_receipt_id: str
    source_event_ref: str
    audit_requirement_ref: str
    local_commit_ref: str
    outbox_ref: str | None
    integrity_chain_ref: str
    persisted_at: datetime
    status: Literal["COMMITTED", "DUPLICATE", "FAILED"]
```

`MANDATORY_BEFORE_EFFECT` 必须在 Tool Effect、Break-glass、权限变更、Credential 使用和策略指定的其他高风险动作之前取得 `COMMITTED` Receipt。

### 5.3 AuditEvent 与 TelemetryEnvelope

Canonical Owner：Observability & Eval。

- `TelemetryEnvelope` 是 at-least-once ingest Contract，负责 Sequence、Watermark、Gap、Replay、Redaction Ref 和 Projection 输入。
- `AuditEvent` 是被 Observability 接受后的不可变合规事实，必须引用 `source_event_ref`、`audit_requirement_ref` 和 `audit_persistence_receipt_ref`。
- `ExternalSinkDelivery` 只证明外部 Sink 交付，不证明源领域动作成功。

禁止等价：

```text
AuditPersistenceReceipt != AuditEvent accepted
AuditEvent accepted != Tool Effect success
ExternalSinkDelivery != source-domain success
StructuredLog != AuditEvent
```

## 6. 决议五：Model Gateway 与 Infrastructure

### 6.1 ProviderConnectionFactory

Canonical Owner：Infrastructure Port；Provider 业务语义归 Model Gateway。

```python
class ProviderConnectionRequestV1(BaseModel):
    provider_ref: str
    credential_version_ref: str
    purpose: str
    residency_ref: str
    tls_profile_ref: str
    proxy_profile_ref: str | None
    connect_timeout_ms: int
    request_timeout_ms: int
    cancellation_token_ref: str | None
    trace_id: str
```

Infrastructure 返回 Transport/Pool/TLS/Timeout/Cancellation 的物理 Receipt，不返回 Provider 成功结论。

### 6.2 QuotaReservation

Canonical Owner：Model Gateway。

```python
class ModelQuotaReservationV1(BaseModel):
    quota_reservation_id: str
    tenant_id: str
    provider_ref: str
    model_ref: str
    model_call_id: str
    attempt_id: str
    reserved_units: float
    unit_kind: str
    expected_generation: int
    expires_at: datetime
    status: Literal["RESERVED", "CONSUMING", "RELEASED", "EXPIRED", "RECONCILING"]
```

Infrastructure 只提供 CAS、权威 Clock、Lease/Fencing、事务和恢复。

### 6.3 UsageReceipt

Canonical Owner：Model Gateway。

```python
class ModelUsageReceiptV1(BaseModel):
    usage_receipt_id: str
    receipt_version: int
    model_call_id: str
    attempt_id: str
    provider_request_ref: str | None
    usage_kind: Literal["ESTIMATED", "OBSERVED", "SETTLED", "CORRECTION"]
    input_units: float
    output_units: float
    cost_amount: float | None
    currency: str | None
    pricing_version_ref: str | None
    supersedes_receipt_ref: str | None
    observed_at: datetime
    idempotency_key: str
```

Correction 追加新 Receipt，不覆盖旧 Receipt。Agent Core 的 Budget Ledger 消费 Usage 事件，但不重定义 Provider Usage。

### 6.4 CancellationReceipt

Canonical Owner：Model Gateway。

```python
class ModelCancellationReceiptV1(BaseModel):
    cancellation_receipt_id: str
    model_call_id: str
    attempt_id: str | None
    requested_at: datetime
    transport_receipt_ref: str | None
    state: Literal["REQUESTED", "CONFIRMED", "UNCONFIRMED", "TOO_LATE", "FAILED"]
    provider_execution_may_have_occurred: bool
    reconciliation_required: bool
```

Transport Cancellation Receipt 只是输入；`REQUESTED` 不等于 `CONFIRMED`。

## 7. 决议六：Knowledge / Memory 派生索引发布

Canonical Ownership：

| Contract | Owner |
| --- | --- |
| `VectorIndexSpec`、`GraphIndexSpec`、`LexicalIndexSpec` | Knowledge / Memory |
| `IndexWriteBatch` | 发起该索引的 Knowledge / Memory Owner |
| `IndexWriteReceipt`、`WriteVisibilityReceipt`、`IndexVerification` | Infrastructure |
| `IndexManifest`、KnowledgeVersion、MemoryVersion、领域 Acceptance | Knowledge / Memory |
| `IndexCutover` execution、`CutoverReceipt`、`ServingWatermark` | Infrastructure |

### 7.1 IndexWriteBatch

```python
class IndexWriteBatchV1(BaseModel):
    batch_id: str
    build_run_id: str
    owner_module: Literal["KNOWLEDGE", "MEMORY"]
    tenant_id: str
    workspace_id: str
    index_kind: Literal["VECTOR", "GRAPH", "LEXICAL"]
    target_version: str
    source_snapshot_ref: str
    item_identity_scheme: str
    item_count: int
    payload_ref: str
    payload_hash: str
    schema_spec_ref: str
    idempotency_key: str
    expected_generation: int
    effective_security_epoch_ref: str
    deadline_at: datetime
```

### 7.2 IndexWriteReceipt 与 Visibility

```python
class IndexWriteReceiptV1(BaseModel):
    receipt_id: str
    batch_id: str
    physical_target_ref: str
    attempt_no: int
    accepted_count: int
    rejected_count: int
    observed_generation: int
    service_commit_ref: str | None
    checksum_or_digest: str | None
    status: Literal["COMMITTED", "PARTIAL", "DUPLICATE", "FAILED", "UNKNOWN"]

class WriteVisibilityReceiptV1(BaseModel):
    receipt_id: str
    write_receipt_ref: str
    consistency_class: Literal["IMMEDIATE", "READ_YOUR_WRITE", "BOUNDED_EVENTUAL", "EVENTUAL"]
    visible_at: datetime | None
    visibility_deadline_at: datetime
    serving_watermark_ref: str | None
    status: Literal["PENDING", "VISIBLE", "DEADLINE_EXCEEDED", "FAILED"]
```

发布顺序固定：

```text
Physical Write
→ Write Visibility
→ Infrastructure Verification
→ Domain IndexManifest
→ Domain Acceptance
→ Generation/CAS Cutover
→ ServingWatermark
```

任一步都不能跳过后续步骤或冒充 KnowledgeVersion/MemoryVersion 已可服务。

## 8. 决议七：PreparedAction 与 Tool Effect 最终拆分

Agent Core 正式文档中历史使用的 `PreparedAction` 名称在后续实现中拆分，不再作为 Agent Core 持有可执行 Payload 的 Aggregate。

### 8.1 Canonical Ownership

```text
Agent Core owns
    ActionProposal
    ActionExecutionBinding（只保存 Ref、Step/Plan binding 和控制状态）
    Retry / Replan / Abort / Wait 控制决策

Tool Runtime owns
    PreparedToolAction
    ToolAttempt
    EffectReceipt
    EffectReconciliation

Security owns
    ActionAuthorizationDecision
    SecurityApprovalDecision
    PreparedToolAction canonical hash verification
    EffectiveSecurityEpoch

Infrastructure owns
    IdempotencyClaim
    Transaction / Outbox
    Queue / Lease / Fencing
    AuditPersistenceReceipt
    Object / Transport physical receipt
```

### 8.2 ActionProposal

```python
class ActionProposalV1(BaseModel):
    action_proposal_id: str
    run_id: str
    step_run_id: str
    proposed_capability_ref: str
    proposed_operation: str
    proposed_args_ref: str
    proposed_args_hash: str
    expected_result_contract_ref: str
    side_effect_class: str
    proposal_source_ref: str
    status: Literal["PROPOSED", "REJECTED", "BOUND", "OBSOLETE"]
```

### 8.3 PreparedToolAction

```python
class PreparedToolActionV1(BaseModel):
    prepared_tool_action_id: str
    action_proposal_ref: str
    tenant_id: str
    workspace_id: str
    principal_context_ref: str
    tool_definition_ref: str
    tool_definition_version: str
    operation: str
    canonical_args_ref: str
    canonical_args_hash: str
    target_resource_refs_hash: str
    side_effect_class: str
    credential_scope_ref: str | None
    idempotency_scope: str
    policy_snapshot_ref: str
    effective_security_epoch_ref: str
    effective_security_epoch_hash: str
    deadline_at: datetime
    canonical_hash_version: str
    prepared_action_hash: str
    status: Literal["PREPARED", "WAITING_APPROVAL", "AUTHORIZED", "EXECUTING", "TERMINAL", "OBSOLETE"]
```

Canonical Hash 输入固定为：

```text
canonical_hash_version
tenant_id
workspace_id
principal_context_ref
tool_definition_ref
tool_definition_version
operation
canonical_args_hash
target_resource_refs_hash
side_effect_class
credential_scope_ref
idempotency_scope
policy_snapshot_ref
effective_security_epoch_hash
deadline_at
```

`prepared_tool_action_id`、创建时间、Attempt ID、Lease ID 和随机运行字段不进入 Hash。

### 8.4 Approval Binding

`SecurityApprovalDecision` 必须绑定：

```text
prepared_tool_action_id
prepared_action_hash
principal_id
tenant_id
workspace_id
tool_definition_ref
operation
canonical_args_hash
policy_snapshot_ref
effective_security_epoch_hash
approval_policy_id
approver_principal_ids
expires_at
nonce
consumption_mode
```

任一绑定字段变化、Approval 过期、Epoch 变化或 Nonce 已消费，都必须重新授权。

### 8.5 Effect 执行顺序

```text
ActionProposal
→ Tool Runtime Prepare / canonicalize
→ Security Prepare Gate
→ optional Approval
→ Security Execute Gate + latest Epoch recheck
→ Mandatory Audit local durable commit（若要求）
→ Infrastructure Idempotency Claim
→ ToolAttempt
→ EffectReceipt or EffectReconciliation
→ Agent Core ControlDecision
```

### 8.6 Retry / Unknown Effect

- 明确 `NOT_DISPATCHED`：Tool Runtime 可按 Policy 创建新 Attempt。
- Provider/Tool 是否执行未知：状态进入 `UNKNOWN` / `RECONCILING`，禁止盲目重试副作用。
- Tool Runtime 负责查询外部 Idempotency Key、Provider Receipt 或资源状态并形成 `EffectReconciliation`。
- Agent Core 只根据 Tool Runtime 结果决定 Retry、Replan、Wait、Abort 或人工处理。

禁止等价：

```text
Queue ACK != Tool Effect Success
Lease Release != Tool Effect Success
Audit Persistence != Tool Effect Success
HTTP 2xx != Effect Receipt Valid
Checkpoint Commit != Domain Commit
```

## 9. 决议八：Failure Code Namespace 与 Owner

Canonical Prefix：

```text
SEC_*      Security
INFRA_*    Infrastructure
MODEL_*    Model Gateway
OBS_*      Observability & Eval
TOOL_*     Tool Runtime
KNOW_*     Knowledge
MEM_*      Memory
AGENT_*    Agent Core
```

跨模块只消费 `failure_ref`、Canonical Code、Retryability、Owner 和 Recovery Action，不在 Consumer 中重命名为另一模块的成功/失败。

本轮冻结的共享 Code：

```text
SEC_CONTEXT_MISSING
SEC_STALE_EPOCH
SEC_APPROVAL_REQUIRED
SEC_APPROVAL_REPLAY
SEC_REDACTION_FAILED
SEC_AUDIT_REQUIREMENT_UNSATISFIED

INFRA_CONDITIONAL_WRITE_CONFLICT
INFRA_SECRET_LEASE_UNAVAILABLE
INFRA_AUDIT_PERSISTENCE_FAILED
INFRA_CAPACITY_EXHAUSTED
INFRA_INDEX_CUTOVER_CONFLICT
INFRA_WRITE_VISIBILITY_DEADLINE

MODEL_PROVIDER_TIMEOUT
MODEL_ATTEMPT_UNKNOWN
MODEL_QUOTA_UNAVAILABLE
MODEL_USAGE_SETTLEMENT_PENDING
MODEL_CANCELLATION_UNCONFIRMED

OBS_ENVELOPE_SCHEMA_UNSUPPORTED
OBS_INGEST_GAP
OBS_AUDIT_ACCEPTANCE_FAILED
OBS_EXTERNAL_SINK_DELIVERY_FAILED

TOOL_PREPARED_ACTION_INVALID
TOOL_EFFECT_UNKNOWN
TOOL_EFFECT_RECONCILIATION_REQUIRED
TOOL_DUPLICATE_EFFECT_BLOCKED

KNOW_INDEX_MANIFEST_REJECTED
KNOW_RETRIEVAL_POLICY_UNSATISFIED
```

模块内部可以增加 Code，但不能复用其他 Prefix，也不能为同一共享条件创建第二个 Canonical Code。

## 10. 决议九：Retry、Recovery 与 Reconcile Owner

| 场景 | Fact Owner | Retry / Recovery Owner | Agent Core Role |
| --- | --- | --- | --- |
| PostgreSQL/Queue/Object/Network 物理失败 | Infrastructure | Infrastructure 重连、重投、恢复 primitive | 消费结构化结果，决定控制路径 |
| Provider/Model Attempt 失败或未知 | Model Gateway | Model Gateway Retry/Fallback/Reconcile；受调用 Policy 限制 | 决定 Retry/Replan/Abstain，不直接调用 Provider |
| Security/Epoch/Approval 失败 | Security | Security 重新授权或返回终局拒绝 | Wait/Replan/Abort |
| Index 物理写入/可见性失败 | Infrastructure | Infrastructure Retry/Rebuild/Reconcile | 不把物理成功当检索质量通过 |
| Retrieval/IndexManifest 质量失败 | Knowledge/Memory | Knowledge/Memory Corrective Retrieval 或 Rebuild Request | Replan/Abstain |
| Tool Effect 未知 | Tool Runtime | Tool Runtime Effect Reconcile | Wait/Abort/Retry only after reconcile result |
| Telemetry/Audit ingest 或 Sink 失败 | Observability/Infrastructure 按边界 | 各自重投；SecurityAuditRequirement 决定 block/degrade | 不改源领域事实 |
| Eval/Release Gate 失败 | Observability & Eval | Eval/Release Owner | 不伪造 quality proven |

Retry 与 Replan 保持分离：执行方式暂时失败而计划仍正确才 Retry；目标、依赖、能力、安全条件或事实假设失效才由 Agent Core Replan。

## 11. Contract 状态与生效顺序

本 ADR 在 Draft PR 中的状态是：

```text
FIELD_FROZEN_PENDING_MERGE
```

生效顺序：

1. PR #17 合并后，本 ADR 和 Registry 成为 `CONFIRMED_TARGET`；
2. PR #18、#19、#20 rebase 最新 `main`，将字段、枚举、Failure Code 和引用对齐本 ADR；
3. Tool Runtime 模块设计必须采用 `PreparedToolAction` / `EffectReceipt` Ownership；
4. 本协调 PR 同步把 Agent Core 的旧 `PreparedAction` Aggregate 改为 `ActionProposal` + `ActionExecutionBinding`，并只引用 Tool Runtime `PreparedToolAction`；
5. 只有代码、Migration、Integration/Fault/E2E、Trace 和运行证据完成后才能提升为 Current。

推荐合并顺序：

```text
PR #17 shared contract freeze
→ rebase / align PR #18 Model Gateway
→ rebase / align PR #19 Security
→ rebase / align PR #20 Observability & Eval
→ design 08 Tool Runtime
→ Codex phased implementation Programs
```

## 12. 验证与完成标准

本 ADR 的文档完成证据：

- 所有共享对象只有一个 Canonical Owner；
- Envelope、Epoch、Secret、Audit、Model、Index 和 Tool Effect 字段已冻结；
- Failure Prefix 和共享 Code 已去重；
- `zuno/platform/**` 物理落位已冻结；
- Receipt 不冒充领域成功；
- Retry、Recovery、Reconcile Owner 已冻结；
- 自动验证检查 ADR、Registry、决议状态和关键不变量。

本 ADR 不证明：

```text
runtime implementation available
PostgreSQL / RabbitMQ / Milvus / Neo4j / Redis integrated
Tool Runtime implemented
full CI passed
quality proven
production ready
```
