# PHASE04 PostgreSQL Domain and Transaction Foundation

phase_id: PHASE04
status: planned
depends_on: PHASE03
owner: Module 11 Infrastructure

## 订正说明

2026-07-16 撤回此前 `completed` 结论。现有 PostgreSQL 16 Migration、基础 UoW、Outbox/Inbox、Idempotency、Lease/Fencing、Object Manifest 和 Checkpoint 表及 5 个集成测试作为部分实现保留，但它们只证明最小 Primitive，不证明完整基础设施 Runtime。

本 Phase 不再接受“最小真实集成闭环”。必须完成 PHASE04 范围内服务器产品 Target 的真实 PostgreSQL、RabbitMQ、S3-compatible Object Store、LangGraph PostgreSQL Checkpointer、Migration、Backup/Restore、并发、故障和恢复能力。

## Phase 目标

建立后续 Security、Observability、Agent Core、Product、Ingestion、Knowledge、Memory、Capability 和 Tool Runtime 可共同依赖的完整耐久基础设施层：

```text
PostgreSQL 16+ and Alembic
Domain Unit of Work and transaction boundaries
Transactional Outbox and Inbox
RabbitMQ at-least-once transport
Idempotency Claim
Worker Lease and Fencing
S3-compatible Object Store and Manifest
LangGraph PostgreSQL Checkpointer
Backup/Restore, replay and disaster recovery evidence
Health, readiness, metrics and operator runbooks
```

Infrastructure 只拥有物理事实、Claim、Lease、Delivery、Commit、Visibility 和 Recovery Receipt，不重定义 Agent、Knowledge、Memory、Tool、Product 或 Security 领域终态。

## Minimal Read Set

- `docs/modules/11-infrastructure.md`
- PHASE01 Persistence/Runtime Inventory 与 Requirement Ledger
- PHASE02 Data Cutover、Rollback 和 Guard
- PHASE03 完整 Contract Bundle
- 当前 database/queue/storage/checkpoint/service 代码、Compose、Alembic、CI 和测试

## Current Anchors

```text
src/backend/zuno/platform/database/**
src/backend/zuno/platform/services/queue/**
src/backend/zuno/platform/services/storage/**
src/backend/zuno/platform/queue/**
src/backend/zuno/platform/storage/**
src/backend/zuno/platform/checkpoint/**
src/backend/zuno/agent/runtime/store.py
src/backend/zuno/agent/runtime/checkpointer.py
infra/**
all migration roots
SQLite/SQLModel/local adapters
```

## Allowed Paths

```text
src/backend/zuno/platform/database/**
src/backend/zuno/platform/queue/**
src/backend/zuno/platform/storage/**
src/backend/zuno/platform/checkpoint/**
src/backend/zuno/platform/services/queue/**
src/backend/zuno/platform/services/storage/**
infra/**
alembic/**
tests/unit/**
tests/integration/**
tests/fault/**
tests/e2e/**
tools/scripts/verify_phase04_*.py
docs/evidence/**
.agent/programs/work-products/**
```

## Forbidden Paths

- 在 Infrastructure 表或 Receipt 中复制 Agent、Knowledge、Memory、Tool、Product 或 Security 业务终态。
- 用 Queue ACK、Object Commit、Checkpoint Commit、Audit Persistence 或 Lease Release 更新领域成功。
- 只在 SQLite、Fake Queue、Mock S3 或内存 Checkpointer 上证明服务器产品语义。
- 创建永久 `legacy_*` schema/table/package、永久双写或无期限 Store Adapter。
- 省略并发、Crash、Network Partition、Duplicate、Out-of-order、Restore 和 Fencing 测试。
- 将服务能连接或表能创建写成完整实现。

## Work Packages

### P04-T01 Production PostgreSQL Configuration, Session and Domain UoW

- Goal：实现 sync/async Engine、Session Factory、显式 transaction scope、tenant context、statement/lock timeout、pool health/readiness、connection rotation 和 test fixture。
- Tests：commit/rollback、nested misuse、connection loss、deadlock/serialization retry boundary、timeout、pool exhaustion、tenant leakage、read-only transaction。
- Acceptance：Domain Service 通过 Port/UoW；没有共享全局 Session；事务 Retry 与业务 Retry 分离。

### P04-T02 Complete Alembic, Naming, Drift and Data Migration Foundation

- Goal：冻结 Revision Chain、schema/constraint/index naming、module ownership、upgrade/downgrade/forward-fix、online migration 和 drift detection。
- Tests：空库 upgrade head、生产基线 upgrade、downgrade/upgrade、重复执行、并行 deploy、schema drift、不可回滚恢复策略。
- Acceptance：`create_all()` 仅测试用途；所有服务器产品 Schema 由 Alembic 管理；Migration 与 PHASE02 Cutover Record 对接。

### P04-T03 Transactional Outbox, Inbox and RabbitMQ Transport

