from __future__ import annotations

import hashlib
import json
from typing import Any

from langgraph.types import Send
from pydantic import BaseModel, Field

from zuno.platform.database.foundation import OutboxEventRecord


DYNAMIC_STEP_DISPATCH_TOPIC = "agent.dynamic_step.dispatch.requested"
DYNAMIC_STEP_WORKER_NODE = "dynamic_step_worker"


class DynamicStepSendValidationError(ValueError):
    pass


class DynamicStepSendEnvelope(BaseModel):
    outbox_event_id: str
    worker_id: str
    dispatch_group_id: str
    dispatch_item_id: str
    run_id: str
    plan_id: str
    plan_version_id: str
    dynamic_step_id: str
    step_run_id: str
    execution_epoch: int
    attempt_no: int
    step_hash: str
    send_idempotency_key: str
    commit_required_before_send: bool
    goal: str
    action_type: str
    expected_output: str = ""
    acceptance_criteria: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    allowed_capabilities: tuple[str, ...] = ()
    budget: dict[str, Any] = Field(default_factory=dict)
    envelope_hash: str = ""

    def model_post_init(self, __context: object) -> None:
        if self.execution_epoch < 1:
            raise DynamicStepSendValidationError("execution_epoch must be positive")
        if self.attempt_no < 1:
            raise DynamicStepSendValidationError("attempt_no must be positive")
        if not self.commit_required_before_send:
            raise DynamicStepSendValidationError("dynamic step send requires commit-before-send")
        expected_hash = _canonical_hash(
            {
                "outbox_event_id": self.outbox_event_id,
                "worker_id": self.worker_id,
                "dispatch_group_id": self.dispatch_group_id,
                "dispatch_item_id": self.dispatch_item_id,
                "run_id": self.run_id,
                "plan_id": self.plan_id,
                "plan_version_id": self.plan_version_id,
                "dynamic_step_id": self.dynamic_step_id,
                "step_run_id": self.step_run_id,
                "execution_epoch": self.execution_epoch,
                "attempt_no": self.attempt_no,
                "step_hash": self.step_hash,
                "send_idempotency_key": self.send_idempotency_key,
                "commit_required_before_send": self.commit_required_before_send,
                "goal": self.goal,
                "action_type": self.action_type,
                "expected_output": self.expected_output,
                "acceptance_criteria": list(self.acceptance_criteria),
                "required_evidence": list(self.required_evidence),
                "allowed_capabilities": list(self.allowed_capabilities),
                "budget": self.budget,
            }
        )
        if not self.envelope_hash:
            self.envelope_hash = expected_hash
        elif self.envelope_hash != expected_hash:
            raise DynamicStepSendValidationError("DynamicStepSendEnvelope hash mismatch")

    def to_langgraph_send(self) -> Send:
        return Send(
            DYNAMIC_STEP_WORKER_NODE,
            {
                "outbox_event_id": self.outbox_event_id,
                "dispatch_group_id": self.dispatch_group_id,
                "dispatch_item_id": self.dispatch_item_id,
                "run_id": self.run_id,
                "plan_id": self.plan_id,
                "plan_version_id": self.plan_version_id,
                "dynamic_step_id": self.dynamic_step_id,
                "step_run_id": self.step_run_id,
                "execution_epoch": self.execution_epoch,
                "attempt_no": self.attempt_no,
                "step_hash": self.step_hash,
                "send_idempotency_key": self.send_idempotency_key,
                "commit_required_before_send": True,
                "goal": self.goal,
                "action_type": self.action_type,
                "expected_output": self.expected_output,
                "acceptance_criteria": list(self.acceptance_criteria),
                "required_evidence": list(self.required_evidence),
                "allowed_capabilities": list(self.allowed_capabilities),
                "budget": self.budget,
            },
        )


class DynamicStepSendBuilder:
    def from_claimed_outbox(self, event: OutboxEventRecord) -> DynamicStepSendEnvelope:
        if event.topic != DYNAMIC_STEP_DISPATCH_TOPIC:
            raise DynamicStepSendValidationError("outbox event is not a dynamic step dispatch request")
        if not event.claim_owner:
            raise DynamicStepSendValidationError("outbox event must be claimed before dynamic send")
        payload = dict(event.payload)
        required = {
            "dispatch_group_id",
            "dispatch_item_id",
            "run_id",
            "plan_id",
            "plan_version_id",
            "dynamic_step_id",
            "step_run_id",
            "execution_epoch",
            "attempt_no",
            "step_hash",
            "commit_required_before_send",
            "goal",
            "action_type",
            "acceptance_criteria",
        }
        missing = sorted(required - set(payload))
        if missing:
            raise DynamicStepSendValidationError(f"dynamic step dispatch payload missing fields: {missing}")
        if payload["commit_required_before_send"] is not True:
            raise DynamicStepSendValidationError("dynamic step dispatch payload missing commit-before-send marker")
        if event.idempotency_key != f"send:{payload['step_run_id']}:{payload['step_hash']}":
            raise DynamicStepSendValidationError("dynamic step dispatch idempotency key mismatch")
        return DynamicStepSendEnvelope(
            outbox_event_id=event.event_id,
            worker_id=event.claim_owner,
            dispatch_group_id=str(payload["dispatch_group_id"]),
            dispatch_item_id=str(payload["dispatch_item_id"]),
            run_id=str(payload["run_id"]),
            plan_id=str(payload["plan_id"]),
            plan_version_id=str(payload["plan_version_id"]),
            dynamic_step_id=str(payload["dynamic_step_id"]),
            step_run_id=str(payload["step_run_id"]),
            execution_epoch=int(payload["execution_epoch"]),
            attempt_no=int(payload["attempt_no"]),
            step_hash=str(payload["step_hash"]),
            send_idempotency_key=event.idempotency_key,
            commit_required_before_send=bool(payload["commit_required_before_send"]),
            goal=str(payload["goal"]),
            action_type=str(payload["action_type"]),
            expected_output=str(payload.get("expected_output") or ""),
            acceptance_criteria=tuple(str(item) for item in payload.get("acceptance_criteria") or ()),
            required_evidence=tuple(str(item) for item in payload.get("required_evidence") or ()),
            allowed_capabilities=tuple(str(item) for item in payload.get("allowed_capabilities") or ()),
            budget=dict(payload.get("budget") or {}),
        )


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "DYNAMIC_STEP_DISPATCH_TOPIC",
    "DYNAMIC_STEP_WORKER_NODE",
    "DynamicStepSendBuilder",
    "DynamicStepSendEnvelope",
    "DynamicStepSendValidationError",
]
