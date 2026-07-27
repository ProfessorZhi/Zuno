from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.capability.tool_runtime.effect_policy import classify_tool_effect
from zuno.capability.tool_runtime.invocation_gateway import ToolEffectUnknownError, ToolInvocationGateway

from zuno.platform.contracts import canonical_sha256
from zuno.platform.security import SecurityPersistenceError, SecurityUnitOfWork, redact_sensitive_payload
from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine
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
                    infra_worker_leases,
                    infra_idempotency_claims,
                    security_approval_decisions,
                    security_approval_requests,
                    security_audit_requirements,
                    security_authorization_decisions,
                    security_principal_contexts,
                    security_effective_epochs,
                    security_secret_leases,
                    security_secret_refs,
                    tool_compensation_attempts,
                    tool_compensation_definitions,
                    tool_manual_effect_assessments,
                    tool_cancellation_receipts,
                    tool_async_callbacks,
                    tool_async_jobs,
                    tool_effect_reconciliations,
                    tool_effect_receipts,
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


def test_phase16_default_tool_runtime_records_readonly_gateway_and_executes_approved_side_effects(engine) -> None:
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
    write_replay = runtime.execute(
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
    assert write_result.status == "completed"
    assert write_replay.status == "completed"
    assert write_result.normalized_result is not None
    assert write_result.normalized_result.data["message_id"] == "msg_123"
    assert write_replay.normalized_result is not None
    assert write_replay.normalized_result.data["idempotency_replay"] is True
    assert write_replay.normalized_result.data["result_ref"] == "tool-effect-receipt:readonly-mail-1"

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
        effect = conn.execute(
            text(
                """
                SELECT provider_effect_id, effect_status, effect_certainty, secret_lease_id
                FROM tool_effect_receipts
                WHERE effect_receipt_id = 'tool-effect-receipt:readonly-mail-1'
                """
            )
        ).mappings().one()
        claim = conn.execute(
            text(
                """
                SELECT status, result_ref
                FROM infra_idempotency_claims
                WHERE tenant_id = 'tenant-b'
                  AND scope = 'tool-side-effect'
                  AND idempotency_key = 'readonly-mail-1'
                """
            )
        ).mappings().one()
        assert conn.execute(
            text("SELECT count(*) FROM security_secret_leases WHERE lease_id = 'security-secret-lease:readonly-mail-1'")
        ).scalar_one() == 1
        assert conn.execute(
            text("SELECT count(*) FROM tool_effect_receipts WHERE effect_receipt_id = 'tool-effect-receipt:readonly-mail-1'")
        ).scalar_one() == 1
        assert ("SUCCEEDED", "CONFIRMED_EFFECT") in [(row.status, row.effect_certainty) for row in statuses]
        assert effect["provider_effect_id"] == "provider-effect:readonly-mail-1"
        assert effect["effect_status"] == "CONFIRMED"
        assert effect["effect_certainty"] == "CONFIRMED_EFFECT"
        assert effect["secret_lease_id"] == "security-secret-lease:readonly-mail-1"
        assert claim["status"] == "completed"
        assert claim["result_ref"] == "tool-effect-receipt:readonly-mail-1"


def test_phase16_gateway_records_side_effect_classification_before_blocking(engine) -> None:
    gateway = ToolInvocationGateway(unit_of_work_factory=lambda: ToolUnitOfWork(engine))
    dispatched = False

    async def executor() -> str:
        nonlocal dispatched
        dispatched = True
        return "sent"

    result, receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello"},
        tenant_id="tenant-phase16",
        workspace_id="workspace-phase16",
        trace_id="trace-phase16",
        call_id="call-phase16-mail",
        adapter_kind="API",
        executor=executor,
        readonly=False,
    ))

    assert result is None
    assert dispatched is False
    assert receipt.status == "blocked"
    assert receipt.blocked_reason == "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL"

    with engine.connect() as conn:
        prepared = conn.execute(
            text(
                """
                SELECT effect_level, status, approval_required, prepared_action_hash
                FROM prepared_tool_actions
                WHERE prepared_tool_action_id = 'prepared-tool-action:call-phase16-mail'
                """
            )
        ).mappings().one()
        version = conn.execute(
            text(
                """
                SELECT effect_level
                FROM tool_versions
                WHERE tool_version_id = 'tool-version:mail.send:v1'
                """
            )
        ).mappings().one()
        observation = conn.execute(
            text(
                """
                SELECT redacted_payload_hash
                FROM tool_observations
                WHERE observation_id = 'tool-observation:tool-attempt:call-phase16-mail'
                """
            )
        ).mappings().one()

    effect_policy = classify_tool_effect(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello"},
        readonly=False,
        adapter_kind="API",
    )
    expected_hash = canonical_sha256(
        {
            "action_proposal_ref": "action-proposal:call-phase16-mail",
            "tool_operation_id": "tool-version:mail.send:v1:operation:default",
            "canonical_args": redact_sensitive_payload({"to": "review@example.com", "body": "hello"}),
            "target_resources": list(effect_policy.target_resource_set.resource_refs),
            "target_resource_set_ref": effect_policy.target_resource_set.resource_set_ref,
            "target_conflict_keys": list(effect_policy.target_resource_set.conflict_keys),
            "effect_level": effect_policy.effect_level,
            "effect_policy_version": effect_policy.policy_version,
            "effect_policy_hash": effect_policy.policy_hash,
            "approval_required": effect_policy.approval_required,
            "security_epoch_ref": "security-epoch:trace-phase16",
            "idempotency_key": "call-phase16-mail",
        }
    )

    assert prepared["effect_level"] == "IRREVERSIBLE_WRITE"
    assert prepared["status"] == "OBSOLETE"
    assert prepared["approval_required"] is True
    assert prepared["prepared_action_hash"] == expected_hash
    assert version["effect_level"] == "IRREVERSIBLE_WRITE"
    assert observation["redacted_payload_hash"] == canonical_sha256(
        {
            "blocked": True,
            "reason": "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL",
            "effect_class": "IRREVERSIBLE_WRITE",
            "target_resource_set_ref": effect_policy.target_resource_set.resource_set_ref,
            "target_conflict_keys": list(effect_policy.target_resource_set.conflict_keys),
        }
    )

