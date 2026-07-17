# PostgreSQL Migration Runbook

status: current
owner: Infrastructure
applies_to: PHASE04 及后续服务器产品迁移

## 目标与边界

本 Runbook 固定 Zuno PostgreSQL Schema 的部署、既有库接管、在线 DDL、回滚与 forward-fix 边界。Alembic revision 是服务器产品 Schema 的唯一变更入口；`SQLModel.metadata.create_all()` 只允许测试构造 legacy fixture，不得用于启动、部署或恢复生产库。

Migration Owner 负责 Schema 状态和执行恢复，Data Owner 负责业务语义与回填验证，Cutover Controller 负责读写路径切换。Migration 成功不等于业务 Cutover 成功。

## 部署前 Gate

1. 固定应用 Commit、配置 SHA-256、目标 Alembic head 和数据库备份引用。
2. 确认 `python tools/scripts/verify_phase04_alembic_migration.py` 与 `python tools/scripts/verify_phase04_existing_database_upgrade.py` 通过。
3. 检查 `alembic -c infra/db/alembic.ini heads` 只有一个 head。
4. 检查当前 revision、长事务、锁等待、可用磁盘和连接池余量。
5. Schema 删除、不可逆数据变换、关键唯一约束变化或超出已验证锁预算时停止执行并提交 Coordinator Decision。

## 空库部署

```powershell
alembic -c infra/db/alembic.ini upgrade head
alembic -c infra/db/alembic.ini current
python tools/scripts/verify_phase04_alembic_migration.py
```

Base revision `20260417_01` 已冻结为 31 张领域表的显式 DDL。任何 revision 都不得导入 runtime metadata 后调用 `create_all()` 或 `drop_all()`。

## 既有库接管

仅当数据库已有完整 legacy domain schema、没有 `alembic_version`，并且 metadata drift 为零时使用：

1. 对目标库执行可恢复备份并记录 hash。
2. 在隔离副本运行 `python tools/scripts/verify_phase04_existing_database_upgrade.py`。
3. 校验目标库的 31 张领域表、列、类型、server default、index 与 frozen base 完全一致。
4. 只有零 drift 才执行 `alembic -c infra/db/alembic.ini stamp 20260417_01`。
5. 执行 `alembic -c infra/db/alembic.ini upgrade head`，再重复执行一次验证幂等。
6. 校验种子数据、领域行数/hash、infra schema、在线 index 和 validated constraint。

发现 drift 时禁止 stamp。先创建独立 reconciliation / forward-fix revision，不得用 stamp 掩盖未知 Schema。

## 在线 DDL

- 大表普通 index 禁止直接 `CREATE INDEX`；使用 Alembic `autocommit_block()` 和 `CREATE INDEX CONCURRENTLY`。
- 新 check constraint 先 `ADD CONSTRAINT ... NOT VALID`，再独立 `VALIDATE CONSTRAINT`。
- 新 `NOT NULL`、唯一约束、列类型重写或大表 backfill 必须先测量锁和扫描成本，再走 Expand → Migrate → Verify → Contract。
- 并行部署由 PostgreSQL advisory lock `zuno:alembic:migration:v1` 阻止；超时必须 fail closed。

当前参考实现为 revision `20260717_09` 的 concurrent index 与 `20260717_10` 的 add-then-validate constraint。

## 回填与 Cutover

回填必须登记 `BackfillSpec`，使用 chunk id、payload hash、source watermark、durable cursor、lease generation 和 verification hash。Pause/Resume、重复 chunk、hash conflict、stale generation 与 forward-fix lineage 由 `PostgresBackfillController` 管理。

只有 backfill state 为 `completed` 且 verification hash 与 Data Owner 复核一致，PHASE02 Cutover Controller 才能推进读写切换。

## 失败恢复

- Revision 尚未提交且事务可回滚：让 Alembic 回滚，释放 advisory lock，修复后重跑。
- Concurrent index 中断：检查 `pg_index.indisready/indisvalid`；无效 index 必须并发删除后由 forward-fix revision 重建。
- Constraint validation 失败：保留 `NOT VALID` constraint，修复冲突数据，再由新 revision 验证；不要删除失败证据。
- 已提交且下游开始依赖：默认 forward-fix，不回滚到绕过 Security、Audit 或新 Contract 的旧路径。
- 不可逆数据变换：停止自动执行，从备份恢复到隔离库并完成 hash/row-count 对账后再决定恢复或 forward-fix。

## 收尾证据

记录 Commit、revision before/after、配置 hash、数据库版本、开始/结束时间、锁等待、row count/hash、命令结果、备份引用和未运行验证。最后运行：

```powershell
python tools/scripts/verify_phase04_alembic_migration.py
python tools/scripts/verify_phase04_existing_database_upgrade.py
python tools/scripts/verify_phase04_migration_control.py
python tools/scripts/verify_phase04_complete_infrastructure.py
```
