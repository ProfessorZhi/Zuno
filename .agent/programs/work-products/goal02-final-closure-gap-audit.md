# Goal02 Final Closure 局部 Gap Audit

date: 2026-07-23
branch: integration/goal02-final-closure-repair
start_sha: 48a67be04e67bbe3a1bced06c51f59391383bc1b
scope: PHASE08 durable Single Controller; PHASE11 Human Review Resume; PHASE11 Delete/Restore/Reconciliation
status: frozen

## 读取事实源

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/programs/program-manifest.yaml`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/task-execution-contract.md`
- `.agent/programs/PHASE08_deterministic-single-controller-runtime.md`
- `.agent/programs/PHASE11_durable-ingestion-and-source-lineage.md`
- `.agent/programs/work-products/requirement-ledger.yaml`
- `.agent/programs/work-products/phase11-readiness.yaml`
- `docs/modules/02-input-document-ingestion.md`
- `docs/modules/06-agent-core-planning-control.md`
- `docs/modules/09-security.md`
- `docs/modules/10-observability-eval.md`
- `docs/modules/11-infrastructure.md`
- `docs/governance/wave1-cross-module-contract-registry.md`
- `docs/status/production-readiness.md`
- `src/backend/zuno/agent/runtime/phase08.py`
- `src/backend/zuno/platform/database/agent/domain.py`
- `src/backend/zuno/platform/database/ingestion/persistence.py`
- PHASE08 / PHASE11 focused tests and closure verifiers.

## Startup Evidence

- main start SHA: `48a67be04e67bbe3a1bced06c51f59391383bc1b`
- Alembic head: `20260724_25 (head)`
- worktree before branch creation: clean
- target branch created from latest `origin/main`: `integration/goal02-final-closure-repair`

## Frozen Gap List

### A. PHASE08 持久 Single Controller

Current:
- Official LangGraph `PostgresSaver` is used by `phase08_postgres_checkpointer`.
- `build_phase08_run_graph` and `build_phase08_step_graph` reject implicit checkpointers.
- Native interrupt / `Command(resume=...)` recovery is covered by `tests/integration/agent/test_phase08_official_postgres_runtime_recovery.py`.
- Agent domain PostgreSQL tables and repository cover TaskContract, GoalVersion, AgentRun, PlanVersion, StepDefinition, ExecutionContextSnapshot, BudgetReservation and BudgetSettlement.

Gap:
- The fixed graph node names in `src/backend/zuno/agent/runtime/phase08.py` did not exactly match the Goal02 final closure contract. Checkpoint/history nodes used `context`, `plan`, `activate`, `execute`, `evaluation`, and `acceptance` instead of the required `context_snapshot`, `create_plan`, `validate_plan`, `activate_plan`, `execute_step`, `action_evaluation`, and `step_acceptance`.
- Program and coordinator closure surfaces still marked PHASE08 as superseded/in_progress.

Frozen action:
- Align graph node names and focused tests to the final closure contract.
- Re-run PHASE08 focused unit/integration tests.
- After evidence is verified, update PHASE08 closure surfaces to `completed` / `coordinator_approval: approved`.

### B. PHASE11 Human Review Resume

Current:
- PostgreSQL review audit migration exists: `20260724_24_ingestion_review_audit.py`.
- Review task, decision receipt, and restart duplicate-resume evidence exists in `tests/integration/test_phase11_ingestion_persistence_runtime.py`.
- `HumanReviewRuntime` keeps approved/rejected/expired/cancelled publish semantics separate.

Gap:
- Program, readiness, production-readiness, and coordinator closure surfaces still mark PHASE11 as superseded/in_progress, so closure gates fail despite implementation evidence.

Frozen action:
- Re-run PHASE11 review focused tests.
- Update PHASE11 readiness and closure surfaces only after tests pass.

### C. PHASE11 Delete / Restore / Reconciliation

Current:
- Delete lifecycle migration exists: `20260724_25_ingestion_delete_lifecycle.py`.
- PostgreSQL `record_delete_lifecycle` and `reconcile_delete_lifecycle` persist state transitions.
- Delete/restore/reconcile focused evidence exists in `tests/integration/test_phase11_ingestion_persistence_runtime.py` and `tests/knowledge/test_ingestion_delete_restore.py`.

Gap:
- Same status-surface closure gap as PHASE11 review: Coordinator approval and readiness files are still reopened.

Frozen action:
- Re-run delete/restore/reconcile focused tests.
- Update PHASE11 closure surfaces to completed only if focused validation and post-closure gate pass.

## Out Of Scope

- PHASE09, PHASE10, PHASE12, PHASE13+ implementation.
- Dynamic DAG, parallel Plan, Replan implementation.
- New global audit or unrelated verifier expansion.
- Direct main push or PR merge.
