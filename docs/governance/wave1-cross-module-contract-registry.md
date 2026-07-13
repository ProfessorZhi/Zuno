# Wave 1 跨模块 Contract Registry

updated: 2026-07-13
status: confirmed-target
previous_status: parallel-proposal-governance
baseline_main_sha: `729e439e29deadc101c5687fc47125104e62e2c1`
coordinating_pr: `#17`
reviewed_parallel_prs:
  - `#18 Model Gateway @ 3bd9b3e4437314c376a5b1b767ef052e3c74db53`
  - `#19 Security @ f9fd19c16721cb9cec97c25d82b86274660622e6`
  - `#20 Observability & Eval @ 4a91953799cd0bae7f3ca441cccabffbce1271f9`
canonical_adr: `docs/decisions/0003-wave1-cross-module-contract-freeze.md`

> 本文件已随 PR #17 合并到 `main`，字段、Owner、Failure Namespace 和恢复责任为 `CONFIRMED_TARGET`；仍不代表 Runtime 已实现、质量已证明或成为 Current。

## 1. 状态与生效规则

状态枚举：

```text
PARALLEL_PROPOSAL
ALIGNED_PENDING_FIELDS
CONFLICT_REQUIRES_DECISION
CONFIRMED_TARGET
CONFIRMED_TARGET
IMPLEMENTATION_AVAILABLE
CURRENT
```

生效条件：

```text
CONFIRMED_TARGET
    已完成字段级设计审计，但仍在未合并 PR。

CONFIRMED_TARGET
    ADR 0003 与本 Registry 已合并到 main。

IMPLEMENTATION_AVAILABLE
    代码、Migration 和最低工程测试存在。

CURRENT
    代码、Migration、Integration/Fault/E2E、Trace 和运行证据均满足状态事实源要求。
```

本轮决议不会把 Target 写成 Current，也不会把 PR #18、#19、#20 当成已合并事实源。

## 2. 合并和实现门禁

共享 Contract 必须满足：

1. 单一 Canonical Owner；
2. Producer、Consumer 和事实存储边界明确；
3. 字段、Enum、Hash、Version 和兼容策略明确；
4. Idempotency、Generation、Effective Security Epoch、Deadline 按适用性贯通；
5. Failure Code 使用唯一模块 Prefix；
6. Retry、Fallback、Reconcile、Recovery 和 Replan Owner 唯一；
7. Security Gate、Mandatory Audit 和 Data Classification 明确；
8. Receipt 不冒充其他模块的领域成功；
9. Requirement、Test、Evidence 有稳定映射；
10. 实现不得绕过 ADR 0003。

## 2.1 产品部署边界

状态：`CONFIRMED_TARGET`。

```text
Frontend Client
→ Server-hosted Product API
→ Backend logical modules
→ Infrastructure primitives
```

- `PrincipalAccount`、Tenant、Workspace、OrgUnit、Grant、Policy、Epoch 和业务事实只在后端成为权威事实。
- 前端不得直连数据服务、Provider、Queue、Checkpoint 或 Secret Store。
- Developer / CI Local Adapter 不得冒充产品部署模式或多用户安全证据。

## 3. 通用 CrossModuleEnvelope

Canonical Schema：`CrossModuleEnvelopeV1`。

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

兼容规则：

- `message_id` 只用于 Envelope 去重；业务幂等使用 `idempotency_key`。
- `contract_bundle_version`、`producer_module`、`consumer_module` 是强制路由与兼容字段。
- `payload` / `payload_ref` 至少一个存在，并同时校验 payload hash 与 schema hash。
- Agent 相关消息保留 `run_id` / `step_run_id`；非 Agent 工作流可以为空。
- `contract_bundle_version`、`producer_module`、`consumer_module` 是强制路由与兼容字段。
- `payload` / `payload_ref` 至少一个存在，并同时校验 payload hash 与 schema hash。
- Agent 相关消息保留 `run_id` / `step_run_id`；非 Agent 工作流可以为空。
- 旧字段 `security_epoch` 只作为迁移期 Alias；Canonical 字段为 `effective_security_epoch_ref/hash`。
- Unknown Version、Unknown Enum、Missing Tenant、Hash Mismatch、Stale Epoch 和 Generation Conflict 默认 fail-closed 或 quarantine。
- Consumer 只能产生自己的 Decision、Receipt 或 Projection，不能改写 Producer 领域事实。

