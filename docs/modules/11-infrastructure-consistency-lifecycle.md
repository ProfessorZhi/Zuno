# 11 Infrastructure 一致性与生命周期附录

updated: 2026-07-13
status: normative-target-module-appendix
module_number: 11
parent_document: `docs/modules/11-infrastructure.md`
sibling_appendix: `docs/modules/11-infrastructure-data-services.md`
agent_mirror: `.agent/modules/11-infrastructure-consistency-lifecycle.md`
current_state_source: `docs/status/production-readiness.md`
contract_registry: `docs/governance/wave1-cross-module-contract-registry.md`

> 本附录补齐第 11 模块在跨存储发布、删除、恢复、审计背压、租户隔离、可见性、升级兼容、Adapter Conformance、SLO、网络、供应链和成本归属上的实施级 Target 规范。
>
> 它不把任何 Target 提升为 Current，也不替 Knowledge、Memory、Security、Observability、Model Gateway、Agent Core 或 Tool Runtime 决定领域结论。主文档仍是第 11 模块唯一模块架构事实源。

## 1. 需要解决的问题

企业知识库不是单数据库系统。一次写入、删除、恢复或升级可能同时触及：

```text
PostgreSQL
RabbitMQ
Object Store
LangGraph Checkpointer
Milvus
Neo4j
BM25 / Search
Redis
Trace / Audit Store
Secret Manager / KMS
```

这些系统没有共同事务。仅定义 Adapter 和健康检查不足以保证：

- 物理索引写成功后领域版本不会被错误激活；
- 删除后敏感内容不会继续被检索；
- PITR 后不会让旧索引配合新数据库继续服务；
- Mandatory Audit 不可用时高风险动作不会绕过审计；
- Local Adapter 通过测试不代表 Enterprise 故障语义被证明；
- 服务升级、Embedding 维度变化和索引 Schema 变化可以安全回滚；
- 租户过滤遗漏不会形成跨租户泄露；
- 容量和成本可以按 Tenant、Workspace、Run 与服务归属。

本附录把这些问题固化为 typed contract、状态机、故障码、测试和证据要求。

## 2. Current / Target / Future / Not Selected

### 2.1 Current

本附录没有新增 Current 声明。当前仍以 `docs/status/production-readiness.md` 和最新 `main` 的代码、测试、Migration 与运行证据为准。

### 2.2 Target

```text
Derived Index Lifecycle
Cross-store Publish / Reconcile
Cross-store Deletion / Revocation
Consistent Recovery Set
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

### 2.3 Future Optional

- 多区域 standby、read replica 和跨区域恢复自动化。
- Kubernetes Operator、Service Mesh 和自动证书轮换平台。
- Managed service 专用控制平面。
- 高级成本优化器和跨服务自动容量重平衡。

### 2.4 Explicitly Not Selected

```text
跨数据服务 XA / 2PC
索引写成功即自动发布 KnowledgeVersion
删除请求仅写一个 tombstone 就宣称完成
PITR 只恢复 PostgreSQL 就直接切回生产
Mandatory Audit 故障时无条件放行高风险副作用
用 Local Adapter 测试代替真实 Enterprise 集成和故障测试
在线修改 active Milvus / Neo4j / BM25 schema 而无版本切换
仅靠 Python 末端过滤实现多租户隔离
用 Redis、Milvus、Neo4j 或 Queue 代替权威领域事实
```

## 3. 核心对象

### 3.1 派生索引对象

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
    status: str
    created_at: datetime
    deadline_at: datetime
    trace_id: str

class IndexWriteBatch(BaseModel):
    batch_id: str
    build_run_id: str
    index_kind: str
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
    write_visibility_state: str
    service_commit_ref: str | None
    checksum_or_digest: str | None
    completed_at: datetime
    trace_id: str

class IndexVerification(BaseModel):
    verification_id: str
    build_run_id: str
    target_version: str
    schema_match: bool
    count_match: bool
    lineage_match: bool
    tenant_filter_passed: bool
    representative_query_passed: bool
    quality_evidence_ref: str | None
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
    retention_policy_ref: str

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
    status: str
    verification_ref: str | None

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
    severity: str
    reason_code: str
    repair_command_ref: str | None
    status: str
```

