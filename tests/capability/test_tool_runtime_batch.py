from __future__ import annotations

from zuno.capability.tool_runtime import (
    AdapterFamily,
    DispatchCertainty,
    EffectLevel,
    PreparedActionStatus,
    ReconciliationConclusion,
    ToolAttemptStatus,
    ToolRuntimeBatch,
)


def test_tool_runtime_batch_definition_prepare_execute_and_effect_receipts() -> None:
    runtime = ToolRuntimeBatch()

    definition = runtime.tool_definition(
        tool_id="mail.send",
        schema={"type": "object", "properties": {"to": {"type": "string"}}},
        definition_event_ref="event:tool-definition:mail:1",
    )
    projection = runtime.planner_projection(
        projection_ref="projection:capability:mail.send",
        source_definition_ref=definition.definition_event_ref,
    )
    version = runtime.tool_version(
        tool_id=definition.tool_id,
        version="1.0.0",
        schema={"input": "mail-send-v1"},
    )
    installation = runtime.installation(
        installation_ref="install:mail:workspace-a",
        tool_definition_ref=definition.definition_event_ref,
        workspace_id="workspace-a",
        credential_scope_ref="credential-scope:mail:workspace-a",
    )
    activation = runtime.activation(
        activation_ref="activation:mail:workspace-a",
        installation_ref=installation.installation_ref,
        version_ref="tool-version:mail.send:1.0.0",
        expected_generation=41,
        committed_generation=42,
    )
    exposure = runtime.exposure_decision(
        exposure_ref="exposure:mail",
        can_show_to_model=True,
        can_prepare=True,
        security_decision_ref="security-decision:expose:mail",
    )
    proposal = runtime.action_proposal(
        proposal_ref="proposal:agent:mail:1",
        producer_module="06 Agent Core / Planning & Control",
        tool_ref=definition.tool_id,
        input_payload={"to": "reviewer@example.com", "body": "hello"},
    )
    canonical = runtime.canonicalization(
        profile_ref="canonical:tool-input:v1",
        version="v1",
        payload={"body": "hello", "to": "reviewer@example.com"},
    )
    resources = runtime.target_resources(
        resource_set_ref="resources:mail:reviewer",
        resource_refs=("mailbox:reviewer",),
        conflict_keys=("mailbox:reviewer",),
    )
    effect_profile = runtime.effect_profile(
        profile_ref="effect:external-mail",
        level=EffectLevel.WRITE_EXTERNAL,
    )
    prepared = runtime.prepare_action(
        prepared_ref="prepared:mail:1",
        proposal=proposal,
        canonical=canonical,
        resource_set=resources,
        effect_profile=effect_profile,
        security_epoch_ref="security-epoch:7",
        audit_requirement_ref="audit:tool:mail:required",
        idempotency_key="idem:mail:workspace-a:1",
        deadline_ref="deadline:mail:1",
        input_payload={"to": "reviewer@example.com", "api_key": "secret-token"},
    )
    blocked_gate = runtime.execution_gate(
        gate_ref="gate:blocked",
        security_epoch_ref="security-epoch:7",
        audit_receipt_ref=None,
        claim_ref="claim:mail:1",
    )
    gate = runtime.execution_gate(
        gate_ref="gate:mail:1",
        security_epoch_ref="security-epoch:7",
        audit_receipt_ref="audit-receipt:tool:mail:1",
        claim_ref="claim:mail:1",
    )
    attempt = runtime.attempt(
        attempt_ref="attempt:mail:1",
        prepared_ref=prepared.prepared_ref,
        status=ToolAttemptStatus.SUCCEEDED,
        dispatch_certainty=DispatchCertainty.DISPATCHED,
        adapter_family=AdapterFamily.CLI,
    )
    receipt = runtime.execution_receipt(
        receipt_ref="execution-receipt:mail:1",
        attempt=attempt,
        generation=1,
    )
    effect = runtime.effect_receipt(
        effect_ref="effect:mail:1",
        attempt_ref=attempt.attempt_ref,
        provider_receipt_ref="smtp:message:1",
        effects=(("mailbox:reviewer", {"message_id": "msg-1"}),),
    )

    assert definition.canonical_owner == "08 Tool Runtime"
    assert projection.owner_module == "07 Capability / Skill" and projection.executable is False
    assert version.immutable_hash and version.mutation_allowed is False
    assert activation.cas_passed and activation.active
    assert exposure.can_show_to_model and exposure.can_prepare and exposure.can_execute is False
    assert proposal.accepted_by_tool_runtime is True
    assert prepared.owner_module == "08 Tool Runtime"
    assert prepared.status == PreparedActionStatus.APPROVAL_WAITING
    assert prepared.approval_binding_hash
    assert prepared.contains_secret_material is False
    assert blocked_gate.dispatch_allowed is False and blocked_gate.reason == "audit_required_before_effect"
    assert gate.dispatch_allowed is True
    assert attempt.state_history == ("STARTED", "SUCCEEDED")
    assert receipt.receipt_ref != gate.claim_ref
    assert receipt.effect_certainty.value == "CONFIRMED_EFFECT"
    assert effect.confirmed is True
    assert len(effect.items) == 1 and effect.items[0].effect_hash