状态：`CONFIRMED_TARGET`。

## 4. Security ↔ Infrastructure

| Contract | Canonical Owner | Producer → Consumer | 冻结边界 | 状态 |
| --- | --- | --- | --- | --- |
| `EffectiveSecurityEpochRefV1` | Security | Security → 所有受控模块 | Security 保存组合 Epoch 与 Hash；Consumer 只验证 Ref/Hash | `CONFIRMED_TARGET` |
| `SecurityConditionalWrite` | Infrastructure primitive | Domain/Security → Infrastructure | 执行 expected epoch hash、generation、fencing CAS，不判断授权 | `CONFIRMED_TARGET` |
| `SecretRef` | Security | Security/Config → Consumer | 仅引用和分类，不含 Secret Material | `CONFIRMED_TARGET` |
| `CredentialVersionRefV1` | Security | Security → Infrastructure/Model/Tool | 授权、Purpose、Scope、Revocation 归 Security | `CONFIRMED_TARGET` |
| `SecretLeaseV1` | Infrastructure execution fact | Infrastructure → Model/Tool/Data Service | 只交付已授权版本、TTL、Generation 和 Receipt | `CONFIRMED_TARGET` |
| `TenantIsolationRequirement` | Security | Security → Infrastructure | Security 定义等级，Infrastructure 执行物理 Profile | `CONFIRMED_TARGET` |
| `LegalHoldBinding` | Security/Policy Owner | Security → Infrastructure/Domain | Hold 决策归 Security，Purge 阻断和 Receipt 归 Infrastructure | `CONFIRMED_TARGET` |

Canonical Failure：

```text
SEC_CONTEXT_MISSING
SEC_STALE_EPOCH
INFRA_CONDITIONAL_WRITE_CONFLICT
INFRA_SECRET_LEASE_UNAVAILABLE
INFRA_TENANT_ISOLATION_UNSATISFIED
INFRA_LEGAL_HOLD_BLOCKED
```

不再新增以下重复名：

```text
SECURITY_CONTEXT_MISSING
SECURITY_EPOCH_STALE
INFRA_SECURITY_CONDITIONAL_WRITE_CONFLICT
```

## 5. Security ↔ Observability ↔ Infrastructure

| Contract | Canonical Owner | Producer → Consumer | 关键规则 | 状态 |
| --- | --- | --- | --- | --- |
| `SecurityAuditRequirementV1` | Security | Security/Domain → Infrastructure/Observability | 冻结 Audit Class、Redaction、Retention、Legal Hold 和 Fail Mode | `CONFIRMED_TARGET` |
| `AuditDurabilityRequirement` | Infrastructure execution projection | Security Requirement → Infrastructure | 只能保持或加强，不能降低 Audit Class | `CONFIRMED_TARGET` |
| `AuditPersistenceReceiptV1` | Infrastructure | Infrastructure → Producer/Observability | 证明 Local Commit、Outbox 和 Integrity Chain | `CONFIRMED_TARGET` |
| `TelemetryEnvelope` | Observability & Eval | 所有模块 → Observability | at-least-once、Sequence、Watermark、Gap、Replay 和 Redaction | `CONFIRMED_TARGET` |
| `AuditEvent` | Observability accepted fact | Source Event → Observability | 接收后为独立不可变合规事实，引用 Persistence Receipt | `CONFIRMED_TARGET` |
| `ExternalSinkDelivery` | Observability & Eval | Observability → External Sink | Delivery Attempt、Retry、DLQ，不代表源领域成功 | `CONFIRMED_TARGET` |

Mandatory Audit 不变量：

```text
Security / Domain 决定是否必须审计
Infrastructure 证明本地持久化是否成功
Observability 接受并拥有 AuditEvent
Tool Runtime 决定 Effect 是否成功
```