Infrastructure 拥有这些对象的物理执行和运行状态；`IndexManifest`、KnowledgeVersion、MemoryVersion 与质量判断仍由领域 Owner 拥有。

### 3.2 可见性与一致性对象

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
    verified_at: datetime
    status: Literal["CURRENT", "LAGGING", "STALE", "BLOCKED"]

class WriteVisibilityReceipt(BaseModel):
    receipt_id: str
    write_receipt_ref: str
    consistency_class: Literal[
        "IMMEDIATE",
        "READ_YOUR_WRITE",
        "BOUNDED_EVENTUAL",
        "EVENTUAL",
    ]
    visible_at: datetime | None
    visibility_deadline_at: datetime
    serving_watermark_ref: str | None
    status: Literal["PENDING", "VISIBLE", "DEADLINE_EXCEEDED", "FAILED"]
```

“服务端接受写入”与“查询路径可见”必须分开。领域模块只有在需要的 `ServingWatermark` 满足版本和安全条件时，才能激活或继续服务。

### 3.3 删除、撤销与清理对象

```python
class DeletionRequest(BaseModel):
    deletion_id: str
    owner_module: str
    tenant_id: str
    workspace_id: str
    subject_type: str
    subject_id: str
    reason_code: str
    requested_by_ref: str
    security_epoch: int
    legal_hold_check_ref: str
    visibility_deadline_at: datetime
    physical_delete_not_before: datetime
    status: str

class DeletionTarget(BaseModel):
    deletion_id: str
    target_kind: Literal[
        "POSTGRES_DOMAIN",
        "OBJECT",
        "VECTOR",
        "GRAPH",
        "LEXICAL",
        "CACHE",
        "CHECKPOINT_REF",
        "BACKUP",
    ]
    target_ref: str
    required_action: Literal["TOMBSTONE", "HIDE", "DELETE", "PURGE", "REBUILD"]
    status: str
    attempt_count: int
    receipt_ref: str | None

class DeletionVerification(BaseModel):
    deletion_id: str
    query_visibility_revoked: bool
    active_snapshot_refs: list[str]
    unresolved_target_refs: list[str]
    legal_hold_refs: list[str]
    verified_at: datetime
    status: Literal["PASSED", "PARTIAL", "BLOCKED"]
```

删除请求的业务合法性由领域 Owner 与 Security 决定；Infrastructure 负责执行目标清单、隐藏、物理清理、重试、验证和证据。

### 3.4 一致恢复对象

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

### 3.5 Mandatory Audit 对象

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
    persisted_at: datetime
    status: Literal["COMMITTED", "DUPLICATE", "FAILED"]
```

Security 或领域模块决定某事件是否必须审计；Infrastructure 只执行对应 durability class 和 backpressure。

### 3.6 隔离、兼容与适配器对象

```python
class TenantIsolationProfile(BaseModel):
    profile_id: str
    service_kind: str
    isolation_class: Literal[
        "SHARED_WITH_ENFORCED_SCOPE",
        "NAMESPACE_PER_TENANT",
        "DATABASE_PER_TENANT",
        "DEDICATED_DEPLOYMENT",
    ]
    scope_injection_mode: str
    physical_policy_ref: str
    encryption_context_required: bool
    cross_tenant_fault_test_ref: str

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
    evidence_ref: str | None
```

### 3.7 SLO、发布与成本对象

```python
class ServiceCriticalityProfile(BaseModel):
    role: str
    service_kind: str
    criticality: Literal["REQUIRED", "DEGRADED_ALLOWED", "OPTIONAL", "REBUILDABLE"]
    readiness_behavior: str
    degradation_policy_ref: str
    recovery_objective_ref: str

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
    measured_at: datetime
    source_receipt_ref: str
```

## 4. 派生索引完整生命周期

### 4.1 IndexBuildRun State Machine

