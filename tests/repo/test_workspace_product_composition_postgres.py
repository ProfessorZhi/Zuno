from __future__ import annotations

import asyncio
import os
from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

from zuno.agent.harness import ControllerRuntimeState, RuntimeCheckpoint, RuntimeInterrupt
from zuno.agent.runtime.postgres_store import PostgresAgentRunStore


REPO_ROOT = Path(__file__).resolve().parents[2]


def _migrated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Engine, Engine, str]:
    raw_url = os.environ.get("ZUNO_TEST_DATABASE_URL")
    if not raw_url:
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; PSC-A PostgreSQL probe is BLOCKED")

    base_url = make_url(raw_url)
    database_name = f"zuno_psc_a_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "psc-a-config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {"database": {"sync_endpoint": database_url.render_as_string(hide_password=False)}}
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ZUNO_CONFIG", str(config_path))

    alembic_config = Config(str(REPO_ROOT / "infra/db/alembic.ini"))
    command.upgrade(alembic_config, "head")
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


def _state(task_id: str = "psc-a-task") -> ControllerRuntimeState:
    return ControllerRuntimeState(
        thread_id="psc-a-thread",
        workspace_id="workspace-psc-a",
        user_id="user-psc-a",
        task_id=task_id,
        trace_id="trace-psc-a",
        goal="verify PostgreSQL runtime persistence",
        context_pack={"tenant_id": "tenant-psc-a"},
    )


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PSC-A PostgreSQL probe is BLOCKED",
)
def test_postgres_agent_run_store_survives_new_store_instance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    state = _state()
    try:
        first = PostgresAgentRunStore(engine)
        first.create_task(state)
        first.save_checkpoint(
            RuntimeCheckpoint(
                checkpoint_id="checkpoint:psc-a:1",
                thread_id=state.thread_id,
                task_id=state.task_id,
                trace_id=state.trace_id,
                node="planning",
                state=state.to_dict(),
                payload={"route": "execute"},
            )
        )
        first.save_interrupt(
            RuntimeInterrupt(
                interrupt_id="interrupt:psc-a:1",
                thread_id=state.thread_id,
                task_id=state.task_id,
                trace_id=state.trace_id,
                node="tool",
                reason="approval required",
                required_approval="tool:mail.send",
                payload={"idempotency_key": "psc-a-idem"},
                resumable=True,
            )
        )

        restarted = PostgresAgentRunStore(engine)
        assert restarted.has_task(state.task_id)
        snapshot = restarted.snapshot(state.task_id)
        assert snapshot.workspace_id == state.workspace_id
        assert snapshot.latest_checkpoint is not None
        assert snapshot.latest_checkpoint.checkpoint_id == "checkpoint:psc-a:1"
        assert snapshot.pending_interrupt is not None
        assert snapshot.pending_interrupt.interrupt_id == "interrupt:psc-a:1"
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PSC-A PostgreSQL probe is BLOCKED",
)
def test_fastapi_init_config_binds_real_workspace_product_composition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    try:
        import zuno.main as app_main
        import zuno.platform.database as database_module
        import zuno.platform.database.init_data as init_data
        import zuno.api.services.product as product_services
        from zuno.api.services.product.runtime_engine import ProductRuntimeMechanics
        from zuno.platform.services.workspace.single_controller_runtime import (
            get_workspace_product_composition,
        )

        async def _async_noop(*args, **kwargs):
            return None

        async def _database_ready(*args, **kwargs):
            return True

        monkeypatch.setattr(database_module, "engine", engine)
        monkeypatch.setattr(app_main, "initialize_app_settings", _async_noop)
        monkeypatch.setattr(app_main, "configure_langsmith", lambda: None)
        monkeypatch.setattr(init_data, "init_database", _database_ready)
        monkeypatch.setattr(init_data, "init_default_agent", _async_noop)
        monkeypatch.setattr(init_data, "update_system_mcp_server", _async_noop)
        monkeypatch.setattr(init_data, "upload_user_avatars_storage", _async_noop)
        monkeypatch.setattr(
            product_services,
            "build_package_a_production_ingestion_runtime",
            lambda **kwargs: None,
        )
        monkeypatch.setattr(
            product_services,
            "resolve_package_a_upload_bucket",
            lambda settings: "psc-a-test-bucket",
        )

        ProductRuntimeMechanics.reset_runtime_state_for_tests()
        assert get_workspace_product_composition() is None

        # Missing TTL keeps PSC-B fail-closed even though PSC-A composition is bound.
        monkeypatch.setattr(app_main.app_settings, "server", {})
        unbound_security = app_main.configure_workspace_product_runtime(engine)
        assert unbound_security.security_decision_resolver is None
        ProductRuntimeMechanics.reset_runtime_state_for_tests()

        # An explicit server policy TTL enables the Security owner port on the
        # same production startup path; Budget/Approval remain separate slices.
        monkeypatch.setattr(
            app_main.app_settings,
            "server",
            {"security": {"product_decision_ttl_seconds": 300}},
        )
        asyncio.run(app_main.init_config())

        composition = get_workspace_product_composition()
        assert composition is not None
        assert isinstance(composition.store, PostgresAgentRunStore)
        assert composition.tool_unit_of_work_factory is not None
        assert composition.security_unit_of_work_factory is not None
        assert composition.infrastructure_unit_of_work_factory is not None
        assert composition.security_approval_sink is None
        from zuno.platform.security.decision_resolvers import PostgresSecurityDecisionResolver
        assert isinstance(composition.security_decision_resolver, PostgresSecurityDecisionResolver)
        assert composition.budget_decision_resolver is None
        assert composition.approval_flow == "none"

        state = _state("psc-a-startup-task")
        composition.store.create_task(state)
        assert PostgresAgentRunStore(engine).has_task(state.task_id)

        ProductRuntimeMechanics.reset_runtime_state_for_tests()
        assert get_workspace_product_composition() is None
    finally:
        from zuno.platform.services.workspace.single_controller_runtime import (
            configure_workspace_product_composition,
        )

        configure_workspace_product_composition(None)
        _drop_database(engine, admin_engine, database_name)
