from __future__ import annotations

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
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; Secret PostgreSQL probe is BLOCKED")

    base_url = make_url(raw_url)
    database_name = f"zuno_secret_probe_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "secret-probe-config.yaml"
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

    # Current infra/db/alembic/env.py still imports the retired `zuno.settings`
    # path. Keep that formal entrypoint defect separate from this test-only
    # send-boundary probe by supplying a process-local compatibility alias.
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


class _RevokeSecretBeforeLeaseGateway(ToolInvocationGateway):
    def __init__(self, *, engine: Engine) -> None:
        self._probe_engine = engine
        super().__init__(
            unit_of_work_factory=lambda: ToolUnitOfWork(engine),
            security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
            infrastructure_unit_of_work_factory=lambda tenant_id: InfrastructureUnitOfWork(
                engine,
                tenant_id=tenant_id,
            ),
        )

    def _issue_secret_lease(
        self,
        *,
        tenant_id: str,
        call_id: str,
        tool_name: str,
        secret_ref: str,
    ) -> str:
        # Fault injection point: prepare + approval + current-epoch reauth have
        # already succeeded. Revoke the exact credential immediately before the
        # real Gateway issues/validates the short-lived lease used for dispatch.
        with self._probe_engine.begin() as connection:
            result = connection.execute(
                text(
                    "UPDATE security_secret_refs SET status = 'revoked' "
                    "WHERE tenant_id = :tenant_id AND secret_ref = :secret_ref"
                ),
                {"tenant_id": tenant_id, "secret_ref": secret_ref},
            )
            assert result.rowcount == 1
        return super()._issue_secret_lease(
            tenant_id=tenant_id,
            call_id=call_id,
            tool_name=tool_name,
            secret_ref=secret_ref,
        )


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Secret PostgreSQL probe is BLOCKED",
)
def test_revoked_secret_before_lease_blocks_external_dispatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A credential revoked after approval but before send must fail closed."""

    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-secret"
    secret_ref = "credref://workspace-secret/mail"
    call_id = "secret-revocation-before-send-1"
    calls: list[dict[str, object]] = []

    try:
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:v1",
                audience="tool:mail.send",
                owner_principal_id="workspace-user:workspace-secret",
                scope={"tool": "mail.send", "workspace_id": "workspace-secret"},
            )

        gateway = _RevokeSecretBeforeLeaseGateway(engine=engine)

        async def executor() -> dict[str, str]:
            calls.append({"dispatched": True})
            return {"provider_effect_id": "provider-effect:unexpected"}

        result, receipt = __import__("asyncio").run(
            gateway.invoke_readonly(
                tool_name="mail.send",
                args={
                    "to": "reviewer@example.com",
                    "body": "approved update",
                    "secret_ref": secret_ref,
                },
                tenant_id=tenant_id,
                workspace_id="workspace-secret",
                trace_id="trace-secret",
                call_id=call_id,
                adapter_kind="API",
                executor=executor,
                readonly=False,
                approval=ToolApprovalBinding(
                    decision_ref="security-decision:secret-approved",
                    adapter_ref="test.approval",
                ),
            )
        )

        assert result is None
        assert receipt.status == "blocked"
        assert "revoked secret" in receipt.blocked_reason
        assert calls == []

        attempt_id = f"tool-attempt:{call_id}"
        execution_receipt_id = f"tool-execution-receipt:{call_id}"
        prepared_id = f"prepared-tool-action:{call_id}"

        with engine.connect() as connection:
            secret_status = connection.execute(
                text(
                    "SELECT status FROM security_secret_refs "
                    "WHERE tenant_id = :tenant_id AND secret_ref = :secret_ref"
                ),
                {"tenant_id": tenant_id, "secret_ref": secret_ref},
            ).scalar_one()
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
            reconciliation_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_effect_reconciliations "
                    "WHERE prepared_tool_action_id = :prepared_id"
                ),
                {"prepared_id": prepared_id},
            ).scalar_one()
            lease_count = connection.execute(
                text(
                    "SELECT count(*) FROM security_secret_leases "
                    "WHERE tenant_id = :tenant_id AND secret_ref = :secret_ref"
                ),
                {"tenant_id": tenant_id, "secret_ref": secret_ref},
            ).scalar_one()

        assert secret_status == "revoked"
        assert attempt == {"status": "FAILED", "dispatch_certainty": "NOT_DISPATCHED"}
        assert execution_receipt == {
            "status": "FAILED",
            "dispatch_certainty": "NOT_DISPATCHED",
            "effect_certainty": "NO_EFFECT",
        }
        assert effect_count == 0
        assert reconciliation_count == 0
        assert lease_count == 0
    finally:
        _drop_database(engine, admin_engine, database_name)
