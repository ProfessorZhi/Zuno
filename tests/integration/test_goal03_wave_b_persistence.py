from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.database.memory import ContextPackInput, MemoryRepository, MemoryUnitOfWork, MemoryVersionInput
from zuno.platform.database.tool_runtime import (
    PreparedToolActionInput,
    ToolAttemptInput,
    ToolExecutionReceiptInput,
    ToolObservationInput,
    ToolRepository,
    ToolUnitOfWork,
    ToolVersionInput,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    env = {
        **os.environ,
        "PGCONNECT_TIMEOUT": os.environ.get("PGCONNECT_TIMEOUT", "5"),
        "ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS": os.environ.get("ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS", "5"),
    }
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    tool_bypass_guard_receipts,
                    tool_adapter_bindings,
                    tool_execution_receipts,
                    tool_observations,
                    tool_attempts,
                    prepared_tool_actions,
                    tool_activations,
                    tool_installations,
                    tool_operations,
                    tool_versions,
                    tool_definitions,
                    tool_providers,
                    memory_reconciliation_decisions,
                    memory_use_traces,
                    context_compression_traces,
                    context_selection_decisions,
                    memory_commit_receipts,
                    memory_records,
                    memory_governance_decisions_v2,
                    memory_candidates_v2,
                    memory_capture_intents,
                    memory_deletion_receipts,
                    memory_deletion_requests,
                    context_pack_versions,
                    memory_manifest_snapshots,
                    memory_snapshots,
                    memory_versions
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def test_phase13_memory_repository_activates_immutable_context_pack_and_delete_receipt(engine) -> None:
    with MemoryUnitOfWork(engine) as repo:
        assert isinstance(repo, MemoryRepository)
        repo.publish_memory_version(
            MemoryVersionInput(
                memory_version_id="memory-version:wave-b:1",
                tenant_id="tenant-b",
                workspace_id="workspace-b",
                memory_scope_ref="memory-scope:user-b",
                memory_kind="SEMANTIC",
                version_no=1,
                content_ref="object://memory/wave-b/1",
                source_refs=("event:turn:1",),
                confidence=0.87,
                content_payload={"content": "User prefers cited answers."},
            )
        )
        repo.activate_memory_version(
            memory_version_id="memory-version:wave-b:1",
            expected_generation=1,
            snapshot_payload={"memory_version_id": "memory-version:wave-b:1", "state": "active"},
            serving_watermark_ref="watermark:memory:1",
        )
        repo.build_context_pack(
            pack=ContextPackInput(
                context_pack_id="context-pack:wave-b:1",
                tenant_id="tenant-b",
                workspace_id="workspace-b",
                run_id="run:wave-b",
                step_run_id="step:memory",
                memory_version_id="memory-version:wave-b:1",
                budget_tokens=256,
                selection_payload={"recency": "recent", "relevance": 0.91, "sensitivity": "safe"},
                compression_payload={"level": "F2", "fidelity_check": "passed"},
                trace_payload={"trace_id": "trace:wave-b", "source_event_ids": ["event:turn:1"]},
            )
        )
        repo.request_delete(
            deletion_request_id="memory-delete:wave-b:1",
            tenant_id="tenant-b",
            workspace_id="workspace-b",
            memory_scope_ref="memory-scope:user-b",
            requested_by="user-b",
            reason="privacy_delete_request",
        )
        repo.complete_delete(
            deletion_receipt_id="memory-delete-receipt:wave-b:1",
            deletion_request_id="memory-delete:wave-b:1",
            tenant_id="tenant-b",
            workspace_id="workspace-b",
            deleted_payload={"memory_version_id": "memory-version:wave-b:1"},
            verification_payload={"verified": True},
        )

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT status, generation, current_snapshot_ref
                FROM memory_versions
                WHERE memory_version_id = 'memory-version:wave-b:1'
                """
            )
        ).mappings().one()
        assert row["status"] == "ACTIVE"
        assert row["generation"] == 2
        assert row["current_snapshot_ref"] == "memory-snapshot:memory-version:wave-b:1"
        assert conn.execute(text("SELECT count(*) FROM context_pack_versions")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM memory_deletion_receipts")).scalar_one() == 1


def test_phase13_governed_memory_runtime_commits_default_agent_outcome_context_and_use_trace(engine) -> None:
    from zuno.memory.contracts import MemoryScope
    from zuno.memory.governed_runtime import GovernedMemoryContextRuntime

    runtime = GovernedMemoryContextRuntime(unit_of_work_factory=lambda: MemoryUnitOfWork(engine))
    receipt = runtime.commit_turn_outcome(
        scope=MemoryScope(
            user_id="tenant-b",
            agent_id="agent-b",
            project_id="workspace-b",
            thread_id="thread-b",
        ),
        event_id="event:wave-b:post-turn",
        run_id="run:wave-b:governed",
        step_run_id="step:post-turn",
        task="Remember the governed runtime boundary.",
        response="Governed memory committed.",
        context_trace={"selected_item_ids": ["message_0"], "security_epoch": "security-epoch:memory-default"},
    )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM memory_capture_intents")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM memory_candidates_v2")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM memory_governance_decisions_v2")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM memory_records")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM memory_commit_receipts")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM context_selection_decisions")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM context_compression_traces")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM memory_use_traces")).scalar_one() == 1
        active = conn.execute(
            text("SELECT status, current_snapshot_ref FROM memory_versions WHERE memory_version_id = :version_id"),
            {"version_id": receipt.memory_version_id},
        ).mappings().one()
        assert active["status"] == "ACTIVE"
        assert active["current_snapshot_ref"].startswith("memory-snapshot:")


def test_phase15_tool_repository_records_readonly_prepared_action_attempt_and_receipt(engine) -> None:
    tool_version_id = "tool-version:filesystem.read:v1"
    tool_operation_id = f"{tool_version_id}:operation:default"

    with ToolUnitOfWork(engine) as repo:
        assert isinstance(repo, ToolRepository)
        repo.publish_tool_version(
            ToolVersionInput(
                tool_definition_id="tool-definition:filesystem.read",
                tool_version_id=tool_version_id,
                tenant_id="tenant-b",
                version_no=1,
                input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                output_schema={"type": "object"},
                adapter_kind="LOCAL_FUNCTION",
                effect_level="READ_ONLY",
            )
        )
        repo.install_tool(
            tool_installation_id="tool-installation:filesystem.read",
            tenant_id="tenant-b",
            workspace_id="workspace-b",
            tool_version_id=tool_version_id,
            policy_ref="policy:readonly",
        )
        repo.activate_tool(
            tool_activation_id="tool-activation:filesystem.read",
            tenant_id="tenant-b",
            workspace_id="workspace-b",
            tool_installation_id="tool-installation:filesystem.read",
            expected_generation=1,
            activation_payload={"activation": "readonly-default"},
        )
        repo.prepare_action(
            PreparedToolActionInput(
                prepared_tool_action_id="prepared-tool-action:read:1",
                tenant_id="tenant-b",
                workspace_id="workspace-b",
                tool_operation_id=tool_operation_id,
                canonical_args={"path": "docs/architecture/README.md"},
                target_resources=("workspace://docs/architecture/README.md",),
                effect_level="READ_ONLY",
                approval_required=False,
                idempotency_key="idem:readonly:read:1",
                security_epoch_ref="security-epoch:readonly:1",
                status="READY",
            )
        )
        repo.record_attempt(
            ToolAttemptInput(
                attempt_id="tool-attempt:read:1",
                tenant_id="tenant-b",
                prepared_tool_action_id="prepared-tool-action:read:1",
                status="SUCCEEDED",
                dispatch_certainty="DISPATCHED",
                adapter_family="CLI",
                hidden_retry_count=0,
                state_history=("STARTED", "SUCCEEDED"),
            )
        )
        repo.record_observation(
            ToolObservationInput(
                observation_id="tool-observation:read:1",
                tenant_id="tenant-b",
                attempt_id="tool-attempt:read:1",
                owner_module="08 Tool Runtime",
                normalized_projection_owner="06 Agent Core / Planning & Control",
                output_trusted=False,
                schema_valid=True,
                memory_write_allowed=False,
                evidence_write_allowed=False,
                payload={"status": "success", "content": "read-only"},
            )
        )
        repo.record_execution_receipt(
            ToolExecutionReceiptInput(
                receipt_id="tool-execution-receipt:read:1",
                tenant_id="tenant-b",
                prepared_tool_action_id="prepared-tool-action:read:1",
                attempt_id="tool-attempt:read:1",
                status="SUCCEEDED",
                dispatch_certainty="DISPATCHED",
                effect_certainty="NO_EFFECT",
                append_only_generation=1,
                receipt_payload={"adapter_receipt_ref": "local-read:1"},
            )
        )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM tool_providers")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM tool_definitions")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM tool_operations")).scalar_one() == 1
        status = conn.execute(text("SELECT status FROM prepared_tool_actions")).scalar_one()
        assert status == "READY"
        receipt = conn.execute(
            text("SELECT effect_certainty, append_only_generation FROM tool_execution_receipts")
        ).mappings().one()
        assert receipt["effect_certainty"] == "NO_EFFECT"
        assert receipt["append_only_generation"] == 1


def test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects(engine) -> None:
    from zuno.capability.runtime import ToolRuntimeRequest, build_default_tool_control_plane_runtime

    runtime = build_default_tool_control_plane_runtime()
    runtime._tool_unit_of_work_factory = lambda: ToolUnitOfWork(engine)

    read_result = runtime.execute(
        ToolRuntimeRequest(
            tool_id="filesystem.read",
            arguments={"path": "docs/architecture/README.md"},
            workspace_id="workspace-b",
            user_id="tenant-b",
            task_id="task-readonly",
            trace_id="trace-readonly",
            model_intent="Read a workspace document.",
            execution_id="readonly-read-1",
        )
    )
    write_result = runtime.execute(
        ToolRuntimeRequest(
            tool_id="mail.send",
            arguments={"to": "review@example.com", "body": "hello", "target": "mailto:review@example.com"},
            workspace_id="workspace-b",
            user_id="tenant-b",
            task_id="task-mail",
            trace_id="trace-mail",
            model_intent="Send email.",
            approved=True,
            execution_id="readonly-mail-1",
        )
    )

    assert read_result.status == "completed"
    assert write_result.status == "blocked"
    assert "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL" in repr(write_result.to_dict())

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM prepared_tool_actions")).scalar_one() == 2
        assert conn.execute(text("SELECT count(*) FROM tool_attempts")).scalar_one() == 2
        assert conn.execute(text("SELECT count(*) FROM tool_observations")).scalar_one() == 2
        assert conn.execute(text("SELECT count(*) FROM tool_execution_receipts")).scalar_one() == 2
        assert conn.execute(text("SELECT count(*) FROM tool_adapter_bindings")).scalar_one() >= 1
        assert conn.execute(text("SELECT count(*) FROM tool_bypass_guard_receipts")).scalar_one() == 2
        statuses = conn.execute(
            text("SELECT status, effect_certainty FROM tool_execution_receipts ORDER BY receipt_id")
        ).all()
        assert ("FAILED", "NO_EFFECT") in [(row.status, row.effect_certainty) for row in statuses]
