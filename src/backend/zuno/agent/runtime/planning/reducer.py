from __future__ import annotations

from enum import StrEnum
import hashlib
import json
from math import ceil

from pydantic import BaseModel, Field

from zuno.agent.runtime.planning.branch_result import BranchResultRef
from zuno.agent.runtime.planning.dynamic_dag import DynamicPlanJoinPolicy


class ReducerValidationError(ValueError):
    pass


class BranchTerminalStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DISCARDED = "DISCARDED"


class JoinDecision(StrEnum):
    CONTINUE = "CONTINUE"
    WAIT = "WAIT"
    FAIL = "FAIL"
    PARTIAL_CONTINUE = "PARTIAL_CONTINUE"


class BranchReductionInput(BaseModel):
    branch_result: BranchResultRef
    terminal_status: BranchTerminalStatus = BranchTerminalStatus.SUCCEEDED


class ReducedBranchResult(BaseModel):
    branch_result_id: str
    step_run_id: str
    dynamic_step_id: str
    result_ref: str
    result_hash: str
    terminal_status: BranchTerminalStatus


class ReducedJoinOutcome(BaseModel):
    plan_id: str
    plan_version_id: str
    join_policy: DynamicPlanJoinPolicy
    expected_branch_count: int
    reduced_results: tuple[ReducedBranchResult, ...]
    duplicate_result_ids: tuple[str, ...] = Field(default_factory=tuple)
    decision: JoinDecision
    outcome_hash: str = ""

    def model_post_init(self, __context: object) -> None:
        expected_hash = _canonical_hash(
            {
                "plan_id": self.plan_id,
                "plan_version_id": self.plan_version_id,
                "join_policy": self.join_policy.value,
                "expected_branch_count": self.expected_branch_count,
                "reduced_results": [result.model_dump(mode="json") for result in self.reduced_results],
                "duplicate_result_ids": list(self.duplicate_result_ids),
                "decision": self.decision.value,
            }
        )
        if not self.outcome_hash:
            self.outcome_hash = expected_hash
        elif self.outcome_hash != expected_hash:
            raise ReducerValidationError("ReducedJoinOutcome hash mismatch")


class BranchResultReducer:
    def reduce(
        self,
        *,
        plan_id: str,
        plan_version_id: str,
        join_policy: DynamicPlanJoinPolicy,
        expected_branch_count: int,
        branch_results: tuple[BranchReductionInput, ...],
    ) -> ReducedJoinOutcome:
        if expected_branch_count < 1:
            raise ReducerValidationError("expected_branch_count must be positive")
        unique: dict[str, BranchReductionInput] = {}
        duplicates: list[str] = []
        for item in branch_results:
            key = item.branch_result.branch_result_id
            existing = unique.get(key)
            if existing is None:
                unique[key] = item
                continue
            if existing.branch_result.ref_hash != item.branch_result.ref_hash:
                raise ReducerValidationError("conflicting BranchResultRef for same branch_result_id")
            duplicates.append(key)

        reduced = tuple(
            ReducedBranchResult(
                branch_result_id=item.branch_result.branch_result_id,
                step_run_id=item.branch_result.step_run_id,
                dynamic_step_id=item.branch_result.dynamic_step_id,
                result_ref=item.branch_result.result_ref,
                result_hash=item.branch_result.result_hash,
                terminal_status=item.terminal_status,
            )
            for item in sorted(
                unique.values(),
                key=lambda value: (
                    value.branch_result.dynamic_step_id,
                    value.branch_result.branch_result_id,
                    value.branch_result.ref_hash,
                ),
            )
        )
        return ReducedJoinOutcome(
            plan_id=plan_id,
            plan_version_id=plan_version_id,
            join_policy=join_policy,
            expected_branch_count=expected_branch_count,
            reduced_results=reduced,
            duplicate_result_ids=tuple(sorted(duplicates)),
            decision=_evaluate_join_policy(join_policy, expected_branch_count, reduced),
        )


def _evaluate_join_policy(
    join_policy: DynamicPlanJoinPolicy,
    expected_branch_count: int,
    reduced: tuple[ReducedBranchResult, ...],
) -> JoinDecision:
    terminal_count = len(reduced)
    success_count = sum(result.terminal_status is BranchTerminalStatus.SUCCEEDED for result in reduced)
    failure_count = sum(result.terminal_status is BranchTerminalStatus.FAILED for result in reduced)
    if join_policy is DynamicPlanJoinPolicy.ALL_REQUIRED:
        if failure_count:
            return JoinDecision.FAIL
        if success_count == expected_branch_count:
            return JoinDecision.CONTINUE
        return JoinDecision.WAIT
    if join_policy is DynamicPlanJoinPolicy.QUORUM:
        quorum = ceil(expected_branch_count / 2)
        if success_count >= quorum:
            return JoinDecision.CONTINUE
        if terminal_count == expected_branch_count:
            return JoinDecision.FAIL
        return JoinDecision.WAIT
    if join_policy is DynamicPlanJoinPolicy.BEST_EFFORT:
        if success_count >= 1:
            return JoinDecision.PARTIAL_CONTINUE if terminal_count < expected_branch_count or failure_count else JoinDecision.CONTINUE
        if terminal_count == expected_branch_count:
            return JoinDecision.FAIL
        return JoinDecision.WAIT
    if join_policy is DynamicPlanJoinPolicy.FAIL_FAST:
        if failure_count:
            return JoinDecision.FAIL
        if success_count == expected_branch_count:
            return JoinDecision.CONTINUE
        return JoinDecision.WAIT
    return JoinDecision.FAIL


def _canonical_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "BranchReductionInput",
    "BranchResultReducer",
    "BranchTerminalStatus",
    "JoinDecision",
    "ReducedBranchResult",
    "ReducedJoinOutcome",
    "ReducerValidationError",
]
