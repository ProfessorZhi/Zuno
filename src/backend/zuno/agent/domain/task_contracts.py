from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum


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


def _require_ref(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise AgentDomainError(f"{field_name} is required")


def _require_hash(value: str, field_name: str) -> None:
    _require_ref(value, field_name)
    if len(value) != 64:
        raise AgentDomainError(f"{field_name} must be a canonical sha256 hex digest")
