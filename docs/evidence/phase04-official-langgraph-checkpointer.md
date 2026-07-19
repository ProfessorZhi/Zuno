# PHASE04 Official LangGraph PostgreSQL Checkpointer Evidence

phase_id: PHASE04
task_id: P04-T06
date: 2026-07-18
status: implementation_available_for_official_checkpointer_lifecycle_subscope

## Result

- coordinator_dependency_decision: approved
- official_package_importable: passed
- langgraph_postgres_checkpointer: proven
- official_postgres_saver_setup: passed
- official_checkpoint_put_get_after_restart: passed
- official_multi_generation_restore: passed
- official_thread_isolation: passed
- official_checkpoint_writes_smoke: passed
- official_delete_thread_cleanup: passed
- official_delta_channel_history: passed
- official_graph_interrupt: passed
- official_graph_resume_after_restart: passed
- official_graph_checkpoint_history: passed
- official_checkpoint_infra_generation_reconcile: passed
- stale_checkpoint_generation_rejected: passed
- official_copy_thread_prune: not_implemented_in_current_package
- checkpoint_receipt_not_domain_success: preserved
- phase_completion: blocked_cross_domain_replay_and_approval

## Commands

```powershell
python tools/scripts/verify_phase04_official_langgraph_checkpointer.py
pytest -q tests/repo/test_phase04_official_langgraph_checkpointer.py -p no:cacheprovider
```

Result:

```text
PHASE04 official LangGraph PostgreSQL Checkpointer verification passed.
1 passed
```

## Boundary

本证据证明官方 `langgraph.checkpoint.postgres.PostgresSaver` 已安装并可在真实 PostgreSQL 上执行 `setup()`、多代 `put()`、restart 后 `get_tuple()`、`list()` thread isolation、`put_writes()`、`get_delta_channel_history()` 和 `delete_thread()` cleanup。Verifier 还编译真实 `StateGraph`，第一次 invoke 触发 `interrupt()`，关闭 saver 后重新打开官方 `PostgresSaver`，再用 `Command(resume="approved")` 从同一 `thread_id` 恢复并完成 graph；`get_state_history()` 保留 interrupted approval node 和 resumed final node。Verifier 同时将官方 checkpoint id 写入 Zuno `infra_checkpoints` receipt 并验证同一 generation 的晚到写入被拒绝，从而证明 Checkpoint receipt 与 Infrastructure generation 可以对账，但仍不等于领域成功。

`PostgresSaver.setup()` 创建的 `checkpoint_migrations`、`checkpoints`、`checkpoint_blobs` 和 `checkpoint_writes` 是官方 Checkpointer schema，不是 Zuno 领域事实表。当前 `langgraph-checkpoint-postgres==3.1.0` 的同步 `copy_thread()`、partial `prune()` 和 run-scoped `delete_for_runs()` 方法抛出 `NotImplementedError`；整 thread retention cleanup 已由 `docs/evidence/phase04-official-checkpointer-retention.md` 通过官方 `delete_thread()` 单独证明。

这不证明 PHASE04 completed。official Checkpointer retention、backup/restore、schema upgrade recovery 和 combined-service fault 已由独立证据补齐；跨领域 replay、P04-T07 readiness、Coordinator approval 和 PHASE05 ready gate 仍需最终收口。
