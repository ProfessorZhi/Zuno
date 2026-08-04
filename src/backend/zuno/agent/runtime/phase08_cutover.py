from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Literal, Protocol

from zuno.agent.domain import AgentDomainConflict
from zuno.agent.runtime.phase08 import Phase08RunService


# Kept only as a product-surface typing annotation (completion routing). The
# phase08 cutover execution surface that dispatched on these modes was removed
# in PHASE22; no runtime dispatches on this literal anymore.
CutoverMode = Literal["shadow", "canary", "new_default", "rollback"]


class Phase08CutoverError(RuntimeError):
    pass


class Phase08SideEffectClaimError(Phase08CutoverError):
    pass


@dataclass(frozen=True, slots=True)
class Phase08RuntimeRequest:
    request_id: str
    tenant_id: str
    workspace_id: str
    user_id: str
    task_id: str
    trace_id: str
    goal: str
    idempotency_key: str
    security_epoch_ref: str = "security-epoch:phase08"
    budget_requested_units: int = 10
    budget_available_units: int = 100

    @property
    def request_hash(self) -> str:
        return _hash(
            {
                "request_id": self.request_id,
                "tenant_id": self.tenant_id,
                "workspace_id": self.workspace_id,
                "user_id": self.user_id,
                "task_id": self.task_id,
                "trace_id": self.trace_id,
                "goal": self.goal,
                "idempotency_key": self.idempotency_key,
                "security_epoch_ref": self.security_epoch_ref,
                "budget_requested_units": self.budget_requested_units,
                "budget_available_units": self.budget_available_units,
            }
        )


@dataclass(frozen=True, slots=True)
class Phase08RuntimeResponse:
    runtime: str
    request_hash: str
    output_ref: str
    trace_ref: str
    side_effect_ref: str | None = None
    shadow_output_ref: str | None = None
    shadow_trace_ref: str | None = None
    shadow_match: bool | None = None
    rollback_reason: str | None = None


class Phase08SideEffectLedger(Protocol):
    def claim(self, request: Phase08RuntimeRequest, *, runtime: str) -> str:
        ...

    def has_claim(self, request: Phase08RuntimeRequest) -> bool:
        ...


class Phase08CutoverAudit(Protocol):
    def record(
        self,
        request: Phase08RuntimeRequest,
        *,
        mode: CutoverMode,
        primary_runtime: str,
        effect_committed: bool,
        fallback_allowed: bool,
        trace_ref: str,
    ) -> str:
        ...


@dataclass
class SideEffectLedger:
    claimed_keys: set[str] = field(default_factory=set)

    def claim(self, request: Phase08RuntimeRequest, *, runtime: str) -> str:
        idempotency_key = request.idempotency_key
        if idempotency_key in self.claimed_keys:
            raise Phase08SideEffectClaimError("duplicate side effect claim")
        self.claimed_keys.add(idempotency_key)
        return f"side-effect:{idempotency_key}"

    def has_claim(self, request: Phase08RuntimeRequest) -> bool:
        return request.idempotency_key in self.claimed_keys


