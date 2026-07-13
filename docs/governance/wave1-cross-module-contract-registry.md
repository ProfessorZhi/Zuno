# Wave 1 跨模块 Contract Registry

updated: 2026-07-13
status: parallel-proposal-governance
baseline_main_sha: `729e439e29deadc101c5687fc47125104e62e2c1`
coordinating_pr: `#17`
parallel_prs: `#18 Model Gateway`、`#19 Security`、`#20 Observability & Eval`

> 本文件是 Wave 1 跨模块设计的合并前协调登记表，不是 Current 事实源，也不替代各模块正式 Target 文档。只有在相关 PR 完成字段级审计、Owner 唯一、失败码一致、验证通过并合并后，条目才能从 Parallel Proposal 提升为 Confirmed Target Contract。

## 1. 目的

多个模块分别定义对象时，最容易出现：

```text
同名不同义
同一事实多个 Owner
Producer / Consumer 不明确
Receipt 被误当成领域成功
Security Epoch、Deadline、Generation 未贯通
Failure Code 重复或语义冲突
Retry、Replan、Recovery 责任混淆
Audit 和 Evidence 缺失
```

本 Registry 统一登记：

```text
Contract 名称与版本
Canonical Owner
Producer / Consumer
事实存储位置
Idempotency / Generation / Security Epoch
Deadline / Cancellation
Failure Owner
Retry / Recovery Owner
Audit / Evidence
当前协调状态
```

## 2. 合并规则

一个 Contract 只有满足以下条件才能标记 `CONFIRMED_TARGET`：

1. 只有一个 Canonical Owner；
2. Producer 和 Consumer 均在正式模块文档出现；
3. 字段、枚举、版本和兼容策略明确；
4. 事实存储位置与物理存储 Owner 分离；
5. Idempotency、Generation、Security Epoch、Deadline 和 Cancellation 按适用性贯通；
6. Failure Code 不与其他模块冲突；
7. Retry、Replan、Fallback、Reconcile 和 Recovery Owner 唯一；
8. Security Gate 和 Mandatory Audit 要求明确；
9. Requirement、Test、Evidence 有稳定映射；
10. 并行 PR 完成互相引用或集中审计记录。

状态枚举：

```text
PARALLEL_PROPOSAL
ALIGNED_PENDING_FIELDS
CONFLICT_REQUIRES_DECISION
CONFIRMED_TARGET
IMPLEMENTATION_AVAILABLE
CURRENT
```

本文件当前所有条目最高只能是 `ALIGNED_PENDING_FIELDS`。

## 3. 通用 Envelope

所有跨模块 Command、Event、Receipt 和 Decision 至少携带：

```python
class CrossModuleEnvelope(BaseModel):
    contract_name: str
    contract_version: str
    message_id: str
    tenant_id: str
    workspace_id: str | None
    correlation_id: str
    causation_id: str
    idempotency_key: str | None
    expected_generation: int | None
    security_epoch: int | None
    deadline_at: datetime | None
    trace_id: str
    producer_module: str
    payload_ref: str | None
    payload_hash: str | None
```

规则：

- Message ID 只标识 Envelope；业务幂等使用 `idempotency_key`。
- Receipt 只证明对应 Owner 的事实，不自动提升其他模块状态。
- Consumer 不得修改 Producer 拥有的事实，只能提交自己的 Decision、Receipt 或 Projection。
- Unknown Version、Unknown Enum、Missing Tenant、Stale Security Epoch 和 Generation Conflict 默认 fail-closed。

## 4. Security ↔ Infrastructure

