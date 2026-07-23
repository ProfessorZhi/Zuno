from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from zuno.agent.domain import (
    AgentDomainConflict,
    AgentDomainError,
    BudgetReservation,
    BudgetReservationStatus,
    ExecutionContextSnapshot,
)


def _now() -> datetime:
    return datetime(2026, 7, 23, 23, 0, tzinfo=timezone.utc)


def _reservation() -> BudgetReservation:
    return BudgetReservation.reserve(
        budget_reservation_id="budget-reservation:p08:t03:1",
        run_id="run:p08:t03:1",
        tenant_id="tenant-a",
        budget_ref="budget:p08:t03",
        reservation_scope="RUN",
        requested_units=100,
        available_units=100,
    )


def _snapshot() -> ExecutionContextSnapshot:
    return ExecutionContextSnapshot(
        execution_snapshot_id="execution-snapshot:p08:t03:1",
        run_id="run:p08:t03:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="principal-a",
        task_contract_id="task-contract:p08:t03:1",
        security_context_ref="security-context:p08:t03",
        security_epoch_ref="security-epoch:p08:t03",
        model_policy_ref="model-policy:p08:t03",
        capability_profile_ref="capability-profile:p08:t03",
        knowledge_snapshot_ref="knowledge-snapshot:p08:t03",
        answer_policy_ref="answer-policy:p08:t03",
        budget_reservation_id="budget-reservation:p08:t03:1",
        deadline_at=datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc),
    )


def test_execution_context_snapshot_is_immutable_and_hash_stable() -> None:
    snapshot = _snapshot()

    assert snapshot.context_hash == _snapshot().context_hash
    with pytest.raises(FrozenInstanceError):
        snapshot.model_policy_ref = "model-policy:mutated"  # type: ignore[misc]
    with pytest.raises(AgentDomainError, match="hash mismatch"):
        replace(snapshot, model_policy_ref="model-policy:mutated")


def test_execution_context_rejects_stale_epoch_and_expired_deadline() -> None:
    snapshot = _snapshot()

    snapshot.assert_current_security_epoch("security-epoch:p08:t03")
    with pytest.raises(AgentDomainError, match="stale security epoch"):
        snapshot.assert_current_security_epoch("security-epoch:new")
    with pytest.raises(AgentDomainError, match="deadline expired"):
        snapshot.assert_deadline_open(datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc))


def test_execution_context_resume_uses_same_policy_refs() -> None:
    snapshot = _snapshot()

    assert snapshot.resume_refs() == {
        "security_context_ref": "security-context:p08:t03",
        "security_epoch_ref": "security-epoch:p08:t03",
        "model_policy_ref": "model-policy:p08:t03",
        "capability_profile_ref": "capability-profile:p08:t03",
        "knowledge_snapshot_ref": "knowledge-snapshot:p08:t03",
        "answer_policy_ref": "answer-policy:p08:t03",
        "budget_reservation_id": "budget-reservation:p08:t03:1",
    }


def test_budget_reservation_and_settlement_are_versioned() -> None:
    reservation = _reservation()
    settled, settlement = reservation.settle(expected_version=1, consumed_units=73, reason_ref="reason:final")

    assert settled.status is BudgetReservationStatus.SETTLED
    assert settled.aggregate_version == 2
    assert settlement.consumed_units == 73
    assert settlement.released_units == 27
    with pytest.raises(AgentDomainError, match="exactly once"):
        settled.settle(expected_version=2, consumed_units=1, reason_ref="reason:repeat")


def test_budget_insufficient_and_stale_settlement_are_rejected() -> None:
    with pytest.raises(AgentDomainError, match="budget insufficient"):
        BudgetReservation.reserve(
            budget_reservation_id="budget-reservation:p08:t03:2",
            run_id="run:p08:t03:1",
            tenant_id="tenant-a",
            budget_ref="budget:p08:t03",
            reservation_scope="RUN",
            requested_units=100,
            available_units=99,
        )

    with pytest.raises(AgentDomainConflict, match="expected aggregate_version"):
        _reservation().settle(expected_version=2, consumed_units=1, reason_ref="reason:stale")
