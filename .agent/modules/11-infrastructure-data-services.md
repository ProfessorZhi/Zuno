# 11 Infrastructure 数据服务能力附录

updated: 2026-07-13
status: normative-target-module-appendix
module_number: 11
parent_document: `docs/modules/11-infrastructure.md`
agent_mirror: `.agent/modules/11-infrastructure-data-services.md`
current_state_source: `docs/status/production-readiness.md`

> 本附录是 `docs/modules/11-infrastructure.md` 的受控规范性展开，冻结 PostgreSQL、RabbitMQ、Redis、Object Store、Milvus、图数据库、BM25/Search 与 Checkpointer 的 Infrastructure 责任。
>
> 主文档仍是第 11 模块的唯一模块架构事实源；本附录不能独立改变 Current/Target、Ownership、故障或完成标准。

## 1. 边界

```text
Infrastructure
    负责部署、连接、凭证、版本、容量、健康、迁移、备份、恢复、隔离、降级和观测。
Domain Owner
    负责数据含义、状态机、检索策略、质量结论、版本激活和业务终局。
```

Infrastructure owns the capability to run a data service reliably；Knowledge、Memory、Agent Core、Security、Model Gateway 与 Observability 拥有通过该能力保存的领域语义。

## 2. Current / Target / Future Optional / Not Selected

当前可证明的 surface 仍是 SQLite / SQLModel、本地 durable store、本地 filesystem object store 与应用级 runtime/checkpoint persistence bridge。Compose、依赖、配置或 adapter skeleton 中出现 PostgreSQL、RabbitMQ、Redis、MinIO、Milvus 或 Neo4j，只是 inventory evidence，不代表 Current。

| Capability | Local-first Target | Enterprise Target | 状态与边界 |
| --- | --- | --- | --- |
| Relational facts | SQLite adapter | PostgreSQL 16+ | Core Target；结构化权威事实能力，领域表归各模块 |
| Async work queue | local durable queue | RabbitMQ durable/quorum queue | Core Target；Infrastructure 管投递，领域模块管消息含义 |
| Immutable payload | local immutable filesystem | S3-compatible Object Store / MinIO | Core Target；物理完整性归 Infrastructure |
| Graph checkpoint | local adapter | LangGraph PostgreSQL Checkpointer | Core Target；控制状态，不替代领域事实 |
| Vector index | local test adapter | Milvus adapter | Selected Target；可重建派生索引，不是事实源 |
| Graph index | local test adapter | Neo4j adapter | Selected Target；可重建派生索引，不拥有 ontology |
| BM25 / Search | local lexical adapter | pluggable search adapter | Logical Target；具体产品经 ADR 选择 |
| Cache / acceleration | bounded in-process cache | Redis adapter | Future Optional；不得保存唯一关键事实 |
| Trace/Audit persistence | local append store | PostgreSQL/Object Store + sink | Target capability；Trace/Audit 语义归对应模块 |
| Secret/KMS | env/file reference | Secret Manager/KMS adapter | Target capability；授权和撤销归 Security |

Explicitly Not Selected：

```text
Milvus、Neo4j、Redis 或 RabbitMQ 作为事务事实源
Redis 作为 Authorization、Budget、Usage、AgentRun 或 IndexManifest 唯一副本
跨 PostgreSQL、RabbitMQ、Milvus、Neo4j 与 Object Store 的 XA / 2PC
把所有在线 LangGraph node 都放入 RabbitMQ
默认 Kafka 工作队列
默认多区域 Active-Active
用一个 CRUD adapter 抹平关系、向量、图、对象和队列的不同故障语义
仅凭 Compose 启动成功宣称 production ready
```

## 3. Ownership Matrix