```text
AuditPersistenceReceipt != AuditEvent accepted
AuditEvent accepted != Tool Effect success
ExternalSinkDelivery != source-domain success
StructuredLog != AuditEvent
```

## 6. Model Gateway ↔ Security ↔ Infrastructure

| Contract | Canonical Owner | Producer → Consumer | 冻结边界 | 状态 |
| --- | --- | --- | --- | --- |
| `ModelSecurityDecision` | Security | Security → Model Gateway | Provider/Model Allowlist、Residency、Classification、Redaction 和 Credential Scope | `CONFIRMED_TARGET` |
| `ProviderConnectionFactory` | Infrastructure Port | Model Gateway → Infrastructure | Transport、Pool、TLS、Proxy、Timeout、Cancellation primitive | `CONFIRMED_TARGET` |
| `ModelRoutingDecision` | Model Gateway | Gateway → Agent Core/Observability | Immutable，固定 Role、Operation、Provider、Model、Policy、Budget、Security Ref | `CONFIRMED_TARGET` |
| `ModelCallAttempt` | Model Gateway | Gateway → Agent Core/Observability | 每次真实 Provider Dispatch 一个 Attempt | `CONFIRMED_TARGET` |
| `QuotaReservation` / `ModelQuotaReservationV1` | Model Gateway | Gateway → Infrastructure persistence | Quota 语义归 Gateway；CAS/Clock/Recovery 归 Infrastructure | `CONFIRMED_TARGET` |
| `UsageReceipt` / `ModelUsageReceiptV1` | Model Gateway | Provider/Gateway → Agent Core/Observability | Estimated、Observed、Settled、Correction 追加式结算 | `CONFIRMED_TARGET` |
| `CancellationReceipt` / `ModelCancellationReceiptV1` | Model Gateway | Gateway → Agent Core | Transport Receipt 是输入；Requested 不等于 Confirmed | `CONFIRMED_TARGET` |

共享字段：

```text
model_call_id
attempt_id
routing_decision_id
credential_version_ref
effective_security_epoch_ref
effective_security_epoch_hash
config_version
quota_reservation_id
deadline_at
transport_request_ref
usage_receipt_id
receipt_version
cancellation_state
reconciliation_state
```

禁止：

```text
Transport accepted != ModelCallAttempt succeeded
Queue ACK != Usage settled
Cancellation requested != Cancellation confirmed
Object stored != ModelResponse valid
```

## 7. Knowledge / Memory ↔ Infrastructure

| Contract | Canonical Owner | Producer → Consumer | 关键规则 | 状态 |
| --- | --- | --- | --- | --- |
| `VectorIndexSpec` | Knowledge/Memory | Domain → Infrastructure | Embedding、Dimension、Filter、Version 语义归领域 Owner | `CONFIRMED_TARGET` |
| `GraphIndexSpec` | Knowledge/Memory | Domain → Infrastructure | Entity、Relation、Ontology、Provenance 归领域 Owner | `CONFIRMED_TARGET` |
| `LexicalIndexSpec` | Knowledge | Knowledge → Infrastructure | Analyzer、Mapping、Ranking Profile 归 Knowledge | `CONFIRMED_TARGET` |
| `IndexWriteBatch` / `IndexWriteBatchV1` | Knowledge/Memory | Domain → Infrastructure | Stable Item ID、Version、Hash、Idempotency、Tenant Scope | `CONFIRMED_TARGET` |
| `IndexWriteReceipt` / `IndexWriteReceiptV1` | Infrastructure | Infrastructure → Domain | 只证明物理写入；允许 PARTIAL、UNKNOWN | `CONFIRMED_TARGET` |
| `WriteVisibilityReceipt` | Infrastructure | Infrastructure → Domain | 声明一致性等级、Visibility Deadline 和 Watermark | `CONFIRMED_TARGET` |
| `IndexVerification` | Infrastructure physical verification | Infrastructure → Domain | Schema、Count、Lineage、Scope 和 Representative Query | `CONFIRMED_TARGET` |
| `IndexManifest` | Knowledge/Memory | Domain → Agent Core/Infrastructure | 领域版本组成、质量和 Lineage 事实 | `CONFIRMED_TARGET` |
| `KnowledgeVersion` / `MemoryVersion` | Knowledge / Memory | Domain → Consumer | 只有领域 Owner 可 Acceptance 和 Activation | `CONFIRMED_TARGET` |
| `IndexCutover` / `CutoverReceipt` | Infrastructure execution | Domain ↔ Infrastructure | Owner Approval + expected serving generation/CAS | `CONFIRMED_TARGET` |
| `ServingWatermark` | Infrastructure | Infrastructure → Domain/Recovery | 当前物理服务版本和 source generation | `CONFIRMED_TARGET` |