def test_phase16_gateway_binds_security_prepare_to_prepared_action_hash(engine) -> None:
    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
    )
    dispatched = False

    async def executor() -> str:
        nonlocal dispatched
        dispatched = True
        return "sent"

    result, receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello"},
        tenant_id="tenant-phase16-security",
        workspace_id="workspace-phase16-security",
        trace_id="trace-phase16-security",
        call_id="call-phase16-security-mail",
        adapter_kind="API",
        executor=executor,
        readonly=False,
    ))

    assert result is None
    assert dispatched is False
    assert receipt.status == "blocked"

    with engine.connect() as conn:
        prepared_hash = conn.execute(
            text(
                """
                SELECT prepared_action_hash
                FROM prepared_tool_actions
                WHERE prepared_tool_action_id = 'prepared-tool-action:call-phase16-security-mail'
                """
            )
        ).scalar_one()
        auth = conn.execute(
            text(
                """
                SELECT decision, reason_code, prepared_action_hash
                FROM security_authorization_decisions
                WHERE decision_id = 'authorization-decision:call-phase16-security-mail'
                """
            )
        ).mappings().one()
        approval = conn.execute(
            text(
                """
                SELECT status, prepared_action_hash
                FROM security_approval_requests
                WHERE approval_request_id = 'approval-request:call-phase16-security-mail'
                """
            )
        ).mappings().one()
        observation_hash = conn.execute(
            text(
                """
                SELECT redacted_payload_hash
                FROM tool_observations
                WHERE observation_id = 'tool-observation:tool-attempt:call-phase16-security-mail'
                """
            )
        ).scalar_one()

    assert auth["decision"] == "REQUIRES_APPROVAL"
    assert auth["reason_code"] == "side_effect_requires_approval"
    assert auth["prepared_action_hash"] == prepared_hash
    assert approval["status"] == "pending"
    assert approval["prepared_action_hash"] == prepared_hash
    assert observation_hash == canonical_sha256(
        {
            "blocked": True,
            "reason": "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL",
            "effect_class": "IRREVERSIBLE_WRITE",
            "target_resource_set_ref": classify_tool_effect(
                tool_name="mail.send",
                args={"to": "review@example.com", "body": "hello"},
                readonly=False,
                adapter_kind="API",
            ).target_resource_set.resource_set_ref,
            "target_conflict_keys": list(
                classify_tool_effect(
                    tool_name="mail.send",
                    args={"to": "review@example.com", "body": "hello"},
                    readonly=False,
                    adapter_kind="API",
                ).target_resource_set.conflict_keys
            ),
            "security_blocked_reason": "approval required before effect",
        }
    )

    with SecurityUnitOfWork(engine) as repo:
        with pytest.raises(SecurityPersistenceError, match="prepared action hash changed before effect"):
            repo.validate_pre_effect_authorization(
                decision_id="authorization-decision:call-phase16-security-mail",
                tenant_id="tenant-phase16-security",
                prepared_action_hash="0" * 64,
            )
        with pytest.raises(SecurityPersistenceError, match="approval required before effect"):
            repo.validate_pre_effect_authorization(
                decision_id="authorization-decision:call-phase16-security-mail",
                tenant_id="tenant-phase16-security",
                prepared_action_hash=prepared_hash,
            )

