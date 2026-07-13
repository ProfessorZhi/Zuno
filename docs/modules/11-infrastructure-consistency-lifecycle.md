# 11 Infrastructure 一致性与生命周期附录

updated: 2026-07-13
status: normative-target-module-appendix
module_number: 11
parent_document: `docs/modules/11-infrastructure.md`
sibling_appendix: `docs/modules/11-infrastructure-data-services.md`
agent_mirror: `.agent/modules/11-infrastructure-consistency-lifecycle.md`
current_state_source: `docs/status/production-readiness.md`
contract_registry: `docs/governance/wave1-cross-module-contract-registry.md`

> 本附录补齐跨存储发布、删除、恢复、Mandatory Audit、租户隔离、可见性、升级、Adapter Conformance、SLO、网络、发布和成本归属的实施级 Target。主文档仍是第 11 模块唯一模块架构事实源。

## 1. 边界与选择

企业知识库一次写入、删除、恢复或升级可能同时触及 PostgreSQL、RabbitMQ、Object Store、Checkpointer、Milvus、Neo4j、BM25/Search、Redis、Trace/Audit Store 与 Secret/KMS。这些系统没有共同事务，必须使用版本、Receipt、Manifest、Watermark、Outbox/Inbox、Generation、Fencing 和 Reconciler 协调。

本文没有新增 Current 声明。Target 包含：

```text
Derived Index Lifecycle
Cross-store Publish / Deletion / Recovery
Mandatory Audit Durability / Backpressure
Tenant Isolation Profile
Write Visibility / Serving Watermark
Data-service Upgrade Compatibility
Local / Enterprise Adapter Conformance
Role-specific SLO / Capacity / Degradation
Network Plane
Release / Supply-chain Binding
Resource Usage Attribution
```

Explicitly Not Selected：

```text
跨数据服务 XA / 2PC
索引写成功即自动发布 KnowledgeVersion
删除只写 tombstone 就宣称完成
PITR 只恢复 PostgreSQL 就切回生产
Mandatory Audit 故障时无条件放行高风险副作用
用 Local Adapter 测试代替 Enterprise 故障测试
在线修改 active Milvus / Neo4j / BM25 schema
仅靠 Python 末端过滤实现租户隔离
```

## 2. 核心 Contract

### 2.1 派生索引

```python
class IndexBuildRun(BaseModel):
    build_run_id: str
    owner_module: Literal["KNOWLEDGE", "MEMORY"]
    tenant_id: str
    workspace_id: str
    index_kind: Literal["VECTOR", "GRAPH", "LEXICAL"]
    target_version: str
    source_snapshot_ref: str
    source_manifest_hash: str
    schema_spec_ref: str
    config_version: str
    idempotency_key: str
    deadline_at: datetime
    status: str

class IndexWriteBatch(BaseModel):
    batch_id: str
    build_run_id: str
    target_version: str
    item_identity_scheme: str
    item_count: int
    payload_ref: str
    payload_hash: str
    idempotency_key: str
    expected_generation: int
    tenant_scope_hash: str

class IndexWriteReceipt(BaseModel):
    receipt_id: str
    batch_id: str
    service_kind: str
    physical_target_ref: str
    attempt_no: int
    accepted_count: int
    rejected_count: int
    observed_generation: int
    service_commit_ref: str | None
    checksum_or_digest: str | None
    status: str

class IndexVerification(BaseModel):
    verification_id: str
    build_run_id: str
    target_version: str
    schema_match: bool
    count_match: bool
    lineage_match: bool
    tenant_filter_passed: bool
    representative_query_passed: bool
    status: Literal["PASSED", "FAILED", "QUARANTINED"]

class DerivedIndexReplica(BaseModel):
    replica_id: str
    owner_module: str
    index_kind: str
    tenant_id: str
    workspace_id: str
    version: str
    physical_ref: str
    schema_version: str
    source_snapshot_ref: str
    source_manifest_hash: str
    serving_generation: int
    status: str

class IndexCutover(BaseModel):
    cutover_id: str
    index_kind: str
    from_version: str | None
    to_version: str
    expected_serving_generation: int
    owner_approval_ref: str
    security_epoch: int
    deadline_at: datetime
    status: str

class IndexRebuildRun(BaseModel):
    rebuild_run_id: str
    stale_replica_ref: str
    reason_code: str
    source_snapshot_ref: str
    target_version: str
    verification_ref: str | None
    status: str

class IndexRetirement(BaseModel):
    retirement_id: str
    replica_ref: str
    earliest_delete_at: datetime
    active_snapshot_count: int
    legal_hold_refs: list[str]
    status: str

class IndexReconciliationFinding(BaseModel):
    finding_id: str
    owner_module: str
    index_kind: str
    expected_version: str
    observed_version: str | None
    reason_code: str
    repair_command_ref: str | None
    status: str
```