发布顺序：

```text
Physical Write
→ Write Visibility
→ Infrastructure Verification
→ Domain IndexManifest
→ Domain Acceptance
→ Generation/CAS Cutover
→ ServingWatermark
```

任何前一步都不能跳过后续步骤或宣称 KnowledgeVersion/MemoryVersion 已可服务。

## 8. 删除、恢复与保留

| Contract | Canonical Owner | Producer → Consumer | 关键规则 | 状态 |
| --- | --- | --- | --- | --- |
| `DeletionRequest` | 领域 Owner | Domain/Security → Infrastructure | 领域 Tombstone 是删除事实源 | `CONFIRMED_TARGET` |
| `DeletionTarget` | Infrastructure execution | Infrastructure Internal | PostgreSQL/Object/Vector/Graph/Lexical/Cache/Backup 清单 | `CONFIRMED_TARGET` |
| `DeletionVerification` | Infrastructure | Infrastructure → Domain/Security | Visibility Deadline、未解决目标和 Legal Hold | `CONFIRMED_TARGET` |
| `RecoverySetManifest` | Infrastructure | Backup/Restore → Cutover Owner | 对齐 LSN、Object、Checkpoint、Outbox、Epoch 和 Index Watermark | `CONFIRMED_TARGET` |
| `RecoverySetValidation` | Infrastructure | Infrastructure → Operations/Owner | 只有 `cutover_allowed=true` 才可切生产 | `CONFIRMED_TARGET` |
| `RetentionPolicy` | Policy Owner | Security/Domain → Infrastructure | Infrastructure 执行，不改变保留语义 | `CONFIRMED_TARGET` |
| `LegalHold` | Security/Policy Owner | Security → Infrastructure | Hold 优先于 Purge 和 Backup Expiry | `CONFIRMED_TARGET` |

## 9. PreparedAction Ownership 决议建议——现已冻结

ADR 0003 将旧的 `PreparedAction` 冲突最终拆分为：

```text
Agent Core
    ActionProposal
    ActionExecutionBinding（只保存 PreparedToolAction Ref、Step/Plan binding 和控制状态）
    Retry / Replan / Wait / Abort ControlDecision

Tool Runtime
    PreparedToolAction
    ToolAttempt
    EffectReceipt
    EffectReconciliation

Security
    ActionAuthorizationDecision
    SecurityApprovalDecision
    PreparedToolAction canonical hash verification
    EffectiveSecurityEpoch

Infrastructure
    IdempotencyClaim
    Transaction / Outbox
    Queue / Lease / Fencing
    AuditPersistenceReceipt
    Object / Transport physical receipt
```

协调状态从 `CONFLICT_REQUIRES_DECISION` 变为 `CONFIRMED_TARGET`。

Canonical 执行顺序：

```text
ActionProposal
→ Tool Runtime Prepare / canonicalize
→ Security Prepare Gate
→ optional Approval
→ Security Execute Gate + latest Epoch recheck
→ Mandatory Audit local durable commit（若要求）
→ Idempotency Claim
→ ToolAttempt
→ EffectReceipt or EffectReconciliation
→ Agent Core ControlDecision
```

Canonical Hash 输入和 Approval Binding 以 ADR 0003 第 8 节为准。

禁止等价：

```text
Queue ACK != Tool Effect Success
Lease Release != Tool Effect Success
Audit Delivery != Tool Effect Success
Audit Persistence != Tool Effect Success
Object Commit != Publication Success
Checkpoint Commit != Domain Commit
HTTP 2xx != EffectReceipt valid
```

