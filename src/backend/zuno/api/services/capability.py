from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.capability import CapabilityUnitOfWork
from zuno.services.capability_registry import CapabilityRegistryService


class CapabilityService:
    @staticmethod
    async def search_capabilities(
        query: str,
        *,
        user_id: str,
        kind: str = "",
        limit: int = 8,
    ) -> list[dict]:
        results = await CapabilityRegistryService.search(
            query,
            user_id=user_id,
            kind=kind,
            limit=limit,
        )
        CapabilityService.record_search_selection(
            user_id=user_id,
            query=query,
            kind=kind,
            limit=limit,
            results=results,
        )
        return results

    @staticmethod
    def record_search_selection(
        *,
        user_id: str,
        query: str,
        kind: str,
        limit: int,
        results: list[dict[str, Any]],
    ) -> None:
        from zuno.database import engine

        tenant_id = f"user:{user_id}"
        workspace_id = "workspace:default"
        principal_id = user_id
        requirement = {
            "query": query,
            "kind": kind,
            "limit": limit,
            "mode": "api_search",
            "owner_boundary": "Capability selects provider candidates only",
        }
        candidate_ids = tuple(str(item.get("id") or item.get("name") or "") for item in results)
        fingerprint = canonical_sha256(
            {
                "principal_id": principal_id,
                "requirement": requirement,
                "candidates": candidate_ids,
            }
        )[:24]
        snapshot_id = f"capability-snapshot:{fingerprint}"
        selection_id = f"capability-selection:{fingerprint}"
        now = datetime.now(tz=UTC)
        with CapabilityUnitOfWork(engine) as repo:
            repo.create_availability_snapshot(
                snapshot_id=snapshot_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                principal_id=principal_id,
                security_epoch_ref=f"security-epoch:{principal_id}:current",
                source_generation=1,
                visible_candidates=candidate_ids,
                ttl_expires_at=now + timedelta(minutes=5),
            )
            repo.record_selection(
                selection_id=selection_id,
                snapshot_id=snapshot_id,
                requirement=requirement,
                selected_binding_id=None,
                candidate_summary={
                    "candidate_count": len(results),
                    "candidate_ids": candidate_ids,
                    "selected_binding_id": None,
                    "tool_execution": "not_owned_by_capability",
                },
                rejection_reason_codes=[
                    str(item.get("status_message") or item.get("status") or "not_selected")
                    for item in results
                    if item.get("status") != "ready"
                ],
            )


__all__ = ["CapabilityService"]
