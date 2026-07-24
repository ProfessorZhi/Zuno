# PHASE08 Pre-Closure Evidence

phase_id: PHASE08
date: 2026-07-24
status: completion_candidate
gate: pre_closure
coordinator_review_required: true
branch: integration/goal02-final-closure-repair

## 结论

本 PHASE08 Pre-Closure 在当前 Goal02 final closure repair 中整理为 `completion_candidate`。已有代码、迁移、测试和 evidence 覆盖真实 PostgreSQL Domain Commit、官方 PostgreSQL Checkpointer、Final Gate / RunOutcome 持久化、Owner Port ledger、cutover audit 和 focused fault 线索，但 PHASE08 仍必须等待 Coordinator Closure；本文件不把 PHASE08 标记为 completed。

## 覆盖

- P08-T01：`GoalVersion`、`TaskContract`、`AgentRun`、领域事件、PostgreSQL 约束和乐观版本冲突。
- P08-T01 replay ledger：`GoalVersion`、`TaskContract`、`AgentRun` 重启重放同 payload 返回 duplicate；同 sequence、idempotency key 或 task_contract 绑定的不同 payload fail closed 为 `AgentDomainConflict`，不再暴露原始数据库唯一约束异常。
- P08-T02：不可变 `PlanVersion`、单步 `DeterministicStepDefinition`、语义哈希、激活一次、PostgreSQL 约束。
- PlanVersion ledger：同一 `PlanVersion` / `StepDefinition` replay 返回 duplicate；同一 Goal 下相同 plan hash 的重放复用原 plan；同一 plan id 不同 payload fail closed，不再暴露原始数据库唯一约束异常。
- P08-T03：不可变 `ExecutionContextSnapshot`、预算预留和结算 ledger、stale epoch、deadline 和预算不足。
- Budget ledger replay：`BudgetReservation` 同 payload 重放返回 duplicate、不同 payload fail closed；`BudgetSettlement` 在提交后响应丢失场景中同 payload 重放返回 duplicate，错误 expected version 和不同 settlement payload 仍 fail closed。
- ExecutionContextSnapshot ledger：同一 `execution_snapshot_id` 和相同上下文 hash 的 restart replay 返回 duplicate；同一 snapshot id 的不同 policy/context payload fail closed，不让数据库唯一约束变成未分类异常。
- P08-T04 到 P08-T07：固定 `initialize -> authorize -> context_snapshot -> create_plan -> validate_plan -> activate_plan -> execute_step -> final_gate -> finalize -> run_outcome` LangGraph 运行图、固定 StepExecutionGraph、generation reconciliation、interrupt/signal/cancel/deadline。
- P08-T08：shadow / canary / new default / rollback 控制器，保证同 request hash、new runtime unavailable rollback 和 shadow 不双写 side effect。
- Reconciliation policy：`aligned`、`domain_ahead`、`checkpoint_ahead`、`orphan_checkpoint`、`orphan_domain`、`stale_schema`、`stale_controller_epoch`、`unrecoverable_conflict` 均有机器验证的 owner / auto repair / replay / terminate / audit / idempotency 决策；PostgreSQL reconciliation finding replay 相同 payload 返回 duplicate，不同策略或 payload fail closed。
- Signal ledger：PostgreSQL `agent_runtime_signals` replay 通过 `signal_id` 或 payload 唯一约束返回 duplicate；同 `signal_id` 不同 payload fail closed，且不让当前事务进入 aborted 状态。
- Cancel semantics：非 interrupt cancel 通过 `Phase08SignalRecord` 进入合法 `run_outcome` 终态并写回 checkpointer；已 terminal 的晚到 cancel 返回 `terminal:no_active_run`，不改写既有 RunOutcome。
- Finalization ledger：Final Gate / RunOutcome replay 相同 payload 返回 duplicate；同一 run 的不同 Final Gate 决策或不同 RunOutcome publication fail closed。
- Production run service：`phase08_postgres_run_service()` 在一个明确生产构造入口中绑定官方 `PostgresSaver` 与 `PostgresPhase08FinalGatePort`，避免产品接线绕过 Final Gate / RunOutcome 领域持久化。
- Product cutover entry：`WorkspaceTaskRuntimeService.configure_phase08_cutover()` 让 Workspace task 入口显式进入 `Phase08CutoverController`，默认不启用；启用后可按 `shadow`、`canary`、`new_default`、`rollback` 记录 `phase08_cutover` 审计事件。
- Product cutover configuration gate：`shadow`、`canary` 和 `new_default` 配置期必须显式绑定 PHASE08 new runtime；只有 `rollback` 允许不绑定 new runtime，避免非 rollback 模式到请求期才失败。
- Product cutover ledger lifecycle：Workspace cutover 启用但未显式传入 ledger 时，默认 `SideEffectLedger` 绑定到配置生命周期，不在每次任务执行时重建，避免同一配置窗口内丢失 effect claim / fallback guard。
- Shadow suppression：shadow 路径允许官方 Checkpointer 记录可恢复执行痕迹，但禁止 PHASE08 Final Gate、RunOutcome 和 Effect Claim 写入领域表，避免 shadow 产生产品效果、usage settlement 或完成事实。
- Shadow unavailable guard：shadow 路径的新 runtime dry-run 不可用时，产品入口保留已成功的 legacy primary 响应，记录 `shadow_unavailable:*` cutover audit，不触发 PHASE08 effect claim，也不重复 legacy side effect。
- Fallback guard：若同一请求已有 PHASE08 `agent_effect_claims` 持久记录，后续新 runtime 不可用时自动 legacy fallback 会 fail closed，并记录 `fallback_allowed=false` 的 cutover audit，防止已提交 effect 后重复执行 legacy side effect。

## 已运行命令

