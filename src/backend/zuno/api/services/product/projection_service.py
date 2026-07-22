from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine

from zuno.platform.observability import ObservabilityUnitOfWork


class ObservabilityQueryAuthorizationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ObservabilityQueryPrincipal:
    principal_id: str
    tenant_ids: frozenset[str]
    workspace_ids: frozenset[str]
    scopes: frozenset[str]
    is_admin: bool = False


RepositoryContextFactory = Callable[[], AbstractContextManager[Any]]

FORBIDDEN_PAYLOAD_KEYS = {
    "prompt",
    "raw_prompt",
    "hidden_reasoning",
    "chain_of_thought",
    "secret",
    "secret_material",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "password",
    "raw_tool_args",
}


class ObservabilityProjectionQueryService:
    def __init__(
        self,
        *,
        engine: Engine | None = None,
        repository_context_factory: RepositoryContextFactory | None = None,
    ) -> None:
        if engine is None and repository_context_factory is None:
            raise ValueError("engine or repository_context_factory is required")
        self.engine = engine
        self.repository_context_factory = repository_context_factory

    def get_trace_projection(
        self,
        *,
        principal: ObservabilityQueryPrincipal,
        tenant_id: str,
        workspace_id: str,
        trace_id: str,
        stream_id: str,
    ) -> dict[str, Any]:
        self._authorize(principal=principal, tenant_id=tenant_id, workspace_id=workspace_id)
        with self._repository() as repo:
            trace_scope = repo.trace_scope(tenant_id=tenant_id, trace_id=trace_id)
            if trace_scope["workspace_id"] != workspace_id:
                raise ObservabilityQueryAuthorizationError("trace workspace boundary mismatch")
            timeline = repo.trace_timeline(tenant_id=tenant_id, trace_id=trace_id)
            freshness = repo.projection_freshness(
                tenant_id=tenant_id,
                trace_id=trace_id,
                stream_id=stream_id,
            )
            dead_letters = repo.dead_letters(tenant_id=tenant_id)
        return {
            "trace_id": trace_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "freshness": {
                "stream_id": freshness.stream_id,
                "contiguous_sequence": freshness.contiguous_sequence,
                "max_seen_sequence": freshness.max_seen_sequence,
                "freshness_status": freshness.freshness_status,
                "open_gap_count": freshness.open_gap_count,
                "dead_letter_count": freshness.dead_letter_count,
                "complete": freshness.freshness_status == "fresh"
                and freshness.open_gap_count == 0,
            },
            "timeline": [
                {
                    "event_id": event.event_id,
                    "stream_id": event.stream_id,
                    "sequence": event.sequence,
                    "event_type": event.event_type,
                    "payload": _public_payload(event.redacted_payload),
                }
                for event in timeline
            ],
            "dead_letters": [
                {
                    "dead_letter_id": item.dead_letter_id,
                    "source_ref": item.source_ref,
                    "reason_code": item.reason_code,
                    "payload_hash": item.payload_hash,
                }
                for item in dead_letters
            ],
        }

    def _repository(self) -> AbstractContextManager[Any]:
        if self.repository_context_factory is not None:
            return self.repository_context_factory()
        assert self.engine is not None
        return ObservabilityUnitOfWork(self.engine)

    def _authorize(
        self,
        *,
        principal: ObservabilityQueryPrincipal,
        tenant_id: str,
        workspace_id: str,
    ) -> None:
        if principal.is_admin:
            return
        if tenant_id not in principal.tenant_ids:
            raise ObservabilityQueryAuthorizationError("tenant is not authorized")
        if workspace_id not in principal.workspace_ids:
            raise ObservabilityQueryAuthorizationError("workspace is not authorized")
        if not (
            "observability:read" in principal.scopes
            or f"observability:read:{workspace_id}" in principal.scopes
        ):
            raise ObservabilityQueryAuthorizationError("observability read scope is required")


def _public_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        public: dict[str, Any] = {}
        for key, value in payload.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_PAYLOAD_KEYS:
                continue
            public[key] = _public_payload(value)
        return public
    if isinstance(payload, list):
        return [_public_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(_public_payload(item) for item in payload)
    return payload
