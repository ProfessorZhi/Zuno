from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution import StepExecutorRegistry
from zuno.agent.runtime.planning.branch_result import (
    BranchResultDecision,
    BranchResultFencer,
    BranchResultSubmission,
)
from zuno.agent.runtime.planning.dispatch import StepRun, StepRunStatus
from zuno.agent.runtime.planning.reducer import BranchTerminalStatus
from zuno.agent.runtime.planning.send import DynamicStepSendEnvelope
from zuno.agent.runtime.state import AgentRuntimeState


class DynamicStepWorkerValidationError(ValueError):
    pass


class BranchResultObjectStore(Protocol):
    def write_result(self, *, step_run_id: str, payload: dict[str, object]) -> tuple[str, str]: ...


class LocalBranchResultObjectStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write_result(self, *, step_run_id: str, payload: dict[str, object]) -> tuple[str, str]:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        result_hash = hashlib.sha256(encoded).hexdigest()
        path = self.root / f"{_safe_ref(step_run_id)}-{result_hash}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encoded)
        return f"object://agent-results/{step_run_id}/{result_hash}.json", result_hash


class DynamicStepWorkerResult(BaseModel):
    terminal_status: BranchTerminalStatus
    branch_result_decision: BranchResultDecision
    object_ref: str
    result_hash: str


class DynamicStepWorker:
    def __init__(
        self,
        *,
        executors: StepExecutorRegistry,
        object_store: BranchResultObjectStore,
        fencer: BranchResultFencer | None = None,
    ) -> None:
        self.executors = executors
        self.object_store = object_store
        self.fencer = fencer or BranchResultFencer()

    def execute(
        self,
        *,
        envelope: DynamicStepSendEnvelope,
        state: AgentRuntimeState,
        deps: RuntimeDependencies,
        step_run: StepRun,
        active_plan_version_id: str,
        active_execution_epoch: int,
    ) -> DynamicStepWorkerResult:
        self._assert_fenced_envelope(envelope, step_run=step_run)
        plan_step = _plan_step_from_envelope(envelope)
        execution_result = self.executors.execute(state=state, step=plan_step, deps=deps)
        terminal_status = (
            BranchTerminalStatus.SUCCEEDED
            if execution_result.status is ObservationStatus.COMPLETED
            else BranchTerminalStatus.FAILED
        )
        payload = {
            "step_run_id": step_run.step_run_id,
            "dynamic_step_id": envelope.dynamic_step_id,
            "observation": execution_result.observation.model_dump(mode="json"),
            "trace_event_ids": list(execution_result.trace_event_ids),
            "terminal_status": terminal_status.value,
        }
        object_ref, result_hash = self.object_store.write_result(step_run_id=step_run.step_run_id, payload=payload)
        decision = self.fencer.accept(
            BranchResultSubmission(
                branch_result_id=f"branch-result:{step_run.step_run_id}:{result_hash}",
                step_run_id=step_run.step_run_id,
                run_id=step_run.run_id,
                plan_version_id=step_run.plan_version_id,
                dynamic_step_id=step_run.dynamic_step_id,
                execution_epoch=step_run.execution_epoch,
                attempt_no=step_run.attempt_no,
                step_hash=step_run.step_hash,
                result_ref=object_ref,
                result_hash=result_hash,
                producer_ref=f"dynamic_step_worker:{envelope.worker_id}",
            ),
            step_run=step_run,
            active_plan_version_id=active_plan_version_id,
            active_execution_epoch=active_execution_epoch,
        )
        return DynamicStepWorkerResult(
            terminal_status=terminal_status,
            branch_result_decision=decision,
            object_ref=object_ref,
            result_hash=result_hash,
        )

    def _assert_fenced_envelope(self, envelope: DynamicStepSendEnvelope, *, step_run: StepRun) -> None:
        if envelope.step_run_id != step_run.step_run_id:
            raise DynamicStepWorkerValidationError("send envelope step_run_id mismatch")
        if envelope.plan_version_id != step_run.plan_version_id:
            raise DynamicStepWorkerValidationError("send envelope plan_version_id mismatch")
        if envelope.dynamic_step_id != step_run.dynamic_step_id:
            raise DynamicStepWorkerValidationError("send envelope dynamic_step_id mismatch")
        if envelope.execution_epoch != step_run.execution_epoch:
            raise DynamicStepWorkerValidationError("send envelope execution_epoch mismatch")
        if envelope.attempt_no != step_run.attempt_no:
            raise DynamicStepWorkerValidationError("send envelope attempt_no mismatch")
        if envelope.step_hash != step_run.step_hash:
            raise DynamicStepWorkerValidationError("send envelope step_hash mismatch")
        if step_run.status not in {StepRunStatus.CLAIMED, StepRunStatus.RUNNING}:
            raise DynamicStepWorkerValidationError("dynamic worker requires claimed or running StepRun")


def _plan_step_from_envelope(envelope: DynamicStepSendEnvelope) -> PlanStep:
    return PlanStep(
        step_id=envelope.dynamic_step_id,
        goal=envelope.goal,
        action_type=envelope.action_type,
        expected_output=envelope.expected_output,
        acceptance_criteria=list(envelope.acceptance_criteria),
        required_evidence=list(envelope.required_evidence),
        allowed_capabilities=list(envelope.allowed_capabilities),
        budget=dict(envelope.budget),
        attempt=envelope.attempt_no,
        status="running",
    )


def _safe_ref(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)


__all__ = [
    "BranchResultObjectStore",
    "DynamicStepWorker",
    "DynamicStepWorkerResult",
    "DynamicStepWorkerValidationError",
    "LocalBranchResultObjectStore",
]
