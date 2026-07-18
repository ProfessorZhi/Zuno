# PHASE04 Recovery Watermark 证据

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-18
status: implementation_available_for_recovery_watermark_subscope

## Result

- recovery_watermark_schema: passed
- authoritative_watermarks_recorded: passed
- derived_watermarks_recorded: passed
- mismatched_derived_watermark_rejected: passed
- recovery_set_authoritative_and_derived_alignment: passed
- recovery_set_verification_hash: passed
- phase_completion: blocked_cross_domain_replay_and_approval

## Command

```powershell
python tools/scripts/verify_phase04_recovery_watermark.py
```

Result: passed.

```powershell
pytest -q tests/integration/test_phase04_recovery_watermark.py -p no:cacheprovider
```

Result: passed.

## Boundary

本证据证明 `ARCH-INFRA-022` 和 `ARCH-INFRA-052` 的当前 Infrastructure 子范围：PostgreSQL `infra_recovery_watermarks` / `infra_recovery_sets` / `infra_recovery_set_members` 提供权威组件和派生组件 watermark 记录、RecoverySet 对齐检查、mismatch fail-closed 和 verification hash。

本证据不单独证明 PITR、Product Projection Replay 或 official Checkpointer restore；这些由各自 verifier 证明。本证据不证明 graph-level Checkpointer interrupt/resume、retention/prune、combined-service fault 或完整 PHASE04 closure。
