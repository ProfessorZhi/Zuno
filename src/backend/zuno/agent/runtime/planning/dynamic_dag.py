from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class DynamicPlanValidationError(ValueError):
    pass


class DynamicPlanDependencyRule(StrEnum):
    ALL_SUCCESS = "ALL_SUCCESS"
    ALL_TERMINAL = "ALL_TERMINAL"
    ANY_SUCCESS = "ANY_SUCCESS"
    OPTIONAL_INPUT = "OPTIONAL_INPUT"
    QUORUM = "QUORUM"


class DynamicPlanJoinPolicy(StrEnum):
    ALL_REQUIRED = "ALL_REQUIRED"
    BEST_EFFORT = "BEST_EFFORT"
    QUORUM = "QUORUM"
    FAIL_FAST = "FAIL_FAST"


class DynamicPlanResourceMode(StrEnum):
    READ = "READ"
    WRITE = "WRITE"
    EXCLUSIVE = "EXCLUSIVE"


class DynamicPlanSideEffectClass(StrEnum):
    NONE = "NONE"
    READ = "READ"
    REVERSIBLE_WRITE = "REVERSIBLE_WRITE"
    IRREVERSIBLE_WRITE = "IRREVERSIBLE_WRITE"
    ASYNC_EXTERNAL = "ASYNC_EXTERNAL"


class DynamicPlanResourceClaim(BaseModel):
    resource_ref: str
    mode: DynamicPlanResourceMode = DynamicPlanResourceMode.READ


class DynamicPlanInputBinding(BaseModel):
    input_name: str
    source_step_id: str | None = None
    source_output_name: str | None = None
    external_ref: str | None = None

    @model_validator(mode="after")
    def _require_exactly_one_source(self) -> "DynamicPlanInputBinding":
        has_step_source = bool(self.source_step_id or self.source_output_name)
        has_external_ref = bool(self.external_ref)
        if has_step_source == has_external_ref:
            raise DynamicPlanValidationError(
                f"input binding {self.input_name} must use exactly one source"
            )
        if has_step_source and not (self.source_step_id and self.source_output_name):
            raise DynamicPlanValidationError(
                f"input binding {self.input_name} must bind step and output"
            )
        return self


class DynamicPlanOutputContract(BaseModel):
    output_name: str
    schema_ref: str
    required: bool = True


class DynamicPlanStep(BaseModel):
    step_id: str
    objective_ref: str
    goal: str
    executor: Literal["model", "knowledge", "tool", "deterministic", "join"]
    dependencies: list[str] = Field(default_factory=list)
    dependency_rule: DynamicPlanDependencyRule = DynamicPlanDependencyRule.ALL_SUCCESS
    activation_condition: str = "always"
    inputs: list[DynamicPlanInputBinding] = Field(default_factory=list)
    outputs: list[DynamicPlanOutputContract] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    allowed_capabilities: list[str] = Field(default_factory=list)
    resource_claims: list[DynamicPlanResourceClaim] = Field(default_factory=list)
    side_effect_class: DynamicPlanSideEffectClass = DynamicPlanSideEffectClass.NONE
    budget: dict[str, int | float] = Field(default_factory=dict)
    deadline_ms: int | None = None


class DynamicPlanProposal(BaseModel):
    plan_id: str
    goal_version_id: str
    planner_ref: str
    join_policy: DynamicPlanJoinPolicy = DynamicPlanJoinPolicy.ALL_REQUIRED
    steps: list[DynamicPlanStep]


