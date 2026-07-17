# PHASE04 备份、恢复与重放证据

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-16
status: partial_implementation_available
postgres_backup: passed
postgres_restore: passed
object_manifest_restore: passed
checkpoint_table_restore: passed
outbox_inbox_watermark: passed
minio_restore_point: passed
projection_replay: partial_infra_rows_only
official_checkpointer_restore: not_yet_proven
pitr: not_yet_proven
runtime_restart_after_restore: passed

## 边界

Backup/Restore/Replay subset != PHASE04 completion.

本证据证明当前 PHASE04 infrastructure primitive rows 的真实恢复演练、真实 MinIO 对象恢复点，以及针对恢复库重新构建的 sync/async PostgreSQL Runtime。它不证明完整产品恢复、官方 LangGraph PostgreSQL Checkpointer 恢复、PITR 或跨领域模块 Projection Replay。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL 服务 | `zuno-postgres`，镜像 `postgres:16` |
| 源数据库 | `zuno` |
| 恢复数据库 | 临时 `zuno_phase04_restore_<marker>` |
| 备份命令 | `docker exec zuno-postgres pg_dump -U postgres -d zuno -Fc -f /tmp/<restore-db>.dump` |
| 恢复命令 | `docker exec zuno-postgres pg_restore -U postgres -d <restore-db> /tmp/<restore-db>.dump` |
| MinIO 服务 | `zuno-minio`，镜像 `minio/minio:RELEASE.2023-03-20T20-16-18Z` |
| 验证命令 | `python tools/scripts/verify_phase04_backup_restore_replay.py` |
| 集成测试 | `pytest -q tests/integration/test_phase04_backup_restore_replay.py -p no:cacheprovider` |

## 已验证行为

- 在真实 PostgreSQL infrastructure tables 写入唯一 PHASE04 recovery seed rows。
- 使用 `infra_outbox_events` 作为 replay/outbox watermark，并验证恢复后的状态为 `published`。
- 使用 `infra_inbox_messages` 作为 inbox dedup replay marker，并验证恢复后的状态为 `received`。
- 使用 `infra_object_manifests` 验证 Object Manifest 恢复边界。
- 使用 `infra_checkpoints` 验证 checkpoint primitive table 恢复，不冒充官方 Checkpointer。
- 数据库备份前在真实 MinIO 完成对象提交、恢复点、删除与恢复循环。
- 对源数据库运行真实 `pg_dump`，创建隔离临时恢复库并执行真实 `pg_restore`。
- 通过新 psycopg 连接查询恢复库，验证 marker/hash 连续性。
- 针对恢复库重建 sync/async `PostgresRuntime`，验证两类 health/readiness；sync read-only UoW 读取 Outbox/Object，async read-only UoW 读取 Inbox/checkpoint primitive。
- 删除临时恢复库、容器内 dump 和 MinIO bucket，再用一个 PostgreSQL 事务删除源库 recovery seed；重复演练不遗留 marker rows。

## 命令与结果

```text
python tools/scripts/verify_phase04_backup_restore_replay.py
PHASE04 backup/restore/replay verification passed.
```

```text
pytest -q tests/integration/test_phase04_backup_restore_replay.py -p no:cacheprovider
1 passed
```

## 剩余缺口

- 官方 LangGraph PostgreSQL Checkpointer package/path 仍不可导入且未证明。
- 当前 Checkpointer 恢复只覆盖 primitive `infra_checkpoints` table，不覆盖官方 Checkpointer schema/runtime。
- PITR 尚未证明。
- Product、Agent、Knowledge、Memory、Tool 和 Observability 的跨领域 Projection Replay 尚未证明。
- PostgreSQL、RabbitMQ、MinIO 与官方 Checkpointer 的完整组合故障恢复仍缺失。
- P04-T07 保持 `ready`，不是 completed。
