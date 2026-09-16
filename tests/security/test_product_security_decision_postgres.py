from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

from zuno.agent.runtime.postgres_store import PostgresAgentRunStore
from zuno.capability.control_plane import ToolExecutionMode, ToolSideEffectLevel
from zuno.platform.database.foundation import InfrastructureUnitOfWork
from zuno.platform.database.tool_runtime import ToolUnitOfWork
from zuno.platform.security import SecurityUnitOfWork
from zuno.platform.security.decision_resolvers import PostgresSecurityDecisionResolver
from zuno.platform.security.persistence import authorization_decision_hash
from zuno.platform.services.workspace.single_controller_runtime import (
    WorkspaceAgentRuntime,
    WorkspaceRunRequest,
    WorkspaceToolBinding,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _migrated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Engine, Engine, str]:
    raw_url = os.environ.get("ZUNO_TEST_DATABASE_URL")
    if not raw_url:
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; PSC-B PostgreSQL probe is BLOCKED")
    base_url = make_url(raw_url)
    database_name = f"zuno_psc_b_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "psc-b-config.yaml"
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


def _context() -> dict[str, object]:
    return {
        "tenant_id": "tenant-psc-b",
        "workspace_id": "workspace-psc-b",
        "principal_id": "user-psc-b",
        "action": "tool.execute",
        "resource": "tool.read",
        "task_id": "task-psc-b",
        "trace_id": "trace-psc-b",
        "run_id": "run:task-psc-b",
        "model_intent": "read governed workspace data",
        "proposed_args": {"query": "status"},
        "side_effect_level": "read",
        "execution_mode": "local_function",
    }


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PSC-B PostgreSQL probe is BLOCKED",
)
def test_product_security_owner_fact_is_scoped_expiring_and_tamper_evident(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    try:
        port = PostgresSecurityDecisionResolver(engine, decision_ttl_seconds=300)
        context = _context()
        handle = port.issue(context)
        assert handle is not None
        fact = port.resolve(handle["decision_id"], {**context, "security_epoch_ref": handle["security_epoch_ref"]})
        assert fact is not None
        assert fact["tenant_id"] == context["tenant_id"]
        assert fact["workspace_id"] == context["workspace_id"]
        assert fact["principal_id"] == context["principal_id"]
        assert fact["resource"] == context["resource"]
        assert fact["issued_at"]
        assert fact["expires_at"]

        replay_handle = port.issue(context)
        assert replay_handle == handle
        replay_fact = port.resolve(
            replay_handle["decision_id"],
            {**context, "security_epoch_ref": replay_handle["security_epoch_ref"]},
        )
        assert replay_fact is not None
        assert replay_fact["issued_at"] == fact["issued_at"]
        assert replay_fact["expires_at"] == fact["expires_at"]

        assert port.resolve(
            handle["decision_id"],
            {**context, "tenant_id": "tenant-foreign", "security_epoch_ref": handle["security_epoch_ref"]},
        ) is None
        assert port.resolve(
            handle["decision_id"],
            {**context, "workspace_id": "workspace-foreign", "security_epoch_ref": handle["security_epoch_ref"]},
        ) is None

        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE security_authorization_decisions SET resource_ref = 'tool.tampered' "
                    "WHERE decision_id = :decision_id"
                ),
                {"decision_id": handle["decision_id"]},
            )
        assert port.resolve(
            handle["decision_id"],
            {**context, "security_epoch_ref": handle["security_epoch_ref"]},
        ) is None
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PSC-B PostgreSQL probe is BLOCKED",
)
def test_expired_product_security_fact_fails_closed_even_with_matching_hash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    try:
        port = PostgresSecurityDecisionResolver(engine, decision_ttl_seconds=300)
        context = _context()
        context["task_id"] = "task-psc-b-expired"
        context["run_id"] = "run:task-psc-b-expired"
        handle = port.issue(context)
        assert handle is not None
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    "SELECT decision_id, tenant_id, principal_context_id, epoch_ref, resource_ref, "
                    "action, decision, reason_code, prepared_action_hash FROM security_authorization_decisions "
                    "WHERE decision_id = :decision_id"
                ),
                {"decision_id": handle["decision_id"]},
            ).mappings().one()
            expired = datetime.now(tz=UTC) - timedelta(seconds=1)
            decision_hash = authorization_decision_hash(
                decision_id=str(row["decision_id"]),
                tenant_id=str(row["tenant_id"]),
                principal_context_id=str(row["principal_context_id"]),
                epoch_ref=str(row["epoch_ref"]),
                resource_ref=str(row["resource_ref"]),
                action=str(row["action"]),
                decision=str(row["decision"]),
                reason_code=str(row["reason_code"]),
                prepared_action_hash=None if row["prepared_action_hash"] is None else str(row["prepared_action_hash"]),
                expires_at=expired,
            )
            connection.execute(
                text(
                    "UPDATE security_authorization_decisions SET expires_at = :expires_at, decision_hash = :decision_hash "
                    "WHERE decision_id = :decision_id"
                ),
                {"expires_at": expired, "decision_hash": decision_hash, "decision_id": handle["decision_id"]},
            )
        assert port.resolve(
            handle["decision_id"],
            {**context, "security_epoch_ref": handle["security_epoch_ref"]},
        ) is None
    finally:
        _drop_database(engine, admin_engine, database_name)


