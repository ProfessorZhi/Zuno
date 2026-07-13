# 11 Infrastructure 数据服务能力附录

updated: 2026-07-13
status: normative-target-module-appendix
module_number: 11
parent_document: `docs/modules/11-infrastructure.md`
agent_mirror: `.agent/modules/11-infrastructure-data-services.md`
current_state_source: `docs/status/production-readiness.md`

> 本附录是 `docs/modules/11-infrastructure.md` 的受控规范性展开，专门冻结 PostgreSQL、RabbitMQ、Redis、Object Store、Milvus、图数据库、BM25/Search 与 Checkpointer 等数据服务的 Infrastructure 责任。
>
> 主文档仍是第 11 模块的唯一模块架构事实源；本附录不得独立改变主文档的 Current/Target、Ownership、故障与完成标准。出现冲突时，以最新 `main`、主文档和已确认 ADR 为准。

## 1. 为什么需要这份附录

“某个组件属于基础设施”至少包含两层不同含义：

```text
物理运行能力
    部署、连接、凭证、版本、容量、健康、备份、恢复、升级、隔离和观测。
领域语义
    数据表示什么、何时写入、何时可服务、检索策略、质量结论和业务状态机。
```

Infrastructure 负责第一层，并向领域模块提供 typed port、失败语义和运行证据；Knowledge、Memory、Agent Core、Security、Model Gateway 与 Observability 继续拥有第二层。

因此：

```text
Infrastructure owns the capability to run a data service reliably.
Domain module owns the meaning of facts and indexes stored through that capability.
```

## 2. Current / Target / Future Optional / Not Selected

### 2.1 Current

以最新 `main` 和 `docs/status/production-readiness.md` 为准：

- SQLite / SQLModel、本地 durable store、本地 filesystem object store 和应用级 runtime/checkpoint persistence bridge 是可证明的 Current surface。
- Compose、依赖、配置或 adapter skeleton 中出现 PostgreSQL、RabbitMQ、Redis、MinIO、Milvus 或 Neo4j，只是 inventory evidence。
- 未完成主链路集成、Migration、故障注入、备份恢复、容量、安全隔离和运行证据的组件，不得提升为 Current。

### 2.2 Target Selection Matrix

| Capability | Local-first Target | Enterprise Target | 选择状态 | 事实与语义边界 |
| --- | --- | --- | --- | --- |
| Relational facts | SQLite adapter | PostgreSQL 16+ | Core Target | PostgreSQL 是结构化权威事实能力；领域表仍由各模块拥有 |
| Async work queue | in-process/local durable queue | RabbitMQ durable/quorum queue | Core Target | Infrastructure 拥有投递 primitive；Producer/Consumer 拥有消息业务语义 |
| Immutable payload | local immutable filesystem | S3-compatible Object Store，managed S3 或 MinIO adapter | Core Target | Infrastructure 拥有物理对象完整性；领域模块拥有对象用途和引用 |
| Graph control checkpoint | local checkpoint adapter | LangGraph-compatible PostgreSQL Checkpointer | Core Target | 保存图控制状态，不替代 Agent Core 领域事实 |
| Vector index runtime | local test adapter | Milvus adapter | Selected Target | Milvus 是可重建派生索引，不是事务事实源 |
| Graph index runtime | local test adapter | Neo4j adapter | Selected Target | Neo4j 是可重建派生图索引，不拥有 Knowledge ontology 语义 |
| Lexical / BM25 index | local lexical adapter | pluggable BM25/Search adapter | Logical Target；产品待 ADR | Knowledge 拥有 analyzer/index/query 策略；Infrastructure 运行选定服务 |
| Cache / acceleration | in-process bounded cache | Redis adapter | Future Optional | 不得保存唯一 Authorization、Budget、Usage、AgentRun 或 IndexManifest 事实 |
| Trace/Audit persistence | local append store | PostgreSQL/Object Store + external sink adapter | Target capability | Observability/Security 拥有 Trace/Audit 语义和保留分类 |
| Secret/KMS | env/file reference | external Secret Manager/KMS adapter | Target capability | Security 拥有授权、scope、revocation；Infrastructure 交付受控引用和 lease |

