# PHASE04 备份、恢复与重放证据

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-18
status: implementation_available_for_backup_restore_product_projection_replay_subscope
postgres_backup: passed
postgres_restore: passed
object_manifest_restore: passed
checkpoint_table_restore: passed
outbox_inbox_watermark: passed
minio_restore_point: passed
product_projection_replay: passed
product_projection_recovery_set: passed
product_projection_hash_verification: passed
official_checkpointer_restore: proven_separately
pitr: proven_separately
runtime_restart_after_restore: passed

## 边界

Backup/Restore/Replay subset != PHASE04 completion.

本证据证明当前 PHASE04 infrastructure primitive rows 的真实恢复演练、真实 MinIO 对象恢复点、恢复后 Product Projection 从权威 Product source fact 与 Object Manifest 重放、以及针对恢复库重新构建的 sync/async PostgreSQL Runtime。它不证明完整产品运行时 cutover，不证明 Agent、Knowledge、Memory、Tool 和 Observability 的跨领域 Projection Replay，也不单独证明官方 LangGraph PostgreSQL Checkpointer 恢复或 PITR；后二者由各自证据文件证明。

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
- 在源库将 Product source fact 写入真实 `infra_outbox_events`，使用 `tenant_id`、`ordering_key` 和 `ordering_sequence` 形成可恢复 source watermark。
- 在恢复库先确认 Product derived projection watermark 不存在，再从 restored Product source fact 和 restored Object Manifest 重放生成 projection payload。
- 重放时同时校验 source payload canonical hash、MinIO restored object hash、PostgreSQL manifest hash 和 projection payload canonical hash；projection hash 不替代 source fact hash。
- 重放后写入 `infra_recovery_watermarks` 的 authoritative Product watermark 与 derived Product Projection watermark，并创建 verified `infra_recovery_sets` / `infra_recovery_set_members`。
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

- 本 verifier 内的 Checkpointer primitive 恢复只覆盖 `infra_checkpoints` table；官方 Checkpointer schema/runtime 恢复由 `docs/evidence/phase04-official-checkpointer-backup-restore.md` 单独证明。
- PITR alignment 由 `docs/evidence/phase04-pitr-alignment.md` 单独证明。
- Agent、Knowledge、Memory、Tool 和 Observability 的跨领域 Projection Replay 尚未证明。
- PostgreSQL、RabbitMQ、MinIO 与官方 Checkpointer 的完整组合故障恢复仍缺失。
- P04-T07 保持 `ready`，不是 completed。
