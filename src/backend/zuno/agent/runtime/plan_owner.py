"""Canonical Plan Owner — Agent Core.

PHASE22 final legacy cutover: public adapter modules
(``service.py`` / ``factory.py`` / ``harness.py`` / ``adapters.py``) must
not own Plan / RunOutcome / CapabilityPlan / FinalGate instantiations.
The plan owner is the single source of truth for seeding
``CapabilityPlan`` from the product request.
"""

from __future__ import annotations

from typing import Any

from zuno.agent.contracts import CapabilityPlan


def build_capability_plan_from_request(
    *,
    task_id: str,
    capability_ids: tuple[str, ...] | list[str],
    allowed_tools: tuple[str, ...] | list[str],
    approval_required_tools: tuple[str, ...] | list[str],
) -> CapabilityPlan | None:
    """Canonical owner of ``CapabilityPlan`` construction.

    Adapters and services must call into this function instead of
    instantiating ``CapabilityPlan(...)`` directly.
    """
    if not capability_ids and not allowed_tools:
        return CapabilityPlan()
    return CapabilityPlan(
        availability_snapshot_ref=f"capability_snapshot:{task_id}",
        selection_result_ref=f"capability_selection:{task_id}",
        selection_validity="fixed_planning_snapshot",
        allowed_capabilities=list(capability_ids),
        allowed_tools=list(allowed_tools),
        approval_required_tools=list(approval_required_tools),
        blocked_capability_reasons={},
        executed_tools=[],
        risk_summary={"blocked_count": 0, "approval_required_count": len(approval_required_tools)},
    )


__all__ = ["build_capability_plan_from_request"]