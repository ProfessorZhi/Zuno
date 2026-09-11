from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys
from typing import Any
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
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; Effect PostgreSQL probe is BLOCKED")

    base_url = make_url(raw_url)
    database_name = f"zuno_receipt_failure_probe_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "receipt-failure-probe-config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "database": {
                    "sync_endpoint": database_url.render_as_string(hide_password=False),
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ZUNO_CONFIG", str(config_path))

    # Formal Alembic env.py still imports the retired `zuno.settings` path.
    # Keep that independent blocker out of this test-only Effect probe.
    previous_legacy_settings = sys.modules.get("zuno.settings")
    sys.modules["zuno.settings"] = platform_settings
    try:
        command.upgrade(Config(str(REPO_ROOT / "infra/db/alembic.ini")), "head")
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


class _FailEffectReceiptRepository:
    def __init__(self, delegate: Any) -> None:
        self._delegate = delegate

    def record_effect_receipt(self, receipt: Any) -> None:
        raise RuntimeError("injected local EffectReceipt persistence failure after remote success")

    def __getattr__(self, name: str) -> Any:
        return getattr(self._delegate, name)


class _FailEffectReceiptUnitOfWork(ToolUnitOfWork):
    def __enter__(self) -> _FailEffectReceiptRepository:
        return _FailEffectReceiptRepository(super().__enter__())


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Effect PostgreSQL probe is BLOCKED",
)
def test_remote_success_with_local_effect_receipt_failure_becomes_unknown_and_reconcile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Remote success plus local receipt failure must not be reported as confirmed completion."""

    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-receipt-failure"
    call_id = "remote-success-local-receipt-failure-1"
    secret_ref = "credref://workspace-receipt-failure/mail"
    calls: list[dict[str, object]] = []

    try:
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:v1",
                audience="tool:mail.send",
                owner_principal_id="workspace-user:workspace-receipt-failure",
                scope={"tool": "mail.send", "workspace_id": "workspace-receipt-failure"},
            )

        gateway = ToolInvocationGateway(
            unit_of_work_factory=lambda: _FailEffectReceiptUnitOfWork(engine),
            security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
            infrastructure_unit_of_work_factory=lambda requested_tenant: InfrastructureUnitOfWork(
                engine,
                tenant_id=requested_tenant,
            ),
        )

        async def remote_success() -> dict[str, str]:
            calls.append({"provider_called": True})
            return {
                "provider_effect_id": "provider-effect:mail:remote-success:1",
                "status": "success",
                "message_id": "remote-message:1",
            }

        result, receipt = asyncio.run(
            gateway.invoke_readonly(
                tool_name="mail.send",
                args={
                    "to": "reviewer@example.com",
                    "body": "approved update",
                    "secret_ref": secret_ref,
                },
                tenant_id=tenant_id,
                workspace_id="workspace-receipt-failure",
                trace_id="trace-receipt-failure",
                call_id=call_id,
                adapter_kind="API",
                executor=remote_success,
                readonly=False,
                approval=ToolApprovalBinding(
                    decision_ref="security-decision:receipt-failure-approved",
                    adapter_ref="test.approval",
                ),
            )
        )

        assert len(calls) == 1
        assert result is None
        assert receipt.status == "reconcile_required"
        assert receipt.blocked_reason == "UNKNOWN_EFFECT_RECONCILIATION_REQUIRED"

        attempt_id = f"tool-attempt:{call_id}"
        execution_receipt_id = f"tool-execution-receipt:{call_id}"
        reconciliation_id = f"tool-effect-reconciliation:{call_id}"
        prepared_id = f"prepared-tool-action:{call_id}"

        with engine.connect() as connection:
            attempt = connection.execute(
                text(
                    "SELECT status, dispatch_certainty FROM tool_attempts "
                    "WHERE attempt_id = :attempt_id"
                ),
                {"attempt_id": attempt_id},
            ).mappings().one()
            execution_receipt = connection.execute(
                text(
                    "SELECT status, dispatch_certainty, effect_certainty "
                    "FROM tool_execution_receipts WHERE receipt_id = :receipt_id"
                ),
                {"receipt_id": execution_receipt_id},
            ).mappings().one()
            effect_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_effect_receipts "
                    "WHERE prepared_tool_action_id = :prepared_id"
                ),
                {"prepared_id": prepared_id},
            ).scalar_one()
            reconciliation = connection.execute(
                text(
                    "SELECT status, next_action, provider_effect_id "
                    "FROM tool_effect_reconciliations "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).mappings().one()

        assert attempt == {"status": "UNKNOWN", "dispatch_certainty": "DISPATCHED"}
        assert execution_receipt == {
            "status": "UNKNOWN",
            "dispatch_certainty": "DISPATCHED",
            "effect_certainty": "UNKNOWN_EFFECT",
        }
        assert effect_count == 0
        assert reconciliation == {
            "status": "OPEN",
            "next_action": "RECONCILE",
            "provider_effect_id": "provider-effect:mail:remote-success:1",
        }
    finally:
        _drop_database(engine, admin_engine, database_name)
