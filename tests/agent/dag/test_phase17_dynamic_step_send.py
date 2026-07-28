from __future__ import annotations

import pytest

from zuno.agent.runtime.planning import (
    DYNAMIC_STEP_DISPATCH_TOPIC,
    DYNAMIC_STEP_WORKER_NODE,
    DynamicStepSendBuilder,
    DynamicStepSendEnvelope,
    DynamicStepSendValidationError,
)
from zuno.platform.database.foundation import OutboxEventRecord


def _event(**overrides) -> OutboxEventRecord:
    payload = {
        "dispatch_group_id": "dispatch-group:p17:send",
        "dispatch_item_id": "dispatch-item:p17:send:1",
        "run_id": "run:p17:send",
        "plan_id": "plan:p17:send",
        "plan_version_id": "plan-version:p17:send",
        "dynamic_step_id": "collect",
        "step_run_id": "step-run:p17:send:collect",
        "execution_epoch": 1,
        "attempt_no": 1,
        "step_hash": "a" * 64,
        "commit_required_before_send": True,
        "goal": "collect evidence",
        "action_type": "model",
        "expected_output": "result",
        "acceptance_criteria": ["accepted"],
        "required_evidence": ["source_span"],
        "allowed_capabilities": ["cap:model"],
        "budget": {"units": 1},
    }
    payload.update(overrides.pop("payload", {}))
    return OutboxEventRecord(
        event_id=overrides.pop("event_id", "outbox:step-run:p17:send:collect"),
        aggregate_id=overrides.pop("aggregate_id", "dispatch-group:p17:send"),
        topic=overrides.pop("topic", DYNAMIC_STEP_DISPATCH_TOPIC),
        payload=payload,
        payload_hash=overrides.pop("payload_hash", "b" * 64),
        idempotency_key=overrides.pop("idempotency_key", f"send:{payload['step_run_id']}:{payload['step_hash']}"),
        claim_owner=overrides.pop("claim_owner", "phase17-send-worker"),
        tenant_id=overrides.pop("tenant_id", "tenant-a"),
        ordering_key=overrides.pop("ordering_key", "dispatch-group:p17:send"),
        ordering_sequence=overrides.pop("ordering_sequence", 1),
        publish_attempts=overrides.pop("publish_attempts", 0),
        retry_count=overrides.pop("retry_count", 0),
        replay_count=overrides.pop("replay_count", 0),
    )


def test_phase17_dynamic_step_send_builds_real_langgraph_send_from_claimed_outbox() -> None:
    envelope = DynamicStepSendBuilder().from_claimed_outbox(_event())
    send = envelope.to_langgraph_send()

    assert send.node == DYNAMIC_STEP_WORKER_NODE
    assert send.arg["step_run_id"] == "step-run:p17:send:collect"
    assert send.arg["commit_required_before_send"] is True
    assert send.arg["send_idempotency_key"] == envelope.send_idempotency_key


def test_phase17_dynamic_step_send_rejects_unclaimed_or_wrong_topic_outbox() -> None:
    with pytest.raises(DynamicStepSendValidationError, match="not a dynamic step"):
        DynamicStepSendBuilder().from_claimed_outbox(_event(topic="other.topic"))

    with pytest.raises(DynamicStepSendValidationError, match="claimed before dynamic send"):
        DynamicStepSendBuilder().from_claimed_outbox(_event(claim_owner=""))


def test_phase17_dynamic_step_send_requires_commit_before_send_marker_and_idempotency() -> None:
    with pytest.raises(DynamicStepSendValidationError, match="commit-before-send"):
        DynamicStepSendBuilder().from_claimed_outbox(_event(payload={"commit_required_before_send": False}))

    with pytest.raises(DynamicStepSendValidationError, match="idempotency key mismatch"):
        DynamicStepSendBuilder().from_claimed_outbox(_event(idempotency_key="send:wrong"))


def test_phase17_dynamic_step_send_hash_fences_mutation() -> None:
    envelope = DynamicStepSendBuilder().from_claimed_outbox(_event())

    with pytest.raises(ValueError, match="hash mismatch"):
        DynamicStepSendEnvelope(
            **{
                **envelope.model_dump(),
                "attempt_no": 2,
                "envelope_hash": envelope.envelope_hash,
            }
        )
