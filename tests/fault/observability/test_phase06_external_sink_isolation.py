from __future__ import annotations

import os
import subprocess
from pathlib import Path

from sqlalchemy import text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.observability import PostgresObservabilityRuntimeAdapter, ZunoSpanBuilder, ZunoSpanKind
from zuno.platform.observability.trace_eval import ObservabilityDeliveryState


REPO_ROOT = Path(__file__).resolve().parents[3]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)


def _migrate() -> None:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _engine():
    _migrate()
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
    return engine


def test_external_sink_failure_does_not_rollback_local_observability_facts() -> None:
    engine = _engine()
    adapter = PostgresObservabilityRuntimeAdapter(engine)
    span = ZunoSpanBuilder().build_span(
        trace_id="trace:external-sink",
        session_id="tenant-a",
        thread_id="",
        task_id="task-a",
        turn_id="turn-a",
        run_id="run-a",
        parent_run_id=None,
        run_type="tool",
        span_kind=ZunoSpanKind.TOOL,
        name="tool.mail.send",
        outputs={"status": "completed"},
    )

    def failing_sink(payload):
        assert payload["trace_id"] == "trace:external-sink"
        raise RuntimeError("external sink unavailable")

    try:
        receipt, delivery = adapter.record_span_with_external_sink(
            span,
            sink_id="sink:langsmith",
            idempotency_key="delivery:external-sink",
            deliver=failing_sink,
        )

        assert receipt.trace_id == "trace:external-sink"
        assert delivery.state is ObservabilityDeliveryState.FAILED
        assert delivery.source_success is False

        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM observability_traces")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM observability_spans")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM observability_runtime_events")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM observability_audit_records")).scalar_one() == 1
            dead_letter = conn.execute(
                text("SELECT source_ref, reason_code FROM observability_dead_letters")
            ).one()
            assert dead_letter.reason_code == "external_sink_delivery_failed"
            assert dead_letter.source_ref == "external-sink:sink:langsmith:delivery:external-sink"
    finally:
        engine.dispose()


def test_external_sink_success_still_does_not_claim_source_domain_success() -> None:
    engine = _engine()
    adapter = PostgresObservabilityRuntimeAdapter(engine)
    delivered_payloads: list[dict] = []
    span = ZunoSpanBuilder().build_span(
        trace_id="trace:external-sink-success",
        session_id="tenant-a",
        thread_id="",
        task_id="task-a",
        turn_id="turn-a",
        run_id="run-success",
        parent_run_id=None,
        run_type="tool",
        span_kind=ZunoSpanKind.TOOL,
        name="tool.read",
    )

    try:
        _, delivery = adapter.record_span_with_external_sink(
            span,
            sink_id="sink:langsmith",
            idempotency_key="delivery:success",
            deliver=delivered_payloads.append,
        )

        assert delivered_payloads
        assert delivery.state is ObservabilityDeliveryState.DELIVERED
        assert delivery.source_success is False
        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM observability_dead_letters")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM observability_runtime_events")).scalar_one() == 1
    finally:
        engine.dispose()
