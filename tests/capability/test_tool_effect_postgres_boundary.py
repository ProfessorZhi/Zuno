from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys
from uuid import uuid4

import pytest
import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

from zuno.capability.control_plane import (
    ExecutorAdapterContract,
    ToolApprovalPolicy,
    ToolCardManifest,
    ToolExecutionMode,
    ToolSideEffectLevel,
    ToolTrustTier,
)
from zuno.capability.runtime import ToolControlPlaneRuntime, ToolRuntimeRequest
from zuno.capability.tool_runtime import ToolApprovalBinding, ToolEffectUnknownError, ToolInvocationGateway
from zuno.platform.database.foundation import InfrastructureUnitOfWork
from zuno.platform.database.tool_runtime import ToolRuntimeConflict, ToolUnitOfWork
from zuno.platform.security import SecurityUnitOfWork
from zuno.platform import settings as platform_settings


REPO_ROOT = Path(__file__).resolve().parents[2]


def _migrated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Engine, Engine, str]:
    raw_url = os.environ.get("ZUNO_TEST_DATABASE_URL")
    if not raw_url:
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; Effect PostgreSQL probe is BLOCKED")

    base_url = make_url(raw_url)
    database_name = f"zuno_effect_probe_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "effect-probe-config.yaml"
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

    alembic_config = Config(str(REPO_ROOT / "infra/db/alembic.ini"))

    # Current infra/db/alembic/env.py still imports the retired `zuno.settings`
    # path. Keep that migration-entrypoint drift visible as a separate Current
    # blocker, but do not let it prevent this test-only probe from reaching the
    # Effect/Recovery behavior under review. This alias is deliberately local
    # to the test process and is not evidence that the formal Alembic entrypoint
    # works without compatibility help.
    previous_legacy_settings = sys.modules.get("zuno.settings")
    sys.modules["zuno.settings"] = platform_settings
    try:
        command.upgrade(alembic_config, "head")
    finally:
        if previous_legacy_settings is None:
            sys.modules.pop("zuno.settings", None)
        else:
            sys.modules["zuno.settings"] = previous_legacy_settings

    engine = create_engine(database_url)
    with InfrastructureUnitOfWork(engine, tenant_id="tenant-effect") as repo:
        repo.configure_audit_channel(
            channel_id="audit-channel:tool-runtime:phase16",
            capacity_limit=100,
            owner_id="security-governance:effect-test-bootstrap",
        )
    return engine, admin_engine, database_name


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


def _runtime(engine: Engine, calls: list[dict[str, object]]) -> ToolControlPlaneRuntime:
    runtime = ToolControlPlaneRuntime(
        tool_unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant_id: InfrastructureUnitOfWork(
            engine,
            tenant_id=tenant_id,
        ),
    )
    runtime.register_manifest(
        ToolCardManifest(
            tool_id="mail.send",
            owner="capability.tools.send_email",
            capability_domain="mail",
            description_for_model="Send an email after explicit approval.",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.API,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=ToolSideEffectLevel.WRITE_EXTERNAL,
            approval_policy=ToolApprovalPolicy.APPROVAL_REQUIRED,
            sandbox_profile="network_limited",
            credential_policy="brokered_secret",
            network_policy="egress_mail_only",
            audit_policy="trace_and_review",
            budget={"timeout_seconds": 10},
            executor_adapter="api.mail.send",
        )
    )

    def uncertain_send(args: dict[str, object], context: object) -> object:
        calls.append({"args": dict(args), "context_type": type(context).__name__})
        raise ToolEffectUnknownError(
            provider_effect_id="provider-effect:mail:unknown:1",
            reconciliation_query={"message_id": "remote-message:unknown:1"},
        )

    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="api.mail.send",
            execution_mode=ToolExecutionMode.API,
            sandbox_profile="network_limited",
            network_policy="egress_mail_only",
            credential_policy="brokered_secret",
            timeout_seconds=10,
        ),
        uncertain_send,
    )
    return runtime