def test_phase16_gateway_records_known_effect_receipt_after_approval(engine) -> None:
    tenant_id = "tenant-phase16-execute"
    workspace_id = "workspace-phase16-execute"
    call_id = "call-phase16-execute-mail"
    secret_ref = "security-secret-ref:phase16:mail"
    with SecurityUnitOfWork(engine) as repo:
        repo.record_secret_ref(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            credential_version_ref="credential-version:phase16:mail:1",
            audience="tool:mail.send",
            owner_principal_id=f"workspace-user:{workspace_id}",
            scope={"tool": "mail.send", "tenant_id": tenant_id},
        )

    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
    )
    dispatched = False

    async def executor() -> dict[str, str]:
        nonlocal dispatched
        dispatched = True
        return {"provider_effect_id": "mail-provider-effect:phase16:1", "message_id": "message-1"}

    result, receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-execute",
        call_id=call_id,
        adapter_kind="API",
        executor=executor,
        readonly=False,
        approved=True,
    ))

    assert result == {"provider_effect_id": "mail-provider-effect:phase16:1", "message_id": "message-1"}
    assert dispatched is True
    assert receipt.status == "completed"

    effect_policy = classify_tool_effect(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello", "secret_ref": secret_ref},
        readonly=False,
        adapter_kind="API",
    )
    effect_payload = {
        "provider_effect_id": "mail-provider-effect:phase16:1",
        "effect_status": "CONFIRMED",
        "effect_certainty": "CONFIRMED_EFFECT",
        "native_result": {"provider_effect_id": "mail-provider-effect:phase16:1", "message_id": "message-1"},
    }
    with engine.connect() as conn:
        assert conn.execute(
            text("SELECT status FROM security_approval_requests WHERE approval_request_id = 'approval-request:call-phase16-execute-mail'")
        ).scalar_one() == "approved"
        assert conn.execute(
            text("SELECT count(*) FROM security_audit_requirements WHERE audit_requirement_id = 'audit-requirement:call-phase16-execute-mail:tool-execute'")
        ).scalar_one() == 1
        assert conn.execute(
            text("SELECT audience FROM security_secret_leases WHERE lease_id = 'security-secret-lease:call-phase16-execute-mail'")
        ).scalar_one() == "tool:mail.send"
        execution = conn.execute(
            text(
                """
                SELECT status, dispatch_certainty, effect_certainty
                FROM tool_execution_receipts
                WHERE receipt_id = 'tool-execution-receipt:call-phase16-execute-mail'
                """
            )
        ).mappings().one()
        effect = conn.execute(
            text(
                """
                SELECT provider_effect_id, effect_status, effect_certainty,
                       idempotency_scope, idempotency_key, idempotency_generation,
                       fencing_resource_id, fencing_epoch, secret_lease_id,
                       native_result_hash, effect_payload_hash
                FROM tool_effect_receipts
                WHERE effect_receipt_id = 'tool-effect-receipt:call-phase16-execute-mail'
                """
            )
        ).mappings().one()
        claim = conn.execute(
            text(
                """
                SELECT owner, status, generation, result_ref
                FROM infra_idempotency_claims
                WHERE tenant_id = :tenant_id
                  AND scope = 'tool-side-effect'
                  AND idempotency_key = :call_id
                """
            ),
            {"tenant_id": tenant_id, "call_id": call_id},
        ).mappings().one()
        lease = conn.execute(
            text(
                """
                SELECT owner_id, epoch
                FROM infra_worker_leases
                WHERE resource_id = :resource_id
                """
            ),
            {"resource_id": effect_policy.target_resource_set.resource_set_ref},
        ).mappings().one()
        observation_hash = conn.execute(
            text(
                """
                SELECT redacted_payload_hash
                FROM tool_observations
                WHERE observation_id = 'tool-observation:tool-attempt:call-phase16-execute-mail'
                """
            )
        ).scalar_one()

    assert execution["status"] == "SUCCEEDED"
    assert execution["dispatch_certainty"] == "DISPATCHED"
    assert execution["effect_certainty"] == "CONFIRMED_EFFECT"
    assert effect["provider_effect_id"] == "mail-provider-effect:phase16:1"
    assert effect["effect_status"] == "CONFIRMED"
    assert effect["effect_certainty"] == "CONFIRMED_EFFECT"
    assert effect["idempotency_scope"] == "tool-side-effect"
    assert effect["idempotency_key"] == call_id
    assert effect["idempotency_generation"] == 1
    assert effect["fencing_resource_id"] == effect_policy.target_resource_set.resource_set_ref
    assert effect["fencing_epoch"] == 1
    assert effect["secret_lease_id"] == "security-secret-lease:call-phase16-execute-mail"
    assert effect["native_result_hash"] == canonical_sha256({"result": effect_payload["native_result"]})
    assert effect["effect_payload_hash"] == canonical_sha256(effect_payload)
    assert claim["owner"] == f"tool-runtime:{call_id}"
    assert claim["status"] == "completed"
    assert claim["generation"] == 1
    assert claim["result_ref"] == "tool-effect-receipt:call-phase16-execute-mail"
    assert lease["owner_id"] == f"tool-runtime:{call_id}"
    assert lease["epoch"] == 1
    assert observation_hash == canonical_sha256(effect_payload)

def test_phase16_gateway_replays_completed_side_effect_idempotency_without_dispatch(engine) -> None:
    tenant_id = "tenant-phase16-idempotency"
    workspace_id = "workspace-phase16-idempotency"
    call_id = "call-phase16-idempotent-mail"
    secret_ref = "security-secret-ref:phase16:idempotent-mail"
    with SecurityUnitOfWork(engine) as repo:
        repo.record_secret_ref(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            credential_version_ref="credential-version:phase16:idempotent-mail:1",
            audience="tool:mail.send",
            owner_principal_id=f"workspace-user:{workspace_id}",
            scope={"tool": "mail.send", "tenant_id": tenant_id},
        )

    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
    )
    calls = 0

    async def executor() -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"provider_effect_id": "mail-provider-effect:phase16:idempotent:1", "message_id": "message-idem-1"}

    first_result, first_receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-idempotency",
        call_id=call_id,
        adapter_kind="API",
        executor=executor,
        readonly=False,
        approved=True,
    ))

    async def replay_executor() -> dict[str, str]:
        raise AssertionError("completed side-effect idempotency replay must not redispatch provider")

    replay_result, replay_receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-idempotency",
        call_id=call_id,
        adapter_kind="API",
        executor=replay_executor,
        readonly=False,
        approved=True,
    ))

    assert first_result == {"provider_effect_id": "mail-provider-effect:phase16:idempotent:1", "message_id": "message-idem-1"}
    assert first_receipt.status == "completed"
    assert replay_result == {
        "idempotency_replay": True,
        "result_ref": "tool-effect-receipt:call-phase16-idempotent-mail",
        "idempotency_scope": "tool-side-effect",
        "idempotency_key": call_id,
    }
    assert replay_receipt.status == "replayed"
    assert replay_receipt.blocked_reason == "IDEMPOTENT_SIDE_EFFECT_REPLAY"
    assert replay_receipt.result_ref == "tool-effect-receipt:call-phase16-idempotent-mail"
    assert calls == 1

    with engine.connect() as conn:
        assert conn.execute(
            text("SELECT count(*) FROM tool_effect_receipts WHERE effect_receipt_id = 'tool-effect-receipt:call-phase16-idempotent-mail'")
        ).scalar_one() == 1
        assert conn.execute(
            text("SELECT count(*) FROM security_secret_leases WHERE lease_id = 'security-secret-lease:call-phase16-idempotent-mail'")
        ).scalar_one() == 1
        claim = conn.execute(
            text(
                """
                SELECT status, generation, result_ref
                FROM infra_idempotency_claims
                WHERE tenant_id = :tenant_id
                  AND scope = 'tool-side-effect'
                  AND idempotency_key = :call_id
                """
            ),
            {"tenant_id": tenant_id, "call_id": call_id},
        ).mappings().one()

    assert claim["status"] == "completed"
    assert claim["generation"] == 1
    assert claim["result_ref"] == "tool-effect-receipt:call-phase16-idempotent-mail"

