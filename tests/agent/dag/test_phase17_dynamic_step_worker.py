from __future__ import annotations

from pathlib import Path

import pytest

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution import StepExecutionResult, StepExecutorRegistry
from zuno.agent.runtime.planning import (
    BranchResultStatus,
    BranchTerminalStatus,
    DynamicStepSendBuilder,
    DynamicStepWorker,
    DynamicStepWorkerValidationError,
    LocalBranchResultObjectStore,
    StepRun,
    StepRunStatus,
)
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.platform.database.foundation import OutboxEventRecord


class _ModelExecutor:
    action_types = frozenset({"model"})

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        del state, deps
        return StepExecutionResult(
            step_id=step.step_id,
            status=ObservationStatus.COMPLETED,
            observation=NormalizedObservation(
                observation_id=f"observation:{step.step_id}",
                step_id=step.step_id,
                kind=ObservationKind.MODEL,
                status=ObservationStatus.COMPLETED,
                source="test-model-executor",
                summary=f"executed {step.goal}",
                evidence_ids=list(step.required_evidence),
                metadata={"budget": step.budget},
            ),
            trace_event_ids=[f"trace:{step.step_id}"],
        )


def _event(**payload_overrides) -> OutboxEventRecord:
    payload = {
        "dispatch_group_id": "dispatch-group:p17:worker",
        "dispatch_item_id": "dispatch-item:p17:worker:1",
        "run_id": "run:p17:worker",
        "plan_id": "plan:p17:worker",
        "plan_version_id": "plan-version:p17:worker",
        "dynamic_step_id": "collect",
        "step_run_id": "step-run:p17:worker:collect",
        "execution_epoch": 2,
        "attempt_no": 1,
        "step_hash": "c" * 64,
        "commit_required_before_send": True,
        "goal": "collect source evidence",
        "action_type": "model",
        "expected_output": "result",
        "acceptance_criteria": ["accepted"],
        "required_evidence": ["source_span"],
        "allowed_capabilities": ["cap:model"],
        "budget": {"units": 1},
    }
    payload.update(payload_overrides)
    return OutboxEventRecord(
        event_id="outbox:step-run:p17:worker:collect",
        aggregate_id="dispatch-group:p17:worker",
        topic="agent.dynamic_step.dispatch.requested",
        payload=payload,
        payload_hash="d" * 64,
        idempotency_key=f"send:{payload['step_run_id']}:{payload['step_hash']}",
        claim_owner="phase17-send-worker",
        tenant_id="tenant-a",
        ordering_key="dispatch-group:p17:worker",
        ordering_sequence=1,
        publish_attempts=0,
        retry_count=0,
        replay_count=0,
    )


def _state() -> AgentRuntimeState:
    return AgentRuntimeState(
        run_id="run:p17:worker",
        thread_id="thread:p17",
        workspace_id="workspace-a",
        user_id="principal-a",
        task_id="task:p17",
        trace_id="trace:p17",
        goal="execute dynamic step",
    )


def _step_run(status: StepRunStatus = StepRunStatus.CLAIMED) -> StepRun:
    return StepRun(
        step_run_id="step-run:p17:worker:collect",
        run_id="run:p17:worker",
        plan_version_id="plan-version:p17:worker",
        dynamic_step_id="collect",
        execution_epoch=2,
        attempt_no=1,
        status=status,
        step_hash="c" * 64,
    )


def test_phase17_dynamic_step_worker_executes_and_returns_fenced_branch_result(tmp_path: Path) -> None:
    envelope = DynamicStepSendBuilder().from_claimed_outbox(_event())
    worker = DynamicStepWorker(
        executors=StepExecutorRegistry((_ModelExecutor(),)),
        object_store=LocalBranchResultObjectStore(tmp_path),
    )

    result = worker.execute(
        envelope=envelope,
        state=_state(),
        deps=RuntimeDependencies(),
        step_run=_step_run(),
        active_plan_version_id="plan-version:p17:worker",
        active_execution_epoch=2,
    )

    assert result.terminal_status is BranchTerminalStatus.SUCCEEDED
    assert result.branch_result_decision.status is BranchResultStatus.ACCEPTED
    assert result.branch_result_decision.branch_result is not None
    assert result.branch_result_decision.branch_result.result_ref.startswith("object://")
    assert result.result_hash == result.branch_result_decision.branch_result.result_hash
    assert list(tmp_path.glob("*.json"))


def test_phase17_dynamic_step_worker_rejects_unclaimed_step_run(tmp_path: Path) -> None:
    envelope = DynamicStepSendBuilder().from_claimed_outbox(_event())
    worker = DynamicStepWorker(
        executors=StepExecutorRegistry((_ModelExecutor(),)),
        object_store=LocalBranchResultObjectStore(tmp_path),
    )

    with pytest.raises(DynamicStepWorkerValidationError, match="claimed or running"):
        worker.execute(
            envelope=envelope,
            state=_state(),
            deps=RuntimeDependencies(),
            step_run=_step_run(StepRunStatus.QUEUED),
            active_plan_version_id="plan-version:p17:worker",
            active_execution_epoch=2,
        )


def test_phase17_dynamic_step_worker_rejects_stale_step_hash_before_execution(tmp_path: Path) -> None:
    envelope = DynamicStepSendBuilder().from_claimed_outbox(_event(step_hash="e" * 64))
    stale = _step_run().model_copy(update={"step_hash": "c" * 64})
    worker = DynamicStepWorker(
        executors=StepExecutorRegistry((_ModelExecutor(),)),
        object_store=LocalBranchResultObjectStore(tmp_path),
    )

    with pytest.raises(DynamicStepWorkerValidationError, match="step_hash mismatch"):
        worker.execute(
            envelope=envelope,
            state=_state(),
            deps=RuntimeDependencies(),
            step_run=stale,
            active_plan_version_id="plan-version:p17:worker",
            active_execution_epoch=2,
        )
