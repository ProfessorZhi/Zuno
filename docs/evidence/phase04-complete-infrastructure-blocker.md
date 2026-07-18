# PHASE04 Complete Infrastructure Blocker Evidence

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-17
status: blocked
coordinator_decision: not_approved
real_services_smoke: passed
alembic_migration_foundation: proven
alembic_schema_drift_full_domain_and_infra: proven
migration_lock_backfill_control: proven
postgres_runtime_context_timeout_subset: passed
postgres_session_runtime_subset: passed
domain_uow_adoption: passed
domain_outbox_inbox_adoption: proven
postgres_deadlock_retry_subset: passed
postgres_serialization_retry_subset: passed
postgres_pool_exhaustion_subset: passed
postgres_connection_loss_recovery_subset: passed
langgraph_postgres_checkpointer: proven
backup_restore_replay: missing
rabbitmq_fault_evidence: proven
minio_restore_evidence: proven
combined_dependency_fault: missing
rabbitmq_transport_subset: passed
rabbitmq_dlq_replay_subset: passed
rabbitmq_backlog_depth_subset: passed
rabbitmq_retry_exhaustion_subset: passed
outbox_rabbitmq_publisher_subset: passed
rabbitmq_broker_restart_subset: passed
rabbitmq_network_partition_subset: passed
outbox_partition_recovery_subset: passed
consumer_crash_redelivery_subset: passed
rabbitmq_out_of_order_subset: passed
outbox_delivery_policy_subset: passed
idempotency_claim_lifecycle_subset: passed
idempotency_high_concurrency_single_winner_subset: passed
idempotency_owner_crash_process_exit_subset: passed
idempotency_tenant_isolation_subset: passed
idempotency_worker_supervision: passed
lease_fencing_subset: passed
lease_worker_coordination: passed
minio_object_store_subset: passed
minio_visibility_duplicate_missing_subset: passed
minio_multipart_reconciliation_subset: passed
minio_governance_subset: passed
minio_storage_restart_subset: passed
minio_postgres_manifest_adoption: proven
backup_restore_replay_subset: passed
backup_restore_runtime_restart_subset: passed
combined_postgres_rabbitmq_minio_fault_subset: passed
operator_readiness_subset: proven
capacity_admission: proven
mandatory_audit: proven
cutover_snapshot: proven
recovery_watermark: proven
secret_rotation_tenant_hit: proven
pitr_alignment: proven
dr_profile_rpo_rto_owner: proven
infrastructure_capability_profile: proven
backup_service_boundaries: proven
infrastructure_docs_governance: proven
infrastructure_domain_boundary: proven
infrastructure_typed_ports: proven
tenant_isolation_profiles: proven
tenant_physical_constraints: proven
upgrade_compatibility_profiles: proven
adapter_conformance_profiles: proven
release_provenance_manifest: proven
redis_optional_boundary: proven
derived_index_boundary: proven
contract_ownership_boundaries: proven
infra_requirement_006_010_ledger_subset: proven
infra_requirement_064_evidence_gate: proven
reconciler_supervision_boundary: proven
checkpoint_boundary_version: proven
restore_cutover_completion_gates: proven
official_langgraph_checkpointer_lifecycle_subset: proven
official_checkpointer_backup_restore: proven

## Stop Condition

PHASE04 仍不能关闭。当前已经启动真实 PostgreSQL、RabbitMQ 和 MinIO/S3，并完成各自 canonical integration/fault 子范围验证；官方 LangGraph PostgreSQL Checkpointer 依赖已由 Coordinator Decision 批准并通过基础 PostgresSaver smoke，但完整 Phase 还要求 official Checkpointer restore/recovery、Product Projection Replay 与包含 official Checkpointer 的组合故障证据。

目标文件要求真实 PostgreSQL、RabbitMQ、MinIO/S3、LangGraph PostgreSQL Checkpointer、Backup/Restore/Replay 和故障证据都成立后，PHASE04 才能 completed，PHASE05 才能 ready。静态 YAML、Compose 声明、primitive table、一次性连通性测试和 mock 不能替代这些证据。

## Environment Probe