Infrastructure 拥有物理执行状态；`IndexManifest`、KnowledgeVersion、MemoryVersion 和质量结论仍由领域 Owner 拥有。

### 2.2 可见性

```python
class ServingWatermark(BaseModel):
    owner_module: str
    tenant_id: str
    workspace_id: str
    index_kind: str
    serving_version: str
    serving_generation: int
    source_generation: int
    visible_through_batch_id: str
    status: Literal["CURRENT", "LAGGING", "STALE", "BLOCKED"]

class WriteVisibilityReceipt(BaseModel):
    receipt_id: str
    write_receipt_ref: str
    consistency_class: Literal["IMMEDIATE", "READ_YOUR_WRITE", "BOUNDED_EVENTUAL", "EVENTUAL"]
    visible_at: datetime | None
    visibility_deadline_at: datetime
    serving_watermark_ref: str | None
    status: Literal["PENDING", "VISIBLE", "DEADLINE_EXCEEDED", "FAILED"]
```

服务接受写入、查询可见、物理验证、领域 Manifest 和领域版本激活是五个不同事实。

### 2.3 删除与撤销

```python
class DeletionRequest(BaseModel):
    deletion_id: str
    owner_module: str
    tenant_id: str
    workspace_id: str
    subject_type: str
    subject_id: str
    requested_by_ref: str
    security_epoch: int
    legal_hold_check_ref: str
    visibility_deadline_at: datetime
    physical_delete_not_before: datetime
    status: str

class DeletionTarget(BaseModel):
    deletion_id: str
    target_kind: Literal["POSTGRES_DOMAIN", "OBJECT", "VECTOR", "GRAPH", "LEXICAL", "CACHE", "CHECKPOINT_REF", "BACKUP"]
    target_ref: str
    required_action: Literal["TOMBSTONE", "HIDE", "DELETE", "PURGE", "REBUILD"]
    receipt_ref: str | None
    status: str

class DeletionVerification(BaseModel):
    deletion_id: str
    query_visibility_revoked: bool
    active_snapshot_refs: list[str]
    unresolved_target_refs: list[str]
    legal_hold_refs: list[str]
    status: Literal["PASSED", "PARTIAL", "BLOCKED"]
```

业务删除合法性归领域 Owner 和 Security；Infrastructure 执行目标清单、隐藏、清理、重试与验证。

### 2.4 一致恢复

```python
class RecoverySetManifest(BaseModel):
    recovery_set_id: str
    recovery_point_at: datetime
    postgres_lsn: str
    object_manifest_version: str
    checkpoint_generation: int
    outbox_sequence: int
    security_epoch: int
    config_version: str
    knowledge_versions: list[str]
    memory_versions: list[str]
    vector_watermarks: list[str]
    graph_watermarks: list[str]
    lexical_watermarks: list[str]
    backup_manifest_refs: list[str]
    status: str

class RecoverySetValidation(BaseModel):
    recovery_set_id: str
    domain_consistent: bool
    checkpoint_consistent: bool
    object_consistent: bool
    security_consistent: bool
    derived_indexes_consistent: bool
    stale_replica_refs: list[str]
    rebuild_required_refs: list[str]
    cutover_allowed: bool
    evidence_ref: str
```

### 2.5 Mandatory Audit

```python
class AuditDurabilityRequirement(BaseModel):
    audit_class: Literal["BEST_EFFORT", "DURABLE", "MANDATORY_BEFORE_EFFECT"]
    event_catalog_id: str
    owner_module: str
    local_persistence_required: bool
    external_delivery_required: bool
    max_buffer_age_seconds: int
    fail_mode: Literal["DEGRADE", "REJECT", "BLOCK_EFFECT"]

class AuditBufferReservation(BaseModel):
    reservation_id: str
    tenant_id: str
    audit_class: str
    units: int
    deadline_at: datetime
    status: str

class AuditPersistenceReceipt(BaseModel):
    audit_event_id: str
    local_commit_ref: str
    outbox_ref: str | None
    integrity_chain_ref: str
    status: Literal["COMMITTED", "DUPLICATE", "FAILED"]
```

