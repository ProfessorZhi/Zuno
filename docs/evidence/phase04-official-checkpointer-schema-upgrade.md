# PHASE04 Official Checkpointer Schema Upgrade Evidence

phase_id: PHASE04
task_id: P04-T06
date: 2026-07-18
status: implementation_available_for_official_checkpointer_schema_upgrade_subscope

## Result

- official_checkpointer_schema_upgrade: proven
- official_old_schema_v8_created: passed
- official_setup_migrated_to_v9: passed
- official_pre_upgrade_checkpoint_recovered: passed
- official_v9_task_path_write: passed
- official_setup_idempotent_after_upgrade: passed
- official_interrupt_resume_after_schema_upgrade: passed
- official_checkpoint_history_retained_after_schema_upgrade: passed
- official_generation_non_regression_after_schema_upgrade: passed
- official_schema_upgrade_failure_fail_closed: passed
- checkpoint_receipt_not_domain_success: preserved
- phase_completion: blocked_cross_domain_replay_and_approval

## Commands

```powershell
python tools/scripts/verify_phase04_official_checkpointer_schema_upgrade.py
pytest -q tests/repo/test_phase04_official_checkpointer_schema_upgrade.py -p no:cacheprovider
```

Result:

```text
PHASE04 official Checkpointer schema upgrade verification passed.
1 passed
```

## Boundary

本证据证明官方 `langgraph.checkpoint.postgres.PostgresSaver.setup()` 可在真实 PostgreSQL 临时库中把旧官方 schema 从 migration v8 升级到当前 v9，并保留升级前 checkpoint 可读。演练先应用官方 migration v0 到 v8，确认 `checkpoint_writes.task_path` 尚不存在，再写入旧 checkpoint；随后用当前官方 `PostgresSaver.setup()` 执行升级，确认 `checkpoint_migrations` 到 v9、`task_path` 列存在、旧 checkpoint 可通过官方 saver 读取，并且新 v9 `put_writes(..., task_path=...)` 可持久化。

升级后同一临时库使用官方 `StateGraph` + `PostgresSaver` 执行 interrupt/resume：interrupt 节点持久化，重启 saver 后用 `Command(resume=...)` 恢复，history 保留 interrupted node 和 resumed final node。负例使用损坏的旧 schema 验证 `setup()` / read path 抛错并 fail closed，不降级到自定义表或伪造成功。升级前 checkpoint generation 保持不回退。

该证据只证明 official Checkpointer schema upgrade/recovery 子范围。Checkpoint receipt 仍不等于领域成功；PHASE04 仍需 Coordinator Closure 才能 completed。