```text
DECLARED
→ SOURCE_PINNED
→ PROVISIONING
→ BUILDING
→ VERIFYING
→ READY_FOR_OWNER_ACCEPTANCE
→ ACCEPTED
→ CUTTING_OVER
→ SERVING

BUILDING/VERIFYING → FAILED
FAILED → RETRY_WAIT | REBUILDING | ABORTED
READY_FOR_OWNER_ACCEPTANCE → REJECTED
CUTTING_OVER → CONFLICT | ROLLED_BACK
SERVING → STALE | RETIRING
STALE → REBUILDING
RETIRING → RETIRED
* → QUARANTINED
```

规则：

- `SOURCE_PINNED` 固定 PostgreSQL/Object Store 权威输入和 hash。
- Infrastructure 的 `VERIFYING` 只验证物理完整性、Schema、Count、Scope 和代表性查询。
- 领域 Owner 的 Acceptance 负责质量、Lineage、ACL、SourceSpan 和 IndexManifest。
- `CUTTING_OVER` 使用 expected serving generation 和 CAS；冲突不自动覆盖。
- `SERVING` 后继续监测 Watermark、Schema drift、跨租户命中和物理损坏。

### 4.2 Write / Visibility / Manifest Boundary

```text
IndexWriteReceipt
    证明一次物理写尝试及其接收结果。
WriteVisibilityReceipt
    证明对应写入在何种一致性等级下已可查询。
IndexVerification
    证明物理版本通过 Infrastructure 验证。
IndexManifest
    由 Knowledge / Memory 拥有，证明领域版本组成和验证结果。
KnowledgeVersion / MemoryVersion
    由领域 Owner 激活。
ServingWatermark
    证明查询路径当前服务到哪个版本和 generation。
```

任意一个 Receipt 都不能独立替代 `IndexManifest` 或领域版本激活。

## 5. 跨存储删除与撤销

### 5.1 Deletion State Machine

```text
REQUESTED
→ AUTHORIZED
→ LEGAL_HOLD_CHECKING
→ TOMBSTONED_IN_DOMAIN
→ QUERY_VISIBILITY_REVOKING
→ QUERY_VISIBILITY_REVOKED
→ PHYSICAL_DELETE_PENDING
→ PHYSICAL_DELETING
→ VERIFYING
→ COMPLETED

LEGAL_HOLD_CHECKING → BLOCKED_LEGAL_HOLD
QUERY_VISIBILITY_REVOKING → PARTIAL_VISIBILITY_REVOKED
PHYSICAL_DELETING → PARTIAL_DELETE
PARTIAL_* → RETRY_WAIT | RECONCILING
VERIFYING → FAILED_VERIFICATION
* → CANCELLED（仅在领域 tombstone 前）
```

### 5.2 删除不变量

- 领域 tombstone 是删除事实源；Infrastructure 不自行创建业务删除结论。
- `visibility_deadline_at` 优先于物理删除完成时间。到期仍可检索必须 fail-closed、隔离相关版本并告警。
- Milvus、Neo4j、BM25、Redis 中任一删除失败，不得恢复已撤销的查询可见性。
- active KnowledgeSnapshot 可以保留物理副本，但必须服从 Security 和删除策略；高风险撤销可以使旧 Snapshot 失效。
- Legal Hold 阻止物理 purge，但不一定阻止前台隐藏；具体规则由 Security/Policy Owner 决定。
- Backup 中数据按 Retention 和 Legal Hold 到期，不得把 Backup expiry 当实时删除机制。
- 删除完成必须有 `DeletionVerification`，包括跨服务查询验证和未解决目标列表。

## 6. Consistent Recovery Set

### 6.1 RecoverySet State Machine

```text
REQUESTED
→ LOCATING_ARTIFACTS
→ RESTORING_ISOLATED_TARGET
→ ALIGNING_DOMAIN_OBJECT_CHECKPOINT
→ CLASSIFYING_DERIVED_INDEXES
→ REBUILDING_REQUIRED_INDEXES
→ VERIFYING_SECURITY_AND_CONFIG
→ READY_FOR_CUTOVER
→ CUTTING_OVER
→ COMPLETED

* → FAILED
FAILED → CLEANING_UP → ABORTED
READY_FOR_CUTOVER → REJECTED
CUTTING_OVER → ROLLED_BACK
```