Security 或领域模块决定审计等级；Infrastructure 只执行 durability 和 backpressure。

### 2.6 隔离、兼容、Conformance、SLO 与发布

```python
class TenantIsolationProfile(BaseModel):
    service_kind: str
    isolation_class: Literal["SHARED_WITH_ENFORCED_SCOPE", "NAMESPACE_PER_TENANT", "DATABASE_PER_TENANT", "DEDICATED_DEPLOYMENT"]
    scope_injection_mode: str
    physical_policy_ref: str
    encryption_context_required: bool

class ServiceCompatibilityEntry(BaseModel):
    service_kind: str
    application_version: str
    adapter_version: str
    server_version: str
    schema_version: str
    read_compatible_versions: list[str]
    write_compatible_versions: list[str]
    rollback_compatible_versions: list[str]

class AdapterConformanceProfile(BaseModel):
    adapter_name: str
    service_kind: str
    deployment_class: Literal["LOCAL", "ENTERPRISE"]
    supported_semantics: list[str]
    unsupported_semantics: list[str]
    fail_fast_on_unsupported: bool
    conformance_suite_version: str

class ServiceCriticalityProfile(BaseModel):
    role: str
    service_kind: str
    criticality: Literal["REQUIRED", "DEGRADED_ALLOWED", "OPTIONAL", "REBUILDABLE"]
    readiness_behavior: str
    degradation_policy_ref: str

class ReleaseManifest(BaseModel):
    release_id: str
    application_image_digest: str
    sbom_ref: str
    signature_ref: str
    config_versions: list[str]
    migration_versions: list[str]
    adapter_versions: list[str]
    data_service_compatibility_ref: str
    rollback_release_ref: str | None

class ResourceUsageAttribution(BaseModel):
    attribution_id: str
    tenant_id: str
    workspace_id: str | None
    run_id: str | None
    service_kind: str
    resource_class: str
    units: float
    source_receipt_ref: str
```

## 3. 状态机与不变量

### 3.1 Index Lifecycle

```text
DECLARED → SOURCE_PINNED → PROVISIONING → BUILDING → VERIFYING
→ READY_FOR_OWNER_ACCEPTANCE → ACCEPTED → CUTTING_OVER → SERVING

BUILDING/VERIFYING → FAILED → RETRY_WAIT | REBUILDING | ABORTED
READY_FOR_OWNER_ACCEPTANCE → REJECTED
CUTTING_OVER → CONFLICT | ROLLED_BACK
SERVING → STALE | RETIRING
STALE → REBUILDING
RETIRING → RETIRED
* → QUARANTINED
```

- Infrastructure Verification 只证明 Schema、Count、Scope、Lineage 和代表性查询等物理条件。
- 领域 Acceptance 负责质量、SourceSpan、ACL、Manifest 和可服务结论。
- Cutover 使用 expected generation/CAS；Receipt 丢失后先对账 Watermark，不能再次无条件切换。
- Active Snapshot 未释放、Retention 未到或 Legal Hold 生效时不能删除旧版本。

### 3.2 Cross-store Deletion

```text
REQUESTED → AUTHORIZED → LEGAL_HOLD_CHECKING → TOMBSTONED_IN_DOMAIN
→ QUERY_VISIBILITY_REVOKING → QUERY_VISIBILITY_REVOKED
→ PHYSICAL_DELETE_PENDING → PHYSICAL_DELETING → VERIFYING → COMPLETED

LEGAL_HOLD_CHECKING → BLOCKED_LEGAL_HOLD
QUERY_VISIBILITY_REVOKING → PARTIAL_VISIBILITY_REVOKED
PHYSICAL_DELETING → PARTIAL_DELETE
PARTIAL_* → RETRY_WAIT | RECONCILING
VERIFYING → FAILED_VERIFICATION
```