| Contract | Canonical Owner | Producer → Consumer | 事实与物理边界 | 状态 |
| --- | --- | --- | --- | --- |
| `SecurityEpoch` | Security | Security → 所有写入模块 | Security 拥有递增原因和有效值；Infrastructure 提供条件写 | `ALIGNED_PENDING_FIELDS` |
| `SecurityConditionalWrite` | Infrastructure primitive | Domain/Security → Infrastructure | 只执行 expected epoch/generation/fencing CAS，不判断授权 | `PARALLEL_PROPOSAL` |
| `SecretRef` | Security | Security/Config → Consumer | 只包含引用、Scope 和 Classification，不含 Secret Material | `ALIGNED_PENDING_FIELDS` |
| `SecretLease` | Infrastructure delivery | Infrastructure → Model/Tool/Data Service | 交付版本、TTL、Lease ID；授权范围来自 Security | `ALIGNED_PENDING_FIELDS` |
| `CredentialVersionRef` | Security | Security → Model Gateway/Infrastructure | Security 拥有授权、Scope、Revocation；Infrastructure 负责安全交付 | `ALIGNED_PENDING_FIELDS` |
| `TenantIsolationRequirement` | Security | Security → Infrastructure | Security 定义等级；Infrastructure 选择并执行物理 Profile | `PARALLEL_PROPOSAL` |
| `LegalHoldBinding` | Security/Policy Owner | Security → Infrastructure/Domain Owner | Security 决定 Hold；Infrastructure 阻止 Purge 并出 Receipt | `ALIGNED_PENDING_FIELDS` |

建议 Failure Code：

```text
SECURITY_EPOCH_STALE
SECURITY_CONTEXT_MISSING
INFRA_SECURITY_CONDITIONAL_WRITE_CONFLICT
INFRA_SECRET_LEASE_UNAVAILABLE
INFRA_SECRET_VERSION_REVOKED
INFRA_TENANT_ISOLATION_UNSATISFIED
INFRA_LEGAL_HOLD_BLOCKED
```

## 5. Security ↔ Observability ↔ Infrastructure

| Contract | Canonical Owner | Producer → Consumer | 关键规则 | 状态 |
| --- | --- | --- | --- | --- |
| `SecurityAuditRequirement` | Security | Security → Observability/Infrastructure | 定义事件目录、Data Class、Durability 和 Retention | `ALIGNED_PENDING_FIELDS` |
| `AuditDurabilityRequirement` | Infrastructure execution | Security/Domain → Infrastructure | `BEST_EFFORT`、`DURABLE`、`MANDATORY_BEFORE_EFFECT` | `PARALLEL_PROPOSAL` |
| `AuditEvent` | Observability accepted fact | Domain/Security → Observability | 接收后形成不可变 Audit 事实；不能修改源领域事实 | `ALIGNED_PENDING_FIELDS` |
| `AuditPersistenceReceipt` | Infrastructure | Infrastructure → Producer/Observability | 证明 Local Commit、Outbox 和 Integrity Chain | `PARALLEL_PROPOSAL` |
| `TelemetryEnvelope` | Observability | 各模块 → Observability | at-least-once、Sequence/Watermark、Redaction Ref | `ALIGNED_PENDING_FIELDS` |
| `ExternalSinkDelivery` | Observability | Observability → External Sink | Attempt、Receipt、Retry、DLQ 由 Observability 拥有 | `ALIGNED_PENDING_FIELDS` |

Mandatory Audit 不变量：

```text
Security / Domain 决定“必须审计”
Infrastructure 决定物理持久化是否成功
Observability 接受并拥有 AuditEvent
Tool Runtime 决定 Effect 是否执行成功
```

`AuditPersistenceReceipt`、Queue ACK 或 External Sink Delivery 都不能替代 `EffectReceipt`。

## 6. Model Gateway ↔ Security ↔ Infrastructure

| Contract | Canonical Owner | Producer → Consumer | 关键规则 | 状态 |
| --- | --- | --- | --- | --- |
| `ModelSecurityDecision` | Security | Security → Model Gateway | Provider Allowlist、Residency、Classification、Redaction、Credential Scope | `ALIGNED_PENDING_FIELDS` |
| `ProviderConnectionFactory` | Infrastructure port | Model Gateway → Infrastructure | Infrastructure 提供 Transport/Pool/TLS/Timeout；Gateway 拥有 Provider 语义 | `ALIGNED_PENDING_FIELDS` |
| `ModelRoutingDecision` | Model Gateway | Gateway → Agent Core/Observability | Immutable，固定 Role、Provider、Model、Policy、Budget、Security Ref | `ALIGNED_PENDING_FIELDS` |
| `ModelCallAttempt` | Model Gateway | Gateway → Agent Core/Observability | 每次真实 Provider 调用一个 Attempt | `ALIGNED_PENDING_FIELDS` |
| `QuotaReservation` | Model Gateway semantic | Gateway → Infrastructure persistence | Gateway 拥有配额语义；Infrastructure 提供原子 CAS、Clock 和恢复 | `ALIGNED_PENDING_FIELDS` |
| `UsageReceipt` | Model Gateway | Provider/Gateway → Agent Core/Observability | Estimated 与 Settled 分离，幂等结算 | `ALIGNED_PENDING_FIELDS` |
| `CancellationReceipt` | Model Gateway | Gateway → Agent Core | Infrastructure 只提供 Transport Cancellation primitive | `PARALLEL_PROPOSAL` |