| Surface | Infrastructure Owns | Domain Owner Owns |
| --- | --- | --- |
| PostgreSQL | engine、pool、UoW、transaction、schema compatibility、backup/PITR、physical isolation | 领域 schema、状态机、约束与事实 |
| RabbitMQ | exchange/queue、durability、confirm、ACK/NACK、redelivery、DLQ、capacity、drain | 消息 contract、处理结果与业务 retry/replan |
| Object Store | bucket/key、upload、hash、version、encryption、lifecycle、restore | SourceObject、Artifact、Observation 等用途和引用 |
| Milvus | cluster/client、collection physical lifecycle、capacity、timeout、backup/rebuild primitive | embedding、vector schema、filter、top-k、score、IndexManifest |
| Neo4j / graph store | cluster/driver、database lifecycle、transaction retry、capacity、backup/rebuild primitive | entity、relation、ontology、provenance、community、traversal |
| BM25/Search | service/client、physical index lifecycle、snapshot、capacity、health | analyzer、tokenization、mapping、query、ranking、index version |
| Redis | client/pool、TTL、eviction、failover、namespace、health | 哪些数据允许缓存以及 invalidation 规则 |
| Checkpointer | saver adapter、physical schema/version、retention、recovery | Agent Core graph control state meaning |

Infrastructure 不能决定 AgentRun 是否成功、Approval 是否有效、KnowledgeVersion 是否可服务、图边是否可信或检索质量是否合格。

## 4. DataServiceCapability

```python
class DataServiceCapability(BaseModel):
    service_kind: Literal[
        "RELATIONAL", "QUEUE", "OBJECT", "CHECKPOINT",
        "VECTOR", "GRAPH", "LEXICAL", "CACHE",
        "TRACE_AUDIT", "SECRET_KMS",
    ]
    adapter_name: str
    adapter_version: str
    deployment_profile: Literal["LOCAL", "ENTERPRISE"]
    authoritative: bool
    rebuildable: bool
    consistency_model: str
    tenant_isolation_mode: str
    backup_restore_class: str
    schema_or_contract_version: str
    config_hash: str
```

- PostgreSQL 领域事实可为 `authoritative=true`；Milvus、Neo4j、BM25 和 Redis 默认必须为 `false`。
- `rebuildable=true` 必须声明权威输入、重建命令、版本 pin、验证方法和 receipt。
- 上层模块只消费 typed port，不获得 SQLAlchemy Session、RabbitMQ channel、Milvus client、Neo4j driver 或 Redis client。
- Adapter 替换不得静默改变 consistency、filter、score、transaction 或 failure semantics。

目标 Port：

```text
VectorIndexRuntimePort
GraphIndexRuntimePort
LexicalIndexRuntimePort
CacheAccelerationPort
```

物理 `IndexWriteReceipt` 只证明写入与校验，不等于 Knowledge 的 `IndexManifest` 已可服务。

## 5. DerivedIndexReplica State Machine

```text
DECLARED → PROVISIONING → BUILDING → VERIFYING → READY → SERVING
BUILDING/VERIFYING → FAILED
SERVING → STALE
STALE/FAILED → REBUILDING → VERIFYING
SERVING/STALE → RETIRING → RETIRED
* → QUARANTINED
```

- `READY` 只表示物理 schema、count/checksum、sample query 与 tenant boundary 通过，不表示检索质量通过。
- `SERVING` 只能由领域 Owner 通过 generation/CAS 激活。
- active Run pin 的 KnowledgeSnapshot 未释放前，旧版本不能被清理。
- `FAILED`、`STALE` 和 `QUARANTINED` 不得被 query path 静默使用。

## 6. Cross-store Publish Protocol

```text
1. PostgreSQL 创建 IndexBuild / KnowledgeVersion 草稿和 idempotency key
2. RabbitMQ 投递 BM25 / Vector / Graph build work
3. Worker 对 Milvus、Neo4j、BM25 执行幂等 batch write
4. Infrastructure 返回 receipt、count、hash/sample verification
5. Knowledge 在 PostgreSQL 提交 IndexManifest 和 validation result
6. Knowledge 使用 generation/CAS 激活 KnowledgeVersion
7. Infrastructure 执行 alias/routing cutover并返回 CutoverReceipt
8. 旧版本按 snapshot、retention 与 LegalHold 进入 RETIRING
```

