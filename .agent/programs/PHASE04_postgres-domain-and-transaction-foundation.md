# PHASE04 PostgreSQL Domain and Transaction Foundation

phase_id: PHASE04
status: planned
depends_on: PHASE03
owner: Module 11 Infrastructure

## Phase 目标

建立服务器产品 Target 的 PostgreSQL 16+、Alembic、Unit of Work、Outbox/Inbox、IdempotencyClaim、Lease/Fencing、Object Manifest 和 LangGraph Checkpointer 物理基础。只拥有物理语义，不重定义模块领域事实。最终目录按 `platform/database|queue|storage|checkpoint` 清晰分层，不保留 `legacy_store` 或旧数据库兼容包。

## Minimal Read Set

- `docs/modules/11-infrastructure.md`
- PHASE01 persistence inventory
- PHASE02 data cutover matrix
- PHASE03 Contract Bundle
- 当前 database/storage/checkpoint/queue 代码

## Current Anchors

```text
src/backend/zuno/platform/database/**
src/backend/zuno/platform/storage/**
src/backend/zuno/agent/runtime/store.py
src/backend/zuno/agent/runtime/checkpointer.py
infra/**
current Alembic roots
SQLite/SQLModel stores
```

## Allowed Paths

```text
src/backend/zuno/platform/database/**
src/backend/zuno/platform/storage/**
src/backend/zuno/platform/queue/**
src/backend/zuno/platform/checkpoint/**
infra/**
alembic/**
tests/integration/**
tests/fault/**
docs/evidence/**
```

## Forbidden Paths

- 在 Infrastructure 表中复制 Agent、Knowledge、Memory、Tool 业务终态。
- 用 Queue ACK 或 Checkpoint Commit 更新领域成功。
- 只在 SQLite 上证明 PostgreSQL 并发/锁。
- 创建永久 `legacy_*` schema/table/package。

## Work Packages

### P04-T01 PostgreSQL Configuration, Session and UoW
- Goal：实现 async/sync connection、transaction scope、tenant context hook、health/readiness、test fixture。
- Tests：commit/rollback、nested misuse、connection loss、timeout、tenant leakage。
- Acceptance：Domain Service 通过 Port/UoW，不共享全局 Session。

### P04-T02 Alembic Baseline and Naming Convention
- Goal：冻结 revision chain、schema/constraint/index naming、upgrade/downgrade policy。
- Tests：空库 upgrade head、downgrade/upgrade、重复执行、schema drift。
- Acceptance：`create_all()` 仅测试用途；Migration 文件按模块清晰命名。

### P04-T03 Transactional Outbox and Inbox
- Goal：实现同事务 Outbox、publisher claim、Inbox dedup、hash conflict、DLQ metadata。
- Tests：commit 后 crash、重复 publish/consume、same key different hash quarantine、out-of-order。
- Acceptance：交付记录不冒充领域消费成功。

### P04-T04 Idempotency Claim Service
- Goal：实现 scope/key/request_hash/owner/status/generation/expiry/result_ref。
- Tests：同 key/hash 返回原结果；不同 hash conflict；并发单 claim；过期/续租。
- Acceptance：Claim 使用 canonical hash，不保存 Secret。

### P04-T05 Lease and Fencing
- Goal：实现 worker lease、heartbeat、epoch/fencing、claim transfer、晚到提交拒绝。
- Tests：lease loss、old worker late result、duplicate worker、cancel、clock tolerance。
- Acceptance：业务 Owner 验证 fencing 后才接受结果。

### P04-T06 Object Manifest and PostgreSQL Checkpointer
- Goal：实现 S3-compatible ObjectRef/Manifest/Hash/visibility/delete receipt 与 LangGraph PostgreSQL Checkpointer Adapter。
- Tests：partial upload、hash mismatch、visibility lag、delete/restore；checkpoint restart、thread isolation、schema version。
- Acceptance：Object/Checkpoint Receipt 不等于领域提交。

### P04-T07 Migration, Restore and Concurrency Evidence
- Goal：生成真实 PostgreSQL integration、backup/restore、projection replay、contention evidence。
- Tests：容器/CI Postgres、Alembic、并发 claim、outbox backlog、restore 后 hash/watermark。
- Acceptance：环境不可用写 blocked；SQLite Adapter 保留在明确 `adapters/sqlite`，不叫 legacy，不作为产品 Target。

## Phase 完成定义

- PostgreSQL/Alembic/UoW 与共享 primitive 可用。
- Outbox/Inbox、Idempotency、Lease/Fencing、Object、Checkpointer Fault Test 通过。
- 目录清晰，无永久 Legacy Store 包或 `legacy_*` 表。

## Validation

```bash
git diff --check
alembic upgrade head
alembic downgrade <verified_revision>
pytest -q tests/integration tests/fault -k 'postgres or outbox or inbox or idempotency or lease or checkpoint or object' -p no:cacheprovider
```
