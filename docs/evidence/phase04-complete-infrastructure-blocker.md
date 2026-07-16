# PHASE04 Complete Infrastructure Blocker Evidence

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-16
status: blocked
coordinator_decision: not_approved
real_services_smoke: passed
langgraph_postgres_checkpointer: missing
backup_restore_replay: missing
rabbitmq_fault_evidence: missing
minio_restore_evidence: missing
combined_dependency_fault: missing
rabbitmq_transport_subset: passed
outbox_rabbitmq_publisher_subset: passed
minio_object_store_subset: passed
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
| `pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider` | passed, `5 passed` against real PostgreSQL on localhost:5432 |
| `python tools/scripts/verify_phase04_real_services_smoke.py` | passed; PostgreSQL schema dump contains infrastructure tables, RabbitMQ publish/get succeeds, MinIO put/get/delete hash check succeeds |
| `python tools/scripts/verify_phase04_rabbitmq_transport.py` | passed; durable exchange/queue/DLQ, publisher confirm path, redelivery and DLQ routing verified against real RabbitMQ |
| `python tools/scripts/verify_phase04_outbox_rabbitmq_publisher.py` | passed; PostgreSQL outbox claim, RabbitMQ publish-confirm, outbox published receipt and inbox receipt verified |
| `python tools/scripts/verify_phase04_minio_object_store.py` | passed; staging, hash mismatch fail-closed, commit cleanup, delete and restore verified against real MinIO |
| `python tools/scripts/verify_phase04_backup_restore_replay.py` | passed; `pg_dump`/temporary `pg_restore`, infra outbox/inbox/object manifest/checkpoint rows and MinIO restore point verified |

## Missing Required Proof

- RabbitMQ replay / broker restart / partition recovery
- MinIO/S3 retention, legal hold, lifecycle, authorization and storage restart
- MinIO/S3 visibility, authorization, delete and legal hold evidence
- LangGraph PostgreSQL Checkpointer interrupt/resume/thread isolation/generation reconciliation
- Backup/Restore/Replay for official Checkpointer, product projections, runtime restart and full recovery set
- PITR
- combined dependency fault evidence

## Current Verified Subset

已证明的最小真实服务闭环：

- PostgreSQL schema backup smoke：`pg_dump --schema-only` 可运行，且包含 `infra_outbox_events` 和 `infra_checkpoints`；
- RabbitMQ smoke：使用 `rabbitmqadmin` 声明临时 durable queue，发布 JSON payload，再以 `ackmode=ack_requeue_false` 读取并删除队列；
- RabbitMQ publisher confirm：`RabbitMQTransport` 使用 `aio_pika` publisher confirm channel 发布 persistent message；
- RabbitMQ redelivery：NACK `requeue=True` 后重新消费到 `redelivered=True` 的同一 message；
- RabbitMQ DLQ：Reject `requeue=False` 后 poison message 进入 durable DLQ；
- RabbitMQ transport subset：`aio_pika` adapter 声明 durable exchange/queue/DLQ，启用 publisher confirms，验证 NACK redelivery 和 reject-to-DLQ；
- Outbox/RabbitMQ publisher subset：PostgreSQL `infra_outbox_events` claim 后发布到 RabbitMQ，publish 返回后标记 `published`，消费端写入 `infra_inbox_messages` 后 ACK；
- Outbox crash recovery subset：模拟 publish 后、complete 前崩溃，超时 reclaim claimed row，重新发布同一 event，并由 inbox dedup 保持单行 receipt；
- MinIO/S3 smoke：创建临时 bucket，写入对象，读回并校验 SHA-256，删除对象和 bucket。
- MinIO/S3 object staging：`MinioObjectStore` 写入 `_staging/<sha256>/...` 并记录 content hash；
- MinIO/S3 restore：commit 后创建 restore point，删除 visible object，再从 restore point 恢复并校验 hash/bytes；
- Backup/Restore/Replay subset：真实 `pg_dump` 备份，恢复到临时 PostgreSQL DB，校验 `infra_outbox_events`、`infra_inbox_messages`、`infra_object_manifests`、`infra_checkpoints` 的唯一 recovery marker，并清理临时 DB 和 dump；

这些结果只证明三类服务已经可用，并证明 RabbitMQ transport 的 confirm/redelivery/DLQ 子集、outbox-to-RabbitMQ publisher 与 publish-before-complete crash recovery 子集、MinIO object staging/delete/restore 子集与基础设施表的 PostgreSQL backup/restore 子集；仍不能证明 broker restart/partition、official Checkpointer、retention/legal hold/lifecycle、PITR、runtime restart after restore 或组合故障恢复。

## Existing Partial Evidence

`docs/evidence/phase04-postgres-foundation.md` remains valid only as partial evidence. It records PostgreSQL 16 primitive integration, Alembic upgrade/downgrade and five focused integration tests, and the PostgreSQL focused integration test was re-run successfully after Docker was started. It explicitly remains `partial_implementation_available` with `phase_completion: withdrawn` because RabbitMQ fault semantics, MinIO/S3 restore semantics, official LangGraph PostgreSQL Checkpointer and Backup/Restore/Replay evidence are still missing.

## Gate Decision

PHASE04 remains not completed. PHASE05 must remain blocked until the official LangGraph PostgreSQL Checkpointer path is proven, Backup/Restore/Replay evidence exists, RabbitMQ and MinIO/S3 fault/restore evidence exists, combined dependency fault evidence exists, `phase04-readiness.yaml` marks P04-T01 through P04-T07 completed, and the Coordinator approval gate is explicit.
