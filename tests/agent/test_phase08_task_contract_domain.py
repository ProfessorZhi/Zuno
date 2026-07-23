from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zuno.agent.domain import (
    AgentDomainConflict,
    AgentDomainError,
    AgentRun,
    AgentRunStatus,
    GoalInputClassification,
    GoalVersion,
    TaskContract,
)


HEX_64 = "a" * 64


def _now() -> datetime:
    return datetime(2026, 7, 23, 21, 0, tzinfo=timezone.utc)


def _goal() -> GoalVersion:
    return GoalVersion(
        goal_version_id="goal:p08:t01:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="principal-a",
        goal_sequence=1,
        input_classification=GoalInputClassification.OBJECTIVE_CHANGE,
        objective_hash=HEX_64,
        output_contract_ref="output:answer",
        constraints_hash="b" * 64,
    )


def _task() -> TaskContract:
    goal = _goal()
    return TaskContract(
        task_contract_id="task-contract:p08:t01:1",
        tenant_id=goal.tenant_id,
        workspace_id=goal.workspace_id,
        principal_id=goal.principal_id,
        goal_version_id=goal.goal_version_id,
        idempotency_key="idem:p08:t01:1",
        security_context_ref="security-context:p08:t01",
        security_epoch_ref="security-epoch:p08:t01",
        deadline_at=_now(),
        budget_ref="budget:p08:t01",
    )


def _run() -> AgentRun:
    task = _task()
    return AgentRun(
        run_id="run:p08:t01:1",
        tenant_id=task.tenant_id,
        workspace_id=task.workspace_id,
        principal_id=task.principal_id,
        task_contract_id=task.task_contract_id,
        trace_id="trace:p08:t01:1",
    )


def test_goal_and_task_contract_require_refs_hashes_and_deadline() -> None:
    goal = _goal()
    task = _task()

    assert goal.input_classification is GoalInputClassification.OBJECTIVE_CHANGE
    assert task.goal_version_id == goal.goal_version_id
    assert task.security_context_ref
    assert task.deadline_at.tzinfo is not None


def test_agent_run_normal_lifecycle_increments_version_and_generation() -> None:
    run = _run()
    authorized = run.authorize(expected_version=1)
    started = authorized.start(expected_version=2, started_at=_now())
    completed = started.complete(expected_version=3, ended_at=_now())

    assert completed.status is AgentRunStatus.COMPLETED
    assert completed.aggregate_version == 4
    assert completed.domain_generation == 4


def test_agent_run_cancel_lifecycle_requires_cancelling_before_cancelled() -> None:
    run = _run().authorize(expected_version=1).start(expected_version=2, started_at=_now())
    cancelling = run.request_cancel(expected_version=3)
    cancelled = cancelling.cancel(expected_version=4, ended_at=_now())

    assert cancelled.status is AgentRunStatus.CANCELLED


def test_agent_run_rejects_illegal_transition() -> None:
    run = _run()

    with pytest.raises(AgentDomainError, match="illegal AgentRun transition"):
        run.complete(expected_version=1, ended_at=_now())


def test_agent_run_rejects_optimistic_version_conflict() -> None:
    run = _run()

    with pytest.raises(AgentDomainConflict, match="expected aggregate_version"):
        run.authorize(expected_version=2)


def test_task_contract_rejects_naive_deadline() -> None:
    with pytest.raises(AgentDomainError, match="deadline_at"):
        TaskContract(
            task_contract_id="task-contract:bad",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            goal_version_id="goal:bad",
            idempotency_key="idem:bad",
            security_context_ref="security-context:bad",
            security_epoch_ref="security-epoch:bad",
            deadline_at=datetime(2026, 7, 23, 21, 0),
            budget_ref="budget:bad",
        )