Milvus 与 Neo4j 已由总架构选为 Target 组件；本附录补足它们的 Infrastructure 运行 Contract。它们仍然不是 Current，且不能因为 Compose 可启动就宣称已深度融合。

### 2.3 Future Optional

- Redis 用于 bounded cache、rate-limit acceleration、短期 non-authoritative coordination 或 hot metadata acceleration。
- OpenSearch、Elasticsearch 或其他独立 Search service 仅在 Knowledge 的 BM25 workload、租户隔离、运维成本和基准测试证明必要时选择。
- managed Milvus、managed graph database、managed RabbitMQ、managed PostgreSQL 和 managed object store。
- Kubernetes Operator、跨区域 standby、read replica 和专用 backup appliance。

### 2.4 Explicitly Not Selected

```text
Milvus、Neo4j、Redis 或 RabbitMQ 作为事务事实源
Redis 作为关键事实唯一副本
跨 PostgreSQL、RabbitMQ、Milvus、Neo4j 与 Object Store 的 XA / 2PC
把所有在线 LangGraph node 都放入 RabbitMQ
默认 Kafka 工作队列
默认多区域 Active-Active 数据服务
用单一“storage adapter”抹平关系、向量、图和对象存储的不同故障语义
仅凭健康端点或 Compose 启动成功宣称 production ready
```

## 3. Ownership Matrix

| Surface | Infrastructure Owns | Domain Owner Owns | Infrastructure Does Not Decide |
| --- | --- | --- | --- |
| PostgreSQL | engine、pool、UoW、transaction、schema compatibility、backup/PITR、physical isolation | 各模块的领域 schema、状态机、约束和事实 | AgentRun 是否成功、Approval 是否有效、IndexManifest 是否可服务 |
| RabbitMQ | exchange/queue binding、durability、publisher confirm、ACK/NACK、redelivery、DLQ、capacity、drain | 消息 contract、处理结果、业务 retry/replan 决策 | ParseJob、StepRun、EvalJob 的领域终局 |
| Object Store | bucket/prefix、upload session、hash、version、encryption、lifecycle execution、restore | SourceObject、Artifact、Observation、模型 payload 的业务用途 | Artifact 是否可发布、文档是否有效 |
| Milvus | cluster/client、collection physical lifecycle、partition/capacity、timeout、retry、backup/restore/rebuild primitive | Knowledge/Memory 的 embedding、vector schema、filter、top-k、score 和 IndexManifest | 哪个向量版本可服务、检索是否合格 |
| Neo4j / graph store | cluster/driver、database physical lifecycle、transaction retry、capacity、backup/restore/rebuild primitive | Knowledge 的 entity、relation、ontology、provenance、community 和 traversal semantics | 图边是否可信、GraphRAG 是否应启用 |
| BM25/Search | service/client、index physical lifecycle、snapshot、capacity、health | Knowledge 的 analyzer、tokenization、field mapping、query、ranking 和 index version | 哪个 analyzer 或 ranking 策略正确 |
| Redis | client/pool、TTL、eviction、failover、namespace、health | 使用方决定哪些数据允许缓存以及 cache invalidation proposal | 权威权限、账单、运行终局或不可重建索引状态 |
| Checkpointer | saver adapter、physical schema/version compatibility、retention、recovery primitive | Agent Core 的 graph control state meaning | Domain Commit 或 RunOutcome |

## 4. 统一能力模型

不同数据服务不能被伪装成完全相同的 CRUD store。统一的是治理字段和生命周期，不是底层语义。

```python
class DataServiceCapability(BaseModel):
    service_id: str
    service_kind: Literal[
        "RELATIONAL",
        "QUEUE",
        "OBJECT",
        "CHECKPOINT",
        "VECTOR",
        "GRAPH",
        "LEXICAL",
        "CACHE",
        "TRACE_AUDIT",
        "SECRET_KMS",
    ]
    adapter_name: str
    adapter_version: str
    deployment_profile: Literal["LOCAL", "ENTERPRISE"]
    authoritative: bool
    rebuildable: bool
    transaction_scope: str
    consistency_model: str
    tenant_isolation_mode: str
    encryption_capabilities: list[str]
    backup_restore_class: str
    health_policy_ref: str
    capacity_policy_ref: str
    schema_or_contract_version: str
    config_hash: str
```