def test_phase16_gateway_records_unknown_effect_reconciliation_without_retry(engine) -> None:
    tenant_id = "tenant-phase16-unknown"
    workspace_id = "workspace-phase16-unknown"
    call_id = "call-phase16-unknown-mail"
    secret_ref = "security-secret-ref:phase16:unknown-mail"
    with SecurityUnitOfWork(engine) as repo:
        repo.record_secret_ref(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            credential_version_ref="credential-version:phase16:unknown-mail:1",
            audience="tool:mail.send",
            owner_principal_id=f"workspace-user:{workspace_id}",
            scope={"tool": "mail.send", "tenant_id": tenant_id},
        )

    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
    )
    calls = 0

    async def executor() -> dict[str, str]:
        nonlocal calls
        calls += 1
        raise ToolEffectUnknownError(
            provider_effect_id="mail-provider-effect:phase16:unknown:1",
            reconciliation_query={"provider": "mail", "message_id": "message-unknown-1"},
        )

    result, receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-unknown",
        call_id=call_id,
        adapter_kind="API",
        executor=executor,
        readonly=False,
        approved=True,
    ))

    assert result is None
    assert calls == 1
    assert receipt.status == "reconcile_required"
    assert receipt.blocked_reason == "UNKNOWN_EFFECT_RECONCILIATION_REQUIRED"

    unknown_payload = {
        "provider_effect_id": "mail-provider-effect:phase16:unknown:1",
        "effect_status": "UNKNOWN",
        "effect_certainty": "UNKNOWN_EFFECT",
        "reconciliation_id": "tool-effect-reconciliation:call-phase16-unknown-mail",
        "next_action": "RECONCILE",
        "reconciliation_query": {"provider": "mail", "message_id": "message-unknown-1"},
    }
    with engine.connect() as conn:
        execution = conn.execute(
            text(
                """
                SELECT status, dispatch_certainty, effect_certainty
                FROM tool_execution_receipts
                WHERE receipt_id = 'tool-execution-receipt:call-phase16-unknown-mail'
                """
            )
        ).mappings().one()
        assert conn.execute(
            text("SELECT count(*) FROM tool_effect_receipts WHERE provider_effect_id = 'mail-provider-effect:phase16:unknown:1'")
        ).scalar_one() == 0
        reconciliation = conn.execute(
            text(
                """
                SELECT status, next_action, provider_effect_id, manual_assessment_required,
                       age_escalation_after_seconds, idempotency_scope, idempotency_key,
                       idempotency_generation, secret_lease_id, reconciliation_query_hash,
                       reconciliation_payload_hash
                FROM tool_effect_reconciliations
                WHERE reconciliation_id = 'tool-effect-reconciliation:call-phase16-unknown-mail'
                """
            )
        ).mappings().one()
        claim = conn.execute(
            text(
                """
                SELECT status, result_ref
                FROM infra_idempotency_claims
                WHERE tenant_id = :tenant_id
                  AND scope = 'tool-side-effect'
                  AND idempotency_key = :call_id
                """
            ),
            {"tenant_id": tenant_id, "call_id": call_id},
        ).mappings().one()
        observation_hash = conn.execute(
            text(
                """
                SELECT redacted_payload_hash
                FROM tool_observations
                WHERE observation_id = 'tool-observation:tool-attempt:call-phase16-unknown-mail'
                """
            )
        ).scalar_one()

    assert execution["status"] == "UNKNOWN"
    assert execution["dispatch_certainty"] == "DISPATCHED"
    assert execution["effect_certainty"] == "UNKNOWN_EFFECT"
    assert reconciliation["status"] == "OPEN"
    assert reconciliation["next_action"] == "RECONCILE"
    assert reconciliation["provider_effect_id"] == "mail-provider-effect:phase16:unknown:1"
    assert reconciliation["manual_assessment_required"] is False
    assert reconciliation["age_escalation_after_seconds"] == 900
    assert reconciliation["idempotency_scope"] == "tool-side-effect"
    assert reconciliation["idempotency_key"] == call_id
    assert reconciliation["idempotency_generation"] == 1
    assert reconciliation["secret_lease_id"] == "security-secret-lease:call-phase16-unknown-mail"
    assert reconciliation["reconciliation_query_hash"] == canonical_sha256(
        {"provider": "mail", "message_id": "message-unknown-1"}
    )
    assert reconciliation["reconciliation_payload_hash"] == canonical_sha256(unknown_payload)
    assert claim["status"] == "completed"
    assert claim["result_ref"] == "tool-effect-reconciliation:call-phase16-unknown-mail"
    assert observation_hash == canonical_sha256(unknown_payload)
    assessment_payload = {
        "provider_console_status": "message id not found after provider outage",
        "operator_note": "manual review could not prove delivery",
    }
    gateway.record_manual_effect_assessment(
        tenant_id=tenant_id,
        manual_assessment_id="tool-manual-assessment:call-phase16-unknown-mail",
        reconciliation_id="tool-effect-reconciliation:call-phase16-unknown-mail",
        provider_effect_id="mail-provider-effect:phase16:unknown:1",
        conclusion="UNRESOLVED",
        confidence=0.55,
        assessor_principal_id="workspace-user:manual-reviewer",
        residual_uncertainty="provider outage left delivery unknown",
        evidence_payload=assessment_payload,
    )
    with engine.connect() as conn:
        assessment = conn.execute(
            text(
                """
                SELECT reconciliation_id, provider_effect_id, conclusion, confidence,
                       assessor_principal_id, residual_uncertainty, evidence_payload_hash
                FROM tool_manual_effect_assessments
                WHERE manual_assessment_id = 'tool-manual-assessment:call-phase16-unknown-mail'
                """
            )
        ).mappings().one()
        assert conn.execute(
            text("SELECT count(*) FROM tool_effect_receipts WHERE provider_effect_id = 'mail-provider-effect:phase16:unknown:1'")
        ).scalar_one() == 0

    assert assessment["reconciliation_id"] == "tool-effect-reconciliation:call-phase16-unknown-mail"
    assert assessment["provider_effect_id"] == "mail-provider-effect:phase16:unknown:1"
    assert assessment["conclusion"] == "UNRESOLVED"
    assert float(assessment["confidence"]) == 0.55
    assert assessment["assessor_principal_id"] == "workspace-user:manual-reviewer"
    assert assessment["residual_uncertainty"] == "provider outage left delivery unknown"
    assert assessment["evidence_payload_hash"] == canonical_sha256(assessment_payload)


