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
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; Security PostgreSQL probe is BLOCKED")

    base_url = make_url(raw_url)
    database_name = f"zuno_security_probe_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "security-probe-config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {"database": {"sync_endpoint": database_url.render_as_string(hide_password=False)}}
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ZUNO_CONFIG", str(config_path))

    alembic_config = Config(str(REPO_ROOT / "infra/db/alembic.ini"))

    # The formal Alembic entrypoint currently imports retired `zuno.settings`.
    # Keep that known Current blocker separate from this Security fault probe by
    # providing a process-local compatibility alias only while migrations run.
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


class _RevokingInfrastructureUnitOfWork:
    """Delegate infrastructure work, then revoke the SecurityEpoch before dispatch re-check."""

    def __init__(
        self,
        engine: Engine,
        *,
        tenant_id: str,
        epoch_ref: str,
        state: dict[str, bool],
    ) -> None:
        self._engine = engine
        self._epoch_ref = epoch_ref
        self._state = state
        self._delegate = InfrastructureUnitOfWork(engine, tenant_id=tenant_id)

    def __enter__(self):
        return self._delegate.__enter__()

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self._delegate.__exit__(exc_type, exc, tb)
        if exc_type is not None or self._state["revoked"]:
            return
        with self._engine.begin() as connection:
            updated = connection.execute(
                text(
                    "UPDATE security_effective_epochs "
                    "SET status = 'revoked' "
                    "WHERE epoch_ref = :epoch_ref AND status = 'active'"
                ),
                {"epoch_ref": self._epoch_ref},
            ).rowcount
        assert updated == 1, "test fault seam must revoke the active epoch exactly once"
        self._state["revoked"] = True


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Security PostgreSQL probe is BLOCKED",
)
def test_revoked_security_epoch_blocks_external_dispatch_before_send(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authorization valid at prepare time must not authorize a later send after revocation."""

    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-security"
    workspace_id = "workspace-security"
    trace_id = "trace-security-revoked"
    call_id = "effect-security-revoked-1"
    epoch_ref = f"security-epoch:{trace_id}"
    secret_ref = "secret-ref:mail:security-revocation-test"
    state = {"revoked": False}
    executor_calls: list[str] = []

    try:
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:test",
                audience="tool:mail.send",
                owner_principal_id=f"workspace-user:{workspace_id}",
                scope={"tool": "mail.send", "workspace_id": workspace_id},
            )

        gateway = ToolInvocationGateway(
            unit_of_work_factory=lambda: ToolUnitOfWork(engine),
            security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
            infrastructure_unit_of_work_factory=lambda requested_tenant: _RevokingInfrastructureUnitOfWork(
                engine,
                tenant_id=requested_tenant,
                epoch_ref=epoch_ref,
                state=state,
            ),
        )

        async def executor() -> dict[str, str]:
            executor_calls.append("sent")
            return {"message_id": "remote-message-should-not-exist"}

        result, receipt = asyncio.run(
            gateway.invoke_readonly(
                tool_name="mail.send",
                args={
                    "to": "reviewer@example.com",
                    "body": "approved before revocation",
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
                    decision_ref="security-decision:approved-before-revocation",
                    adapter_ref="test.approval",
                    comment="approved while epoch active",
                ),
            )
        )

        assert state["revoked"] is True
        assert executor_calls == [], "revocation before send must prevent provider dispatch"
        assert result is None
        assert receipt.status == "blocked"
        assert "stale security epoch before effect" in receipt.blocked_reason

        attempt_id = f"tool-attempt:{call_id}"
        execution_receipt_id = f"tool-execution-receipt:{call_id}"
        with engine.connect() as connection:
            epoch_status = connection.execute(
                text(
                    "SELECT status FROM security_effective_epochs "
                    "WHERE epoch_ref = :epoch_ref"
                ),
                {"epoch_ref": epoch_ref},
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
                    "SELECT status, effect_certainty FROM tool_execution_receipts "
                    "WHERE receipt_id = :receipt_id"
                ),
                {"receipt_id": execution_receipt_id},
            ).mappings().one()
            effect_receipt_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_effect_receipts "
                    "WHERE prepared_tool_action_id = :prepared_id"
                ),
                {"prepared_id": f"prepared-tool-action:{call_id}"},
            ).scalar_one()
            reconciliation_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_effect_reconciliations "
                    "WHERE prepared_tool_action_id = :prepared_id"
                ),
                {"prepared_id": f"prepared-tool-action:{call_id}"},
            ).scalar_one()

        assert epoch_status == "revoked"
        assert attempt == {"status": "FAILED", "dispatch_certainty": "NOT_DISPATCHED"}
        assert execution_receipt == {"status": "FAILED", "effect_certainty": "NO_EFFECT"}
        assert effect_receipt_count == 0
        assert reconciliation_count == 0
    finally:
        _drop_database(engine, admin_engine, database_name)
