# PHASE04 Alembic 迁移证据

phase_id: PHASE04
task_id: P04-T02
date: 2026-07-17
status: implementation_available
verification_baseline_commit: 49015ed714f085b52f20f89581e510bb2997835c
head_revision: 20260718_11
temporary_database_upgrade_head: passed
repeated_upgrade_head: passed
downgrade_base: passed
reupgrade_head: passed
infra_table_roundtrip: passed
single_revision_chain: passed
frozen_explicit_baseline: passed
module_ownership_registry: passed
schema_drift_detection: passed_full_domain_and_infra
existing_database_upgrade: passed
online_index_concurrently: passed
online_constraint_validation: passed
delivery_ordering_schema: passed
data_backfill_framework: passed
online_migration_lock: passed
forward_fix_lineage: passed
p04_t02_completion: proven

## 结论与边界

P04-T02 已达到 `implementation available`。服务器产品 Schema 的唯一变更入口是单一 Alembic revision chain；空库、production-like 既有库、重复执行、完整 downgrade/re-upgrade、全量领域与基础设施 drift、迁移锁、持久回填、在线 index、约束渐进验证和 forward-fix 均已在真实 PostgreSQL 16 验证。

这只关闭 P04-T02，不关闭 PHASE04。Backfill framework 不等于任一领域数据已经迁移或 cutover；各领域 Owner 仍必须用同一 ledger 提交独立数据迁移与对账证据。

## 环境与可复现输入

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，`PostgreSQL 16.14`，镜像族 `postgres:16` |
| 管理连接 | `postgresql+psycopg://postgres:postgres@localhost:5432/postgres` |
| 临时数据库 | `zuno_phase04_alembic_<uuid>`、`zuno_phase04_existing_<uuid>` |
| Compose SHA-256 | `fb53082b499ec5363591562d8a67d663c4430e13bd26903a136f4677df9e1d23` |
| Alembic config SHA-256 | `6a7b2e86ed968e5994343fab47692d34e3d1f66c03c4856547b0fb4f27f949ba` |
| Frozen base SHA-256 | `98b571beaf38e66d76f55695da0a3952e4e9b5869963e87f5de3053db11dd494` |
| Online index revision SHA-256 | `4072fe1447697ff9e3c2e9e0c7c36585452e941a311f8f8588a967ab420788a3` |
| Online constraint revision SHA-256 | `bc2d1e5632aaf9083cb14dfe2fc006c36d3470340b705b1da8cf9f88e67298a2` |
| Empty DB verifier SHA-256 | `5298344a5e68aaa248846d452a14fa6d5e9fb08a64830200d24eec2c2d6ac782` |
| Existing DB verifier SHA-256 | `56e423f82ce872e0041c3cfe37484cd8b590785fe4be9e9f87d468cf6e1c162f` |

## 已验证行为

- `20260417_01` 已冻结为 31 张领域表的显式 `op.create_table` / index DDL；所有 revision 均禁止 `metadata.create_all()` 与 `drop_all()`。
- `schema_registry.py` 为 31 张领域表和 12 张基础设施表登记唯一模块 Owner，并覆盖全部 revision；ScriptDirectory 证明只有一个 head、无 branch label、revision registry 无缺漏。
- 空库从 base 升级到 `20260718_11`，重复 upgrade 无副作用；downgrade base 删除全部 43 张托管表，再次 upgrade 完整重建。
- Alembic `compare_metadata` 对 31 张领域表执行完整 drift 比较；基础设施表同时校验列、约束、index 和 server default。
- Production-like 既有库先由当前 frozen metadata 构造并写入种子事实，证明零 drift 后 stamp `20260417_01`，再 upgrade/repeated upgrade 到 head；原有 `message_like` 与 `workspace_session` 数据保持不变。
- `20260717_09` 通过 Alembic `autocommit_block()` 执行 `CREATE INDEX CONCURRENTLY`，真实数据库中的 index 为 ready 且 valid。
- `20260717_10` 使用 `NOT VALID` 后独立 `VALIDATE CONSTRAINT`，真实数据库中的约束为 validated。
- Alembic online execution 在 revision 前获取 PostgreSQL session advisory lock；并行 deploy 超时 fail closed，锁释放后可恢复。
- Backfill ledger 支持 immutable spec、chunk 幂等、payload hash 冲突拒绝、cursor/watermark、pause/resume、lease generation fencing、verification hash 和 forward-fix lineage。
- 正式操作流程、stamp 禁止条件、在线 DDL、失败恢复和证据要求固定在 `docs/governance/postgresql-migration-runbook.md`。

## 命令与结果

```text
python tools/scripts/verify_phase04_alembic_migration.py
PHASE04 Alembic migration verification passed.
```

```text
python tools/scripts/verify_phase04_existing_database_upgrade.py
PHASE04 existing database upgrade verification passed.
```

```text
python tools/scripts/verify_phase04_migration_control.py
PHASE04 migration control verification passed.
```

```text
pytest -q tests/integration/test_phase04_alembic_migration.py tests/integration/test_phase04_existing_database_upgrade.py tests/integration/test_phase04_migration_control.py -p no:cacheprovider
3 passed
```

## 剩余目标

- 各领域的实际数据迁移与读写 cutover 必须由领域 Owner 独立证明，不能从 framework 完成状态推导。
- 不可逆数据变换仍是 Stop Condition；必须先备份、隔离恢复与对账，再由 Coordinator 决定 forward-fix 或恢复。
- P04-T06、P04-T07 与 PHASE04 总关闭闸门仍未完成。
