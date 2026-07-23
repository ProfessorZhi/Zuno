from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import exc, text

from zuno.agent.domain import (
    AgentDomainConflict,
    DeterministicStepDefinition,
    GoalInputClassification,
    GoalVersion,
    PlanVersion,
    PlanVersionStatus,
    StepExecutorType,
)
from zuno.platform.database.agent import AgentDomainUnitOfWork
from zuno.platform.database.foundation import create_foundation_engine


REPO_ROOT = Path(__file__).resolve().parents[3]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
HEX_64 = "e" * 64


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
    return datetime(2026, 7, 23, 22, 0, tzinfo=timezone.utc)


def _goal() -> GoalVersion:
    return GoalVersion(
        goal_version_id="goal:p08:t02:pg:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="principal-a",
        goal_sequence=1,
        input_classification=GoalInputClassification.OBJECTIVE_CHANGE,
        objective_hash=HEX_64,
        output_contract_ref="output:answer",
        constraints_hash="f" * 64,
    )


def _plan() -> PlanVersion:
    step = DeterministicStepDefinition(
        step_definition_id="step-def:p08:t02:pg:1",
        plan_version_id="plan:p08:t02:pg:1",
        tenant_id="tenant-a",
        step_no=1,
        objective_ref="objective:primary",
        input_contract_ref="input:task-contract",
        output_contract_ref="output:answer",
        acceptance_refs=("acceptance:final-gate",),
        executor_type=StepExecutorType.MODEL,
        required_evidence_refs=("evidence:trace",),
        budget_ref="budget:p08:t02:pg",
        deadline_at=_now(),
    )
    return PlanVersion.create_single_step(
        plan_version_id="plan:p08:t02:pg:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        goal_version_id="goal:p08:t02:pg:1",
        step=step,
    )


def test_plan_version_persistence_records_single_step_and_activation(engine) -> None:
    goal = _goal()
    plan = _plan()

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_plan_version(plan)
        active = repo.load_plan_version(plan.plan_version_id).activate(expected_version=1, activated_at=_now())
        repo.activate_plan_version(active, expected_version=1)
        loaded = repo.load_plan_version(plan.plan_version_id)

    assert loaded.status is PlanVersionStatus.ACTIVE
    assert loaded.aggregate_version == 2
    assert loaded.steps[0].step_hash == plan.steps[0].step_hash


def test_plan_version_duplicate_hash_is_rejected_per_goal(engine) -> None:
    goal = _goal()
    plan = _plan()

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_plan_version(plan)

    with pytest.raises(exc.IntegrityError):
        with AgentDomainUnitOfWork(engine) as repo:
            duplicate = PlanVersion.create_single_step(
                plan_version_id="plan:p08:t02:pg:duplicate",
                tenant_id=plan.tenant_id,
                workspace_id=plan.workspace_id,
                goal_version_id=plan.goal_version_id,
                step=DeterministicStepDefinition(
                    step_definition_id="step-def:p08:t02:pg:duplicate",
                    plan_version_id="plan:p08:t02:pg:duplicate",
                    tenant_id=plan.tenant_id,
                    step_no=1,
                    objective_ref=plan.steps[0].objective_ref,
                    input_contract_ref=plan.steps[0].input_contract_ref,
                    output_contract_ref=plan.steps[0].output_contract_ref,
                    acceptance_refs=plan.steps[0].acceptance_refs,
                    executor_type=plan.steps[0].executor_type,
                    required_evidence_refs=plan.steps[0].required_evidence_refs,
                    budget_ref=plan.steps[0].budget_ref,
                    deadline_at=plan.steps[0].deadline_at,
                ),
            )
            repo.record_plan_version(duplicate)


def test_plan_version_optimistic_conflict_blocks_stale_activation(engine) -> None:
    goal = _goal()
    plan = _plan()

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_plan_version(plan)
        active = repo.load_plan_version(plan.plan_version_id).activate(expected_version=1, activated_at=_now())
        repo.activate_plan_version(active, expected_version=1)

        with pytest.raises(AgentDomainConflict, match="expected aggregate_version"):
            repo.activate_plan_version(active, expected_version=1)
