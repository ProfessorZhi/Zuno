from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from zuno.agent.domain import (
    AgentDomainConflict,
    AgentDomainError,
    DynamicStepDefinition,
    PlanKind,
    PlanVersion,
    PlanVersionStatus,
    StepExecutorType,
)


def _now() -> datetime:
    return datetime(2026, 7, 27, 13, 0, tzinfo=timezone.utc)


def _step(
    dynamic_step_id: str,
    *,
    step_no: int,
    dependencies: tuple[str, ...] = (),
    executor_type: StepExecutorType = StepExecutorType.MODEL,
) -> DynamicStepDefinition:
    return DynamicStepDefinition(
        step_definition_id=f"step-def:p17:{dynamic_step_id}",
        plan_version_id="plan:p17:dag:1",
        tenant_id="tenant-a",
        step_no=step_no,
        dynamic_step_id=dynamic_step_id,
        objective_ref=f"objective:{dynamic_step_id}",
        input_contract_ref=f"input:{dynamic_step_id}",
        output_contract_ref=f"output:{dynamic_step_id}",
        acceptance_refs=(f"acceptance:{dynamic_step_id}",),
        executor_type=executor_type,
        required_evidence_refs=(f"evidence:{dynamic_step_id}",),
        dependency_step_ids=dependencies,
        dependency_rule="ALL_SUCCESS",
        activation_condition_ref="activation:always",
        resource_claim_refs=(f"resource:{dynamic_step_id}",),
        join_policy_ref="join:ALL",
        budget_ref=f"budget:{dynamic_step_id}",
        deadline_at=_now(),
    )


def _plan() -> PlanVersion:
    return PlanVersion.create_dynamic_dag(
        plan_version_id="plan:p17:dag:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        goal_version_id="goal:p17:dag:1",
        steps=(
            _step("collect", step_no=1),
            _step("analyze", step_no=2, dependencies=("collect",)),
            _step("join", step_no=3, dependencies=("collect", "analyze"), executor_type=StepExecutorType.JOIN),
        ),
    )


def test_phase17_dynamic_plan_version_hash_and_activation_are_immutable() -> None:
    plan = _plan()
    active = plan.activate(expected_version=1, activated_at=_now())

    assert plan.plan_kind == PlanKind.DYNAMIC_DAG.value
    assert plan.plan_hash == _plan().plan_hash
    assert active.status is PlanVersionStatus.ACTIVE
    assert active.aggregate_version == 2
    with pytest.raises(AgentDomainError, match="immutable"):
        active.reject_mutation()
    with pytest.raises(AgentDomainError, match="allowed exactly once"):
        active.activate(expected_version=2, activated_at=_now())


def test_phase17_dynamic_plan_version_supersession_requires_active_cas() -> None:
    active = _plan().activate(expected_version=1, activated_at=_now())
    superseded = active.supersede(expected_version=2)

    assert superseded.status is PlanVersionStatus.SUPERSEDED
    assert superseded.aggregate_version == 3
    with pytest.raises(AgentDomainConflict, match="expected aggregate_version"):
        active.supersede(expected_version=1)
    with pytest.raises(AgentDomainError, match="only ACTIVE"):
        _plan().supersede(expected_version=1)


def test_phase17_dynamic_plan_version_rejects_unknown_dependency_and_cycles() -> None:
    with pytest.raises(AgentDomainError, match="unknown step"):
        PlanVersion.create_dynamic_dag(
            plan_version_id="plan:p17:dag:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            goal_version_id="goal:p17:dag:1",
            steps=(
                _step("a", step_no=1, dependencies=("missing",)),
            ),
        )

    with pytest.raises(AgentDomainError, match="cycle"):
        PlanVersion.create_dynamic_dag(
            plan_version_id="plan:p17:dag:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            goal_version_id="goal:p17:dag:1",
            steps=(
                _step("a", step_no=1, dependencies=("b",)),
                _step("b", step_no=2, dependencies=("a",)),
            ),
        )


def test_phase17_dynamic_plan_version_rejects_duplicate_step_identity() -> None:
    with pytest.raises(AgentDomainError, match="step ids must be unique"):
        PlanVersion.create_dynamic_dag(
            plan_version_id="plan:p17:dag:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            goal_version_id="goal:p17:dag:1",
            steps=(
                _step("a", step_no=1),
                _step("a", step_no=2),
            ),
        )

    with pytest.raises(AgentDomainError, match="step numbers must be unique"):
        PlanVersion.create_dynamic_dag(
            plan_version_id="plan:p17:dag:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            goal_version_id="goal:p17:dag:1",
            steps=(
                _step("a", step_no=1),
                _step("b", step_no=1),
            ),
        )


def test_phase17_dynamic_step_hash_fences_step_mutation() -> None:
    step = _step("collect", step_no=1)

    with pytest.raises(AgentDomainError, match="hash mismatch"):
        replace(step, objective_ref="objective:changed")
