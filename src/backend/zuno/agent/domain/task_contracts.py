from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json


class AgentDomainError(ValueError):
    pass


class AgentDomainConflict(AgentDomainError):
    pass


class GoalInputClassification(StrEnum):
    SUPPLEMENTAL_INPUT = "SUPPLEMENTAL_INPUT"
    CLARIFICATION_RESPONSE = "CLARIFICATION_RESPONSE"
    CONSTRAINT_CHANGE = "CONSTRAINT_CHANGE"
    OUTPUT_CONTRACT_CHANGE = "OUTPUT_CONTRACT_CHANGE"
    OBJECTIVE_CHANGE = "OBJECTIVE_CHANGE"
    CANCELLATION_REQUEST = "CANCELLATION_REQUEST"
    NEW_TASK = "NEW_TASK"


class AgentRunStatus(StrEnum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    STARTED = "STARTED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class PlanVersionStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class StepExecutorType(StrEnum):
    MODEL = "MODEL"
    KNOWLEDGE = "KNOWLEDGE"
    CAPABILITY = "CAPABILITY"
    TOOL = "TOOL"
    INGESTION_WAIT = "INGESTION_WAIT"
    FINAL_GATE = "FINAL_GATE"


class BudgetReservationStatus(StrEnum):
    RESERVED = "RESERVED"
    SETTLED = "SETTLED"


_ALLOWED_TRANSITIONS: dict[AgentRunStatus, set[AgentRunStatus]] = {
    AgentRunStatus.CREATED: {AgentRunStatus.AUTHORIZED, AgentRunStatus.CANCELLING, AgentRunStatus.FAILED},
    AgentRunStatus.AUTHORIZED: {AgentRunStatus.STARTED, AgentRunStatus.CANCELLING, AgentRunStatus.FAILED},
    AgentRunStatus.STARTED: {AgentRunStatus.CANCELLING, AgentRunStatus.FAILED, AgentRunStatus.COMPLETED},
    AgentRunStatus.CANCELLING: {AgentRunStatus.CANCELLED, AgentRunStatus.FAILED},
    AgentRunStatus.CANCELLED: set(),
    AgentRunStatus.FAILED: set(),
    AgentRunStatus.COMPLETED: set(),
}


@dataclass(frozen=True, slots=True)
class GoalVersion:
    goal_version_id: str
    tenant_id: str
    workspace_id: str
    principal_id: str
    goal_sequence: int
    input_classification: GoalInputClassification
    objective_hash: str
    output_contract_ref: str
    constraints_hash: str

    def __post_init__(self) -> None:
        _require_ref(self.goal_version_id, "goal_version_id")
        _require_ref(self.tenant_id, "tenant_id")
        _require_ref(self.workspace_id, "workspace_id")
        _require_ref(self.principal_id, "principal_id")
        _require_hash(self.objective_hash, "objective_hash")
        _require_hash(self.constraints_hash, "constraints_hash")
        if self.goal_sequence < 1:
            raise AgentDomainError("goal_sequence must be positive")


@dataclass(frozen=True, slots=True)
class TaskContract:
    task_contract_id: str
    tenant_id: str
    workspace_id: str
    principal_id: str
    goal_version_id: str
    idempotency_key: str
    security_context_ref: str
    security_epoch_ref: str
    deadline_at: datetime
    budget_ref: str
    status: str = "ACTIVE"
    aggregate_version: int = 1

    def __post_init__(self) -> None:
        for field_name in (
            "task_contract_id",
            "tenant_id",
            "workspace_id",
            "principal_id",
            "goal_version_id",
            "idempotency_key",
            "security_context_ref",
            "security_epoch_ref",
            "budget_ref",
        ):
            _require_ref(getattr(self, field_name), field_name)
        if self.deadline_at.tzinfo is None:
            raise AgentDomainError("deadline_at must be timezone-aware")
        if self.aggregate_version < 1:
            raise AgentDomainError("aggregate_version must be positive")


@dataclass(frozen=True, slots=True)
class AgentRun:
    run_id: str
    tenant_id: str
    workspace_id: str
    principal_id: str
    task_contract_id: str
    trace_id: str
    status: AgentRunStatus = AgentRunStatus.CREATED
    aggregate_version: int = 1
    domain_generation: int = 1
    started_at: datetime | None = None
    ended_at: datetime | None = None
    failure_code: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("run_id", "tenant_id", "workspace_id", "principal_id", "task_contract_id", "trace_id"):
            _require_ref(getattr(self, field_name), field_name)
        if self.aggregate_version < 1 or self.domain_generation < 1:
            raise AgentDomainError("aggregate_version and domain_generation must be positive")

    def authorize(self, *, expected_version: int) -> "AgentRun":
        return self._transition(AgentRunStatus.AUTHORIZED, expected_version=expected_version)

    def start(self, *, expected_version: int, started_at: datetime) -> "AgentRun":
        return self._transition(AgentRunStatus.STARTED, expected_version=expected_version, started_at=started_at)

    def request_cancel(self, *, expected_version: int) -> "AgentRun":
        return self._transition(AgentRunStatus.CANCELLING, expected_version=expected_version)

    def cancel(self, *, expected_version: int, ended_at: datetime) -> "AgentRun":
        return self._transition(AgentRunStatus.CANCELLED, expected_version=expected_version, ended_at=ended_at)

    def fail(self, *, expected_version: int, ended_at: datetime, failure_code: str) -> "AgentRun":
        _require_ref(failure_code, "failure_code")
        return self._transition(
            AgentRunStatus.FAILED,
            expected_version=expected_version,
            ended_at=ended_at,
            failure_code=failure_code,
        )

    def complete(self, *, expected_version: int, ended_at: datetime) -> "AgentRun":
        return self._transition(AgentRunStatus.COMPLETED, expected_version=expected_version, ended_at=ended_at)

    def _transition(
        self,
        next_status: AgentRunStatus,
        *,
        expected_version: int,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        failure_code: str | None = None,
    ) -> "AgentRun":
        if expected_version != self.aggregate_version:
            raise AgentDomainConflict(
                f"expected aggregate_version {expected_version}, observed {self.aggregate_version}"
            )
        if next_status not in _ALLOWED_TRANSITIONS[self.status]:
            raise AgentDomainError(f"illegal AgentRun transition: {self.status.value}->{next_status.value}")
        if started_at is not None and started_at.tzinfo is None:
            raise AgentDomainError("started_at must be timezone-aware")
        if ended_at is not None and ended_at.tzinfo is None:
            raise AgentDomainError("ended_at must be timezone-aware")
        return replace(
            self,
            status=next_status,
            aggregate_version=self.aggregate_version + 1,
            domain_generation=self.domain_generation + 1,
            started_at=started_at if started_at is not None else self.started_at,
            ended_at=ended_at if ended_at is not None else self.ended_at,
            failure_code=failure_code if failure_code is not None else self.failure_code,
        )


@dataclass(frozen=True, slots=True)
class DeterministicStepDefinition:
    step_definition_id: str
    plan_version_id: str
    tenant_id: str
    step_no: int
    objective_ref: str
    input_contract_ref: str
    output_contract_ref: str
    acceptance_refs: tuple[str, ...]
    executor_type: StepExecutorType
    required_evidence_refs: tuple[str, ...]
    budget_ref: str
    deadline_at: datetime
    step_hash: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "step_definition_id",
            "plan_version_id",
            "tenant_id",
            "objective_ref",
            "input_contract_ref",
            "output_contract_ref",
            "budget_ref",
        ):
            _require_ref(getattr(self, field_name), field_name)
        if self.step_no != 1:
            raise AgentDomainError("PHASE08 deterministic PlanVersion supports exactly one step")
        if not self.acceptance_refs:
            raise AgentDomainError("StepDefinition requires acceptance_refs")
        if self.deadline_at.tzinfo is None:
            raise AgentDomainError("deadline_at must be timezone-aware")
        expected_hash = self.compute_hash()
        if not self.step_hash:
            object.__setattr__(self, "step_hash", expected_hash)
        elif self.step_hash != expected_hash:
            raise AgentDomainError("StepDefinition hash mismatch")

    def compute_hash(self) -> str:
        return _canonical_hash(
            {
                "tenant_id": self.tenant_id,
                "step_no": self.step_no,
                "objective_ref": self.objective_ref,
                "input_contract_ref": self.input_contract_ref,
                "output_contract_ref": self.output_contract_ref,
                "acceptance_refs": list(self.acceptance_refs),
                "executor_type": self.executor_type.value,
                "required_evidence_refs": list(self.required_evidence_refs),
                "budget_ref": self.budget_ref,
                "deadline_at": _canonical_datetime(self.deadline_at),
            }
        )


