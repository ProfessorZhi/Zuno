from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.security.persistence import SecurityPersistenceError, SecurityUnitOfWork


REPO_ROOT = Path(__file__).resolve().parents[3]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)
HASH_A = "a" * 64
HASH_B = "b" * 64


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


def test_pre_effect_gate_rejects_stale_epoch_argument_change_and_expired_approval(engine) -> None:
    expired_deadline = datetime.now(tz=UTC) - timedelta(seconds=1)
    with SecurityUnitOfWork(engine) as repo:
        epoch = repo.record_effective_epoch(
            epoch_ref="epoch:fault:stale",
            tenant_id="tenant-a",
            policy_bundle_ref="policy:fault",
            policy_bundle={"grant": "mail.send"},
            action_set_version="actions:v1",
            principal_context_hash=HASH_A,
            generation=1,
        )
        context = repo.record_principal_context(
            principal_context_id="principal:fault",
            tenant_id="tenant-a",
            user_principal_id="user:fault",
            epoch_ref=epoch.epoch_ref,
        )
        authorization = repo.record_authorization_decision(
            decision_id="decision:fault",
            tenant_id="tenant-a",
            principal_context_id=context.principal_context_id,
            epoch_ref=epoch.epoch_ref,
            resource_ref="tool:mail.send",
            action="tool.execute",
            decision="REQUIRES_APPROVAL",
            reason_code="side_effect",
            prepared_action_hash=HASH_A,
        )
        approval = repo.request_approval(
            approval_request_id="approval:fault",
            tenant_id="tenant-a",
            decision_id=authorization.decision_id,
            prepared_action_hash=HASH_A,
            requested_by_principal_id="agent:fault",
            required_approver_policy_ref="approval-policy:fault",
            deadline_at=expired_deadline,
        )
        repo.decide_approval(
            approval_decision_id="approval-decision:fault",
            tenant_id="tenant-a",
            approval_request_id=approval.approval_request_id,
            approver_principal_id="user:fault",
            decision="approved",
        )

        with pytest.raises(SecurityPersistenceError, match="prepared action hash changed"):
            repo.validate_pre_effect_authorization(
                decision_id=authorization.decision_id,
                tenant_id="tenant-a",
                prepared_action_hash=HASH_B,
            )
        with pytest.raises(SecurityPersistenceError, match="approval deadline expired"):
            repo.validate_pre_effect_authorization(
                decision_id=authorization.decision_id,
                tenant_id="tenant-a",
                prepared_action_hash=HASH_A,
            )

    with engine.begin() as conn:
        conn.execute(
            text("UPDATE security_effective_epochs SET status = 'revoked' WHERE epoch_ref = 'epoch:fault:stale'")
        )

    with pytest.raises(SecurityPersistenceError, match="stale security epoch"):
        with SecurityUnitOfWork(engine) as repo:
            repo.validate_pre_effect_authorization(
                decision_id="decision:fault",
                tenant_id="tenant-a",
                prepared_action_hash=HASH_A,
                now=datetime.now(tz=UTC) - timedelta(minutes=10),
            )


def test_secret_lease_rejects_wrong_audience_expiry_and_revoked_secret(engine) -> None:
    with SecurityUnitOfWork(engine) as repo:
        secret = repo.record_secret_ref(
            secret_ref="secret:fault:mail",
            tenant_id="tenant-a",
            credential_version_ref="credential-version:mail:v1",
            audience="tool:mail.send",
            owner_principal_id="user:fault",
            scope={"actions": ["mail.send"], "workspace_id": "workspace-a"},
        )
        lease = repo.issue_secret_lease(
            lease_id="lease:fault:mail",
            tenant_id="tenant-a",
            secret_ref=secret.secret_ref,
            workload_identity_ref="workload:tool-runtime",
            on_behalf_of_binding_ref="obo:user:fault",
            audience="tool:mail.send",
            lease_generation=1,
            expires_at=datetime.now(tz=UTC) + timedelta(minutes=5),
        )
        assert repo.validate_secret_lease(
            lease_id=lease.lease_id,
            tenant_id="tenant-a",
            audience="tool:mail.send",
        ).lease_hash == lease.lease_hash
        with pytest.raises(SecurityPersistenceError, match="audience mismatch"):
            repo.validate_secret_lease(
                lease_id=lease.lease_id,
                tenant_id="tenant-a",
                audience="tool:other",
            )
        with pytest.raises(SecurityPersistenceError, match="expired"):
            repo.validate_secret_lease(
                lease_id=lease.lease_id,
                tenant_id="tenant-a",
                audience="tool:mail.send",
                now=datetime.now(tz=UTC) + timedelta(minutes=10),
            )

    with engine.begin() as conn:
        conn.execute(text("UPDATE security_secret_refs SET status = 'revoked' WHERE secret_ref = 'secret:fault:mail'"))

    with pytest.raises(SecurityPersistenceError, match="revoked secret"):
        with SecurityUnitOfWork(engine) as repo:
            repo.validate_secret_lease(
                lease_id="lease:fault:mail",
                tenant_id="tenant-a",
                audience="tool:mail.send",
            )


def test_redaction_failure_records_block_decision_without_secret_payload(engine) -> None:
    with SecurityUnitOfWork(engine) as repo:
        decision = repo.record_redaction_decision(
            redaction_id="redaction:fault",
            tenant_id="tenant-a",
            source_ref="trace:raw-output",
            sink_ref="external:sink",
            trust_label="confidential",
            requested_decision="allow",
            redaction_policy_ref="redaction-policy:fault",
            redacted_payload={"body": "[REDACTED_SECRET]"},
            redaction_succeeded=False,
        )
        assert decision.decision == "block"

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT decision, length(redacted_payload_hash), length(decision_hash) FROM security_redaction_decisions")
        ).one()
        assert row == ("block", 64, 64)