def test_tool_runtime_batch_unknown_reconciliation_compensation_and_observation() -> None:
    runtime = ToolRuntimeBatch()

    unknown_attempt = runtime.attempt(
        attempt_ref="attempt:unknown:1",
        prepared_ref="prepared:effectful:1",
        status=ToolAttemptStatus.UNKNOWN,
        dispatch_certainty=DispatchCertainty.MAYBE_DISPATCHED,
        adapter_family=AdapterFamily.SDK,
        hidden_retry_count=1,
    )
    receipt = runtime.execution_receipt(
        receipt_ref="execution-receipt:unknown:1",
        attempt=unknown_attempt,
        generation=3,
    )
    pending = runtime.reconciliation(
        reconciliation_ref="reconcile:pending:1",
        attempt_ref=unknown_attempt.attempt_ref,
        conclusion=ReconciliationConclusion.PENDING,
    )
    confirmed_not_executed = runtime.reconciliation(
        reconciliation_ref="reconcile:not-executed:1",
        attempt_ref=unknown_attempt.attempt_ref,
        conclusion=ReconciliationConclusion.CONFIRMED_NOT_EXECUTED,
    )
    compensation = runtime.compensation(
        compensation_ref="compensate:mail:1",
        source_effect_ref="effect:mail:1",
        new_action_proposal_ref="proposal:agent:compensate-mail:1",
    )
    cancellation = runtime.cancellation(
        cancellation_ref="cancel:mail:1",
        prepared_ref="prepared:mail:1",
        provider_stop_confirmed=False,
    )
    observation = runtime.observation(
        observation_ref="observation:tool:1",
        output_payload={"api_key": "secret-token", "result": "ok"},
        schema_valid=True,
    )

    assert runtime.transition_allowed(current=ToolAttemptStatus.UNKNOWN, next_status=ToolAttemptStatus.RECONCILING)
    assert runtime.transition_allowed(current=ToolAttemptStatus.UNKNOWN, next_status=ToolAttemptStatus.SUCCEEDED) is False
    assert receipt.effect_certainty.value == "UNKNOWN_EFFECT"
    assert pending.durable_after_run is True and pending.retry_same_effect_allowed is False
    assert confirmed_not_executed.retry_same_effect_allowed is True
    assert compensation.hidden_rollback is False
    assert compensation.new_action_proposal_ref.startswith("proposal:")
    assert cancellation.final_certainty == DispatchCertainty.MAYBE_DISPATCHED
    assert observation.owner_module == "08 Tool Runtime"
    assert observation.normalized_projection_owner == "06 Agent Core / Planning & Control"
    assert observation.output_trusted is False
    assert observation.schema_valid is True
    assert observation.memory_write_allowed is False
    assert observation.evidence_write_allowed is False


