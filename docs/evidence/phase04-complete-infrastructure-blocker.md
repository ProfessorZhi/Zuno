# PHASE04 Complete Infrastructure Blocker Evidence

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-17
status: blocked
coordinator_decision: not_approved
real_services_smoke: passed
alembic_migration_roundtrip_subset: passed
alembic_schema_drift_infra_subset: passed
migration_lock_backfill_control_subset: passed
postgres_runtime_context_timeout_subset: passed
postgres_session_runtime_subset: passed
postgres_deadlock_retry_subset: passed
postgres_serialization_retry_subset: passed
postgres_pool_exhaustion_subset: passed
postgres_connection_loss_recovery_subset: passed
langgraph_postgres_checkpointer: missing
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
lease_fencing_subset: passed
minio_object_store_subset: passed
minio_visibility_duplicate_missing_subset: passed
minio_multipart_reconciliation_subset: passed
minio_governance_subset: passed
minio_storage_restart_subset: passed
backup_restore_replay_subset: passed
backup_restore_runtime_restart_subset: passed
combined_postgres_rabbitmq_minio_fault_subset: passed

## Stop Condition

PHASE04 仍不能关闭。当前已经启动真实 PostgreSQL、RabbitMQ 和 MinIO/S3，并完成最小 smoke 验证，但完整 Phase 要求不只是“服务可连通”。

目标文件要求真实 PostgreSQL、RabbitMQ、MinIO/S3、LangGraph PostgreSQL Checkpointer、Backup/Restore/Replay 和故障证据都成立后，PHASE04 才能 completed，PHASE05 才能 ready。静态 YAML、Compose 声明、primitive table、一次性连通性测试和 mock 不能替代这些证据。

## Environment Probe

| Probe | Result |
| --- | --- |
| `docker info --format "{{.ServerVersion}}"` | Docker engine `29.4.0` |
| `docker compose -f infra/docker/docker-compose.yml ps postgres rabbitmq minio` | `zuno-postgres`、`zuno-rabbitmq`、`zuno-minio` 均为 healthy |
| `Test-NetConnection localhost -Port 5432` | initial `TcpTestSucceeded: False`; after Docker start `TcpTestSucceeded: True` |
| `Test-NetConnection localhost -Port 5672` | after Docker start `TcpTestSucceeded: True` |
| `Test-NetConnection localhost -Port 9000` | after Docker start `TcpTestSucceeded: True` |
| `python tools/scripts/verify_phase04_alembic_migration.py` | passed; temporary PostgreSQL DB upgrade head, repeated upgrade, downgrade base, re-upgrade and infra schema drift subset verified |
| `python tools/scripts/verify_phase04_migration_control.py` | passed; PostgreSQL advisory lock 阻止并行 Alembic deploy，Backfill ledger 的 matrix adoption、chunk 幂等/hash conflict、pause/restart/resume、generation fencing 与 forward-fix lineage 通过 |
| `python tools/scripts/verify_phase04_postgres_runtime.py` | passed; readiness, transaction-local tenant context, statement timeout and lock timeout verified |
| `python tools/scripts/verify_phase04_postgres_session_runtime.py` | passed; sync/async Session Factory、显式 UoW、commit/rollback、nested reject、failed-entry cleanup、read-only、tenant 并发隔离、async timeout/cancel、connection loss recovery 与 rotation 通过 |
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
| `python tools/scripts/verify_phase04_lease_fencing.py` | passed; lease acquire, heartbeat renew, duplicate worker reject, expiry transfer, cancel transfer and late fencing token reject verified |
| `python tools/scripts/verify_phase04_minio_object_store.py` | passed; staging, duplicate staging, multipart/partial upload, orphan cleanup, lost-response/duplicate-complete reconciliation, authorization deny-before-I/O, Object Lock version、retention、legal hold、lifecycle、pre-commit visibility、missing/hash fail-closed、commit cleanup、delete 和 restore 均在真实 MinIO 验证 |
| `python tools/scripts/verify_phase04_minio_storage_restart.py` | passed; committed object and restore point survived real `docker restart zuno-minio` |
| `python tools/scripts/verify_phase04_backup_restore_replay.py` | passed; `pg_dump`/temporary `pg_restore`、MinIO restore point，并在恢复库重建 sync/async PostgresRuntime 与 read-only UoW 后校验 infra rows |
| `python tools/scripts/verify_phase04_combined_service_fault.py` | passed; PostgreSQL/RabbitMQ/MinIO 同时停机期间新调用 fail closed，全部健康恢复后 persistent message、Outbox→Inbox、Object hash、Manifest 与 checkpoint primitive 对账通过 |
| `python tools/scripts/verify_phase04_complete_infrastructure.py` | expected blocked; 全部已登记真实子 verifier 执行通过，最终仍由 P04-T01–T07/审批/PHASE05 gate、official Checkpointer、完整恢复与含 Checkpointer 的组合故障 marker 阻止关闭 |

