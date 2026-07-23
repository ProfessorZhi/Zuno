from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Callable, Literal

from zuno.agent.runtime.phase08 import Phase08RunService


CutoverMode = Literal["shadow", "canary", "new_default", "rollback"]


class Phase08CutoverError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Phase08RuntimeRequest:
    request_id: str
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


@dataclass
class SideEffectLedger:
    claimed_keys: set[str] = field(default_factory=set)

    def claim(self, idempotency_key: str) -> str:
        if idempotency_key in self.claimed_keys:
            raise Phase08CutoverError("duplicate side effect claim")
        self.claimed_keys.add(idempotency_key)
        return f"side-effect:{idempotency_key}"


LegacyRunner = Callable[[Phase08RuntimeRequest, bool], Phase08RuntimeResponse]


@dataclass
class Phase08CutoverController:
    mode: CutoverMode
    legacy_runner: LegacyRunner
    new_runtime: Phase08RunService | None = None
    side_effect_ledger: SideEffectLedger = field(default_factory=SideEffectLedger)

    def handle(self, request: Phase08RuntimeRequest) -> Phase08RuntimeResponse:
        if self.mode == "rollback":
            return self._run_legacy(request, allow_side_effect=True)

        if self.mode == "shadow":
            legacy = self._run_legacy(request, allow_side_effect=True)
            shadow = self._run_new(request, allow_side_effect=False)
            return Phase08RuntimeResponse(
                runtime=legacy.runtime,
                request_hash=request.request_hash,
                output_ref=legacy.output_ref,
                trace_ref=legacy.trace_ref,
                side_effect_ref=legacy.side_effect_ref,
                shadow_output_ref=shadow.output_ref,
                shadow_trace_ref=shadow.trace_ref,
                shadow_match=legacy.output_ref == shadow.output_ref,
            )

        try:
            primary = self._run_new(request, allow_side_effect=True)
        except Phase08CutoverError as exc:
            if "duplicate side effect claim" in str(exc):
                raise
            legacy = self._run_legacy(request, allow_side_effect=True)
            return Phase08RuntimeResponse(
                runtime=legacy.runtime,
                request_hash=request.request_hash,
                output_ref=legacy.output_ref,
                trace_ref=legacy.trace_ref,
                side_effect_ref=legacy.side_effect_ref,
                rollback_reason=f"new_runtime_unavailable:{type(exc).__name__}",
            )
        except Exception as exc:
            legacy = self._run_legacy(request, allow_side_effect=True)
            return Phase08RuntimeResponse(
                runtime=legacy.runtime,
                request_hash=request.request_hash,
                output_ref=legacy.output_ref,
                trace_ref=legacy.trace_ref,
                side_effect_ref=legacy.side_effect_ref,
                rollback_reason=f"new_runtime_unavailable:{type(exc).__name__}",
            )
        if self.mode == "canary":
            legacy_shadow = self._run_legacy(request, allow_side_effect=False)
            return Phase08RuntimeResponse(
                runtime=primary.runtime,
                request_hash=request.request_hash,
                output_ref=primary.output_ref,
                trace_ref=primary.trace_ref,
                side_effect_ref=primary.side_effect_ref,
                shadow_output_ref=legacy_shadow.output_ref,
                shadow_trace_ref=legacy_shadow.trace_ref,
                shadow_match=primary.output_ref == legacy_shadow.output_ref,
            )
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
            }
        )
        if state.get("finalization_status") != "finalized":
            raise Phase08CutoverError(f"new runtime did not finalize: {state.get('finalization_status')}")
        side_effect_ref = self.side_effect_ledger.claim(request.idempotency_key) if allow_side_effect else None
        return Phase08RuntimeResponse(
            runtime="phase08",
            request_hash=request.request_hash,
            output_ref=f"answer:{request.request_hash[:16]}",
            trace_ref=str(state["trace_id"]),
            side_effect_ref=side_effect_ref,
        )


def _hash(payload: dict[str, object]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


__all__ = [
    "CutoverMode",
    "Phase08CutoverController",
    "Phase08CutoverError",
    "Phase08RuntimeRequest",
    "Phase08RuntimeResponse",
    "SideEffectLedger",
]