| Probe | Result |
| --- | --- |
| `docker info --format "{{.ServerVersion}}"` | Docker engine `29.4.0` |
| `docker compose -f infra/docker/docker-compose.yml ps postgres rabbitmq minio` | `zuno-postgres`、`zuno-rabbitmq`、`zuno-minio` 均为 healthy |
| `Test-NetConnection localhost -Port 5432` | initial `TcpTestSucceeded: False`; after Docker start `TcpTestSucceeded: True` |
| `Test-NetConnection localhost -Port 5672` | after Docker start `TcpTestSucceeded: True` |
| `Test-NetConnection localhost -Port 9000` | after Docker start `TcpTestSucceeded: True` |
| `python tools/scripts/verify_phase04_alembic_migration.py` | passed; 单一 revision chain、冻结显式 baseline、31 张领域表与 24 张基础设施表 ownership/drift、空库 upgrade/repeated upgrade/downgrade/re-upgrade、online index/constraint 全部验证 |
| `python tools/scripts/verify_phase04_existing_database_upgrade.py` | passed; production-like 既有库零 drift 后 stamp base，升级到 `20260718_15`，重复升级且领域种子数据保持 |
| `python tools/scripts/verify_phase04_migration_control.py` | passed; PostgreSQL advisory lock 阻止并行 Alembic deploy，Backfill ledger 的 matrix adoption、chunk 幂等/hash conflict、pause/restart/resume、generation fencing 与 forward-fix lineage 通过 |
| `python tools/scripts/verify_phase04_postgres_runtime.py` | passed; readiness, transaction-local tenant context, statement timeout and lock timeout verified |
| `python tools/scripts/verify_phase04_postgres_session_runtime.py` | passed; sync/async Session Factory、显式 UoW、commit/rollback、nested reject、failed-entry cleanup、read-only、tenant 并发隔离、async timeout/cancel、connection loss recovery 与 rotation 通过 |
| `python tools/scripts/verify_phase04_domain_uow_adoption.py` | passed; 唯一默认 `PostgresRuntime`、DAO UoW-owned commit、跨两个 Repository 原子回滚、sync/async Session 复用、tenant no-leak 与 async task isolation 通过 |
| `python tools/scripts/verify_phase04_domain_event_adoption.py` | passed; Product 领域事实 + Outbox、Inbox + Memory 领域事实分别同事务，producer/consumer pre-commit crash 回滚，consumer redelivery、same-hash dedup、different-hash quarantine 与 commit 后 ACK 通过 |
| `python tools/scripts/verify_phase04_postgres_deadlock_retry.py` | passed; two real concurrent PostgreSQL transactions deadlocked on opposite row locks, one received transient `40P01`, retried the whole transaction and both workers committed |
| `python tools/scripts/verify_phase04_postgres_serialization_retry.py` | passed; two real `SERIALIZABLE` PostgreSQL transactions conflicted on a shared invariant, one received transient `40001`, retried the whole transaction and both workers committed |
| `python tools/scripts/verify_phase04_postgres_pool_exhaustion.py` | passed; real PostgreSQL engine with `pool_size=1`, `max_overflow=0`, `pool_timeout=1` rejected a second checkout while the only connection was held and recovered after release |
| `python tools/scripts/verify_phase04_postgres_connection_loss.py` | passed; real PostgreSQL backend was terminated with `pg_terminate_backend`, old connection failed closed and the same engine recovered on a new checkout |
| `pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider` | passed, `9 passed` against real PostgreSQL on localhost:5432 |
| `python tools/scripts/verify_phase04_real_services_smoke.py` | passed; PostgreSQL schema dump contains infrastructure tables, RabbitMQ publish/get succeeds, MinIO put/get/delete hash check succeeds |
| `python tools/scripts/verify_phase04_rabbitmq_transport.py` | passed; durable exchange/queue/DLQ, publisher confirm path, redelivery, DLQ routing and DLQ replay verified against real RabbitMQ |
| `python tools/scripts/verify_phase04_rabbitmq_backlog.py` | passed; queue depth grows after publish and drains after ACK |
| `python tools/scripts/verify_phase04_rabbitmq_retry_exhaustion.py` | passed; retry attempts are recorded in headers, tenant context is preserved, persistent retry republishes drain the main queue and exhausted message reaches DLQ |
| `python tools/scripts/verify_phase04_outbox_rabbitmq_publisher.py` | passed; PostgreSQL outbox claim, RabbitMQ publish-confirm, outbox published receipt and inbox receipt verified |
| `python tools/scripts/verify_phase04_outbox_delivery_policy.py` | passed; 真实 RabbitMQ 停机期间持久 backoff、重试耗尽 dead-letter、backlog visibility，以及恢复后的人工 replay、publisher confirm 和交付审计通过 |
| `python tools/scripts/verify_phase04_rabbitmq_broker_restart.py` | passed; persistent RabbitMQ message survived real `docker restart zuno-rabbitmq` |
| `python tools/scripts/verify_phase04_rabbitmq_network_partition.py` | passed; TCP blackhole 阻断 publisher confirm，恢复后对账 UNKNOWN publish、重连 transport；Outbox claimed/reclaim/republish 与 consumer crash rollback/redelivery/first-seen dedup 通过 |
| `python tools/scripts/verify_phase04_rabbitmq_out_of_order.py` | passed; tenant-scoped sequence、RabbitMQ `3,1,2` 乱序投递、Inbox durable buffer、engine 重建、watermark `0/3 -> 1/3 -> 3/3`、连续释放与 duplicate 收敛通过 |
| `python tools/scripts/verify_phase04_idempotency_claim.py` | passed; same-hash replay, different-hash conflict, renew, expiry, stale generation reject, result replay and high-concurrency single-winner verified |
| `python tools/scripts/verify_phase04_idempotency_owner_crash.py` | passed; subprocess committed an in-progress claim, exited before completion, replacement owner reclaimed after expiry, stale generation completion was rejected and replacement result replayed |
| `python tools/scripts/verify_phase04_idempotency_tenant_isolation.py` | passed; transaction tenant context participates in the idempotency uniqueness boundary and same scope/key can safely exist in two tenants with distinct request hashes/results |
| `python tools/scripts/verify_phase04_idempotency_supervision.py` | passed; owner/generation/expiry fencing、heartbeat、busy-owner reject、abort/reclaim、进程级取消传播、进程退出后的 durable effect reconciliation 与 no-reexecution 通过 |
| `python tools/scripts/verify_phase04_lease_fencing.py` | passed; lease acquire, heartbeat renew, duplicate worker reject, expiry transfer, cancel transfer and late fencing token reject verified |
| `python tools/scripts/verify_phase04_lease_worker_coordination.py` | passed; database clock、同 owner 幂等 acquire、显式 transfer、heartbeat、同事务 fenced commit、crash/pause/cancel race、clock tolerance 与 PostgreSQL TCP partition 通过 |
| `python tools/scripts/verify_phase04_minio_object_store.py` | passed; staging, duplicate staging, multipart/partial upload, orphan cleanup, lost-response/duplicate-complete reconciliation, authorization deny-before-I/O, Object Lock version、retention、legal hold、lifecycle、pre-commit visibility、missing/hash fail-closed、commit cleanup、delete 和 restore 均在真实 MinIO 验证 |
| `python tools/scripts/verify_phase04_minio_manifest_adoption.py` | passed; MinIO raw SHA-256/size receipt 进入 PostgreSQL Manifest，Input domain + Manifest 同事务，物理 commit 后 crash 可 reconcile，staged/deleted/quarantined read fail closed，篡改进入持久 quarantine |
| `python tools/scripts/verify_phase04_minio_storage_restart.py` | passed; committed object and restore point survived real `docker restart zuno-minio` |
| `python tools/scripts/verify_phase04_backup_restore_replay.py` | passed; `pg_dump`/temporary `pg_restore`、MinIO restore point，并在恢复库重建 sync/async PostgresRuntime 与 read-only UoW 后校验 infra rows |
| `python tools/scripts/verify_phase04_combined_service_fault.py` | passed; PostgreSQL/RabbitMQ/MinIO 同时停机期间新调用 fail closed，全部健康恢复后 persistent message、Outbox→Inbox、Object hash、Manifest 与 checkpoint primitive 对账通过 |
| `python tools/scripts/verify_phase04_operator_readiness.py` | passed; Operator readiness snapshot 聚合 PostgreSQL health/readiness/pool metrics、Outbox backlog、RabbitMQ queue depth、MinIO object read probe、trace correlation、failure owner/retry owner/recovery owner，并明确 telemetry 不产生 Eval verdict |
| `python tools/scripts/verify_phase04_capacity_admission.py` | passed; PostgreSQL capacity admission schema、drain、atomic reservation、owner-fenced release、exhaustion backpressure 与 release 后恢复 admission 均通过 |
| `python tools/scripts/verify_phase04_mandatory_audit.py` | passed; PostgreSQL mandatory audit schema、durable-before-effect gate、无 audit 拒绝 effect、audit capacity fail-closed、capacity failed path no effect 与 observed 后 capacity 恢复均通过 |
| `python tools/scripts/verify_phase04_cutover_snapshot.py` | passed; PostgreSQL cutover snapshot schema、Generation/CAS activation、stale generation reject、active snapshot ref、current/active-ref retirement reject 与 ref release 后 retirement 均通过 |
| `python tools/scripts/verify_phase04_recovery_watermark.py` | passed; PostgreSQL recovery watermark schema、权威/派生 watermark 记录、derived mismatch reject、RecoverySet 对齐和 verification hash 均通过 |
| `python tools/scripts/verify_phase04_secret_rotation_tenant_hit.py` | passed; PostgreSQL secret version activation、secret material reject、active-generation lease、rollback、stale generation reject、cross-tenant fail-closed/quarantine receipt 均通过 |
| `python tools/scripts/verify_phase04_pitr_alignment.py` | passed; 临时真实 PostgreSQL primary/recovery 容器启用 WAL archive、`pg_basebackup`、recovery target time，恢复后 DB/Object/Checkpoint/Index RecoverySet 保持对齐，target 后 derived index watermark 未混入 |
| `python tools/scripts/verify_phase04_dr_profile.py` | passed; `docs/governance/infrastructure-dr-profile.yaml` 覆盖 PostgreSQL、Object Manifest/MinIO、RabbitMQ Outbox/Inbox、official Checkpointer、Product Projection Replay 和 PITR 的 RPO/RTO/Owner/Recovery Owner/验证命令/evidence ref，并保持 cutover fail closed |
| `python tools/scripts/verify_phase04_infrastructure_capability_profile.py` | passed; `InfrastructureCapabilityProfileV1` 与 `DataServiceCapabilityV1` immutable、versioned、canonical-hash、Developer CI / Server Product typed contract 共用、派生服务非权威和 unsupported semantics 显式声明均通过 |
| `python tools/scripts/verify_phase04_backup_service_boundaries.py` | passed; Backup Scope/RPO/Encryption/Verify profile 与 PostgreSQL/RabbitMQ/Object/Checkpoint typed service boundary 均通过，其中 official Checkpointer 保持 blocked boundary |
| `python tools/scripts/verify_phase04_infrastructure_docs_governance.py` | passed; Infrastructure Current/Target/Future/Explicitly Not Selected 分层、唯一正式 Target 文档、Agent 镜像、architecture canonical 四文件集合和 entrypoint verifier 均通过 |
| `python tools/scripts/verify_phase04_infrastructure_domain_boundary.py` | passed; 基础设施 receipt contract 和 PHASE04 evidence 均明确 Queue ACK、Object Commit、Idempotency Claim、Object Manifest visibility 与 operator telemetry 不代表领域成功 |
| `python tools/scripts/verify_phase04_infrastructure_typed_ports.py` | passed; Developer CI 与 Server Product profile 使用同一 `InfrastructureCapabilityProfileV1` / `DataServiceCapabilityV1` typed port，覆盖全部 required service kind，并对 unknown service kind fail closed |
| `python tools/scripts/verify_phase04_tenant_isolation_profiles.py` | passed; Infrastructure Capability Profile 中每个 service kind 都有 `TenantIsolationProfileV1`，包含 tenant scope、强隔离选项、cross-tenant fail-closed/quarantine/audit action 和存在的 evidence ref |
| `python tools/scripts/verify_phase04_tenant_physical_constraints.py` | passed; PostgreSQL tenant context/unique key/WHERE、RabbitMQ tenant header、Object ref/MinIO bucket-prefix-auth hook 和 Operator tenant snapshot 的当前证据共同证明 `ARCH-INFRA-034` |
| `python tools/scripts/verify_phase04_upgrade_compatibility_profiles.py` | passed; Infrastructure Capability Profile 中每个 service kind 都有 `UpgradeCompatibilityProfileV1`，包含显式 adapter/schema version、read/write/rollback compatible versions、unknown-version fail-closed action 和 canonical content hash |
| `python tools/scripts/verify_phase04_adapter_conformance_profiles.py` | passed; Developer CI 与 Server Product 对每个 service kind 共用 `AdapterConformanceProfileV1`、conformance suite version、supported/unsupported semantics、required test refs 和 evidence refs，并对 unsupported local semantic fail-fast |
| `python tools/scripts/verify_phase04_release_provenance_manifest.py` | passed; `ReleaseManifestV1` 绑定 source commit、运行中 image id bundle、Compose network/port refs、config hash、migration versions、adapter versions、compatibility evidence 和 provenance refs |
| `python tools/scripts/verify_phase04_redis_optional_boundary.py` | passed; Redis/CACHE 在 `DataServiceCapabilityV1` 中为 optional、non-authoritative、rebuildable，并且不进入 PHASE04 required real services 或 release adapter provenance |
| `python tools/scripts/verify_phase04_derived_index_boundary.py` | passed; VECTOR/Milvus、GRAPH/Neo4j 和 LEXICAL/BM25/Search 在 `DataServiceCapabilityV1` 中为 versioned、non-authoritative、rebuildable，并且不进入 PHASE04 required release adapter provenance |
| `python tools/scripts/verify_phase04_contract_ownership_boundaries.py` | passed; Index write/receipt/visibility 与 Knowledge acceptance 分层、IndexManifest/Acceptance 领域归属、PreparedToolAction/ActionProposal/SecurityApproval/AuditPersistence owner 不重叠均通过 |
| `python tools/scripts/verify_phase04_complete_infrastructure.py` | expected blocked; 全部已登记真实子 verifier 执行通过，P04-T01/T02/T03/T04/T05 与 P04-T06 MinIO 子范围已完成，最终仍由 P04-T06 official Checkpointer 子范围、P04-T07、审批/PHASE05 gate、完整恢复与含 Checkpointer 的组合故障 marker 阻止关闭 |
| `python tools/scripts/verify_phase04_reconciler_supervision_boundary.py` | passed; IdempotencyWorkerSupervisor 的 reconcile/no-reexecution 与 LeaseWorkerCoordinator 的 heartbeat/fenced commit/fail-closed 边界均有证据 |
| `python tools/scripts/verify_phase04_checkpoint_boundary_version.py` | passed; Checkpoint/Domain fact boundary 与 Checkpoint adapter/schema unknown version fail-closed profile 均通过，official Checkpointer 仍 blocked |
| `python tools/scripts/verify_phase04_restore_cutover_completion_gates.py` | passed; backup completed、isolated restore cutover 和 recovery cutover explicit allow 三类 gate 均保持 fail-closed |
| `python tools/scripts/verify_phase04_official_langgraph_checkpointer.py` | passed; official `langgraph.checkpoint.postgres.PostgresSaver` 在真实 PostgreSQL 上完成 setup、多代 put、restart restore、thread isolation、writes、delta channel history、delete cleanup、infra generation 对账和 stale generation reject |
| `python tools/scripts/verify_phase04_official_checkpointer_backup_restore.py` | passed; official `PostgresSaver` checkpoint schema/rows/writes 随真实 `pg_dump -Fc` 备份并在临时恢复库经 `pg_restore` 后由官方 saver 读取 |