建议共享字段：

```text
routing_decision_id
attempt_id
credential_version_ref
security_epoch
config_version
quota_reservation_id
deadline_at
transport_request_id
estimated_usage
settled_usage
cancellation_state
reconciliation_state
```

## 7. Knowledge / Memory ↔ Infrastructure

| Contract | Canonical Owner | Producer → Consumer | 关键规则 | 状态 |
| --- | --- | --- | --- | --- |
| `VectorIndexSpec` | Knowledge/Memory | Domain → Infrastructure | Embedding、Dimension、Filter、Version 语义归领域 Owner | `PARALLEL_PROPOSAL` |
| `GraphIndexSpec` | Knowledge/Memory | Domain → Infrastructure | Entity/Relation/Ontology/Provenance 归领域 Owner | `PARALLEL_PROPOSAL` |
| `LexicalIndexSpec` | Knowledge | Knowledge → Infrastructure | Analyzer、Mapping、Ranking Profile 归 Knowledge | `PARALLEL_PROPOSAL` |
| `IndexWriteBatch` | Domain request；Infrastructure envelope | Knowledge/Memory → Infrastructure | 稳定 Item ID、Version、Hash、Idempotency、Tenant Scope | `ALIGNED_PENDING_FIELDS` |
| `IndexWriteReceipt` | Infrastructure | Infrastructure → Knowledge/Memory | 只证明物理写入，不代表版本可服务 | `ALIGNED_PENDING_FIELDS` |
| `WriteVisibilityReceipt` | Infrastructure | Infrastructure → Knowledge/Memory | 声明一致性等级和可见 Watermark | `PARALLEL_PROPOSAL` |
| `IndexVerification` | Infrastructure physical verification | Infrastructure → Domain Owner | Schema、Count、Scope、Lineage、Representative Query | `PARALLEL_PROPOSAL` |
| `IndexManifest` | Knowledge/Memory | Domain Owner → Agent Core/Infrastructure | 领域版本组成与验证事实 | `ALIGNED_PENDING_FIELDS` |
| `KnowledgeVersion` / `MemoryVersion` | Knowledge / Memory | Domain Owner → Consumer | 领域 Owner 使用 Generation/CAS 激活 | `ALIGNED_PENDING_FIELDS` |
| `IndexCutover` / `CutoverReceipt` | Infrastructure execution | Domain Owner ↔ Infrastructure | Owner Approval + expected serving generation | `PARALLEL_PROPOSAL` |
| `ServingWatermark` | Infrastructure | Infrastructure → Domain/Recovery | 当前物理服务版本与 source generation | `PARALLEL_PROPOSAL` |

发布不变量：

```text
Physical Write
→ Visibility
→ Infrastructure Verification
→ Domain IndexManifest
→ Domain Acceptance
→ Generation/CAS Cutover
→ ServingWatermark
```

任何前一步都不能独立跳过后续步骤。

## 8. 删除、恢复与保留

| Contract | Canonical Owner | Producer → Consumer | 关键规则 | 状态 |
| --- | --- | --- | --- | --- |
| `DeletionRequest` | 领域 Owner | Domain/Security → Infrastructure | 领域 Tombstone 是删除事实源 | `PARALLEL_PROPOSAL` |
| `DeletionTarget` | Infrastructure execution | Infrastructure Internal | PostgreSQL/Object/Vector/Graph/Lexical/Cache/Backup 目标清单 | `PARALLEL_PROPOSAL` |
| `DeletionVerification` | Infrastructure | Infrastructure → Domain/Security | Visibility Deadline、未解决目标、Legal Hold | `PARALLEL_PROPOSAL` |
| `RecoverySetManifest` | Infrastructure | Backup/Restore → Cutover Owner | 对齐 LSN、Object、Checkpoint、Outbox、Epoch、Index Watermark | `PARALLEL_PROPOSAL` |
| `RecoverySetValidation` | Infrastructure | Infrastructure → Operations/Owner | 只有 `cutover_allowed=true` 才可切生产 | `PARALLEL_PROPOSAL` |
| `RetentionPolicy` | Policy Owner | Security/Domain → Infrastructure | Infrastructure 执行，不自行改变保留语义 | `ALIGNED_PENDING_FIELDS` |
| `LegalHold` | Security/Policy Owner | Security → Infrastructure | Hold 优先于 Purge 和 Backup Expiry | `ALIGNED_PENDING_FIELDS` |

