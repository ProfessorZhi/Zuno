from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Callable, Literal, Protocol

from zuno.agent.domain import AgentDomainConflict
from zuno.agent.runtime.phase08 import Phase08RunService


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


LegacyRunner = Callable[[Phase08RuntimeRequest, bool], Phase08RuntimeResponse]


@dataclass
class Phase08CutoverController:
    mode: CutoverMode
    legacy_runner: LegacyRunner
    new_runtime: Phase08RunService | None = None
    side_effect_ledger: Phase08SideEffectLedger = field(default_factory=SideEffectLedger)
    audit: Phase08CutoverAudit | None = None

    def handle(self, request: Phase08RuntimeRequest) -> Phase08RuntimeResponse:
        if self.mode == "rollback":
            response = self._run_legacy(request, allow_side_effect=True)
            self._record_audit(request, response, primary_runtime="legacy", effect_committed=True, fallback_allowed=False)
            return response

        if self.mode == "shadow":
            legacy = self._run_legacy(request, allow_side_effect=True)
            try:
                shadow = self._run_new(request, allow_side_effect=False)
            except Exception as exc:
                response = Phase08RuntimeResponse(
                    runtime=legacy.runtime,
                    request_hash=request.request_hash,
                    output_ref=legacy.output_ref,
                    trace_ref=legacy.trace_ref,
                    side_effect_ref=legacy.side_effect_ref,
                    shadow_match=False,
                    rollback_reason=f"shadow_unavailable:{type(exc).__name__}",
                )
                self._record_audit(
                    request,
                    response,
                    primary_runtime="legacy",
                    effect_committed=True,
                    fallback_allowed=False,
                )
                return response
            response = Phase08RuntimeResponse(
                runtime=legacy.runtime,
                request_hash=request.request_hash,
                output_ref=legacy.output_ref,
                trace_ref=legacy.trace_ref,
                side_effect_ref=legacy.side_effect_ref,
                shadow_output_ref=shadow.output_ref,
                shadow_trace_ref=shadow.trace_ref,
                shadow_match=legacy.output_ref == shadow.output_ref,
            )
            self._record_audit(request, response, primary_runtime="legacy", effect_committed=True, fallback_allowed=False)
            return response

        try:
            primary = self._run_new(request, allow_side_effect=True)
        except Phase08SideEffectClaimError:
            raise
        except Phase08CutoverError as exc:
            return self._fallback_to_legacy(request, exc)
        except Exception as exc:
            return self._fallback_to_legacy(request, exc)
        if self.mode == "canary":
            legacy_shadow = self._run_legacy(request, allow_side_effect=False)
            response = Phase08RuntimeResponse(
                runtime=primary.runtime,
                request_hash=request.request_hash,
                output_ref=primary.output_ref,
                trace_ref=primary.trace_ref,
                side_effect_ref=primary.side_effect_ref,
                shadow_output_ref=legacy_shadow.output_ref,
                shadow_trace_ref=legacy_shadow.trace_ref,
                shadow_match=primary.output_ref == legacy_shadow.output_ref,
            )
            self._record_audit(request, response, primary_runtime="phase08", effect_committed=True, fallback_allowed=False)
            return response
        self._record_audit(request, primary, primary_runtime="phase08", effect_committed=True, fallback_allowed=False)
        return primary

    def _run_legacy(self, request: Phase08RuntimeRequest, *, allow_side_effect: bool) -> Phase08RuntimeResponse:
        return self.legacy_runner(request, allow_side_effect)

    def _run_new(self, request: Phase08RuntimeRequest, *, allow_side_effect: bool) -> Phase08RuntimeResponse:
        if self.new_runtime is None:
            raise Phase08CutoverError("phase08 durable runtime is not configured")
        state = self.new_runtime.start(
            {
                "run_id": f"run:{request.task_id}:phase08",
                "thread_id": f"thread:{request.task_id}:phase08",
                "trace_id": request.trace_id,
                "task_contract_id": f"task-contract:{request.task_id}",
                "active_goal_version_id": f"goal:{request.task_id}",
                "security_epoch_ref": request.security_epoch_ref,
                "current_security_epoch_ref": request.security_epoch_ref,
                "budget_requested_units": request.budget_requested_units,
                "budget_available_units": request.budget_available_units,
                "shadow_domain_commit_suppressed": not allow_side_effect,
            }
        )
        if state.get("finalization_status") != "finalized":
            raise Phase08CutoverError(f"new runtime did not finalize: {state.get('finalization_status')}")
        side_effect_ref = self.side_effect_ledger.claim(request, runtime="phase08") if allow_side_effect else None
        return Phase08RuntimeResponse(
            runtime="phase08",
            request_hash=request.request_hash,
            output_ref=f"answer:{request.request_hash[:16]}",
            trace_ref=str(state["trace_id"]),
            side_effect_ref=side_effect_ref,
        )

    def _fallback_to_legacy(self, request: Phase08RuntimeRequest, exc: Exception) -> Phase08RuntimeResponse:
        if self.side_effect_ledger.has_claim(request):
            response = Phase08RuntimeResponse(
                runtime="phase08",
                request_hash=request.request_hash,
                output_ref=f"answer:{request.request_hash[:16]}",
                trace_ref=request.trace_id,
                side_effect_ref=f"side-effect:{request.idempotency_key}",
                rollback_reason=f"fallback_blocked_after_effect:{type(exc).__name__}",
            )
            self._record_audit(
                request,
                response,
                primary_runtime="phase08",
                effect_committed=True,
                fallback_allowed=False,
            )
            raise Phase08CutoverError(response.rollback_reason) from exc
        legacy = self._run_legacy(request, allow_side_effect=True)
        response = Phase08RuntimeResponse(
            runtime=legacy.runtime,
            request_hash=request.request_hash,
            output_ref=legacy.output_ref,
            trace_ref=legacy.trace_ref,
            side_effect_ref=legacy.side_effect_ref,
            rollback_reason=f"new_runtime_unavailable:{type(exc).__name__}",
        )
        self._record_audit(request, response, primary_runtime="legacy", effect_committed=True, fallback_allowed=True)
        return response

    def _record_audit(
        self,
        request: Phase08RuntimeRequest,
        response: Phase08RuntimeResponse,
        *,
        primary_runtime: str,
        effect_committed: bool,
        fallback_allowed: bool,
    ) -> None:
        if self.audit is None:
            return
        self.audit.record(
            request,
            mode=self.mode,
            primary_runtime=primary_runtime,
            effect_committed=effect_committed,
            fallback_allowed=fallback_allowed,
            trace_ref=response.trace_ref,
        )


def _hash(payload: dict[str, object]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


__all__ = [
    "CutoverMode",
    "Phase08CutoverController",
    "Phase08CutoverError",
    "Phase08CutoverAudit",
    "Phase08RuntimeRequest",
    "Phase08RuntimeResponse",
    "Phase08SideEffectClaimError",
    "Phase08SideEffectLedger",
    "PostgresPhase08CutoverLedger",
    "SideEffectLedger",
]
