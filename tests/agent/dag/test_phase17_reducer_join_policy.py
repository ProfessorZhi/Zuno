from __future__ import annotations

import pytest

from zuno.agent.runtime.planning import (
    BranchReductionInput,
    BranchResultReducer,
    BranchResultRef,
    BranchTerminalStatus,
    DynamicPlanJoinPolicy,
    JoinDecision,
    ReducerValidationError,
)


def _result(step_id: str, *, result_hash: str = "b") -> BranchResultRef:
    return BranchResultRef(
        branch_result_id=f"branch-result:p17:{step_id}",
        step_run_id=f"step-run:p17:{step_id}",
        run_id="run:p17:reduce",
        plan_version_id="plan-version:p17:reduce",
        dynamic_step_id=step_id,
        execution_epoch=1,
        attempt_no=1,
        result_ref=f"object://agent-results/p17/{step_id}.json",
        result_hash=result_hash * 64,
        producer_ref=f"langgraph-send:{step_id}",
    )


def _input(step_id: str, status: BranchTerminalStatus = BranchTerminalStatus.SUCCEEDED) -> BranchReductionInput:
    return BranchReductionInput(branch_result=_result(step_id), terminal_status=status)


def _reduce(
    policy: DynamicPlanJoinPolicy,
    items: tuple[BranchReductionInput, ...],
    *,
    expected: int = 3,
):
    return BranchResultReducer().reduce(
        plan_id="plan:p17:reduce",
        plan_version_id="plan-version:p17:reduce",
        join_policy=policy,
        expected_branch_count=expected,
        branch_results=items,
    )


def test_phase17_reducer_is_order_independent_and_idempotent_for_duplicate_refs() -> None:
    left = _reduce(
        DynamicPlanJoinPolicy.ALL_REQUIRED,
        (_input("b"), _input("a"), _input("a"), _input("c")),
    )
    right = _reduce(
        DynamicPlanJoinPolicy.ALL_REQUIRED,
        (_input("c"), _input("a"), _input("b")),
    )

    assert [result.dynamic_step_id for result in left.reduced_results] == ["a", "b", "c"]
    assert left.duplicate_result_ids == ("branch-result:p17:a",)
    assert left.decision is JoinDecision.CONTINUE
    assert left.outcome_hash != right.outcome_hash
    assert [result.model_dump() for result in left.reduced_results] == [
        result.model_dump() for result in right.reduced_results
    ]


def test_phase17_reducer_rejects_conflicting_duplicate_result_identity() -> None:
    duplicate = BranchReductionInput(
        branch_result=_result("a", result_hash="c"),
        terminal_status=BranchTerminalStatus.SUCCEEDED,
    )

    with pytest.raises(ReducerValidationError, match="conflicting BranchResultRef"):
        _reduce(DynamicPlanJoinPolicy.ALL_REQUIRED, (_input("a"), duplicate))


@pytest.mark.parametrize(
    ("policy", "items", "expected_decision"),
    [
        (DynamicPlanJoinPolicy.ALL_REQUIRED, (_input("a"), _input("b")), JoinDecision.WAIT),
        (
            DynamicPlanJoinPolicy.ALL_REQUIRED,
            (_input("a"), _input("b", BranchTerminalStatus.FAILED), _input("c")),
            JoinDecision.FAIL,
        ),
        (DynamicPlanJoinPolicy.QUORUM, (_input("a"), _input("b")), JoinDecision.CONTINUE),
        (
            DynamicPlanJoinPolicy.QUORUM,
            (
                _input("a", BranchTerminalStatus.FAILED),
                _input("b", BranchTerminalStatus.FAILED),
                _input("c", BranchTerminalStatus.CANCELLED),
            ),
            JoinDecision.FAIL,
        ),
        (DynamicPlanJoinPolicy.BEST_EFFORT, (_input("a"),), JoinDecision.PARTIAL_CONTINUE),
        (
            DynamicPlanJoinPolicy.FAIL_FAST,
            (_input("a"), _input("b", BranchTerminalStatus.FAILED)),
            JoinDecision.FAIL,
        ),
    ],
)
def test_phase17_reducer_evaluates_join_policy(
    policy: DynamicPlanJoinPolicy,
    items: tuple[BranchReductionInput, ...],
    expected_decision: JoinDecision,
) -> None:
    outcome = _reduce(policy, items)

    assert outcome.decision is expected_decision


def test_phase17_reducer_outcome_hash_fences_mutation() -> None:
    outcome = _reduce(DynamicPlanJoinPolicy.QUORUM, (_input("a"), _input("b")))

    with pytest.raises(ValueError, match="hash mismatch"):
        type(outcome)(
            **{
                **outcome.model_dump(),
                "decision": JoinDecision.FAIL,
                "outcome_hash": outcome.outcome_hash,
            }
        )