class _UnusedModel:
    async def ainvoke(self, prompt):
        raise AssertionError("PSC-B admission probe must not invoke the model")


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PSC-B PostgreSQL probe is BLOCKED",
)
def test_product_runtime_resolves_security_owner_fact_before_budget_blocker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    try:
        security_port = PostgresSecurityDecisionResolver(engine, decision_ttl_seconds=300)
        runtime = WorkspaceAgentRuntime(
            model=_UnusedModel(),
            bindings=[
                WorkspaceToolBinding(
                    tool_id="tool.read",
                    display_name="Read Tool",
                    description="Read governed workspace data.",
                    input_schema={"type": "object"},
                    side_effect_level=ToolSideEffectLevel.READ,
                    execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
                    executor=lambda args: {"ok": True},
                ),
                WorkspaceToolBinding(
                    tool_id="tool.unselected",
                    display_name="Unselected Tool",
                    description="Must not broaden the selected Security resource scope.",
                    input_schema={"type": "object"},
                    side_effect_level=ToolSideEffectLevel.READ,
                    execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
                    executor=lambda args: {"ok": True},
                ),
            ],
            tenant_id="tenant-psc-b",
            workspace_id="workspace-psc-b",
            principal_id="user-psc-b",
            store=PostgresAgentRunStore(engine),
            tool_unit_of_work_factory=lambda: ToolUnitOfWork(engine),
            security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
            infrastructure_unit_of_work_factory=lambda tenant_id: InfrastructureUnitOfWork(engine, tenant_id=tenant_id),
            security_decision_resolver=security_port,
            budget_decision_resolver=None,
            approval_flow="none",
        )
        request = WorkspaceRunRequest(
            task_id="task-psc-b-runtime",
            thread_id="thread-psc-b",
            tenant_id="tenant-psc-b",
            workspace_id="workspace-psc-b",
            principal_id="user-psc-b",
            submission_id="submission-psc-b",
            client_request_id="request-psc-b",
            user_id="user-psc-b",
            trace_id="trace-psc-b-runtime",
            goal="read governed workspace data",
            tool_id="tool.read",
            tool_arguments={"query": "status"},
            plan_kind="tool",
        )
        admitted = runtime._to_runtime_request(request)
        assert admitted.security_decision_ref is not None
        assert admitted.security_decision_ref["resource"] == "tool.read"
        assert admitted.security_epoch_ref.startswith("security-epoch:product:")
        assert admitted.budget_verdict == {"allowed": False, "reason": "budget_owner_resolver_unbound"}
        assert admitted.capability_ids == ()

        snapshot = runtime.start(request)
        assert snapshot.security_summary["decision"] == "block"
        assert snapshot.security_summary["reason"] == "budget_owner_resolver_unbound"
        assert snapshot.budget_verdict == {"allowed": False, "reason": "budget_owner_resolver_unbound"}
    finally:
        _drop_database(engine, admin_engine, database_name)
