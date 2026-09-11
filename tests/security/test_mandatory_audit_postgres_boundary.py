from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys
from uuid import uuid4

import pytest
import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

from zuno.capability.tool_runtime import ToolApprovalBinding, ToolInvocationGateway
from zuno.platform import settings as platform_settings
from zuno.platform.database.foundation import InfrastructureUnitOfWork
from zuno.platform.database.tool_runtime import ToolUnitOfWork
from zuno.platform.security import SecurityUnitOfWork


REPO_ROOT = Path(__file__).resolve().parents[2]


def _migrated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Engine, Engine, str]:
    raw_url = os.environ.get("ZUNO_TEST_DATABASE_URL")
    if not raw_url:
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED")

    base_url = make_url(raw_url)
    database_name = f"zuno_audit_probe_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "audit-probe-config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {"database": {"sync_endpoint": database_url.render_as_string(hide_password=False)}}
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ZUNO_CONFIG", str(config_path))

    alembic_config = Config(str(REPO_ROOT / "infra/db/alembic.ini"))

    # Keep the known formal Alembic `zuno.settings` import drift separate from
    # this diagnostic. The alias is local to the test process and is not a fix.
    previous_legacy_settings = sys.modules.get("zuno.settings")
    sys.modules["zuno.settings"] = platform_settings
    try:
        command.upgrade(alembic_config, "head")
    finally:
        if previous_legacy_settings is None:
            sys.modules.pop("zuno.settings", None)
        else:
            sys.modules["zuno.settings"] = previous_legacy_settings

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


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_external_effect_requires_durable_mandatory_audit_before_dispatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Security audit requirement alone must not authorize the external send."""

    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-audit"
    workspace_id = "workspace-audit"
    trace_id = "trace-mandatory-audit"
    call_id = "effect-mandatory-audit-1"
    secret_ref = "secret-ref:mail:mandatory-audit-test"
    executor_calls: list[str] = []

    try:
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:audit-test",
                audience="tool:mail.send",
                owner_principal_id=f"workspace-user:{workspace_id}",
                scope={"tool": "mail.send", "workspace_id": workspace_id},
            )

        gateway = ToolInvocationGateway(
            unit_of_work_factory=lambda: ToolUnitOfWork(engine),
            security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
            infrastructure_unit_of_work_factory=lambda requested_tenant: InfrastructureUnitOfWork(
                engine,
                tenant_id=requested_tenant,
            ),
        )

        async def executor() -> dict[str, str]:
            executor_calls.append("sent")
            return {"message_id": "remote-message:audit-gap:1"}

        result, receipt = asyncio.run(
            gateway.invoke_readonly(
                tool_name="mail.send",
                args={
                    "to": "reviewer@example.com",
                    "body": "must be durably audited before send",
                    "secret_ref": secret_ref,
                },
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                trace_id=trace_id,
                call_id=call_id,
                adapter_kind="API",
                executor=executor,
                readonly=False,
                approval=ToolApprovalBinding(
                    decision_ref="security-decision:mandatory-audit-approved",
                    adapter_ref="test.approval",
                    comment="approved, but no durable audit receipt was created",
                ),
            )
        )

        prepared_id = f"prepared-tool-action:{call_id}"
        with engine.connect() as connection:
            security_requirement_count = connection.execute(
                text(
                    "SELECT count(*) FROM security_audit_requirements "
                    "WHERE audit_requirement_id = :requirement_id"
                ),
                {"requirement_id": f"audit-requirement:{call_id}:tool-execute"},
            ).scalar_one()
            durable_audit_count = connection.execute(
                text(
                    "SELECT count(*) FROM infra_mandatory_audit_events "
                    "WHERE effect_id = :effect_id"
                ),
                {"effect_id": prepared_id},
            ).scalar_one()
            effect_receipt_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_effect_receipts "
                    "WHERE prepared_tool_action_id = :prepared_id"
                ),
                {"prepared_id": prepared_id},
            ).scalar_one()
            attempt = connection.execute(
                text(
                    "SELECT status, dispatch_certainty FROM tool_attempts "
                    "WHERE attempt_id = :attempt_id"
                ),
                {"attempt_id": f"tool-attempt:{call_id}"},
            ).mappings().first()

        observed = {
            "gateway_status": receipt.status,
            "result_is_none": result is None,
            "executor_calls": len(executor_calls),
            "security_audit_requirement_count": int(security_requirement_count),
            "durable_audit_receipt_count": int(durable_audit_count),
            "effect_receipt_count": int(effect_receipt_count),
            "attempt_status": None if attempt is None else str(attempt["status"]),
            "attempt_dispatch_certainty": None
            if attempt is None
            else str(attempt["dispatch_certainty"]),
        }

        assert observed == {
            "gateway_status": "blocked",
            "result_is_none": True,
            "executor_calls": 0,
            "security_audit_requirement_count": 1,
            "durable_audit_receipt_count": 0,
            "effect_receipt_count": 0,
            "attempt_status": "FAILED",
            "attempt_dispatch_certainty": "NOT_DISPATCHED",
        }, (
            "MANDATORY_BEFORE_EFFECT requires the Security requirement to be backed by a "
            "durable AuditPersistenceReceipt before provider dispatch"
        )
    finally:
        _drop_database(engine, admin_engine, database_name)