## Missing Required Proof

- LangGraph PostgreSQL Checkpointer graph-level interrupt/resume、retention/prune 和 schema upgrade recovery
- Backup/Restore/Replay for product projections、完整产品 Runtime restart 与 full recovery set
- 包含官方 Checkpointer 的完整 combined dependency fault evidence

## Current Verified Subset

已证明的最小真实服务闭环：

- PostgreSQL schema backup smoke：`pg_dump --schema-only` 可运行，且包含 `infra_outbox_events` 和 `infra_checkpoints`；
- PostgreSQL runtime context/timeout subset：readiness、transaction-local tenant context、tenant no-leak、statement timeout 和 lock timeout 经真实 PostgreSQL 验证；
- PostgreSQL session runtime subset：显式配置创建 sync/async Engine 与 Session Factory；两类 UoW 的 commit/rollback、nested reject、isolation/read-only、并发 tenant no-leak、async timeout/cancel、backend termination recovery、pool metrics 和 connection rotation 均通过；
- PostgreSQL 默认 Domain UoW：应用只构造一个 `PostgresRuntime`；旧 Engine 导出指向同一 Runtime；DAO 不再拥有 commit/rollback；跨 `MessageLikeDao` 与 `MessageDownDao` 的事务失败后原子回滚，async DAO 与 task isolation 通过；
- PostgreSQL deadlock retry subset：真实双事务 row-lock deadlock 触发 `40P01`，retry boundary 重跑完整事务并最终提交；
- PostgreSQL serialization retry subset：真实 `SERIALIZABLE` 写偏斜冲突触发 `40001`，retry boundary 重跑完整事务并最终提交；
- PostgreSQL pool exhaustion subset：真实 PostgreSQL engine 在 `pool_size=1/max_overflow=0/pool_timeout=1` 下拒绝第二个 checkout，释放后恢复；
- PostgreSQL connection loss recovery subset：真实 `pg_terminate_backend` 终止旧 connection，旧 connection fail closed，同一 engine 重新 checkout 后恢复；
- Domain Outbox/Inbox adoption：Product `MessageLikeDao` 与 canonical Outbox 共享 Domain UoW；Memory consumer 的 Inbox 与 `MemoryRawEventTable` 共享 Domain UoW，consumer crash 时共同回滚并由 RabbitMQ redeliver，commit 后才 ACK；
- Alembic migration foundation：单一 revision chain 以显式冻结 base 管理 31 张领域表和 24 张基础设施表；空库 upgrade/repeated upgrade/downgrade/re-upgrade 与 production-like 既有库接管、数据保持均通过；
- Alembic schema drift 与 online DDL：领域 metadata 完整比较，基础设施 columns/constraints/indexes 精确比较；concurrent index ready/valid，`NOT VALID` constraint 独立验证为 validated；
- Migration control：Alembic online execution 使用 PostgreSQL session advisory lock；并行 deploy 在 timeout 后 fail closed，释放后恢复。PHASE02 matrix 输入进入持久 Backfill ledger，chunk replay 幂等、hash conflict、pause/restart/resume、stale generation reject 与 forward-fix lineage 均通过；
- RabbitMQ smoke：使用 `rabbitmqadmin` 声明临时 durable queue，发布 JSON payload，再以 `ackmode=ack_requeue_false` 读取并删除队列；
- RabbitMQ publisher confirm：`RabbitMQTransport` 使用 `aio_pika` publisher confirm channel 发布 persistent message；
- RabbitMQ redelivery：NACK `requeue=True` 后重新消费到 `redelivered=True` 的同一 message；
- RabbitMQ DLQ：Reject `requeue=False` 后 poison message 进入 durable DLQ；
- RabbitMQ DLQ replay：DLQ message 以相同 message id/payload replay 回主队列，并带 `replayed_from_dlq` receipt header；
- RabbitMQ backlog depth：passive queue depth 在 publish 后增长、ACK 后归零，证明 backlog 可观测；
- RabbitMQ retry exhaustion：transport retry policy 按 `retry_attempt` 递增并保持 tenant/trace context，达到 `max_attempts` 后以 persistent message 进入 DLQ；
- RabbitMQ transport subset：`aio_pika` adapter 声明 durable exchange/queue/DLQ，启用 publisher confirms，验证 NACK redelivery 和 reject-to-DLQ；
- Outbox/RabbitMQ publisher subset：PostgreSQL `infra_outbox_events` claim 后发布到 RabbitMQ，publish 返回后标记 `published`，消费端写入 `infra_inbox_messages` 后 ACK；
- Outbox crash recovery subset：模拟 publish 后、complete 前崩溃，超时 reclaim claimed row，重新发布同一 event，并由 inbox dedup 保持单行 receipt；
- RabbitMQ broker restart subset：durable topology 和 persistent message 经真实 `docker restart zuno-rabbitmq` 后仍可重新连接消费；
- RabbitMQ network partition subset：fault proxy 暂停 client/broker 双向转发；partition 中 publish deadline fail closed，恢复后 confirm/message-id 对账 UNKNOWN delivery，新 transport 重连并消费 partition 前与恢复后消息；
- Outbox partition recovery subset：confirm-UNKNOWN 时 PostgreSQL row 保持 claimed，恢复 confirm 后模拟 owner 未 complete，stale reclaim 使用同 event id republish，最终 Outbox published 且 Inbox 单行；
- Consumer crash subset：Inbox + follow-up Outbox 在提交前 crash 时共同 rollback，未 ACK delivery 经新连接 redeliver；提交后 duplicate 由 `InboxReceipt.first_seen=false` 阻止重复 follow-up 写入；
- RabbitMQ out-of-order subset：tenant-scoped Outbox sequence 与 message header 经真实 RabbitMQ 以 `3,1,2` 交付；Inbox 持久缓冲 sequence 3，consumer engine 重建后重载 payload/hash，delivery watermark 最终收敛到 `3/3`，duplicate sequence 不重复处理；
- Outbox delivery policy subset：真实 RabbitMQ 停机期间 Publisher Owner 将第一次失败持久化为 delayed backlog，第二次失败耗尽后进入 dead-letter；服务恢复后人工 replay 保留 owner/次数/错误审计，并以同一 event id 完成 publisher confirm，消息头记录总尝试、当前 retry 与 replay 次数；
- Idempotency Claim lifecycle subset：same hash replay、different hash fail-closed、renew、expiry reclaim、stale generation reject、result replay 和 12-thread high-concurrency single-winner 经真实 PostgreSQL 验证；
- Idempotency owner crash subset：worker 子进程提交 in-progress claim 后退出，replacement owner 在 expiry 后接管，旧 generation 完成被拒绝，replacement result 可 replay；
- Idempotency tenant isolation subset：`app.tenant_id` 参与唯一键边界，同一 scope/key 在不同 tenant 下可保存不同 request hash/result，同 tenant hash conflict 仍 fail closed；
- Idempotency worker supervision：长任务由 heartbeat 跨 TTL 保持 owner；错误 owner、过期 owner 与 stale generation 均不能 complete/abort；确定无 effect 的失败立即 abort 并由下一 generation 接管；worker 子进程提交 Outbox effect 后退出时，replacement 通过 reconciliation 完成 Claim 且不重复执行 operation；
- Lease/Fencing subset：lease acquire、heartbeat renew、duplicate worker reject、expiry transfer、cancel transfer 和 late fencing token reject 经真实 PostgreSQL 验证；
- Lease/Fencing Worker Coordinator：deadline/renew 使用 PostgreSQL 时钟；同 owner live reacquire 保持 lease identity；显式 transfer 递增 epoch；`FOR UPDATE` fence 与业务写同事务；heartbeat 跨 TTL 保持 owner；crash handoff、pause/GC delay、cancel/transfer race、clock tolerance、PostgreSQL TCP blackhole 与恢复后的旧 token late commit reject 均通过；
- MinIO/S3 smoke：创建临时 bucket，写入对象，读回并校验 SHA-256，删除对象和 bucket。
- MinIO/S3 object staging：`MinioObjectStore` 写入 `_staging/<sha256>/...` 并记录 content hash；
- MinIO/S3 duplicate and visibility subset：相同 content/object re-stage 收敛到同 staged key/hash，commit 前 visible key 不可读，missing object read fail closed；
- MinIO/S3 restore：commit 后创建 restore point，删除 visible object，再从 restore point 恢复并校验 hash/bytes；
- MinIO/S3 storage restart subset：committed object 与 restore point 经真实 `docker restart zuno-minio` 后仍可读取且 bytes/hash receipt 不变；
- MinIO/S3 multipart recovery subset：真实两段 multipart upload 完成后 bytes/hash 一致；partial upload 在完成前不可读，active upload 不被误清理，orphan upload 可 abort；服务端已完成但响应丢失及重复 complete 均通过 size/hash 对账收敛到同 staged receipt；
- MinIO/S3 governance subset：Object Lock committed version、GOVERNANCE retention、legal hold、exact-version purge deny、`_staging/` expiration lifecycle 与 authorization hook deny-before-I/O 均经真实 MinIO 验证；
- MinIO/PostgreSQL Manifest adoption：Input domain fact 与 staged/visible Manifest 使用同一 Domain UoW；物理 commit 后 DB 更新前 crash 保持 staged gate，reconciler 按 raw SHA-256/size 收敛；篡改 object 持久 quarantine，删除先撤销数据库可见性再物理 purge；
- Backup/Restore/Replay subset：真实 `pg_dump` 备份，恢复到临时 PostgreSQL DB，校验 `infra_outbox_events`、`infra_inbox_messages`、`infra_object_manifests`、`infra_checkpoints` 的唯一 recovery marker，并清理临时 DB 和 dump；
- Restore Runtime restart subset：`pg_restore` 后针对临时恢复库新建 sync/async `PostgresRuntime`，两类 health/readiness 和 read-only UoW 均能读取对应恢复事实；
- 三服务组合故障 subset：PostgreSQL、RabbitMQ、MinIO 同时停止期间新连接/读取 fail closed；恢复后新建 Runtime 与 Adapter 对账 durable RabbitMQ marker、Outbox→Inbox、MinIO bytes/hash、Object Manifest 和 checkpoint primitive；
- Operator readiness subset：真实 PostgreSQL sync/async health/readiness、pool metrics、Outbox backlog、RabbitMQ durable queue depth、MinIO stage/commit/read、trace correlation、failure owner/retry owner/recovery owner 与 evidence ref 均由结构化 snapshot 验证；Operator readiness telemetry 不生成 Eval verdict。
- Capacity admission subset：PostgreSQL `infra_capacity_admissions` / `infra_capacity_reservations` 提供 drain flag、generation、atomic reservation、owner-fenced release 和 capacity exhaustion backpressure；并发两个 worker 只有一个获得 capacity，错误 owner release 被拒绝，release 后 capacity 可恢复，drain 后新 admission fail closed。
- Mandatory audit subset：PostgreSQL `infra_audit_channels` / `infra_mandatory_audit_events` 提供 durable audit receipt、effect 前 durable audit gate、fail-closed audit capacity mode，以及 effect observed 后 capacity 释放；无 durable audit 时 effect outbox 写入被拒绝，capacity 满时 audit fail closed 且 no effect。
- Cutover snapshot subset：PostgreSQL `infra_cutover_targets` / `infra_cutover_snapshots` / `infra_active_snapshot_refs` 提供 target generation、CAS cutover activation、active snapshot reference 和 retirement guard；stale generation 被拒绝，当前 active snapshot 不能退休，带 active ref 的 superseded snapshot 不能退休。
- Recovery watermark subset：PostgreSQL `infra_recovery_watermarks` / `infra_recovery_sets` / `infra_recovery_set_members` 提供 authoritative/derived component watermark、RecoverySet alignment、mismatch fail-closed 和 verification hash；derived index watermark 落后时 RecoverySet 创建被拒绝，对齐后才 verified。
- Secret rotation / tenant hit subset：PostgreSQL `infra_secret_versions` / `infra_secret_rotation_heads` / `infra_secret_leases` 提供 generation-fenced secret activation、active-version lease receipt、secret material reject 和 rollback；`infra_cross_tenant_hits` 持久化跨租户命中的 FAIL_CLOSED / QUARANTINE 证据，并在运行时拒绝继续服务。
- PITR alignment subset：临时真实 PostgreSQL primary/recovery 容器启用 WAL archive、`pg_basebackup` 和 recovery target time；恢复库中 verified RecoverySet 的 PostgreSQL/Object/Checkpoint/Index watermark 均对齐，target time 之后写入的 derived index ahead watermark 未进入恢复结果。
- DR Profile subset：`docs/governance/infrastructure-dr-profile.yaml` 明确 PostgreSQL、Object Manifest/MinIO、RabbitMQ Outbox/Inbox、official Checkpointer、Product Projection Replay 和 PITR 的 RPO、RTO、owner、recovery owner、验证命令、evidence ref 与 cutover fail-closed policy；其中 official Checkpointer 仍为 blocked，product projection replay 仍为 target_not_current。
- Infrastructure Capability Profile subset：`InfrastructureCapabilityProfileV1` 和 `DataServiceCapabilityV1` 提供 frozen Pydantic contract、canonical content hash、profile version、deployment class、typed service capability、config hash、supported/unsupported semantics 和派生服务非权威校验；这只证明 profile contract 本身 current，不证明 blocked adapters 已实现。
- Backup/Service Boundary subset：`tools/scripts/verify_phase04_backup_service_boundaries.py` 固化 Backup Scope/RPO/Encryption/Verify profile，并把 PostgreSQL、RabbitMQ、Object Store 和 Checkpoint Store 的 typed service boundary 纳入同一 gate；该 gate 不证明生产 encrypted backup、PITR、完整 RecoverySet 或 official Checkpointer restore。
- Infrastructure docs governance subset：`tools/scripts/verify_phase04_infrastructure_docs_governance.py` 固化 Current/Target/Future/Explicitly Not Selected 分层、唯一正式 Infrastructure Target 文档、Agent 镜像、architecture canonical 四文件集合和文档入口；该 gate 不替代任何 runtime 证据。
- Infrastructure/domain boundary subset：`tools/scripts/verify_phase04_infrastructure_domain_boundary.py` 固化 Queue ACK、RabbitMQ delivery、Object Commit、Idempotency Claim、Object Manifest visibility 和 operator telemetry 都不能解释为 product/domain success；MinIO manifest adoption verifier 同时证明 object receipt 不会在 crash path 推进领域成功。
- Infrastructure typed-port subset：`tools/scripts/verify_phase04_infrastructure_typed_ports.py` 固化 Developer CI 与 Server Product profile 共用同一 typed contract surface，并覆盖 PostgreSQL、RabbitMQ、Object、Checkpoint、Vector、Graph、Lexical、Cache、Secret 和 Telemetry service kind；unknown service kind fail closed。
- Tenant isolation profile subset：`TenantIsolationProfileV1` 为每个 typed Infrastructure service kind 固定 tenant scope、默认 target、强隔离选项、cross-tenant action 和 evidence ref；runtime cross-tenant hit gate 已由 `ARCH-INFRA-058` 单独证明。
- Tenant physical constraints subset：`tools/scripts/verify_phase04_tenant_physical_constraints.py` 把 `ARCH-INFRA-034` 固定到当前真实服务证据：PostgreSQL tenant context、tenant-scoped unique key 和 SQL filter，RabbitMQ tenant header，Object ref/MinIO bucket-prefix-auth hook，以及 Operator tenant snapshot；official Checkpointer tenant physical constraint 仍随 official Checkpointer blocker 保留。
- Contract ownership boundary subset：`tools/scripts/verify_phase04_contract_ownership_boundaries.py` 固化 Index write/receipt/visibility 与 Knowledge acceptance 分层、IndexManifest/Acceptance 领域归属，以及 PreparedToolAction/ActionProposal/SecurityApproval/AuditPersistence owner 不重叠；该 gate 不替代 index adapter runtime、Tool effect runtime 或 audit runtime。
- Reconciler supervision boundary subset：`tools/scripts/verify_phase04_reconciler_supervision_boundary.py` 固化 IdempotencyWorkerSupervisor 的 reconcile callback、owner/generation/expiry fencing、lost completion no-reexecution，以及 LeaseWorkerCoordinator 的 heartbeat、同事务 fenced commit、crash handoff 和 PostgreSQL partition fail-closed；该 gate 不证明所有产品 Reconciler 已接入。
- Checkpoint boundary/version subset：`tools/scripts/verify_phase04_checkpoint_boundary_version.py` 固化 `agent_runtime_checkpoints` 归 Agent Core、`infra_checkpoints` 为 Infrastructure receipt、Checkpoint Commit 不等于 Domain Commit，以及 CHECKPOINT adapter/schema unknown version fail-closed；该 gate 不证明 official Checkpointer runtime 已安装或可恢复。
- Restore/cutover completion gate subset：`tools/scripts/verify_phase04_restore_cutover_completion_gates.py` 固化 backup/restore/replay marker、isolated restore target、Coordinator approval 和 cutover fail-closed policy；该 gate 不证明完整 Backup/Restore/PITR、RecoverySet 或 official Checkpointer restore。

