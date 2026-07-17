# PHASE04 Complete Infrastructure Blocker Evidence

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-16
status: blocked
coordinator_decision: not_approved
real_services_smoke: passed
alembic_migration_roundtrip_subset: passed
alembic_schema_drift_infra_subset: passed
postgres_runtime_context_timeout_subset: passed
postgres_deadlock_retry_subset: passed
postgres_serialization_retry_subset: passed
postgres_pool_exhaustion_subset: passed
langgraph_postgres_checkpointer: missing
backup_restore_replay: missing
rabbitmq_fault_evidence: missing
minio_restore_evidence: missing
combined_dependency_fault: missing
rabbitmq_transport_subset: passed
rabbitmq_dlq_replay_subset: passed
rabbitmq_backlog_depth_subset: passed
rabbitmq_retry_exhaustion_subset: passed
outbox_rabbitmq_publisher_subset: passed
rabbitmq_broker_restart_subset: passed
idempotency_claim_lifecycle_subset: passed
idempotency_high_concurrency_single_winner_subset: passed
idempotency_owner_crash_process_exit_subset: passed
idempotency_tenant_isolation_subset: passed
lease_fencing_subset: passed
minio_object_store_subset: passed
minio_storage_restart_subset: passed
backup_restore_replay_subset: passed

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
| `python tools/scripts/verify_phase04_postgres_runtime.py` | passed; readiness, transaction-local tenant context, statement timeout and lock timeout verified |
| `python tools/scripts/verify_phase04_postgres_deadlock_retry.py` | passed; two real concurrent PostgreSQL transactions deadlocked on opposite row locks, one received transient `40P01`, retried the whole transaction and both workers committed |
| `python tools/scripts/verify_phase04_postgres_serialization_retry.py` | passed; two real `SERIALIZABLE` PostgreSQL transactions conflicted on a shared invariant, one received transient `40001`, retried the whole transaction and both workers committed |
| `python tools/scripts/verify_phase04_postgres_pool_exhaustion.py` | passed; real PostgreSQL engine with `pool_size=1`, `max_overflow=0`, `pool_timeout=1` rejected a second checkout while the only connection was held and recovered after release |
| `pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider` | passed, `9 passed` against real PostgreSQL on localhost:5432 |
| `python tools/scripts/verify_phase04_real_services_smoke.py` | passed; PostgreSQL schema dump contains infrastructure tables, RabbitMQ publish/get succeeds, MinIO put/get/delete hash check succeeds |
| `python tools/scripts/verify_phase04_rabbitmq_transport.py` | passed; durable exchange/queue/DLQ, publisher confirm path, redelivery, DLQ routing and DLQ replay verified against real RabbitMQ |
| `python tools/scripts/verify_phase04_rabbitmq_backlog.py` | passed; queue depth grows after publish and drains after ACK |
| `python tools/scripts/verify_phase04_rabbitmq_retry_exhaustion.py` | passed; retry attempts are recorded in headers, tenant context is preserved, persistent retry republishes drain the main queue and exhausted message reaches DLQ |
| `python tools/scripts/verify_phase04_outbox_rabbitmq_publisher.py` | passed; PostgreSQL outbox claim, RabbitMQ publish-confirm, outbox published receipt and inbox receipt verified |
| `python tools/scripts/verify_phase04_rabbitmq_broker_restart.py` | passed; persistent RabbitMQ message survived real `docker restart zuno-rabbitmq` |
| `python tools/scripts/verify_phase04_idempotency_claim.py` | passed; same-hash replay, different-hash conflict, renew, expiry, stale generation reject, result replay and high-concurrency single-winner verified |
| `python tools/scripts/verify_phase04_idempotency_owner_crash.py` | passed; subprocess committed an in-progress claim, exited before completion, replacement owner reclaimed after expiry, stale generation completion was rejected and replacement result replayed |
| `python tools/scripts/verify_phase04_idempotency_tenant_isolation.py` | passed; transaction tenant context participates in the idempotency uniqueness boundary and same scope/key can safely exist in two tenants with distinct request hashes/results |
| `python tools/scripts/verify_phase04_lease_fencing.py` | passed; lease acquire, heartbeat renew, duplicate worker reject, expiry transfer, cancel transfer and late fencing token reject verified |
| `python tools/scripts/verify_phase04_minio_object_store.py` | passed; staging, hash mismatch fail-closed, commit cleanup, delete and restore verified against real MinIO |
| `python tools/scripts/verify_phase04_minio_storage_restart.py` | passed; committed object and restore point survived real `docker restart zuno-minio` |
| `python tools/scripts/verify_phase04_backup_restore_replay.py` | passed; `pg_dump`/temporary `pg_restore`, infra outbox/inbox/object manifest/checkpoint rows and MinIO restore point verified |

## Missing Required Proof

- RabbitMQ network partition and full recovery
- Alembic full domain schema drift detection, data backfill framework, online migration lock and forward-fix governance
- PostgreSQL async engine and connection loss recovery
- MinIO/S3 retention, legal hold, lifecycle and authorization
- MinIO/S3 visibility, authorization, delete and legal hold evidence
- Idempotency full worker runtime crash supervision
- Lease/Fencing worker crash handoff, network partition, pause/GC delay, cancel race and full worker coordination runtime
- LangGraph PostgreSQL Checkpointer interrupt/resume/thread isolation/generation reconciliation
- Backup/Restore/Replay for official Checkpointer, product projections, runtime restart and full recovery set
- PITR
- combined dependency fault evidence