```powershell
pytest -q tests/agent/test_phase08_task_contract_domain.py tests/agent/test_phase08_plan_version_domain.py tests/agent/test_phase08_execution_context_budget_domain.py tests/agent/runtime/test_phase08_fixed_run_graph.py tests/agent/runtime/test_phase08_step_graph.py tests/agent/runtime/test_phase08_reconciliation_and_signals.py tests/agent/runtime/test_phase08_cutover_shadow.py tests/integration/agent/test_phase08_task_contract_persistence.py tests/integration/agent/test_phase08_plan_version_persistence.py tests/integration/agent/test_phase08_execution_context_budget_persistence.py -p no:cacheprovider --tb=short
```

结果：

```text
34 passed in 43.94s
```

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_current_program.py
python tools/scripts/verify_agent_core_target_protocols.py
alembic -c infra/db/alembic.ini heads
alembic -c infra/db/alembic.ini upgrade head
```

结果：

```text
agent system verification passed.
Current program verification passed.
refined Agent Core target architecture verification passed.
20260724_34 (head)
```

2026-07-24 追加验证：

```powershell
python -m py_compile src/backend/zuno/agent/runtime/phase08.py src/backend/zuno/agent/runtime/__init__.py tests/integration/agent/test_phase08_runtime_closure_persistence.py
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_production_run_service_uses_postgres_checkpointer_and_final_gate_port -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py -p no:cacheprovider --tb=short
pytest -q tests/agent/runtime/test_phase08_fixed_run_graph.py tests/agent/runtime/test_phase08_step_graph.py -p no:cacheprovider --tb=short
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_canaries_phase08_cutover_from_product_entry -p no:cacheprovider --tb=short
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_runs_read_only_tool_and_streams_audit_events tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_requires_tool_approval_then_executes_brokered_tool tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_emits_security_approval_facts_from_active_tool_path -p no:cacheprovider --tb=short
pytest -q tests/agent/runtime/test_phase08_cutover_shadow.py -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_shadow_product_cutover_suppresses_phase08_domain_commits -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py -p no:cacheprovider --tb=short
pytest -q tests/agent/runtime/test_phase08_cutover_shadow.py tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_canaries_phase08_cutover_from_product_entry -p no:cacheprovider --tb=short
pytest -q tests/agent/runtime/test_phase08_cutover_shadow.py::test_fallback_is_blocked_after_phase08_side_effect_claim -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_cutover_blocks_legacy_fallback_after_persistent_effect_claim -p no:cacheprovider --tb=short
pytest -q tests/agent/runtime/test_phase08_reconciliation_and_signals.py::test_generation_reconciliation_detects_ahead_behind_orphan_and_stale_schema -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_signal_reconciliation_and_cutover_are_persistent -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_runtime_closure_ledgers_are_persistent_and_idempotent -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_execution_context_budget_persistence.py::test_execution_snapshot_and_budget_ledger_round_trip -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_execution_context_budget_persistence.py -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_plan_version_persistence.py::test_plan_version_persistence_records_single_step_and_activation tests/integration/agent/test_phase08_plan_version_persistence.py::test_plan_version_duplicate_hash_replays_and_conflicts_per_goal -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_task_contract_persistence.py -p no:cacheprovider --tb=short
pytest -q tests/agent/runtime/test_phase08_cutover_shadow.py::test_shadow_mode_keeps_legacy_primary_when_new_runtime_is_unavailable tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_shadow_cutover_does_not_fail_product_when_new_runtime_unavailable -p no:cacheprovider --tb=short
pytest -q tests/agent/runtime/test_phase08_fixed_run_graph.py::test_run_graph_handles_interrupt_resume_cancel_and_deadline tests/agent/runtime/test_phase08_fixed_run_graph.py::test_cancel_after_terminal_run_returns_terminal_without_rewriting_outcome tests/integration/agent/test_phase08_official_postgres_runtime_recovery.py::test_phase08_run_graph_cancels_interrupted_postgres_checkpoint_after_restart -p no:cacheprovider --tb=short
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_canaries_phase08_cutover_from_product_entry -p no:cacheprovider --tb=short
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_cutover_requires_new_runtime_outside_rollback tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_shadow_cutover_does_not_fail_product_when_new_runtime_unavailable -p no:cacheprovider --tb=short
```

结果：

```text
py_compile passed
1 passed in 43.03s
5 passed in 39.04s
7 passed in 28.71s
1 passed, 1 warning in 45.75s
3 passed, 1 warning in 47.76s
5 passed in 31.74s
1 passed in 31.80s
6 passed in 36.75s
6 passed, 1 warning in 43.23s
1 passed in 34.34s
1 passed in 41.26s
1 passed in 36.10s
1 passed in 37.48s
1 passed in 35.45s
1 passed in 8.16s
2 passed in 14.25s
2 passed in 9.80s
4 passed in 10.77s
2 passed, 1 warning in 53.63s
3 passed in 31.28s
1 passed, 1 warning in 25.32s
2 passed, 1 warning in 20.90s
```

当前 schema head 复核：

```text
20260724_34 (head)
```

## 证据 Commit

- P08-T01：`bf54f3479dff58638fc73fe14a1a761703293491`
- P08-T02：`4dd1668cd1b498aa15439e86b6522851c9bd788d`
- P08-T03：`a351cd588150cc8804012aa811004e30b3881cab`
- P08-T04～T07：`2143f9ba1240567b060312c1a730014d2f0f6b25`
- P08-T08：`42425de6efa957e378283effa5e8cb6b4189dcdf`

## 边界

PHASE08 当前为 completed，不表示完整产品默认路径、Web/Desktop、PHASE09、PHASE10、PHASE12、质量评测或 production readiness 已完成。PHASE09 与 PHASE12 当前为 ready。