- Visibility Deadline 优先于物理删除完成时间；到期仍可检索必须 fail-closed。
- Milvus、Neo4j、BM25 或 Redis 删除失败不能恢复内容可见性。
- Legal Hold 可阻止物理 Purge，但是否阻止前台隐藏由 Security/Policy Owner 决定。
- 完成必须有跨服务 `DeletionVerification`。

### 3.3 Recovery Set

```text
REQUESTED → LOCATING_ARTIFACTS → RESTORING_ISOLATED_TARGET
→ ALIGNING_DOMAIN_OBJECT_CHECKPOINT → CLASSIFYING_DERIVED_INDEXES
→ REBUILDING_REQUIRED_INDEXES → VERIFYING_SECURITY_AND_CONFIG
→ READY_FOR_CUTOVER → CUTTING_OVER → COMPLETED

* → FAILED → CLEANING_UP → ABORTED
CUTTING_OVER → ROLLED_BACK
```

- PostgreSQL、Object Store、Checkpoint、Outbox 和 Security Epoch 必须一致。
- 派生索引领先恢复点时 `QUARANTINED`，落后时 `STALE/REBUILDING`。
- Redis 默认冷启动重建，不进入权威 Recovery Set。
- `cutover_allowed=false` 时自动化不得切生产。

### 3.4 Mandatory Audit Backpressure

```text
REQUIRED → CAPACITY_RESERVED → LOCAL_COMMITTING → LOCAL_COMMITTED
→ OUTBOX_PENDING → EXTERNAL_DELIVERING → DELIVERED

CAPACITY_RESERVED → REJECTED_CAPACITY
LOCAL_COMMITTING → FAILED_LOCAL_COMMIT
OUTBOX_PENDING/EXTERNAL_DELIVERING → RETRY_WAIT | DEAD_LETTERED
```

| Audit Class | Local 不可用 | External Sink 不可用 | Buffer 满 |
| --- | --- | --- | --- |
| `BEST_EFFORT` | 可按策略丢弃调试事件并计数 | 降级 | 丢弃并告警 |
| `DURABLE` | 降级或拒绝，不能伪造成功 | Local + Outbox 重试 | backpressure / retryable reject |
| `MANDATORY_BEFORE_EFFECT` | `BLOCK_EFFECT` | Local 已提交后可按策略异步外送 | `BLOCK_EFFECT` |

Break-glass、Approval、权限变更、Credential 使用、不可逆 Tool Effect 和跨租户异常默认不得低于 `MANDATORY_BEFORE_EFFECT`，最终目录由 Security 冻结。

### 3.5 Upgrade Compatibility

```text
PLANNED → COMPATIBILITY_CHECKING → PROVISIONING_PARALLEL_TARGET
→ DUAL_SUPPORT → BACKFILLING → VERIFYING → CUTTING_OVER
→ OBSERVING → CONTRACTING_OLD_VERSION → COMPLETED

COMPATIBILITY_CHECKING → BLOCKED
BACKFILLING/VERIFYING → FAILED
CUTTING_OVER/OBSERVING → ROLLING_BACK
FAILED → FORWARD_FIXING | ABORTED
```

PostgreSQL 使用 Expand/Contract；RabbitMQ 使用 versioned routing；Milvus/Neo4j/BM25 使用并行版本、回填、验证和 alias/routing cutover；Redis 使用 versioned namespace 或 cold rebuild；Checkpoint 必须保留旧 Run 的 graph/state compatibility。

## 4. PreparedAction 与 Tool Effect Ownership

```text
Agent Core
    owns ActionProposalRef、Step/Plan orchestration binding、控制决策。
Tool Runtime
    owns ExecutablePreparedAction、ToolAttempt、EffectReceipt、EffectReconciliation。
Security
    owns ApprovalBinding、PreparedAction canonical hash、SecurityEpoch、AuthorizationDecision。
Infrastructure
    owns IdempotencyClaim、Lease/Fencing、Transaction/Outbox、Audit Durability 和物理 Receipt primitive。
```

Queue ACK、Lease release、Audit delivery 或 ObjectCommit 都不能被当成 Tool Effect 成功。

## 5. Tenant Isolation Profile

