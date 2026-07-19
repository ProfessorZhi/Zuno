from __future__ import annotations

from contextlib import contextmanager

import pytest

from zuno.api.services.product import (
    ObservabilityProjectionQueryService,
    ObservabilityQueryAuthorizationError,
    ObservabilityQueryPrincipal,
)
from zuno.platform.observability import (
    ObservabilityDeadLetterReceipt,
    ObservabilityFreshnessRecord,
    ObservabilityTimelineRecord,
)


class FakeObservabilityRepository:
    def trace_scope(self, *, tenant_id: str, trace_id: str) -> dict[str, str]:
        assert tenant_id == "tenant-a"
        assert trace_id == "trace-a"
        return {"tenant_id": tenant_id, "workspace_id": "workspace-a", "root_run_id": "run-a"}

    def trace_timeline(self, *, tenant_id: str, trace_id: str):
        return (
            ObservabilityTimelineRecord(
                event_id="event-a",
                stream_id="stream-a",
                sequence=1,
                event_type="tool_call",
                redacted_payload={
                    "status": "started",
                    "password": "[REDACTED_SECRET]",
                    "nested": {"api_key": "[REDACTED_SECRET]", "safe": "kept"},
                },
            ),
        )

    def projection_freshness(self, *, tenant_id: str, trace_id: str, stream_id: str):
        return ObservabilityFreshnessRecord(
            trace_id=trace_id,
            stream_id=stream_id,
            contiguous_sequence=1,
            max_seen_sequence=2,
            freshness_status="gap",
            open_gap_count=1,
            dead_letter_count=1,
        )

    def dead_letters(self, *, tenant_id: str):
        return (
            ObservabilityDeadLetterReceipt(
                dead_letter_id="dead-letter-a",
                source_ref="event-b",
                reason_code="duplicate_sequence_payload_mismatch",
                payload_hash="a" * 64,
            ),
        )


@contextmanager
def fake_repository_context():
    yield FakeObservabilityRepository()


def _principal(**overrides):
    values = {
        "principal_id": "user-a",
        "tenant_ids": frozenset({"tenant-a"}),
        "workspace_ids": frozenset({"workspace-a"}),
        "scopes": frozenset({"observability:read"}),
        "is_admin": False,
    }
    values.update(overrides)
    return ObservabilityQueryPrincipal(**values)


def test_observability_query_surface_returns_freshness_without_sensitive_payload() -> None:
    service = ObservabilityProjectionQueryService(repository_context_factory=fake_repository_context)

    result = service.get_trace_projection(
        principal=_principal(),
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        trace_id="trace-a",
        stream_id="stream-a",
    )

    assert result["freshness"] == {
        "stream_id": "stream-a",
        "contiguous_sequence": 1,
        "max_seen_sequence": 2,
        "freshness_status": "gap",
        "open_gap_count": 1,
        "dead_letter_count": 1,
        "complete": False,
    }
    assert result["timeline"][0]["payload"] == {
        "status": "started",
        "nested": {"safe": "kept"},
    }
    assert result["dead_letters"][0]["reason_code"] == "duplicate_sequence_payload_mismatch"


@pytest.mark.parametrize(
    ("principal", "message"),
    [
        (_principal(tenant_ids=frozenset({"tenant-b"})), "tenant is not authorized"),
        (_principal(workspace_ids=frozenset({"workspace-b"})), "workspace is not authorized"),
        (_principal(scopes=frozenset()), "observability read scope is required"),
    ],
)
def test_observability_query_surface_rejects_unauthorized_principal(principal, message) -> None:
    service = ObservabilityProjectionQueryService(repository_context_factory=fake_repository_context)

    with pytest.raises(ObservabilityQueryAuthorizationError, match=message):
        service.get_trace_projection(
            principal=principal,
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            trace_id="trace-a",
            stream_id="stream-a",
        )


def test_observability_query_surface_rejects_trace_workspace_mismatch() -> None:
    service = ObservabilityProjectionQueryService(repository_context_factory=fake_repository_context)

    with pytest.raises(ObservabilityQueryAuthorizationError, match="trace workspace boundary mismatch"):
        service.get_trace_projection(
            principal=_principal(is_admin=True),
            tenant_id="tenant-a",
            workspace_id="workspace-b",
            trace_id="trace-a",
            stream_id="stream-a",
        )
