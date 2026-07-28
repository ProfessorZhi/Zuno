from __future__ import annotations

from enum import StrEnum
from math import ceil

from pydantic import BaseModel, Field

from zuno.agent.runtime.planning.dynamic_dag import (
    DynamicPlanDependencyRule,
    DynamicPlanProposal,
    DynamicPlanResourceClaim,
    DynamicPlanResourceMode,
    DynamicPlanStep,
)


class DynamicPlanStepStatus(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    ADMITTED = "ADMITTED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


class AdmissionDecisionStatus(StrEnum):
    ADMITTED = "ADMITTED"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"


class AdmissionRejectionCode(StrEnum):
    STALE_SECURITY_EPOCH = "STALE_SECURITY_EPOCH"
    CAPABILITY_NOT_AUTHORIZED = "CAPABILITY_NOT_AUTHORIZED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    CAPACITY_EXHAUSTED = "CAPACITY_EXHAUSTED"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"


class DynamicStepRunState(BaseModel):
    step_id: str
    status: DynamicPlanStepStatus = DynamicPlanStepStatus.PENDING


class ReadySetSnapshot(BaseModel):
    plan_id: str
    ready_step_ids: tuple[str, ...]
    waiting_step_ids: tuple[str, ...]
    terminal_step_ids: tuple[str, ...]


class AdmissionContext(BaseModel):
    plan_id: str
    plan_version_id: str
    security_epoch_ref: str
    current_security_epoch_ref: str
    authorized_capabilities: set[str] = Field(default_factory=set)
    available_budget_units: float
    quota_slots: int
    capacity_slots: int
    in_flight_resource_claims: tuple[DynamicPlanResourceClaim, ...] = Field(default_factory=tuple)


class StepAdmissionDecision(BaseModel):
    step_id: str
    status: AdmissionDecisionStatus
    reason_codes: tuple[AdmissionRejectionCode, ...] = Field(default_factory=tuple)
    reserved_budget_units: float = 0


class AdmissionResult(BaseModel):
    plan_id: str
    plan_version_id: str
    decisions: tuple[StepAdmissionDecision, ...]

    @property
    def admitted_step_ids(self) -> tuple[str, ...]:
        return tuple(
            decision.step_id
            for decision in self.decisions
            if decision.status is AdmissionDecisionStatus.ADMITTED
        )


class ReadySetBuilder:
    TERMINAL_STATUSES = {
        DynamicPlanStepStatus.SUCCEEDED,
        DynamicPlanStepStatus.FAILED,
        DynamicPlanStepStatus.CANCELLED,
        DynamicPlanStepStatus.SKIPPED,
    }

    def build(
        self,
        proposal: DynamicPlanProposal,
        *,
        step_states: tuple[DynamicStepRunState, ...] = (),
    ) -> ReadySetSnapshot:
        states = {state.step_id: state.status for state in step_states}
        steps_by_id = {step.step_id: step for step in proposal.steps}
        ready: list[str] = []
        waiting: list[str] = []
        terminal: list[str] = []

        for step in proposal.steps:
            status = states.get(step.step_id, DynamicPlanStepStatus.PENDING)
            if status in self.TERMINAL_STATUSES:
                terminal.append(step.step_id)
                continue
            if status in {DynamicPlanStepStatus.RUNNING, DynamicPlanStepStatus.ADMITTED}:
                waiting.append(step.step_id)
                continue
            if self._dependencies_satisfied(step, states, steps_by_id):
                ready.append(step.step_id)
            else:
                waiting.append(step.step_id)
        return ReadySetSnapshot(
            plan_id=proposal.plan_id,
            ready_step_ids=tuple(ready),
            waiting_step_ids=tuple(waiting),
            terminal_step_ids=tuple(terminal),
        )

    def _dependencies_satisfied(
        self,
        step: DynamicPlanStep,
        states: dict[str, DynamicPlanStepStatus],
        steps_by_id: dict[str, DynamicPlanStep],
    ) -> bool:
        if not step.dependencies:
            return True
        dependency_statuses = [
            states.get(dependency, DynamicPlanStepStatus.PENDING)
            for dependency in step.dependencies
            if dependency in steps_by_id
        ]
        if len(dependency_statuses) != len(step.dependencies):
            return False
        terminal_count = sum(status in self.TERMINAL_STATUSES for status in dependency_statuses)
        success_count = sum(status is DynamicPlanStepStatus.SUCCEEDED for status in dependency_statuses)
        if step.dependency_rule is DynamicPlanDependencyRule.ALL_SUCCESS:
            return success_count == len(step.dependencies)
        if step.dependency_rule is DynamicPlanDependencyRule.ALL_TERMINAL:
            return terminal_count == len(step.dependencies)
        if step.dependency_rule is DynamicPlanDependencyRule.ANY_SUCCESS:
            return success_count >= 1
        if step.dependency_rule is DynamicPlanDependencyRule.OPTIONAL_INPUT:
            return terminal_count == len(step.dependencies)
        if step.dependency_rule is DynamicPlanDependencyRule.QUORUM:
            return success_count >= ceil(len(step.dependencies) / 2)
        return False


class AdmissionController:
    def admit(
        self,
        proposal: DynamicPlanProposal,
        ready_set: ReadySetSnapshot,
        context: AdmissionContext,
    ) -> AdmissionResult:
        if proposal.plan_id != ready_set.plan_id or proposal.plan_id != context.plan_id:
            raise ValueError("admission inputs must bind the same plan_id")

        steps_by_id = {step.step_id: step for step in proposal.steps}
        remaining_budget = context.available_budget_units
        remaining_quota = context.quota_slots
        remaining_capacity = context.capacity_slots
        claimed_resources = list(context.in_flight_resource_claims)
        decisions: list[StepAdmissionDecision] = []

        for step_id in ready_set.ready_step_ids:
            step = steps_by_id[step_id]
            reason_codes = self._step_rejection_codes(
                step,
                context=context,
                remaining_budget=remaining_budget,
                remaining_quota=remaining_quota,
                remaining_capacity=remaining_capacity,
                claimed_resources=tuple(claimed_resources),
            )
            if reason_codes:
                status = (
                    AdmissionDecisionStatus.REJECTED
                    if AdmissionRejectionCode.STALE_SECURITY_EPOCH in reason_codes
                    or AdmissionRejectionCode.CAPABILITY_NOT_AUTHORIZED in reason_codes
                    else AdmissionDecisionStatus.DEFERRED
                )
                decisions.append(
                    StepAdmissionDecision(
                        step_id=step_id,
                        status=status,
                        reason_codes=reason_codes,
                    )
                )
                continue

            step_budget = _step_budget_units(step)
            remaining_budget -= step_budget
            remaining_quota -= 1
            remaining_capacity -= 1
            claimed_resources.extend(step.resource_claims)
            decisions.append(
                StepAdmissionDecision(
                    step_id=step_id,
                    status=AdmissionDecisionStatus.ADMITTED,
                    reserved_budget_units=step_budget,
                )
            )

        return AdmissionResult(
            plan_id=proposal.plan_id,
            plan_version_id=context.plan_version_id,
            decisions=tuple(decisions),
        )

    def _step_rejection_codes(
        self,
        step: DynamicPlanStep,
        *,
        context: AdmissionContext,
        remaining_budget: float,
        remaining_quota: int,
        remaining_capacity: int,
        claimed_resources: tuple[DynamicPlanResourceClaim, ...],
    ) -> tuple[AdmissionRejectionCode, ...]:
        reason_codes: list[AdmissionRejectionCode] = []
        if context.security_epoch_ref != context.current_security_epoch_ref:
            reason_codes.append(AdmissionRejectionCode.STALE_SECURITY_EPOCH)
        if any(capability not in context.authorized_capabilities for capability in step.allowed_capabilities):
            reason_codes.append(AdmissionRejectionCode.CAPABILITY_NOT_AUTHORIZED)
        if _step_budget_units(step) > remaining_budget:
            reason_codes.append(AdmissionRejectionCode.BUDGET_EXHAUSTED)
        if remaining_quota < 1:
            reason_codes.append(AdmissionRejectionCode.QUOTA_EXHAUSTED)
        if remaining_capacity < 1:
            reason_codes.append(AdmissionRejectionCode.CAPACITY_EXHAUSTED)
        if self._conflicts_with_claimed_resources(step, claimed_resources):
            reason_codes.append(AdmissionRejectionCode.RESOURCE_CONFLICT)
        return tuple(reason_codes)

    @staticmethod
    def _conflicts_with_claimed_resources(
        step: DynamicPlanStep,
        claimed_resources: tuple[DynamicPlanResourceClaim, ...],
    ) -> bool:
        for step_claim in step.resource_claims:
            for claimed in claimed_resources:
                if step_claim.resource_ref != claimed.resource_ref:
                    continue
                if DynamicPlanResourceMode.EXCLUSIVE in {step_claim.mode, claimed.mode}:
                    return True
                if DynamicPlanResourceMode.READ not in {step_claim.mode, claimed.mode}:
                    return True
        return False


def _step_budget_units(step: DynamicPlanStep) -> float:
    if not step.budget:
        return 0
    if "units" in step.budget:
        return float(step.budget["units"])
    return float(sum(value for value in step.budget.values() if isinstance(value, int | float)))


__all__ = [
    "AdmissionContext",
    "AdmissionController",
    "AdmissionDecisionStatus",
    "AdmissionRejectionCode",
    "AdmissionResult",
    "DynamicPlanStepStatus",
    "DynamicStepRunState",
    "ReadySetBuilder",
    "ReadySetSnapshot",
    "StepAdmissionDecision",
]