Operator readiness 已有正式证据和 runbook，但这些结果只证明三类服务的 canonical integration path 已可用，并证明 PostgreSQL sync/async Session Runtime、完整 Alembic migration foundation、RabbitMQ Transactional Outbox/Inbox、Idempotency、Lease/Fencing、PITR alignment，以及 MinIO Object/Manifest/治理/恢复子范围；仍不能证明 official Checkpointer、完整领域 Projection Replay 或包含 Checkpointer 的组合故障恢复。

Infrastructure requirement `ARCH-INFRA-003` is now proven by `tools/scripts/verify_phase04_infrastructure_capability_profile.py`: the capability profile contract is immutable, versioned, canonical-hashed, and shared by Developer CI and Server Product deployment classes. This does not prove official Checkpointer, PITR, complete recovery set, or enterprise index adapters.

Infrastructure requirements `ARCH-INFRA-001` and `ARCH-INFRA-002` are now proven by `tools/scripts/verify_phase04_infrastructure_docs_governance.py`: Infrastructure Current/Target/Future/Explicitly Not Selected layering, the single formal Infrastructure Target document, the byte-identical Agent mirror, and canonical architecture entrypoints are machine-verifiable. This does not prove any runtime adapter, Checkpointer, PITR, or recovery set.

Infrastructure requirement `ARCH-INFRA-004` is now proven by `tools/scripts/verify_phase04_infrastructure_domain_boundary.py`: infrastructure receipts are checked against domain-success boundary evidence and the MinIO manifest crash guard. This does not prove any domain terminal state; it proves Infrastructure does not own one.