跨存储不使用 2PC，而使用 PostgreSQL domain facts、Outbox/Inbox、idempotency key、immutable version、physical receipt、IndexManifest、generation/CAS 与 reconciler。

## 7. 组件故障与恢复

### PostgreSQL

serialization/deadlock 只重试整个 UoW；schema 不兼容时 readiness fail-closed；failover 后验证 WAL/LSN、outbox sequence、fencing 与 RecoveryWatermark。

### RabbitMQ

at-least-once delivery；ACK 前崩溃依靠 Inbox 去重；publisher confirm 丢失允许重发；DLQ 不替领域模块产生终局。

### Redis

Redis 不可用时回退权威 store 或降低吞吐；cache entry 带 source generation/version；eviction、TTL 和 failover 不能触发领域状态变化。

### Milvus

- batch write 使用稳定 vector id、index version 和 idempotency key。
- Milvus 写入后、IndexManifest commit 前崩溃：重投后 verify/upsert，不直接发布版本。
- schema 不兼容：`INFRA_VECTOR_SCHEMA_INCOMPATIBLE`。
- partial write、count mismatch 或 sample mismatch：版本进入 `FAILED/QUARANTINED`，从 PostgreSQL/Object Store 重建。
- Milvus unavailable 时，由 Knowledge policy 决定降级或 fail-closed。

### Neo4j / Graph Store

- node/edge identity 包含 tenant/workspace、knowledge version 与稳定 domain key。
- batch 重放使用 MERGE/conditional write 或等价幂等策略。
- graph commit 后、IndexManifest commit 前崩溃：通过 receipt 和 version scope 对账，不激活图版本。
- schema/constraint 不兼容：`INFRA_GRAPH_SCHEMA_INCOMPATIBLE`。
- 图路径无法回到 SourceSpan 是 Knowledge 证据失败，不是 Infrastructure 健康成功。

### BM25 / Search

analyzer、mapping、synonym 和 index version 固定；active index 不原地静默修改；snapshot/restore 后验证 count、version distribution、tenant filter 与 representative query。

### Object Store / Checkpointer

继续服从主文档的 staged ObjectCommit、hash、metadata commit、orphan reconciliation 与 Checkpoint/Domain boundary。Milvus、Neo4j 或 Redis 成功不能替代 Domain Commit。

## 8. Failure Taxonomy Extension

```text
INFRA_DATA_SERVICE_UNAVAILABLE
INFRA_DATA_SERVICE_TIMEOUT
INFRA_DATA_SERVICE_AUTH_FAILED
INFRA_DATA_SERVICE_SCHEMA_INCOMPATIBLE
INFRA_DATA_SERVICE_TENANT_ISOLATION_VIOLATION
INFRA_VECTOR_WRITE_PARTIAL
INFRA_VECTOR_SCHEMA_INCOMPATIBLE
INFRA_VECTOR_VERSION_NOT_READY
INFRA_GRAPH_WRITE_PARTIAL
INFRA_GRAPH_SCHEMA_INCOMPATIBLE
INFRA_GRAPH_VERSION_NOT_READY
INFRA_LEXICAL_INDEX_CORRUPT
INFRA_CACHE_UNAVAILABLE
INFRA_CACHE_STALE_GENERATION
INFRA_CROSS_STORE_VERSION_DIVERGENCE
INFRA_INDEX_CUTOVER_CONFLICT
INFRA_DERIVED_INDEX_REBUILD_FAILED
```

Failure 必须带 service、operation、attempt、retryability、tenant/workspace、expected/observed version、idempotency key、generation、owner、recovery action、evidence ref 与 trace id。

## 9. Backup、Restore、Rebuild 与 DR