规则：

- `authoritative=true` 只允许权威事实能力，例如 PostgreSQL 领域事实；Milvus、Neo4j、BM25 和 Redis 默认必须为 `false`。
- `rebuildable=true` 必须给出权威输入、重建命令、版本 pin、验证方法和完成 receipt。
- 上层模块只消费对应 typed port，不得获得 SQLAlchemy Session、RabbitMQ channel、Milvus client、Neo4j driver、Redis client 或厂商 secret。
- Adapter 替换不得静默改变 consistency、filter、score、transaction 或 failure semantics。

## 5. Typed Ports

```python
class VectorIndexRuntimePort(Protocol):
    async def ensure_physical_index(self, spec_ref: str) -> str: ...
    async def apply_batch(self, batch_ref: str, idempotency_key: str) -> "IndexWriteReceipt": ...
    async def verify_version(self, index_version_ref: str) -> "IndexVerification": ...
    async def activate_alias(self, from_version: str | None, to_version: str, expected_generation: int) -> "CutoverReceipt": ...
    async def retire_version(self, version_ref: str, retention_ref: str) -> "RetirementReceipt": ...

class GraphIndexRuntimePort(Protocol):
    async def ensure_physical_graph(self, spec_ref: str) -> str: ...
    async def apply_batch(self, batch_ref: str, idempotency_key: str) -> "IndexWriteReceipt": ...
    async def verify_version(self, graph_version_ref: str) -> "IndexVerification": ...
    async def activate_version(self, from_version: str | None, to_version: str, expected_generation: int) -> "CutoverReceipt": ...

class LexicalIndexRuntimePort(Protocol):
    async def ensure_physical_index(self, spec_ref: str) -> str: ...
    async def apply_batch(self, batch_ref: str, idempotency_key: str) -> "IndexWriteReceipt": ...
    async def verify_version(self, index_version_ref: str) -> "IndexVerification": ...
    async def activate_alias(self, from_version: str | None, to_version: str, expected_generation: int) -> "CutoverReceipt": ...

class CacheAccelerationPort(Protocol):
    async def get(self, namespace: str, key: str) -> bytes | None: ...
    async def set(self, namespace: str, key: str, value: bytes, ttl_seconds: int, source_generation: int) -> None: ...
    async def invalidate(self, namespace: str, key: str, min_generation: int) -> None: ...
```

`IndexWriteReceipt` 只证明物理写入尝试及其校验结果，不等于 Knowledge 的 `IndexManifest` 已可服务。只有领域 Owner 在验证 BM25、Vector、Graph、SourceSpan 与 ACL 一致性后，才能发布 KnowledgeVersion。

## 6. 派生索引生命周期

### 6.1 DerivedIndexReplica State Machine

```text
DECLARED
→ PROVISIONING
→ BUILDING
→ VERIFYING
→ READY
→ SERVING

BUILDING/VERIFYING → FAILED
SERVING → STALE
STALE/FAILED → REBUILDING → VERIFYING
SERVING/STALE → RETIRING → RETIRED
* → QUARANTINED（完整性、租户隔离或 schema 违规）
```

状态边界：

- `READY` 只表示 Infrastructure 验证物理服务、schema、count/checksum/sample query 和 tenant boundary；不表示 Knowledge 质量通过。
- `SERVING` 必须由领域 Owner 提交版本激活命令，并通过 generation/CAS 切换 alias 或 routing reference。
- `STALE` 不自动删除旧版本；active Run pin 的 KnowledgeSnapshot 仍可能需要读取。
- `FAILED` 和 `QUARANTINED` 不得被 query path 静默使用。

### 6.2 Cross-store Publish Protocol

```text
1. PostgreSQL 创建领域 IndexBuild/KnowledgeVersion 草稿与 idempotency key
2. RabbitMQ 投递 BM25 / Vector / Graph build work
3. Worker 对 Milvus、Neo4j、BM25 服务执行幂等 batch write
4. Infrastructure 返回每个物理 index 的 receipt、count、hash/sample verification
5. Knowledge 在 PostgreSQL 提交 IndexManifest 与 validation result
6. Knowledge 使用 generation/CAS 激活 KnowledgeVersion
7. Infrastructure 执行 alias/routing cutover并返回 CutoverReceipt
8. 旧版本按 active snapshot、retention 与 LegalHold 进入 RETIRING
```