Infrastructure requirement `ARCH-INFRA-005` is now proven by `tools/scripts/verify_phase04_infrastructure_typed_ports.py`: Local/Developer CI and Server Product profiles share the same typed InfrastructureCapabilityProfile/DataServiceCapability port surface. This does not prove every target adapter is implemented.

Infrastructure requirement `ARCH-INFRA-057` is now proven by `tools/scripts/verify_phase04_tenant_isolation_profiles.py`: every service kind in the Infrastructure Capability Profile has a typed TenantIsolationProfile with tenant scope and fail-closed/quarantine/audit action. This does not prove the separate full-runtime cross-tenant hit requirement.

Infrastructure requirement `ARCH-INFRA-034` is now proven by `tools/scripts/verify_phase04_tenant_physical_constraints.py`: tenant scope participates in current PostgreSQL physical keys and filters, RabbitMQ protocol headers, Object ref/MinIO target/auth hook boundaries, and Operator tenant snapshots. This does not prove official Checkpointer tenant isolation or the separate full-runtime cross-tenant hit requirement.

Infrastructure requirements `ARCH-INFRA-046`, `ARCH-INFRA-047`, and `ARCH-INFRA-056` are now proven by `tools/scripts/verify_phase04_contract_ownership_boundaries.py`: Index write/receipt/visibility contracts are separated from Knowledge acceptance, IndexManifest/Acceptance remains domain-owned, and PreparedToolAction ownership is distinct from Agent Core proposal/binding, Security approval, and Infrastructure audit persistence. This does not prove current index adapters, Tool effect runtime, or audit durable-before-effect runtime.

