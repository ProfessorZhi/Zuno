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
from zuno.platform.database.foundation import InfrastructureConflictError, InfrastructureUnitOfWork
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


def _configure_audit_channel(engine: Engine, *, tenant_id: str, capacity_limit: int = 100) -> None:
    with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
        repo.configure_audit_channel(
            channel_id="audit-channel:tool-runtime:phase16",
            capacity_limit=capacity_limit,
            owner_id="security-governance:test-bootstrap",
        )


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
                    "WHERE payload->>'prepared_tool_action_id' = :prepared_id"
                ),
                {"prepared_id": prepared_id},
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


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_matching_durable_audit_allows_external_dispatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-audit-allowed"
    workspace_id = "workspace-audit-allowed"
    trace_id = "trace-mandatory-audit-allowed"
    call_id = "effect-mandatory-audit-allowed-1"
    secret_ref = "secret-ref:mail:mandatory-audit-allowed"
    executor_calls: list[str] = []
    try:
        _configure_audit_channel(engine, tenant_id=tenant_id)
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:audit-allowed",
                audience="tool:mail.send",
                owner_principal_id=f"workspace-user:{workspace_id}",
                scope={"tool": "mail.send", "workspace_id": workspace_id},
            )
        gateway = ToolInvocationGateway(
            unit_of_work_factory=lambda: ToolUnitOfWork(engine),
            security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
            infrastructure_unit_of_work_factory=lambda requested_tenant: InfrastructureUnitOfWork(
                engine, tenant_id=requested_tenant
            ),
        )

        async def executor() -> dict[str, str]:
            executor_calls.append("sent")
            return {"message_id": "remote-message:audit-allowed:1"}

        result, receipt = asyncio.run(
            gateway.invoke_readonly(
                tool_name="mail.send",
                args={"to": "reviewer@example.com", "body": "audited send", "secret_ref": secret_ref},
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
                    comment="approved",
                ),
            )
        )
        prepared_id = f"prepared-tool-action:{call_id}"
        assert receipt.status == "completed"
        assert result is not None
        assert executor_calls == ["sent"]
        with engine.connect() as connection:
            action_hash = connection.execute(
                text("SELECT prepared_action_hash FROM prepared_tool_actions WHERE prepared_tool_action_id = :id"),
                {"id": prepared_id},
            ).scalar_one()
            audit = connection.execute(
                text(
                    "SELECT audit_id, effect_id, owner_id, status, payload "
                    "FROM infra_mandatory_audit_events "
                    "WHERE payload->>'prepared_tool_action_id' = :prepared_id"
                ),
                {"prepared_id": prepared_id},
            ).mappings().one()
            effect_count = connection.execute(
                text("SELECT count(*) FROM tool_effect_receipts WHERE prepared_tool_action_id = :id"),
                {"id": prepared_id},
            ).scalar_one()
        assert audit["status"] == "effect_observed"
        assert audit["owner_id"] == f"tool-runtime:{call_id}"
        assert audit["payload"]["prepared_action_hash"] == action_hash
        assert audit["payload"]["security_epoch_ref"] == f"security-epoch:{trace_id}"
        assert int(effect_count) == 1
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_observed_effect_releases_mandatory_audit_capacity_for_next_send(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-audit-capacity"
    workspace_id = "workspace-audit-capacity"
    secret_ref = "secret-ref:mail:mandatory-audit-capacity"
    executor_calls: list[str] = []
    try:
        _configure_audit_channel(engine, tenant_id=tenant_id, capacity_limit=1)
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:audit-capacity",
                audience="tool:mail.send",
                owner_principal_id=f"workspace-user:{workspace_id}",
                scope={"tool": "mail.send", "workspace_id": workspace_id},
            )
        gateway = ToolInvocationGateway(
            unit_of_work_factory=lambda: ToolUnitOfWork(engine),
            security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
            infrastructure_unit_of_work_factory=lambda requested_tenant: InfrastructureUnitOfWork(
                engine, tenant_id=requested_tenant
            ),
        )

        async def executor() -> dict[str, str]:
            executor_calls.append("sent")
            return {"message_id": f"remote-message:audit-capacity:{len(executor_calls)}"}

        for sequence in (1, 2):
            _, receipt = asyncio.run(
                gateway.invoke_readonly(
                    tool_name="mail.send",
                    args={"to": f"reviewer-{sequence}@example.com", "body": f"audited send {sequence}", "secret_ref": secret_ref},
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    trace_id=f"trace-mandatory-audit-capacity-{sequence}",
                    call_id=f"effect-mandatory-audit-capacity-{sequence}",
                    adapter_kind="API",
                    executor=executor,
                    readonly=False,
                    approval=ToolApprovalBinding(
                        decision_ref=f"security-decision:audit-capacity-{sequence}",
                        adapter_ref="test.approval",
                        comment="approved",
                    ),
                )
            )
            assert receipt.status == "completed"

        assert executor_calls == ["sent", "sent"]
        with engine.connect() as connection:
            statuses = connection.execute(
                text("SELECT status, count(*) AS count FROM infra_mandatory_audit_events GROUP BY status ORDER BY status")
            ).mappings().all()
        assert statuses == [{"status": "effect_observed", "count": 2}]
    finally:
        _drop_database(engine, admin_engine, database_name)


