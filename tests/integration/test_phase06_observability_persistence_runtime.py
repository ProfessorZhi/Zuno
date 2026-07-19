from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.model_gateway import ModelCallRequest, ModelCategory, ModelGateway, MockModelProvider
from zuno.platform.model_roles import ModelRole
from zuno.platform.observability.persistence import (
    ObservabilityPersistenceError,
    ObservabilityUnitOfWork,
    PostgresObservabilityRuntimeAdapter,
)
from zuno.platform.security.governance import SandboxProfile, ToolSecurityGate, ToolSecurityProfile

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)
ROOT_HASH = "0" * 64


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    observability_projection_rebuilds,
                    observability_dead_letters,
                    observability_gaps,
                    observability_projection_watermarks,
                    observability_audit_records,
                    observability_runtime_events,
                    observability_spans,
                    observability_traces,
                    observability_ingest_envelopes
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def test_observability_uow_ingests_trace_event_audit_and_gap(engine) -> None:
    with ObservabilityUnitOfWork(engine) as repo:
        envelope = repo.ingest_envelope(
            envelope_id="envelope:phase06:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            trace_id="trace:phase06",
            schema_ref="TelemetryEnvelopeV1",
            schema_version="1.0",
            producer="agent-runtime",
            scope_ref="task:phase06",
            effective_security_epoch_ref="security-epoch:phase06",
            payload={"kind": "trace", "api_key": "sk-secret"},
        )
        duplicate = repo.ingest_envelope(
            envelope_id="envelope:phase06:dup",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            trace_id="trace:phase06",
            schema_ref="TelemetryEnvelopeV1",
            schema_version="1.0",
            producer="agent-runtime",
            scope_ref="task:phase06",
            effective_security_epoch_ref="security-epoch:phase06",
            payload={"kind": "trace", "api_key": "sk-secret"},
        )
        trace = repo.record_trace(
            trace_id="trace:phase06",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            root_run_id="run:phase06",
        )
        span = repo.record_span(
            span_id="span:phase06:root",
            trace_id=trace.trace_id,
            tenant_id="tenant-a",
            span_kind="tool",
            name="tool.mail.send",
        )
        repo.record_runtime_event(
            event_id="event:phase06:1",
            tenant_id="tenant-a",
            trace_id=trace.trace_id,
            span_id=span.span_id,
            stream_id="stream:phase06",
            sequence=1,
            event_type="tool_call",
            payload={"tool": "mail.send", "password": "raw-secret"},
        )
        repo.record_runtime_event(
            event_id="event:phase06:3",
            tenant_id="tenant-a",
            trace_id=trace.trace_id,
            span_id=span.span_id,
            stream_id="stream:phase06",
            sequence=3,
            event_type="tool_result",
            payload={"status": "completed"},
        )
        freshness_with_gap = repo.projection_freshness(
            tenant_id="tenant-a",
            trace_id=trace.trace_id,
            stream_id="stream:phase06",
        )
        repo.record_runtime_event(
            event_id="event:phase06:2",
            tenant_id="tenant-a",
            trace_id=trace.trace_id,
            span_id=span.span_id,
            stream_id="stream:phase06",
            sequence=2,
            event_type="tool_progress",
            payload={"status": "in_progress"},
        )
        freshness_after_fill = repo.projection_freshness(
            tenant_id="tenant-a",
            trace_id=trace.trace_id,
            stream_id="stream:phase06",
        )
        timeline = repo.trace_timeline(tenant_id="tenant-a", trace_id=trace.trace_id)
        audit = repo.record_audit(
            audit_id="audit:phase06:1",
            tenant_id="tenant-a",
            trace_id=trace.trace_id,
            sequence=1,
            previous_hash=ROOT_HASH,
            payload={"decision": "allow", "secret": "raw-secret"},
        )

    assert envelope.status == "accepted"
    assert duplicate.status == "duplicate"
    assert freshness_with_gap.freshness_status == "gap"
    assert freshness_after_fill.freshness_status == "fresh"
    assert freshness_after_fill.open_gap_count == 0
    assert [event.sequence for event in timeline] == [1, 2, 3]
    assert "raw-secret" not in repr(timeline)
    assert audit.audit_hash
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM observability_ingest_envelopes")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_traces")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_spans")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_runtime_events")).scalar_one() == 3
        assert conn.execute(text("SELECT count(*) FROM observability_audit_records")).scalar_one() == 1
        watermark = conn.execute(
            text("SELECT contiguous_sequence, max_seen_sequence, freshness_status FROM observability_projection_watermarks")
        ).one()
        assert watermark.contiguous_sequence == 3
        assert watermark.max_seen_sequence == 3
        assert watermark.freshness_status == "fresh"
        assert conn.execute(text("SELECT status FROM observability_gaps")).scalar_one() == "filled"
        payloads = conn.execute(
            text(
                """
                SELECT redacted_payload FROM observability_runtime_events
                UNION ALL
                SELECT redacted_payload FROM observability_audit_records
                """
            )
        ).scalars().all()
        assert "raw-secret" not in repr(payloads)


