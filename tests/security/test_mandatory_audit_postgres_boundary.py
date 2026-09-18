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
from zuno.platform.database.foundation import (\n    FencingRejectedError,\n    InfrastructureConflictError,\n    InfrastructureUnitOfWork,\n)
from zuno.platform.database.tool_runtime import ToolUnitOfWork
from zuno.platform.security import SecurityPersistenceError, SecurityUnitOfWork


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


def _audit_channel_id(tenant_id: str) -> str:\n    return f"audit-channel:tool-runtime:{tenant_id}"\n\n\ndef _configure_audit_channel(engine: Engine, *, tenant_id: str, capacity_limit: int = 100) -> None:
    with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
        repo.configure_audit_channel(
            channel_id=_audit_channel_id(tenant_id),
            capacity_limit=capacity_limit,
            owner_id="security-governance:test-bootstrap",
        )


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_security_audit_requirement_identity_rejects_conflicting_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-audit-requirement-binding"
    epoch_ref = "security-epoch:audit-requirement-binding"
    principal_context_id = "principal-context:audit-requirement-binding"
    decision_id = "authorization-decision:audit-requirement-binding"
    requirement_id = "audit-requirement:audit-requirement-binding:tool-execute"
    try:
        with SecurityUnitOfWork(engine) as repo:
            repo.ensure_effective_epoch(
                epoch_ref=epoch_ref,
                tenant_id=tenant_id,
                policy_bundle_ref="policy:audit-requirement-binding",
                policy_bundle={"test": "audit-requirement-binding"},
                action_set_version="test:v1",
                principal_context_hash="a" * 64,
                generation=1,
            )
            repo.ensure_principal_context(
                principal_context_id=principal_context_id,
                tenant_id=tenant_id,
                user_principal_id="workspace-user:audit-requirement-binding",
                epoch_ref=epoch_ref,
            )
            repo.ensure_authorization_decision(
                decision_id=decision_id,
                tenant_id=tenant_id,
                principal_context_id=principal_context_id,
                epoch_ref=epoch_ref,
                resource_ref="resource:audit-requirement-binding",
                action="tool.execute",
                decision="USE_ONLY",
                reason_code="test",
                prepared_action_hash="b" * 64,
            )
            first = repo.ensure_audit_requirement(
                audit_requirement_id=requirement_id,
                tenant_id=tenant_id,
                decision_id=decision_id,
                audit_channel_id=_audit_channel_id(tenant_id),
            )

        with pytest.raises(
            SecurityPersistenceError,
            match="audit requirement identity was reused with different content",
        ):
            with SecurityUnitOfWork(engine) as repo:
                repo.ensure_audit_requirement(
                    audit_requirement_id=requirement_id,
                    tenant_id=tenant_id,
                    decision_id=decision_id,
                    audit_channel_id="audit-channel:different",
                )

        with SecurityUnitOfWork(engine) as repo:
            persisted = repo.read_audit_requirement(
                audit_requirement_id=requirement_id,
                tenant_id=tenant_id,
            )
        assert persisted == first
        with pytest.raises(SecurityPersistenceError, match="belongs to another tenant"):
            with SecurityUnitOfWork(engine) as repo:
                repo.read_audit_requirement(
                    audit_requirement_id=requirement_id,
                    tenant_id="tenant-audit-requirement-other",
                )
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_security_owner_ensure_facts_reject_identity_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-security-fact-identity"
    epoch_ref = "security-epoch:test-owner-identity"
    principal_context_id = "principal-context:test-owner-identity"
    decision_id = "authorization-decision:test-owner-identity"
    try:
        epoch_kwargs = {
            "epoch_ref": epoch_ref,
            "tenant_id": tenant_id,
            "policy_bundle_ref": "policy:test-owner-identity",
            "policy_bundle": {"policy": "v1"},
            "action_set_version": "test:v1",
            "principal_context_hash": "a" * 64,
            "generation": 1,
        }
        with SecurityUnitOfWork(engine) as repo:
            first_epoch = repo.ensure_effective_epoch(**epoch_kwargs)
        with SecurityUnitOfWork(engine) as repo:
            assert repo.ensure_effective_epoch(**epoch_kwargs) == first_epoch
        with pytest.raises(
            SecurityPersistenceError,
            match="effective security epoch identity was reused with different content",
        ):
            with SecurityUnitOfWork(engine) as repo:
                repo.ensure_effective_epoch(
                    **{**epoch_kwargs, "policy_bundle": {"policy": "v2"}}
                )

        context_kwargs = {
            "principal_context_id": principal_context_id,
            "tenant_id": tenant_id,
            "user_principal_id": "workspace-user:test-owner-identity",
            "epoch_ref": epoch_ref,
            "agent_principal_id": "agent:test",
            "task_principal_id": "task:test",
            "session_principal_id": "session:test",
            "run_id": "run:test",
        }
        with SecurityUnitOfWork(engine) as repo:
            repo.ensure_principal_context(**context_kwargs)

        decision_kwargs = {
            "decision_id": decision_id,
            "tenant_id": tenant_id,
            "principal_context_id": principal_context_id,
            "epoch_ref": epoch_ref,
            "resource_ref": "resource:test-owner-identity",
            "action": "tool.execute",
            "decision": "USE_ONLY",
            "reason_code": "test",
            "prepared_action_hash": "b" * 64,
        }
        with SecurityUnitOfWork(engine) as repo:
            first_decision = repo.ensure_authorization_decision(**decision_kwargs)
        with SecurityUnitOfWork(engine) as repo:
            assert repo.ensure_authorization_decision(**decision_kwargs) == first_decision
        with pytest.raises(
            SecurityPersistenceError,
            match="authorization decision identity was reused with different content",
        ):
            with SecurityUnitOfWork(engine) as repo:
                repo.ensure_authorization_decision(
                    **{**decision_kwargs, "prepared_action_hash": "c" * 64}
                )
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_same_trace_distinct_tool_calls_get_distinct_security_epochs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-security-epoch-scope"
    workspace_id = "workspace-security-epoch-scope"
    trace_id = "trace-shared-across-tool-calls"
    secret_ref = "secret-ref:mail:security-epoch-scope"
    executor_calls: list[str] = []
    try:
        _configure_audit_channel(engine, tenant_id=tenant_id)
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:security-epoch-scope",
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
            return {"message_id": f"remote-message:epoch-scope:{len(executor_calls)}"}

        for sequence in (1, 2):
            _, receipt = asyncio.run(
                gateway.invoke_readonly(
                    tool_name="mail.send",
                    args={
                        "to": f"reviewer-{sequence}@example.com",
                        "body": f"same trace call {sequence}",
                        "secret_ref": secret_ref,
                    },
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    trace_id=trace_id,
                    call_id=f"effect-same-trace-{sequence}",
                    adapter_kind="API",
                    executor=executor,
                    readonly=False,
                    approval=ToolApprovalBinding(
                        decision_ref=f"security-decision:same-trace-{sequence}",
                        adapter_ref="test.approval",
                        comment="approved",
                    ),
                )
            )
            assert receipt.status == "completed"

        assert executor_calls == ["sent", "sent"]
        with engine.connect() as connection:
            prepared_epochs = connection.execute(
                text(
                    "SELECT security_epoch_ref FROM prepared_tool_actions "
                    "WHERE tenant_id = :tenant_id "
                    "AND prepared_tool_action_id LIKE 'prepared-tool-action:effect-same-trace-%' "
                    "ORDER BY prepared_tool_action_id"
                ),
                {"tenant_id": tenant_id},
            ).scalars().all()
            epoch_rows = connection.execute(
                text(
                    "SELECT epoch_ref FROM security_effective_epochs "
                    "WHERE tenant_id = :tenant_id ORDER BY epoch_ref"
                ),
                {"tenant_id": tenant_id},
            ).scalars().all()
        assert len(prepared_epochs) == 2
        assert len(set(prepared_epochs)) == 2
        assert set(prepared_epochs) == set(epoch_rows)
        assert all(str(ref).startswith("security-epoch:tool-effect:") for ref in epoch_rows)
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_same_effect_replay_does_not_depend_on_trace_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-security-epoch-replay"
    workspace_id = "workspace-security-epoch-replay"
    call_id = "effect-security-epoch-replay-1"
    secret_ref = "secret-ref:mail:security-epoch-replay"
    executor_calls: list[str] = []
    try:
        _configure_audit_channel(engine, tenant_id=tenant_id)
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:security-epoch-replay",
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
            return {"message_id": "remote-message:epoch-replay:1"}

        common = {
            "tool_name": "mail.send",
            "args": {
                "to": "reviewer@example.com",
                "body": "stable security action",
                "secret_ref": secret_ref,
            },
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "call_id": call_id,
            "adapter_kind": "API",
            "executor": executor,
            "readonly": False,
            "approval": ToolApprovalBinding(
                decision_ref="security-decision:epoch-replay",
                adapter_ref="test.approval",
                comment="approved",
            ),
        }
        _, first = asyncio.run(gateway.invoke_readonly(trace_id="trace-before-response-loss", **common))
        replay_payload, replay = asyncio.run(
            gateway.invoke_readonly(trace_id="trace-after-response-loss", **common)
        )

        assert first.status == "completed"
        assert replay.status == "replayed"
        assert replay_payload is not None
        assert executor_calls == ["sent"]
        with engine.connect() as connection:
            epoch_count = connection.execute(
                text(
                    "SELECT count(*) FROM security_effective_epochs "
                    "WHERE tenant_id = :tenant_id"
                ),
                {"tenant_id": tenant_id},
            ).scalar_one()
        assert int(epoch_count) == 1
    finally:
        _drop_database(engine, admin_engine, database_name)


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
            prepared = connection.execute(
                text(
                    "SELECT prepared_action_hash, security_epoch_ref FROM prepared_tool_actions "
                    "WHERE prepared_tool_action_id = :id"
                ),
                {"id": prepared_id},
            ).mappings().one()
            action_hash = str(prepared["prepared_action_hash"])
            security_epoch_ref = str(prepared["security_epoch_ref"])
            requirement = connection.execute(
                text(
                    "SELECT tenant_id, decision_id, audit_channel_id, requirement_hash, status "
                    "FROM security_audit_requirements "
                    "WHERE audit_requirement_id = :requirement_id"
                ),
                {"requirement_id": f"audit-requirement:{call_id}:tool-execute"},
            ).mappings().one()
            audit = connection.execute(
                text(
                    "SELECT audit_id, channel_id, effect_id, owner_id, status, payload "
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
        assert audit["channel_id"] == requirement["audit_channel_id"]
        assert audit["payload"]["tenant_id"] == tenant_id
        assert audit["payload"]["audit_requirement_id"] == f"audit-requirement:{call_id}:tool-execute"
        assert audit["payload"]["audit_requirement_hash"] == requirement["requirement_hash"]
        assert audit["payload"]["authorization_decision_id"] == requirement["decision_id"]
        assert audit["payload"]["prepared_action_hash"] == action_hash
        assert audit["payload"]["security_epoch_ref"] == security_epoch_ref
        assert requirement["tenant_id"] == tenant_id
        assert requirement["status"] == "required"
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


class _TamperingAuditRequirementGateway(ToolInvocationGateway):
    def __init__(self, *, engine: Engine, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._test_engine = engine

    def _persist_mandatory_audit_before_effect(self, **kwargs: object) -> object:
        security_prepare = kwargs.get("security_prepare")
        requirement_id = str(getattr(security_prepare, "audit_requirement_id", ""))
        assert requirement_id
        with self._test_engine.begin() as connection:
            updated = connection.execute(
                text(
                    "UPDATE security_audit_requirements "
                    "SET audit_channel_id = 'audit-channel:tampered' "
                    "WHERE audit_requirement_id = :requirement_id"
                ),
                {"requirement_id": requirement_id},
            ).rowcount
        assert updated == 1, "fault seam must tamper exactly one audit requirement"
        return super()._persist_mandatory_audit_before_effect(**kwargs)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_changed_security_audit_requirement_blocks_provider_send(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-audit-requirement-tamper"
    workspace_id = "workspace-audit-requirement-tamper"
    trace_id = "trace-audit-requirement-tamper"
    call_id = "effect-audit-requirement-tamper-1"
    secret_ref = "secret-ref:mail:audit-requirement-tamper"
    executor_calls: list[str] = []
    try:
        _configure_audit_channel(engine, tenant_id=tenant_id)
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:mail.send:audit-requirement-tamper",
                audience="tool:mail.send",
                owner_principal_id=f"workspace-user:{workspace_id}",
                scope={"tool": "mail.send", "workspace_id": workspace_id},
            )
        gateway = _TamperingAuditRequirementGateway(
            engine=engine,
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
                args={
                    "to": "reviewer@example.com",
                    "body": "tampered requirement must stop",
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
                    decision_ref="security-decision:audit-requirement-tamper",
                    adapter_ref="test.approval",
                    comment="approved before requirement tamper",
                ),
            )
        )

        prepared_id = f"prepared-tool-action:{call_id}"
        assert result is None
        assert receipt.status == "blocked"
        assert "audit requirement hash does not match persisted content" in receipt.blocked_reason
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
                text(
                    "SELECT count(*) FROM tool_effect_receipts "
                    "WHERE prepared_tool_action_id = :prepared_id"
                ),
                {"prepared_id": prepared_id},
            ).scalar_one()
        assert int(audit_count) == 0
        assert int(effect_count) == 0
    finally:
        _drop_database(engine, admin_engine, database_name)


class _RevokingAfterAuditGateway(ToolInvocationGateway):
    def __init__(self, *, engine: Engine, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._test_engine = engine

    def _persist_mandatory_audit_before_effect(self, **kwargs: object) -> object:
        binding = super()._persist_mandatory_audit_before_effect(**kwargs)
        security_prepare = kwargs.get("security_prepare")
        epoch_ref = str(getattr(security_prepare, "security_epoch_ref", ""))
        assert epoch_ref
        with self._test_engine.begin() as connection:
            updated = connection.execute(
                text(
                    "UPDATE security_effective_epochs SET status = 'revoked' "
                    "WHERE epoch_ref = :epoch_ref AND status = 'active'"
                ),
                {"epoch_ref": epoch_ref},
            ).rowcount
        assert updated == 1, "fault seam must revoke exactly one active SecurityEpoch"
        return binding


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
                channel_id=_audit_channel_id(tenant_id),
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
                    channel_id=_audit_channel_id(tenant_id),
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


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Mandatory Audit probe is BLOCKED",
)
def test_mandatory_audit_storage_is_tenant_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_a = "tenant-audit-isolation-a"
    tenant_b = "tenant-audit-isolation-b"
    channel_a = _audit_channel_id(tenant_a)
    channel_b = _audit_channel_id(tenant_b)
    try:
        _configure_audit_channel(engine, tenant_id=tenant_a, capacity_limit=1)
        with pytest.raises(
            InfrastructureConflictError,
            match="mandatory audit channel belongs to another tenant",
        ):
            with InfrastructureUnitOfWork(engine, tenant_id=tenant_b) as repo:
                repo.configure_audit_channel(
                    channel_id=channel_a,
                    capacity_limit=1,
                    owner_id="security-governance:cross-tenant-probe",
                )

        _configure_audit_channel(engine, tenant_id=tenant_b, capacity_limit=1)

        with InfrastructureUnitOfWork(engine, tenant_id=tenant_a) as repo:
            audit_a = repo.record_mandatory_audit(
                channel_id=channel_a,
                effect_id="tool-effect-audit:tenant-a",
                owner_id="tool-runtime:tenant-a",
                payload={
                    "tenant_id": tenant_a,
                    "prepared_tool_action_id": "prepared-tool-action:tenant-a",
                    "prepared_action_hash": "a" * 64,
                },
            )
        with InfrastructureUnitOfWork(engine, tenant_id=tenant_b) as repo:
            audit_b = repo.record_mandatory_audit(
                channel_id=channel_b,
                effect_id="tool-effect-audit:tenant-b",
                owner_id="tool-runtime:tenant-b",
                payload={
                    "tenant_id": tenant_b,
                    "prepared_tool_action_id": "prepared-tool-action:tenant-b",
                    "prepared_action_hash": "b" * 64,
                },
            )
        assert audit_a.remaining_capacity == 0
        assert audit_b.remaining_capacity == 0

        with pytest.raises(FencingRejectedError, match="tenant-scoped durable mandatory audit"):
            with InfrastructureUnitOfWork(engine, tenant_id=tenant_b) as repo:
                repo.assert_audit_durable_for_effect(
                    audit_id=audit_a.audit_id,
                    effect_id=audit_a.effect_id,
                    owner_id=audit_a.owner_id,
                )

        with pytest.raises(FencingRejectedError, match="tenant-scoped audited effect"):
            with InfrastructureUnitOfWork(engine, tenant_id=tenant_b) as repo:
                repo.mark_audited_effect_observed(
                    audit_id=audit_a.audit_id,
                    effect_id=audit_a.effect_id,
                    owner_id=audit_a.owner_id,
                )

        with engine.connect() as connection:
            channel_rows = connection.execute(
                text(
                    "SELECT tenant_id, channel_id FROM infra_audit_channels "
                    "WHERE tenant_id IN (:tenant_a, :tenant_b) ORDER BY tenant_id"
                ),
                {"tenant_a": tenant_a, "tenant_b": tenant_b},
            ).mappings().all()
            event_rows = connection.execute(
                text(
                    "SELECT tenant_id, effect_id FROM infra_mandatory_audit_events "
                    "WHERE tenant_id IN (:tenant_a, :tenant_b) ORDER BY tenant_id"
                ),
                {"tenant_a": tenant_a, "tenant_b": tenant_b},
            ).mappings().all()
        assert channel_rows == [
            {"tenant_id": tenant_a, "channel_id": channel_a},
            {"tenant_id": tenant_b, "channel_id": channel_b},
        ]
        assert event_rows == [
            {"tenant_id": tenant_a, "effect_id": "tool-effect-audit:tenant-a"},
            {"tenant_id": tenant_b, "effect_id": "tool-effect-audit:tenant-b"},
        ]
    finally:
        _drop_database(engine, admin_engine, database_name)