### 6.2 恢复规则

- PostgreSQL、Object Store、Checkpoint、Outbox 和 Security Epoch 必须形成一致基线。
- Milvus、Neo4j 和 BM25 可以通过 Snapshot 恢复，也可以从权威输入重建，但必须有 Watermark 和验证。
- 恢复后的派生索引版本若晚于 PostgreSQL 领域事实，必须 `QUARANTINED`；若早于领域事实，必须 `STALE/REBUILDING`。
- Redis 默认冷启动重建，不进入权威 Recovery Set。
- Queue 中可由 Outbox 重建的消息不得在恢复后重复产生领域副作用。
- `cutover_allowed=false` 时任何自动化不得切换生产。

## 7. Mandatory Audit Durability 与背压

### 7.1 Audit Persistence State Machine

```text
REQUIRED
→ CAPACITY_RESERVED
→ LOCAL_COMMITTING
→ LOCAL_COMMITTED
→ OUTBOX_PENDING
→ EXTERNAL_DELIVERING
→ DELIVERED

CAPACITY_RESERVED → REJECTED_CAPACITY
LOCAL_COMMITTING → FAILED_LOCAL_COMMIT
OUTBOX_PENDING/EXTERNAL_DELIVERING → RETRY_WAIT | DEAD_LETTERED
```

### 7.2 Backpressure Matrix

| Audit Class | Local Store unavailable | External Sink unavailable | Buffer exhausted |
| --- | --- | --- | --- |
| `BEST_EFFORT` | 允许丢弃受策略允许的非敏感调试事件并计数 | 降级 | 丢弃并告警 |
| `DURABLE` | 请求降级或拒绝，不能伪造成功 | Local + Outbox 保留并重试 | backpressure / reject retryable |
| `MANDATORY_BEFORE_EFFECT` | `BLOCK_EFFECT`，高风险副作用不得执行 | Local 已提交可允许 effect，External 异步重试，除非策略要求同步 | `BLOCK_EFFECT` 或 fail-closed |

Break-glass、Approval、权限变更、Credential 使用、不可逆 Tool effect 和跨租户隔离异常默认不得低于 `MANDATORY_BEFORE_EFFECT`，最终目录由 Security 冻结。

## 8. PreparedAction / Tool Effect Boundary

该冲突必须在 Tool Runtime 设计前冻结：

```text
Agent Core
    owns ActionProposalRef、Step/Plan orchestration binding、控制决策。
Tool Runtime
    owns ExecutablePreparedAction、ToolAttempt、EffectReceipt、EffectReconciliation。
Security
    owns ApprovalBinding、PreparedAction canonical hash、SecurityEpoch、AuthorizationDecision。
Infrastructure
    owns IdempotencyClaim、Lease/Fencing、transaction/outbox、audit durability 和物理 receipt primitive。
```

Infrastructure 不创建 Tool 业务成功状态，也不把 Queue ACK、Lease release 或 Audit delivery 当成 Tool effect 成功。

## 9. Tenant Isolation Profile

### 9.1 服务级选择

| Service | 默认 Target | 可升级隔离 | 必须验证 |
| --- | --- | --- | --- |
| PostgreSQL | shared schema + enforced tenant/workspace scope；高安全可 RLS | schema/database per tenant | query context、FK/unique scope、RLS bypass |
| RabbitMQ | shared vhost + scoped routing/queue policy | vhost per tenant | envelope scope、binding、DLQ 泄露 |
| Object Store | scoped prefix + bucket policy + encryption context | bucket/account per tenant | list/get/put/delete policy |
| Milvus | database/collection/partition + enforced metadata filter，按版本隔离 | dedicated database/deployment | filter omission、alias scope、cross-tenant hit |
| Neo4j | database 或强制 tenant property/label scope | database/deployment per tenant | traversal scope、index/constraint scope |
| BM25/Search | index/alias 或 shared index + mandatory filter | index/deployment per tenant | query filter、aggregation leakage |
| Redis | namespace + tenant-scoped key + ACL | dedicated instance | key collision、scan exposure、TTL isolation |
| Checkpointer | thread/namespace + tenant binding | dedicated schema/database | cross-thread/cross-tenant resume |