禁止跨存储 XA/2PC。跨存储一致性通过：

```text
PostgreSQL domain facts
+ Outbox/Inbox
+ idempotency key
+ immutable version
+ physical write receipt
+ IndexManifest
+ generation/CAS cutover
+ reconciler
```

实现。

## 7. 组件级故障与恢复

### 7.1 PostgreSQL

- serialization/deadlock 仅按 policy 重试整个 UoW。
- schema compatibility 不满足时 role readiness fail-closed。
- primary failover 后验证 transaction fencing、WAL/LSN、outbox sequence 和 RecoveryWatermark。

### 7.2 RabbitMQ

- at-least-once delivery；ACK 前崩溃依靠 Inbox 与领域幂等去重。
- publisher confirm 丢失时允许重发；不得推断 domain mutation 未提交。
- DLQ 只保存 delivery failure，不替领域模块生成业务终局。

### 7.3 Redis

- Redis 不可用时，允许 bounded performance degradation 或回退 PostgreSQL；不得丢失权威事实。
- cache entry 必须带 source generation/version；过旧 generation 视为 miss。
- eviction、TTL 和 failover 不能触发领域状态转换。

### 7.4 Milvus

- batch write 使用稳定 entity/vector id、index version 和 idempotency key；重复投递不得逻辑重复。
- Worker 在 Milvus 写入后、领域 IndexManifest commit 前崩溃：重投后 verify/upsert，不直接发布版本。
- collection/index schema 不兼容：`INFRA_VECTOR_SCHEMA_INCOMPATIBLE`，阻止切流。
- 部分写、count mismatch、sample retrieval/hash mismatch：标记 version `FAILED` 或 `QUARANTINED`，从 PostgreSQL/Object Store 权威输入重建。
- Milvus unavailable 时，Knowledge 根据 RuntimePolicy 选择 vector-disabled degraded retrieval 或 fail-closed；Infrastructure 不自行决定答案策略。

### 7.5 Neo4j / Graph Store

- node/edge identity 必须包含 tenant/workspace、knowledge version 与稳定 domain key。
- graph batch 重放必须通过 MERGE/conditional write 或等价幂等策略避免重复节点和边。
- Worker 在 graph commit 后、IndexManifest commit 前崩溃：通过 batch receipt 和 version scope 对账，不直接激活图版本。
- constraint/schema mismatch：`INFRA_GRAPH_SCHEMA_INCOMPATIBLE`。
- 图路径无法回到 SourceSpan 是 Knowledge 证据失败，不得被 Infrastructure 标成健康成功。
- Neo4j unavailable 时，可由 Knowledge 关闭 Graph branch 并保留 BM25/Vector；高风险 strict graph requirement 则 fail-closed。

### 7.6 BM25 / Search

- analyzer、mapping、synonym 和 index version 必须固定，不能对 active index 原地静默修改。
- snapshot/restore 后验证 document count、version distribution、tenant filter 和 representative query。
- search service 不可用时，由 Knowledge 决定是否使用 Vector/Graph 降级；Infrastructure 返回结构化 dependency failure。

### 7.7 Object Store 与 Checkpointer