## 10. Infrastructure 通用协议与物理 Ownership

Infrastructure 是逻辑模块，物理实现统一归：

```text
src/backend/zuno/platform/**
```

不新增 `src/backend/zuno/infrastructure/` 顶层目录。

| Contract | Canonical Owner | Consumers | 状态 |
| --- | --- | --- | --- |
| `InfrastructureCapabilityProfile` | Infrastructure | 所有模块 | `CONFIRMED_TARGET` |
| `DatabaseTransaction` / UoW | Infrastructure | 所有领域模块 | `CONFIRMED_TARGET` |
| `OutboxRecord` / `InboxRecord` | Infrastructure primitive | Producer/Consumer | `CONFIRMED_TARGET` |
| `WorkerLease` / `FencingToken` | Infrastructure | Worker Runtime | `CONFIRMED_TARGET` |
| `CapacityReservation` | Infrastructure | Agent/Model/Tool/Worker | `CONFIRMED_TARGET` |
| `RecoveryWatermark` | Infrastructure | Agent/Knowledge/Operations | `CONFIRMED_TARGET` |
| `TenantIsolationProfile` | Infrastructure execution | Security/Domain | `CONFIRMED_TARGET` |
| `AdapterConformanceProfile` | Infrastructure | Engineering/Release | `CONFIRMED_TARGET` |
| `ServiceCompatibilityEntry` | Infrastructure | Release/Migration | `CONFIRMED_TARGET` |
| `ServiceCriticalityProfile` | Infrastructure | Readiness/Operations | `CONFIRMED_TARGET` |
| `ReleaseManifest` | Infrastructure/Release Engineering | Deployment/Operations | `CONFIRMED_TARGET` |
| `ResourceUsageAttribution` | Infrastructure physical measurement | Product/FinOps/Domain | `CONFIRMED_TARGET` |

Target 目录映射：

```text
platform/database
platform/storage
platform/jobs
platform/checkpoint
platform/coordination
platform/data_services/{vector,graph,lexical,cache}
platform/operations
platform/network
platform/release
platform/security
platform/observability
```

## 11. Failure Ownership Matrix

Canonical Prefix：

```text
SEC_* / INFRA_* / MODEL_* / OBS_* / TOOL_* / KNOW_* / MEM_* / AGENT_*
```

| Failure Category | Normalizer / Fact Owner | Retry / Recovery Owner | Agent Core Control |
| --- | --- | --- | --- |
| Database/Queue/Object/Network physical failure | Infrastructure | Infrastructure | Consume result; choose wait/retry/replan/abort |
| Provider/model failure or unknown | Model Gateway | Model Gateway Retry/Fallback/Reconcile | Decide Retry/Replan/Abstain |
| Authorization/Policy/Epoch failure | Security | Security re-authorize or final deny | Wait/Replan/Abort |
| Index physical write/visibility failure | Infrastructure | Infrastructure Retry/Rebuild/Reconcile | Do not infer retrieval quality |
| Retrieval/IndexManifest quality failure | Knowledge/Memory | Knowledge/Memory corrective path | Replan/Abstain |
| Tool Effect uncertainty | Tool Runtime | Tool Runtime Effect Reconcile | Wait/Abort; retry only after reconcile |
| Telemetry/Audit ingest or Sink failure | Observability/Infrastructure by boundary | respective owner | Security Requirement decides block/degrade |
| Eval/Release Gate failure | Observability & Eval | Eval/Release owner | Do not claim quality proven |

Canonical shared Failure Code：

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

Failure 不能被 Consumer 重命名成另一模块的成功或失败。

## 12. Version 与 Compatibility

所有跨模块 Contract：

- 使用显式 `contract_version`；
- 新增字段默认可选且有确定默认语义；
- 删除或重命名字段必须保留兼容窗口；
- Unknown Enum 默认 fail-closed；
- Producer/Consumer 最低和最高兼容版本可查询；
- Migration、Replay、Outbox、Checkpoint 和长期 Run 保留旧版本读取；
- Contract 激活通过 ReleaseManifest 或显式配置版本，不在运行时静默变化；
- `security_epoch` → `effective_security_epoch_ref/hash` 使用受控兼容 Alias，不允许永久保留双重事实。