具体部署等级由 Security classification、规模、成本和 ADR 决定；应用层末端过滤不能作为唯一隔离措施。

## 10. 服务可见性与一致性

- PostgreSQL 领域事实要求 transaction commit 后可读。
- RabbitMQ 只承诺 at-least-once transport，不承诺业务 exactly-once。
- Object Store 读路径只接受 committed metadata + hash/version 匹配对象。
- Milvus、Neo4j、BM25 的一致性等级由 `WriteVisibilityReceipt` 声明，不得硬编码假设。
- Alias/cutover 必须带 generation，不能在并行请求中静默混用两个版本。
- Query request 固定 `KnowledgeSnapshotRef` / `MemorySnapshotRef`；并行 Retriever 必须读取兼容版本。
- Visibility Deadline 超时产生 `INFRA_WRITE_VISIBILITY_DEADLINE`，由领域 Owner 决定重试、降级或阻止发布。

## 11. Data-service Upgrade Compatibility

### 11.1 Upgrade State Machine

```text
PLANNED
→ COMPATIBILITY_CHECKING
→ PROVISIONING_PARALLEL_TARGET
→ DUAL_SUPPORT
→ BACKFILLING
→ VERIFYING
→ CUTTING_OVER
→ OBSERVING
→ CONTRACTING_OLD_VERSION
→ COMPLETED

COMPATIBILITY_CHECKING → BLOCKED
BACKFILLING/VERIFYING → FAILED
CUTTING_OVER/OBSERVING → ROLLING_BACK
FAILED → FORWARD_FIXING | ABORTED
```

### 11.2 组件策略

- PostgreSQL：Expand / Contract、dual read/write、online backfill。
- RabbitMQ：versioned exchange/routing key、双发布或桥接、consumer compatibility window。
- Object Store：versioned metadata/schema，不原地重写不可变对象。
- Milvus：新 Collection/Index Version 回填、验证、alias cutover。
- Neo4j：新 constraint/schema/version scope，必要时并行 database 或 version label。
- BM25/Search：新 Index + analyzer/mapping 固定、reindex、alias cutover。
- Redis：versioned namespace、双读或 cold rebuild，避免 key schema 原地漂移。
- Checkpointer：graph bundle/state schema compatibility，旧 Run 恢复链不可破坏。

## 12. Adapter Conformance Suite

### 12.1 必测能力

```text
transaction / rollback / conflict
idempotency / duplicate delivery
deadline / cancellation
lease / fencing
tenant scope
schema/version compatibility
write visibility
restart / reconnect
backup/restore or rebuild
health/readiness/degradation
telemetry and failure normalization
```

### 12.2 Local 与 Enterprise

- Local Adapter 必须显式列出不支持的语义，并在调用时 fail-fast，不能静默模拟。
- SQLite 不能证明 PostgreSQL isolation、locking、SKIP LOCKED 或 failover。
- In-process Queue 不能证明 RabbitMQ publisher confirm、quorum、redelivery 和 broker restart。
- Local Vector/Graph adapter 不能证明 Milvus/Neo4j 的 eventual visibility、Schema 或集群故障。
- 每个 Port 至少有共用 Contract Test；Enterprise Adapter 另外运行真实服务 Integration、Fault 和 E2E。

## 13. SLO、Capacity 与 Degradation

### 13.1 Criticality

| Role | Required | Degraded Allowed | Optional / Rebuildable |
| --- | --- | --- | --- |
| API / Agent Controller | PostgreSQL、Checkpoint、Object Store、Security epoch source、Mandatory Audit local path | External telemetry sink | Redis、未启用 Retriever |
| Ingestion Worker | PostgreSQL、RabbitMQ、Object Store | 非本任务索引服务 | Redis |
| Vector Worker | PostgreSQL、RabbitMQ、Object Store、Milvus | Neo4j/BM25 | Redis |
| Graph Worker | PostgreSQL、RabbitMQ、Object Store、Neo4j | Milvus/BM25 | Redis |
| Online Knowledge | PostgreSQL、Object Store、当前 RuntimePolicy 必需 Retriever | 其他 Retriever，前提是 Knowledge policy 允许 | Redis |
| Eval Worker | PostgreSQL、Queue、Artifact Store、Eval policy 需要的服务 | External sink | Redis |
| Reconciler | PostgreSQL、Object Store、Queue、目标数据服务 | External sink | Redis |