- 继续服从主文档的 staged ObjectCommit、hash、metadata commit、orphan reconciliation。
- Checkpoint 只保存图控制状态；Milvus/Neo4j/Redis 的成功不能替代 Domain Commit 或 Checkpoint/Domain 对账。

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
INFRA_LEXICAL_VERSION_NOT_READY
INFRA_CACHE_UNAVAILABLE
INFRA_CACHE_STALE_GENERATION
INFRA_CROSS_STORE_VERSION_DIVERGENCE
INFRA_INDEX_CUTOVER_CONFLICT
INFRA_DERIVED_INDEX_REBUILD_FAILED
```

每个 failure 必须携带：

```text
service_kind / adapter / deployment
operation / attempt / retryability
tenant_id / workspace_id
expected_version / observed_version
idempotency_key / generation
owner / recovery_action
evidence_ref / trace_id
```

Infrastructure 返回 dependency failure 和恢复建议，但不替 Knowledge 决定 corrective retrieval、abstain 或回答策略。

## 9. Backup、Restore、Rebuild 与 DR

| Service | 权威性 | 最低恢复要求 | Target 证据 |
| --- | --- | --- | --- |
| PostgreSQL | authoritative | backup + WAL/PITR + restore rehearsal | RPO/RTO、LSN、integrity queries、domain/outbox/checkpoint reconciliation |
| Object Store | authoritative for immutable payload | version manifest、checksum、replication/restore | object manifest、missing/corrupt scan、domain ref reconciliation |
| RabbitMQ | transport | durable/quorum queue 或 managed HA；domain/outbox 可重新发布 | redelivery、publisher recovery、DLQ test |
| Checkpointer | control-state authority within boundary | compatible backup/restore 或从 domain-safe watermark 恢复 | graph/state version、interrupt、pending-send recovery |
| Milvus | rebuildable derived | snapshot/backup 可加速，但必须能从权威输入重建 | count/hash/sample retrieval、tenant filter、version activation test |
| Neo4j | rebuildable derived | backup 可加速，但必须能从权威 entity/relation/source lineage 重建 | node/edge count、constraints、path/source lineage、tenant filter |
| BM25/Search | rebuildable derived | snapshot 或重建 | document/version count、query regression、tenant filter |
| Redis | non-authoritative | 默认不要求关键数据恢复；冷启动可重建 | failover/degradation test，证明没有事实丢失 |

PITR/cutover 不能只恢复 PostgreSQL：必须计算目标时间点可用的 Object Store manifest、Checkpoint generation、IndexManifest 和派生索引 watermark。无法对齐的 Milvus、Neo4j 或 BM25 版本必须标记 `STALE/REBUILDING`，不能假装与恢复后的领域事实一致。

## 10. Security 与多租户

- 所有数据服务连接使用独立 service identity、最小权限、TLS 和受控 SecretRef。
- PostgreSQL、Milvus、Neo4j、BM25/Search、Redis namespace、RabbitMQ vhost/queue、Object Store key 均必须带 tenant/workspace scope 或使用等价强隔离。
- ACL/authorization filter 必须在 Retriever query 前进入 Vector、Graph 和 BM25 query；不能先召回敏感内容再在 Python 中过滤。
- Infrastructure 验证 filter capability、tenant scope 注入和物理隔离；Security 决定授权；Knowledge 决定 retrieval query。
- Backup、snapshot、rebuild artifact、DLQ payload 与 telemetry 同样执行 data classification、redaction、retention 和 LegalHold。
- 出现跨租户命中、缺失 tenant filter 或 scope mismatch 时，服务版本进入 `QUARANTINED`，相关 readiness/admission fail-closed。

## 11. Health、Readiness、Degradation 与 Capacity

### 11.1 Role-specific Readiness

- API/Agent Controller：PostgreSQL、Checkpoint、Object Store 和 Security epoch source 为关键依赖。
- Ingestion/Index Worker：PostgreSQL、RabbitMQ、Object Store，以及本 worker 对应的 Milvus/Neo4j/BM25 服务为关键依赖。
- Online Knowledge retrieval：只检查当前 RuntimePolicy 需要的 Retriever；Graph 未启用时 Neo4j 故障不能无条件使全部问答离线。
- Maintenance/Reconciler：需要 PostgreSQL、Object Store、Queue 和被对账的数据服务。

### 11.2 Degradation Rules

| Failure | 允许的候选降级 | 禁止 |
| --- | --- | --- |
| Redis unavailable | 回退权威 store、降低吞吐 | 丢弃权限/预算/运行事实 |
| Milvus unavailable | BM25/Graph retrieval，前提是 Knowledge policy 允许 | Infrastructure 自行生成答案或假装 vector success |
| Neo4j unavailable | BM25/Vector retrieval，前提是问题不强依赖 graph | 返回未验证 graph evidence |
| BM25 unavailable | Vector/Graph retrieval，前提是 exact-match policy 允许 | 静默改变 strict retrieval profile |
| RabbitMQ unavailable | 拒绝或延迟异步 admission，保留 Outbox | 在内存中无界堆积或绕过 durable dispatch |
| PostgreSQL unavailable | fail-closed for authoritative mutation | 用 Redis/Milvus/Neo4j 代替事实源 |

### 11.3 Capacity Signals

```text
PostgreSQL pool wait / lock wait / WAL lag
RabbitMQ depth / age / redelivery / unacked / DLQ
Object upload backlog / storage watermark / checksum lag
Milvus insert/search latency / segment count / compaction backlog / memory
Neo4j transaction latency / page cache / store size / query concurrency
BM25 indexing lag / shard or segment health / query latency
Redis memory / eviction / hit ratio / connection saturation
Cross-store IndexManifest-to-physical-version lag
```

Capacity exhaustion 必须触发 bounded concurrency、admission delay、queue、reject 或 rebuild scheduling；不得通过无限增加 pool、prefetch、segment、shard 或 cache 隐藏问题。

## 12. Cross-module Dependency Requests

### 12.1 Knowledge / Agentic GraphRAG

必须冻结：

- `VectorIndexSpec`、`GraphIndexSpec`、`LexicalIndexSpec` 与各自 version identity。
- `IndexWriteBatch`、稳定 item identity、idempotency key 和 source lineage。
- `IndexManifest`、KnowledgeVersion 激活、回滚和 active snapshot retention。
- ACL/tenant filter contract、schema/analyzer/embedding/graph extractor compatibility。
- 物理 receipt 与质量 verdict 的边界。

### 12.2 Memory & Context

必须冻结：

- 长期 Memory vector/graph 与 Knowledge index 的 namespace、retention 和治理边界。
- MemoryCandidate 未通过治理时不得进入 serving index。
- 删除、撤销、LegalHold 和 re-embedding/re-graph version semantics。

### 12.3 Security

必须冻结：

- 各数据服务的 service identity、SecretRef/SecretLease、tenant isolation class 和 encryption requirement。
- query-time authorization filter 的 fail-closed 语义。
- cross-tenant finding、credential rotation 和 revocation epoch。

### 12.4 Observability & Eval

必须冻结：

- data-service operation span、index build/cutover/rebuild event 和 redaction boundary。
- vector/graph/BM25 retrieval diagnostics 的稳定字段。
- 基准测试固定 corpus、KnowledgeVersion、adapter/config 和 failure profile。

## 13. Target Code and Deployment Mapping

```text
src/backend/zuno/infrastructure/
├── contracts/data_services.py
├── ports/{vector_index,graph_index,lexical_index,cache_acceleration}.py
├── data_services/
│   ├── capability_registry.py
│   ├── lifecycle.py
│   ├── cutover.py
│   ├── reconciliation.py
│   └── failures.py
├── vector/{local,milvus,backup,rebuild,health}.py
├── graph/{local,neo4j,backup,rebuild,health}.py
├── lexical/{local,adapter,backup,rebuild,health}.py
└── cache/{local,redis,namespace,health}.py

