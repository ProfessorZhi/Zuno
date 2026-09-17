from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

from zuno.platform.security import PostgresSecurityApprovalEventSink, SecurityPersistenceError

REPO_ROOT = Path(__file__).resolve().parents[2]


def _migrated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Engine, Engine, str]:
    raw_url = os.environ.get("ZUNO_TEST_DATABASE_URL")
    if not raw_url:
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; PSC-D PostgreSQL probe is BLOCKED")
    base_url = make_url(raw_url)
    database_name = f"zuno_psc_d_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "psc-d-config.yaml"
    config_path.write_text(
        yaml.safe_dump({"database": {"sync_endpoint": database_url.render_as_string(hide_password=False)}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ZUNO_CONFIG", str(config_path))
    command.upgrade(Config(str(REPO_ROOT / "infra/db/alembic.ini")), "head")
    return create_engine(database_url), admin_engine, database_name


def _drop_database(engine: Engine, admin_engine: Engine, database_name: str) -> None:
    engine.dispose()
    with admin_engine.connect() as connection:
        connection.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :database_name AND pid <> pg_backend_pid()"
            ),
            {"database_name": database_name},
        )
        connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
    admin_engine.dispose()


def _fact() -> dict[str, object]:
    return {
        "tenant_id": "tenant-psc-d",
        "workspace_id": "workspace-psc-d",
        "user_id": "user-psc-d",
        "task_id": "task-psc-d",
        "trace_id": "trace-psc-d",
        "tool_id": "mail.send",
        "tool_request_id": "toolreq-psc-d",
        "approval_id": "approval-psc-d",
        "approval_decision_ref": "approval-decision:psc-d",
        "approval_adapter_ref": "test.approval",
        "required_approval": "tool:mail.send",
        "prepared_action_hash": "a" * 64,
        "security_decision": "require_approval",
        "audit_ref": "audit:psc-d",
        "status": "approved_before_effect",
    }


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PSC-D PostgreSQL probe is BLOCKED",
)
def test_product_approval_sink_is_projection_only_and_tenant_scoped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    try:
        sink = PostgresSecurityApprovalEventSink(engine)
        fact = _fact()
        sink.record_tool_approval_fact(fact)
        sink.record_tool_approval_fact(fact)

        with engine.connect() as connection:
            event = connection.execute(
                text(
                    "SELECT tenant_id, aggregate_id, topic, payload FROM security_outbox_events "
                    "WHERE tenant_id = :tenant_id AND idempotency_key = :key"
                ),
                {
                    "tenant_id": fact["tenant_id"],
                    "key": "security-approval:approval-psc-d:approved_before_effect",
                },
            ).mappings().one()
            authority_counts = {
                table: int(connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one())
                for table in (
                    "security_effective_epochs",
                    "security_principal_contexts",
                    "security_authorization_decisions",
                    "security_approval_requests",
                    "security_approval_decisions",
                    "security_audit_requirements",
                )
            }
            event_count = int(
                connection.execute(
                    text("SELECT count(*) FROM security_outbox_events WHERE tenant_id = :tenant_id"),
                    {"tenant_id": fact["tenant_id"]},
                ).scalar_one()
            )

        assert event_count == 1
        assert event["tenant_id"] == "tenant-psc-d"
        assert event["aggregate_id"] == "tool-approval:approval-psc-d"
        assert event["topic"] == "security.tool_approval.approved_before_effect"
        assert event["payload"]["workspace_id"] == "workspace-psc-d"
        assert event["payload"]["prepared_action_hash"] == "a" * 64
        assert authority_counts == {
            "security_effective_epochs": 0,
            "security_principal_contexts": 0,
            "security_authorization_decisions": 0,
            "security_approval_requests": 0,
            "security_approval_decisions": 0,
            "security_audit_requirements": 0,
        }

        changed = dict(fact)
        changed["prepared_action_hash"] = "b" * 64
        with pytest.raises(
            SecurityPersistenceError,
            match="security event idempotency key was reused with different content",
        ):
            sink.record_tool_approval_fact(changed)
    finally:
        _drop_database(engine, admin_engine, database_name)