## Missing Required Proof

- 真实领域 handler adoption 与完整运维指标出口
- Alembic full domain schema drift、production-like existing DB upgrade、online index/constraint 策略与不可逆 migration 独立 runbook
- PostgreSQL domain service 默认路径接入显式 Runtime Factory/UoW，并收缩旧全局 engine/session compatibility surface
- Idempotency full worker runtime crash supervision
- Lease/Fencing worker crash handoff, network partition, pause/GC delay, cancel race and full worker coordination runtime
- LangGraph PostgreSQL Checkpointer interrupt/resume/thread isolation/generation reconciliation
- Backup/Restore/Replay for official Checkpointer、product projections、完整产品 Runtime restart 与 full recovery set
- PITR
- 包含官方 Checkpointer 的完整 combined dependency fault evidence

## Current Verified Subset

已证明的最小真实服务闭环：

- PostgreSQL schema backup smoke：`pg_dump --schema-only` 可运行，且包含 `infra_outbox_events` 和 `infra_checkpoints`；
- PostgreSQL runtime context/timeout subset：readiness、transaction-local tenant context、tenant no-leak、statement timeout 和 lock timeout 经真实 PostgreSQL 验证；
- PostgreSQL session runtime subset：显式配置创建 sync/async Engine 与 Session Factory；两类 UoW 的 commit/rollback、nested reject、isolation/read-only、并发 tenant no-leak、async timeout/cancel、backend termination recovery、pool metrics 和 connection rotation 均通过；
- PostgreSQL deadlock retry subset：真实双事务 row-lock deadlock 触发 `40P01`，retry boundary 重跑完整事务并最终提交；
- PostgreSQL serialization retry subset：真实 `SERIALIZABLE` 写偏斜冲突触发 `40001`，retry boundary 重跑完整事务并最终提交；
- PostgreSQL pool exhaustion subset：真实 PostgreSQL engine 在 `pool_size=1/max_overflow=0/pool_timeout=1` 下拒绝第二个 checkout，释放后恢复；
- PostgreSQL connection loss recovery subset：真实 `pg_terminate_backend` 终止旧 connection，旧 connection fail closed，同一 engine 重新 checkout 后恢复；
- Alembic migration roundtrip subset：临时 PostgreSQL DB 上 `upgrade head`、重复 `upgrade head`、`downgrade base`、再次 `upgrade head` 均通过，并验证 PHASE04 infra tables 创建/移除/重建；
- Alembic schema drift subset：从真实临时库读取 `information_schema.columns`、`pg_constraint` 和 `pg_indexes`，校验 PHASE04 infra tables 关键 columns、constraints、indexes 和 idempotency tenant unique boundary；
- Migration control subset：Alembic online execution 使用 PostgreSQL session advisory lock；并行 deploy 在 timeout 后 fail closed，释放后恢复。PHASE02 matrix 输入进入持久 Backfill ledger，chunk replay 幂等、hash conflict、pause/restart/resume、stale generation reject 与 forward-fix lineage 均通过；
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
- Lease/Fencing subset：lease acquire、heartbeat renew、duplicate worker reject、expiry transfer、cancel transfer 和 late fencing token reject 经真实 PostgreSQL 验证；
- MinIO/S3 smoke：创建临时 bucket，写入对象，读回并校验 SHA-256，删除对象和 bucket。
- MinIO/S3 object staging：`MinioObjectStore` 写入 `_staging/<sha256>/...` 并记录 content hash；
- MinIO/S3 duplicate and visibility subset：相同 content/object re-stage 收敛到同 staged key/hash，commit 前 visible key 不可读，missing object read fail closed；
- MinIO/S3 restore：commit 后创建 restore point，删除 visible object，再从 restore point 恢复并校验 hash/bytes；
- MinIO/S3 storage restart subset：committed object 与 restore point 经真实 `docker restart zuno-minio` 后仍可读取且 bytes/hash receipt 不变；
- MinIO/S3 multipart recovery subset：真实两段 multipart upload 完成后 bytes/hash 一致；partial upload 在完成前不可读，active upload 不被误清理，orphan upload 可 abort；服务端已完成但响应丢失及重复 complete 均通过 size/hash 对账收敛到同 staged receipt；
- MinIO/S3 governance subset：Object Lock committed version、GOVERNANCE retention、legal hold、exact-version purge deny、`_staging/` expiration lifecycle 与 authorization hook deny-before-I/O 均经真实 MinIO 验证；
- Backup/Restore/Replay subset：真实 `pg_dump` 备份，恢复到临时 PostgreSQL DB，校验 `infra_outbox_events`、`infra_inbox_messages`、`infra_object_manifests`、`infra_checkpoints` 的唯一 recovery marker，并清理临时 DB 和 dump；
- Restore Runtime restart subset：`pg_restore` 后针对临时恢复库新建 sync/async `PostgresRuntime`，两类 health/readiness 和 read-only UoW 均能读取对应恢复事实；
- 三服务组合故障 subset：PostgreSQL、RabbitMQ、MinIO 同时停止期间新连接/读取 fail closed；恢复后新建 Runtime 与 Adapter 对账 durable RabbitMQ marker、Outbox→Inbox、MinIO bytes/hash、Object Manifest 和 checkpoint primitive；

