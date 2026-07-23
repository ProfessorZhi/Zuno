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
    GoalInputClassification,
    GoalVersion,
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
