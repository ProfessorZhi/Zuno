from __future__ import annotations

from contextlib import contextmanager

import pytest

from zuno.api.services.product import (
    ObservabilityEvalQueryService,
    ObservabilityProjectionQueryService,
    ObservabilityQueryAuthorizationError,
    ObservabilityQueryPrincipal,
)
from zuno.platform.observability import (
    EvalRunProjection,
    ObservabilityDeadLetterReceipt,
    ObservabilityFreshnessRecord,
    ObservabilityTimelineRecord,
    ReleaseGateReport,
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


class FakeEvalRepository:
    def eval_run_projection(self, *, tenant_id: str, workspace_id: str, run_id: str):
        assert tenant_id == "tenant-a"
        assert workspace_id == "workspace-a"
        assert run_id == "run-a"
        return EvalRunProjection(
            run_id=run_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            status="COMPLETED",
            result_set_hash="a" * 64,
            projection_freshness="fresh",
            authorization_scope="tenant-a:workspace-a",
            redaction_status="redacted",
            trace_completeness="complete",
            measurement_status="MEASURED",
            case_status_counts={"COMPLETED": 1},
            metric_status_counts={"MEASURED": 5},
            failure_buckets=(),
        )

    def release_gate_report(self, *, tenant_id: str, workspace_id: str, gate_id: str):
        assert tenant_id == "tenant-a"
        assert workspace_id == "workspace-a"
        assert gate_id == "gate-a"
        return ReleaseGateReport(
            gate_id=gate_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            status="PASSED",
            reason="passed",
            result_set_hash="a" * 64,
            comparison_hash="b" * 64,
            comparison_status="PASSED",
            evidence_hash="c" * 64,
            artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
            artifact_hash="d" * 64,
            projection_freshness="fresh",
            measurement_status="MEASURED",
        )

    def comparison_report(self, *, tenant_id: str, workspace_id: str, comparison_hash: str):
        assert tenant_id == "tenant-a"
        assert workspace_id == "workspace-a"
        return type(
            "ComparisonReport",
            (),
            {
                "to_dict": lambda self: {
                    "comparison_hash": comparison_hash,
                    "status": "PASSED",
                    "comparable": True,
                }
            },
        )()

    def evidence_report(self, *, tenant_id: str, workspace_id: str, evidence_id: str):
        assert tenant_id == "tenant-a"
        assert workspace_id == "workspace-a"
        return type(
            "EvidenceReport",
            (),
            {
                "to_dict": lambda self: {
                    "evidence_id": evidence_id,
                    "artifact_hash": "d" * 64,
                }
            },
        )()


@contextmanager
def fake_repository_context():
    yield FakeObservabilityRepository()


@contextmanager
def fake_eval_repository_context():
    yield FakeEvalRepository()


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


def test_eval_query_surface_returns_authorized_run_projection_and_gate_report() -> None:
    service = ObservabilityEvalQueryService(repository_context_factory=fake_eval_repository_context)

    run = service.get_eval_run_projection(
        principal=_principal(scopes=frozenset({"eval:read"})),
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        eval_run_id="run-a",
    )
    gate = service.get_release_gate_report(
        principal=_principal(scopes=frozenset({"eval:read"})),
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        gate_id="gate-a",
    )

    assert run["projection_freshness"] == "fresh"
    assert run["measurement_status"] == "MEASURED"
    assert run["metric_status_counts"] == {"MEASURED": 5}
    assert gate["status"] == "PASSED"
    assert gate["comparison_status"] == "PASSED"


def test_eval_query_surface_returns_metrics_failures_comparison_and_evidence_reports() -> None:
    service = ObservabilityEvalQueryService(repository_context_factory=fake_eval_repository_context)
    principal = _principal(scopes=frozenset({"eval:read"}))

    metrics = service.get_eval_metrics_projection(
        principal=principal,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        eval_run_id="run-a",
    )
    failures = service.get_eval_failures_projection(
        principal=principal,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        eval_run_id="run-a",
    )
    comparison = service.get_comparison_report(
        principal=principal,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        comparison_hash="comparison-a",
    )
    evidence = service.get_evidence_report(
        principal=principal,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        evidence_id="evidence-a",
    )

    assert metrics["metric_status_counts"] == {"MEASURED": 5}
    assert failures["failure_buckets"] == []
    assert comparison["status"] == "PASSED"
    assert evidence["artifact_hash"] == "d" * 64


def test_eval_query_surface_rejects_missing_eval_scope() -> None:
    service = ObservabilityEvalQueryService(repository_context_factory=fake_eval_repository_context)

    with pytest.raises(ObservabilityQueryAuthorizationError, match="eval read scope is required"):
        service.get_eval_run_projection(
            principal=_principal(scopes=frozenset()),
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            eval_run_id="run-a",
        )
