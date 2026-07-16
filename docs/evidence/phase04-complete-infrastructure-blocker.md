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

## Missing Required Proof

- RabbitMQ publisher confirm
- RabbitMQ redelivery
- RabbitMQ DLQ
- RabbitMQ replay / broker restart / partition recovery
- MinIO/S3 object staging
- MinIO/S3 restore
- MinIO/S3 visibility, authorization, delete and legal hold evidence
- LangGraph PostgreSQL Checkpointer interrupt/resume/thread isolation/generation reconciliation
- Backup/Restore/Replay
- PITR
- combined dependency fault evidence

## Current Verified Subset

已证明的最小真实服务闭环：

- PostgreSQL schema backup smoke：`pg_dump --schema-only` 可运行，且包含 `infra_outbox_events` 和 `infra_checkpoints`；
- RabbitMQ smoke：使用 `rabbitmqadmin` 声明临时 durable queue，发布 JSON payload，再以 `ackmode=ack_requeue_false` 读取并删除队列；
- MinIO/S3 smoke：创建临时 bucket，写入对象，读回并校验 SHA-256，删除对象和 bucket。

这些结果只证明三类服务已经可用，不能证明 publisher confirm、redelivery、DLQ、official Checkpointer、restore、PITR 或组合故障恢复。

## Existing Partial Evidence

`docs/evidence/phase04-postgres-foundation.md` remains valid only as partial evidence. It records PostgreSQL 16 primitive integration, Alembic upgrade/downgrade and five focused integration tests, and the PostgreSQL focused integration test was re-run successfully after Docker was started. It explicitly remains `partial_implementation_available` with `phase_completion: withdrawn` because RabbitMQ fault semantics, MinIO/S3 restore semantics, official LangGraph PostgreSQL Checkpointer and Backup/Restore/Replay evidence are still missing.

## Gate Decision

PHASE04 remains not completed. PHASE05 must remain blocked until the official LangGraph PostgreSQL Checkpointer path is proven, Backup/Restore/Replay evidence exists, RabbitMQ and MinIO/S3 fault/restore evidence exists, combined dependency fault evidence exists, `phase04-readiness.yaml` marks P04-T01 through P04-T07 completed, and the Coordinator approval gate is explicit.