class _RevokingAfterAuditGateway(ToolInvocationGateway):
    def __init__(self, *, engine: Engine, epoch_ref: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._test_engine = engine
        self._test_epoch_ref = epoch_ref

    def _persist_mandatory_audit_before_effect(self, **kwargs: object) -> str:
        audit_id = super()._persist_mandatory_audit_before_effect(**kwargs)
        with self._test_engine.begin() as connection:
            updated = connection.execute(
                text(
                    "UPDATE security_effective_epochs SET status = 'revoked' "
                    "WHERE epoch_ref = :epoch_ref AND status = 'active'"
                ),
                {"epoch_ref": self._test_epoch_ref},
            ).rowcount
        assert updated == 1, "fault seam must revoke exactly one active SecurityEpoch"
        return audit_id


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_security_epoch_revoked_after_audit_still_blocks_provider_send(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-audit-revoked"
    workspace_id = "workspace-audit-revoked"
    trace_id = "trace-audit-then-revoked"
    epoch_ref = f"security-epoch:{trace_id}"
    call_id = "effect-audit-then-revoked-1"
    secret_ref = "secret-ref:mail:audit-then-revoked"
    executor_calls: list[str] = []
    try:
        _configure_audit_channel(engine, tenant_id=tenant_id)
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:audit-revoked",
                audience="tool:mail.send",
                owner_principal_id=f"workspace-user:{workspace_id}",
                scope={"tool": "mail.send", "workspace_id": workspace_id},
            )
        gateway = _RevokingAfterAuditGateway(
            engine=engine,
            epoch_ref=epoch_ref,
            unit_of_work_factory=lambda: ToolUnitOfWork(engine),
            security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
            infrastructure_unit_of_work_factory=lambda requested_tenant: InfrastructureUnitOfWork(
                engine, tenant_id=requested_tenant
            ),
        )

        async def executor() -> dict[str, str]:
            executor_calls.append("sent")
            return {"message_id": "must-not-be-created"}

        result, receipt = asyncio.run(
            gateway.invoke_readonly(
                tool_name="mail.send",
                args={"to": "reviewer@example.com", "body": "must stop", "secret_ref": secret_ref},
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                trace_id=trace_id,
                call_id=call_id,
                adapter_kind="API",
                executor=executor,
                readonly=False,
                approval=ToolApprovalBinding(
                    decision_ref="security-decision:audit-revocation-approved",
                    adapter_ref="test.approval",
                    comment="approved before post-audit revocation",
                ),
            )
        )
        prepared_id = f"prepared-tool-action:{call_id}"
        assert result is None
        assert receipt.status == "blocked"
        assert "stale security epoch before effect" in receipt.blocked_reason
        assert executor_calls == []
        with engine.connect() as connection:
            audit_count = connection.execute(
                text(
                    "SELECT count(*) FROM infra_mandatory_audit_events "
                    "WHERE payload->>'prepared_tool_action_id' = :prepared_id"
                ),
                {"prepared_id": prepared_id},
            ).scalar_one()
            effect_count = connection.execute(
                text("SELECT count(*) FROM tool_effect_receipts WHERE prepared_tool_action_id = :id"),
                {"id": prepared_id},
            ).scalar_one()
            attempt = connection.execute(
                text("SELECT status, dispatch_certainty FROM tool_attempts WHERE attempt_id = :id"),
                {"id": f"tool-attempt:{call_id}"},
            ).mappings().one()
        assert int(audit_count) == 1
        assert int(effect_count) == 0
        assert attempt == {"status": "FAILED", "dispatch_certainty": "NOT_DISPATCHED"}
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_mandatory_audit_identity_cannot_be_reused_for_different_action_hash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-audit-binding"
    try:
        _configure_audit_channel(engine, tenant_id=tenant_id)
        effect_id = "tool-effect-audit:binding-test"
        owner_id = "tool-runtime:binding-test"
        with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
            first = repo.record_mandatory_audit(
                channel_id="audit-channel:tool-runtime:phase16",
                effect_id=effect_id,
                owner_id=owner_id,
                payload={
                    "prepared_tool_action_id": "prepared-tool-action:binding-test",
                    "prepared_action_hash": "a" * 64,
                },
            )
        with pytest.raises(
            InfrastructureConflictError,
            match="mandatory audit effect identity was reused with different proof content",
        ):
            with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
                repo.record_mandatory_audit(
                    channel_id="audit-channel:tool-runtime:phase16",
                    effect_id=effect_id,
                    owner_id=owner_id,
                    payload={
                        "prepared_tool_action_id": "prepared-tool-action:binding-test",
                        "prepared_action_hash": "b" * 64,
                    },
                )
        with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
            committed = repo.assert_audit_durable_for_effect(
                audit_id=first.audit_id, effect_id=effect_id, owner_id=owner_id
            )
        assert committed.payload_hash == first.payload_hash
    finally:
        _drop_database(engine, admin_engine, database_name)
