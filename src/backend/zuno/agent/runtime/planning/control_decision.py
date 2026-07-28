from __future__ import annotations

from enum import StrEnum
import hashlib
import json

from pydantic import BaseModel, Field

from zuno.agent.runtime.planning.reducer import (
    BranchTerminalStatus,
    JoinDecision,
    ReducedJoinOutcome,
)


class ControlDecisionValidationError(ValueError):
    pass


class DynamicControlAction(StrEnum):
    CONTINUE = "CONTINUE"
    WAIT_FOR_BRANCHES = "WAIT_FOR_BRANCHES"
    REQUEST_REFLECTION = "REQUEST_REFLECTION"
    REQUEST_REPLAN_BARRIER = "REQUEST_REPLAN_BARRIER"
    FAIL_RUN = "FAIL_RUN"


class ControlDecisionReason(StrEnum):
    JOIN_COMPLETE = "JOIN_COMPLETE"
    BRANCHES_PENDING = "BRANCHES_PENDING"
    PARTIAL_BRANCH_RESULT = "PARTIAL_BRANCH_RESULT"
    JOIN_FAILURE = "JOIN_FAILURE"
    REFLECTION_DISABLED = "REFLECTION_DISABLED"


class ConditionalReflectionPolicy(BaseModel):
    policy_id: str = "phase17-default-conditional-reflection"
    allow_reflection: bool = True
    reflect_on_partial_continue: bool = True
    require_reflection_before_replan: bool = True
    allow_replan_barrier: bool = True


class JoinControlDecision(BaseModel):
    plan_id: str
    plan_version_id: str
    source_join_decision: JoinDecision
    source_join_outcome_hash: str
    action: DynamicControlAction
    reason: ControlDecisionReason
    reflection_required: bool = False
    replan_barrier_required: bool = False
    retry_permitted: bool = False
    failed_branch_result_ids: tuple[str, ...] = Field(default_factory=tuple)
    pending_branch_count: int = 0
    policy_id: str
    decision_id: str = ""
    decision_hash: str = ""

    def model_post_init(self, __context: object) -> None:
        expected_decision_id = _canonical_hash(
            {
                "plan_id": self.plan_id,
                "plan_version_id": self.plan_version_id,
                "source_join_outcome_hash": self.source_join_outcome_hash,
                "policy_id": self.policy_id,
                "action": self.action.value,
            }
        )
        if not self.decision_id:
            self.decision_id = f"join-control:{expected_decision_id}"
        elif self.decision_id != f"join-control:{expected_decision_id}":
            raise ControlDecisionValidationError("JoinControlDecision decision_id mismatch")

        expected_hash = _canonical_hash(
            {
                "plan_id": self.plan_id,
                "plan_version_id": self.plan_version_id,
                "source_join_decision": self.source_join_decision.value,
                "source_join_outcome_hash": self.source_join_outcome_hash,
                "action": self.action.value,
                "reason": self.reason.value,
                "reflection_required": self.reflection_required,
                "replan_barrier_required": self.replan_barrier_required,
                "retry_permitted": self.retry_permitted,
                "failed_branch_result_ids": list(self.failed_branch_result_ids),
                "pending_branch_count": self.pending_branch_count,
                "policy_id": self.policy_id,
                "decision_id": self.decision_id,
            }
        )
        if not self.decision_hash:
            self.decision_hash = expected_hash
        elif self.decision_hash != expected_hash:
            raise ControlDecisionValidationError("JoinControlDecision hash mismatch")


class JoinControlDecisionEngine:
    def decide(
        self,
        *,
        outcome: ReducedJoinOutcome,
        policy: ConditionalReflectionPolicy | None = None,
    ) -> JoinControlDecision:
        policy = policy or ConditionalReflectionPolicy()
        failed_branch_ids = tuple(
            result.branch_result_id
            for result in outcome.reduced_results
            if result.terminal_status
            in {BranchTerminalStatus.FAILED, BranchTerminalStatus.CANCELLED}
        )
        pending_count = max(outcome.expected_branch_count - len(outcome.reduced_results), 0)

        if outcome.decision is JoinDecision.CONTINUE:
            return _decision(
                outcome,
                policy,
                action=DynamicControlAction.CONTINUE,
                reason=ControlDecisionReason.JOIN_COMPLETE,
                pending_branch_count=pending_count,
            )
        if outcome.decision is JoinDecision.WAIT:
            return _decision(
                outcome,
                policy,
                action=DynamicControlAction.WAIT_FOR_BRANCHES,
                reason=ControlDecisionReason.BRANCHES_PENDING,
                pending_branch_count=pending_count,
            )
        if outcome.decision is JoinDecision.PARTIAL_CONTINUE:
            if policy.allow_reflection and policy.reflect_on_partial_continue:
                return _decision(
                    outcome,
                    policy,
                    action=DynamicControlAction.REQUEST_REFLECTION,
                    reason=ControlDecisionReason.PARTIAL_BRANCH_RESULT,
                    reflection_required=True,
                    failed_branch_result_ids=failed_branch_ids,
                    pending_branch_count=pending_count,
                )
            return _decision(
                outcome,
                policy,
                action=DynamicControlAction.CONTINUE,
                reason=ControlDecisionReason.REFLECTION_DISABLED,
                failed_branch_result_ids=failed_branch_ids,
                pending_branch_count=pending_count,
            )
        if outcome.decision is JoinDecision.FAIL:
            if policy.allow_replan_barrier:
                return _decision(
                    outcome,
                    policy,
                    action=DynamicControlAction.REQUEST_REPLAN_BARRIER,
                    reason=ControlDecisionReason.JOIN_FAILURE,
                    reflection_required=policy.require_reflection_before_replan
                    and policy.allow_reflection,
                    replan_barrier_required=True,
                    failed_branch_result_ids=failed_branch_ids,
                    pending_branch_count=pending_count,
                )
            if policy.allow_reflection:
                return _decision(
                    outcome,
                    policy,
                    action=DynamicControlAction.REQUEST_REFLECTION,
                    reason=ControlDecisionReason.JOIN_FAILURE,
                    reflection_required=True,
                    failed_branch_result_ids=failed_branch_ids,
                    pending_branch_count=pending_count,
                )
        return _decision(
            outcome,
            policy,
            action=DynamicControlAction.FAIL_RUN,
            reason=ControlDecisionReason.REFLECTION_DISABLED,
            failed_branch_result_ids=failed_branch_ids,
            pending_branch_count=pending_count,
        )


def _decision(
    outcome: ReducedJoinOutcome,
    policy: ConditionalReflectionPolicy,
    *,
    action: DynamicControlAction,
    reason: ControlDecisionReason,
    reflection_required: bool = False,
    replan_barrier_required: bool = False,
    failed_branch_result_ids: tuple[str, ...] = (),
    pending_branch_count: int = 0,
) -> JoinControlDecision:
    return JoinControlDecision(
        plan_id=outcome.plan_id,
        plan_version_id=outcome.plan_version_id,
        source_join_decision=outcome.decision,
        source_join_outcome_hash=outcome.outcome_hash,
        action=action,
        reason=reason,
        reflection_required=reflection_required,
        replan_barrier_required=replan_barrier_required,
        retry_permitted=False,
        failed_branch_result_ids=tuple(sorted(failed_branch_result_ids)),
        pending_branch_count=pending_branch_count,
        policy_id=policy.policy_id,
    )


def _canonical_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "ConditionalReflectionPolicy",
    "ControlDecisionReason",
    "ControlDecisionValidationError",
    "DynamicControlAction",
    "JoinControlDecision",
    "JoinControlDecisionEngine",
]