| Service | 权威性 | 最低恢复要求 |
| --- | --- | --- |
| PostgreSQL | authoritative | backup + WAL/PITR + restore rehearsal |
| Object Store | authoritative immutable payload | version manifest、checksum、restore reconciliation |
| RabbitMQ | transport | durable/quorum queue；domain/outbox 可重发 |
| Checkpointer | control-state authority within boundary | compatible restore 或 domain-safe watermark recovery |
| Milvus | rebuildable derived | snapshot 可加速，但必须能从权威输入重建 |
| Neo4j | rebuildable derived | backup 可加速，但必须能从 entity/relation/source lineage 重建 |
| BM25/Search | rebuildable derived | snapshot 或重建，并验证 query regression |
| Redis | non-authoritative | 冷启动可重建；故障不能造成事实丢失 |

PITR 不能只恢复 PostgreSQL。Object manifest、Checkpoint generation、IndexManifest 与派生索引 watermark 必须对齐；无法对齐的 Milvus、Neo4j 或 BM25 版本进入 `STALE/REBUILDING`。

## 10. Security、多租户、Readiness 与 Capacity

- PostgreSQL、Milvus、Neo4j、BM25/Search、Redis namespace、RabbitMQ vhost/queue 与 Object Store key 均带 tenant/workspace scope 或等价强隔离。
- ACL/authorization filter 在 Vector、Graph 和 BM25 召回前执行，不能先召回敏感内容再过滤。
- cross-tenant hit、缺失 filter 或 scope mismatch 使版本 `QUARANTINED`，相关 readiness/admission fail-closed。
- API/Controller 的关键依赖与 Index Worker 的关键依赖不同；Graph 未启用时 Neo4j 故障不能无条件拖垮全部问答。
- Redis、Milvus、Neo4j 或 BM25 降级只返回结构化能力状态；是否改变检索策略由 Knowledge 决定。
- Capacity 信号至少覆盖 PostgreSQL pool/WAL、RabbitMQ age/depth/redelivery、Object backlog、Milvus latency/segment/compaction、Neo4j latency/page cache、BM25 lag、Redis memory/eviction 和跨存储 version lag。

## 11. Cross-module Requests

Knowledge 必须冻结 `VectorIndexSpec`、`GraphIndexSpec`、`LexicalIndexSpec`、`IndexWriteBatch`、稳定 item identity、`IndexManifest`、KnowledgeVersion 激活/回滚、ACL filter、embedding/analyzer/graph extractor compatibility，以及 physical receipt 与 quality verdict 的边界。

Memory 必须冻结长期 Memory vector/graph namespace、retention、治理、删除/撤销、LegalHold 和 re-embedding/re-graph version semantics。

Security 必须冻结 service identity、SecretRef/SecretLease、tenant isolation class、query-time filter fail-closed、credential rotation 和 revocation epoch。

Observability & Eval 必须冻结 data-service operation span、index build/cutover/rebuild event、redaction boundary，以及固定 corpus、KnowledgeVersion、adapter/config 和 failure profile 的评测方法。

## 12. Target Code Mapping

```text
src/backend/zuno/infrastructure/
├── contracts/data_services.py
├── ports/{vector_index,graph_index,lexical_index,cache_acceleration}.py
├── data_services/{capability_registry,lifecycle,cutover,reconciliation,failures}.py
├── vector/{local,milvus,backup,rebuild,health}.py
├── graph/{local,neo4j,backup,rebuild,health}.py
├── lexical/{local,adapter,backup,rebuild,health}.py
└── cache/{local,redis,namespace,health}.py

infra/{postgres,rabbitmq,object-store,milvus,neo4j,search,redis,backup-restore,runbooks}/
```

Knowledge 与 Memory 不导入 `pymilvus`、Neo4j driver、Redis client 或搜索引擎 SDK。

## 13. Requirement Matrix