Infrastructure requirement ledger subset `ARCH-INFRA-006` through `ARCH-INFRA-010` is now proven by the same real-service verifier set: PostgreSQL authoritative fact storage, Repository no-commit ownership, external I/O / DB transaction boundary, Generation/Epoch/Fencing conditional writes, and PostgreSQL role-specific pool/timeout/leak evidence are marked `implementation_available`. This subset does not include the official LangGraph PostgreSQL Checkpointer, PITR, complete Projection Replay, or the full recovery set.

Infrastructure requirement `ARCH-INFRA-064` is now proven by `tools/scripts/verify_requirement_ledger_evidence_gate.py`: every ledger item promoted to `implementation_available` must have existing current paths, current tests, current evidence refs, and complete reverse trace refs. This gate protects Target-to-Current promotion only; it does not prove any still-target runtime capability.

Infrastructure requirement `ARCH-INFRA-040` is now proven by `tools/scripts/verify_phase04_dr_profile.py`: the DR Profile has explicit RPO/RTO/Owner/Recovery Owner, bounded verification commands, existing evidence refs, and fail-closed cutover policy. This does not prove full Backup/Restore/PITR/Projection Replay or official Checkpointer recovery.

Infrastructure requirements `ARCH-INFRA-031`, `ARCH-INFRA-032`, and `ARCH-INFRA-033` are now proven by `tools/scripts/verify_phase04_capacity_admission.py`: drain stops new admission, reservations are atomically serialized by PostgreSQL, owner-fenced release restores capacity, and exhausted capacity raises backpressure. This does not prove caller-level Product/Agent/Model/Tool adoption.

