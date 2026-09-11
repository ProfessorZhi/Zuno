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

from zuno.capability.control_plane import (
    ExecutorAdapterContract,
    ToolApprovalPolicy,
    ToolCardManifest,
    ToolExecutionMode,
    ToolSideEffectLevel,
    ToolTrustTier,
)
from zuno.capability.runtime import ToolControlPlaneRuntime, ToolRuntimeRequest
from zuno.capability.tool_runtime import ToolEffectUnknownError
from zuno.platform.database.foundation import InfrastructureUnitOfWork
from zuno.platform.database.tool_runtime import ToolUnitOfWork
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
    finally:
        _drop_database(engine, admin_engine, database_name)
