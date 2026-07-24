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
- Alembic head：`20260724_29`
- Fixed runtime surface：`src/backend/zuno/agent/runtime/phase08.py`
- Shadow / canary / rollback：`src/backend/zuno/agent/runtime/phase08_cutover.py`
- Production service factory：`phase08_postgres_run_service()` binds official `PostgresSaver` and `PostgresPhase08FinalGatePort`.
- Product entry cutover：`WorkspaceTaskRuntimeService.configure_phase08_cutover()` routes Workspace task creation through `Phase08CutoverController` when explicitly configured.
- Focused tests：`tests/agent/test_phase08_*.py`、`tests/integration/agent/test_phase08_*.py`、`tests/agent/runtime/test_phase08_*.py`

## 边界

PHASE08 不拥有 Product Surface、Web/Desktop、Knowledge Version、Tool Side Effect、Benchmark Release Gate 或完整 production operations。旧 `GeneralAgent` 主路径仍只作为后续 PHASE09/PHASE22 的迁移和移除对象；本 Closure 不批准永久双 runtime。

## 验证命令

```powershell
pytest -q tests/agent/runtime/test_phase08_fixed_run_graph.py tests/agent/runtime/test_phase08_step_graph.py tests/integration/agent/test_phase08_official_postgres_runtime_recovery.py -p no:cacheprovider --tb=short
pytest -q tests/integration/agent/test_phase08_runtime_closure_persistence.py -p no:cacheprovider --tb=short
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_canaries_phase08_cutover_from_product_entry -p no:cacheprovider --tb=short
```

结果：`6 passed`；追加 persistence closure：`5 passed in 39.04s`；Workspace product canary：`1 passed, 1 warning in 45.75s`。

## 下游影响

PHASE08 重新关闭前，PHASE09 保持 `planned`，PHASE12 的 PHASE08 依赖未满足。PHASE09、PHASE12 仍未在本轮实现；Production readiness is not established.
