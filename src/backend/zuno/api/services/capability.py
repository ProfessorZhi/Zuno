from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.capability import CapabilityUnitOfWork
from zuno.platform.database.foundation import InfrastructureRepository
from zuno.services.capability_registry import CapabilityRegistryService


CAPABILITY_TRANSITION_TOPIC = "capability.transition.committed"
CAPABILITY_TRANSITION_CONSUMER = "agent-core-capability-transition"
CAPABILITY_SELECTION_TOPIC = "capability.selection.committed"
CAPABILITY_SELECTION_CONSUMER = "agent-core-capability-selection"


@dataclass(frozen=True, slots=True)
class CapabilityTransitionConsumeResult:
    event_id: str
    transition_id: str
    aggregate_ref: str
    committed_generation: int | None
    inbox_first_seen: bool
    outbox_status: str


@dataclass(frozen=True, slots=True)
class CapabilitySelectionConsumeResult:
    event_id: str
    snapshot_id: str
    selection_id: str
    inbox_first_seen: bool
    outbox_status: str


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
                runtime_signals={
                    str(item.get("id") or item.get("name") or ""): {
                        "status": item.get("status") or "unknown",
                        "health": item.get("health") or item.get("status") or "unknown",
                        "quota_remaining": item.get("quota_remaining"),
                        "capacity_remaining": item.get("capacity_remaining"),
                    }
                    for item in results
                },
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

    @staticmethod
    def consume_transition_event(
        *,
        event_id: str,
        worker_id: str,
        engine: Any | None = None,
    ) -> CapabilityTransitionConsumeResult:
        if engine is None:
            from zuno.database import engine as default_engine

            engine = default_engine

        context = nullcontext(engine) if hasattr(engine, "execute") else engine.begin()
        with context as conn:
            infra_repo = InfrastructureRepository(conn)
            if not infra_repo.claim_outbox_event(event_id=event_id, worker_id=worker_id):
                return CapabilityTransitionConsumeResult(
                    event_id=event_id,
                    transition_id="",
                    aggregate_ref="",
                    committed_generation=None,
                    inbox_first_seen=False,
                    outbox_status="not_claimed",
                )
            record = infra_repo.load_claimed_outbox_event(event_id=event_id, worker_id=worker_id)
            payload = dict(record.payload)
            if (
                record.topic != CAPABILITY_TRANSITION_TOPIC
                or payload.get("consumer_module") != "Agent Core"
            ):
                raise ValueError("outbox event is not an Agent Core capability transition")
            tenant_id = str(record.tenant_id)
            receipt = infra_repo.record_inbox_receipt(
                consumer=CAPABILITY_TRANSITION_CONSUMER,
                message_id=record.event_id,
                payload=payload,
                tenant_id=tenant_id,
                ordering_key=record.ordering_key,
                ordering_sequence=record.ordering_sequence,
            )
            if receipt.first_seen:
                infra_repo.mark_inbox_processed(
                    tenant_id=tenant_id,
                    consumer=CAPABILITY_TRANSITION_CONSUMER,
                    message_id=record.event_id,
                )
            infra_repo.complete_outbox(event_id=record.event_id, worker_id=worker_id)
        return CapabilityTransitionConsumeResult(
            event_id=event_id,
            transition_id=str(payload.get("transition_id") or ""),
            aggregate_ref=str(payload.get("aggregate_ref") or ""),
            committed_generation=int(payload["committed_generation"]) if payload.get("committed_generation") is not None else None,
            inbox_first_seen=receipt.first_seen,
            outbox_status="published",
        )

    @staticmethod
    def consume_selection_event(
        *,
        event_id: str,
        worker_id: str,
        engine: Any | None = None,
    ) -> CapabilitySelectionConsumeResult:
        if engine is None:
            from zuno.database import engine as default_engine

            engine = default_engine

        context = nullcontext(engine) if hasattr(engine, "execute") else engine.begin()
        with context as conn:
            infra_repo = InfrastructureRepository(conn)
            if not infra_repo.claim_outbox_event(event_id=event_id, worker_id=worker_id):
                return CapabilitySelectionConsumeResult(
                    event_id=event_id,
                    snapshot_id="",
                    selection_id="",
                    inbox_first_seen=False,
                    outbox_status="not_claimed",
                )
            record = infra_repo.load_claimed_outbox_event(event_id=event_id, worker_id=worker_id)
            payload = dict(record.payload)
            if (
                record.topic != CAPABILITY_SELECTION_TOPIC
                or payload.get("consumer_module") != "Agent Core"
            ):
                raise ValueError("outbox event is not an Agent Core capability selection")
            tenant_id = str(record.tenant_id)
            receipt = infra_repo.record_inbox_receipt(
                consumer=CAPABILITY_SELECTION_CONSUMER,
                message_id=record.event_id,
                payload=payload,
                tenant_id=tenant_id,
                ordering_key=record.ordering_key,
                ordering_sequence=record.ordering_sequence,
            )
            if receipt.first_seen:
                infra_repo.mark_inbox_processed(
                    tenant_id=tenant_id,
                    consumer=CAPABILITY_SELECTION_CONSUMER,
                    message_id=record.event_id,
                )
            infra_repo.complete_outbox(event_id=record.event_id, worker_id=worker_id)
        return CapabilitySelectionConsumeResult(
            event_id=event_id,
            snapshot_id=str(payload.get("snapshot_id") or ""),
            selection_id=str(payload.get("selection_id") or ""),
            inbox_first_seen=receipt.first_seen,
            outbox_status="published",
        )


__all__ = [
    "CapabilitySelectionConsumeResult",
    "CapabilityService",
    "CapabilityTransitionConsumeResult",
]
