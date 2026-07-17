# PHASE04 Migration Control 证据

phase_id: PHASE04
task_id: P04-T02
date: 2026-07-17
status: implementation_available
migration_advisory_lock: passed
parallel_deploy_fail_closed: passed
lock_release_recovery: passed
phase02_cutover_input_adoption: passed
durable_backfill_ledger: passed
chunk_idempotency: passed
chunk_hash_conflict: passed_fail_closed
pause_restart_resume: passed
stale_generation_reject: passed
forward_fix_lineage: passed
migration_control_completion_input: proven

## 边界

本证据证明 Alembic online execution 已具备 PostgreSQL session advisory lock，并证明 PHASE02 Data Cutover Matrix 可以进入持久 Backfill ledger，支持 chunk 幂等、cursor/watermark、pause/restart/resume、lease generation fencing、验证 hash 和 forward-fix lineage。

本证据与 `phase04-alembic-migration.md` 的 frozen baseline、完整 drift、既有库升级和在线 DDL 证据共同关闭 P04-T02，但不关闭 PHASE04。Backfill receipt 只证明迁移控制事实，不证明任一模块的目标领域数据已经迁移或 cutover。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，镜像 `postgres:16` |
| 数据库 | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| Alembic revision | `20260717_10` |
| Advisory lock namespace | `zuno:alembic:migration:v1` |
| Cutover 输入 | `.agent/programs/work-products/data-cutover-matrix.yaml` |
| 验证命令 | `python tools/scripts/verify_phase04_migration_control.py` |
| 集成测试 | `pytest -q tests/integration/test_phase04_migration_control.py -p no:cacheprovider` |

## 已验证行为

- Alembic online migration 在执行 revision 前获取 session advisory lock，默认等待 30 秒。
- `ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS` 只控制锁等待；非数字、零或负值 fail closed。
- 验证进程先占用同一 lock，第二个真实 Alembic 进程在 0.5 秒后失败，且输出明确的 lock timeout。
- lock 释放后，重复 `upgrade head` 恢复成功，不残留进程级或数据库级锁。
- Revision `20260717_08` 创建 `infra_migration_backfills` 与 `infra_migration_backfill_chunks`，并以 FK、状态、计数、lease shape 和 completed shape 约束状态。
- Backfill immutable spec 直接采用 PHASE02 matrix 的 owner/source/target，并以 matrix canonical hash 固定 transform version。
- 首次 claim 获得 generation 1；活动 lease 期间第二个 worker 无法获得 claim。
- chunk 首次提交原子写入 chunk receipt 并推进 cursor、source watermark 与 processed count。
- 相同 chunk id、相同 hash 的重复提交返回已有 receipt，不重复增加 processed count。
- 相同 chunk id、不同 payload hash 或 source watermark 均 fail closed，并持久增加 conflict count。
- pause 原子释放 lease；重建 SQLAlchemy engine 后由新 worker 从持久 cursor 以 generation 2 resume。
- generation 1 的旧 worker 在 resume 后写入被 fencing reject。
- 完成状态必须保存 verification hash 和 completed timestamp，且最终 cursor/count/conflict evidence 可读。
- 失败 Backfill 保存非 Secret 错误代码；只有 failed 状态可以声明 forward-fix，新记录保留 `forward_fix_of`，旧记录进入 superseded。

## 命令与结果

```text
python tools/scripts/verify_phase04_alembic_migration.py
PHASE04 Alembic migration verification passed.
```

```text
python tools/scripts/verify_phase04_migration_control.py
PHASE04 migration control verification passed.
```

```text
pytest -q tests/integration/test_phase04_alembic_migration.py tests/integration/test_phase04_migration_control.py -p no:cacheprovider
2 passed
```

## 剩余边界

- 全量领域 schema drift、module ownership matrix、production-like existing DB upgrade 与在线 DDL 已由 `phase04-alembic-migration.md` 聚合证明。
- 各领域实际数据迁移与 cutover 仍由其目标 Phase 负责，并必须复用本 ledger；不能把 framework 存在解释为领域迁移完成。
- 不可逆数据变换必须遵守 `docs/governance/postgresql-migration-runbook.md` 的 Stop Condition、备份、隔离恢复和 forward-fix 规则。