## 9. Agent Core ↔ Tool Runtime ↔ Security ↔ Infrastructure

### 9.1 PreparedAction Ownership 决议建议

```text
Agent Core
    ActionProposalRef
    Step / Plan orchestration binding
    ControlDecision / Retry / Replan / Abort

Tool Runtime
    ExecutablePreparedAction
    ToolAttempt
    EffectReceipt
    EffectReconciliation

Security
    AuthorizationDecision
    ApprovalBinding
    PreparedAction canonical hash
    SecurityEpoch

Infrastructure
    IdempotencyClaim
    Transaction / Outbox
    Queue / Lease / Fencing
    Mandatory Audit durability
    Object / Physical Receipt
```

协调状态：`CONFLICT_REQUIRES_DECISION`。

必须在 Tool Runtime 实现前冻结：

- `PreparedAction` 是否分为 Proposal 和 Executable 两个对象；
- canonical hash 输入字段；
- Approval 绑定对象和过期语义；
- Effect 前 Security Epoch recheck；
- Provider 返回成功但响应丢失时的 Effect Reconciliation；
- Retry 与重复副作用边界。

### 9.2 禁止等价关系

```text
Queue ACK != Tool Effect Success
Lease Release != Tool Effect Success
Audit Delivery != Tool Effect Success
Object Commit != Publication Success
Checkpoint Commit != Domain Commit
```

## 10. Infrastructure 通用协议

| Contract | Canonical Owner | Consumers | 状态 |
| --- | --- | --- | --- |
| `InfrastructureCapabilityProfile` | Infrastructure | 所有模块 | `ALIGNED_PENDING_FIELDS` |
| `DatabaseTransaction` / UoW | Infrastructure | 所有领域模块 | `ALIGNED_PENDING_FIELDS` |
| `OutboxRecord` / `InboxRecord` | Infrastructure primitive | Producer/Consumer | `ALIGNED_PENDING_FIELDS` |
| `WorkerLease` / `FencingToken` | Infrastructure | Worker Runtime | `ALIGNED_PENDING_FIELDS` |
| `CapacityReservation` | Infrastructure | Agent/Model/Tool/Worker | `ALIGNED_PENDING_FIELDS` |
| `RecoveryWatermark` | Infrastructure | Agent/Knowledge/Operations | `ALIGNED_PENDING_FIELDS` |
| `TenantIsolationProfile` | Infrastructure execution | Security/Domain | `PARALLEL_PROPOSAL` |
| `AdapterConformanceProfile` | Infrastructure | Engineering/Release | `PARALLEL_PROPOSAL` |
| `ServiceCompatibilityEntry` | Infrastructure | Release/Migration | `PARALLEL_PROPOSAL` |
| `ServiceCriticalityProfile` | Infrastructure | Readiness/Operations | `PARALLEL_PROPOSAL` |
| `ReleaseManifest` | Infrastructure/Release Engineering | Deployment/Operations | `PARALLEL_PROPOSAL` |
| `ResourceUsageAttribution` | Infrastructure physical measurement | Product/FinOps/Domain Owner | `PARALLEL_PROPOSAL` |

## 11. Failure Ownership Matrix

| Failure Category | Normalizer / Fact Owner | Control Decision Owner |
| --- | --- | --- |
| Database/Queue/Object/Network physical failure | Infrastructure | Calling domain module |
| Provider/model failure | Model Gateway | Agent Core decides Retry/Replan/Abstain |
| Authorization/Policy/Epoch failure | Security | Agent Core/Tool/Product consumes fail-closed result |
| Retrieval/index quality failure | Knowledge/Memory | Agent Core chooses corrective retrieval or abstain |
| Tool Effect uncertainty | Tool Runtime | Agent Core consumes reconciliation result |
| Telemetry/Audit delivery failure | Observability/Infrastructure by boundary | Security/Domain policy decides block/degrade |
| Eval/Release Gate failure | Observability & Eval | Release owner |

