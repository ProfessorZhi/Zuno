from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import IntegrityError

from zuno.agent.domain import (
    AgentDomainConflict,
    AgentDomainError,
    AgentRun,
    AgentRunStatus,
    DeterministicStepDefinition,
    GoalInputClassification,
    GoalVersion,
    PlanVersion,
    PlanVersionStatus,
    StepExecutorType,
    TaskContract,
)


class AgentDomainPersistenceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AgentDomainReceipt:
    ref: str
    status: str
    aggregate_version: int
    domain_generation: int | None = None


class AgentDomainUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __enter__(self) -> "AgentDomainRepository":
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        return AgentDomainRepository(self._connection)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()
        finally:
            self._connection.close()


class AgentDomainRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def record_goal_version(self, goal: GoalVersion) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_goal_versions (
                    goal_version_id, tenant_id, workspace_id, principal_id,
                    goal_sequence, input_classification, objective_hash,
                    output_contract_ref, constraints_hash
                )
                VALUES (
                    :goal_version_id, :tenant_id, :workspace_id, :principal_id,
                    :goal_sequence, :input_classification, :objective_hash,
                    :output_contract_ref, :constraints_hash
                )
                """
            ),
            {
                **_goal_params(goal),
                "input_classification": goal.input_classification.value,
            },
        )
        return AgentDomainReceipt(goal.goal_version_id, "RECORDED", 1)

    def record_task_contract(self, task: TaskContract) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_task_contracts (
                    task_contract_id, tenant_id, workspace_id, principal_id,
                    goal_version_id, idempotency_key, security_context_ref,
                    security_epoch_ref, deadline_at, budget_ref, status, aggregate_version
                )
                VALUES (
                    :task_contract_id, :tenant_id, :workspace_id, :principal_id,
                    :goal_version_id, :idempotency_key, :security_context_ref,
                    :security_epoch_ref, :deadline_at, :budget_ref, :status, :aggregate_version
                )
                """
            ),
            _task_params(task),
        )
        return AgentDomainReceipt(task.task_contract_id, task.status, task.aggregate_version)

    def record_agent_run(self, run: AgentRun) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_domain_runs (
                    run_id, tenant_id, workspace_id, principal_id, task_contract_id,
                    trace_id, status, aggregate_version, domain_generation,
                    started_at, ended_at, failure_code
                )
                VALUES (
                    :run_id, :tenant_id, :workspace_id, :principal_id, :task_contract_id,
                    :trace_id, :status, :aggregate_version, :domain_generation,
                    :started_at, :ended_at, :failure_code
                )
                """
            ),
            _run_params(run),
        )
        self._record_event(
            run_id=run.run_id,
            tenant_id=run.tenant_id,
            sequence_no=run.domain_generation,
            event_type="agent_run.created",
            from_status=None,
            to_status=run.status.value,
            domain_generation=run.domain_generation,
            payload={"task_contract_id": run.task_contract_id, "trace_id": run.trace_id},
        )
        return AgentDomainReceipt(run.run_id, run.status.value, run.aggregate_version, run.domain_generation)

    def load_run(self, run_id: str) -> AgentRun:
        row = self.connection.execute(
            text("SELECT * FROM agent_domain_runs WHERE run_id = :run_id"),
            {"run_id": run_id},
        ).mappings().one()
        return _run_from_row(row)

    def transition_run(self, next_run: AgentRun, *, expected_version: int) -> AgentDomainReceipt:
        previous = self.load_run(next_run.run_id)
        if previous.aggregate_version != expected_version:
            raise AgentDomainConflict(
                f"expected aggregate_version {expected_version}, observed {previous.aggregate_version}"
            )
        if next_run.aggregate_version != expected_version + 1:
            raise AgentDomainError("next_run aggregate_version must increment exactly once")
        result = self.connection.execute(
            text(
                """
                UPDATE agent_domain_runs
                SET status = :status,
                    aggregate_version = :next_version,
                    domain_generation = :domain_generation,
                    started_at = :started_at,
                    ended_at = :ended_at,
                    failure_code = :failure_code
                WHERE run_id = :run_id
                  AND aggregate_version = :expected_version
                """
            ),
            {
                "run_id": next_run.run_id,
                "status": next_run.status.value,
                "next_version": next_run.aggregate_version,
                "domain_generation": next_run.domain_generation,
                "started_at": next_run.started_at,
                "ended_at": next_run.ended_at,
                "failure_code": next_run.failure_code,
                "expected_version": expected_version,
            },
        )
        if result.rowcount != 1:
            raise AgentDomainConflict(f"stale AgentRun transition for {next_run.run_id}")
        self._record_event(
            run_id=next_run.run_id,
            tenant_id=next_run.tenant_id,
            sequence_no=next_run.domain_generation,
            event_type=f"agent_run.{next_run.status.value.lower()}",
            from_status=previous.status.value,
            to_status=next_run.status.value,
            domain_generation=next_run.domain_generation,
            payload={"aggregate_version": next_run.aggregate_version},
        )
        return AgentDomainReceipt(
            next_run.run_id,
            next_run.status.value,
            next_run.aggregate_version,
            next_run.domain_generation,
        )

    def record_plan_version(self, plan: PlanVersion) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_plan_versions (
                    plan_version_id, tenant_id, workspace_id, goal_version_id,
                    plan_kind, status, plan_hash, aggregate_version, activated_at
                )
                VALUES (
                    :plan_version_id, :tenant_id, :workspace_id, :goal_version_id,
                    :plan_kind, :status, :plan_hash, :aggregate_version, :activated_at
                )
                """
            ),
            _plan_params(plan),
        )
        for step in plan.steps:
            self.record_step_definition(step)
        return AgentDomainReceipt(plan.plan_version_id, plan.status.value, plan.aggregate_version)

    def record_step_definition(self, step: DeterministicStepDefinition) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_plan_step_definitions (
                    step_definition_id, plan_version_id, tenant_id, step_no,
                    objective_ref, input_contract_ref, output_contract_ref,
                    acceptance_refs, executor_type, required_evidence_refs,
                    budget_ref, deadline_at, step_hash
                )
                VALUES (
                    :step_definition_id, :plan_version_id, :tenant_id, :step_no,
                    :objective_ref, :input_contract_ref, :output_contract_ref,
                    CAST(:acceptance_refs AS JSON), :executor_type, CAST(:required_evidence_refs AS JSON),
                    :budget_ref, :deadline_at, :step_hash
                )
                """
            ),
            _step_params(step),
        )
        return AgentDomainReceipt(step.step_definition_id, "RECORDED", 1)

    def load_plan_version(self, plan_version_id: str) -> PlanVersion:
        plan_row = self.connection.execute(
            text("SELECT * FROM agent_plan_versions WHERE plan_version_id = :plan_version_id"),
            {"plan_version_id": plan_version_id},
        ).mappings().one()
        step_rows = self.connection.execute(
            text(
                """
                SELECT * FROM agent_plan_step_definitions
                WHERE plan_version_id = :plan_version_id
                ORDER BY step_no
                """
            ),
            {"plan_version_id": plan_version_id},
        ).mappings().all()
        return _plan_from_rows(plan_row, step_rows)

    def activate_plan_version(self, next_plan: PlanVersion, *, expected_version: int) -> AgentDomainReceipt:
        previous = self.load_plan_version(next_plan.plan_version_id)
        if previous.aggregate_version != expected_version:
            raise AgentDomainConflict(
                f"expected aggregate_version {expected_version}, observed {previous.aggregate_version}"
            )
        result = self.connection.execute(
            text(
                """
                UPDATE agent_plan_versions
                SET status = :status,
                    aggregate_version = :next_version,
                    activated_at = :activated_at
                WHERE plan_version_id = :plan_version_id
                  AND aggregate_version = :expected_version
                  AND status = 'DRAFT'
                """
            ),
            {
                "plan_version_id": next_plan.plan_version_id,
                "status": next_plan.status.value,
                "next_version": next_plan.aggregate_version,
                "activated_at": next_plan.activated_at,
                "expected_version": expected_version,
            },
        )
        if result.rowcount != 1:
            raise AgentDomainConflict(f"stale PlanVersion activation for {next_plan.plan_version_id}")
        return AgentDomainReceipt(next_plan.plan_version_id, next_plan.status.value, next_plan.aggregate_version)

    def find_task_contract_by_idempotency(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        idempotency_key: str,
    ) -> TaskContract | None:
        row = self.connection.execute(
            text(
                """
                SELECT * FROM agent_task_contracts
                WHERE tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                  AND idempotency_key = :idempotency_key
                """
            ),
            {"tenant_id": tenant_id, "workspace_id": workspace_id, "idempotency_key": idempotency_key},
        ).mappings().first()
        return None if row is None else _task_from_row(row)

    def _record_event(
        self,
        *,
        run_id: str,
        tenant_id: str,
        sequence_no: int,
        event_type: str,
        from_status: str | None,
        to_status: str,
        domain_generation: int,
        payload: dict[str, Any],
    ) -> None:
        event_id = f"{run_id}:event:{sequence_no}"
        try:
            self.connection.execute(
                text(
                    """
                    INSERT INTO agent_domain_events (
                        event_id, run_id, tenant_id, sequence_no, event_type,
                        from_status, to_status, domain_generation, payload
                    )
                    VALUES (
                        :event_id, :run_id, :tenant_id, :sequence_no, :event_type,
                        :from_status, :to_status, :domain_generation, CAST(:payload AS JSON)
                    )
                    """
                ),
                {
                    "event_id": event_id,
                    "run_id": run_id,
                    "tenant_id": tenant_id,
                    "sequence_no": sequence_no,
                    "event_type": event_type,
                    "from_status": from_status,
                    "to_status": to_status,
                    "domain_generation": domain_generation,
                    "payload": json.dumps(payload, sort_keys=True, separators=(",", ":")),
                },
            )
        except IntegrityError as exc:
            raise AgentDomainConflict(f"duplicate AgentRun domain event: {event_id}") from exc


def _goal_params(goal: GoalVersion) -> dict[str, Any]:
    return {
        "goal_version_id": goal.goal_version_id,
        "tenant_id": goal.tenant_id,
        "workspace_id": goal.workspace_id,
        "principal_id": goal.principal_id,
        "goal_sequence": goal.goal_sequence,
        "objective_hash": goal.objective_hash,
        "output_contract_ref": goal.output_contract_ref,
        "constraints_hash": goal.constraints_hash,
    }


def _task_params(task: TaskContract) -> dict[str, Any]:
    return {
        "task_contract_id": task.task_contract_id,
        "tenant_id": task.tenant_id,
        "workspace_id": task.workspace_id,
        "principal_id": task.principal_id,
        "goal_version_id": task.goal_version_id,
        "idempotency_key": task.idempotency_key,
        "security_context_ref": task.security_context_ref,
        "security_epoch_ref": task.security_epoch_ref,
        "deadline_at": task.deadline_at,
        "budget_ref": task.budget_ref,
        "status": task.status,
        "aggregate_version": task.aggregate_version,
    }


def _run_params(run: AgentRun) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "tenant_id": run.tenant_id,
        "workspace_id": run.workspace_id,
        "principal_id": run.principal_id,
        "task_contract_id": run.task_contract_id,
        "trace_id": run.trace_id,
        "status": run.status.value,
        "aggregate_version": run.aggregate_version,
        "domain_generation": run.domain_generation,
        "started_at": run.started_at,
        "ended_at": run.ended_at,
        "failure_code": run.failure_code,
    }


def _plan_params(plan: PlanVersion) -> dict[str, Any]:
    return {
        "plan_version_id": plan.plan_version_id,
        "tenant_id": plan.tenant_id,
        "workspace_id": plan.workspace_id,
        "goal_version_id": plan.goal_version_id,
        "plan_kind": plan.plan_kind,
        "status": plan.status.value,
        "plan_hash": plan.plan_hash,
        "aggregate_version": plan.aggregate_version,
        "activated_at": plan.activated_at,
    }


def _step_params(step: DeterministicStepDefinition) -> dict[str, Any]:
    return {
        "step_definition_id": step.step_definition_id,
        "plan_version_id": step.plan_version_id,
        "tenant_id": step.tenant_id,
        "step_no": step.step_no,
        "objective_ref": step.objective_ref,
        "input_contract_ref": step.input_contract_ref,
        "output_contract_ref": step.output_contract_ref,
        "acceptance_refs": json.dumps(list(step.acceptance_refs), sort_keys=True, separators=(",", ":")),
        "executor_type": step.executor_type.value,
        "required_evidence_refs": json.dumps(
            list(step.required_evidence_refs),
            sort_keys=True,
            separators=(",", ":"),
        ),
        "budget_ref": step.budget_ref,
        "deadline_at": step.deadline_at,
        "step_hash": step.step_hash,
    }


def _task_from_row(row: Any) -> TaskContract:
    return TaskContract(
        task_contract_id=row["task_contract_id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        principal_id=row["principal_id"],
        goal_version_id=row["goal_version_id"],
        idempotency_key=row["idempotency_key"],
        security_context_ref=row["security_context_ref"],
        security_epoch_ref=row["security_epoch_ref"],
        deadline_at=row["deadline_at"],
        budget_ref=row["budget_ref"],
        status=row["status"],
        aggregate_version=row["aggregate_version"],
    )


def _run_from_row(row: Any) -> AgentRun:
    return AgentRun(
        run_id=row["run_id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        principal_id=row["principal_id"],
        task_contract_id=row["task_contract_id"],
        trace_id=row["trace_id"],
        status=AgentRunStatus(row["status"]),
        aggregate_version=row["aggregate_version"],
        domain_generation=row["domain_generation"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        failure_code=row["failure_code"],
    )


def _step_from_row(row: Any) -> DeterministicStepDefinition:
    return DeterministicStepDefinition(
        step_definition_id=row["step_definition_id"],
        plan_version_id=row["plan_version_id"],
        tenant_id=row["tenant_id"],
        step_no=row["step_no"],
        objective_ref=row["objective_ref"],
        input_contract_ref=row["input_contract_ref"],
        output_contract_ref=row["output_contract_ref"],
        acceptance_refs=tuple(row["acceptance_refs"]),
        executor_type=StepExecutorType(row["executor_type"]),
        required_evidence_refs=tuple(row["required_evidence_refs"]),
        budget_ref=row["budget_ref"],
        deadline_at=row["deadline_at"],
        step_hash=row["step_hash"],
    )


def _plan_from_rows(plan_row: Any, step_rows: list[Any]) -> PlanVersion:
    return PlanVersion(
        plan_version_id=plan_row["plan_version_id"],
        tenant_id=plan_row["tenant_id"],
        workspace_id=plan_row["workspace_id"],
        goal_version_id=plan_row["goal_version_id"],
        plan_kind=plan_row["plan_kind"],
        status=PlanVersionStatus(plan_row["status"]),
        steps=tuple(_step_from_row(row) for row in step_rows),
        plan_hash=plan_row["plan_hash"],
        aggregate_version=plan_row["aggregate_version"],
        activated_at=plan_row["activated_at"],
    )
