from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.security.persistence import SecurityPersistenceError, SecurityUnitOfWork

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)
HEX_64 = "a" * 64


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
                    security_outbox_events,
                    security_audit_requirements,
                    security_redaction_decisions,
                    security_secret_leases,
                    security_secret_refs,
                    security_approval_decisions,
                    security_approval_requests,
                    security_authorization_decisions,
                    security_principal_contexts,
                    security_effective_epochs
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def test_security_uow_persists_authorization_approval_and_outbox_in_one_transaction(engine) -> None:
    deadline = datetime.now(tz=UTC) + timedelta(minutes=5)
    with SecurityUnitOfWork(engine) as repo:
        epoch = repo.record_effective_epoch(
            epoch_ref="epoch:security:test",
            tenant_id="tenant-a",
            policy_bundle_ref="policy:bundle:test",
            policy_bundle={"actions": ["tool.prepare"]},
            action_set_version="actions:v1",
            principal_context_hash=HEX_64,
            generation=1,
        )
        context = repo.record_principal_context(
            principal_context_id="principal-context:test",
            tenant_id="tenant-a",
            user_principal_id="user:test",
            agent_principal_id="agent:test",
            task_principal_id="task:test",
            session_principal_id="session:test",
            run_id="run:test",
            epoch_ref=epoch.epoch_ref,
        )
        authorization = repo.record_authorization_decision(
            decision_id="decision:test",
            tenant_id="tenant-a",
            principal_context_id=context.principal_context_id,
            epoch_ref=epoch.epoch_ref,
            resource_ref="tool:filesystem",
            action="tool.prepare",
            decision="REQUIRES_APPROVAL",
            reason_code="side_effect",
            prepared_action_hash=HEX_64,
        )
        approval_request = repo.request_approval(
            approval_request_id="approval-request:test",
            tenant_id="tenant-a",
            decision_id=authorization.decision_id,
            prepared_action_hash=HEX_64,
            requested_by_principal_id="agent:test",
            required_approver_policy_ref="approval-policy:test",
            deadline_at=deadline,
        )
        approval_decision = repo.decide_approval(
            approval_decision_id="approval-decision:test",
            tenant_id="tenant-a",
            approval_request_id=approval_request.approval_request_id,
            approver_principal_id="user:test",
            decision="approved",
        )
        event = repo.enqueue_security_event(
            event_id="security-event:test",
            tenant_id="tenant-a",
            aggregate_id=authorization.decision_id,
            topic="security.approval.decided",
            payload={
                "approval_decision_id": approval_decision.approval_decision_id,
                "decision_hash": approval_decision.decision_hash,
            },
            idempotency_key="security:test:approval",
        )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM security_effective_epochs")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM security_principal_contexts")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM security_authorization_decisions")).scalar_one() == 1
        assert conn.execute(text("SELECT status FROM security_approval_requests")).scalar_one() == "approved"
        assert conn.execute(text("SELECT count(*) FROM security_approval_decisions")).scalar_one() == 1
        row = conn.execute(text("SELECT payload_hash, status FROM security_outbox_events")).one()
        assert row.payload_hash == event.payload_hash
        assert row.status == "pending"


def test_security_uow_rolls_back_and_rejects_secret_material_in_outbox(engine) -> None:
    with pytest.raises(SecurityPersistenceError):
        with SecurityUnitOfWork(engine) as repo:
            repo.enqueue_security_event(
                event_id="security-event:secret",
                tenant_id="tenant-a",
                aggregate_id="decision:secret",
                topic="security.approval.decided",
                payload={"secret_material": "never-store"},
                idempotency_key="security:test:secret",
            )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM security_outbox_events")).scalar_one() == 0