def test_observability_duplicate_sequence_payload_mismatch_dead_letters(engine) -> None:
    with ObservabilityUnitOfWork(engine) as repo:
        repo.record_trace(
            trace_id="trace:mismatch",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            root_run_id="run:mismatch",
        )
        repo.record_runtime_event(
            event_id="event:mismatch:1",
            tenant_id="tenant-a",
            trace_id="trace:mismatch",
            stream_id="stream:mismatch",
            sequence=1,
            event_type="first",
            payload={"value": "one"},
        )
        repo.record_runtime_event(
            event_id="event:mismatch:1b",
            tenant_id="tenant-a",
            trace_id="trace:mismatch",
            stream_id="stream:mismatch",
            sequence=1,
            event_type="second",
            payload={"value": "two"},
        )
        dead_letters = repo.dead_letters(tenant_id="tenant-a")

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM observability_runtime_events")).scalar_one() == 1
        dead_letter = conn.execute(
            text("SELECT reason_code FROM observability_dead_letters")
        ).scalar_one()
        assert dead_letter == "duplicate_sequence_payload_mismatch"
    assert [item.reason_code for item in dead_letters] == ["duplicate_sequence_payload_mismatch"]


def test_observability_ingest_requires_tenant_workspace_trace_boundary(engine) -> None:
    with pytest.raises(ObservabilityPersistenceError):
        with ObservabilityUnitOfWork(engine) as repo:
            repo.ingest_envelope(
                envelope_id="envelope:missing-boundary",
                tenant_id="",
                workspace_id="workspace-a",
                trace_id="trace:missing",
                schema_ref="TelemetryEnvelopeV1",
                schema_version="1.0",
                producer="agent-runtime",
                scope_ref="task:missing",
                effective_security_epoch_ref="security-epoch:missing",
                payload={"kind": "trace"},
            )


def test_observability_runtime_adapter_persists_security_audit_span(engine) -> None:
    adapter = PostgresObservabilityRuntimeAdapter(engine)
    audit = ToolSecurityGate().evaluate(
        profile=ToolSecurityProfile(
            tool_id="mail.send",
            side_effect_level="write_external",
            execution_mode="api",
            approval_required=True,
            sandbox_required=True,
            sandbox_profile=SandboxProfile.NETWORK_LIMITED,
            network_policy="egress_mail_only",
            audit_required=True,
            credential_policy="brokered",
        ),
        model_intent="Send email",
        proposed_args={"to": "hr@example.com", "password": "raw-secret"},
        workspace_id="workspace-adapter",
        trace_id="trace-adapter",
        task_id="task-adapter",
    ).audit_event

    receipt = adapter.record_security_audit(audit, run_id="run-adapter")

    assert receipt.trace_id == "trace-adapter"
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM observability_traces")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_spans")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_runtime_events")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_audit_records")).scalar_one() == 1
        payload = conn.execute(
            text("SELECT redacted_payload FROM observability_runtime_events")
        ).scalar_one()
        assert "raw-secret" not in repr(payload)


def test_observability_runtime_adapter_persists_model_gateway_trace_event(engine) -> None:
    gateway = ModelGateway(
        providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")]
    )
    result = gateway.invoke(
        ModelCallRequest(
            category=ModelCategory.CHAT,
            role=ModelRole.PLANNER,
            run_id="run-model-phase06",
            task_id="task-model-phase06",
            trace_id="trace-model-phase06",
            workspace_id="workspace-model-phase06",
            user_id="user-model-phase06",
            provider_id="primary",
            prompt="Summarize without leaking api_key sk-secret.",
            metadata={"api_key": "sk-secret", "safe": "yes"},
        )
    )
    adapter = PostgresObservabilityRuntimeAdapter(engine)

    receipt = adapter.record_model_gateway_trace_event(
        tenant_id="tenant-model-phase06",
        trace_event=result.trace_event,
    )

    assert receipt.event_id == result.trace_event["event_id"]
    with engine.connect() as conn:
        span = conn.execute(
            text("SELECT span_kind, name, status FROM observability_spans")
        ).one()
        event = conn.execute(
            text("SELECT event_type, redacted_payload FROM observability_runtime_events")
        ).one()
        audit_payload = conn.execute(
            text("SELECT redacted_payload FROM observability_audit_records")
        ).scalar_one()
    assert span.span_kind == "model"
    assert span.name == "model.gateway.model_call_completed"
    assert span.status == "completed"
    assert event.event_type == "model.model_call_completed"
    assert event.redacted_payload["call_id"] == result.call_id
    assert event.redacted_payload["binding"]["role"] == "planner"
    assert {item["kind"] for item in event.redacted_payload["usage_receipts"]} == {
        "ESTIMATE",
        "OBSERVED",
    }
    assert "sk-secret" not in repr(event.redacted_payload)
    assert audit_payload["call_state"] == "SUCCEEDED"
    assert audit_payload["usage_receipt_count"] == 2
