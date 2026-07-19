# PHASE04 Official Checkpointer Retention / Prune Evidence

phase_id: PHASE04
task_id: P04-T06
date: 2026-07-18
status: implementation_available_for_official_checkpointer_retention_subscope

## Result

- official_checkpointer_retention: proven
- official_delete_thread_retention_cleanup: passed
- official_active_thread_preserved_after_retention: passed
- official_partial_prune_fail_closed: passed
- official_run_delete_fail_closed: passed
- official_retention_restart_restore: passed
- checkpoint_receipt_not_domain_success: preserved
- phase_completion: blocked_cross_domain_replay_and_approval

## Commands

```powershell
python tools/scripts/verify_phase04_official_checkpointer_retention.py
pytest -q tests/repo/test_phase04_official_checkpointer_retention.py -p no:cacheprovider
```

Result:

```text
PHASE04 official Checkpointer retention verification passed.
1 passed
```

## Boundary

本证据证明当前官方 `langgraph.checkpoint.postgres.PostgresSaver` 在真实 PostgreSQL 上支持整 thread retention cleanup：verifier 创建 active 与 expired 两个官方 checkpoint thread，写入 checkpoints 与 checkpoint_writes，通过官方 `delete_thread()` 删除 expired thread，并证明 active thread 的 checkpoint rows、writes、history 和 restart restore 不受影响。

当前 `langgraph-checkpoint-postgres==3.1.0` 的同步 `prune()` 和 `delete_for_runs()` 会抛出 `NotImplementedError`。本证据把 partial prune 与 run-scoped delete 固定为 fail-closed，不把它们冒充为 Current，也不允许在缺少官方实现时删除仍可能被 DeltaChannel 重建依赖的 ancestor checkpoints 或 writes。

本证据不关闭 PHASE04。official Checkpointer combined-service fault 已由独立证据证明；剩余缺口是跨领域 replay、P04-T07 readiness、Coordinator approval 和 PHASE05 ready gate。
