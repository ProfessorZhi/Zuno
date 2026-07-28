from __future__ import annotations

from enum import StrEnum
import hashlib
import json

from pydantic import BaseModel, Field

from zuno.agent.runtime.planning.admission import (
    AdmissionDecisionStatus,
    AdmissionResult,
)
from zuno.agent.runtime.planning.dynamic_dag import DynamicPlanProposal, DynamicPlanStep


class DispatchValidationError(ValueError):
    pass


class DispatchGroupStatus(StrEnum):
    COMMITTED = "COMMITTED"
    CANCELLED = "CANCELLED"
    DRAINED = "DRAINED"


class DispatchItemStatus(StrEnum):
    PENDING_SEND = "PENDING_SEND"
    SENT = "SENT"
    CANCELLED = "CANCELLED"
    OBSOLETE = "OBSOLETE"


class StepRunStatus(StrEnum):
    QUEUED = "QUEUED"
    CLAIMED = "CLAIMED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    OBSOLETE = "OBSOLETE"


class DispatchGroup(BaseModel):
    dispatch_group_id: str
    run_id: str
    plan_id: str
    plan_version_id: str
    execution_epoch: int
    admitted_step_ids: tuple[str, ...]
    status: DispatchGroupStatus = DispatchGroupStatus.COMMITTED
    committed_before_send: bool = True
    group_hash: str = ""

    def model_post_init(self, __context: object) -> None:
        if self.execution_epoch < 1:
            raise DispatchValidationError("dispatch execution_epoch must be positive")
        if not self.admitted_step_ids:
            raise DispatchValidationError("dispatch group requires admitted steps")
        expected_hash = _canonical_hash(
            {
                "run_id": self.run_id,
                "plan_id": self.plan_id,
                "plan_version_id": self.plan_version_id,
                "execution_epoch": self.execution_epoch,
                "admitted_step_ids": list(self.admitted_step_ids),
                "status": self.status.value,
                "committed_before_send": self.committed_before_send,
            }
        )
        if not self.group_hash:
            self.group_hash = expected_hash
        elif self.group_hash != expected_hash:
            raise DispatchValidationError("dispatch group hash mismatch")


class StepRun(BaseModel):
    step_run_id: str
    run_id: str
    plan_version_id: str
    dynamic_step_id: str
    execution_epoch: int
    attempt_no: int = 1
    status: StepRunStatus = StepRunStatus.QUEUED
    step_hash: str

    def model_post_init(self, __context: object) -> None:
        if self.execution_epoch < 1:
            raise DispatchValidationError("step run execution_epoch must be positive")
        if self.attempt_no < 1:
            raise DispatchValidationError("step run attempt_no must be positive")


class DispatchItem(BaseModel):
    dispatch_item_id: str
    dispatch_group_id: str
    step_run_id: str
    dynamic_step_id: str
    send_idempotency_key: str
    outbox_event_id: str
    status: DispatchItemStatus = DispatchItemStatus.PENDING_SEND


class DispatchOutboxMessage(BaseModel):
    event_id: str
    aggregate_id: str
    topic: str = "agent.dynamic_step.dispatch.requested"
    idempotency_key: str
    payload: dict[str, object]


class DispatchCommit(BaseModel):
    dispatch_group: DispatchGroup
    items: tuple[DispatchItem, ...]
    step_runs: tuple[StepRun, ...]
    outbox_messages: tuple[DispatchOutboxMessage, ...]

    def assert_committed_before_send(self) -> None:
        if self.dispatch_group.status is not DispatchGroupStatus.COMMITTED:
            raise DispatchValidationError("dispatch group must be committed before send")
        if not self.dispatch_group.committed_before_send:
            raise DispatchValidationError("dispatch group missing commit-before-send marker")
        item_step_runs = {item.step_run_id for item in self.items}
        run_ids = {step_run.step_run_id for step_run in self.step_runs}
        outbox_step_runs = {
            str(message.payload.get("step_run_id"))
            for message in self.outbox_messages
        }
        if item_step_runs != run_ids or item_step_runs != outbox_step_runs:
            raise DispatchValidationError("dispatch items, step runs and outbox messages must match")