## 13. Requirement / Validation

| Requirement | Target | Test | Evidence |
| --- | --- | --- | --- |
| `ARCH-XMOD-001` | 所有共享 Contract 只有一个 Owner | `XMOD-001-UT, XMOD-001-IT` | `EV-XMOD-001` |
| `ARCH-XMOD-002` | Producer/Consumer/Storage/Failure Owner 完整 | `XMOD-002-UT, XMOD-002-IT` | `EV-XMOD-002` |
| `ARCH-XMOD-003` | Effective Epoch/Generation/Deadline 按适用性贯通 | `XMOD-003-UT, XMOD-003-IT, XMOD-003-FT` | `EV-XMOD-003` |
| `ARCH-XMOD-004` | Receipt 不冒充领域成功 | `XMOD-004-UT, XMOD-004-IT, XMOD-004-FT` | `EV-XMOD-004` |
| `ARCH-XMOD-005` | PreparedAction Ownership 已冻结为四方拆分 | `XMOD-005-UT, XMOD-005-IT` | `EV-XMOD-005` |
| `ARCH-XMOD-006` | Mandatory Audit Backpressure 跨模块一致 | `XMOD-006-UT, XMOD-006-IT, XMOD-006-FT, XMOD-006-E2E` | `EV-XMOD-006` |
| `ARCH-XMOD-007` | Index Publish/Deletion/Recovery 协议一致 | `XMOD-007-UT, XMOD-007-IT, XMOD-007-FT, XMOD-007-E2E` | `EV-XMOD-007` |
| `ARCH-XMOD-008` | Contract Version/Enum Compatibility 可验证 | `XMOD-008-UT, XMOD-008-IT` | `EV-XMOD-008` |
| `ARCH-XMOD-009` | Failure Prefix 与共享 Code 无重复冲突 | `XMOD-009-UT, XMOD-009-IT` | `EV-XMOD-009` |
| `ARCH-XMOD-010` | Confirmed Contract 必须有 ADR 与合并审计证据 | `XMOD-010-UT, XMOD-010-IT` | `EV-XMOD-010` |

## 14. Wave 1 合并前审计清单

```text
[x] 最新 main SHA 重新读取并保持 729e439e29deadc101c5687fc47125104e62e2c1
[x] PR #17 / #18 / #19 / #20 当前 Head 已重新读取
[x] Contract 名称、字段、Enum、Hash 和版本在 ADR 0003 冻结
[x] Security Epoch / Secret / Credential Ownership 对齐
[x] AuditEvent / TelemetryEnvelope / Mandatory Audit 对齐
[x] UsageReceipt / QuotaReservation / CancellationReceipt 对齐
[x] Index Batch / Receipt / Manifest / Cutover / Watermark 对齐
[x] PreparedAction / ToolAttempt / EffectReceipt Owner 决议
[x] Failure Code Prefix 和共享 Code 去重
[x] Retry / Replan / Fallback / Recovery Owner 去重
[x] Infrastructure 物理目录冻结到 zuno/platform/**
[x] 文档、ADR、Registry 和专用验证计划同步
[x] 未运行验证继续明确记录
[x] 没有把 Parallel Proposal 或 Target 写成 Current
[ ] PR #17 合并，Registry 成为 CONFIRMED_TARGET
[ ] PR #18 / #19 / #20 rebase 已合并 Registry 并更新兼容 Alias
[ ] Tool Runtime 正式模块采用 PreparedToolAction Contract
[ ] Runtime 实现和工程证据完成
```

## 15. 当前结论

```text
design field freeze complete
status = CONFIRMED_TARGET
module-internal Infrastructure design substantially complete
cross-module ownership and schemas resolved
implementation not established
quality not proven
production ready not established
```

PR #17 合并后，本 Registry 状态应更新为 `CONFIRMED_TARGET`；在此之前它仍不是 `main` 的正式事实源。