## Current Verified Subset

已证明的最小真实服务闭环：

- PostgreSQL schema backup smoke：`pg_dump --schema-only` 可运行，且包含 `infra_outbox_events` 和 `infra_checkpoints`；
- PostgreSQL runtime context/timeout subset：readiness、transaction-local tenant context、tenant no-leak、statement timeout 和 lock timeout 经真实 PostgreSQL 验证；
- PostgreSQL deadlock retry subset：真实双事务 row-lock deadlock 触发 `40P01`，retry boundary 重跑完整事务并最终提交；
- PostgreSQL serialization retry subset：真实 `SERIALIZABLE` 写偏斜冲突触发 `40001`，retry boundary 重跑完整事务并最终提交；
- PostgreSQL pool exhaustion subset：真实 PostgreSQL engine 在 `pool_size=1/max_overflow=0/pool_timeout=1` 下拒绝第二个 checkout，释放后恢复；
- Alembic migration roundtrip subset：临时 PostgreSQL DB 上 `upgrade head`、重复 `upgrade head`、`downgrade base`、再次 `upgrade head` 均通过，并验证 PHASE04 infra tables 创建/移除/重建；
- Alembic schema drift subset：从真实临时库读取 `information_schema.columns`、`pg_constraint` 和 `pg_indexes`，校验 PHASE04 infra tables 关键 columns、constraints、indexes 和 idempotency tenant unique boundary；
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
- Idempotency Claim lifecycle subset：same hash replay、different hash fail-closed、renew、expiry reclaim、stale generation reject、result replay 和 12-thread high-concurrency single-winner 经真实 PostgreSQL 验证；
- Idempotency owner crash subset：worker 子进程提交 in-progress claim 后退出，replacement owner 在 expiry 后接管，旧 generation 完成被拒绝，replacement result 可 replay；
- Idempotency tenant isolation subset：`app.tenant_id` 参与唯一键边界，同一 scope/key 在不同 tenant 下可保存不同 request hash/result，同 tenant hash conflict 仍 fail closed；
- Lease/Fencing subset：lease acquire、heartbeat renew、duplicate worker reject、expiry transfer、cancel transfer 和 late fencing token reject 经真实 PostgreSQL 验证；
- MinIO/S3 smoke：创建临时 bucket，写入对象，读回并校验 SHA-256，删除对象和 bucket。
- MinIO/S3 object staging：`MinioObjectStore` 写入 `_staging/<sha256>/...` 并记录 content hash；
- MinIO/S3 restore：commit 后创建 restore point，删除 visible object，再从 restore point 恢复并校验 hash/bytes；
- MinIO/S3 storage restart subset：committed object 与 restore point 经真实 `docker restart zuno-minio` 后仍可读取且 bytes/hash receipt 不变；
- Backup/Restore/Replay subset：真实 `pg_dump` 备份，恢复到临时 PostgreSQL DB，校验 `infra_outbox_events`、`infra_inbox_messages`、`infra_object_manifests`、`infra_checkpoints` 的唯一 recovery marker，并清理临时 DB 和 dump；

这些结果只证明三类服务已经可用，并证明 PostgreSQL runtime context/timeout/deadlock retry/serialization retry/pool exhaustion 子集、Alembic 临时库往返子集、RabbitMQ transport 的 confirm/redelivery/DLQ/replay/backlog depth/retry exhaustion 子集、outbox-to-RabbitMQ publisher 与 publish-before-complete crash recovery 子集、RabbitMQ broker restart 子集、Idempotency Claim 生命周期、高并发单赢家、tenant isolation 与 owner process-exit reclaim 子集、Lease/Fencing acquire/renew/cancel/late-token reject 子集、MinIO object staging/delete/restore/storage restart 子集与基础设施表的 PostgreSQL backup/restore 子集；仍不能证明 network partition、official Checkpointer、retention/legal hold/lifecycle、PITR、runtime restart after restore 或组合故障恢复。

## Existing Partial Evidence

`docs/evidence/phase04-postgres-foundation.md` remains valid only as partial evidence. It records PostgreSQL 16 primitive integration, Alembic upgrade/downgrade and five focused integration tests, and the PostgreSQL focused integration test was re-run successfully after Docker was started. It explicitly remains `partial_implementation_available` with `phase_completion: withdrawn` because RabbitMQ fault semantics, MinIO/S3 restore semantics, official LangGraph PostgreSQL Checkpointer and Backup/Restore/Replay evidence are still missing.

## Gate Decision

PHASE04 remains not completed. PHASE05 must remain blocked until the official LangGraph PostgreSQL Checkpointer path is proven, Backup/Restore/Replay evidence exists, RabbitMQ and MinIO/S3 fault/restore evidence exists, combined dependency fault evidence exists, `phase04-readiness.yaml` marks P04-T01 through P04-T07 completed, and the Coordinator approval gate is explicit.