| Requirement | Target | Required Tests | Evidence |
| --- | --- | --- | --- |
| `ARCH-INFRA-DS-001` | 所有数据服务明确分层 | `INFRA-DS-001-UT, INFRA-DS-001-IT` | `EV-INFRA-DS-001` |
| `ARCH-INFRA-DS-002` | 权威事实与派生索引分离 | `INFRA-DS-002-UT, INFRA-DS-002-IT, INFRA-DS-002-FT` | `EV-INFRA-DS-002` |
| `ARCH-INFRA-DS-003` | runtime ownership 与领域语义分离 | `INFRA-DS-003-UT, INFRA-DS-003-IT` | `EV-INFRA-DS-003` |
| `ARCH-INFRA-DS-004` | Milvus 重复、partial、rebuild 可验证 | `INFRA-DS-004-UT, INFRA-DS-004-IT, INFRA-DS-004-FT, INFRA-DS-004-E2E` | `EV-INFRA-DS-004` |
| `ARCH-INFRA-DS-005` | Neo4j 幂等、schema、rebuild 可验证 | `INFRA-DS-005-UT, INFRA-DS-005-IT, INFRA-DS-005-FT, INFRA-DS-005-E2E` | `EV-INFRA-DS-005` |
| `ARCH-INFRA-DS-006` | BM25 analyzer/mapping/version 不漂移 | `INFRA-DS-006-UT, INFRA-DS-006-IT, INFRA-DS-006-FT` | `EV-INFRA-DS-006` |
| `ARCH-INFRA-DS-007` | Redis 故障不丢权威事实 | `INFRA-DS-007-UT, INFRA-DS-007-IT, INFRA-DS-007-FT` | `EV-INFRA-DS-007` |
| `ARCH-INFRA-DS-008` | 跨存储 publish 不使用 2PC | `INFRA-DS-008-UT, INFRA-DS-008-IT, INFRA-DS-008-FT, INFRA-DS-008-E2E` | `EV-INFRA-DS-008` |
| `ARCH-INFRA-DS-009` | 召回前执行 tenant/ACL filter | `INFRA-DS-009-UT, INFRA-DS-009-IT, INFRA-DS-009-FT, INFRA-DS-009-E2E` | `EV-INFRA-DS-009` |
| `ARCH-INFRA-DS-010` | PITR 识别派生索引 watermark | `INFRA-DS-010-UT, INFRA-DS-010-IT, INFRA-DS-010-FT, INFRA-DS-010-E2E` | `EV-INFRA-DS-010` |
| `ARCH-INFRA-DS-011` | role readiness 与 degradation 分离 | `INFRA-DS-011-UT, INFRA-DS-011-IT, INFRA-DS-011-FT` | `EV-INFRA-DS-011` |
| `ARCH-INFRA-DS-012` | Target → Current 需要完整工程证据 | `INFRA-DS-012-UT, INFRA-DS-012-IT` | `EV-INFRA-DS-012` |

## 14. Mandatory Fault Tests

```text
PostgreSQL Primary Failover
RabbitMQ Redelivery and Publisher Confirm Loss
Redis Unavailable and Stale Generation
Milvus Write-Then-Crash Before Manifest Commit
Milvus Partial Batch and Schema Incompatibility
Milvus Rebuild and Version Cutover
Neo4j Commit-Then-Crash Before Manifest Commit
Neo4j Duplicate Batch and Constraint Mismatch
Neo4j Rebuild and Version Cutover
BM25 Analyzer/Mapping Version Mismatch
Cross-store Version Divergence
Tenant Filter Omission / Cross-tenant Hit
PITR with Stale Derived Indexes
Component-specific Degradation
Capacity Exhaustion per Data Service
```

每项测试必须验证触发条件、状态变化、事实 Owner、失败传播、retry/rebuild/rollback、幂等、安全门禁、Trace 与 evidence。

## 15. Target → Current Evidence

任何组件提升为 Current，至少需要 adapter implementation、versioned config/schema、真实 integration、fault/E2E、restart/redelivery/idempotency、backup/restore 或 authoritative rebuild、tenant isolation、benchmark、Trace/metric/audit、runbook/cutover/rollback 和 production-readiness 状态更新。

因此第 11 模块覆盖：PostgreSQL、RabbitMQ、Object Store/MinIO/S3、LangGraph Checkpointer、Redis、Milvus、Neo4j/可替换图数据库、BM25/可替换 Search runtime、Trace/Audit persistence 与 Secret Manager/KMS；但领域含义和最终结论仍归对应业务模块。
