from __future__ import annotations

import os
import subprocess
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.agent.domain import (
    AgentDomainConflict,
    AgentRun,
    BudgetReservation,
    BudgetReservationStatus,
    ExecutionContextSnapshot,
    GoalInputClassification,
    GoalVersion,
    TaskContract,
)
from zuno.platform.database.agent import AgentDomainUnitOfWork
from zuno.platform.database.foundation import create_foundation_engine


REPO_ROOT = Path(__file__).resolve().parents[3]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
HEX_64 = "a" * 64


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    env = {
        **os.environ,
        "PGCONNECT_TIMEOUT": os.environ.get("PGCONNECT_TIMEOUT", "5"),
        "ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS": os.environ.get("ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS", "5"),
    }
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    agent_cutover_audit_events,
                    agent_reconciliation_findings,
                    agent_runtime_signals,
                    agent_run_outcomes,
                    agent_final_gate_receipts,
                    agent_effect_claims,
                    agent_step_acceptances,
                    agent_observations,
                    agent_action_runs,
                    agent_request_idempotency_keys,
                    agent_execution_context_snapshots,
                    agent_budget_settlements,
                    agent_budget_reservations,
                    agent_plan_step_definitions,
                    agent_plan_versions,
                    agent_domain_events,
                    agent_domain_runs,
                    agent_task_contracts,
                    agent_goal_versions
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def _now() -> datetime:
    return datetime(2026, 7, 23, 23, 0, tzinfo=timezone.utc)


def _goal() -> GoalVersion:
    return GoalVersion(
        goal_version_id="goal:p08:t03:pg:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="principal-a",
        goal_sequence=1,
        input_classification=GoalInputClassification.OBJECTIVE_CHANGE,
        objective_hash=HEX_64,
        output_contract_ref="output:answer",
        constraints_hash="b" * 64,
    )


def _task(goal: GoalVersion) -> TaskContract:
    return TaskContract(
        task_contract_id="task-contract:p08:t03:pg:1",
        tenant_id=goal.tenant_id,
        workspace_id=goal.workspace_id,
        principal_id=goal.principal_id,
        goal_version_id=goal.goal_version_id,
        idempotency_key="idem:p08:t03:pg:1",
        security_context_ref="security-context:p08:t03:pg",
        security_epoch_ref="security-epoch:p08:t03:pg",
        deadline_at=datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc),
        budget_ref="budget:p08:t03:pg",
    )


def _run(task: TaskContract) -> AgentRun:
    return AgentRun(
        run_id="run:p08:t03:pg:1",
        tenant_id=task.tenant_id,
        workspace_id=task.workspace_id,
        principal_id=task.principal_id,
        task_contract_id=task.task_contract_id,
        trace_id="trace:p08:t03:pg:1",
    )


def _reservation(run: AgentRun) -> BudgetReservation:
    return BudgetReservation.reserve(
        budget_reservation_id="budget-reservation:p08:t03:pg:1",
        run_id=run.run_id,
        tenant_id=run.tenant_id,
        budget_ref="budget:p08:t03:pg",
        reservation_scope="RUN",
        requested_units=100,
        available_units=120,
    )


def _snapshot(task: TaskContract, run: AgentRun, reservation: BudgetReservation) -> ExecutionContextSnapshot:
    return ExecutionContextSnapshot(
        execution_snapshot_id="execution-snapshot:p08:t03:pg:1",
        run_id=run.run_id,
        tenant_id=run.tenant_id,
        workspace_id=run.workspace_id,
        principal_id=run.principal_id,
        task_contract_id=task.task_contract_id,
        security_context_ref=task.security_context_ref,
        security_epoch_ref=task.security_epoch_ref,
        model_policy_ref="model-policy:p08:t03:pg",
        capability_profile_ref="capability-profile:p08:t03:pg",
        knowledge_snapshot_ref="knowledge-snapshot:p08:t03:pg",
        answer_policy_ref="answer-policy:p08:t03:pg",
        budget_reservation_id=reservation.budget_reservation_id,
        deadline_at=task.deadline_at,
    )


def test_execution_snapshot_and_budget_ledger_round_trip(engine) -> None:
    goal = _goal()
    task = _task(goal)
    run = _run(task)
    reservation = _reservation(run)
    snapshot = _snapshot(task, run, reservation)

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)
        repo.record_budget_reservation(reservation)
        recorded_snapshot = repo.record_execution_context_snapshot(snapshot)
        duplicate_snapshot = repo.record_execution_context_snapshot(snapshot)
        with pytest.raises(AgentDomainConflict, match="conflicting execution context snapshot"):
            repo.record_execution_context_snapshot(
                replace(snapshot, model_policy_ref="model-policy:p08:t03:pg:conflict", context_hash="")
            )
        loaded_snapshot = repo.load_execution_context_snapshot(snapshot.execution_snapshot_id)
        loaded_reservation = repo.load_budget_reservation(reservation.budget_reservation_id)

    assert recorded_snapshot.status == "RECORDED"
    assert duplicate_snapshot.status == "duplicate:RECORDED"
    assert loaded_snapshot.context_hash == snapshot.context_hash
    assert loaded_snapshot.resume_refs() == snapshot.resume_refs()
    assert loaded_reservation.status is BudgetReservationStatus.RESERVED


def test_budget_settlement_is_atomic_and_stale_settlement_conflicts(engine) -> None:
    goal = _goal()
    task = _task(goal)
    run = _run(task)
    reservation = _reservation(run)

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)
        repo.record_budget_reservation(reservation)
        settled, settlement = repo.load_budget_reservation(reservation.budget_reservation_id).settle(
            expected_version=1,
            consumed_units=64,
            reason_ref="reason:p08:t03:pg",
        )
        repo.settle_budget_reservation(settled, settlement, expected_version=1)

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT r.status, r.aggregate_version, s.consumed_units, s.released_units
                FROM agent_budget_reservations r
                JOIN agent_budget_settlements s USING (budget_reservation_id)
                """
            )
        ).one()

    assert row.status == BudgetReservationStatus.SETTLED.value
    assert row.aggregate_version == 2
    assert row.consumed_units == 64
    assert row.released_units == 36

    with pytest.raises(AgentDomainConflict, match="expected aggregate_version"):
        with AgentDomainUnitOfWork(engine) as repo:
            repo.settle_budget_reservation(settled, settlement, expected_version=1)