class DispatchCommitBuilder:
    def build(
        self,
        proposal: DynamicPlanProposal,
        admission: AdmissionResult,
        *,
        run_id: str,
        execution_epoch: int,
    ) -> DispatchCommit:
        if admission.plan_id != proposal.plan_id:
            raise DispatchValidationError("dispatch admission must bind proposal plan_id")
        admitted_ids = admission.admitted_step_ids
        if not admitted_ids:
            raise DispatchValidationError("dispatch requires at least one admitted step")
        steps_by_id = {step.step_id: step for step in proposal.steps}
        missing = [step_id for step_id in admitted_ids if step_id not in steps_by_id]
        if missing:
            raise DispatchValidationError("dispatch admission references unknown step")

        group_id = f"dispatch-group:{run_id}:{admission.plan_version_id}:epoch:{execution_epoch}"
        group = DispatchGroup(
            dispatch_group_id=group_id,
            run_id=run_id,
            plan_id=proposal.plan_id,
            plan_version_id=admission.plan_version_id,
            execution_epoch=execution_epoch,
            admitted_step_ids=admitted_ids,
        )
        step_runs: list[StepRun] = []
        items: list[DispatchItem] = []
        messages: list[DispatchOutboxMessage] = []

        for index, step_id in enumerate(admitted_ids, start=1):
            step = steps_by_id[step_id]
            step_hash = _step_hash(step)
            step_run_id = f"step-run:{run_id}:{admission.plan_version_id}:{step_id}:epoch:{execution_epoch}:attempt:1"
            outbox_event_id = f"outbox:{step_run_id}"
            send_idempotency_key = f"send:{step_run_id}:{step_hash}"
            item = DispatchItem(
                dispatch_item_id=f"dispatch-item:{group_id}:{index}",
                dispatch_group_id=group_id,
                step_run_id=step_run_id,
                dynamic_step_id=step_id,
                send_idempotency_key=send_idempotency_key,
                outbox_event_id=outbox_event_id,
            )
            step_run = StepRun(
                step_run_id=step_run_id,
                run_id=run_id,
                plan_version_id=admission.plan_version_id,
                dynamic_step_id=step_id,
                execution_epoch=execution_epoch,
                status=StepRunStatus.QUEUED,
                step_hash=step_hash,
            )
            message = DispatchOutboxMessage(
                event_id=outbox_event_id,
                aggregate_id=group_id,
                idempotency_key=send_idempotency_key,
                payload={
                    "dispatch_group_id": group_id,
                    "dispatch_item_id": item.dispatch_item_id,
                    "run_id": run_id,
                    "plan_id": proposal.plan_id,
                    "plan_version_id": admission.plan_version_id,
                    "dynamic_step_id": step_id,
                    "step_run_id": step_run_id,
                    "execution_epoch": execution_epoch,
                    "attempt_no": step_run.attempt_no,
                    "step_hash": step_hash,
                    "commit_required_before_send": True,
                    "goal": step.goal,
                    "action_type": step.executor,
                    "expected_output": ",".join(output.output_name for output in step.outputs),
                    "acceptance_criteria": list(step.acceptance_criteria),
                    "required_evidence": list(step.required_evidence),
                    "allowed_capabilities": list(step.allowed_capabilities),
                    "budget": dict(step.budget),
                },
            )
            items.append(item)
            step_runs.append(step_run)
            messages.append(message)

        commit = DispatchCommit(
            dispatch_group=group,
            items=tuple(items),
            step_runs=tuple(step_runs),
            outbox_messages=tuple(messages),
        )
        commit.assert_committed_before_send()
        return commit


def _step_hash(step: DynamicPlanStep) -> str:
    return _canonical_hash(step.model_dump(mode="json"))


def _canonical_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "DispatchCommit",
    "DispatchCommitBuilder",
    "DispatchGroup",
    "DispatchGroupStatus",
    "DispatchItem",
    "DispatchItemStatus",
    "DispatchOutboxMessage",
    "DispatchValidationError",
    "StepRun",
    "StepRunStatus",
]
