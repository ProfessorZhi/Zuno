from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from zuno.agent.domain import (
    AgentDomainConflict,
    AgentDomainError,
    DeterministicStepDefinition,
    PlanVersion,
    PlanVersionStatus,
    StepExecutorType,
)


def _now() -> datetime:
    return datetime(2026, 7, 23, 22, 0, tzinfo=timezone.utc)


def _step(step_definition_id: str = "step-def:p08:t02:1") -> DeterministicStepDefinition:
    return DeterministicStepDefinition(
        step_definition_id=step_definition_id,
        plan_version_id="plan:p08:t02:1",
        tenant_id="tenant-a",
        step_no=1,
        objective_ref="objective:primary",
        input_contract_ref="input:task-contract",
        output_contract_ref="output:answer",
        acceptance_refs=("acceptance:final-gate",),
        executor_type=StepExecutorType.MODEL,
        required_evidence_refs=("evidence:trace",),
        budget_ref="budget:p08:t02",
        deadline_at=_now(),
    )


def _plan() -> PlanVersion:
    step = _step()
    return PlanVersion.create_single_step(
        plan_version_id="plan:p08:t02:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        goal_version_id="goal:p08:t02:1",
        step=step,
    )


def test_deterministic_single_step_plan_hash_is_stable() -> None:
    assert _step().step_hash == _step().step_hash
    assert _plan().plan_hash == _plan().plan_hash


def test_plan_version_activation_once_and_immutability_guard() -> None:
    active = _plan().activate(expected_version=1, activated_at=_now())

    assert active.status is PlanVersionStatus.ACTIVE
    assert active.aggregate_version == 2
    with pytest.raises(AgentDomainError, match="immutable"):
        active.reject_mutation()
    with pytest.raises(AgentDomainError, match="allowed exactly once"):
        active.activate(expected_version=2, activated_at=_now())


def test_plan_version_rejects_optimistic_conflict() -> None:
    with pytest.raises(AgentDomainConflict, match="expected aggregate_version"):
        _plan().activate(expected_version=2, activated_at=_now())


def test_step_definition_rejects_invalid_dependency_shape_for_phase08() -> None:
    with pytest.raises(AgentDomainError, match="exactly one step"):
        replace(_step(), step_no=2)


def test_step_definition_rejects_missing_acceptance_and_unsupported_executor() -> None:
    with pytest.raises(AgentDomainError, match="acceptance_refs"):
        replace(_step(), acceptance_refs=())

    with pytest.raises(ValueError):
        StepExecutorType("SHELL")