| Service | 默认 Target | 强隔离选项 | 强制故障测试 |
| --- | --- | --- | --- |
| PostgreSQL | enforced tenant/workspace scope；高安全可 RLS | schema/database per tenant | scope、FK/unique、RLS bypass |
| RabbitMQ | scoped envelope/routing/queue | vhost per tenant | binding、DLQ、redelivery 泄露 |
| Object Store | prefix + bucket policy + encryption context | bucket/account per tenant | list/get/put/delete 越权 |
| Milvus | database/collection/partition + mandatory filter | dedicated database/deployment | filter omission、alias scope |
| Neo4j | database 或 tenant property/label scope | dedicated database/deployment | traversal 和 aggregation 泄露 |
| BM25/Search | index/alias 或 mandatory filter | index/deployment per tenant | query/aggregation 泄露 |
| Redis | tenant namespace + ACL | dedicated instance | collision、scan、TTL 隔离 |
| Checkpointer | thread/namespace + tenant binding | schema/database per tenant | cross-thread resume |

应用末端过滤不能作为唯一隔离措施。

## 6. Visibility、Conformance、SLO、Network 与 Release

- PostgreSQL commit 后可读；RabbitMQ 只承诺 at-least-once；Object Store 只读取 committed metadata + hash/version 匹配对象。
- Milvus、Neo4j、BM25 的一致性由 `WriteVisibilityReceipt` 声明；Query 固定 Knowledge/Memory Snapshot，不能静默混用版本。
- Local Adapter 必须列出 unsupported semantics 并 fail-fast。SQLite、in-process Queue、local vector/graph adapter 不能证明真实 PostgreSQL、RabbitMQ、Milvus、Neo4j 故障语义。
- 所有 Adapter 共用 Contract Test；Enterprise Adapter 额外运行真实 Integration、Fault、E2E、Backup/Restore/Rebuild。
- Role-specific Criticality 区分 `REQUIRED`、`DEGRADED_ALLOWED`、`OPTIONAL`、`REBUILDABLE`；未启用的 Retriever 故障不能无条件拖垮全部问答。
- SLO 数字必须由真实 workload 冻结，至少测量 p95/p99、Queue Age、Outbox Lag、Watermark Lag、Rebuild Throughput、RPO、RTO、Stale Duration 和 Tenant Fairness。
- Network Plane 提供 Ingress/Egress 执行、DNS、TLS/mTLS、证书轮换、Outbound Proxy、连接 Drain、Partition 检测和 Timeout；Security 决定策略。
- Release 必须绑定 Commit、Image Digest、SBOM、Signature/Provenance、Config、Migration、Adapter 和 Compatibility Matrix；不要求 Kubernetes。
- Infrastructure 产生 PostgreSQL、RabbitMQ、Object Store、Milvus、Neo4j、Search、Redis、Backup/Rebuild 的物理用量 Receipt；业务预算与收费语义归上层 Owner。

## 7. Failure Taxonomy

```text
INFRA_INDEX_BUILD_SOURCE_CHANGED
INFRA_INDEX_WRITE_VISIBILITY_DEADLINE
INFRA_INDEX_OWNER_ACCEPTANCE_REJECTED
INFRA_INDEX_CUTOVER_GENERATION_CONFLICT
INFRA_INDEX_ACTIVE_SNAPSHOT_BLOCKS_RETIREMENT
INFRA_DELETION_LEGAL_HOLD_BLOCKED
INFRA_DELETION_VISIBILITY_DEADLINE
INFRA_DELETION_PARTIAL
INFRA_DELETION_VERIFICATION_FAILED
INFRA_RECOVERY_SET_INCONSISTENT
INFRA_RECOVERY_CUTOVER_BLOCKED
INFRA_AUDIT_CAPACITY_EXHAUSTED
INFRA_AUDIT_LOCAL_PERSISTENCE_FAILED
INFRA_MANDATORY_AUDIT_BLOCK_EFFECT
INFRA_TENANT_ISOLATION_PROFILE_MISSING
INFRA_CROSS_TENANT_HIT
INFRA_WRITE_VISIBILITY_DEADLINE
INFRA_SERVICE_COMPATIBILITY_BLOCKED
INFRA_ADAPTER_SEMANTIC_UNSUPPORTED
INFRA_RELEASE_PROVENANCE_INVALID
INFRA_NETWORK_POLICY_DENIED
INFRA_RESOURCE_ATTRIBUTION_MISSING
```

Failure 必须携带 Owner、Scope、Retryability、Deadline、Security Epoch、Generation、Evidence Ref 和 Recovery Action。