这些结果证明三类服务已经可用，并证明 PostgreSQL sync/async Session Runtime、context/timeout/deadlock retry/serialization retry/pool exhaustion/connection loss recovery 子集、Alembic 临时库往返、advisory lock 与可恢复 Backfill control 子集、RabbitMQ transport 的 confirm/redelivery/DLQ/replay/backlog depth/retry exhaustion/network partition/out-of-order 子集、Outbox Publisher 的持久 backoff/dead-letter/manual replay 与 publish-before-complete crash recovery 子集、RabbitMQ broker restart 子集、Idempotency Claim 生命周期、高并发单赢家、tenant isolation 与 owner process-exit reclaim 子集、Lease/Fencing acquire/renew/cancel/late-token reject 子集、MinIO object staging/multipart/partial-abort/lost-response reconciliation/authorization/retention/legal-hold/lifecycle/duplicate/visibility/missing/delete/restore/storage restart 子集、基础设施表的 PostgreSQL backup/restore 与恢复库 Runtime restart，以及三服务组合停机恢复子集；仍不能证明 official Checkpointer、PITR、完整领域 Projection Replay 或包含 Checkpointer 的组合故障恢复。

## Existing Partial Evidence

`docs/evidence/phase04-postgres-foundation.md` remains valid only as partial evidence. It records PostgreSQL 16 primitive integration, Alembic upgrade/downgrade and five focused integration tests, and the PostgreSQL focused integration test was re-run successfully after Docker was started. It explicitly remains `partial_implementation_available` with `phase_completion: withdrawn` because RabbitMQ fault semantics, MinIO/S3 restore semantics, official LangGraph PostgreSQL Checkpointer and Backup/Restore/Replay evidence are still missing.

## Gate Decision

PHASE04 remains not completed. PHASE05 must remain blocked until the official LangGraph PostgreSQL Checkpointer path is proven, Backup/Restore/Replay evidence exists, RabbitMQ and MinIO/S3 fault/restore evidence exists, combined dependency fault evidence exists, `phase04-readiness.yaml` marks P04-T01 through P04-T07 completed, and the Coordinator approval gate is explicit.
