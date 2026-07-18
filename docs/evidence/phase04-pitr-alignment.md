# PHASE04 PITR Alignment Evidence

## Scope

本证据覆盖 `ARCH-INFRA-029`：PITR 对齐 DB / Object / Checkpoint / Index。

它证明 PostgreSQL WAL archive + base backup + point-in-time recovery 可以恢复到一个已验证 RecoverySet，并且 target time 之后写入的 derived index watermark 不会混入恢复结果。

它不证明 graph-level Checkpointer interrupt/resume、retention/prune、跨领域 Projection Replay、combined-service fault 或 PHASE04 closure。

## Environment

- Docker image：`postgres:16`
- Drill topology：临时 primary container + 临时 recovery container
- Primary config：`wal_level=replica`、`archive_mode=on`、`archive_timeout=1s`、`archive_command=cp %p /var/lib/postgresql/wal_archive/%f`
- Schema：Alembic upgrade to current head
- Recovery primitive：`infra_recovery_watermarks` / `infra_recovery_sets` / `infra_recovery_set_members`
- Cleanup：verifier 结束后删除临时 containers 和临时 backup/archive 目录

## Command

```powershell
python tools/scripts/verify_phase04_pitr_alignment.py
```

## Result

- pitr_primary_archive_mode: passed
- alembic_head_on_pitr_primary: passed
- pg_basebackup_taken: passed
- recovery_set_before_target_time: passed
- post_target_derived_index_ahead_write: passed
- wal_archive_switch: passed
- recovery_container_to_target_time: passed
- recovery_target_promoted: passed
- restored_recovery_set_verified: passed
- restored_authoritative_and_derived_watermarks_aligned: passed
- post_target_derived_index_watermark_excluded: passed
- phase_completion: blocked_cross_domain_replay_and_approval

## Boundary

`ARCH-INFRA-029` 当前达到 `implementation_available`：PITR drill 使用真实 PostgreSQL WAL archive/basebackup/recovery，并把 DB/Object/Checkpoint/Index 的恢复点通过 RecoverySet 对齐。

该证据仍不能关闭 PHASE04，因为跨领域 Projection Replay、P04-T06/P04-T07 readiness 状态和 Coordinator approval gate 仍未完成。