## 8. Crash / Partition Matrix

| 场景 | 恢复动作 | 禁止 |
| --- | --- | --- |
| Index 物理 commit 后 Receipt 前崩溃 | 用 Batch ID/Version verify + upsert | 直接激活版本 |
| Manifest commit 后 Cutover 前崩溃 | 重试 generation/CAS | 静默混读新旧版本 |
| Alias 已切换但 Receipt 丢失 | 对账 ServingWatermark，补写 Receipt | 再次无条件切换 |
| Tombstone 后索引删除失败 | 保持 fail-closed 隐藏并重试 | 恢复可见性 |
| 清理中 Legal Hold 生效 | 停止 Purge，记录已执行 Receipt | 删除受保护副本 |
| PITR 后派生索引领先 | Quarantine + Rebuild | 直接服务 |
| Mandatory Audit local commit 前崩溃 | Effect 不执行或重试 | 推断 Effect 已执行 |
| Audit committed、Effect 前崩溃 | Tool Runtime Reconcile | Infrastructure 标记 Effect Success |
| 网络分区旧 Worker 恢复 | Stale Fencing Token 拒绝 | 晚到覆盖 |
| Upgrade 双写分叉 | Pause Cutover，Reconcile/Forward-fix | Contract 旧版本 |

## 9. Requirement / Test / Evidence

| Requirement | Target | Required Tests | Evidence |
| --- | --- | --- | --- |
| `ARCH-INFRA-LC-001` | Receipt、Verification、Manifest、Activation 分层 | `INFRA-LC-001-UT, INFRA-LC-001-IT` | `EV-INFRA-LC-001` |
| `ARCH-INFRA-LC-002` | ServingWatermark 与 Visibility 明确 | `INFRA-LC-002-UT, INFRA-LC-002-IT, INFRA-LC-002-FT` | `EV-INFRA-LC-002` |
| `ARCH-INFRA-LC-003` | Cutover 使用 generation/CAS | `INFRA-LC-003-UT, INFRA-LC-003-IT, INFRA-LC-003-FT` | `EV-INFRA-LC-003` |
| `ARCH-INFRA-LC-004` | Active Snapshot 阻止错误退休 | `INFRA-LC-004-UT, INFRA-LC-004-IT` | `EV-INFRA-LC-004` |
| `ARCH-INFRA-LC-005` | 删除先撤销可见性再清理 | `INFRA-LC-005-UT, INFRA-LC-005-IT, INFRA-LC-005-FT, INFRA-LC-005-E2E` | `EV-INFRA-LC-005` |
| `ARCH-INFRA-LC-006` | Legal Hold 与删除协调 | `INFRA-LC-006-UT, INFRA-LC-006-IT, INFRA-LC-006-FT` | `EV-INFRA-LC-006` |
| `ARCH-INFRA-LC-007` | 删除有跨服务 Verification | `INFRA-LC-007-UT, INFRA-LC-007-IT, INFRA-LC-007-E2E` | `EV-INFRA-LC-007` |
| `ARCH-INFRA-LC-008` | RecoverySet 对齐所有 Watermark | `INFRA-LC-008-UT, INFRA-LC-008-IT, INFRA-LC-008-FT, INFRA-LC-008-E2E` | `EV-INFRA-LC-008` |
| `ARCH-INFRA-LC-009` | Recovery Cutover 显式允许 | `INFRA-LC-009-UT, INFRA-LC-009-IT, INFRA-LC-009-FT` | `EV-INFRA-LC-009` |
| `ARCH-INFRA-LC-010` | Mandatory Audit durable 后才可 Effect | `INFRA-LC-010-UT, INFRA-LC-010-IT, INFRA-LC-010-FT, INFRA-LC-010-E2E` | `EV-INFRA-LC-010` |
| `ARCH-INFRA-LC-011` | Audit Capacity 有 fail-mode | `INFRA-LC-011-UT, INFRA-LC-011-IT, INFRA-LC-011-FT` | `EV-INFRA-LC-011` |
| `ARCH-INFRA-LC-012` | PreparedAction 四方 Ownership | `INFRA-LC-012-UT, INFRA-LC-012-IT` | `EV-INFRA-LC-012` |
| `ARCH-INFRA-LC-013` | 每种服务有 TenantIsolationProfile | `INFRA-LC-013-UT, INFRA-LC-013-IT, INFRA-LC-013-FT` | `EV-INFRA-LC-013` |
| `ARCH-INFRA-LC-014` | Cross-tenant Hit fail-closed | `INFRA-LC-014-UT, INFRA-LC-014-IT, INFRA-LC-014-FT, INFRA-LC-014-E2E` | `EV-INFRA-LC-014` |
| `ARCH-INFRA-LC-015` | Visibility 等级不静默假设 | `INFRA-LC-015-UT, INFRA-LC-015-IT, INFRA-LC-015-FT` | `EV-INFRA-LC-015` |
| `ARCH-INFRA-LC-016` | Upgrade Compatibility 版本化 | `INFRA-LC-016-UT, INFRA-LC-016-IT, INFRA-LC-016-FT` | `EV-INFRA-LC-016` |
| `ARCH-INFRA-LC-017` | 派生索引并行版本和回滚 | `INFRA-LC-017-UT, INFRA-LC-017-IT, INFRA-LC-017-FT, INFRA-LC-017-E2E` | `EV-INFRA-LC-017` |
| `ARCH-INFRA-LC-018` | Local/Enterprise 共用 Conformance | `INFRA-LC-018-UT, INFRA-LC-018-IT` | `EV-INFRA-LC-018` |
| `ARCH-INFRA-LC-019` | Unsupported Local semantics fail-fast | `INFRA-LC-019-UT, INFRA-LC-019-IT` | `EV-INFRA-LC-019` |
| `ARCH-INFRA-LC-020` | Role-specific Readiness/Degradation | `INFRA-LC-020-UT, INFRA-LC-020-IT, INFRA-LC-020-FT` | `EV-INFRA-LC-020` |
| `ARCH-INFRA-LC-021` | SLO 由真实 workload 冻结 | `INFRA-LC-021-UT, INFRA-LC-021-IT` | `EV-INFRA-LC-021` |
| `ARCH-INFRA-LC-022` | Network/TLS/Drain/Retry 边界 | `INFRA-LC-022-UT, INFRA-LC-022-IT, INFRA-LC-022-FT` | `EV-INFRA-LC-022` |
| `ARCH-INFRA-LC-023` | ReleaseManifest 绑定 Provenance | `INFRA-LC-023-UT, INFRA-LC-023-IT` | `EV-INFRA-LC-023` |
| `ARCH-INFRA-LC-024` | Resource Attribution 可关联租户和 Run | `INFRA-LC-024-UT, INFRA-LC-024-IT` | `EV-INFRA-LC-024` |

