from __future__ import annotations

from types import SimpleNamespace
import os
from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

import zuno.platform.database as database_module
from zuno.api.services.completion import CompletionService
from zuno.api.services.product.command_service import ProductService
from zuno.platform.database.product import (
    ProductPersistenceConflict,
    ProductRuntimeExecutionSpecInput,
    ProductUnitOfWork,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _migrated_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Engine, Engine, str]:
    raw_url = os.environ.get("ZUNO_TEST_DATABASE_URL")
    if not raw_url:
        pytest.skip("ZUNO_TEST_DATABASE_URL is not configured; PRD-A1 PostgreSQL probe is BLOCKED")

    base_url = make_url(raw_url)
    database_name = f"zuno_prd_a1_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    database_url = base_url.set(database=database_name)
    config_path = tmp_path / "prd-a1-config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {"database": {"sync_endpoint": database_url.render_as_string(hide_password=False)}}
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ZUNO_CONFIG", str(config_path))

    alembic_config = Config(str(REPO_ROOT / "infra/db/alembic.ini"))
    command.upgrade(alembic_config, "head")
    engine = create_engine(database_url)
    monkeypatch.setattr(database_module, "engine", engine)
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


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PRD-A1 PostgreSQL probe is BLOCKED",
)
def test_runtime_execution_spec_is_durable_replay_safe_and_tenant_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-prd-a1"
    workspace_id = "workspace-prd-a1"
    client_request_id = "prd-a1-client-1"
    runtime_request_ref = "runtime-request:prd-a1:shared"
    payload = {
        "goal": "Find the controlling authorities for the filing deadline.",
        "plan_kind": "default",
        "knowledge_space_refs": ["knowledge-space:case-law"],
        "budget_limits": {
            "max_steps": 8,
            "max_tokens": 4096,
            "timeout_seconds": 120,
        },
    }
    try:
        agent_version_id = ProductService.runtime_agent_version_id(
            surface="product",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
        )
        common = {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "conversation_id": "conversation-prd-a1",
            "principal_id": "user-prd-a1",
            "active_agent_version_id": agent_version_id,
            "client_request_id": client_request_id,
            "runtime_request_ref": runtime_request_ref,
            "raw_intent_ref": "intent-prd-a1",
            "payload": payload,
            "bootstrap_runtime_agent": True,
            "runtime_surface": "product",
        }
        first = ProductService.submit_runtime_request(**common)
        replay = ProductService.submit_runtime_request(**common)
        assert first.status == "ACCEPTED"
        assert replay.status == "DUPLICATE"

        with engine.connect() as connection:
            durable = connection.execute(
                text(
                    "SELECT runtime_execution_spec_ref, spec_hash, content_fingerprint, "
                    "goal_text, runtime_surface, plan_kind, knowledge_space_refs, budget_limits, "
                    "data_classification, retention_scope "
                    "FROM product_runtime_execution_specs "
                    "WHERE tenant_id = :tenant_id AND runtime_request_ref = :runtime_request_ref"
                ),
                {"tenant_id": tenant_id, "runtime_request_ref": runtime_request_ref},
            ).mappings().one()
            spec_count = connection.execute(
                text(
                    "SELECT count(*) FROM product_runtime_execution_specs "
                    "WHERE tenant_id = :tenant_id AND runtime_request_ref = :runtime_request_ref"
                ),
                {"tenant_id": tenant_id, "runtime_request_ref": runtime_request_ref},
            ).scalar_one()
            outbox = connection.execute(
                text(
                    "SELECT payload FROM infra_outbox_events "
                    "WHERE tenant_id = :tenant_id AND event_id = :event_id"
                ),
                {"tenant_id": tenant_id, "event_id": f"outbox:{client_request_id}"},
            ).mappings().one()

        assert int(spec_count) == 1
        assert durable["goal_text"] == payload["goal"]
        assert durable["runtime_surface"] == "product"
        assert durable["plan_kind"] == "default"
        assert list(durable["knowledge_space_refs"]) == ["knowledge-space:case-law"]
        assert dict(durable["budget_limits"])["max_tokens"] == 4096
        assert durable["data_classification"] == "internal"
        assert durable["retention_scope"] == "CONVERSATION"
        assert outbox["payload"]["runtime_execution_spec_ref"] == durable["runtime_execution_spec_ref"]
        assert outbox["payload"]["runtime_execution_spec_hash"] == durable["spec_hash"]
        assert "goal" not in outbox["payload"]
        assert "budget_limits" not in outbox["payload"]

        with ProductUnitOfWork(engine) as repo:
            loaded = repo.get_runtime_execution_spec(
                tenant_id=tenant_id,
                runtime_execution_spec_ref=str(durable["runtime_execution_spec_ref"]),
                expected_spec_hash=str(durable["spec_hash"]),
            )
        assert loaded.goal_text == payload["goal"]
        assert loaded.content_fingerprint == durable["content_fingerprint"]

        changed = ProductRuntimeExecutionSpecInput(
            runtime_execution_spec_ref=loaded.runtime_execution_spec_ref,
            runtime_request_ref=loaded.runtime_request_ref,
            tenant_id=loaded.tenant_id,
            workspace_id=loaded.workspace_id,
            conversation_id=loaded.conversation_id,
            principal_id=loaded.principal_id,
            submission_id=loaded.submission_id,
            client_request_id=loaded.client_request_id,
            active_agent_version_id=loaded.active_agent_version_id,
            goal_material_ref=loaded.goal_material_ref,
            goal_text=loaded.goal_text + " Changed after submission.",
            runtime_surface=loaded.runtime_surface,
            plan_kind=loaded.plan_kind,
            knowledge_space_refs=loaded.knowledge_space_refs,
            budget_limits=loaded.budget_limits,
            data_classification=loaded.data_classification,
            retention_scope=loaded.retention_scope,
            spec_version=loaded.spec_version,
        )
        with pytest.raises(
            ProductPersistenceConflict,
            match="RuntimeExecutionSpec identity was reused with different content",
        ):
            with ProductUnitOfWork(engine) as repo:
                repo.ensure_runtime_execution_spec(changed)

        other_tenant = "tenant-prd-a1-other"
        other_agent_version = ProductService.runtime_agent_version_id(
            surface="product",
            tenant_id=other_tenant,
            workspace_id=workspace_id,
        )
        ProductService.submit_runtime_request(
            tenant_id=other_tenant,
            workspace_id=workspace_id,
            conversation_id="conversation-prd-a1-other",
            principal_id="user-prd-a1-other",
            active_agent_version_id=other_agent_version,
            client_request_id=client_request_id,
            runtime_request_ref=runtime_request_ref,
            raw_intent_ref="intent-prd-a1-other",
            payload=payload,
            bootstrap_runtime_agent=True,
            runtime_surface="product",
        )
        with engine.connect() as connection:
            cross_tenant = connection.execute(
                text(
                    "SELECT tenant_id, runtime_execution_spec_ref "
                    "FROM product_runtime_execution_specs "
                    "WHERE runtime_request_ref = :runtime_request_ref ORDER BY tenant_id"
                ),
                {"runtime_request_ref": runtime_request_ref},
            ).mappings().all()
        assert [row["tenant_id"] for row in cross_tenant] == [other_tenant, tenant_id]
        assert len({row["runtime_execution_spec_ref"] for row in cross_tenant}) == 2

        with pytest.raises(ValueError, match="must not persist secret material"):
            ProductService.submit_runtime_request(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                conversation_id="conversation-prd-a1-secret",
                principal_id="user-prd-a1",
                active_agent_version_id=agent_version_id,
                client_request_id="prd-a1-secret",
                runtime_request_ref="runtime-request:prd-a1:secret",
                raw_intent_ref="intent-prd-a1-secret",
                payload={"goal": "Use api_key = super-secret-value to query the provider."},
                bootstrap_runtime_agent=True,
                runtime_surface="product",
            )
        with engine.connect() as connection:
            secret_count = connection.execute(
                text(
                    "SELECT count(*) FROM product_runtime_execution_specs "
                    "WHERE tenant_id = :tenant_id AND client_request_id = 'prd-a1-secret'"
                ),
                {"tenant_id": tenant_id},
            ).scalar_one()
        assert int(secret_count) == 0
    finally:
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PRD-A1 PostgreSQL probe is BLOCKED",
)
def test_completion_goal_is_restart_safe_and_dispatch_rejects_spec_hash_tamper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-prd-a1-completion"
    workspace_id = "workspace-prd-a1-completion"
    goal = "Summarize the governing rule and cite the controlling authority."
    try:
        req = SimpleNamespace(
            workspace_id=workspace_id,
            dialog_id="dialog-prd-a1-completion",
            user_input=goal,
            product_mode="legal_research",
            query_method="standard",
        )
        recorded = CompletionService.record_product_runtime_request(
            req=req,
            login_user_id="user-prd-a1-completion",
            tenant_id=tenant_id,
        )
        assert recorded["product_runtime_recorded"] is True
        assert recorded["status"] == "ACCEPTED"

        with engine.connect() as connection:
            spec = connection.execute(
                text(
                    "SELECT runtime_execution_spec_ref, runtime_request_ref, spec_hash, "
                    "goal_text, runtime_surface FROM product_runtime_execution_specs "
                    "WHERE tenant_id = :tenant_id"
                ),
                {"tenant_id": tenant_id},
            ).mappings().one()
            outbox = connection.execute(
                text(
                    "SELECT event_id, payload FROM infra_outbox_events "
                    "WHERE tenant_id = :tenant_id AND topic = 'product.runtime_request.dispatch'"
                ),
                {"tenant_id": tenant_id},
            ).mappings().one()

        assert spec["goal_text"] == goal
        assert spec["runtime_surface"] == "completion"
        assert outbox["payload"]["runtime_execution_spec_ref"] == spec["runtime_execution_spec_ref"]
        assert outbox["payload"]["runtime_execution_spec_hash"] == spec["spec_hash"]
        assert "goal" not in outbox["payload"]
        assert "user_input" not in outbox["payload"]

        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE infra_outbox_events "
                    "SET payload = jsonb_set("
                    "payload, '{runtime_execution_spec_hash}', "
                    "to_jsonb(CAST(:bad_hash AS text)), true"
                    ") WHERE event_id = :event_id"
                ),
                {"bad_hash": "0" * 64, "event_id": outbox["event_id"]},
            )

        with pytest.raises(
            ProductPersistenceConflict,
            match="RuntimeExecutionSpec hash does not match durable fact",
        ):
            ProductService.consume_runtime_request_dispatch(
                event_id=str(outbox["event_id"]),
                worker_id="worker-prd-a1",
                engine=engine,
            )

        with engine.connect() as connection:
            agent_run_count = connection.execute(
                text(
                    "SELECT count(*) FROM agent_domain_runs "
                    "WHERE tenant_id = :tenant_id"
                ),
                {"tenant_id": tenant_id},
            ).scalar_one()
            outbox_status = connection.execute(
                text(
                    "SELECT status FROM infra_outbox_events WHERE event_id = :event_id"
                ),
                {"event_id": outbox["event_id"]},
            ).scalar_one()
        assert int(agent_run_count) == 0
        assert outbox_status == "pending"
    finally:
        _drop_database(engine, admin_engine, database_name)