def _approved_request(*, pending, execution_id: str) -> ToolRuntimeRequest:
    return ToolRuntimeRequest(
        tool_id="mail.send",
        arguments={"to": "reviewer@example.com", "body": "status update"},
        workspace_id="workspace-effect",
        user_id="tenant-effect",
        task_id="task-effect",
        trace_id="trace-effect",
        model_intent="Send the approved status update.",
        approval_decision_ref="security-decision:effect-approved",
        approval_adapter_ref="test.approval",
        approval_comment="approved",
        tool_request_id=pending.tool_request_id,
        approval_id=pending.approval_id,
        execution_id=execution_id,
    )


def _gateway(engine: Engine) -> ToolInvocationGateway:
    return ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant_id: InfrastructureUnitOfWork(
            engine,
            tenant_id=tenant_id,
        ),
    )


def _escalated_unknown_effect(
    *,
    engine: Engine,
    calls: list[dict[str, object]],
    execution_id: str,
) -> tuple[ToolInvocationGateway, ToolRuntimeRequest, str]:
    runtime = _runtime(engine, calls)
    pending = runtime.execute(
        ToolRuntimeRequest(
            tool_id="mail.send",
            arguments={"to": "reviewer@example.com", "body": "status update"},
            workspace_id="workspace-effect",
            user_id="tenant-effect",
            task_id="task-effect",
            trace_id=f"trace-effect-{execution_id}",
            model_intent="Send the approved status update.",
            execution_id=execution_id,
        )
    )
    assert pending.status == "approval_required"
    approved_request = _approved_request(pending=pending, execution_id=execution_id)
    first = runtime.execute(approved_request)
    assert first.status == "reconcile_required"
    assert first.effect_certainty == "UNKNOWN_EFFECT"
    assert len(calls) == 1

    reconciliation_id = f"tool-effect-reconciliation:{execution_id}"
    gateway = _gateway(engine)
    assert gateway.escalate_due_reconciliations(
        tenant_id="tenant-effect",
        now=datetime.now(tz=UTC) + timedelta(hours=2),
    ) == 1
    return gateway, approved_request, reconciliation_id


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Effect PostgreSQL probe is BLOCKED",
)
def test_unknown_external_effect_stays_reconcile_required_after_runtime_restart(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A durable UNKNOWN effect must not become CONFIRMED merely because the action is replayed."""

    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    calls: list[dict[str, object]] = []
    execution_id = "effect-unknown-replay-1"

    try:
        runtime = _runtime(engine, calls)
        pending = runtime.execute(
            ToolRuntimeRequest(
                tool_id="mail.send",
                arguments={"to": "reviewer@example.com", "body": "status update"},
                workspace_id="workspace-effect",
                user_id="tenant-effect",
                task_id="task-effect",
                trace_id="trace-effect",
                model_intent="Send the approved status update.",
                execution_id=execution_id,
            )
        )
        assert pending.status == "approval_required"
        assert calls == []

        approved_request = _approved_request(pending=pending, execution_id=execution_id)
        first = runtime.execute(approved_request)

        assert first.status == "reconcile_required"
        assert first.effect_certainty == "UNKNOWN_EFFECT"
        assert len(calls) == 1

        attempt_id = f"tool-attempt:{execution_id}"
        receipt_id = f"tool-execution-receipt:{execution_id}"
        reconciliation_id = f"tool-effect-reconciliation:{execution_id}"
        with engine.connect() as connection:
            attempt = connection.execute(
                text(
                    "SELECT status, dispatch_certainty FROM tool_attempts "
                    "WHERE attempt_id = :attempt_id"
                ),
                {"attempt_id": attempt_id},
            ).mappings().one()
            receipt = connection.execute(
                text(
                    "SELECT status, effect_certainty FROM tool_execution_receipts "
                    "WHERE receipt_id = :receipt_id"
                ),
                {"receipt_id": receipt_id},
            ).mappings().one()
            reconciliation = connection.execute(
                text(
                    "SELECT status, next_action, provider_effect_id FROM tool_effect_reconciliations "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).mappings().one()

        assert attempt == {"status": "UNKNOWN", "dispatch_certainty": "DISPATCHED"}
        assert receipt == {"status": "UNKNOWN", "effect_certainty": "UNKNOWN_EFFECT"}
        assert reconciliation == {
            "status": "OPEN",
            "next_action": "RECONCILE",
            "provider_effect_id": "provider-effect:mail:unknown:1",
        }

        restarted_runtime = _runtime(engine, calls)
        replay = restarted_runtime.execute(approved_request)

        assert len(calls) == 1, "restart replay must not dispatch the external effect twice"
        assert replay.status == "reconcile_required"
        assert replay.effect_certainty == "UNKNOWN_EFFECT"

        with engine.connect() as connection:
            still_open = connection.execute(
                text(
                    "SELECT status, next_action FROM tool_effect_reconciliations "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).mappings().one()
        assert still_open == {"status": "OPEN", "next_action": "RECONCILE"}

        gateway = _gateway(engine)
        assert gateway.escalate_due_reconciliations(
            tenant_id="tenant-effect",
            now=datetime.now(tz=UTC) + timedelta(hours=2),
        ) == 1
        assessment_kwargs = {
            "tenant_id": "tenant-effect",
            "manual_assessment_id": f"tool-manual-effect-assessment:{execution_id}",
            "reconciliation_id": reconciliation_id,
            "provider_effect_id": "provider-effect:mail:unknown:1",
            "conclusion": "CONFIRMED_EXECUTED",
            "confidence": 1.0,
            "assessor_principal_id": "workspace-user:manual-reviewer:effect",
            "residual_uncertainty": "",
            "evidence_payload": {"source": "provider-console", "status": "committed"},
        }
        gateway.record_manual_effect_assessment(**assessment_kwargs)
        # Response loss after a conclusive write must make the exact same durable
        # judgment replay idempotently even though reconciliation is now RESOLVED.
        gateway.record_manual_effect_assessment(**assessment_kwargs)
        resolved_ref = f"tool-effect-receipt:{execution_id}"

        resolved_replay = _runtime(engine, calls).execute(approved_request)
        assert len(calls) == 1, "conclusive replay must still not redispatch the effect"
        assert resolved_replay.status == "completed"
        assert resolved_replay.effect_certainty == "CONFIRMED_EFFECT"

        with engine.connect() as connection:
            resolved = connection.execute(
                text(
                    "SELECT status, next_action FROM tool_effect_reconciliations "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).mappings().one()
            effect = connection.execute(
                text(
                    "SELECT effect_status, effect_certainty FROM tool_effect_receipts "
                    "WHERE effect_receipt_id = :effect_receipt_id"
                ),
                {"effect_receipt_id": resolved_ref},
            ).mappings().one()
        assert resolved == {"status": "RESOLVED", "next_action": "WAIT"}
        assert effect == {"effect_status": "CONFIRMED", "effect_certainty": "CONFIRMED_EFFECT"}
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Effect PostgreSQL probe is BLOCKED",
)
def test_conclusive_not_executed_reconciliation_never_becomes_completed_or_redispatched(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    calls: list[dict[str, object]] = []
    execution_id = "effect-confirmed-not-executed-1"

    try:
        runtime = _runtime(engine, calls)
        pending = runtime.execute(
            ToolRuntimeRequest(
                tool_id="mail.send",
                arguments={"to": "reviewer@example.com", "body": "status update"},
                workspace_id="workspace-effect",
                user_id="tenant-effect",
                task_id="task-effect",
                trace_id="trace-effect",
                model_intent="Send the approved status update.",
                execution_id=execution_id,
            )
        )
        approved_request = _approved_request(pending=pending, execution_id=execution_id)
        first = runtime.execute(approved_request)
        assert first.status == "reconcile_required"
        assert first.effect_certainty == "UNKNOWN_EFFECT"
        assert len(calls) == 1

        reconciliation_id = f"tool-effect-reconciliation:{execution_id}"
        gateway = _gateway(engine)
        assert gateway.escalate_due_reconciliations(
            tenant_id="tenant-effect",
            now=datetime.now(tz=UTC) + timedelta(hours=2),
        ) == 1
        gateway.record_manual_effect_assessment(
            tenant_id="tenant-effect",
            manual_assessment_id=f"tool-manual-effect-assessment:inconclusive:{execution_id}",
            reconciliation_id=reconciliation_id,
            provider_effect_id="provider-effect:mail:unknown:1",
            conclusion="UNRESOLVED",
            confidence=0.4,
            assessor_principal_id="workspace-user:manual-reviewer:effect",
            residual_uncertainty="provider logs are incomplete",
            evidence_payload={"source": "provider-console", "status": "incomplete"},
        )
        still_unknown = _runtime(engine, calls).execute(approved_request)
        assert still_unknown.status == "reconcile_required"
        assert still_unknown.effect_certainty == "UNKNOWN_EFFECT"
        assert len(calls) == 1

        effect_receipt_id = gateway.resolve_effect_reconciliation(
            tenant_id="tenant-effect",
            reconciliation_id=reconciliation_id,
            conclusion="CONFIRMED_NOT_EXECUTED",
            resolution_payload={"source": "REMOTE_QUERY", "provider_status": "not_found"},
        )

        replay = _runtime(engine, calls).execute(approved_request)
        assert len(calls) == 1, "confirmed no-effect must not silently redispatch"
        assert replay.status == "confirmed_not_executed"
        assert replay.effect_certainty == "NO_EFFECT"

        with engine.connect() as connection:
            reconciliation = connection.execute(
                text(
                    "SELECT status, next_action FROM tool_effect_reconciliations "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).mappings().one()
            effect = connection.execute(
                text(
                    "SELECT effect_status, effect_certainty FROM tool_effect_receipts "
                    "WHERE effect_receipt_id = :effect_receipt_id"
                ),
                {"effect_receipt_id": effect_receipt_id},
            ).mappings().one()
            execution = connection.execute(
                text(
                    "SELECT status, effect_certainty FROM tool_execution_receipts "
                    "WHERE receipt_id = :receipt_id"
                ),
                {"receipt_id": f"tool-execution-receipt:{execution_id}"},
            ).mappings().one()
        assert reconciliation == {"status": "RESOLVED", "next_action": "WAIT"}
        assert effect == {"effect_status": "NO_EFFECT", "effect_certainty": "CONFIRMED_NO_EFFECT"}
        assert execution == {"status": "FAILED", "effect_certainty": "CONFIRMED_NO_EFFECT"}
    finally:
        _drop_database(engine, admin_engine, database_name)

@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Effect PostgreSQL probe is BLOCKED",
)
def test_manual_assessment_provider_identity_must_match_reconciliation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    calls: list[dict[str, object]] = []
    execution_id = "effect-manual-provider-mismatch-1"
    try:
        gateway, approved_request, reconciliation_id = _escalated_unknown_effect(
            engine=engine, calls=calls, execution_id=execution_id
        )
        with pytest.raises(
            ToolRuntimeConflict,
            match="provider effect does not match reconciliation",
        ):
            gateway.record_manual_effect_assessment(
                tenant_id="tenant-effect",
                manual_assessment_id=f"tool-manual-effect-assessment:{execution_id}",
                reconciliation_id=reconciliation_id,
                provider_effect_id="provider-effect:mail:different",
                conclusion="CONFIRMED_EXECUTED",
                confidence=1.0,
                assessor_principal_id="workspace-user:manual-reviewer:effect",
                residual_uncertainty="",
                evidence_payload={"source": "provider-console", "status": "committed"},
            )

        with engine.connect() as connection:
            assessment_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_manual_effect_assessments "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).scalar_one()
            reconciliation = connection.execute(
                text(
                    "SELECT status, next_action, provider_effect_id "
                    "FROM tool_effect_reconciliations "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).mappings().one()
            effect_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_effect_receipts "
                    "WHERE prepared_tool_action_id = :prepared_id"
                ),
                {"prepared_id": f"prepared-tool-action:{execution_id}"},
            ).scalar_one()
        assert int(assessment_count) == 0
        assert reconciliation == {
            "status": "ESCALATED",
            "next_action": "MANUAL_ASSESSMENT",
            "provider_effect_id": "provider-effect:mail:unknown:1",
        }
        assert int(effect_count) == 0

        replay = _runtime(engine, calls).execute(approved_request)
        assert replay.status == "reconcile_required"
        assert replay.effect_certainty == "UNKNOWN_EFFECT"
        assert len(calls) == 1
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Effect PostgreSQL probe is BLOCKED",
)
def test_manual_assessment_conflict_cannot_resolve_from_unpersisted_second_judgment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    calls: list[dict[str, object]] = []
    execution_id = "effect-manual-assessment-conflict-1"
    assessment_id = f"tool-manual-effect-assessment:{execution_id}"
    try:
        gateway, approved_request, reconciliation_id = _escalated_unknown_effect(
            engine=engine, calls=calls, execution_id=execution_id
        )
        first_kwargs = {
            "tenant_id": "tenant-effect",
            "manual_assessment_id": assessment_id,
            "reconciliation_id": reconciliation_id,
            "provider_effect_id": "provider-effect:mail:unknown:1",
            "conclusion": "UNRESOLVED",
            "confidence": 0.4,
            "assessor_principal_id": "workspace-user:manual-reviewer:effect",
            "residual_uncertainty": "provider logs are incomplete",
            "evidence_payload": {"source": "provider-console", "status": "incomplete"},
        }
        gateway.record_manual_effect_assessment(**first_kwargs)
        gateway.record_manual_effect_assessment(**first_kwargs)

        with pytest.raises(
            ToolRuntimeConflict,
            match="manual effect assessment already exists with different content",
        ):
            gateway.record_manual_effect_assessment(
                tenant_id="tenant-effect",
                manual_assessment_id=assessment_id,
                reconciliation_id=reconciliation_id,
                provider_effect_id="provider-effect:mail:unknown:1",
                conclusion="CONFIRMED_EXECUTED",
                confidence=1.0,
                assessor_principal_id="workspace-user:manual-reviewer:effect",
                residual_uncertainty="",
                evidence_payload={"source": "provider-console", "status": "committed"},
            )

        with engine.connect() as connection:
            assessment = connection.execute(
                text(
                    "SELECT manual_assessment_id, conclusion, residual_uncertainty, "
                    "provider_effect_id FROM tool_manual_effect_assessments "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).mappings().one()
            reconciliation = connection.execute(
                text(
                    "SELECT status, next_action FROM tool_effect_reconciliations "
                    "WHERE reconciliation_id = :reconciliation_id"
                ),
                {"reconciliation_id": reconciliation_id},
            ).mappings().one()
            effect_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_effect_receipts "
                    "WHERE prepared_tool_action_id = :prepared_id"
                ),
                {"prepared_id": f"prepared-tool-action:{execution_id}"},
            ).scalar_one()
        assert assessment == {
            "manual_assessment_id": assessment_id,
            "conclusion": "UNRESOLVED",
            "residual_uncertainty": "provider logs are incomplete",
            "provider_effect_id": "provider-effect:mail:unknown:1",
        }
        assert reconciliation == {
            "status": "ESCALATED",
            "next_action": "MANUAL_ASSESSMENT",
        }
        assert int(effect_count) == 0

        replay = _runtime(engine, calls).execute(approved_request)
        assert replay.status == "reconcile_required"
        assert replay.effect_certainty == "UNKNOWN_EFFECT"
        assert len(calls) == 1
    finally:
        _drop_database(engine, admin_engine, database_name)



@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Effect PostgreSQL probe is BLOCKED",
)
def test_cancel_requested_async_job_still_accepts_late_completed_callback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-effect"
    workspace_id = "workspace-effect"
    call_id = "effect-cancel-late-callback-1"
    provider_job_id = "provider-job:cancel-late:1"
    secret_ref = "secret-ref:async-cancel-late"
    try:
        with SecurityUnitOfWork(engine) as repo:
            repo.record_secret_ref(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                credential_version_ref="credential-version:async-cancel-late",
                audience="tool:mail.send",
                owner_principal_id=f"workspace-user:{workspace_id}",
                scope={"tool": "mail.send", "workspace_id": workspace_id},
            )

        gateway = _gateway(engine)

        async def executor() -> dict[str, str]:
            return {"provider_job_id": provider_job_id}

        result, receipt = asyncio.run(
            gateway.invoke_readonly(
                tool_name="mail.send",
                args={
                    "to": "reviewer@example.com",
                    "body": "async status update",
                    "secret_ref": secret_ref,
                },
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                trace_id="trace-cancel-late",
                call_id=call_id,
                adapter_kind="ASYNC_JOB",
                executor=executor,
                readonly=False,
                approval=ToolApprovalBinding(
                    decision_ref="security-decision:cancel-late-approved",
                    adapter_ref="test.approval",
                    comment="approved",
                ),
            )
        )
        assert result == {"provider_job_id": provider_job_id}
        assert receipt.status == "async_waiting"

        prepared_id = f"prepared-tool-action:{call_id}"
        attempt_id = f"tool-attempt:{call_id}"
        async_job_id = f"tool-async-job:{call_id}"
        audit_requirement_id = f"audit-requirement:{call_id}:tool-execute"

        gateway.record_cancellation_request(
            tenant_id=tenant_id,
            prepared_id=prepared_id,
            attempt_id=attempt_id,
            async_job_id=async_job_id,
            provider_job_id=provider_job_id,
            requested_by_principal_id=f"workspace-user:{workspace_id}",
            audit_requirement_id=audit_requirement_id,
        )
        gateway.record_cancellation_request(
            tenant_id=tenant_id,
            prepared_id=prepared_id,
            attempt_id=attempt_id,
            async_job_id=async_job_id,
            provider_job_id=provider_job_id,
            requested_by_principal_id=f"workspace-user:{workspace_id}",
            audit_requirement_id=audit_requirement_id,
        )

        with engine.connect() as connection:
            job = connection.execute(
                text(
                    "SELECT status, callback_order FROM tool_async_jobs "
                    "WHERE tenant_id = :tenant_id AND async_job_id = :async_job_id"
                ),
                {"tenant_id": tenant_id, "async_job_id": async_job_id},
            ).mappings().one()
            cancellation_count = connection.execute(
                text(
                    "SELECT count(*) FROM tool_cancellation_receipts "
                    "WHERE tenant_id = :tenant_id AND async_job_id = :async_job_id"
                ),
                {"tenant_id": tenant_id, "async_job_id": async_job_id},
            ).scalar_one()
        assert job == {"status": "CANCEL_REQUESTED", "callback_order": 0}
        assert int(cancellation_count) == 1

        gateway.record_async_callback(
            tenant_id=tenant_id,
            async_job_id=async_job_id,
            provider_job_id=provider_job_id,
            callback_order=1,
            callback_payload={"state": "completed", "provider_job_id": provider_job_id},
            expected_binding_ref=f"callback-binding:{call_id}",
            provided_binding_ref=f"callback-binding:{call_id}",
        )

        with engine.connect() as connection:
            final_job = connection.execute(
                text(
                    "SELECT status, callback_order FROM tool_async_jobs "
                    "WHERE tenant_id = :tenant_id AND async_job_id = :async_job_id"
                ),
                {"tenant_id": tenant_id, "async_job_id": async_job_id},
            ).mappings().one()
            callback = connection.execute(
                text(
                    "SELECT accepted, authenticity_status FROM tool_async_callbacks "
                    "WHERE tenant_id = :tenant_id AND async_job_id = :async_job_id "
                    "AND callback_order = 1"
                ),
                {"tenant_id": tenant_id, "async_job_id": async_job_id},
            ).mappings().one()
            cancellation = connection.execute(
                text(
                    "SELECT status, external_effect_revoked FROM tool_cancellation_receipts "
                    "WHERE tenant_id = :tenant_id AND async_job_id = :async_job_id"
                ),
                {"tenant_id": tenant_id, "async_job_id": async_job_id},
            ).mappings().one()

        assert final_job == {"status": "COMPLETED", "callback_order": 1}
        assert callback == {"accepted": True, "authenticity_status": "VERIFIED"}
        assert cancellation == {"status": "NOT_GUARANTEED", "external_effect_revoked": False}

        with pytest.raises(ToolRuntimeConflict, match="cancellation identity does not match async job"):
            gateway.record_cancellation_request(
                tenant_id=tenant_id,
                prepared_id=prepared_id,
                attempt_id=attempt_id,
                async_job_id=async_job_id,
                provider_job_id="provider-job:different",
                requested_by_principal_id=f"workspace-user:{workspace_id}",
                audit_requirement_id=audit_requirement_id,
            )
    finally:
        _drop_database(engine, admin_engine, database_name)