### 13.2 Measurement Contract

每个 deployment profile 必须通过真实 workload 冻结：

```text
p95 / p99 latency
error rate
pool wait / lock wait
queue age / redelivery / unacked
outbox lag
index build and rebuild throughput
serving watermark lag
backup RPO
restore RTO
maximum stale duration
capacity saturation threshold
tenant fairness
```

文档不能预设未经测量的具体数值；Program 必须记录 workload profile、数据规模、并发、硬件和基准结果。

## 14. Network Plane

Infrastructure Target 包括：

```text
Ingress / Egress policy execution
DNS / service discovery
TLS / optional mTLS
Certificate lifecycle and rotation
Outbound proxy
Provider allowlist enforcement primitive
Connection pool and drain
Network partition detection
Timeout and retry boundary
```

Security 决定允许访问什么、数据驻留与证书策略；Infrastructure 执行网络能力和 fail-closed 门禁。网络重试不得绕过上层 Retry Budget 或产生重复副作用。

## 15. Release 与 Supply Chain

Target Release 必须关联：

```text
image digest
source commit
SBOM
signature / provenance
configuration version
migration version
adapter version
data-service compatibility matrix
rollback release
```

不要求 Kubernetes，但要求部署产物可追溯、可验证、可回滚。未签名或 compatibility 不满足的受保护环境 readiness fail-closed。

## 16. Resource Usage Attribution

Infrastructure 产生物理用量 receipt：

```text
PostgreSQL storage / query / connection units
RabbitMQ message / byte / queue-age units
Object Store bytes / operations / transfer
Milvus vector count / storage / query units
Neo4j node-edge / storage / query units
BM25 index / query units
Redis memory / operation units
Backup / restore / rebuild units
```

业务预算和收费语义不归 Infrastructure；Model Gateway 拥有模型 UsageReceipt，Knowledge/Memory 拥有索引业务归属，Product/FinOps 使用统一 Attribution 进行展示和治理。

## 17. Failure Taxonomy Extension

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

Failure 必须携带 owner、scope、retryability、deadline、security epoch、generation、evidence ref 和 recovery action。

## 18. Crash / Partition Matrix

| 场景 | 已有事实 | 恢复 | 禁止 |
| --- | --- | --- | --- |
| Milvus 写完，Receipt 前崩溃 | 可能部分写入 | 以 batch id/version verify + upsert | 直接激活版本 |
| IndexManifest commit 后，alias cutover 前崩溃 | 领域版本待切流 | 重试 generation/CAS cutover | 新旧版本静默混读 |
| alias cutover 后，领域 activation receipt 丢失 | 物理已切流 | 对账 serving watermark，补写 receipt | 再次无条件切流 |
| 删除 tombstone 后，Milvus 删除失败 | 查询必须隐藏 | fail-closed filter/版本隔离，异步重试 | 恢复内容可见 |
| Legal Hold 在清理中生效 | 部分目标待删 | 停止 purge，记录已执行 receipt | 继续删除受保护副本 |
| PITR 后派生索引领先 | 索引包含恢复点后数据 | quarantine + rebuild | 直接服务 |
| Mandatory Audit local commit 前崩溃 | 无 durable audit | effect 不执行或重试 | 推断 effect 已授权执行 |
| Audit local commit 后、effect 前崩溃 | audit committed，effect 未知 | Tool Runtime effect reconcile | Infrastructure 标记 effect success |
| 网络分区导致旧 Worker 恢复 | 新 fencing token 可能已签发 | stale token reject | 晚到覆盖 |
| Upgrade 双写期间旧版本失败 | 新旧状态可能分叉 | pause cutover、reconcile/forward-fix | contract 旧版本 |

