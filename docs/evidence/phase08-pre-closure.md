# PHASE08 Pre-Closure Evidence

phase_id: PHASE08
date: 2026-07-23
status: completed
gate: pre_closure
coordinator_review_required: true

## 结论

本 PHASE08 Pre-Closure 已由 Goal02 final closure repair 重新批准。已有代码、迁移、测试和 evidence，加上 final closure repair 的 graph contract / native recovery focused validation，构成当前 PHASE08 completed 证据。

## 覆盖

- P08-T01：`GoalVersion`、`TaskContract`、`AgentRun`、领域事件、PostgreSQL 约束和乐观版本冲突。
- P08-T02：不可变 `PlanVersion`、单步 `DeterministicStepDefinition`、语义哈希、激活一次、PostgreSQL 约束。
- P08-T03：不可变 `ExecutionContextSnapshot`、预算预留和结算 ledger、stale epoch、deadline 和预算不足。
- P08-T04 到 P08-T07：固定 `initialize -> authorize -> context_snapshot -> create_plan -> validate_plan -> activate_plan -> execute_step -> final_gate -> finalize -> run_outcome` LangGraph 运行图、固定 StepExecutionGraph、generation reconciliation、interrupt/signal/cancel/deadline。
- P08-T08：shadow / canary / new default / rollback 控制器，保证同 request hash、new runtime unavailable rollback 和 shadow 不双写 side effect。

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
20260724_25 (head)
```

## 证据 Commit

- P08-T01：`bf54f3479dff58638fc73fe14a1a761703293491`
- P08-T02：`4dd1668cd1b498aa15439e86b6522851c9bd788d`
- P08-T03：`a351cd588150cc8804012aa811004e30b3881cab`
- P08-T04～T07：`2143f9ba1240567b060312c1a730014d2f0f6b25`
- P08-T08：`42425de6efa957e378283effa5e8cb6b4189dcdf`

## 边界

PHASE08 completed 不表示完整产品默认路径、Web/Desktop、PHASE09、PHASE10、PHASE12、质量评测或 production readiness 已完成。PHASE09 仅为 ready；PHASE12 仅为 ready。
