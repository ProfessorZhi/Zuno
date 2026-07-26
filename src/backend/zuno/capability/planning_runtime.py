from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
from typing import Any

from zuno.agent.contracts import CapabilityPlan
from zuno.capability.layer import (
    CapabilityLayerRegistry,
    CapabilityRouteRequest,
    CapabilityRouter,
    build_default_capability_layer_registry,
)


class CapabilityPlanningRuntime:
    def __init__(
        self,
        *,
        registry: CapabilityLayerRegistry | None = None,
        unit_of_work_factory: Any | None = None,
    ) -> None:
        self._router = CapabilityRouter(registry or build_default_capability_layer_registry())
        self._unit_of_work_factory = unit_of_work_factory

    def select(self, request: Any) -> CapabilityPlan:
        payload = dict(request)
        requested_capability_ids = tuple(str(item) for item in payload.get("available_capability_ids", ()) if item)
        if not requested_capability_ids:
            return CapabilityPlan()

        route = self._router.route(
            CapabilityRouteRequest(
                task_id=str(payload["task_id"]),
                workspace_id=str(payload["workspace_id"]),
                task_goal=str(payload["user_goal"]),
                requested_capability_ids=requested_capability_ids,
                pinned_skill_id=payload.get("pinned_skill_id"),
                user_roles=tuple(str(role) for role in payload.get("user_roles", ())),
            )
        )
        snapshot_ref = _stable_id(
            "capability_snapshot",
            payload["workspace_id"],
            payload["task_id"],
            payload["trace_id"],
            *requested_capability_ids,
        )
        selection_ref = _stable_id(
            "capability_selection",
            snapshot_ref,
            *route.allowed_capability_ids,
            *route.blocked_capability_reasons.keys(),
        )
        plan = CapabilityPlan(
            availability_snapshot_ref=snapshot_ref,
            selection_result_ref=selection_ref,
            selection_validity="fixed_planning_snapshot",
            allowed_capabilities=list(route.allowed_capability_ids),
            allowed_tools=list(route.allowed_tool_ids),
            blocked_capability_reasons=dict(route.blocked_capability_reasons),
            approval_required_tools=list(route.approval_required_capability_ids),
            executed_tools=[],
            risk_summary={
                "blocked_count": len(route.blocked_capability_reasons),
                "approval_required_count": len(route.approval_required_capability_ids),
                "planner_exposure": route.planner_exposure,
            },
        )
        if self._unit_of_work_factory is not None:
            self._record_selection(payload=payload, route=route, plan=plan)
        return plan

    def _record_selection(self, *, payload: dict[str, Any], route: Any, plan: CapabilityPlan) -> None:
        now = datetime.now(tz=UTC)
        tenant_id = str(payload.get("tenant_id") or f"user:{payload.get('user_id', 'unknown')}")
        visible_candidates = tuple(
            dict.fromkeys(
                [
                    *[str(item) for item in route.allowed_capability_ids],
                    *[str(item) for item in route.blocked_capability_reasons.keys()],
                ]
            )
        )
        with self._unit_of_work_factory() as repo:
            repo.create_availability_snapshot(
                snapshot_id=str(plan.availability_snapshot_ref),
                tenant_id=tenant_id,
                workspace_id=str(payload["workspace_id"]),
                principal_id=str(payload.get("user_id") or "unknown"),
                security_epoch_ref=str(payload.get("security_epoch_ref") or "security-epoch:current"),
                source_generation=int(payload.get("source_generation") or 1),
                visible_candidates=visible_candidates,
                ttl_expires_at=now + timedelta(minutes=5),
                runtime_signals={
                    capability_id: {
                        "status": "ready" if capability_id in route.allowed_capability_ids else "blocked",
                        "health": "ready" if capability_id in route.allowed_capability_ids else "blocked",
                    }
                    for capability_id in visible_candidates
                },
            )
            repo.record_selection(
                selection_id=str(plan.selection_result_ref),
                snapshot_id=str(plan.availability_snapshot_ref),
                requirement={
                    "task_goal_hash": _stable_hash(str(payload["user_goal"])),
                    "requested_capability_ids": list(payload.get("available_capability_ids", ())),
                    "owner_boundary": "Capability selects provider candidates only",
                },
                selected_binding_id=None,
                candidate_summary={
                    "candidate_count": len(visible_candidates),
                    "candidate_ids": visible_candidates,
                    "allowed_capability_ids": list(route.allowed_capability_ids),
                    "allowed_tool_ids": list(route.allowed_tool_ids),
                    "blocked_capability_reasons": dict(route.blocked_capability_reasons),
                    "tool_execution": "not_owned_by_capability",
                },
                rejection_reason_codes=list(route.blocked_capability_reasons.values()),
            )


def _stable_id(prefix: str, *parts: Any) -> str:
    source = "|".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(source.encode('utf-8')).hexdigest()[:12]}"


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


__all__ = ["CapabilityPlanningRuntime"]