## 19. Requirement Matrix

| Requirement | Target | Required Tests | Evidence |
| --- | --- | --- | --- |
| `ARCH-INFRA-LC-001` | IndexBuild/Receipt/Verification/Manifest/Activation 分层 | `INFRA-LC-001-UT, INFRA-LC-001-IT` | `EV-INFRA-LC-001` |
| `ARCH-INFRA-LC-002` | ServingWatermark 与 WriteVisibility 明确 | `INFRA-LC-002-UT, INFRA-LC-002-IT, INFRA-LC-002-FT` | `EV-INFRA-LC-002` |
| `ARCH-INFRA-LC-003` | Cutover 使用 generation/CAS | `INFRA-LC-003-UT, INFRA-LC-003-IT, INFRA-LC-003-FT` | `EV-INFRA-LC-003` |
| `ARCH-INFRA-LC-004` | Active Snapshot 阻止错误退休 | `INFRA-LC-004-UT, INFRA-LC-004-IT` | `EV-INFRA-LC-004` |
| `ARCH-INFRA-LC-005` | 删除先撤销可见性再物理清理 | `INFRA-LC-005-UT, INFRA-LC-005-IT, INFRA-LC-005-FT, INFRA-LC-005-E2E` | `EV-INFRA-LC-005` |
| `ARCH-INFRA-LC-006` | Legal Hold 与删除协调 | `INFRA-LC-006-UT, INFRA-LC-006-IT, INFRA-LC-006-FT` | `EV-INFRA-LC-006` |
| `ARCH-INFRA-LC-007` | 删除有跨服务 Verification | `INFRA-LC-007-UT, INFRA-LC-007-IT, INFRA-LC-007-E2E` | `EV-INFRA-LC-007` |
| `ARCH-INFRA-LC-008` | RecoverySet 对齐所有权威和派生 Watermark | `INFRA-LC-008-UT, INFRA-LC-008-IT, INFRA-LC-008-FT, INFRA-LC-008-E2E` | `EV-INFRA-LC-008` |
| `ARCH-INFRA-LC-009` | Recovery cutover 必须显式允许 | `INFRA-LC-009-UT, INFRA-LC-009-IT, INFRA-LC-009-FT` | `EV-INFRA-LC-009` |
| `ARCH-INFRA-LC-010` | Mandatory Audit local durable 后才可 effect | `INFRA-LC-010-UT, INFRA-LC-010-IT, INFRA-LC-010-FT, INFRA-LC-010-E2E` | `EV-INFRA-LC-010` |
| `ARCH-INFRA-LC-011` | Audit capacity exhaustion 有 fail-mode | `INFRA-LC-011-UT, INFRA-LC-011-IT, INFRA-LC-011-FT` | `EV-INFRA-LC-011` |
| `ARCH-INFRA-LC-012` | PreparedAction 四方 Ownership 不重叠 | `INFRA-LC-012-UT, INFRA-LC-012-IT` | `EV-INFRA-LC-012` |
| `ARCH-INFRA-LC-013` | 每种服务有 TenantIsolationProfile | `INFRA-LC-013-UT, INFRA-LC-013-IT, INFRA-LC-013-FT` | `EV-INFRA-LC-013` |
| `ARCH-INFRA-LC-014` | Cross-tenant hit 进入 quarantine/fail-closed | `INFRA-LC-014-UT, INFRA-LC-014-IT, INFRA-LC-014-FT, INFRA-LC-014-E2E` | `EV-INFRA-LC-014` |
| `ARCH-INFRA-LC-015` | 服务可见性等级不能静默假设 | `INFRA-LC-015-UT, INFRA-LC-015-IT, INFRA-LC-015-FT` | `EV-INFRA-LC-015` |
| `ARCH-INFRA-LC-016` | Upgrade Compatibility 显式版本化 | `INFRA-LC-016-UT, INFRA-LC-016-IT, INFRA-LC-016-FT` | `EV-INFRA-LC-016` |
| `ARCH-INFRA-LC-017` | Milvus/Neo4j/BM25 使用并行版本和 cutover | `INFRA-LC-017-UT, INFRA-LC-017-IT, INFRA-LC-017-FT, INFRA-LC-017-E2E` | `EV-INFRA-LC-017` |
| `ARCH-INFRA-LC-018` | Local/Enterprise 共用 Conformance Suite | `INFRA-LC-018-UT, INFRA-LC-018-IT` | `EV-INFRA-LC-018` |
| `ARCH-INFRA-LC-019` | Unsupported Local semantics fail-fast | `INFRA-LC-019-UT, INFRA-LC-019-IT` | `EV-INFRA-LC-019` |
| `ARCH-INFRA-LC-020` | Role-specific criticality/readiness/degradation | `INFRA-LC-020-UT, INFRA-LC-020-IT, INFRA-LC-020-FT` | `EV-INFRA-LC-020` |
| `ARCH-INFRA-LC-021` | SLO 由真实 workload measurement 冻结 | `INFRA-LC-021-UT, INFRA-LC-021-IT` | `EV-INFRA-LC-021` |
| `ARCH-INFRA-LC-022` | Network policy、TLS、drain 与 retry 边界明确 | `INFRA-LC-022-UT, INFRA-LC-022-IT, INFRA-LC-022-FT` | `EV-INFRA-LC-022` |
| `ARCH-INFRA-LC-023` | ReleaseManifest 绑定 provenance/config/migration/adapter | `INFRA-LC-023-UT, INFRA-LC-023-IT` | `EV-INFRA-LC-023` |
| `ARCH-INFRA-LC-024` | ResourceUsageAttribution 可关联 tenant/workspace/run | `INFRA-LC-024-UT, INFRA-LC-024-IT` | `EV-INFRA-LC-024` |

