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
from zuno.platform.contracts import canonical_sha256
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.postgres_store import PostgresAgentRunStore
from zuno.platform.database.foundation import InfrastructureRepository
from zuno.platform.services.workspace.single_controller_runtime import (
    WorkspaceRuntimeComposition,
    configure_workspace_product_composition,
)
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
        "knowledge_space_ids": ["knowledge-space:case-law"],
        "budget": {
            "max_steps": 8,
            "max_tokens": 4096,
            "timeout_seconds": 120,
        },
        "tool_id": "research.search",
        "tool_arguments": {"jurisdiction": "SG"},
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
                    "tool_id, tool_arguments, data_classification, retention_scope "
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
                    "SELECT event_id, payload FROM infra_outbox_events "
                    "WHERE tenant_id = :tenant_id "
                    "AND aggregate_id = :command_id "
                    "AND topic = 'product.runtime_request.dispatch'"
                ),
                {"tenant_id": tenant_id, "command_id": first.command_id},
            ).mappings().one()

        assert int(spec_count) == 1
        assert durable["goal_text"] == payload["goal"]
        assert durable["runtime_surface"] == "product"
        assert durable["plan_kind"] == "auto"
        assert list(durable["knowledge_space_refs"]) == ["knowledge-space:case-law"]
        assert dict(durable["budget_limits"])["max_tokens"] == 4096
        assert durable["tool_id"] == "research.search"
        assert dict(durable["tool_arguments"]) == {"jurisdiction": "SG"}
        assert durable["data_classification"] == "internal"
        assert durable["retention_scope"] == "CONVERSATION"
        assert outbox["payload"]["runtime_execution_spec_ref"] == durable["runtime_execution_spec_ref"]
        assert outbox["payload"]["runtime_execution_spec_hash"] == durable["spec_hash"]
        assert "goal" not in outbox["payload"]
        assert "budget_limits" not in outbox["payload"]
        assert "budget" not in outbox["payload"]
        assert "tool_arguments" not in outbox["payload"]

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
            tool_id=loaded.tool_id,
            tool_arguments=loaded.tool_arguments,
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
        assert {row["tenant_id"] for row in cross_tenant} == {tenant_id, other_tenant}
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
            tampered_payload = connection.execute(
                text(
                    "UPDATE infra_outbox_events "
                    "SET payload = jsonb_set("
                    "payload, '{runtime_execution_spec_hash}', "
                    "to_jsonb(CAST(:bad_hash AS text)), true"
                    ") WHERE event_id = :event_id "
                    "RETURNING payload"
                ),
                {"bad_hash": "0" * 64, "event_id": outbox["event_id"]},
            ).scalar_one()
            # Keep the Infrastructure outbox envelope internally consistent so
            # this probe reaches the Product-owned spec ref/hash validation
            # rather than failing earlier on generic payload-integrity checks.
            connection.execute(
                text(
                    "UPDATE infra_outbox_events "
                    "SET payload_hash = :payload_hash "
                    "WHERE event_id = :event_id"
                ),
                {
                    "payload_hash": canonical_sha256(dict(tampered_payload)),
                    "event_id": outbox["event_id"],
                },
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

        with engine.begin() as connection:
            restored_payload = connection.execute(
                text(
                    "UPDATE infra_outbox_events "
                    "SET payload = jsonb_set("
                    "jsonb_set(payload, '{runtime_execution_spec_hash}', "
                    "to_jsonb(CAST(:spec_hash AS text)), true), "
                    "'{tenant_id}', to_jsonb(CAST(:foreign_tenant AS text)), true"
                    ") WHERE event_id = :event_id "
                    "RETURNING payload"
                ),
                {
                    "spec_hash": str(spec["spec_hash"]),
                    "foreign_tenant": "tenant-prd-a1-foreign",
                    "event_id": outbox["event_id"],
                },
            ).scalar_one()
            connection.execute(
                text(
                    "UPDATE infra_outbox_events "
                    "SET payload_hash = :payload_hash "
                    "WHERE event_id = :event_id"
                ),
                {
                    "payload_hash": canonical_sha256(dict(restored_payload)),
                    "event_id": outbox["event_id"],
                },
            )

        with pytest.raises(
            ProductPersistenceConflict,
            match="outbox tenant does not match payload",
        ):
            ProductService.consume_runtime_request_dispatch(
                event_id=str(outbox["event_id"]),
                worker_id="worker-prd-a1-foreign-tenant",
                engine=engine,
            )
        with engine.connect() as connection:
            assert int(
                connection.execute(
                    text("SELECT count(*) FROM agent_domain_runs")
                ).scalar_one()
            ) == 0
    finally:
        _drop_database(engine, admin_engine, database_name)


def _configure_prd_a2_runtime(engine: Engine) -> PostgresAgentRunStore:
    store = PostgresAgentRunStore(engine)
    configure_workspace_product_composition(
        WorkspaceRuntimeComposition(
            store=store,
            runtime_dependencies_factory=lambda: RuntimeDependencies(),
        )
    )
    return store


def _submit_simple_prd_a2_request(
    *,
    tenant_id: str,
    workspace_id: str,
    client_request_id: str,
    runtime_request_ref: str,
):
    agent_version_id = ProductService.runtime_agent_version_id(
        surface="product",
        tenant_id=tenant_id,
        workspace_id=workspace_id,
    )
    result = ProductService.submit_runtime_request(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        conversation_id=f"conversation:{client_request_id}",
        principal_id=f"user:{client_request_id}",
        active_agent_version_id=agent_version_id,
        client_request_id=client_request_id,
        runtime_request_ref=runtime_request_ref,
        raw_intent_ref=f"intent:{client_request_id}",
        payload={
            "goal": "Summarize the current record using the canonical runtime.",
            "plan_kind": "simple",
            "budget_limits": {
                "max_steps": 4,
                "max_tokens": 2048,
                "timeout_seconds": 60,
            },
        },
        bootstrap_runtime_agent=True,
        runtime_surface="product",
    )
    return result


def _runtime_dispatch_event_id(engine: Engine, *, tenant_id: str, command_id: str) -> str:
    with engine.connect() as connection:
        return str(
            connection.execute(
                text(
                    "SELECT event_id FROM infra_outbox_events "
                    "WHERE tenant_id = :tenant_id "
                    "AND aggregate_id = :command_id "
                    "AND topic = 'product.runtime_request.dispatch'"
                ),
                {"tenant_id": tenant_id, "command_id": command_id},
            ).scalar_one()
        )


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PRD-A2 PostgreSQL probe is BLOCKED",
)
def test_product_dispatch_starts_one_canonical_runtime_with_stable_binding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-prd-a2"
    workspace_id = "workspace-prd-a2"
    try:
        store = _configure_prd_a2_runtime(engine)
        submitted = _submit_simple_prd_a2_request(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            client_request_id="prd-a2-client-1",
            runtime_request_ref="runtime-request:prd-a2:1",
        )
        event_id = _runtime_dispatch_event_id(
            engine,
            tenant_id=tenant_id,
            command_id=submitted.command_id,
        )

        consumed = ProductService.consume_runtime_request_dispatch(
            event_id=event_id,
            worker_id="worker-prd-a2-1",
            engine=engine,
        )
        assert consumed.outbox_status == "published"
        assert consumed.inbox_first_seen is True
        assert consumed.agent_run_id is not None
        assert consumed.agent_run_id.startswith("run:product-runtime-task:")

        with engine.connect() as connection:
            binding = connection.execute(
                text(
                    "SELECT runtime_request_ref, canonical_task_id, canonical_run_id, "
                    "runtime_execution_spec_ref, runtime_execution_spec_hash "
                    "FROM product_command_receipts "
                    "WHERE tenant_id = :tenant_id AND command_id = :command_id "
                    "AND owner_receipt_ref IS NOT NULL"
                ),
                {"tenant_id": tenant_id, "command_id": submitted.command_id},
            ).mappings().one()
            owner_run = connection.execute(
                text(
                    "SELECT run_id, tenant_id, workspace_id "
                    "FROM agent_domain_runs WHERE run_id = :run_id"
                ),
                {"run_id": binding["canonical_run_id"]},
            ).mappings().one()
            runtime_row = connection.execute(
                text(
                    "SELECT task_id, run_id, workspace_id, user_id, status "
                    "FROM agent_runtime_runs WHERE task_id = :task_id"
                ),
                {"task_id": binding["canonical_task_id"]},
            ).mappings().one()
            outbox_status = connection.execute(
                text("SELECT status FROM infra_outbox_events WHERE event_id = :event_id"),
                {"event_id": event_id},
            ).scalar_one()

        assert binding["runtime_request_ref"] == "runtime-request:prd-a2:1"
        assert binding["canonical_run_id"] == f"run:{binding['canonical_task_id']}"
        assert consumed.agent_run_id == binding["canonical_run_id"]
        assert owner_run == {
            "run_id": binding["canonical_run_id"],
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
        }
        assert runtime_row["task_id"] == binding["canonical_task_id"]
        assert runtime_row["run_id"] == binding["canonical_run_id"]
        assert runtime_row["workspace_id"] == workspace_id
        assert outbox_status == "published"

        snapshot = store.snapshot(str(binding["canonical_task_id"]))
        context = dict(snapshot.state.context_pack or {})
        assert context["run_id"] == binding["canonical_run_id"]
        assert context["tenant_id"] == tenant_id
        assert context["workspace_id"] == workspace_id
        assert context["plan_state"]["status"] == "blocked"
        assert context["budget_verdict"]["allowed"] is False
        runtime_started = [
            event for event in store.events(str(binding["canonical_task_id"]))
            if event.type == "runtime_started"
        ]
        assert len(runtime_started) == 1

        duplicate = ProductService.consume_runtime_request_dispatch(
            event_id=event_id,
            worker_id="worker-prd-a2-duplicate",
            engine=engine,
        )
        assert duplicate.outbox_status == "not_claimed"
        with engine.connect() as connection:
            assert int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM agent_runtime_runs "
                        "WHERE task_id = :task_id"
                    ),
                    {"task_id": binding["canonical_task_id"]},
                ).scalar_one()
            ) == 1
    finally:
        configure_workspace_product_composition(None)
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PRD-A2 PostgreSQL probe is BLOCKED",
)
def test_owner_commit_response_loss_retries_same_canonical_task(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-prd-a2-owner-loss"
    workspace_id = "workspace-prd-a2-owner-loss"
    try:
        _configure_prd_a2_runtime(engine)
        submitted = _submit_simple_prd_a2_request(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            client_request_id="prd-a2-owner-loss",
            runtime_request_ref="runtime-request:prd-a2:owner-loss",
        )
        event_id = _runtime_dispatch_event_id(
            engine,
            tenant_id=tenant_id,
            command_id=submitted.command_id,
        )

        original = ProductService._start_or_recover_canonical_runtime

        def _lost_after_owner_commit(**kwargs):
            raise RuntimeError("fault: response lost after owner commit")

        monkeypatch.setattr(
            ProductService,
            "_start_or_recover_canonical_runtime",
            staticmethod(_lost_after_owner_commit),
        )
        first = ProductService.consume_runtime_request_dispatch(
            event_id=event_id,
            worker_id="worker-prd-a2-owner-loss-1",
            engine=engine,
        )
        assert first.agent_run_status == "runtime_unavailable"
        assert first.outbox_status == "pending"

        with engine.connect() as connection:
            binding = connection.execute(
                text(
                    "SELECT canonical_task_id, canonical_run_id "
                    "FROM product_command_receipts "
                    "WHERE tenant_id = :tenant_id AND command_id = :command_id "
                    "AND owner_receipt_ref IS NOT NULL"
                ),
                {"tenant_id": tenant_id, "command_id": submitted.command_id},
            ).mappings().one()
            assert int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM agent_domain_runs "
                        "WHERE run_id = :run_id"
                    ),
                    {"run_id": binding["canonical_run_id"]},
                ).scalar_one()
            ) == 1
            assert int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM agent_runtime_runs "
                        "WHERE task_id = :task_id"
                    ),
                    {"task_id": binding["canonical_task_id"]},
                ).scalar_one()
            ) == 0

        monkeypatch.setattr(
            ProductService,
            "_start_or_recover_canonical_runtime",
            staticmethod(original),
        )
        second = ProductService.consume_runtime_request_dispatch(
            event_id=event_id,
            worker_id="worker-prd-a2-owner-loss-2",
            engine=engine,
        )
        assert second.outbox_status == "published"
        assert second.inbox_first_seen is False
        assert second.agent_run_id == binding["canonical_run_id"]
        with engine.connect() as connection:
            assert int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM product_command_receipts "
                        "WHERE tenant_id = :tenant_id AND command_id = :command_id "
                        "AND owner_receipt_ref IS NOT NULL"
                    ),
                    {"tenant_id": tenant_id, "command_id": submitted.command_id},
                ).scalar_one()
            ) == 1
            assert int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM agent_runtime_runs "
                        "WHERE task_id = :task_id"
                    ),
                    {"task_id": binding["canonical_task_id"]},
                ).scalar_one()
            ) == 1
    finally:
        configure_workspace_product_composition(None)
        _drop_database(engine, admin_engine, database_name)


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PRD-A2 PostgreSQL probe is BLOCKED",
)
def test_runtime_start_response_loss_redelivery_does_not_duplicate_runtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, admin_engine, database_name = _migrated_database(tmp_path, monkeypatch)
    tenant_id = "tenant-prd-a2-runtime-loss"
    workspace_id = "workspace-prd-a2-runtime-loss"
    try:
        store = _configure_prd_a2_runtime(engine)
        submitted = _submit_simple_prd_a2_request(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            client_request_id="prd-a2-runtime-loss",
            runtime_request_ref="runtime-request:prd-a2:runtime-loss",
        )
        event_id = _runtime_dispatch_event_id(
            engine,
            tenant_id=tenant_id,
            command_id=submitted.command_id,
        )

        original_complete = InfrastructureRepository.complete_outbox
        fault = {"raised": False}

        def _complete_with_response_loss(self, *, event_id: str, worker_id: str):
            if not fault["raised"]:
                fault["raised"] = True
                raise RuntimeError("fault: response lost before outbox completion")
            return original_complete(self, event_id=event_id, worker_id=worker_id)

        monkeypatch.setattr(
            InfrastructureRepository,
            "complete_outbox",
            _complete_with_response_loss,
        )
        with pytest.raises(RuntimeError, match="response lost before outbox completion"):
            ProductService.consume_runtime_request_dispatch(
                event_id=event_id,
                worker_id="worker-prd-a2-runtime-loss-1",
                engine=engine,
            )

        with engine.connect() as connection:
            binding = connection.execute(
                text(
                    "SELECT canonical_task_id, canonical_run_id "
                    "FROM product_command_receipts "
                    "WHERE tenant_id = :tenant_id AND command_id = :command_id "
                    "AND owner_receipt_ref IS NOT NULL"
                ),
                {"tenant_id": tenant_id, "command_id": submitted.command_id},
            ).mappings().one()
            assert int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM agent_runtime_runs "
                        "WHERE task_id = :task_id"
                    ),
                    {"task_id": binding["canonical_task_id"]},
                ).scalar_one()
            ) == 1

        runtime_started_before = [
            event for event in store.events(str(binding["canonical_task_id"]))
            if event.type == "runtime_started"
        ]
        assert len(runtime_started_before) == 1

        monkeypatch.setattr(
            InfrastructureRepository,
            "complete_outbox",
            original_complete,
        )
        with engine.begin() as connection:
            reclaimed = InfrastructureRepository(connection).reclaim_stale_outbox_event(
                event_id=event_id,
                older_than_seconds=0,
            )
        assert reclaimed is True

        replay = ProductService.consume_runtime_request_dispatch(
            event_id=event_id,
            worker_id="worker-prd-a2-runtime-loss-2",
            engine=engine,
        )
        assert replay.outbox_status == "published"
        assert replay.inbox_first_seen is False
        assert replay.agent_run_id == binding["canonical_run_id"]
        runtime_started_after = [
            event for event in store.events(str(binding["canonical_task_id"]))
            if event.type == "runtime_started"
        ]
        assert len(runtime_started_after) == 1
        with engine.connect() as connection:
            assert int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM agent_runtime_runs "
                        "WHERE task_id = :task_id"
                    ),
                    {"task_id": binding["canonical_task_id"]},
                ).scalar_one()
            ) == 1
    finally:
        configure_workspace_product_composition(None)
        _drop_database(engine, admin_engine, database_name)