Failure 不能跨 Owner 被重命名成看似成功。例如 Infrastructure 不能把 Milvus 健康转换成 Retrieval Quality Passed。

## 12. Version 与 Compatibility

所有跨模块 Contract 必须：

- 使用显式 `contract_version`；
- 新增字段默认可选且有确定默认语义；
- 删除/重命名字段需要兼容窗口；
- Unknown Enum 默认 fail-closed；
- Producer 与 Consumer 的最低/最高兼容版本可查询；
- Migration、Replay、Outbox、Checkpoint 和长期运行 Run 必须保留旧版本读取能力；
- Contract 激活通过 ReleaseManifest 或明确配置版本，不能运行时静默改变。

## 13. Requirement / Validation

| Requirement | Target | Test | Evidence |
| --- | --- | --- | --- |
| `ARCH-XMOD-001` | 所有共享 Contract 只有一个 Owner | `XMOD-001-UT, XMOD-001-IT` | `EV-XMOD-001` |
| `ARCH-XMOD-002` | Producer/Consumer/Storage/Failure Owner 完整 | `XMOD-002-UT, XMOD-002-IT` | `EV-XMOD-002` |
| `ARCH-XMOD-003` | SecurityEpoch/Generation/Deadline 按适用性贯通 | `XMOD-003-UT, XMOD-003-IT, XMOD-003-FT` | `EV-XMOD-003` |
| `ARCH-XMOD-004` | Receipt 不冒充领域成功 | `XMOD-004-UT, XMOD-004-IT, XMOD-004-FT` | `EV-XMOD-004` |
| `ARCH-XMOD-005` | PreparedAction Ownership 冲突合并前解决 | `XMOD-005-UT, XMOD-005-IT` | `EV-XMOD-005` |
| `ARCH-XMOD-006` | Mandatory Audit Backpressure 跨模块一致 | `XMOD-006-UT, XMOD-006-IT, XMOD-006-FT, XMOD-006-E2E` | `EV-XMOD-006` |
| `ARCH-XMOD-007` | Index Publish/Deletion/Recovery 协议一致 | `XMOD-007-UT, XMOD-007-IT, XMOD-007-FT, XMOD-007-E2E` | `EV-XMOD-007` |
| `ARCH-XMOD-008` | Contract Version/Enum Compatibility 可验证 | `XMOD-008-UT, XMOD-008-IT` | `EV-XMOD-008` |
| `ARCH-XMOD-009` | Failure Code 无重复冲突 | `XMOD-009-UT, XMOD-009-IT` | `EV-XMOD-009` |
| `ARCH-XMOD-010` | 每个 Confirmed Contract 有合并审计证据 | `XMOD-010-UT, XMOD-010-IT` | `EV-XMOD-010` |

## 14. Wave 1 合并前审计清单

```text
[ ] PR #17 / #18 / #19 / #20 均基于最新 main 重放或确认差异
[ ] Contract 名称、字段、枚举和版本对齐
[ ] Security Epoch / Secret / Credential Ownership 对齐
[ ] AuditEvent / TelemetryEnvelope / Mandatory Audit 对齐
[ ] UsageReceipt / QuotaReservation / CancellationReceipt 对齐
[ ] Index Batch / Receipt / Manifest / Cutover / Watermark 对齐
[ ] PreparedAction / ToolAttempt / EffectReceipt Owner 决议
[ ] Failure Code Registry 去重
[ ] Retry / Replan / Fallback / Recovery Owner 去重
[ ] 文档入口、镜像、验证器和测试同步
[ ] 未运行验证明确记录
[ ] 没有把 Parallel Proposal 或 Target 写成 Current
```

## 15. 当前结论

Wave 1 四个 Draft PR 的高层 Ownership 基本兼容，但字段级 Contract 尚未全部确认。当前状态是：

```text
design available
cross-module alignment in progress
implementation not established
quality not proven
production ready not established
```
