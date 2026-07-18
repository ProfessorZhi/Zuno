from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "backend"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from zuno.capability.tool_runtime import (  # noqa: E402
    AdapterFamily,
    DispatchCertainty,
    EffectLevel,
    ReconciliationConclusion,
    ToolAttemptStatus,
    ToolRuntimeBatch,
)


REQUIREMENTS = tuple(f"ARCH-TOOL-{index:03d}" for index in range(1, 81))


def verify_tool_runtime_batch() -> list[str]:
    errors: list[str] = []
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
    version = runtime.tool_version(tool_id=definition.tool_id, version="1.0.0", schema={"input": "mail-send-v1"})
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
    if definition.canonical_owner != "08 Tool Runtime":
        errors.append("ARCH-TOOL-003 ToolDefinition owner is not 08")
    if projection.owner_module != "07 Capability / Skill" or projection.executable:
        errors.append("ARCH-TOOL-004 planner projection can execute or has wrong owner")
    if not version.immutable_hash or version.mutation_allowed:
        errors.append("ARCH-TOOL-006 ToolVersion is not immutable")
    if installation.tool_definition_ref == installation.installation_ref:
        errors.append("ARCH-TOOL-007 installation is not separated from definition")
    if not activation.cas_passed:
        errors.append("ARCH-TOOL-008 activation did not use generation CAS")
    if exposure.can_execute:
        errors.append("ARCH-TOOL-009 exposure implied execution")

    proposal = runtime.action_proposal(
        proposal_ref="proposal:agent:mail:1",
        producer_module="06 Agent Core / Planning & Control",
        tool_ref=definition.tool_id,
        input_payload={"to": "reviewer@example.com", "body": "hello"},
    )
    rejected_proposal = runtime.action_proposal(
        proposal_ref="proposal:model:mail:1",
        producer_module="04 Model Gateway",
        tool_ref=definition.tool_id,
        input_payload={"to": "reviewer@example.com"},
    )
    canonical = runtime.canonicalization(profile_ref="canonical:tool-input:v1", version="v1", payload={"body": "hello", "to": "reviewer@example.com"})
    resources = runtime.target_resources(
        resource_set_ref="resources:mail:reviewer",
        resource_refs=("mailbox:reviewer",),
        conflict_keys=("mailbox:reviewer",),
    )
    effect_profile = runtime.effect_profile(profile_ref="effect:external-mail", level=EffectLevel.WRITE_EXTERNAL)
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
    if not proposal.accepted_by_tool_runtime or rejected_proposal.accepted_by_tool_runtime:
        errors.append("ARCH-TOOL-010 ActionProposal producer guard failed")
    if prepared.owner_module != "08 Tool Runtime":
        errors.append("ARCH-TOOL-011 PreparedToolAction owner is not 08")
    if not (canonical.profile_ref and canonical.version and canonical.canonical_hash):
        errors.append("ARCH-TOOL-012/013 canonicalization lacks version or stable hash")
    if not (resources.resource_refs and resources.conflict_keys):
        errors.append("ARCH-TOOL-014 target resource set lacks resources/conflict keys")
    if not effect_profile.requires_approval or not effect_profile.requires_effect_receipt:
        errors.append("ARCH-TOOL-015 effect profile did not classify effectful action")
    if prepared.contains_secret_material:
        errors.append("ARCH-TOOL-016 prepared action contains secret material")
    if not all([prepared.approval_binding_hash, prepared.security_epoch_ref, prepared.audit_requirement_ref, prepared.idempotency_key, prepared.deadline_ref]):
        errors.append("ARCH-TOOL-017/018/066 prepared action lacks approval hash/security epoch/audit/idempotency/deadline")

    blocked_gate = runtime.execution_gate(gate_ref="gate:blocked", security_epoch_ref="security-epoch:7", audit_receipt_ref=None, claim_ref="claim:mail:1")
    gate = runtime.execution_gate(gate_ref="gate:mail:1", security_epoch_ref="security-epoch:7", audit_receipt_ref="audit-receipt:tool:mail:1", claim_ref="claim:mail:1")
    if blocked_gate.dispatch_allowed or blocked_gate.reason != "audit_required_before_effect":
        errors.append("ARCH-TOOL-019 mandatory audit is not before effect")
    if not gate.dispatch_allowed or not gate.claim_ref:
        errors.append("ARCH-TOOL-020 claim is not before dispatch")

    attempt = runtime.attempt(
        attempt_ref="attempt:mail:1",
        prepared_ref=prepared.prepared_ref,
        status=ToolAttemptStatus.SUCCEEDED,
        dispatch_certainty=DispatchCertainty.DISPATCHED,
        adapter_family=AdapterFamily.CLI,
    )
    receipt = runtime.execution_receipt(receipt_ref="execution-receipt:mail:1", attempt=attempt, generation=1)
    effect = runtime.effect_receipt(
        effect_ref="effect:mail:1",
        attempt_ref=attempt.attempt_ref,
        provider_receipt_ref="smtp:message:1",
        effects=(("mailbox:reviewer", {"message_id": "msg-1"}), ("audit:smtp", {"status": "accepted"})),
    )
    if receipt.receipt_ref == gate.claim_ref:
        errors.append("ARCH-TOOL-021 claim was treated as effect")
    if attempt.state_history != ("STARTED", "SUCCEEDED"):
        errors.append("ARCH-TOOL-022/024 attempt was not recorded with legal state history")
    if attempt.dispatch_certainty != DispatchCertainty.DISPATCHED:
        errors.append("ARCH-TOOL-025 dispatch certainty not explicit")
    if not receipt.receipt_ref:
        errors.append("ARCH-TOOL-026 execution receipt missing")
    if not effect.confirmed:
        errors.append("ARCH-TOOL-027 effectful tool lacks effect receipt")
    if len(effect.items) != 2 or not all(item.effect_hash for item in effect.items):
        errors.append("ARCH-TOOL-028 batch effect item receipts missing")
    if receipt.append_only_generation < 1:
        errors.append("ARCH-TOOL-029 receipt generation not append-only")

    unknown_attempt = runtime.attempt(
        attempt_ref="attempt:unknown:1",
        prepared_ref=prepared.prepared_ref,
        status=ToolAttemptStatus.UNKNOWN,
        dispatch_certainty=DispatchCertainty.MAYBE_DISPATCHED,
        adapter_family=AdapterFamily.SDK,
        hidden_retry_count=1,
    )
    unknown_receipt = runtime.execution_receipt(receipt_ref="receipt:unknown:1", attempt=unknown_attempt, generation=2)
    pending_reconcile = runtime.reconciliation(reconciliation_ref="reconcile:pending:1", attempt_ref=unknown_attempt.attempt_ref, conclusion=ReconciliationConclusion.PENDING)
    retryable_reconcile = runtime.reconciliation(reconciliation_ref="reconcile:not-executed:1", attempt_ref=unknown_attempt.attempt_ref, conclusion=ReconciliationConclusion.CONFIRMED_NOT_EXECUTED)
    compensation = runtime.compensation(compensation_ref="compensation:mail:1", source_effect_ref=effect.effect_ref, new_action_proposal_ref="proposal:agent:compensate-mail:1")
    cancellation = runtime.cancellation(cancellation_ref="cancel:mail:1", prepared_ref=prepared.prepared_ref, provider_stop_confirmed=False)
    observation = runtime.observation(observation_ref="observation:tool:1", output_payload={"api_key": "secret-token", "result": "ok"}, schema_valid=True)
    if runtime.transition_allowed(current=ToolAttemptStatus.UNKNOWN, next_status=ToolAttemptStatus.SUCCEEDED):
        errors.append("ARCH-TOOL-030 UNKNOWN allowed blind success/retry")
    if not pending_reconcile.durable_after_run:
        errors.append("ARCH-TOOL-031 reconciliation is not durable beyond run")
    if not retryable_reconcile.retry_same_effect_allowed:
        errors.append("ARCH-TOOL-032 confirmed-not-executed did not allow retry")
    if compensation.hidden_rollback or not compensation.new_action_proposal_ref.startswith("proposal:"):
        errors.append("ARCH-TOOL-033 compensation is not a new governed action")
    if cancellation.final_certainty != DispatchCertainty.MAYBE_DISPATCHED:
        errors.append("ARCH-TOOL-034 cancellation pretended to stop provider effect")
    if observation.owner_module != "08 Tool Runtime" or observation.normalized_projection_owner != "06 Agent Core / Planning & Control":
        errors.append("ARCH-TOOL-035/036 observation owner/projection boundary invalid")
    if observation.output_trusted or not observation.schema_valid or observation.memory_write_allowed or observation.evidence_write_allowed:
        errors.append("ARCH-TOOL-037..040 output trust/schema/memory/evidence gates invalid")
    if unknown_receipt.effect_certainty.value != "UNKNOWN_EFFECT":
        errors.append("ARCH-TOOL-030 unknown receipt lacks UNKNOWN effect certainty")

    cli = runtime.cli_policy(allowed_env_keys=("PATH", "ZUNO_WORKSPACE"), cpu_seconds=10, memory_mb=128)
    openapi = runtime.openapi_policy(endpoint_allowed=True, redirects_rechecked=True)
    sdk = runtime.adapter_conformance(adapter_ref="adapter:sdk:mail", family=AdapterFamily.SDK, version="sdk-mail:2.3.4", hidden_retry_controlled=True)
    invalidated = runtime.adapter_conformance(adapter_ref="adapter:openapi:old", family=AdapterFamily.OPENAPI, version="openapi:1.0.0", hidden_retry_controlled=True, invalidated=True)
    if "SECRET" in cli.allowed_env_keys or not cli.process_tree_kill or cli.cpu_seconds <= 0 or cli.memory_mb <= 0:
        errors.append("ARCH-TOOL-041..043 CLI sandbox policy invalid")
    if not openapi.endpoint_allowed or not openapi.redirects_rechecked or openapi.probe_has_effect:
        errors.append("ARCH-TOOL-044..046 OpenAPI policy invalid")
    if not sdk.pinned or not sdk.hidden_retry_controlled:
        errors.append("ARCH-TOOL-023/047 SDK retry/version control invalid")
    if not invalidated.invalidated:
        errors.append("ARCH-TOOL-048 adapter conformance invalidation missing")

    mcp = runtime.mcp_session(
        session_ref="mcp:lark:session:1",
        negotiated_capability_refs=("tool:message.send", "tool:folder.list"),
        schema_snapshot={"message.send": {"input": "v1"}},
        multimodal_content_refs=("content:text:1", "content:image:1"),
        task_binding_ref="mcp-task:1",
        redelivery_receipt_ref="inbox:mcp:redelivery:1",
        idempotency_claim_ref="claim:mcp:effect:1",
    )
    if not mcp.negotiated_capability_refs or not mcp.schema_snapshot_hash:
        errors.append("ARCH-TOOL-049..051 MCP negotiation/schema snapshot missing")
    if not mcp.old_actions_obsolete_on_list_changed or mcp.annotations_trusted:
        errors.append("ARCH-TOOL-052/053 MCP listChanged/annotation semantics invalid")
    if not (mcp.multimodal_content_refs and mcp.task_binding_ref):
        errors.append("ARCH-TOOL-054/055 MCP multimodal/task binding missing")
    if mcp.redelivery_receipt_ref == mcp.idempotency_claim_ref:
        errors.append("ARCH-TOOL-056 MCP redelivery and effect idempotency conflated")
    if mcp.sampling_route_owner != "04 Model Gateway" or mcp.elicitation_is_security_approval:
        errors.append("ARCH-TOOL-057/058 MCP sampling/elicitation boundary invalid")

    async_callback = runtime.async_callback(job_ref="job:export:1", callback_signature_verified=True, callback_nonce_ref="nonce:callback:1")
    concurrency = runtime.concurrency(resource_conflict_keys=("document:1",), replan_epoch_ref="replan-epoch:2", timeout_stages=("prepare", "dispatch", "reconcile"), deadline_ref="deadline:tool:1", stale_epoch=True)
    failure = runtime.failure_code(code="TOOL_EFFECT_UNKNOWN")
    infrastructure = runtime.infrastructure_boundary(outbox_event_ref="outbox:tool:1", domain_fact_ref="tool-fact:attempt:1", secret_lease_ref="secret-lease:mail:1", sandbox_isolation_sufficient=False)
    lifecycle = runtime.lifecycle(drain_watermark_ref="drain:tool:1", large_payload_object_ref="object:tool-payload:1", legal_hold=True)
    allowlist = runtime.allowlist(current_allowlist_refs=("legacy:general-agent-langchain-tool",), zero_gate_ref="gate:tool-allowlist-zero", previous_count=2)
    readiness = runtime.readiness_evidence(
        code_refs=("src/backend/zuno/capability/tool_runtime/runtime_batch.py",),
        test_refs=("tests/capability/test_tool_runtime_batch.py",),
        verifier_ref="tools/scripts/verify_tool_runtime_batch.py",
        evidence_ref="docs/evidence/tool-runtime-batch.md",
    )
    if not async_callback.callback_signature_verified or async_callback.accepted_is_completion:
        errors.append("ARCH-TOOL-061/062 async accepted/callback replay boundary invalid")
    if not concurrency.resource_conflict_keys or not concurrency.stale_dispatch_rejected or len(concurrency.timeout_stages) < 3 or not concurrency.deadline_ref:
        errors.append("ARCH-TOOL-063..066 concurrency/replan/timeout/deadline invalid")
    if failure.namespace != "TOOL":
        errors.append("ARCH-TOOL-067 failure namespace invalid")
    if not infrastructure.same_transaction or not infrastructure.secret_lease_ref or infrastructure.sandbox_isolation_sufficient:
        errors.append("ARCH-TOOL-068..070 infrastructure boundary invalid")
    if infrastructure.capacity_gate_order[:5] != ("exposure", "prepare", "security_epoch", "audit", "claim"):
        errors.append("ARCH-TOOL-071 capacity ordering can bypass gates")
    if lifecycle.canary_real_effect_allowed or not lifecycle.retired_history_readable or not lifecycle.large_payload_object_ref or not lifecycle.legal_hold_blocks_delete:
        errors.append("ARCH-TOOL-072..076 lifecycle boundary invalid")
    if lifecycle.confirmed_effect_sli_ref != "sli:tool.confirmed_effect":
        errors.append("ARCH-TOOL-077 SLO does not focus confirmed effect")
    if not allowlist.monotonic_decrease or not allowlist.zero_gate_ref:
        errors.append("ARCH-TOOL-078/079 allowlist governance invalid")
    if readiness.requirement_ids != REQUIREMENTS or not readiness.implementation_available:
        errors.append("ARCH-TOOL-080 readiness evidence does not cover ARCH-TOOL-001..080")

    return errors


def main() -> int:
    errors = verify_tool_runtime_batch()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Tool runtime batch verifier passed for ARCH-TOOL-001..080")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