@dataclass(frozen=True, slots=True)
class PostgresPhase08CutoverLedger:
    engine: Any

    def claim(self, request: Phase08RuntimeRequest, *, runtime: str) -> str:
        from zuno.platform.database.agent import AgentDomainUnitOfWork

        effect_claim_id = f"effect-claim:cutover:{request.request_id}:{runtime}"
        effect_ref = f"side-effect:{request.idempotency_key}"
        payload = {
            "request_id": request.request_id,
            "request_hash": request.request_hash,
            "runtime": runtime,
            "workspace_id": request.workspace_id,
            "task_id": request.task_id,
        }
        try:
            with AgentDomainUnitOfWork(self.engine) as repo:
                receipt = repo.claim_effect(
                    effect_claim_id=effect_claim_id,
                    tenant_id=request.tenant_id,
                    idempotency_key=request.idempotency_key,
                    payload=payload,
                    owner_port=f"phase08-cutover:{runtime}",
                    effect_ref=effect_ref,
                )
        except AgentDomainConflict as exc:
            raise Phase08SideEffectClaimError(str(exc)) from exc
        if receipt.status.startswith("duplicate:"):
            return effect_ref
        return effect_ref

    def has_claim(self, request: Phase08RuntimeRequest) -> bool:
        from zuno.platform.database.agent import AgentDomainUnitOfWork

        with AgentDomainUnitOfWork(self.engine) as repo:
            return repo.has_effect_claim(
                tenant_id=request.tenant_id,
                idempotency_key=request.idempotency_key,
            )

    def record(
        self,
        request: Phase08RuntimeRequest,
        *,
        mode: CutoverMode,
        primary_runtime: str,
        effect_committed: bool,
        fallback_allowed: bool,
        trace_ref: str,
    ) -> str:
        from zuno.platform.database.agent import AgentDomainUnitOfWork

        event_id = f"cutover:{request.request_id}:{mode}"
        with AgentDomainUnitOfWork(self.engine) as repo:
            receipt = repo.record_cutover_audit_event(
                cutover_event_id=event_id,
                tenant_id=request.tenant_id,
                workspace_id=request.workspace_id,
                request_id=request.request_id,
                mode=mode,
                primary_runtime=primary_runtime,
                effect_committed=effect_committed,
                fallback_allowed=fallback_allowed,
                request_hash=request.request_hash,
                trace_ref=trace_ref,
            )
        return receipt.ref


class Phase08RetiredController:
    """PHASE22 fail-closed retired adapter for the removed cutover controller.

    The PHASE08 dual-path controller (rollback / shadow / canary dispatch and
    automatic fallback to the old runtime after new-runtime exceptions) was
    removed when the rollback window closed. This adapter is the only surviving
    controller symbol and it is inert:

    - it accepts no mode and no runner; passing either raises ``TypeError``;
    - ``handle`` always raises :class:`Phase08CutoverError`;
    - it holds no runtime reference and can never execute one.

    Production reaches the canonical runtime directly
    (``Phase08RunService`` / ``UnifiedAgentRuntimeService``); see
    :func:`classify_phase08_final_state` for the post-retirement failure
    semantics.
    """

    def handle(self, request: Phase08RuntimeRequest) -> Phase08RuntimeResponse:
        del request
        raise Phase08CutoverError(
            "phase08 cutover controller is retired: production runs the canonical phase08 runtime directly"
        )


def classify_phase08_final_state(state: dict[str, Any]) -> str:
    """Classify a canonical ``Phase08RunService.start`` result under PHASE22 semantics.

    The retired cutover controller never falls back to another runtime, so the
    classification of a new-runtime result is the whole failure contract:

    - ``EFFECT_COMMITTED`` — a side-effect claim was recorded; no second runtime
      may ever execute for this request; return the committed facts or enter
      reconciliation.
    - ``COMPLETED`` — finalized with an outcome; the original facts are returned.
    - ``FAILED/BLOCKED`` — the run failed or was blocked before any side effect
      claim; a retry may reuse the original plan, and there is no old runtime
      to switch to.
    - ``RECONCILIATION_REQUIRED`` — the effect state is unknown: no recognized
      terminal shape (e.g. the run did not finalize). The caller must consult
      the effect ledger / generation reconciliation
      (:func:`~zuno.agent.runtime.reconcile_generations`) and get operator
      confirmation before any retry.
    """
    finalization_status = str(state.get("finalization_status") or "")
    if state.get("effect_claim_ref") is not None:
        return "EFFECT_COMMITTED"
    if state.get("outcome_ref") is not None and finalization_status == "finalized":
        return "COMPLETED"
    if finalization_status in {"failed", "blocked", "cancelled", "abstained", "interrupted"}:
        return "FAILED/BLOCKED"
    return "RECONCILIATION_REQUIRED"


def _hash(payload: dict[str, object]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


__all__ = [
    "CutoverMode",
    "Phase08CutoverAudit",
    "Phase08CutoverError",
    "Phase08RetiredController",
    "Phase08RuntimeRequest",
    "Phase08RuntimeResponse",
    "Phase08SideEffectClaimError",
    "Phase08SideEffectLedger",
    "PostgresPhase08CutoverLedger",
    "SideEffectLedger",
    "classify_phase08_final_state",
]