class DynamicPlanValidator:
    def __init__(self, *, max_steps: int = 64, supported_executors: set[str] | None = None) -> None:
        self.max_steps = max_steps
        self.supported_executors = supported_executors or {"model", "knowledge", "tool", "deterministic", "join"}

    def validate(self, proposal: DynamicPlanProposal) -> DynamicPlanProposal:
        if not proposal.steps:
            raise DynamicPlanValidationError("dynamic plan must contain at least one step")
        if len(proposal.steps) > self.max_steps:
            raise DynamicPlanValidationError("dynamic plan exceeds max step count")

        steps_by_id: dict[str, DynamicPlanStep] = {}
        for step in proposal.steps:
            if step.step_id in steps_by_id:
                raise DynamicPlanValidationError(f"duplicate dynamic plan step: {step.step_id}")
            if step.executor not in self.supported_executors:
                raise DynamicPlanValidationError(f"unsupported dynamic plan executor: {step.executor}")
            if not step.goal.strip():
                raise DynamicPlanValidationError(f"dynamic plan step has empty goal: {step.step_id}")
            if not step.acceptance_criteria:
                raise DynamicPlanValidationError(
                    f"dynamic plan step has no acceptance criteria: {step.step_id}"
                )
            if not step.outputs:
                raise DynamicPlanValidationError(f"dynamic plan step has no output contract: {step.step_id}")
            if step.step_id in step.dependencies:
                raise DynamicPlanValidationError(f"dynamic plan step depends on itself: {step.step_id}")
            steps_by_id[step.step_id] = step

        self._validate_dependencies(proposal, steps_by_id)
        self._reject_cycles(proposal)
        self._validate_input_bindings(proposal, steps_by_id)
        self._reject_unsafe_parallel_side_effects(proposal)
        return proposal

    def _validate_dependencies(
        self,
        proposal: DynamicPlanProposal,
        steps_by_id: dict[str, DynamicPlanStep],
    ) -> None:
        known = set(steps_by_id)
        for step in proposal.steps:
            missing = set(step.dependencies) - known
            if missing:
                raise DynamicPlanValidationError(f"dynamic plan step has missing dependencies: {step.step_id}")

    def _reject_cycles(self, proposal: DynamicPlanProposal) -> None:
        deps = {step.step_id: set(step.dependencies) for step in proposal.steps}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(step_id: str) -> None:
            if step_id in visited:
                return
            if step_id in visiting:
                raise DynamicPlanValidationError("dynamic plan dependency cycle detected")
            visiting.add(step_id)
            for dependency in deps.get(step_id, set()):
                visit(dependency)
            visiting.remove(step_id)
            visited.add(step_id)

        for step_id in deps:
            visit(step_id)

    def _validate_input_bindings(
        self,
        proposal: DynamicPlanProposal,
        steps_by_id: dict[str, DynamicPlanStep],
    ) -> None:
        outputs_by_step = {
            step.step_id: {output.output_name for output in step.outputs}
            for step in proposal.steps
        }
        for step in proposal.steps:
            for binding in step.inputs:
                if binding.external_ref:
                    continue
                assert binding.source_step_id is not None
                assert binding.source_output_name is not None
                if binding.source_step_id not in steps_by_id:
                    raise DynamicPlanValidationError(
                        f"dynamic plan step has input from unknown step: {step.step_id}"
                    )
                if binding.source_step_id not in step.dependencies:
                    raise DynamicPlanValidationError(
                        f"dynamic plan step input is not dependency-bound: {step.step_id}"
                    )
                if binding.source_output_name not in outputs_by_step[binding.source_step_id]:
                    raise DynamicPlanValidationError(
                        f"dynamic plan step input references missing output: {step.step_id}"
                    )

    def _reject_unsafe_parallel_side_effects(self, proposal: DynamicPlanProposal) -> None:
        for index, left in enumerate(proposal.steps):
            for right in proposal.steps[index + 1 :]:
                if self._ordered(left, right):
                    continue
                if self._has_resource_conflict(left, right):
                    raise DynamicPlanValidationError(
                        f"dynamic plan has unsafe parallel resource conflict: {left.step_id}, {right.step_id}"
                    )
                if self._has_unscoped_parallel_side_effect(left, right):
                    raise DynamicPlanValidationError(
                        f"dynamic plan has unsafe parallel side effect: {left.step_id}, {right.step_id}"
                    )

    @staticmethod
    def _ordered(left: DynamicPlanStep, right: DynamicPlanStep) -> bool:
        return left.step_id in right.dependencies or right.step_id in left.dependencies

    @staticmethod
    def _has_resource_conflict(left: DynamicPlanStep, right: DynamicPlanStep) -> bool:
        left_claims = {claim.resource_ref: claim.mode for claim in left.resource_claims}
        right_claims = {claim.resource_ref: claim.mode for claim in right.resource_claims}
        for resource_ref, left_mode in left_claims.items():
            right_mode = right_claims.get(resource_ref)
            if right_mode is None:
                continue
            if DynamicPlanResourceMode.READ not in {left_mode, right_mode}:
                return True
            if DynamicPlanResourceMode.EXCLUSIVE in {left_mode, right_mode}:
                return True
        return False

    @staticmethod
    def _has_unscoped_parallel_side_effect(left: DynamicPlanStep, right: DynamicPlanStep) -> bool:
        effectful = {
            DynamicPlanSideEffectClass.REVERSIBLE_WRITE,
            DynamicPlanSideEffectClass.IRREVERSIBLE_WRITE,
            DynamicPlanSideEffectClass.ASYNC_EXTERNAL,
        }
        if left.side_effect_class not in effectful or right.side_effect_class not in effectful:
            return False
        left_resources = {claim.resource_ref for claim in left.resource_claims}
        right_resources = {claim.resource_ref for claim in right.resource_claims}
        return not left_resources or not right_resources


class DynamicPlanRepairer:
    def repair(self, proposal: DynamicPlanProposal) -> DynamicPlanProposal:
        repaired_steps = []
        for step in proposal.steps:
            updates: dict[str, object] = {}
            if not step.acceptance_criteria:
                updates["acceptance_criteria"] = [f"{step.step_id} output contract satisfied"]
            if not step.outputs:
                updates["outputs"] = [
                    DynamicPlanOutputContract(
                        output_name="result",
                        schema_ref=f"schema://agent/dynamic-plan/{step.executor}/result",
                    )
                ]
            repaired_steps.append(step.model_copy(update=updates) if updates else step)
        return proposal.model_copy(update={"steps": repaired_steps})


__all__ = [
    "DynamicPlanDependencyRule",
    "DynamicPlanInputBinding",
    "DynamicPlanJoinPolicy",
    "DynamicPlanOutputContract",
    "DynamicPlanProposal",
    "DynamicPlanRepairer",
    "DynamicPlanResourceClaim",
    "DynamicPlanResourceMode",
    "DynamicPlanSideEffectClass",
    "DynamicPlanStep",
    "DynamicPlanValidationError",
    "DynamicPlanValidator",
]