def test_tool_runtime_batch_adapter_mcp_security_lifecycle_and_readiness() -> None:
    runtime = ToolRuntimeBatch()

    cli = runtime.cli_policy(
        allowed_env_keys=("PATH", "ZUNO_WORKSPACE"),
        cpu_seconds=10,
        memory_mb=128,
    )
    openapi = runtime.openapi_policy(endpoint_allowed=True, redirects_rechecked=True)
    sdk = runtime.adapter_conformance(
        adapter_ref="adapter:sdk:mail",
        family=AdapterFamily.SDK,
        version="sdk-mail:2.3.4",
        hidden_retry_controlled=True,
    )
    invalidated = runtime.adapter_conformance(
        adapter_ref="adapter:openapi:old",
        family=AdapterFamily.OPENAPI,
        version="openapi:1.0.0",
        hidden_retry_controlled=True,
        invalidated=True,
    )
    mcp = runtime.mcp_session(
        session_ref="mcp:lark:session:1",
        negotiated_capability_refs=("tool:message.send", "tool:folder.list"),
        schema_snapshot={"message.send": {"input": "v1"}},
        multimodal_content_refs=("content:text:1", "content:image:1"),
        task_binding_ref="mcp-task:1",
        redelivery_receipt_ref="inbox:mcp:redelivery:1",
        idempotency_claim_ref="claim:mcp:effect:1",
    )
    async_callback = runtime.async_callback(
        job_ref="job:export:1",
        callback_signature_verified=True,
        callback_nonce_ref="nonce:callback:1",
    )
    concurrency = runtime.concurrency(
        resource_conflict_keys=("document:1",),
        replan_epoch_ref="replan-epoch:2",
        timeout_stages=("prepare", "dispatch", "reconcile"),
        deadline_ref="deadline:tool:1",
        stale_epoch=True,
    )
    failure = runtime.failure_code(code="TOOL_EFFECT_UNKNOWN")
    infrastructure = runtime.infrastructure_boundary(
        outbox_event_ref="outbox:tool:1",
        domain_fact_ref="tool-fact:attempt:1",
        secret_lease_ref="secret-lease:mail:1",
        sandbox_isolation_sufficient=False,
    )
    lifecycle = runtime.lifecycle(
        drain_watermark_ref="drain:tool:1",
        large_payload_object_ref="object:tool-payload:1",
        legal_hold=True,
    )
    allowlist = runtime.allowlist(
        current_allowlist_refs=("legacy:general-agent-langchain-tool",),
        zero_gate_ref="gate:tool-allowlist-zero",
        previous_count=2,
    )
    readiness = runtime.readiness_evidence(
        code_refs=("src/backend/zuno/capability/tool_runtime/runtime_batch.py",),
        test_refs=("tests/capability/test_tool_runtime_batch.py",),
        verifier_ref="tools/scripts/verify_tool_runtime_batch.py",
        evidence_ref="docs/evidence/tool-runtime-batch.md",
    )

    assert cli.allowed_env_keys == ("PATH", "ZUNO_WORKSPACE")
    assert cli.process_tree_kill is True and cli.cpu_seconds == 10 and cli.memory_mb == 128
    assert openapi.endpoint_allowed and openapi.redirects_rechecked and openapi.probe_has_effect is False
    assert sdk.pinned and sdk.hidden_retry_controlled
    assert invalidated.invalidated is True
    assert mcp.negotiated_capability_refs
    assert mcp.old_actions_obsolete_on_list_changed is True
    assert mcp.annotations_trusted is False
    assert mcp.multimodal_content_refs
    assert mcp.redelivery_receipt_ref != mcp.idempotency_claim_ref
    assert mcp.sampling_route_owner == "04 Model Gateway"
    assert mcp.elicitation_is_security_approval is False
    assert async_callback.accepted_is_completion is False
    assert async_callback.callback_signature_verified is True and async_callback.callback_nonce_ref
    assert concurrency.resource_conflict_keys and concurrency.stale_dispatch_rejected
    assert concurrency.timeout_stages == ("prepare", "dispatch", "reconcile")
    assert failure.namespace == "TOOL"
    assert infrastructure.same_transaction is True
    assert infrastructure.secret_lease_ref.startswith("secret-lease:")
    assert infrastructure.sandbox_isolation_sufficient is False
    assert infrastructure.capacity_gate_order[:4] == ("exposure", "prepare", "security_epoch", "audit")
    assert lifecycle.canary_real_effect_allowed is False
    assert lifecycle.retired_history_readable is True
    assert lifecycle.legal_hold_blocks_delete is True
    assert lifecycle.confirmed_effect_sli_ref == "sli:tool.confirmed_effect"
    assert allowlist.monotonic_decrease is True and allowlist.zero_gate_ref
    assert readiness.implementation_available is True
    assert readiness.requirement_ids == tuple(f"ARCH-TOOL-{index:03d}" for index in range(1, 81))
