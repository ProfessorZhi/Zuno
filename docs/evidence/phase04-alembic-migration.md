# PHASE04 Alembic Migration Evidence

phase_id: PHASE04
task_id: P04-T02
date: 2026-07-17
status: partial_implementation_available
temporary_database_upgrade_head: passed
repeated_upgrade_head: passed
downgrade_base: passed
reupgrade_head: passed
infra_table_roundtrip: passed
head_revision: 20260717_07
schema_drift_detection: passed_infra_schema_subset
delivery_ordering_schema: passed
data_backfill_framework: not_yet_proven
online_migration_lock: not_yet_proven

## 边界

本证据证明 Alembic 在真实 PostgreSQL 临时数据库上的迁移往返子集：空库 upgrade head、重复 upgrade head、downgrade base、再次 upgrade head、PHASE04 infra tables 的创建/移除/重建，以及基础设施表关键列、唯一约束、check constraint 和 index 的 schema drift 检查。

这不关闭 P04-T02，也不关闭 PHASE04。当前 migration chain 仍未证明完整 schema drift detection、data backfill framework、online migration lock、forward-fix 策略和所有领域 schema 的 cutover 集成。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL service | `zuno-postgres`, image `postgres:16` |
| Admin URL | `postgresql+psycopg://postgres:postgres@localhost:5432/postgres` |
| Temporary DB pattern | `zuno_phase04_alembic_<uuid>` |
| Verification command | `python tools/scripts/verify_phase04_alembic_migration.py` |
| Integration test | `pytest -q tests/integration/test_phase04_alembic_migration.py -p no:cacheprovider` |

## 已验证行为

- Verifier 创建隔离的真实 PostgreSQL 临时数据库，不修改当前 `zuno` 数据库。
- 通过临时 `ZUNO_CONFIG` 驱动 `infra/db/alembic/env.py` 指向临时数据库。
- `alembic -c infra/db/alembic.ini upgrade head` 在空库上到达 revision `20260717_07`。
- 重复 `upgrade head` 保持 revision `20260717_07`，不产生重复对象错误。
- PHASE04 infra tables 在 upgrade 后存在，且 verifier 从真实数据库读取 `information_schema.columns`、`pg_constraint` 和 `pg_indexes` 校验关键列、约束和索引。
- `alembic downgrade base` 移除 PHASE04 infra tables。
- 再次 `upgrade head` 重建 PHASE04 infra tables，并回到 revision `20260717_07`。
- Revision `20260716_05` 为 `infra_idempotency_claims` 增加 `tenant_id`，并将唯一约束从 `scope/idempotency_key` 扩展为 `tenant_id/scope/idempotency_key`。
- Revision `20260717_06` 增加 tenant-scoped Outbox sequence、Outbox/Inbox ordering metadata、`buffered` Inbox 状态和 delivery watermark，并提供可逆 downgrade；downgrade 前将 `buffered` 行 fail closed 为 `quarantined`。
- Revision `20260717_07` 增加 Outbox 发布次数、当前重试轮次、持久退避时间、dead-letter、replay 审计字段，以及 claim/dead-letter 状态约束和可领取 backlog 索引。
- Schema drift 子集校验 ordering tables、columns、pair/sequence constraints、tenant-scoped unique constraints 和 buffered lookup index。
- Schema drift 子集会检查 `tenant_id` 为 NOT NULL 且无持久 server default、旧 `uq_infra_idempotency_claims_scope_key` 不再存在、新 `uq_infra_idempotency_claims_tenant_scope_key` 存在。
- Verifier 结束时终止临时数据库连接并删除临时数据库。

## 命令与结果

```text
python tools/scripts/verify_phase04_alembic_migration.py
PHASE04 Alembic migration verification passed.
```

```text
pytest -q tests/integration/test_phase04_alembic_migration.py -p no:cacheprovider
1 passed
```

## 剩余缺口

- `20260417_01` 仍使用 `metadata.create_all()`；这不满足完整产品 migration governance。
- Schema drift detection 已覆盖 PHASE04 基础设施表关键列、约束和索引子集；全量 domain schema drift、module ownership matrix、data backfill framework、online migration lock 和 forward-fix runbook 仍未证明。
- Existing production-like DB upgrade 和 parallel deploy migration lock 尚未证明。
- P04-T02 仍是 `ready`，不是 completed。