infra/
├── postgres/
├── rabbitmq/
├── object-store/
├── milvus/
├── neo4j/
├── search/
├── redis/
├── backup-restore/
└── runbooks/
```

Knowledge 与 Memory 的 domain/application 代码只依赖 port 和领域 Contract，不导入 `pymilvus`、Neo4j driver、Redis client 或搜索引擎 SDK。

## 14. Appendix Requirement Matrix

| Requirement | Target | Required Tests | Evidence |
| --- | --- | --- | --- |
| `ARCH-INFRA-DS-001` | PostgreSQL、RabbitMQ、Object Store、Checkpointer、Milvus、Neo4j、BM25/Search、Redis 明确分层 | `INFRA-DS-001-UT, INFRA-DS-001-IT` | `EV-INFRA-DS-001` |
| `ARCH-INFRA-DS-002` | 权威事实与可重建派生索引分离 | `INFRA-DS-002-UT, INFRA-DS-002-IT, INFRA-DS-002-FT` | `EV-INFRA-DS-002` |
| `ARCH-INFRA-DS-003` | Infrastructure runtime ownership 与 Knowledge/Memory semantics 分离 | `INFRA-DS-003-UT, INFRA-DS-003-IT` | `EV-INFRA-DS-003` |
| `ARCH-INFRA-DS-004` | Milvus batch write、重复投递、partial write 与 rebuild 可验证 | `INFRA-DS-004-UT, INFRA-DS-004-IT, INFRA-DS-004-FT, INFRA-DS-004-E2E` | `EV-INFRA-DS-004` |
| `ARCH-INFRA-DS-005` | Neo4j batch write、幂等、schema mismatch 与 rebuild 可验证 | `INFRA-DS-005-UT, INFRA-DS-005-IT, INFRA-DS-005-FT, INFRA-DS-005-E2E` | `EV-INFRA-DS-005` |
| `ARCH-INFRA-DS-006` | BM25/Search analyzer、mapping 与 version 不可静默漂移 | `INFRA-DS-006-UT, INFRA-DS-006-IT, INFRA-DS-006-FT` | `EV-INFRA-DS-006` |
| `ARCH-INFRA-DS-007` | Redis 故障不丢失权威事实，stale generation 视为 miss | `INFRA-DS-007-UT, INFRA-DS-007-IT, INFRA-DS-007-FT` | `EV-INFRA-DS-007` |
| `ARCH-INFRA-DS-008` | 跨存储 publish 使用 receipt、manifest、generation 与 reconciler，不使用 2PC | `INFRA-DS-008-UT, INFRA-DS-008-IT, INFRA-DS-008-FT, INFRA-DS-008-E2E` | `EV-INFRA-DS-008` |
| `ARCH-INFRA-DS-009` | 向量、图和 lexical query 在召回前执行 tenant/ACL filter | `INFRA-DS-009-UT, INFRA-DS-009-IT, INFRA-DS-009-FT, INFRA-DS-009-E2E` | `EV-INFRA-DS-009` |
| `ARCH-INFRA-DS-010` | Backup/restore/PITR 能识别派生索引 watermark 并触发重建 | `INFRA-DS-010-UT, INFRA-DS-010-IT, INFRA-DS-010-FT, INFRA-DS-010-E2E` | `EV-INFRA-DS-010` |
| `ARCH-INFRA-DS-011` | role-specific readiness 与 component degradation 不混淆领域策略 | `INFRA-DS-011-UT, INFRA-DS-011-IT, INFRA-DS-011-FT` | `EV-INFRA-DS-011` |
| `ARCH-INFRA-DS-012` | Target → Current 需要代码、Migration、integration/fault/E2E、Trace、benchmark 和 restore/rebuild evidence | `INFRA-DS-012-UT, INFRA-DS-012-IT` | `EV-INFRA-DS-012` |

## 15. Mandatory Fault and Recovery Tests

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

每项测试必须验证：触发条件、状态变化、事实 Owner、失败传播、retry/rebuild/rollback、幂等、安全门禁、Trace 与最终 evidence。

## 16. Target → Current Evidence

任何数据服务能力提升为 Current，至少需要：

```text
adapter implementation
versioned configuration and schema/migration
real integration test against selected service
normal-path and fault-path E2E
restart/redelivery/idempotency evidence
backup/restore or authoritative rebuild rehearsal
tenant isolation and authorization-filter test
capacity and latency benchmark
structured trace/metric/audit evidence
runbook and rollback/cutover evidence
production-readiness status update
```

Milvus、Neo4j、Redis、RabbitMQ、PostgreSQL 或任何 Search service 只要缺少其中关键证据，就只能写成 `design available` 或 `implementation available`，不能写成 `quality proven` 或 `production ready`。

## 17. Coverage Conclusion

本附录确认第 11 模块覆盖的不只是 PostgreSQL 和 RabbitMQ，而是完整数据服务底座：

```text
PostgreSQL
RabbitMQ
Object Store / MinIO / S3
LangGraph Checkpointer
Redis
Milvus
Neo4j / replaceable graph database
BM25 / replaceable search runtime
Trace/Audit persistence
Secret Manager / KMS
```

同时保留唯一原则：

> Infrastructure 对这些组件的可靠运行、连接、升级、恢复、隔离、容量和证据负责；Knowledge、Memory、Agent Core、Security、Model Gateway 与 Observability 对存储内容的领域含义和最终结论负责。
