from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.observability.persistence import (
    ObservabilityPersistenceError,
    ObservabilityUnitOfWork,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
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


def test_duplicate_envelope_payload_mismatch_is_quarantined_and_dead_lettered(engine) -> None:
    with ObservabilityUnitOfWork(engine) as repo:
        accepted = repo.ingest_envelope(
            envelope_id="envelope:fault:duplicate",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            trace_id="trace:fault:duplicate",
            schema_ref="TelemetryEnvelopeV1",
            schema_version="1.0",
            producer="agent-runtime",
            scope_ref="task:fault",
            effective_security_epoch_ref="security-epoch:fault",
            payload={"status": "started"},
        )
        quarantined = repo.ingest_envelope(
            envelope_id="envelope:fault:duplicate",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            trace_id="trace:fault:duplicate",
            schema_ref="TelemetryEnvelopeV1",
            schema_version="1.0",
            producer="agent-runtime",
            scope_ref="task:fault",
            effective_security_epoch_ref="security-epoch:fault",
            payload={"status": "changed"},
        )
        dead_letters = repo.dead_letters(tenant_id="tenant-a")

    assert accepted.status == "accepted"
    assert quarantined.status == "quarantined"
    assert [item.reason_code for item in dead_letters] == ["duplicate_envelope_payload_mismatch"]
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT status, quarantine_reason FROM observability_ingest_envelopes")
        ).one()
        assert row == ("quarantined", "duplicate_envelope_payload_mismatch")


def test_audit_chain_detects_sequence_gap_and_hash_mismatch(engine) -> None:
    with ObservabilityUnitOfWork(engine) as repo:
        repo.record_trace(
            trace_id="trace:fault:audit-gap",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            root_run_id="run:audit-gap",
        )
        audit1 = repo.record_audit(
            audit_id="audit:fault:gap:1",
            tenant_id="tenant-a",
            trace_id="trace:fault:audit-gap",
            sequence=1,
            previous_hash=ROOT_HASH,
            payload={"decision": "allow"},
        )
        repo.record_audit(
            audit_id="audit:fault:gap:3",
            tenant_id="tenant-a",
            trace_id="trace:fault:audit-gap",
            sequence=3,
            previous_hash=audit1.audit_hash,
            payload={"decision": "allow"},
        )
        with pytest.raises(ObservabilityPersistenceError, match="audit sequence gap"):
            repo.verify_audit_chain(tenant_id="tenant-a", trace_id="trace:fault:audit-gap")

    with ObservabilityUnitOfWork(engine) as repo:
        repo.record_trace(
            trace_id="trace:fault:audit-hash",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            root_run_id="run:audit-hash",
        )
        repo.record_audit(
            audit_id="audit:fault:hash:1",
            tenant_id="tenant-a",
            trace_id="trace:fault:audit-hash",
            sequence=1,
            previous_hash=ROOT_HASH,
            payload={"decision": "allow"},
        )
        repo.record_audit(
            audit_id="audit:fault:hash:2",
            tenant_id="tenant-a",
            trace_id="trace:fault:audit-hash",
            sequence=2,
            previous_hash=ROOT_HASH,
            payload={"decision": "allow"},
        )
        with pytest.raises(ObservabilityPersistenceError, match="audit hash mismatch"):
            repo.verify_audit_chain(tenant_id="tenant-a", trace_id="trace:fault:audit-hash")


def test_projection_rebuild_rejects_stale_projector_late_commit(engine) -> None:
    with ObservabilityUnitOfWork(engine) as repo:
        claim = repo.claim_projection_rebuild(
            rebuild_id="rebuild:fault",
            tenant_id="tenant-a",
            projection_id="runtime-events",
            claim_owner="projector-a",
            fencing_token="token-current",
            replay_from_sequence=0,
        )
        assert claim.status == "claimed"
        with pytest.raises(ObservabilityPersistenceError, match="stale projector late commit"):
            repo.complete_projection_rebuild(
                rebuild_id="rebuild:fault",
                tenant_id="tenant-a",
                fencing_token="token-stale",
            )
        completed = repo.complete_projection_rebuild(
            rebuild_id="rebuild:fault",
            tenant_id="tenant-a",
            fencing_token="token-current",
        )

    assert completed.status == "completed"
    with engine.connect() as conn:
        assert conn.execute(text("SELECT status FROM observability_projection_rebuilds")).scalar_one() == "completed"
        assert conn.execute(text("SELECT reason_code FROM observability_dead_letters")).scalar_one() == "stale_projector_late_commit"