def test_phase16_reconciliation_restart_age_escalates_without_retry(engine) -> None:
    tenant_id = "tenant-phase16-restart-reconcile"
    workspace_id = "workspace-phase16-restart-reconcile"
    call_id = "call-phase16-restart-unknown"
    secret_ref = "security-secret-ref:phase16:restart-unknown"
    with SecurityUnitOfWork(engine) as repo:
        repo.record_secret_ref(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            credential_version_ref="credential-version:phase16:restart-unknown:1",
            audience="tool:mail.send",
            owner_principal_id=f"workspace-user:{workspace_id}",
            scope={"tool": "mail.send", "tenant_id": tenant_id},
        )

    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
    )
    calls = 0

    async def executor() -> dict[str, str]:
        nonlocal calls
        calls += 1
        raise ToolEffectUnknownError(
            provider_effect_id="mail-provider-effect:phase16:restart-unknown:1",
            reconciliation_query={"provider": "mail", "message_id": "message-restart-unknown-1"},
        )

    result, receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "hello", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-restart-unknown",
        call_id=call_id,
        adapter_kind="API",
        executor=executor,
        readonly=False,
        approved=True,
    ))

    assert result is None
    assert receipt.status == "reconcile_required"
    assert calls == 1

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE tool_effect_reconciliations
                SET created_at = now() - interval '20 minutes',
                    age_escalation_after_seconds = 60
                WHERE reconciliation_id = 'tool-effect-reconciliation:call-phase16-restart-unknown'
                """
            )
        )

    restarted_gateway = ToolInvocationGateway(unit_of_work_factory=lambda: ToolUnitOfWork(engine))
    escalated = restarted_gateway.escalate_due_reconciliations(tenant_id=tenant_id)

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT status, next_action, manual_assessment_required
                FROM tool_effect_reconciliations
                WHERE reconciliation_id = 'tool-effect-reconciliation:call-phase16-restart-unknown'
                """
            )
        ).mappings().one()
        claim = conn.execute(
            text(
                """
                SELECT status, result_ref
                FROM infra_idempotency_claims
                WHERE tenant_id = :tenant_id
                  AND scope = 'tool-side-effect'
                  AND idempotency_key = :call_id
                """
            ),
            {"tenant_id": tenant_id, "call_id": call_id},
        ).mappings().one()

    assert escalated == 1
    assert calls == 1
    assert row["status"] == "ESCALATED"
    assert row["next_action"] == "MANUAL_ASSESSMENT"
    assert row["manual_assessment_required"] is True
    assert claim["status"] == "completed"
    assert claim["result_ref"] == "tool-effect-reconciliation:call-phase16-restart-unknown"