Infrastructure requirements `ARCH-INFRA-054` and `ARCH-INFRA-055` are now proven by `tools/scripts/verify_phase04_mandatory_audit.py`: durable audit receipt is required before the verifier can write an effect outbox row, audit capacity exhaustion fails closed, and the capacity-failed path writes no effect. This does not prove Tool/Product/Agent/Security runtime adoption.

Infrastructure requirements `ARCH-INFRA-048` and `ARCH-INFRA-049` are now proven by `tools/scripts/verify_phase04_cutover_snapshot.py`: cutover activation uses target generation CAS, stale writers are rejected, current active snapshots cannot be retired, and superseded snapshots with active refs cannot be retired until refs are released. This does not prove full Product recovery cutover, PITR, RecoverySet, or official Checkpointer restore.

Infrastructure requirements `ARCH-INFRA-022` and `ARCH-INFRA-052` are now proven by `tools/scripts/verify_phase04_recovery_watermark.py`: authoritative and derived component watermarks must align to the requested recovery point before a verified RecoverySet can be created. This does not prove PITR, Product Projection Replay, or official Checkpointer restore.

Infrastructure requirements `ARCH-INFRA-035` and `ARCH-INFRA-058` are now proven by `tools/scripts/verify_phase04_secret_rotation_tenant_hit.py`: secret rotation is generation-fenced and rollbackable without persisting secret material, and cross-tenant hits are durably fail-closed or quarantined. This does not prove production KMS, PITR, Product Projection Replay, or official Checkpointer restore.