@dataclass(frozen=True, slots=True)
class PlanVersion:
    plan_version_id: str
    tenant_id: str
    workspace_id: str
    goal_version_id: str
    plan_kind: str
    status: PlanVersionStatus
    steps: tuple[DeterministicStepDefinition, ...]
    plan_hash: str = ""
    aggregate_version: int = 1
    activated_at: datetime | None = None

    def __post_init__(self) -> None:
        for field_name in ("plan_version_id", "tenant_id", "workspace_id", "goal_version_id", "plan_kind"):
            _require_ref(getattr(self, field_name), field_name)
        if self.plan_kind != "DETERMINISTIC_SINGLE_STEP":
            raise AgentDomainError("PHASE08-T02 only supports DETERMINISTIC_SINGLE_STEP")
        if len(self.steps) != 1:
            raise AgentDomainError("Deterministic PlanVersion must contain exactly one step")
        if self.steps[0].plan_version_id != self.plan_version_id:
            raise AgentDomainError("StepDefinition must bind PlanVersion")
        if self.aggregate_version < 1:
            raise AgentDomainError("aggregate_version must be positive")
        expected_hash = self.compute_hash()
        if not self.plan_hash:
            object.__setattr__(self, "plan_hash", expected_hash)
        elif self.plan_hash != expected_hash:
            raise AgentDomainError("PlanVersion hash mismatch")

    @classmethod
    def create_single_step(
        cls,
        *,
        plan_version_id: str,
        tenant_id: str,
        workspace_id: str,
        goal_version_id: str,
        step: DeterministicStepDefinition,
    ) -> "PlanVersion":
        return cls(
            plan_version_id=plan_version_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_version_id=goal_version_id,
            plan_kind="DETERMINISTIC_SINGLE_STEP",
            status=PlanVersionStatus.DRAFT,
            steps=(step,),
        )

    def compute_hash(self) -> str:
        return _canonical_hash(
            {
                "tenant_id": self.tenant_id,
                "workspace_id": self.workspace_id,
                "goal_version_id": self.goal_version_id,
                "plan_kind": self.plan_kind,
                "steps": [step.step_hash for step in self.steps],
            }
        )

    def activate(self, *, expected_version: int, activated_at: datetime) -> "PlanVersion":
        if expected_version != self.aggregate_version:
            raise AgentDomainConflict(
                f"expected aggregate_version {expected_version}, observed {self.aggregate_version}"
            )
        if self.status is not PlanVersionStatus.DRAFT:
            raise AgentDomainError("PlanVersion activation is allowed exactly once from DRAFT")
        if activated_at.tzinfo is None:
            raise AgentDomainError("activated_at must be timezone-aware")
        return replace(
            self,
            status=PlanVersionStatus.ACTIVE,
            aggregate_version=self.aggregate_version + 1,
            activated_at=activated_at,
        )

    def reject_mutation(self) -> None:
        if self.status is PlanVersionStatus.ACTIVE:
            raise AgentDomainError("active PlanVersion is immutable; create a new PlanVersion instead")


