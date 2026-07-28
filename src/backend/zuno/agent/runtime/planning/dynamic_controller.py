from __future__ import annotations

from pydantic import BaseModel

from zuno.agent.runtime.planning.admission import (
    AdmissionContext,
    AdmissionController,
    AdmissionResult,
    DynamicStepRunState,
    ReadySetBuilder,
    ReadySetSnapshot,
)
from zuno.agent.runtime.planning.dispatch import DispatchCommit, DispatchCommitBuilder
from zuno.agent.runtime.planning.dynamic_dag import DynamicPlanProposal


class DynamicRuntimeDispatchResult(BaseModel):
    ready_set: ReadySetSnapshot
    admission: AdmissionResult
    dispatch_commit: DispatchCommit | None = None
    persisted_receipt_ref: str | None = None
    persisted_status: str | None = None


class DynamicPlanRuntimeController:
    def __init__(
        self,
        *,
        ready_set_builder: ReadySetBuilder | None = None,
        admission_controller: AdmissionController | None = None,
        dispatch_builder: DispatchCommitBuilder | None = None,
    ) -> None:
        self.ready_set_builder = ready_set_builder or ReadySetBuilder()
        self.admission_controller = admission_controller or AdmissionController()
        self.dispatch_builder = dispatch_builder or DispatchCommitBuilder()

    def dispatch_ready_steps(
        self,
        *,
        tenant_id: str,
        proposal: DynamicPlanProposal,
        admission_context: AdmissionContext,
        run_id: str,
        execution_epoch: int,
        repository: object,
        step_states: tuple[DynamicStepRunState, ...] = (),
    ) -> DynamicRuntimeDispatchResult:
        ready_set = self.ready_set_builder.build(proposal, step_states=step_states)
        admission = self.admission_controller.admit(proposal, ready_set, admission_context)
        if not admission.admitted_step_ids:
            return DynamicRuntimeDispatchResult(ready_set=ready_set, admission=admission)
        dispatch_commit = self.dispatch_builder.build(
            proposal,
            admission,
            run_id=run_id,
            execution_epoch=execution_epoch,
        )
        receipt = repository.record_dispatch_commit(tenant_id=tenant_id, commit=dispatch_commit)
        return DynamicRuntimeDispatchResult(
            ready_set=ready_set,
            admission=admission,
            dispatch_commit=dispatch_commit,
            persisted_receipt_ref=receipt.ref,
            persisted_status=receipt.status,
        )


__all__ = [
    "DynamicPlanRuntimeController",
    "DynamicRuntimeDispatchResult",
]