def test_phase16_gateway_records_async_job_callback_and_cancellation(engine) -> None:
    tenant_id = "tenant-phase16-async"
    workspace_id = "workspace-phase16-async"
    call_id = "call-phase16-async-export"
    secret_ref = "security-secret-ref:phase16:async-export"
    with SecurityUnitOfWork(engine) as repo:
        repo.record_secret_ref(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            credential_version_ref="credential-version:phase16:async-export:1",
            audience="tool:export.start",
            owner_principal_id=f"workspace-user:{workspace_id}",
            scope={"tool": "export.start", "tenant_id": tenant_id},
        )

    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
    )
    calls = 0

    async def executor() -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"provider_job_id": "provider-job:phase16:async:1", "status_url": "https://provider/jobs/1"}

    result, receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="export.start",
        args={"resource": "s3://bucket/export", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-async",
        call_id=call_id,
        adapter_kind="ASYNC_JOB",
        executor=executor,
        readonly=False,
        approved=True,
    ))

    assert result == {"provider_job_id": "provider-job:phase16:async:1", "status_url": "https://provider/jobs/1"}
    assert receipt.status == "async_waiting"
    assert calls == 1

    gateway.record_async_callback(
        tenant_id=tenant_id,
        async_job_id="tool-async-job:call-phase16-async-export",
        provider_job_id="provider-job:phase16:async:1",
        callback_order=2,
        callback_payload={"state": "done", "order": 2},
        expected_binding_ref="callback-binding:call-phase16-async-export",
        provided_binding_ref="callback-binding:call-phase16-async-export",
    )
    gateway.record_async_callback(
        tenant_id=tenant_id,
        async_job_id="tool-async-job:call-phase16-async-export",
        provider_job_id="provider-job:phase16:async:1",
        callback_order=1,
        callback_payload={"state": "running", "order": 1},
        expected_binding_ref="callback-binding:call-phase16-async-export",
        provided_binding_ref="callback-binding:call-phase16-async-export",
    )
    gateway.record_async_callback(
        tenant_id=tenant_id,
        async_job_id="tool-async-job:call-phase16-async-export",
        provider_job_id="provider-job:phase16:async:1",
        callback_order=2,
        callback_payload={"state": "done", "order": 2},
        expected_binding_ref="callback-binding:call-phase16-async-export",
        provided_binding_ref="callback-binding:call-phase16-async-export",
    )
    gateway.record_async_callback(
        tenant_id=tenant_id,
        async_job_id="tool-async-job:call-phase16-async-export",
        provider_job_id="provider-job:phase16:async:1",
        callback_order=3,
        callback_payload={"state": "done", "order": 3},
        expected_binding_ref="callback-binding:call-phase16-async-export",
        provided_binding_ref="callback-binding:forged",
    )
    gateway.record_cancellation_request(
        tenant_id=tenant_id,
        prepared_id="prepared-tool-action:call-phase16-async-export",
        attempt_id="tool-attempt:call-phase16-async-export",
        async_job_id="tool-async-job:call-phase16-async-export",
        provider_job_id="provider-job:phase16:async:1",
        requested_by_principal_id="workspace-user:cancel",
        audit_requirement_id="audit-requirement:call-phase16-async-export:cancel",
    )

    async_payload = {
        "provider_job_id": "provider-job:phase16:async:1",
        "async_status": "WAITING_CALLBACK",
        "effect_certainty": "UNKNOWN_EFFECT",
        "native_result": {"provider_job_id": "provider-job:phase16:async:1", "status_url": "https://provider/jobs/1"},
    }
    with engine.connect() as conn:
        execution = conn.execute(
            text(
                """
                SELECT status, dispatch_certainty, effect_certainty
                FROM tool_execution_receipts
                WHERE receipt_id = 'tool-execution-receipt:call-phase16-async-export'
                """
            )
        ).mappings().one()
        job = conn.execute(
            text(
                """
                SELECT provider_job_id, status, callback_binding_ref, callback_order,
                       idempotency_scope, idempotency_key, idempotency_generation,
                       secret_lease_id, job_payload_hash
                FROM tool_async_jobs
                WHERE async_job_id = 'tool-async-job:call-phase16-async-export'
                """
            )
        ).mappings().one()
        callbacks = conn.execute(
            text(
                """
                SELECT callback_order, authenticity_status, accepted
                FROM tool_async_callbacks
                WHERE provider_job_id = 'provider-job:phase16:async:1'
                ORDER BY callback_order
                """
            )
        ).mappings().all()
        cancellation = conn.execute(
            text(
                """
                SELECT status, external_effect_revoked, requested_by_principal_id,
                       audit_requirement_id, cancellation_payload_hash
                FROM tool_cancellation_receipts
                WHERE cancellation_receipt_id = 'tool-cancellation-receipt:provider-job:phase16:async:1'
                """
            )
        ).mappings().one()
        claim = conn.execute(
            text(
                """
                SELECT status, result_ref
                FROM infra_idempotency_claims
                WHERE tenant_id = :tenant_id
                  AND scope = 'tool-side-effect'
                  AND idempotency_key = :call_id
                """
            ),
            {"tenant_id": tenant_id, "call_id": call_id},
        ).mappings().one()

    assert execution["status"] == "DISPATCHED"
    assert execution["dispatch_certainty"] == "DISPATCHED"
    assert execution["effect_certainty"] == "UNKNOWN_EFFECT"
    assert job["provider_job_id"] == "provider-job:phase16:async:1"
    assert job["status"] == "COMPLETED"
    assert job["callback_binding_ref"] == "callback-binding:call-phase16-async-export"
    assert job["callback_order"] == 2
    assert job["idempotency_scope"] == "tool-side-effect"
    assert job["idempotency_key"] == call_id
    assert job["idempotency_generation"] == 1
    assert job["secret_lease_id"] == "security-secret-lease:call-phase16-async-export"
    assert job["job_payload_hash"] == canonical_sha256(async_payload)
    assert [dict(row) for row in callbacks] == [
        {"callback_order": 1, "authenticity_status": "VERIFIED", "accepted": True},
        {"callback_order": 2, "authenticity_status": "VERIFIED", "accepted": True},
        {"callback_order": 3, "authenticity_status": "FORGED", "accepted": False},
    ]
    assert cancellation["status"] == "NOT_GUARANTEED"
    assert cancellation["external_effect_revoked"] is False
    assert cancellation["requested_by_principal_id"] == "workspace-user:cancel"
    assert cancellation["audit_requirement_id"] == "audit-requirement:call-phase16-async-export:cancel"
    assert cancellation["cancellation_payload_hash"] == canonical_sha256(
        {
            "provider_job_id": "provider-job:phase16:async:1",
            "status": "NOT_GUARANTEED",
            "external_effect_revoked": False,
            "requested_by_principal_id": "workspace-user:cancel",
            "audit_requirement_id": "audit-requirement:call-phase16-async-export:cancel",
        }
    )
    assert claim["status"] == "completed"
    assert claim["result_ref"] == "tool-async-job:call-phase16-async-export"