@dataclass(frozen=True, slots=True)
class BudgetSettlement:
    budget_settlement_id: str
    budget_reservation_id: str
    run_id: str
    tenant_id: str
    consumed_units: int
    released_units: int
    reason_ref: str

    def __post_init__(self) -> None:
        for field_name in ("budget_settlement_id", "budget_reservation_id", "run_id", "tenant_id", "reason_ref"):
            _require_ref(getattr(self, field_name), field_name)
        if self.consumed_units < 0 or self.released_units < 0:
            raise AgentDomainError("BudgetSettlement units must be non-negative")


@dataclass(frozen=True, slots=True)
class BudgetReservation:
    budget_reservation_id: str
    run_id: str
    tenant_id: str
    budget_ref: str
    reservation_scope: str
    requested_units: int
    reserved_units: int
    status: BudgetReservationStatus = BudgetReservationStatus.RESERVED
    aggregate_version: int = 1

    def __post_init__(self) -> None:
        for field_name in ("budget_reservation_id", "run_id", "tenant_id", "budget_ref", "reservation_scope"):
            _require_ref(getattr(self, field_name), field_name)
        if self.requested_units < 1:
            raise AgentDomainError("requested_units must be positive")
        if self.reserved_units < 1:
            raise AgentDomainError("reserved_units must be positive")
        if self.reserved_units > self.requested_units:
            raise AgentDomainError("reserved_units cannot exceed requested_units")
        if self.aggregate_version < 1:
            raise AgentDomainError("aggregate_version must be positive")

    @classmethod
    def reserve(
        cls,
        *,
        budget_reservation_id: str,
        run_id: str,
        tenant_id: str,
        budget_ref: str,
        reservation_scope: str,
        requested_units: int,
        available_units: int,
    ) -> "BudgetReservation":
        if available_units < requested_units:
            raise AgentDomainError("budget insufficient for reservation")
        return cls(
            budget_reservation_id=budget_reservation_id,
            run_id=run_id,
            tenant_id=tenant_id,
            budget_ref=budget_ref,
            reservation_scope=reservation_scope,
            requested_units=requested_units,
            reserved_units=requested_units,
        )

    def settle(self, *, expected_version: int, consumed_units: int, reason_ref: str) -> tuple["BudgetReservation", BudgetSettlement]:
        if expected_version != self.aggregate_version:
            raise AgentDomainConflict(
                f"expected aggregate_version {expected_version}, observed {self.aggregate_version}"
            )
        if self.status is not BudgetReservationStatus.RESERVED:
            raise AgentDomainError("BudgetReservation can be settled exactly once")
        if consumed_units < 0 or consumed_units > self.reserved_units:
            raise AgentDomainError("consumed_units must fit reserved budget")
        settlement = BudgetSettlement(
            budget_settlement_id=f"{self.budget_reservation_id}:settlement",
            budget_reservation_id=self.budget_reservation_id,
            run_id=self.run_id,
            tenant_id=self.tenant_id,
            consumed_units=consumed_units,
            released_units=self.reserved_units - consumed_units,
            reason_ref=reason_ref,
        )
        return (
            replace(self, status=BudgetReservationStatus.SETTLED, aggregate_version=self.aggregate_version + 1),
            settlement,
        )


