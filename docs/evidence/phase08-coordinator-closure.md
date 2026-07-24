# PHASE08 Coordinator Closure Decision

phase_id: PHASE08
date: 2026-07-24
status: reopened
coordinator_approval: pending
phase08_state: in_progress
production_ready: false

## Closure Decision

本 PHASE08 Coordinator Closure 在本轮 Goal02 final closure repair 中撤回到 `pending`。PR #41 初版 closure 将部分 PostgreSQL Checkpointer、Native Resume、Final Gate、durable step commit、Owner integration 和 cutover 证据写成 completed，但代码审查已证明真实 Owner Port、持久幂等、reconciliation、product cutover 和故障证据仍不足。

## 审查依据

- PHASE08 Pre-Closure：`docs/evidence/phase08-pre-closure.md`
- Domain facts：`src/backend/zuno/agent/domain/task_contracts.py`
- PostgreSQL repository：`src/backend/zuno/platform/database/agent/domain.py`
- Alembic head：`20260724_34`
- Fixed runtime surface：`src/backend/zuno/agent/runtime/phase08.py`
- Shadow / canary / rollback：`src/backend/zuno/agent/runtime/phase08_cutover.py`
- Production service factory：`phase08_postgres_run_service()` binds official `PostgresSaver` and `PostgresPhase08FinalGatePort`.
- Product entry cutover：`WorkspaceTaskRuntimeService.configure_phase08_cutover()` routes Workspace task creation through `Phase08CutoverController` when explicitly configured.
- Shadow suppression：PHASE08 shadow runs keep official checkpoint evidence but do not write `agent_final_gate_receipts`、`agent_run_outcomes` or `agent_effect_claims`.
- Reconciliation policy：all required statuses now carry explicit owner / auto repair / replay / terminate / audit / idempotency decisions, and PostgreSQL finding replay returns duplicate or conflict instead of raw database errors.
- Signal ledger：runtime signal replay now returns duplicate for matching `signal_id` or matching payload uniqueness, and conflicting same-id payloads fail closed without aborting the surrounding PostgreSQL transaction.
- Finalization ledger：Final Gate and RunOutcome replay returns duplicate for matching payloads, while conflicting final gate decisions or publication outcomes fail closed.
- Fallback guard：after a persisted PHASE08 `agent_effect_claims` row exists for the request idempotency key, automatic legacy fallback is blocked and audited with `fallback_allowed=false`.
- Focused tests：`tests/agent/test_phase08_*.py`、`tests/integration/agent/test_phase08_*.py`、`tests/agent/runtime/test_phase08_*.py`

## 边界

PHASE08 不拥有 Product Surface、Web/Desktop、Knowledge Version、Tool Side Effect、Benchmark Release Gate 或完整 production operations。旧 `GeneralAgent` 主路径仍只作为后续 PHASE09/PHASE22 的迁移和移除对象；本 Closure 不批准永久双 runtime。

## 验证命令

```powershell
pytest -q tests/agent/runtime/test_phase08_fixed_run_graph.py tests/agent/runtime/test_phase08_step_graph.py tests/integration/agent/test_phase08_official_postgres_runtime_recovery.py -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py -p no:cacheprovider --tb=short
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_canaries_phase08_cutover_from_product_entry -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_shadow_product_cutover_suppresses_phase08_domain_commits -p no:cacheprovider --tb=short
```

结果：`6 passed`；追加 persistence closure：`5 passed in 39.04s`；Workspace product canary：`1 passed, 1 warning in 45.75s`；shadow suppression：`1 passed in 31.80s`。

Fallback guard focused validation：`tests/agent/runtime/test_phase08_cutover_shadow.py::test_fallback_is_blocked_after_phase08_side_effect_claim` 为 `1 passed in 34.34s`；`tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_cutover_blocks_legacy_fallback_after_persistent_effect_claim` 为 `1 passed in 41.26s`。

Reconciliation and signal ledger focused validation：`tests/agent/runtime/test_phase08_reconciliation_and_signals.py::test_generation_reconciliation_detects_ahead_behind_orphan_and_stale_schema` 为 `1 passed in 36.10s`；`tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_signal_reconciliation_and_cutover_are_persistent` 为 `1 passed in 37.48s`。

Finalization ledger focused validation：`tests/integration/agent/test_phase08_runtime_closure_persistence.py::test_phase08_runtime_closure_ledgers_are_persistent_and_idempotent` 为 `1 passed in 35.45s`。

## 下游影响

PHASE08 重新关闭前，PHASE09 保持 `planned`，PHASE12 的 PHASE08 依赖未满足。PHASE09、PHASE12 仍未在本轮实现；Production readiness is not established.