def test_phase16_async_restart_times_out_due_job_without_callback_replay(engine) -> None:
    tenant_id = "tenant-phase16-async-timeout"
    workspace_id = "workspace-phase16-async-timeout"
    call_id = "call-phase16-async-timeout-export"
    secret_ref = "security-secret-ref:phase16:async-timeout"
    with SecurityUnitOfWork(engine) as repo:
        repo.record_secret_ref(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            credential_version_ref="credential-version:phase16:async-timeout:1",
            audience="tool:export.start",
            owner_principal_id=f"workspace-user:{workspace_id}",
            scope={"tool": "export.start", "tenant_id": tenant_id},
        )

    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
    )
    calls = 0

    async def executor() -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"provider_job_id": "provider-job:phase16:async-timeout:1"}

    result, receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="export.start",
        args={"resource": "s3://bucket/timeout-export", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-async-timeout",
        call_id=call_id,
        adapter_kind="ASYNC_JOB",
        executor=executor,
        readonly=False,
        approved=True,
    ))

    assert result == {"provider_job_id": "provider-job:phase16:async-timeout:1"}
    assert receipt.status == "async_waiting"
    assert calls == 1

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE tool_async_jobs
                SET deadline_at = now() - interval '1 second'
                WHERE async_job_id = 'tool-async-job:call-phase16-async-timeout-export'
                """
            )
        )

    restarted_gateway = ToolInvocationGateway(unit_of_work_factory=lambda: ToolUnitOfWork(engine))
    timed_out = restarted_gateway.timeout_due_async_jobs(tenant_id=tenant_id)

    with engine.connect() as conn:
        job = conn.execute(
            text(
                """
                SELECT status, provider_job_id
                FROM tool_async_jobs
                WHERE async_job_id = 'tool-async-job:call-phase16-async-timeout-export'
                """
            )
        ).mappings().one()
        claim = conn.execute(
            text(
                """
                SELECT status, result_ref
                FROM infra_idempotency_claims
                WHERE tenant_id = :tenant_id
                  AND scope = 'tool-side-effect'
                  AND idempotency_key = :call_id
                """
            ),
            {"tenant_id": tenant_id, "call_id": call_id},
        ).mappings().one()

    assert timed_out == 1
    assert calls == 1
    assert job["provider_job_id"] == "provider-job:phase16:async-timeout:1"
    assert job["status"] == "TIMEOUT"
    assert claim["status"] == "completed"
    assert claim["result_ref"] == "tool-async-job:call-phase16-async-timeout-export"


def test_phase16_async_cancellation_moves_waiting_job_without_timeout_overwrite(engine) -> None:
    tenant_id = "tenant-phase16-async-cancel"
    workspace_id = "workspace-phase16-async-cancel"
    call_id = "call-phase16-async-cancel-export"
    secret_ref = "security-secret-ref:phase16:async-cancel"
    async_job_id = "tool-async-job:call-phase16-async-cancel-export"
    provider_job_id = "provider-job:phase16:async-cancel:1"
    with SecurityUnitOfWork(engine) as repo:
        repo.record_secret_ref(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            credential_version_ref="credential-version:phase16:async-cancel:1",
            audience="tool:export.start",
            owner_principal_id=f"workspace-user:{workspace_id}",
            scope={"tool": "export.start", "tenant_id": tenant_id},
        )

    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
    )
    calls = 0

    async def executor() -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"provider_job_id": provider_job_id}

    result, receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="export.start",
        args={"resource": "s3://bucket/cancel-export", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-async-cancel",
        call_id=call_id,
        adapter_kind="ASYNC_JOB",
        executor=executor,
        readonly=False,
        approved=True,
    ))

    assert result == {"provider_job_id": provider_job_id}
    assert receipt.status == "async_waiting"
    assert calls == 1

    gateway.record_cancellation_request(
        tenant_id=tenant_id,
        prepared_id=f"prepared-tool-action:{call_id}",
        attempt_id=f"tool-attempt:{call_id}",
        async_job_id=async_job_id,
        provider_job_id=provider_job_id,
        requested_by_principal_id="workspace-user:cancel",
        audit_requirement_id=f"audit-requirement:{call_id}:cancel",
    )

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE tool_async_jobs
                SET deadline_at = now() - interval '1 second'
                WHERE async_job_id = :async_job_id
                """
            ),
            {"async_job_id": async_job_id},
        )

    timed_out = gateway.timeout_due_async_jobs(tenant_id=tenant_id)

    with engine.connect() as conn:
        job = conn.execute(
            text(
                """
                SELECT status, provider_job_id, callback_order
                FROM tool_async_jobs
                WHERE async_job_id = :async_job_id
                """
            ),
            {"async_job_id": async_job_id},
        ).mappings().one()
        cancellation = conn.execute(
            text(
                """
                SELECT status, external_effect_revoked, requested_by_principal_id,
                       audit_requirement_id
                FROM tool_cancellation_receipts
                WHERE cancellation_receipt_id = :receipt_id
                """
            ),
            {"receipt_id": f"tool-cancellation-receipt:{provider_job_id}"},
        ).mappings().one()

    assert timed_out == 0
    assert calls == 1
    assert job["provider_job_id"] == provider_job_id
    assert job["status"] == "CANCEL_REQUESTED"
    assert job["callback_order"] == 0
    assert cancellation["status"] == "NOT_GUARANTEED"
    assert cancellation["external_effect_revoked"] is False
    assert cancellation["requested_by_principal_id"] == "workspace-user:cancel"
    assert cancellation["audit_requirement_id"] == f"audit-requirement:{call_id}:cancel"