Mandatory Fault/E2E：

```text
Index Receipt Lost After Physical Commit
Manifest Committed Before Cutover Crash
Cutover Receipt Lost After Alias Switch
Visibility Deadline Exceeded
Active Snapshot Blocks Retirement
Deletion Partial Across Vector / Graph / Lexical
Deletion Visibility Deadline
Legal Hold Arrives During Purge
PITR With Ahead / Behind Derived Index
Mandatory Audit Local Store Failure
Mandatory Audit Capacity Exhaustion
Audit Committed Before Tool Effect Crash
Tenant Filter Omission / Cross-tenant Hit
Milvus / Neo4j / BM25 Upgrade Rollback
Local Adapter Unsupported Semantic
Network Partition With Stale Worker
Unsigned Release Rejected
Resource Attribution Missing
```

## 10. Target Code 与完成证据

```text
src/backend/zuno/infrastructure/
├── contracts/{index_lifecycle,deletion,recovery_set,audit_durability,tenant_isolation,compatibility,conformance,service_levels,release,attribution}.py
├── application/{index_lifecycle,deletion,recovery_set,audit_admission,upgrade,reconciliation}_service.py
└── operations/{network,conformance,service_levels,release_validation,attribution}.py

infra/{network,certificates,release,sbom,conformance,benchmarks,runbooks}/
```

Target 提升为 Current 必须具备代码、Migration/Index Version、真实服务 Integration、Fault/E2E、Crash/Partition/Idempotency、安全隔离、Backup/Restore/Rebuild/Deletion 演练、SLO/Capacity Measurement、Trace/Audit、Runbook、Rollback、Release Provenance 和 production-readiness 更新。
