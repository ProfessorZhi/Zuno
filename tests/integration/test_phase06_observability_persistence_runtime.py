from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.observability.persistence import ObservabilityPersistenceError, ObservabilityUnitOfWork

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
    assert audit.audit_hash
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM observability_ingest_envelopes")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_traces")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_spans")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_runtime_events")).scalar_one() == 2
        assert conn.execute(text("SELECT count(*) FROM observability_audit_records")).scalar_one() == 1
        watermark = conn.execute(
            text("SELECT contiguous_sequence, max_seen_sequence, freshness_status FROM observability_projection_watermarks")
        ).one()
        assert watermark.contiguous_sequence == 1
        assert watermark.max_seen_sequence == 3
        assert watermark.freshness_status == "gap"
        assert conn.execute(text("SELECT count(*) FROM observability_gaps")).scalar_one() == 1
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

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM observability_runtime_events")).scalar_one() == 1
        dead_letter = conn.execute(
            text("SELECT reason_code FROM observability_dead_letters")
        ).scalar_one()
        assert dead_letter == "duplicate_sequence_payload_mismatch"


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
