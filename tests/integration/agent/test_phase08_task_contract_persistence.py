from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import exc, text

from zuno.agent.domain import (
    AgentDomainConflict,
    AgentRun,
    AgentRunStatus,
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
HEX_64 = "c" * 64


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
    return datetime(2026, 7, 23, 21, 0, tzinfo=timezone.utc)


def _goal(goal_version_id: str = "goal:p08:t01:pg:1") -> GoalVersion:
    return GoalVersion(
        goal_version_id=goal_version_id,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="principal-a",
        goal_sequence=1,
        input_classification=GoalInputClassification.OBJECTIVE_CHANGE,
        objective_hash=HEX_64,
        output_contract_ref="output:answer",
        constraints_hash="d" * 64,
    )


def _task(goal: GoalVersion, task_contract_id: str = "task-contract:p08:t01:pg:1") -> TaskContract:
    return TaskContract(
        task_contract_id=task_contract_id,
        tenant_id=goal.tenant_id,
        workspace_id=goal.workspace_id,
        principal_id=goal.principal_id,
        goal_version_id=goal.goal_version_id,
        idempotency_key="idem:p08:t01:pg:1",
        security_context_ref="security-context:p08:t01:pg",
        security_epoch_ref="security-epoch:p08:t01:pg",
        deadline_at=_now(),
        budget_ref="budget:p08:t01:pg",
    )


def _run(task: TaskContract, run_id: str = "run:p08:t01:pg:1") -> AgentRun:
    return AgentRun(
        run_id=run_id,
        tenant_id=task.tenant_id,
        workspace_id=task.workspace_id,
        principal_id=task.principal_id,
        task_contract_id=task.task_contract_id,
        trace_id="trace:p08:t01:pg:1",
    )


def test_agent_domain_uow_persists_task_contract_goal_and_run_lifecycle(engine) -> None:
    goal = _goal()
    task = _task(goal)
    run = _run(task)

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)
        authorized = repo.load_run(run.run_id).authorize(expected_version=1)
        repo.transition_run(authorized, expected_version=1)
        started = repo.load_run(run.run_id).start(expected_version=2, started_at=_now())
        repo.transition_run(started, expected_version=2)
        completed = repo.load_run(run.run_id).complete(expected_version=3, ended_at=_now())
        repo.transition_run(completed, expected_version=3)

    with engine.connect() as conn:
        row = conn.execute(text("SELECT status, aggregate_version, domain_generation FROM agent_domain_runs")).one()
        event_count = conn.execute(text("SELECT count(*) FROM agent_domain_events")).scalar_one()

    assert row.status == AgentRunStatus.COMPLETED.value
    assert row.aggregate_version == 4
    assert row.domain_generation == 4
    assert event_count == 4


def test_agent_task_contract_duplicate_request_is_tenant_workspace_scoped(engine) -> None:
    goal = _goal()
    task = _task(goal)

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        replayed = repo.find_task_contract_by_idempotency(
            tenant_id=task.tenant_id,
            workspace_id=task.workspace_id,
            idempotency_key=task.idempotency_key,
        )

    assert replayed is not None
    assert replayed.task_contract_id == task.task_contract_id

    with pytest.raises(exc.IntegrityError):
        with AgentDomainUnitOfWork(engine) as repo:
            repo.record_task_contract(_task(goal, task_contract_id="task-contract:p08:t01:duplicate"))


def test_agent_run_optimistic_conflict_blocks_stale_transition(engine) -> None:
    goal = _goal()
    task = _task(goal)
    run = _run(task)

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)
        authorized = repo.load_run(run.run_id).authorize(expected_version=1)
        repo.transition_run(authorized, expected_version=1)
        stale_started = authorized.start(expected_version=2, started_at=_now())
        repo.transition_run(stale_started, expected_version=2)

        with pytest.raises(AgentDomainConflict, match="expected aggregate_version"):
            repo.transition_run(stale_started.complete(expected_version=3, ended_at=_now()), expected_version=2)
