from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.capability.runtime import ToolRuntimeRequest, build_default_tool_control_plane_runtime
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.security.persistence import (
    PostgresSecurityApprovalFactSink,
    SecurityPersistenceError,
    SecurityUnitOfWork,
)

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


def test_tool_runtime_security_approval_sink_persists_before_effect(engine) -> None:
    runtime = build_default_tool_control_plane_runtime(
        security_approval_sink=PostgresSecurityApprovalFactSink(engine)
    )

    pending = runtime.execute(
        ToolRuntimeRequest(
            tool_id="mail.send",
            arguments={
                "to": "hr@example.com",
                "body": "Candidate update",
                "smtp_password": "raw-secret",
            },
            workspace_id="workspace_phase05",
            user_id="user_phase05",
            task_id="task_phase05_mail",
            trace_id="trace_phase05_mail",
            model_intent="Send a candidate update email.",
            approval_id="approval_phase05_mail",
            tool_request_id="toolreq_phase05_mail",
            execution_id="toolclaim_phase05_mail",
        )
    )

    assert pending.status == "approval_required"

    approved = runtime.execute(
        ToolRuntimeRequest(
            tool_id="mail.send",
            arguments={
                "to": "hr@example.com",
                "body": "Candidate update",
                "smtp_password": "raw-secret",
            },
            workspace_id="workspace_phase05",
            user_id="user_phase05",
            task_id="task_phase05_mail",
            trace_id="trace_phase05_mail",
            model_intent="Send a candidate update email.",
            approved=True,
            approval_comment="Approved.",
            approval_id="approval_phase05_mail",
            tool_request_id="toolreq_phase05_mail",
            execution_id="toolclaim_phase05_mail",
        )
    )

    assert approved.status == "completed"
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM security_effective_epochs")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM security_principal_contexts")).scalar_one() == 1
        assert conn.execute(text("SELECT decision FROM security_authorization_decisions")).scalar_one() == "REQUIRES_APPROVAL"
        assert conn.execute(text("SELECT status FROM security_approval_requests")).scalar_one() == "approved"
        assert conn.execute(text("SELECT count(*) FROM security_approval_decisions")).scalar_one() == 1
        topics = conn.execute(
            text("SELECT topic FROM security_outbox_events ORDER BY topic")
        ).scalars().all()
        assert topics == [
            "security.tool_approval.approval_waiting",
            "security.tool_approval.approved_before_effect",
        ]
        payloads = conn.execute(text("SELECT payload FROM security_outbox_events")).scalars().all()
        assert "raw-secret" not in repr(payloads)
