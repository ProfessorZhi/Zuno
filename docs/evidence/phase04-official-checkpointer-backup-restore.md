# PHASE04 Official Checkpointer Backup / Restore Evidence

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-18
status: partial_implementation_available

## Result

- official_checkpointer_backup_restore: proven
- official_checkpointer_pg_dump: passed
- official_checkpointer_pg_restore: passed
- official_checkpoint_schema_restored: passed
- official_postgres_saver_read_restored_checkpoint: passed
- official_postgres_saver_restored_generation: passed
- official_checkpoint_writes_restored: passed
- checkpoint_receipt_not_domain_success: preserved
- phase_completion: blocked_cross_domain_replay_and_approval

## Commands

```powershell
python tools/scripts/verify_phase04_official_checkpointer_backup_restore.py
pytest -q tests/repo/test_phase04_official_checkpointer_backup_restore.py -p no:cacheprovider
```

Result:

```text
PHASE04 official Checkpointer backup/restore verification passed.
1 passed
```

## Boundary

本证据证明官方 `langgraph.checkpoint.postgres.PostgresSaver` 的 `checkpoint_*` schema 能随真实 PostgreSQL `pg_dump -Fc` 进入备份，并在临时恢复库中通过 `pg_restore` 后继续被官方 `PostgresSaver` 读取。恢复验证覆盖两代 checkpoint、latest generation、list count 和 writes row；简单 checkpoint 不一定产生 `checkpoint_blobs` row，但 `checkpoint_blobs` 表必须随官方 schema 恢复。

本证据不证明 schema upgrade recovery，也不把 checkpoint receipt 解释为领域成功。Graph-level interrupt/resume、retention cleanup、combined-service fault 和 Product Projection Replay 已由独立证据证明；PHASE04 仍受跨领域 replay、P04-T07 readiness、Coordinator approval 和 PHASE05 ready gate 阻止。
