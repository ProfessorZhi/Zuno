from __future__ import annotations

import pytest

from zuno.agent.runtime.planning import (
    BranchResultFencer,
    BranchResultRef,
    BranchResultStatus,
    BranchResultSubmission,
    BranchResultValidationError,
    StepRun,
    StepRunStatus,
)


def _step_run(*, status: StepRunStatus = StepRunStatus.RUNNING) -> StepRun:
    return StepRun(
        step_run_id="step-run:run:p17:branch:plan-version:p17:branch:collect:epoch:2:attempt:1",
        run_id="run:p17:branch",
        plan_version_id="plan-version:p17:branch",
        dynamic_step_id="collect",
        execution_epoch=2,
        attempt_no=1,
        status=status,
        step_hash="a" * 64,
    )


def _submission(**updates: object) -> BranchResultSubmission:
    values = {
        "branch_result_id": "branch-result:p17:branch:collect:1",
        "step_run_id": "step-run:run:p17:branch:plan-version:p17:branch:collect:epoch:2:attempt:1",
        "run_id": "run:p17:branch",
        "plan_version_id": "plan-version:p17:branch",
        "dynamic_step_id": "collect",
        "execution_epoch": 2,
        "attempt_no": 1,
        "step_hash": "a" * 64,
        "result_ref": "object://agent-results/p17/collect.json",
        "result_hash": "b" * 64,
        "producer_ref": "langgraph-send:worker:1",
    }
    values.update(updates)
    return BranchResultSubmission(**values)


def test_phase17_branch_result_fencer_accepts_current_object_ref() -> None:
    decision = BranchResultFencer().accept(
        _submission(),
        step_run=_step_run(),
        active_plan_version_id="plan-version:p17:branch",
        active_execution_epoch=2,
    )

    assert decision.status is BranchResultStatus.ACCEPTED
    assert decision.branch_result is not None
    assert decision.branch_result.result_ref.startswith("object://")
    assert decision.branch_result.ref_hash == decision.branch_result.model_copy().ref_hash


@pytest.mark.parametrize(
    ("updates", "active_plan", "active_epoch", "expected"),
    [
        (
            {"plan_version_id": "plan-version:p17:superseded"},
            "plan-version:p17:branch",
            2,
            BranchResultStatus.REJECTED_STALE_PLAN,
        ),
        (
            {"execution_epoch": 1},
            "plan-version:p17:branch",
            2,
            BranchResultStatus.REJECTED_STALE_EPOCH,
        ),
        (
            {"step_hash": "c" * 64},
            "plan-version:p17:branch",
            2,
            BranchResultStatus.REJECTED_STALE_STEP_HASH,
        ),
    ],
)
def test_phase17_branch_result_fencer_rejects_late_result_fencing_mismatch(
    updates: dict[str, object],
    active_plan: str,
    active_epoch: int,
    expected: BranchResultStatus,
) -> None:
    decision = BranchResultFencer().accept(
        _submission(**updates),
        step_run=_step_run(),
        active_plan_version_id=active_plan,
        active_execution_epoch=active_epoch,
    )

    assert decision.status is expected
    assert decision.branch_result is None


def test_phase17_branch_result_fencer_rejects_terminal_step_run_and_inline_payload() -> None:
    terminal = BranchResultFencer().accept(
        _submission(),
        step_run=_step_run(status=StepRunStatus.OBSOLETE),
        active_plan_version_id="plan-version:p17:branch",
        active_execution_epoch=2,
    )
    inline = BranchResultFencer().accept(
        _submission(result_ref='{"inline":"payload"}'),
        step_run=_step_run(),
        active_plan_version_id="plan-version:p17:branch",
        active_execution_epoch=2,
    )

    assert terminal.status is BranchResultStatus.REJECTED_OBSOLETE_STEP_RUN
    assert inline.status is BranchResultStatus.REJECTED_INLINE_PAYLOAD


def test_phase17_branch_result_ref_hash_fences_mutation() -> None:
    accepted = BranchResultFencer().accept(
        _submission(),
        step_run=_step_run(),
        active_plan_version_id="plan-version:p17:branch",
        active_execution_epoch=2,
    ).branch_result
    assert accepted is not None

    with pytest.raises(ValueError, match="hash mismatch"):
        BranchResultRef(
            **{
                **accepted.model_dump(),
                "result_hash": "d" * 64,
                "ref_hash": accepted.ref_hash,
            }
        )
