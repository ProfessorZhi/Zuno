from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "backend"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from zuno.platform.model_gateway import (  # noqa: E402
    BudgetPolicy,
    BudgetVerdict,
    ModelAdmissionLayer,
    ModelAttemptState,
    ModelCallState,
    ModelCategory,
    ModelCapabilityStatus,
    ModelConfigActivationGate,
    ModelCircuitStatus,
    ModelControlActionType,
    ModelDomainWrite,
    ModelGateway,
    ModelGatewayProviderError,
    ModelGatewayRequest,
    ModelOperation,
    ModelOverloadState,
    ModelProviderHealthStatus,
    ModelProviderLifecycleState,
    ModelProviderSignalStatus,
    ModelRepairRecord,
    ModelQuotaPolicy,
    ModelUsageKind,
    MockModelProvider,
)
from zuno.platform.model_roles import ModelRole  # noqa: E402


REQUIREMENTS = tuple(f"ARCH-MODEL-{index:03d}" for index in range(1, 58))


def verify_model_gateway_runtime_batch() -> list[str]:
    errors: list[str] = []

    provider = MockModelProvider(
        provider_id="primary",
        model_id="mock-chat",
        response='{"answer": "ok", "confidence": 0.9}',
    )
    gateway = ModelGateway(providers=[provider])
    result = gateway.invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            operation=ModelOperation.GENERATE,
            role=ModelRole.PLANNER,
            prompt="Return a structured answer.",
            provider_id="primary",
            model_slot="reasoning_model",
            config_version="config:batch:1",
            prompt_version="prompt:batch:1",
            schema_version="schema:answer:1",
            adapter_version="adapter:primary:1",
            pricing_version="pricing:primary:1",
            security_epoch_ref="security:tenant:1",
            output_schema={"answer": str, "confidence": float},
        )
    )

    binding = result.binding.to_dict()
    required_binding = {
        "role",
        "operation",
        "model_slot",
        "config_version",
        "prompt_version",
        "schema_version",
        "model_version",
        "adapter_version",
        "pricing_version",
        "security_epoch_ref",
        "binding_hash",
    }
    if result.status != "succeeded" or result.call_state != ModelCallState.SUCCEEDED:
        errors.append("gateway call did not reach a distinct succeeded call state")
    if set(binding) != required_binding:
        errors.append("gateway binding does not freeze role/operation/config/prompt/schema/model/adapter/pricing/security")
    if result.binding.role != ModelRole.PLANNER or result.binding.operation != ModelOperation.GENERATE:
        errors.append("gateway did not keep role and operation separate")
    if result.selected_attempt_id != result.attempts[0].attempt_id:
        errors.append("gateway did not select exactly one response attempt")
    if [attempt.state for attempt in result.attempts] != [ModelAttemptState.SUCCEEDED]:
        errors.append("gateway attempt state machine did not record success")
    if [receipt.kind for receipt in result.usage_receipts] != [ModelUsageKind.ESTIMATE, ModelUsageKind.OBSERVED]:
        errors.append("gateway usage receipts did not separate estimate and observed facts")
    if not all(receipt.immutable for receipt in result.usage_receipts):
        errors.append("gateway usage receipts are not immutable")
    if result.structured_output != {"answer": "ok", "confidence": 0.9}:
        errors.append("gateway did not locally validate structured output")

    repair_result = ModelGateway(
        providers=[MockModelProvider(provider_id="repair", model_id="mock-repair", response='{"answer": "ok"}')]
    ).invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Return repairable structured output.",
            provider_id="repair",
            schema_version="schema:answer:2",
            output_schema={"answer": str, "confidence": float},
            repair_output='{"answer": "ok", "confidence": 0.8}',
        )
    )
    if not isinstance(repair_result.repair_record, ModelRepairRecord):
        errors.append("repair did not preserve a deterministic repair record")
    elif not repair_result.repair_record.deterministic or not repair_result.repair_record.original_output_sha256:
        errors.append("repair record did not preserve original output hash")
    if repair_result.output != '{"answer": "ok", "confidence": 0.8}':
        errors.append("repair result did not use validated repaired output")

    stream_result = ModelGateway(providers=[MockModelProvider(provider_id="stream", model_id="mock-stream")]).stream(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Stream in chunks.",
            provider_id="stream",
            metadata={
                "provider_stream_chunks": [
                    {"provider_chunk_id": "c2", "sequence": 2, "content": "done", "final": True},
                    {"provider_chunk_id": "c1", "sequence": 1, "content": "there"},
                    {"provider_chunk_id": "c0", "sequence": 0, "content": "hello"},
                    {"provider_chunk_id": "c1-dup", "sequence": 1, "content": "there"},
                ]
            },
        )
    )
    if [chunk.sequence for chunk in stream_result.gateway_chunks] != [0, 1, 1, 2]:
        errors.append("gateway stream chunks are not ordered")
    if [chunk.duplicate for chunk in stream_result.gateway_chunks] != [False, False, True, False]:
        errors.append("gateway stream chunks are not deduplicated")
    if not all(chunk.content_sha256 for chunk in stream_result.gateway_chunks):
        errors.append("gateway stream chunks do not carry content hashes")
    if [event.content for event in stream_result.product_events] != ["hello", "there", "done"]:
        errors.append("product stream events did not exclude duplicate provider chunks")
    if [event.provisional for event in stream_result.product_events] != [True, True, False]:
        errors.append("product stream events did not preserve provisional semantics")
    if stream_result.product_events[-1].event_type != "model_stream_completed":
        errors.append("product stream did not end with a completion event")

    blocked_provider = MockModelProvider(provider_id="blocked", model_id="mock-blocked")
    blocked = ModelGateway(providers=[blocked_provider], default_budget=BudgetPolicy(max_cost=0.000001)).invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt=" ".join(["expensive"] * 200),
            provider_id="blocked",
        )
    )
    if blocked.status != "blocked" or blocked_provider.call_count != 0:
        errors.append("budget gate did not block before provider dispatch")

    primary = MockModelProvider(provider_id="timeout", model_id="mock-timeout", fail_mode="timeout")
    fallback = MockModelProvider(provider_id="fallback", model_id="mock-fallback")
    fallback_result = ModelGateway(providers=[primary, fallback]).invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Fallback after timeout.",
            provider_id="timeout",
            fallback_provider_ids=["fallback"],
        )
    )
    if [attempt.state for attempt in fallback_result.attempts] != [
        ModelAttemptState.UNKNOWN_RECONCILE,
        ModelAttemptState.SUCCEEDED,
    ]:
        errors.append("timeout did not enter unknown/reconcile before fallback")
    if not fallback_result.attempts[0].reconcile_required:
        errors.append("unknown provider execution did not require reconcile")

    failed_result = ModelGateway(
        providers=[MockModelProvider(provider_id="failed", model_id="mock-failed", fail_mode="timeout")]
    ).invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Fail without fallback.",
            provider_id="failed",
        )
    )
    if failed_result.status != "failed" or failed_result.call_state != ModelCallState.FAILED:
        errors.append("all-provider-failed path did not return a failed result")
    if not failed_result.attempts[0].reconcile_required:
        errors.append("provider-may-have-executed timeout did not enter reconcile")
    if [action.action_type for action in failed_result.control_actions] != [
        ModelControlActionType.RECONCILE,
        ModelControlActionType.ESCALATE,
        ModelControlActionType.REPLAN_PROPOSAL,
    ]:
        errors.append("retry/fallback/escalation/replan control actions are not separated")
    if failed_result.control_actions[-1].owner != "AGENT_CORE":
        errors.append("replan proposal is not owned by Agent Core")
    if any(action.activates_plan_version or action.modifies_run_outcome for action in failed_result.control_actions):
        errors.append("model gateway control action mutates Agent Core domain state")

    operation_gateway = ModelGateway(
        providers=[
            MockModelProvider(provider_id="judge", model_id="mock-judge", categories=[ModelCategory.EVAL_JUDGE]),
            MockModelProvider(provider_id="embedding", model_id="mock-embedding", categories=[ModelCategory.EMBEDDING]),
        ]
    )
    embeddings = operation_gateway.embed_batch(
        texts=("alpha", "", "beta"),
        revision="embed-rev-1",
        dimension=4,
        normalization="L2",
        index_generation="index-gen-7",
    )
    if [item.state for item in embeddings] != ["SUCCEEDED", "FAILED", "SUCCEEDED"]:
        errors.append("embedding batch did not keep item-level terminal states")
    if not all(item.revision == "embed-rev-1" and item.dimension == 4 for item in embeddings):
        errors.append("embedding results did not freeze revision and dimension")
    if embeddings[0].normalization != "L2" or embeddings[0].index_generation != "index-gen-7":
        errors.append("embedding result did not freeze normalization and index generation")

    reranked = operation_gateway.rerank((("doc-b", 0.2), ("doc-a", 0.9)))
    if [(item.item_id, item.score, item.rank) for item in reranked] != [("doc-a", 0.9, 1), ("doc-b", 0.2, 2)]:
        errors.append("rerank result did not preserve item id, score, and rank")

    region = operation_gateway.analyze_vision(
        source_lineage_ref="source:pdf:1",
        page_number=3,
        bbox=(1.0, 2.0, 30.0, 40.0),
        text="OCR text",
    )
    if region.page_number != 3 or region.bbox != (1.0, 2.0, 30.0, 40.0) or region.source_lineage_ref != "source:pdf:1":
        errors.append("vision/OCR result did not preserve page, bbox, and source lineage")

    segments = operation_gateway.transcribe(((0, 1200, "hello", True), (1200, 2400, "world", False)))
    if [(segment.start_ms, segment.end_ms, segment.partial) for segment in segments] != [(0, 1200, True), (1200, 2400, False)]:
        errors.append("transcription result did not preserve segment timestamp and partial semantics")

    classification = operation_gateway.classify(
        label_scores={"approve": 0.61, "deny": 0.39},
        threshold=0.7,
        calibration_ref="calibration:v1",
    )
    if classification.label is not None or not classification.abstained or classification.calibration_ref != "calibration:v1":
        errors.append("classification did not support threshold, calibration, and abstain")

    judge = operation_gateway.judge(
        ModelGatewayRequest(
            category=ModelCategory.EVAL_JUDGE,
            prompt="Judge the answer.",
            provider_id="judge",
        ),
        score=0.82,
        rationale="grounded enough",
    )
    if not judge.gateway_audited or not judge.budget_verdict.allowed:
        errors.append("judge call did not go through gateway budget audit")
    if judge.sole_quality_proof_allowed or not judge.requires_external_evidence:
        errors.append("judge result can be used as sole quality proof")

    compressed = operation_gateway.compress_context(
        source_text="Important renewal constraints conflict with outdated pricing.",
        lineage_refs=("ctx:event:1", "ctx:evidence:2"),
        constraints=("preserve renewal date",),
        conflict_refs=("conflict:pricing",),
        distortion_risks=("pricing may be stale",),
    )
    if not compressed.lineage_refs or not compressed.preserved_constraints or not compressed.distortion_risks:
        errors.append("context compression did not preserve lineage, constraints, and distortion risks")
    if compressed.conflict_refs != ("conflict:pricing",):
        errors.append("context compression did not preserve conflict refs")

    memory = operation_gateway.memory_candidate(
        payload={"fact": "Supplier renewal date is July 18."},
        source_model_call_ref="model_call_memory",
    )
    if memory.target_owner != "MEMORY" or not memory.requires_owner_review or memory.directly_committable:
        errors.append("memory model output is not restricted to candidate form")

    risk = operation_gateway.security_risk_proposal(
        risk_level="HIGH",
        evidence_refs=("ev:secret",),
        source_model_call_ref="model_call_security",
    )
    if risk.target_owner != "SECURITY" or not risk.requires_owner_review or risk.directly_enforced:
        errors.append("security model output is not restricted to risk proposal form")

    action = operation_gateway.tool_action_proposal(
        action_name="send_email",
        args={"to": "team@example.com", "body": "Draft"},
        source_model_call_ref="model_call_tool",
    )
    if action.target_owner != "AGENT_CORE" or not action.requires_owner_binding or action.directly_executable:
        errors.append("tool model output is not restricted to action proposal form")

    usage_gateway = ModelGateway(
        providers=[
            MockModelProvider(provider_id="usage_primary", model_id="mock-primary", fail_mode="timeout"),
            MockModelProvider(provider_id="usage_fallback", model_id="mock-fallback"),
        ]
    )
    usage_result = usage_gateway.invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Fallback usage accounting.",
            provider_id="usage_primary",
            fallback_provider_ids=["usage_fallback"],
            pricing_version="pricing:v1",
        )
    )
    if [receipt.kind for receipt in usage_result.usage_receipts] != [
        ModelUsageKind.ESTIMATE,
        ModelUsageKind.OBSERVED,
        ModelUsageKind.OBSERVED,
    ]:
        errors.append("every attempt, including failure/fallback, did not produce usage facts")
    if usage_result.attempts[0].usage_receipt_id != usage_result.usage_receipts[1].usage_receipt_id:
        errors.append("failed attempt is not linked to an observed usage receipt")
    observed = usage_result.usage_receipts[-1]
    settled = usage_gateway.settle_usage(observed)
    correction = usage_gateway.correct_usage(observed, prompt_tokens=7, completion_tokens=11)
    if [receipt.kind for receipt in [observed, settled, correction]] != [
        ModelUsageKind.OBSERVED,
        ModelUsageKind.SETTLED,
        ModelUsageKind.CORRECTION,
    ]:
        errors.append("usage estimate/observed/settled/correction are not separated")
    if observed.pricing_version != settled.pricing_version or observed.pricing_version != correction.pricing_version:
        errors.append("pricing version was not frozen across historical receipts")
    if observed.usage_receipt_id in {settled.usage_receipt_id, correction.usage_receipt_id}:
        errors.append("settlement/correction overwrote historical usage receipt")

    quota = ModelQuotaPolicy(quota_scope="tenant:t1:model", token_limit=10, reserved_tokens=0, generation=0)
    first = usage_gateway.reserve_quota(policy=quota, requested_tokens=6, expected_generation=0)
    stale = usage_gateway.reserve_quota(policy=quota, requested_tokens=6, expected_generation=0)
    second = usage_gateway.reserve_quota(policy=quota, requested_tokens=3, expected_generation=1)
    exhausted = usage_gateway.reserve_quota(policy=quota, requested_tokens=2, expected_generation=2)
    if not first.accepted or first.committed_generation != 1:
        errors.append("quota CAS first reservation did not commit generation 1")
    if stale.accepted or stale.reason != "generation_mismatch":
        errors.append("quota CAS race did not reject stale generation")
    if not second.accepted or second.committed_generation != 2:
        errors.append("quota CAS second reservation did not commit generation 2")
    if exhausted.accepted or exhausted.reason != "quota_exhausted":
        errors.append("quota did not enforce token limit separately from budget")

    unknown_health = usage_gateway.evaluate_provider_health(
        provider_id="usage_fallback",
        model_id="mock-fallback",
        region="us-east-1",
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        window_started_at=1.0,
        window_ended_at=2.0,
        success_count=0,
        failure_count=0,
        evidence_ref=None,
    )
    healthy = usage_gateway.evaluate_provider_health(
        provider_id="usage_fallback",
        model_id="mock-fallback",
        region="us-east-1",
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        window_started_at=1.0,
        window_ended_at=2.0,
        success_count=9,
        failure_count=1,
        evidence_ref="ev:health-window:1",
    )
    unhealthy_other_region = usage_gateway.evaluate_provider_health(
        provider_id="usage_fallback",
        model_id="mock-fallback",
        region="eu-west-1",
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        window_started_at=1.0,
        window_ended_at=2.0,
        success_count=1,
        failure_count=9,
        evidence_ref="ev:health-window:2",
    )
    if unknown_health.status != ModelProviderHealthStatus.UNKNOWN or unknown_health.is_healthy:
        errors.append("provider health without evidence defaulted to healthy")
    if healthy.status != ModelProviderHealthStatus.HEALTHY or not healthy.is_healthy:
        errors.append("provider health did not use window evidence for healthy state")

    healthy_circuit = usage_gateway.evaluate_circuit(healthy)
    unhealthy_region_circuit = usage_gateway.evaluate_circuit(unhealthy_other_region)
    unknown_circuit = usage_gateway.evaluate_circuit(unknown_health)
    if healthy_circuit.status != ModelCircuitStatus.CLOSED:
        errors.append("healthy provider window did not close circuit")
    if unhealthy_region_circuit.status != ModelCircuitStatus.OPEN or unknown_circuit.status != ModelCircuitStatus.OPEN:
        errors.append("unhealthy/unknown provider windows did not open circuit")
    if healthy_circuit.key.isolation_key == unhealthy_region_circuit.key.isolation_key:
        errors.append("circuit isolation key did not include region")

    capability_states = [
        usage_gateway.capability_profile(
            capability_id=f"cap:{status.value.lower()}",
            provider_id="usage_fallback",
            model_id="mock-fallback",
            operation=ModelOperation.GENERATE,
            status=status,
            evidence_ref=f"ev:capability:{status.value.lower()}",
        )
        for status in (
            ModelCapabilityStatus.DEGRADED,
            ModelCapabilityStatus.STALE,
            ModelCapabilityStatus.REVOKED,
        )
    ]
    if [profile.status for profile in capability_states] != [
        ModelCapabilityStatus.DEGRADED,
        ModelCapabilityStatus.STALE,
        ModelCapabilityStatus.REVOKED,
    ]:
        errors.append("capability lifecycle did not preserve degrade/stale/revoke states")
    if capability_states[-1].dispatch_allowed:
        errors.append("revoked capability still allows dispatch")
    if not all(profile.requires_operator_review for profile in capability_states):
        errors.append("degraded/stale/revoked capabilities do not require operator review")

    generate_suite = usage_gateway.adapter_conformance_suite(
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v1",
        model_mapping_version="mapping:v1",
        evidence_ref="ev:conformance:generate:v1",
        passed=True,
    )
    embed_suite = usage_gateway.adapter_conformance_suite(
        operation=ModelOperation.EMBED,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v1",
        model_mapping_version="mapping:v1",
        evidence_ref="ev:conformance:embed:v1",
        passed=True,
    )
    if generate_suite.suite_id == embed_suite.suite_id or generate_suite.conformance_hash == embed_suite.conformance_hash:
        errors.append("adapter conformance suite is not operation-specific")
    if not usage_gateway.validate_adapter_conformance(
        generate_suite,
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v1",
        model_mapping_version="mapping:v1",
    ).valid:
        errors.append("unchanged adapter conformance did not validate")
    if not usage_gateway.validate_adapter_conformance(
        generate_suite,
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v2",
        model_mapping_version="mapping:v1",
    ).requires_revalidation:
        errors.append("SDK/API change did not invalidate conformance")
    if not usage_gateway.validate_adapter_conformance(
        generate_suite,
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v1",
        model_mapping_version="mapping:v2",
    ).requires_revalidation:
        errors.append("model mapping change did not invalidate conformance")

    unknown_signal = usage_gateway.interpret_provider_signal(
        signal_kind="event",
        raw_value="provider_future_success",
        known_values=("provider_success", "provider_failure"),
    )
    known_signal = usage_gateway.interpret_provider_signal(
        signal_kind="event",
        raw_value="provider_success",
        known_values=("provider_success", "provider_failure"),
    )
    if unknown_signal.status != ModelProviderSignalStatus.UNKNOWN_FAIL_CLOSED or unknown_signal.success:
        errors.append("unknown provider signal did not fail closed")
    if known_signal.status != ModelProviderSignalStatus.ACCEPTED or not known_signal.success:
        errors.append("known provider signal did not remain accepted")

    snapshot_a = usage_gateway.create_config_snapshot(
        config_version="config:v1",
        generation=7,
        payload={"routing": {"planner": "primary"}, "limits": {"max_tokens": 128}},
    )
    snapshot_b = usage_gateway.create_config_snapshot(
        config_version="config:v1",
        generation=7,
        payload={"limits": {"max_tokens": 128}, "routing": {"planner": "primary"}},
    )
    changed_snapshot = usage_gateway.create_config_snapshot(
        config_version="config:v1",
        generation=8,
        payload={"routing": {"planner": "fallback"}, "limits": {"max_tokens": 128}},
    )
    if snapshot_a.content_sha256 != snapshot_b.content_sha256 or snapshot_a.snapshot_id != snapshot_b.snapshot_id:
        errors.append("gateway config snapshot is not canonical/content-addressed")
    if snapshot_a.snapshot_id == changed_snapshot.snapshot_id:
        errors.append("gateway config snapshot id did not change when config content/generation changed")

    rejected_activation = usage_gateway.activate_config_snapshot(
        snapshot_a,
        expected_generation=6,
        active_generation=7,
        validation_passed=True,
        replay_passed=True,
        canary_passed=True,
        rollback_snapshot_ref="config_snapshot_previous",
    )
    accepted_activation = usage_gateway.activate_config_snapshot(
        snapshot_a,
        expected_generation=7,
        active_generation=7,
        validation_passed=True,
        replay_passed=True,
        canary_passed=True,
        rollback_snapshot_ref="config_snapshot_previous",
    )
    if rejected_activation.accepted or rejected_activation.reason != "generation_mismatch":
        errors.append("config activation did not enforce CAS generation")
    if not accepted_activation.accepted:
        errors.append("valid config activation was not accepted")
    if accepted_activation.completed_gates != (
        ModelConfigActivationGate.VALIDATION,
        ModelConfigActivationGate.REPLAY,
        ModelConfigActivationGate.CANARY,
        ModelConfigActivationGate.CAS,
        ModelConfigActivationGate.ROLLBACK,
    ):
        errors.append("config activation did not record validation/replay/canary/CAS/rollback gates")

    call_binding = usage_gateway.bind_call_config_snapshot(call_id="model_call_1", snapshot=snapshot_a)
    if (
        call_binding.config_snapshot_id != snapshot_a.snapshot_id
        or call_binding.config_hash != snapshot_a.content_sha256
        or not call_binding.immutable
    ):
        errors.append("model call did not bind an immutable config snapshot")

    states = {
        state: usage_gateway.provider_lifecycle_record(
            provider_id="usage_fallback",
            model_id="mock-fallback",
            state=state,
            generation=index,
            evidence_ref=f"ev:lifecycle:{state.value.lower()}",
        )
        for index, state in enumerate(ModelProviderLifecycleState, start=1)
    }
    if states[ModelProviderLifecycleState.PROBE].accepts_new_dispatch:
        errors.append("provider probe state accepts new dispatch")
    if not states[ModelProviderLifecycleState.ENABLED].accepts_new_dispatch:
        errors.append("provider enabled state blocks dispatch")
    if not states[ModelProviderLifecycleState.DEPRECATED].accepts_new_dispatch:
        errors.append("provider deprecated state did not allow controlled dispatch")
    if states[ModelProviderLifecycleState.DRAINING].accepts_new_dispatch:
        errors.append("provider draining state accepts new dispatch")
    if states[ModelProviderLifecycleState.DISABLED].accepts_new_dispatch:
        errors.append("provider disabled state accepts new dispatch")
    if states[ModelProviderLifecycleState.RETIRED].accepts_new_dispatch:
        errors.append("provider retired state accepts new dispatch")
    if not all(record.preserves_history for record in states.values()):
        errors.append("provider lifecycle does not preserve historical attempt/usage/audit")

    emergency = usage_gateway.emergency_disable_provider(
        provider_id="usage_fallback",
        model_id="mock-fallback",
        generation=9,
        reason="provider_key_leak",
    )
    if not emergency.blocks_new_dispatch or not emergency.late_results_isolated:
        errors.append("emergency disable did not block new dispatch and isolate late results")
    if not emergency.quarantine_ref.startswith("provider_disable_quarantine_"):
        errors.append("emergency disable did not create quarantine ref for late results")

    capacity = {
        "global": 10,
        "provider:usage_fallback": 10,
        "model:usage_fallback:mock-fallback": 10,
        "operation:generate": 10,
        "role:executor": 10,
    }
    admitted = usage_gateway.evaluate_admission(
        tenant_id="tenant-a",
        role=ModelRole.EXECUTOR,
        provider_id="usage_fallback",
        model_id="mock-fallback",
        operation=ModelOperation.GENERATE,
        requested_units=2,
        capacity_by_key=capacity,
        tenant_inflight=1,
        tenant_fairness_limit=3,
        reserved_capacity_units=0,
        waiting_age_ms=10,
        starvation_threshold_ms=1000,
    )
    fair_limited = usage_gateway.evaluate_admission(
        tenant_id="tenant-a",
        role=ModelRole.EXECUTOR,
        provider_id="usage_fallback",
        model_id="mock-fallback",
        operation=ModelOperation.GENERATE,
        requested_units=2,
        capacity_by_key=capacity,
        tenant_inflight=3,
        tenant_fairness_limit=3,
        reserved_capacity_units=0,
        waiting_age_ms=10,
        starvation_threshold_ms=1000,
    )
    reserved = usage_gateway.evaluate_admission(
        tenant_id="tenant-a",
        role=ModelRole.EXECUTOR,
        provider_id="usage_fallback",
        model_id="mock-fallback",
        operation=ModelOperation.GENERATE,
        requested_units=2,
        capacity_by_key=capacity,
        tenant_inflight=3,
        tenant_fairness_limit=3,
        reserved_capacity_units=2,
        waiting_age_ms=10,
        starvation_threshold_ms=1000,
    )
    anti_starvation = usage_gateway.evaluate_admission(
        tenant_id="tenant-b",
        role=ModelRole.EXECUTOR,
        provider_id="usage_fallback",
        model_id="mock-fallback",
        operation=ModelOperation.GENERATE,
        requested_units=2,
        capacity_by_key=capacity,
        tenant_inflight=3,
        tenant_fairness_limit=3,
        reserved_capacity_units=0,
        waiting_age_ms=1500,
        starvation_threshold_ms=1000,
    )
    if not admitted.accepted:
        errors.append("admission did not accept available global/provider/model/operation/role capacity")
    if [check.layer for check in admitted.layer_checks] != [
        ModelAdmissionLayer.GLOBAL,
        ModelAdmissionLayer.PROVIDER,
        ModelAdmissionLayer.MODEL,
        ModelAdmissionLayer.OPERATION,
        ModelAdmissionLayer.ROLE,
    ]:
        errors.append("admission did not evaluate capacity from global through role")
    if fair_limited.accepted or not fair_limited.fairness_limited:
        errors.append("admission did not enforce tenant fairness")
    if not reserved.accepted or reserved.reserved_capacity_used != 2:
        errors.append("admission did not apply reserved capacity")
    if not anti_starvation.accepted or not anti_starvation.starvation_prevention_applied:
        errors.append("admission did not prevent starvation for old queued work")

    queued_binding = usage_gateway.bind_call_config_snapshot(call_id="model_call_queued", snapshot=snapshot_a)
    queued = usage_gateway.queue_request_binding(
        call_id="model_call_queued",
        deadline_at=1234.5,
        security_epoch_ref="security:tenant:2",
        budget_verdict=BudgetVerdict(allowed=True, reason="within_budget", estimated_cost=0.01),
        config_binding=queued_binding,
    )
    if (
        queued.deadline_at != 1234.5
        or queued.security_epoch_ref != "security:tenant:2"
        or not queued.budget_verdict.allowed
        or queued.config_binding.config_snapshot_id != snapshot_a.snapshot_id
    ):
        errors.append("queued request did not preserve deadline/security/budget/config binding")

    normal = usage_gateway.evaluate_overload(current_load_units=5, capacity_units=10)
    backpressure = usage_gateway.evaluate_overload(current_load_units=15, capacity_units=10)
    shedding = usage_gateway.evaluate_overload(current_load_units=25, capacity_units=10)
    required_gates = ("security", "validation", "usage", "audit", "budget")
    if normal.state != ModelOverloadState.NORMAL:
        errors.append("normal load did not produce explicit normal state")
    if backpressure.state != ModelOverloadState.BACKPRESSURE or not backpressure.backpressure:
        errors.append("overload did not produce explicit backpressure state")
    if shedding.state != ModelOverloadState.LOAD_SHEDDING or not shedding.load_shedding:
        errors.append("severe overload did not produce explicit load shedding state")
    if shedding.preserved_gates != required_gates or shedding.bypass_allowed:
        errors.append("overload bypassed security/validation/usage/audit/budget gates")

    split_action_result = ModelGateway(
        providers=[
            MockModelProvider(provider_id="primary_error", model_id="mock-primary", fail_mode="error"),
            MockModelProvider(provider_id="fallback_repair", model_id="mock-fallback", response='{"answer": "ok"}'),
        ]
    ).invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Fallback then repair.",
            provider_id="primary_error",
            fallback_provider_ids=["fallback_repair"],
            schema_version="schema:answer:2",
            output_schema={"answer": str, "confidence": float},
            repair_output='{"answer": "ok", "confidence": 0.7}',
        )
    )
    if [action.action_type for action in split_action_result.control_actions] != [
        ModelControlActionType.FALLBACK,
        ModelControlActionType.REPAIR,
    ]:
        errors.append("fallback and repair are not independent control actions")

    guarded_gateway = ModelGateway(providers=[MockModelProvider(provider_id="guard", model_id="mock-guard")])
    for forbidden_write in [ModelDomainWrite.PLAN_VERSION_ACTIVATION, ModelDomainWrite.RUN_OUTCOME_UPDATE]:
        try:
            guarded_gateway.invoke(
                ModelGatewayRequest(
                    category=ModelCategory.CHAT,
                    prompt="Forbidden domain write.",
                    provider_id="guard",
                    requested_domain_writes=(forbidden_write,),
                )
            )
        except ModelGatewayProviderError:
            pass
        else:
            errors.append(f"gateway accepted forbidden Agent Core domain write: {forbidden_write.value}")

    cancelled_provider = MockModelProvider(provider_id="cancel", model_id="mock-cancel")
    cancelled = ModelGateway(providers=[cancelled_provider]).invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Cancel before dispatch.",
            provider_id="cancel",
            metadata={"cancel_before_dispatch": True},
        )
    )
    if cancelled.status != "cancelled" or cancelled.call_state != ModelCallState.CANCELLED:
        errors.append("cancel-before-dispatch did not produce a distinct cancelled call state")
    if cancelled.attempts or cancelled_provider.call_count != 0:
        errors.append("cancel-before-dispatch still dispatched a provider attempt")

    source = (REPO_ROOT / "src/backend/zuno/platform/model_gateway.py").read_text(encoding="utf-8")
    forbidden = ("import openai", "from openai", "import anthropic", "from anthropic")
    if any(token in source for token in forbidden):
        errors.append("model gateway imports provider SDK directly")

    return errors


def main() -> int:
    errors = verify_model_gateway_runtime_batch()
    if errors:
        print("Model Gateway runtime batch verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Model Gateway runtime batch verification passed for {', '.join(REQUIREMENTS)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