def test_phase16_gateway_records_compensation_as_new_governed_action(engine) -> None:
    tenant_id = "tenant-phase16-compensation"
    workspace_id = "workspace-phase16-compensation"
    source_call_id = "call-phase16-source-mail"
    compensation_call_id = "call-phase16-compensation-mail"
    secret_ref = "security-secret-ref:phase16:compensation-mail"
    with SecurityUnitOfWork(engine) as repo:
        repo.record_secret_ref(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            credential_version_ref="credential-version:phase16:compensation-mail:1",
            audience="tool:mail.send",
            owner_principal_id=f"workspace-user:{workspace_id}",
            scope={"tool": "mail.send", "tenant_id": tenant_id},
        )

    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
    )

    async def source_executor() -> dict[str, str]:
        return {"provider_effect_id": "mail-provider-effect:phase16:source:1", "message_id": "message-source-1"}

    async def compensation_executor() -> dict[str, str]:
        return {"provider_effect_id": "mail-provider-effect:phase16:compensation:1", "message_id": "message-compensation-1"}

    source_result, source_receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "review@example.com", "body": "incorrect body", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-compensation-source",
        call_id=source_call_id,
        adapter_kind="API",
        executor=source_executor,
        readonly=False,
        approved=True,
    ))
    compensation_result, compensation_receipt = asyncio.run(gateway.invoke_readonly(
        tool_name="mail.send",
        args={"to": "correction@example.com", "body": "correction body", "secret_ref": secret_ref},
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        trace_id="trace-phase16-compensation-action",
        call_id=compensation_call_id,
        adapter_kind="API",
        executor=compensation_executor,
        readonly=False,
        approved=True,
    ))

    assert source_result["provider_effect_id"] == "mail-provider-effect:phase16:source:1"
    assert compensation_result["provider_effect_id"] == "mail-provider-effect:phase16:compensation:1"
    assert source_receipt.status == "completed"
    assert compensation_receipt.status == "completed"

    gateway.record_compensation_attempt(
        tenant_id=tenant_id,
        compensation_definition_id="tool-compensation-definition:phase16:source-mail",
        compensation_attempt_id="tool-compensation-attempt:phase16:source-mail:1",
        source_effect_receipt_id=f"tool-effect-receipt:{source_call_id}",
        source_reconciliation_id=None,
        compensation_call_id=compensation_call_id,
        new_action_proposal_ref="action-proposal:phase16:compensate-source-mail",
        operation_ref="tool-version:mail.send:v1:operation:default",
        compensation_capability="BEST_EFFORT_COMPENSATION",
        residual_impact="PARTIAL",
        audit_requirement_id=f"audit-requirement:{compensation_call_id}:tool-execute",
        idempotency_generation=1,
    )

    definition_payload = {
        "source_effect_receipt_id": f"tool-effect-receipt:{source_call_id}",
        "source_reconciliation_id": None,
        "compensation_capability": "BEST_EFFORT_COMPENSATION",
        "operation_ref": "tool-version:mail.send:v1:operation:default",
        "new_action_proposal_ref": "action-proposal:phase16:compensate-source-mail",
        "requires_approval": True,
        "residual_impact": "PARTIAL",
        "hidden_rollback": False,
    }
    attempt_payload = {
        "compensation_definition_id": "tool-compensation-definition:phase16:source-mail",
        "prepared_tool_action_id": f"prepared-tool-action:{compensation_call_id}",
        "attempt_id": f"tool-attempt:{compensation_call_id}",
        "execution_receipt_id": f"tool-execution-receipt:{compensation_call_id}",
        "status": "CONFIRMED",
        "hidden_rollback": False,
        "idempotency_scope": "tool-side-effect",
        "idempotency_key": compensation_call_id,
        "idempotency_generation": 1,
        "audit_requirement_id": f"audit-requirement:{compensation_call_id}:tool-execute",
    }
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM tool_effect_receipts")).scalar_one() == 2
        definition = conn.execute(
            text(
                """
                SELECT source_effect_receipt_id, source_reconciliation_id, compensation_capability,
                       operation_ref, new_action_proposal_ref, requires_approval,
                       residual_impact, definition_payload_hash
                FROM tool_compensation_definitions
                WHERE compensation_definition_id = 'tool-compensation-definition:phase16:source-mail'
                """
            )
        ).mappings().one()
        attempt = conn.execute(
            text(
                """
                SELECT compensation_definition_id, prepared_tool_action_id, attempt_id,
                       execution_receipt_id, status, hidden_rollback, idempotency_scope,
                       idempotency_key, idempotency_generation, audit_requirement_id,
                       attempt_payload_hash
                FROM tool_compensation_attempts
                WHERE compensation_attempt_id = 'tool-compensation-attempt:phase16:source-mail:1'
                """
            )
        ).mappings().one()
        claim = conn.execute(
            text(
                """
                SELECT status, result_ref
                FROM infra_idempotency_claims
                WHERE tenant_id = :tenant_id
                  AND scope = 'tool-side-effect'
                  AND idempotency_key = :compensation_call_id
                """
            ),
            {"tenant_id": tenant_id, "compensation_call_id": compensation_call_id},
        ).mappings().one()

    assert definition["source_effect_receipt_id"] == f"tool-effect-receipt:{source_call_id}"
    assert definition["source_reconciliation_id"] is None
    assert definition["compensation_capability"] == "BEST_EFFORT_COMPENSATION"
    assert definition["operation_ref"] == "tool-version:mail.send:v1:operation:default"
    assert definition["new_action_proposal_ref"] == "action-proposal:phase16:compensate-source-mail"
    assert definition["requires_approval"] is True
    assert definition["residual_impact"] == "PARTIAL"
    assert definition["definition_payload_hash"] == canonical_sha256(definition_payload)
    assert attempt["compensation_definition_id"] == "tool-compensation-definition:phase16:source-mail"
    assert attempt["prepared_tool_action_id"] == f"prepared-tool-action:{compensation_call_id}"
    assert attempt["attempt_id"] == f"tool-attempt:{compensation_call_id}"
    assert attempt["execution_receipt_id"] == f"tool-execution-receipt:{compensation_call_id}"
    assert attempt["status"] == "CONFIRMED"
    assert attempt["hidden_rollback"] is False
    assert attempt["idempotency_scope"] == "tool-side-effect"
    assert attempt["idempotency_key"] == compensation_call_id
    assert attempt["idempotency_generation"] == 1
    assert attempt["audit_requirement_id"] == f"audit-requirement:{compensation_call_id}:tool-execute"
    assert attempt["attempt_payload_hash"] == canonical_sha256(attempt_payload)
    assert claim["status"] == "completed"
    assert claim["result_ref"] == f"tool-effect-receipt:{compensation_call_id}"