## 20. Mandatory Fault / E2E Tests

```text
Index Receipt Lost After Physical Commit
Index Manifest Committed Before Cutover Crash
Cutover Receipt Lost After Alias Switch
Visibility Deadline Exceeded
Active Snapshot Blocks Retirement
Deletion Partial Across Vector / Graph / Lexical
Deletion Visibility Deadline
Legal Hold Arrives During Purge
PITR With Ahead Derived Index
PITR With Behind Derived Index
Recovery Cutover Rejected
Mandatory Audit Local Store Failure
Mandatory Audit Capacity Exhaustion
Audit Committed Before Tool Effect Crash
Tenant Filter Omission
Cross-tenant Aggregation / Traversal Hit
Milvus / Neo4j / BM25 Upgrade Rollback
Local Adapter Unsupported Semantic
Network Partition With Stale Worker
Unsigned Release Rejected
Resource Attribution Missing
```

## 21. Target Code Mapping

```text
src/backend/zuno/infrastructure/
├── contracts/
│   ├── index_lifecycle.py
│   ├── deletion.py
│   ├── recovery_set.py
│   ├── audit_durability.py
│   ├── tenant_isolation.py
│   ├── compatibility.py
│   ├── conformance.py
│   ├── service_levels.py
│   ├── release.py
│   └── attribution.py
├── application/
│   ├── index_lifecycle_service.py
│   ├── deletion_service.py
│   ├── recovery_set_service.py
│   ├── audit_admission_service.py
│   ├── upgrade_service.py
│   └── reconciliation_service.py
├── operations/
│   ├── network.py
│   ├── conformance.py
│   ├── service_levels.py
│   ├── release_validation.py
│   └── attribution.py
└── telemetry/

infra/
├── network/
├── certificates/
├── release/
├── sbom/
├── conformance/
├── benchmarks/
└── runbooks/
```

## 22. Target → Current Evidence

本附录任一 Target 提升为 Current，需要相应：

```text
contract implementation
Migration / schema / index version
real service integration
normal and fault E2E
crash / partition / retry / idempotency evidence
security isolation evidence
backup / restore / rebuild / deletion rehearsal
SLO and capacity measurement
trace / audit / evidence record
runbook / rollback / release provenance
production-readiness update
```

在这些证据完成前，状态只能是 `design available`，不能声明 `quality proven` 或 `production ready`。