@dataclass(frozen=True, slots=True)
class ExecutionContextSnapshot:
    execution_snapshot_id: str
    run_id: str
    tenant_id: str
    workspace_id: str
    principal_id: str
    task_contract_id: str
    security_context_ref: str
    security_epoch_ref: str
    model_policy_ref: str
    capability_profile_ref: str
    knowledge_snapshot_ref: str
    answer_policy_ref: str
    budget_reservation_id: str
    deadline_at: datetime
    context_hash: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "execution_snapshot_id",
            "run_id",
            "tenant_id",
            "workspace_id",
            "principal_id",
            "task_contract_id",
            "security_context_ref",
            "security_epoch_ref",
            "model_policy_ref",
            "capability_profile_ref",
            "knowledge_snapshot_ref",
            "answer_policy_ref",
            "budget_reservation_id",
        ):
            _require_ref(getattr(self, field_name), field_name)
        if self.deadline_at.tzinfo is None:
            raise AgentDomainError("deadline_at must be timezone-aware")
        expected_hash = self.compute_hash()
        if not self.context_hash:
            object.__setattr__(self, "context_hash", expected_hash)
        elif self.context_hash != expected_hash:
            raise AgentDomainError("ExecutionContextSnapshot hash mismatch")

    def assert_current_security_epoch(self, current_epoch_ref: str) -> None:
        if current_epoch_ref != self.security_epoch_ref:
            raise AgentDomainError("stale security epoch for ExecutionContextSnapshot")

    def assert_deadline_open(self, observed_at: datetime) -> None:
        if observed_at.tzinfo is None:
            raise AgentDomainError("observed_at must be timezone-aware")
        if observed_at >= self.deadline_at:
            raise AgentDomainError("deadline expired for ExecutionContextSnapshot")

    def resume_refs(self) -> dict[str, str]:
        return {
            "security_context_ref": self.security_context_ref,
            "security_epoch_ref": self.security_epoch_ref,
            "model_policy_ref": self.model_policy_ref,
            "capability_profile_ref": self.capability_profile_ref,
            "knowledge_snapshot_ref": self.knowledge_snapshot_ref,
            "answer_policy_ref": self.answer_policy_ref,
            "budget_reservation_id": self.budget_reservation_id,
        }

    def compute_hash(self) -> str:
        return _canonical_hash(
            {
                "run_id": self.run_id,
                "tenant_id": self.tenant_id,
                "workspace_id": self.workspace_id,
                "principal_id": self.principal_id,
                "task_contract_id": self.task_contract_id,
                "security_context_ref": self.security_context_ref,
                "security_epoch_ref": self.security_epoch_ref,
                "model_policy_ref": self.model_policy_ref,
                "capability_profile_ref": self.capability_profile_ref,
                "knowledge_snapshot_ref": self.knowledge_snapshot_ref,
                "answer_policy_ref": self.answer_policy_ref,
                "budget_reservation_id": self.budget_reservation_id,
                "deadline_at": _canonical_datetime(self.deadline_at),
            }
        )


def _require_ref(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise AgentDomainError(f"{field_name} is required")


def _require_hash(value: str, field_name: str) -> None:
    _require_ref(value, field_name)
    if len(value) != 64:
        raise AgentDomainError(f"{field_name} must be a canonical sha256 hex digest")


def _canonical_hash(payload: dict[str, object]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _canonical_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()