Infrastructure requirement `ARCH-INFRA-029` is now proven by `tools/scripts/verify_phase04_pitr_alignment.py`: WAL archive/basebackup/PITR restores to a verified DB/Object/Checkpoint/Index RecoverySet and excludes post-target derived index writes. This does not prove official Checkpointer restore or full Product Projection Replay.

Infrastructure requirements `ARCH-INFRA-026` and `ARCH-INFRA-041` are now proven by `tools/scripts/verify_phase04_backup_service_boundaries.py`: Backup Scope/RPO/Encryption/Verify is explicitly defined for each recovery component, and PostgreSQL/RabbitMQ/Object/Checkpoint service boundaries are machine-verifiable through the typed capability profile. This does not prove production encrypted backup, PITR, complete RecoverySet, or official Checkpointer restore.

Infrastructure requirement `ARCH-INFRA-039` is now proven by `tools/scripts/verify_phase04_reconciler_supervision_boundary.py`: current Infrastructure reconciler supervision uses idempotency claim fencing, reconciliation without re-execution, lease heartbeat, fencing token and fail-closed ownership loss. This does not prove every product Reconciler has adopted the boundary.

Infrastructure requirements `ARCH-INFRA-021` and `ARCH-INFRA-023` are now proven by `tools/scripts/verify_phase04_checkpoint_boundary_version.py`: Checkpoint/Domain facts are separated by schema ownership and receipt boundary, and CHECKPOINT adapter/schema unknown versions fail closed through the upgrade compatibility profile. This does not prove official Checkpointer runtime or restore.

Infrastructure requirements `ARCH-INFRA-027`, `ARCH-INFRA-028`, and `ARCH-INFRA-053` are now proven by `tools/scripts/verify_phase04_restore_cutover_completion_gates.py`: backup completion is gated by required proof markers, isolated restore does not cut over automatically, and recovery cutover requires explicit Coordinator approval. This does not prove full recovery completion.

## Existing Partial Evidence

`docs/evidence/phase04-postgres-foundation.md` remains valid only as historical partial evidence for its original primitive scope. Current aggregate evidence now separately proves PostgreSQL Domain UoW、Alembic、RabbitMQ Outbox/Inbox 与 MinIO 子能力；该旧文件不能被回写成完整 Phase 证据，PHASE04 仍受 official LangGraph PostgreSQL Checkpointer 和完整恢复闭环阻止。

## Gate Decision

PHASE04 remains not completed. PHASE05 must remain blocked until P04-T06/T07 are completed, the official LangGraph PostgreSQL Checkpointer path is proven, full Backup/Restore/Projection Replay and Checkpointer recovery evidence exists, combined dependency fault evidence includes the Checkpointer, and the Coordinator approval gate is explicit.