- Goal：实现同事务 Outbox、Publisher Claim/Lease、RabbitMQ topology、publisher confirm、consumer Inbox、dedup/hash conflict、ordering metadata、retry/dead-letter/replay 和 backlog visibility。
- Tests：commit 前/后 crash、lost confirm、duplicate publish/consume、same key different hash quarantine、out-of-order、consumer crash、redelivery、DLQ replay、broker reconnect/partition。
- Acceptance：RabbitMQ 提供 at-least-once transport；Queue Receipt 不冒充领域消费成功；Outbox/Inbox 与领域事务原子边界有真实证据。

### P04-T04 Complete Idempotency Claim Service

- Goal：实现 scope/key/request_hash/owner/status/generation/expiry/result_ref、renew、complete、abort、conflict 和 reconciliation。
- Tests：同 key/hash 返回原结果；不同 hash conflict；高并发单 Claim；过期/续租；Owner crash；结果丢失；跨 Tenant 隔离。
- Acceptance：Claim 使用 PHASE03 Canonical Hash，不保存 Secret；不能替代业务幂等键或 Effect Reconciliation。

### P04-T05 Complete Lease, Fencing and Worker Coordination

- Goal：实现 worker lease、heartbeat、epoch/fencing token、claim transfer、drain/cancel、late commit rejection 和 clock-skew policy。
- Tests：lease loss、old worker late result、duplicate worker、network partition、pause/GC delay、cancel race、clock tolerance、handoff after crash。
- Acceptance：业务 Owner 在写入结果前验证 Fencing；旧 Holder 永远不能覆盖新 Generation。

### P04-T06 S3-compatible Object Store and LangGraph PostgreSQL Checkpointer

- Goal：实现 staging/upload/hash/commit/visibility/read/delete/restore Object Adapter、Manifest/Retention/Legal Hold Receipt，以及官方 LangGraph PostgreSQL Checkpointer Adapter、thread/namespace/generation/schema-version/cursor 管理。
- Tests：partial/multipart upload、hash mismatch、lost response、visibility lag、duplicate commit、authorization、delete/restore/legal hold；checkpoint crash/restart、interrupt/resume、thread isolation、concurrent generation、schema upgrade、domain/checkpoint reconcile。
- Acceptance：真实 MinIO/S3-compatible 环境和真实 LangGraph Checkpointer 路径通过；Object/Checkpoint Receipt 不等于领域提交。

### P04-T07 Backup, Restore, Replay, Concurrency and Operational Evidence

- Goal：完成 PostgreSQL/RabbitMQ/Object/Checkpointer 组合环境的 Backup/Restore、Projection Replay、Recovery Set、contention、capacity baseline、health/readiness 和 Runbook。
- Tests：容器/CI 冷启动、Alembic、并发 Claim、Outbox Backlog、Broker Restart、Object Restore、PostgreSQL Restore/PITR（环境支持时）、Checkpoint Resume、Hash/Watermark Reconcile、partial dependency outage。
- Acceptance：恢复后领域事实、Outbox/Inbox、Object Manifest、Checkpoint Generation 和 Projection Watermark 可对账；不可用环境必须标记 blocked，不能以本地替代品关闭 Phase。

## Phase 完成定义

- PostgreSQL、Alembic、UoW、Outbox/Inbox、RabbitMQ、Idempotency、Lease/Fencing、S3-compatible Object Store 和 LangGraph PostgreSQL Checkpointer 均有真实实现与 Integration Evidence。
- Crash、Duplicate、Out-of-order、Network Partition、Lease Loss、Late Result、Hash Conflict、Lost Response、Delete/Restore 和 Replay Fault Test 通过。
- Backup/Restore、Migration、Rollback/Forward-fix、Projection Replay 和 Recovery Reconciliation 有可重复命令与 Evidence。
- Health/Readiness/Metrics/Runbook 可用；后续 Phase 可通过稳定 Port 使用这些能力。
- SQLite/local adapters 只保留 Developer/CI profile，并与服务器产品 Target 明确隔离；无永久 Legacy Store 包或 `legacy_*` 表。
- Requirement Ledger 中属于 PHASE04 的 Mandatory 项全部有 Code/Migration/Test/Evidence；任何范围内 `target_not_current` 项都会阻止关闭。
- 所有 Work Package 经 Coordinator 批准，不能停留在 `completion_candidate`。

## Validation

```bash
git diff --check
alembic -c infra/db/alembic.ini upgrade head
alembic -c infra/db/alembic.ini downgrade <verified_revision>
alembic -c infra/db/alembic.ini upgrade head
python tools/scripts/verify_current_program.py
python tools/scripts/verify_phase04_postgres_foundation.py
python tools/scripts/verify_phase04_complete_infrastructure.py
pytest -q tests/integration tests/fault tests/e2e -k 'postgres or alembic or outbox or inbox or rabbitmq or idempotency or lease or fencing or object or minio or s3 or checkpoint or restore or replay' -p no:cacheprovider
# Backup/restore and service-combination commands with exact environment/version/hash are stored in docs/evidence/
```
