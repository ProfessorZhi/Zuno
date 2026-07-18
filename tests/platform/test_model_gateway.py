from __future__ import annotations

from types import SimpleNamespace

from zuno.platform.model_gateway import (
    BudgetPolicy,
    BudgetVerdict,
    ModelAdapterRolloutMode,
    ModelAdmissionLayer,
    ModelAttemptState,
    ModelCacheKind,
    ModelCallRequest,
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
    ModelOperationalCommandKind,
    ModelOverloadState,
    ModelProviderHealthStatus,
    ModelProviderLifecycleState,
    ModelProviderSignalStatus,
    ModelQuotaPolicy,
    ModelRepairRecord,
    ModelReadinessProbe,
    ModelReadinessStatus,
    ModelRetentionSubject,
    ModelDeletionStep,
    ModelUsageKind,
    MockModelProvider,
)
from zuno.platform.model_roles import ModelRole


def test_model_gateway_routes_roles_and_records_trace_metadata() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat")
    gateway = ModelGateway(providers=[provider])

    result = gateway.invoke(
        ModelCallRequest(
            category=ModelCategory.CHAT,
            role=ModelRole.PLANNER,
            run_id="run-1",
            task_id="task-1",
            trace_id="trace-1",
            workspace_id="workspace-1",
            user_id="user-1",
            model_slot="reasoning_model",
            timeout_ms=1500,
            prompt="Plan with api_key sk-secret.",
            provider_id="primary",
            metadata={"api_key": "sk-secret", "safe": "yes"},
        )
    )

    assert result.status == "succeeded"
    assert result.metrics.role == ModelRole.PLANNER
    assert result.trace_event["payload"]["role"] == "planner"
    assert result.trace_event["payload"]["run_id"] == "run-1"
    assert result.trace_event["payload"]["model_slot"] == "reasoning_model"
    assert result.trace_event["payload"]["timeout_ms"] == 1500
    assert "sk-secret" not in repr(result.trace_event)


def test_model_call_request_alias_preserves_old_gateway_request() -> None:
    request = ModelGatewayRequest(
        category="chat",
        role="tool_call",
        prompt="Pick a tool.",
    )

    assert isinstance(request, ModelCallRequest)
    assert request.category == ModelCategory.CHAT
    assert request.role == ModelRole.TOOL_CALL


def test_gateway_get_chat_model_uses_legacy_model_manager_adapter(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []
    fake_model = SimpleNamespace(model_name="fake-chat")

    def fake_get_user_model(**kwargs):
        calls.append(("user", kwargs))
        return fake_model

    def fake_get_conversation_model():
        calls.append(("conversation", None))
        return fake_model

    def fake_get_tool_invocation_model():
        calls.append(("tool", None))
        return fake_model

    monkeypatch.setattr("zuno.core.models.manager.ModelManager.get_user_model", fake_get_user_model)
    monkeypatch.setattr(
        "zuno.core.models.manager.ModelManager.get_conversation_model",
        fake_get_conversation_model,
    )
    monkeypatch.setattr(
        "zuno.core.models.manager.ModelManager.get_tool_invocation_model",
        fake_get_tool_invocation_model,
    )

    gateway = ModelGateway(providers=[MockModelProvider()])

    assert gateway.get_chat_model({"model": "deepseek-chat"}, role=ModelRole.EXECUTOR) is fake_model
    assert gateway.get_chat_model({"model_slot": "conversation_model"}, role=ModelRole.SYNTHESIS) is fake_model
    assert gateway.get_chat_model(role=ModelRole.TOOL_CALL) is fake_model

    assert calls == [
        ("user", {"model": "deepseek-chat"}),
        ("conversation", None),
        ("tool", None),
    ]


def test_model_gateway_budget_block_includes_role_without_provider_call() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat")
    gateway = ModelGateway(providers=[provider], default_budget=BudgetPolicy(max_cost=0.000001))

    result = gateway.invoke(
        ModelCallRequest(
            category="chat",
            role="critic",
            prompt=" ".join(["expensive"] * 200),
            provider_id="primary",
        )
    )

    assert result.status == "blocked"
    assert result.metrics.role == ModelRole.CRITIC
    assert result.trace_event["payload"]["role"] == "critic"
    assert provider.call_count == 0


def test_model_gateway_freezes_call_binding_attempt_and_usage_receipts() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat", response='{"answer": "ok", "confidence": 0.9}')
    gateway = ModelGateway(providers=[provider])

    result = gateway.invoke(
        ModelGatewayRequest(
            category="chat",
            operation=ModelOperation.GENERATE,
            role="planner",
            prompt="Return structured output.",
            provider_id="primary",
            model_slot="reasoning_model",
            config_version="config:2026-07-18",
            prompt_version="prompt:planner:3",
            schema_version="schema:answer:1",
            adapter_version="adapter:primary:2",
            pricing_version="pricing:primary:2026-07",
            security_epoch_ref="sec_epoch:tenant:9",
            output_schema={"answer": str, "confidence": float},
        )
    )

    assert result.status == "succeeded"
    assert result.call_state == ModelCallState.SUCCEEDED
    assert result.binding.operation == ModelOperation.GENERATE
    assert result.binding.config_version == "config:2026-07-18"
    assert result.binding.prompt_version == "prompt:planner:3"
    assert result.binding.schema_version == "schema:answer:1"
    assert result.binding.adapter_version == "adapter:primary:2"
    assert result.binding.pricing_version == "pricing:primary:2026-07"
    assert result.binding.security_epoch_ref == "sec_epoch:tenant:9"
    assert result.selected_attempt_id == result.attempts[0].attempt_id
    assert [attempt.state for attempt in result.attempts] == [ModelAttemptState.SUCCEEDED]
    assert [receipt.kind for receipt in result.usage_receipts] == [ModelUsageKind.ESTIMATE, ModelUsageKind.OBSERVED]
    assert all(receipt.immutable for receipt in result.usage_receipts)
    assert result.structured_output == {"answer": "ok", "confidence": 0.9}
    assert result.trace_event["payload"]["binding"]["binding_hash"] == result.binding.binding_hash
    assert len([attempt for attempt in result.attempts if attempt.state == ModelAttemptState.SUCCEEDED]) == 1


def test_model_gateway_timeout_records_unknown_attempt_before_fallback() -> None:
    primary = MockModelProvider(provider_id="primary", model_id="mock-primary", fail_mode="timeout")
    fallback = MockModelProvider(provider_id="fallback", model_id="mock-fallback")
    gateway = ModelGateway(providers=[primary, fallback])

    result = gateway.invoke(
        ModelGatewayRequest(
            category="chat",
            prompt="Fallback after an unknown timeout.",
            provider_id="primary",
            fallback_provider_ids=["fallback"],
        )
    )

    assert result.status == "succeeded"
    assert [attempt.state for attempt in result.attempts] == [
        ModelAttemptState.UNKNOWN_RECONCILE,
        ModelAttemptState.SUCCEEDED,
    ]
    assert result.attempts[0].reconcile_required is True
    assert result.attempts[0].failure_code == "MODEL_TIMEOUT_UNKNOWN"
    assert len(result.usage_receipts) == 3
    assert result.metrics.fallback_reason == "timeout:primary"


def test_model_gateway_cancel_before_dispatch_records_usage_without_provider_call() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat")
    gateway = ModelGateway(providers=[provider])

    result = gateway.invoke(
        ModelGatewayRequest(
            category="chat",
            prompt="This should not dispatch.",
            provider_id="primary",
            metadata={"cancel_before_dispatch": True},
        )
    )

    assert result.status == "cancelled"
    assert result.call_state == ModelCallState.CANCELLED
    assert result.attempts == ()
    assert [receipt.kind for receipt in result.usage_receipts] == [ModelUsageKind.ESTIMATE, ModelUsageKind.OBSERVED]
    assert provider.call_count == 0


def test_model_gateway_repair_preserves_original_output_with_deterministic_record() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat", response='{"answer": "ok"}')
    gateway = ModelGateway(providers=[provider])

    result = gateway.invoke(
        ModelGatewayRequest(
            category="chat",
            prompt="Return structured output with repair.",
            provider_id="primary",
            schema_version="schema:answer:2",
            output_schema={"answer": str, "confidence": float},
            repair_output='{"answer": "ok", "confidence": 0.8}',
        )
    )

    assert result.status == "succeeded"
    assert result.output == '{"answer": "ok", "confidence": 0.8}'
    assert result.structured_output == {"answer": "ok", "confidence": 0.8}
    assert isinstance(result.repair_record, ModelRepairRecord)
    assert result.repair_record.deterministic is True
    assert result.repair_record.schema_version == "schema:answer:2"
    assert result.repair_record.failure_code == "MODEL_STRUCTURED_OUTPUT_MISSING_FIELDS"


def test_model_gateway_stream_layers_chunks_for_product_events() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat")
    gateway = ModelGateway(providers=[provider])

    result = gateway.stream(
        ModelGatewayRequest(
            category="chat",
            prompt="Stream this.",
            provider_id="primary",
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

    assert [chunk.sequence for chunk in result.gateway_chunks] == [0, 1, 1, 2]
    assert [chunk.duplicate for chunk in result.gateway_chunks] == [False, False, True, False]
    assert all(chunk.content_sha256 for chunk in result.gateway_chunks)
    assert [event.content for event in result.product_events] == ["hello", "there", "done"]
    assert [event.provisional for event in result.product_events] == [True, True, False]
    assert result.product_events[-1].event_type == "model_stream_completed"
    assert result.attempt.provider_id == "primary"
    assert result.usage_receipts[0].attempt_id == result.attempt.attempt_id


def test_model_gateway_failed_call_returns_reconcile_escalation_and_replan_proposal() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat", fail_mode="timeout")
    gateway = ModelGateway(providers=[provider])

    result = gateway.invoke(
        ModelGatewayRequest(
            category="chat",
            prompt="Fail without fallback.",
            provider_id="primary",
        )
    )

    assert result.status == "failed"
    assert result.call_state == ModelCallState.FAILED
    assert result.attempts[0].reconcile_required is True
    assert result.attempts[0].state == ModelAttemptState.UNKNOWN_RECONCILE
    assert [action.action_type for action in result.control_actions] == [
        ModelControlActionType.RECONCILE,
        ModelControlActionType.ESCALATE,
        ModelControlActionType.REPLAN_PROPOSAL,
    ]
    assert result.control_actions[-1].owner == "AGENT_CORE"
    assert all(not action.activates_plan_version and not action.modifies_run_outcome for action in result.control_actions)


def test_model_gateway_fallback_and_repair_are_separate_control_actions() -> None:
    primary = MockModelProvider(provider_id="primary", model_id="mock-primary", fail_mode="error")
    fallback = MockModelProvider(provider_id="fallback", model_id="mock-fallback", response='{"answer": "ok"}')
    gateway = ModelGateway(providers=[primary, fallback])

    result = gateway.invoke(
        ModelGatewayRequest(
            category="chat",
            prompt="Fallback then repair.",
            provider_id="primary",
            fallback_provider_ids=["fallback"],
            schema_version="schema:answer:2",
            output_schema={"answer": str, "confidence": float},
            repair_output='{"answer": "ok", "confidence": 0.7}',
        )
    )

    assert result.status == "succeeded"
    assert [action.action_type for action in result.control_actions] == [
        ModelControlActionType.FALLBACK,
        ModelControlActionType.REPAIR,
    ]
    assert result.repair_record is not None
    assert result.metrics.provider_id == "fallback"


def test_model_gateway_rejects_plan_version_and_run_outcome_writes() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])

    for write in [ModelDomainWrite.PLAN_VERSION_ACTIVATION, ModelDomainWrite.RUN_OUTCOME_UPDATE]:
        try:
            gateway.invoke(
                ModelGatewayRequest(
                    category="chat",
                    prompt="Forbidden domain write.",
                    provider_id="primary",
                    requested_domain_writes=(write,),
                )
            )
        except ModelGatewayProviderError as exc:
            assert "PlanVersion" in str(exc) or "RunOutcome" in str(exc)
        else:
            raise AssertionError("gateway accepted forbidden Agent Core domain write")


def test_model_gateway_operation_result_contracts_cover_embedding_rerank_media_and_judge() -> None:
    gateway = ModelGateway(
        providers=[
            MockModelProvider(provider_id="judge", model_id="mock-judge", categories=[ModelCategory.EVAL_JUDGE]),
            MockModelProvider(provider_id="embedding", model_id="mock-embedding", categories=[ModelCategory.EMBEDDING]),
        ]
    )

    embeddings = gateway.embed_batch(
        texts=("alpha", "", "beta"),
        revision="embed-rev-1",
        dimension=4,
        normalization="L2",
        index_generation="index-gen-7",
    )
    assert [item.state for item in embeddings] == ["SUCCEEDED", "FAILED", "SUCCEEDED"]
    assert embeddings[0].revision == "embed-rev-1"
    assert embeddings[0].dimension == 4
    assert embeddings[0].normalization == "L2"
    assert embeddings[0].index_generation == "index-gen-7"
    assert len(embeddings[0].vector) == 4
    assert embeddings[1].failure_reason == "empty_text"

    reranked = gateway.rerank((("doc-b", 0.2), ("doc-a", 0.9)))
    assert [(item.item_id, item.score, item.rank) for item in reranked] == [("doc-a", 0.9, 1), ("doc-b", 0.2, 2)]

    region = gateway.analyze_vision(
        source_lineage_ref="source:pdf:1",
        page_number=3,
        bbox=(1.0, 2.0, 30.0, 40.0),
        text="OCR text",
    )
    assert region.page_number == 3
    assert region.bbox == (1.0, 2.0, 30.0, 40.0)
    assert region.source_lineage_ref == "source:pdf:1"

    segments = gateway.transcribe(((0, 1200, "hello", True), (1200, 2400, "world", False)))
    assert [(segment.start_ms, segment.end_ms, segment.partial) for segment in segments] == [(0, 1200, True), (1200, 2400, False)]

    classification = gateway.classify(
        label_scores={"approve": 0.61, "deny": 0.39},
        threshold=0.7,
        calibration_ref="calibration:v1",
    )
    assert classification.label is None
    assert classification.abstained is True
    assert classification.threshold == 0.7
    assert classification.calibration_ref == "calibration:v1"

    judge = gateway.judge(
        ModelGatewayRequest(
            category=ModelCategory.EVAL_JUDGE,
            prompt="Judge the answer.",
            provider_id="judge",
        ),
        score=0.82,
        rationale="grounded enough",
    )
    assert judge.gateway_audited is True
    assert judge.budget_verdict.allowed is True
    assert judge.sole_quality_proof_allowed is False
    assert judge.requires_external_evidence is True


def test_model_gateway_compression_and_domain_outputs_are_candidates_or_proposals() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])

    compressed = gateway.compress_context(
        source_text="Important renewal constraints conflict with outdated pricing.",
        lineage_refs=("ctx:event:1", "ctx:evidence:2"),
        constraints=("preserve renewal date",),
        conflict_refs=("conflict:pricing",),
        distortion_risks=("pricing may be stale",),
    )
    assert compressed.lineage_refs == ("ctx:event:1", "ctx:evidence:2")
    assert compressed.preserved_constraints == ("preserve renewal date",)
    assert compressed.conflict_refs == ("conflict:pricing",)
    assert compressed.distortion_risks == ("pricing may be stale",)

    memory = gateway.memory_candidate(
        payload={"fact": "Supplier renewal date is July 18."},
        source_model_call_ref="model_call_memory",
    )
    assert memory.target_owner == "MEMORY"
    assert memory.requires_owner_review is True
    assert memory.directly_committable is False

    risk = gateway.security_risk_proposal(
        risk_level="HIGH",
        evidence_refs=("ev:secret",),
        source_model_call_ref="model_call_security",
    )
    assert risk.target_owner == "SECURITY"
    assert risk.requires_owner_review is True
    assert risk.directly_enforced is False

    action = gateway.tool_action_proposal(
        action_name="send_email",
        args={"to": "team@example.com", "body": "Draft"},
        source_model_call_ref="model_call_tool",
    )
    assert action.target_owner == "AGENT_CORE"
    assert action.requires_owner_binding is True
    assert action.directly_executable is False


def test_model_gateway_usage_pricing_and_quota_boundaries() -> None:
    primary = MockModelProvider(provider_id="primary", model_id="mock-primary", fail_mode="timeout")
    fallback = MockModelProvider(provider_id="fallback", model_id="mock-fallback")
    gateway = ModelGateway(providers=[primary, fallback])

    result = gateway.invoke(
        ModelGatewayRequest(
            category="chat",
            prompt="Fallback usage accounting.",
            provider_id="primary",
            fallback_provider_ids=["fallback"],
            pricing_version="pricing:v1",
        )
    )

    assert result.status == "succeeded"
    assert [receipt.kind for receipt in result.usage_receipts] == [
        ModelUsageKind.ESTIMATE,
        ModelUsageKind.OBSERVED,
        ModelUsageKind.OBSERVED,
    ]
    assert result.attempts[0].usage_receipt_id == result.usage_receipts[1].usage_receipt_id
    assert result.attempts[1].usage_receipt_id == result.usage_receipts[2].usage_receipt_id

    observed = result.usage_receipts[-1]
    settled = gateway.settle_usage(observed)
    correction = gateway.correct_usage(observed, prompt_tokens=7, completion_tokens=11)

    assert [receipt.kind for receipt in [observed, settled, correction]] == [
        ModelUsageKind.OBSERVED,
        ModelUsageKind.SETTLED,
        ModelUsageKind.CORRECTION,
    ]
    assert observed.pricing_version == settled.pricing_version == correction.pricing_version == "pricing:v1"
    assert observed.usage_receipt_id != settled.usage_receipt_id
    assert observed.usage_receipt_id != correction.usage_receipt_id

    quota = ModelQuotaPolicy(quota_scope="tenant:t1:model", token_limit=10, reserved_tokens=0, generation=0)
    first = gateway.reserve_quota(policy=quota, requested_tokens=6, expected_generation=0)
    stale = gateway.reserve_quota(policy=quota, requested_tokens=6, expected_generation=0)
    second = gateway.reserve_quota(policy=quota, requested_tokens=3, expected_generation=1)
    exhausted = gateway.reserve_quota(policy=quota, requested_tokens=2, expected_generation=2)

    assert first.accepted is True and first.committed_generation == 1
    assert stale.accepted is False and stale.reason == "generation_mismatch"
    assert second.accepted is True and second.committed_generation == 2
    assert exhausted.accepted is False and exhausted.reason == "quota_exhausted"


def test_model_gateway_health_circuit_capability_and_conformance_boundaries() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])

    unknown_health = gateway.evaluate_provider_health(
        provider_id="primary",
        model_id="mock-chat",
        region="us-east-1",
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        window_started_at=1.0,
        window_ended_at=2.0,
        success_count=0,
        failure_count=0,
        evidence_ref=None,
    )
    healthy = gateway.evaluate_provider_health(
        provider_id="primary",
        model_id="mock-chat",
        region="us-east-1",
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        window_started_at=1.0,
        window_ended_at=2.0,
        success_count=9,
        failure_count=1,
        evidence_ref="ev:health-window:1",
    )
    unhealthy_other_region = gateway.evaluate_provider_health(
        provider_id="primary",
        model_id="mock-chat",
        region="eu-west-1",
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        window_started_at=1.0,
        window_ended_at=2.0,
        success_count=1,
        failure_count=9,
        evidence_ref="ev:health-window:2",
    )

    assert unknown_health.status == ModelProviderHealthStatus.UNKNOWN
    assert unknown_health.is_healthy is False
    assert healthy.status == ModelProviderHealthStatus.HEALTHY
    assert healthy.is_healthy is True

    healthy_circuit = gateway.evaluate_circuit(healthy)
    unhealthy_region_circuit = gateway.evaluate_circuit(unhealthy_other_region)
    unknown_circuit = gateway.evaluate_circuit(unknown_health)

    assert healthy_circuit.status == ModelCircuitStatus.CLOSED
    assert unhealthy_region_circuit.status == ModelCircuitStatus.OPEN
    assert unknown_circuit.status == ModelCircuitStatus.OPEN
    assert healthy_circuit.key.isolation_key != unhealthy_region_circuit.key.isolation_key

    degraded = gateway.capability_profile(
        capability_id="cap:generate",
        provider_id="primary",
        model_id="mock-chat",
        operation=ModelOperation.GENERATE,
        status=ModelCapabilityStatus.DEGRADED,
        evidence_ref="ev:capability:degraded",
    )
    stale = gateway.capability_profile(
        capability_id="cap:generate",
        provider_id="primary",
        model_id="mock-chat",
        operation=ModelOperation.GENERATE,
        status=ModelCapabilityStatus.STALE,
        evidence_ref="ev:capability:stale",
    )
    revoked = gateway.capability_profile(
        capability_id="cap:generate",
        provider_id="primary",
        model_id="mock-chat",
        operation=ModelOperation.GENERATE,
        status=ModelCapabilityStatus.REVOKED,
        evidence_ref="ev:capability:revoked",
    )

    assert degraded.dispatch_allowed is True and degraded.requires_operator_review is True
    assert stale.dispatch_allowed is True and stale.requires_operator_review is True
    assert revoked.dispatch_allowed is False and revoked.requires_operator_review is True

    generate_suite = gateway.adapter_conformance_suite(
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v1",
        model_mapping_version="mapping:v1",
        evidence_ref="ev:conformance:generate:v1",
        passed=True,
    )
    embed_suite = gateway.adapter_conformance_suite(
        operation=ModelOperation.EMBED,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v1",
        model_mapping_version="mapping:v1",
        evidence_ref="ev:conformance:embed:v1",
        passed=True,
    )

    assert generate_suite.suite_id != embed_suite.suite_id
    assert generate_suite.conformance_hash != embed_suite.conformance_hash
    assert gateway.validate_adapter_conformance(
        generate_suite,
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v1",
        model_mapping_version="mapping:v1",
    ).valid is True
    assert gateway.validate_adapter_conformance(
        generate_suite,
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v2",
        model_mapping_version="mapping:v1",
    ).requires_revalidation is True
    assert gateway.validate_adapter_conformance(
        generate_suite,
        operation=ModelOperation.GENERATE,
        adapter_version="adapter:v1",
        sdk_api_version="sdk:v1",
        model_mapping_version="mapping:v2",
    ).requires_revalidation is True


def test_model_gateway_provider_signal_config_and_lifecycle_boundaries() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])

    unknown_signal = gateway.interpret_provider_signal(
        signal_kind="event",
        raw_value="provider_future_success",
        known_values=("provider_success", "provider_failure"),
    )
    known_signal = gateway.interpret_provider_signal(
        signal_kind="event",
        raw_value="provider_success",
        known_values=("provider_success", "provider_failure"),
    )
    assert unknown_signal.status == ModelProviderSignalStatus.UNKNOWN_FAIL_CLOSED
    assert unknown_signal.success is False
    assert known_signal.status == ModelProviderSignalStatus.ACCEPTED
    assert known_signal.success is True

    snapshot_a = gateway.create_config_snapshot(
        config_version="config:v1",
        generation=7,
        payload={"routing": {"planner": "primary"}, "limits": {"max_tokens": 128}},
    )
    snapshot_b = gateway.create_config_snapshot(
        config_version="config:v1",
        generation=7,
        payload={"limits": {"max_tokens": 128}, "routing": {"planner": "primary"}},
    )
    changed_snapshot = gateway.create_config_snapshot(
        config_version="config:v1",
        generation=8,
        payload={"routing": {"planner": "fallback"}, "limits": {"max_tokens": 128}},
    )

    assert snapshot_a.content_sha256 == snapshot_b.content_sha256
    assert snapshot_a.snapshot_id == snapshot_b.snapshot_id
    assert snapshot_a.snapshot_id != changed_snapshot.snapshot_id

    rejected_activation = gateway.activate_config_snapshot(
        snapshot_a,
        expected_generation=6,
        active_generation=7,
        validation_passed=True,
        replay_passed=True,
        canary_passed=True,
        rollback_snapshot_ref="config_snapshot_previous",
    )
    accepted_activation = gateway.activate_config_snapshot(
        snapshot_a,
        expected_generation=7,
        active_generation=7,
        validation_passed=True,
        replay_passed=True,
        canary_passed=True,
        rollback_snapshot_ref="config_snapshot_previous",
    )

    assert rejected_activation.accepted is False
    assert rejected_activation.reason == "generation_mismatch"
    assert accepted_activation.accepted is True
    assert accepted_activation.completed_gates == (
        ModelConfigActivationGate.VALIDATION,
        ModelConfigActivationGate.REPLAY,
        ModelConfigActivationGate.CANARY,
        ModelConfigActivationGate.CAS,
        ModelConfigActivationGate.ROLLBACK,
    )

    call_binding = gateway.bind_call_config_snapshot(call_id="model_call_1", snapshot=snapshot_a)
    assert call_binding.config_snapshot_id == snapshot_a.snapshot_id
    assert call_binding.config_hash == snapshot_a.content_sha256
    assert call_binding.immutable is True

    states = {
        state: gateway.provider_lifecycle_record(
            provider_id="primary",
            model_id="mock-chat",
            state=state,
            generation=index,
            evidence_ref=f"ev:lifecycle:{state.value.lower()}",
        )
        for index, state in enumerate(ModelProviderLifecycleState, start=1)
    }
    assert states[ModelProviderLifecycleState.PROBE].accepts_new_dispatch is False
    assert states[ModelProviderLifecycleState.ENABLED].accepts_new_dispatch is True
    assert states[ModelProviderLifecycleState.DEPRECATED].accepts_new_dispatch is True
    assert states[ModelProviderLifecycleState.DRAINING].accepts_new_dispatch is False
    assert states[ModelProviderLifecycleState.DISABLED].accepts_new_dispatch is False
    assert states[ModelProviderLifecycleState.RETIRED].accepts_new_dispatch is False
    assert all(record.preserves_history for record in states.values())

    emergency = gateway.emergency_disable_provider(
        provider_id="primary",
        model_id="mock-chat",
        generation=9,
        reason="provider_key_leak",
    )
    retired = states[ModelProviderLifecycleState.RETIRED]
    assert emergency.blocks_new_dispatch is True
    assert emergency.late_results_isolated is True
    assert emergency.quarantine_ref.startswith("provider_disable_quarantine_")
    assert retired.preserves_history is True


def test_model_gateway_admission_queue_and_overload_boundaries() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])
    capacity = {
        "global": 10,
        "provider:primary": 10,
        "model:primary:mock-chat": 10,
        "operation:generate": 10,
        "role:executor": 10,
    }

    admitted = gateway.evaluate_admission(
        tenant_id="tenant-a",
        role=ModelRole.EXECUTOR,
        provider_id="primary",
        model_id="mock-chat",
        operation=ModelOperation.GENERATE,
        requested_units=2,
        capacity_by_key=capacity,
        tenant_inflight=1,
        tenant_fairness_limit=3,
        reserved_capacity_units=0,
        waiting_age_ms=10,
        starvation_threshold_ms=1000,
    )
    fair_limited = gateway.evaluate_admission(
        tenant_id="tenant-a",
        role=ModelRole.EXECUTOR,
        provider_id="primary",
        model_id="mock-chat",
        operation=ModelOperation.GENERATE,
        requested_units=2,
        capacity_by_key=capacity,
        tenant_inflight=3,
        tenant_fairness_limit=3,
        reserved_capacity_units=0,
        waiting_age_ms=10,
        starvation_threshold_ms=1000,
    )
    reserved = gateway.evaluate_admission(
        tenant_id="tenant-a",
        role=ModelRole.EXECUTOR,
        provider_id="primary",
        model_id="mock-chat",
        operation=ModelOperation.GENERATE,
        requested_units=2,
        capacity_by_key=capacity,
        tenant_inflight=3,
        tenant_fairness_limit=3,
        reserved_capacity_units=2,
        waiting_age_ms=10,
        starvation_threshold_ms=1000,
    )
    anti_starvation = gateway.evaluate_admission(
        tenant_id="tenant-b",
        role=ModelRole.EXECUTOR,
        provider_id="primary",
        model_id="mock-chat",
        operation=ModelOperation.GENERATE,
        requested_units=2,
        capacity_by_key=capacity,
        tenant_inflight=3,
        tenant_fairness_limit=3,
        reserved_capacity_units=0,
        waiting_age_ms=1500,
        starvation_threshold_ms=1000,
    )

    assert admitted.accepted is True
    assert [check.layer for check in admitted.layer_checks] == [
        ModelAdmissionLayer.GLOBAL,
        ModelAdmissionLayer.PROVIDER,
        ModelAdmissionLayer.MODEL,
        ModelAdmissionLayer.OPERATION,
        ModelAdmissionLayer.ROLE,
    ]
    assert fair_limited.accepted is False and fair_limited.fairness_limited is True
    assert reserved.accepted is True and reserved.reserved_capacity_used == 2
    assert anti_starvation.accepted is True and anti_starvation.starvation_prevention_applied is True

    snapshot = gateway.create_config_snapshot(
        config_version="config:v2",
        generation=1,
        payload={"routing": {"executor": "primary"}},
    )
    config_binding = gateway.bind_call_config_snapshot(call_id="model_call_queued", snapshot=snapshot)
    queued = gateway.queue_request_binding(
        call_id="model_call_queued",
        deadline_at=1234.5,
        security_epoch_ref="security:tenant:2",
        budget_verdict=BudgetVerdict(allowed=True, reason="within_budget", estimated_cost=0.01),
        config_binding=config_binding,
    )

    assert queued.deadline_at == 1234.5
    assert queued.security_epoch_ref == "security:tenant:2"
    assert queued.budget_verdict.allowed is True
    assert queued.config_binding.config_snapshot_id == snapshot.snapshot_id

    normal = gateway.evaluate_overload(current_load_units=5, capacity_units=10)
    backpressure = gateway.evaluate_overload(current_load_units=15, capacity_units=10)
    shedding = gateway.evaluate_overload(current_load_units=25, capacity_units=10)
    required = ("security", "validation", "usage", "audit", "budget")

    assert normal.state == ModelOverloadState.NORMAL
    assert backpressure.state == ModelOverloadState.BACKPRESSURE and backpressure.backpressure is True
    assert shedding.state == ModelOverloadState.LOAD_SHEDDING and shedding.load_shedding is True
    assert shedding.preserved_gates == required
    assert shedding.bypass_allowed is False


def test_model_gateway_cache_boundaries() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])
    prompt_policy = gateway.cache_policy(
        cache_kind=ModelCacheKind.PROVIDER_PROMPT,
        tenant_id="tenant-a",
        config_version="config:v1",
        schema_version="schema:v1",
        model_version="model:v1",
        adapter_version="adapter:v1",
        security_epoch_ref="security:v1",
        enabled=True,
    )
    metadata_policy = gateway.cache_policy(
        cache_kind=ModelCacheKind.METADATA,
        tenant_id="tenant-a",
        config_version="config:v1",
        schema_version="schema:v1",
        model_version="model:v1",
        adapter_version="adapter:v1",
        security_epoch_ref="security:v1",
        enabled=True,
    )
    result_policy_default = gateway.cache_policy(
        cache_kind=ModelCacheKind.RESULT,
        tenant_id="tenant-a",
        config_version="config:v1",
        schema_version="schema:v1",
        model_version="model:v1",
        adapter_version="adapter:v1",
        security_epoch_ref="security:v1",
    )
    result_policy_enabled = gateway.cache_policy(
        cache_kind=ModelCacheKind.RESULT,
        tenant_id="tenant-a",
        config_version="config:v1",
        schema_version="schema:v1",
        model_version="model:v1",
        adapter_version="adapter:v1",
        security_epoch_ref="security:v1",
        enabled=True,
    )

    prompt_key = gateway.cache_key(policy=prompt_policy, prompt_hash="prompt-hash")
    metadata_key = gateway.cache_key(policy=metadata_policy, prompt_hash="prompt-hash")
    result_key = gateway.cache_key(policy=result_policy_enabled, prompt_hash="prompt-hash")
    other_tenant_key = gateway.cache_key(
        policy=gateway.cache_policy(
            cache_kind=ModelCacheKind.RESULT,
            tenant_id="tenant-b",
            config_version="config:v1",
            schema_version="schema:v1",
            model_version="model:v1",
            adapter_version="adapter:v1",
            security_epoch_ref="security:v1",
            enabled=True,
        ),
        prompt_hash="prompt-hash",
    )
    other_version_key = gateway.cache_key(
        policy=gateway.cache_policy(
            cache_kind=ModelCacheKind.RESULT,
            tenant_id="tenant-a",
            config_version="config:v2",
            schema_version="schema:v1",
            model_version="model:v1",
            adapter_version="adapter:v1",
            security_epoch_ref="security:v1",
            enabled=True,
        ),
        prompt_hash="prompt-hash",
    )

    assert len({prompt_key.cache_key, metadata_key.cache_key, result_key.cache_key}) == 3
    assert result_policy_default.enabled is False
    assert result_key.cache_key != other_tenant_key.cache_key
    assert result_key.cache_key != other_version_key.cache_key

    disabled_lookup = gateway.lookup_cache(
        policy=result_policy_default,
        key=result_key,
        stored_result_ref="result:1",
    )
    hit = gateway.lookup_cache(
        policy=result_policy_enabled,
        key=result_key,
        stored_result_ref="result:1",
    )
    reuse = gateway.cache_reuse_receipt(
        lookup=hit,
        source_result_ref="result:1",
        call_id="model_call_cache_hit",
    )

    assert disabled_lookup.hit is False
    assert disabled_lookup.provider_attempt_allowed is True
    assert hit.hit is True
    assert hit.provider_attempt_allowed is False
    assert reuse.creates_provider_attempt is False
    assert reuse.source_result_ref == "result:1"

    invalidations = [
        gateway.invalidate_cache(key=result_key, reason=reason)
        for reason in ("revocation", "deletion", "model_retirement", "validity_changed")
    ]
    assert [item.invalidated for item in invalidations] == [True, True, True, True]
    assert [item.reason for item in invalidations] == [
        "revocation",
        "deletion",
        "model_retirement",
        "validity_changed",
    ]
    assert all(item.tombstone_ref.startswith("cache_tombstone_") for item in invalidations)


def test_model_gateway_operational_command_retention_and_delete_boundaries() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])

    command = gateway.operational_command(
        command_kind=ModelOperationalCommandKind.DISABLE_PROVIDER,
        command_version="opcmd:v1",
        target_ref="provider:primary",
        expected_generation=4,
        payload={"reason": "incident"},
        high_risk=True,
        authorized_by="ops-admin",
        approval_ref="approval:123",
        audit_ref="audit:456",
    )
    missing_controls = gateway.operational_command(
        command_kind=ModelOperationalCommandKind.DISABLE_PROVIDER,
        command_version="opcmd:v1",
        target_ref="provider:primary",
        expected_generation=4,
        payload={"reason": "incident"},
        high_risk=True,
    )

    accepted = gateway.evaluate_operational_command(command, active_generation=4)
    rejected = gateway.evaluate_operational_command(missing_controls, active_generation=4)
    stale = gateway.evaluate_operational_command(command, active_generation=5)

    assert command.command_id.startswith("model_op_cmd_")
    assert command.command_version == "opcmd:v1"
    assert accepted.accepted is True and accepted.committed_generation == 5
    assert rejected.accepted is False and rejected.reason == "missing_high_risk_controls"
    assert stale.accepted is False and stale.reason == "generation_mismatch"

    retention = gateway.retention_bindings(
        retention_until_by_subject={
            ModelRetentionSubject.PROMPT: 10.0,
            ModelRetentionSubject.RESPONSE: 20.0,
            ModelRetentionSubject.STREAM: 30.0,
            ModelRetentionSubject.USAGE: 40.0,
            ModelRetentionSubject.FAILURE: 50.0,
            ModelRetentionSubject.DECISION: 60.0,
        },
        policy_ref_by_subject={
            ModelRetentionSubject.PROMPT: "retention:prompt",
            ModelRetentionSubject.RESPONSE: "retention:response",
            ModelRetentionSubject.STREAM: "retention:stream",
            ModelRetentionSubject.USAGE: "retention:usage",
            ModelRetentionSubject.FAILURE: "retention:failure",
            ModelRetentionSubject.DECISION: "retention:decision",
        },
    )

    assert [item.subject for item in retention] == list(ModelRetentionSubject)
    assert len({item.retention_policy_ref for item in retention}) == len(ModelRetentionSubject)

    blocked_delete = gateway.deletion_workflow(
        object_ref="model-artifact:1",
        tombstone=True,
        visibility_revoked=False,
        physical_cleanup_requested=True,
        verification_passed=True,
    )
    completed_delete = gateway.deletion_workflow(
        object_ref="model-artifact:1",
        tombstone=True,
        visibility_revoked=True,
        physical_cleanup_requested=True,
        verification_passed=True,
    )

    assert blocked_delete.physical_cleanup_allowed is False
    assert blocked_delete.steps == (ModelDeletionStep.TOMBSTONE,)
    assert completed_delete.steps == (
        ModelDeletionStep.TOMBSTONE,
        ModelDeletionStep.VISIBILITY_REVOCATION,
        ModelDeletionStep.PHYSICAL_CLEANUP,
        ModelDeletionStep.VERIFICATION,
    )
    assert completed_delete.verified is True


def test_model_gateway_legal_hold_sli_slo_and_readiness_boundaries() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])

    legal_hold_delete = gateway.deletion_workflow(
        object_ref="model-artifact:legal",
        tombstone=True,
        visibility_revoked=True,
        physical_cleanup_requested=True,
        verification_passed=True,
        legal_hold=True,
    )
    assert legal_hold_delete.legal_hold is True
    assert legal_hold_delete.visibility_revoked is True
    assert legal_hold_delete.physical_cleanup_allowed is False
    assert legal_hold_delete.steps == (
        ModelDeletionStep.TOMBSTONE,
        ModelDeletionStep.VISIBILITY_REVOCATION,
    )

    sli = gateway.sli_slo_dimension(
        call_id="call:1",
        attempt_id="attempt:1",
        operation=ModelOperation.GENERATE,
        role=ModelRole.EXECUTOR,
        tenant_id="tenant-a",
        provider_id="primary",
        config_version="config:v1",
        slo_ref="slo:model-generate:v1",
    )
    assert (
        sli.call_id,
        sli.attempt_id,
        sli.operation,
        sli.role,
        sli.tenant_id,
        sli.provider_id,
        sli.config_version,
        sli.slo_ref,
    ) == (
        "call:1",
        "attempt:1",
        ModelOperation.GENERATE,
        ModelRole.EXECUTOR,
        "tenant-a",
        "primary",
        "config:v1",
        "slo:model-generate:v1",
    )

    missing = gateway.readiness_verdict(
        ModelReadinessProbe(
            adapter_evidence_ref="ev:adapter",
            security_evidence_ref=None,
            persistence_evidence_ref="ev:persistence",
            usage_evidence_ref="ev:usage",
            reconcile_evidence_ref="ev:reconcile",
            capacity_evidence_ref="ev:capacity",
            deletion_evidence_ref="ev:deletion",
        )
    )
    mock_only = gateway.readiness_verdict(
        ModelReadinessProbe(
            adapter_evidence_ref="ev:adapter",
            security_evidence_ref="ev:security",
            persistence_evidence_ref="ev:persistence",
            usage_evidence_ref="ev:usage",
            reconcile_evidence_ref="ev:reconcile",
            capacity_evidence_ref="ev:capacity",
            deletion_evidence_ref="ev:deletion",
            mock_only=True,
        )
    )
    ready = gateway.readiness_verdict(
        ModelReadinessProbe(
            adapter_evidence_ref="ev:adapter",
            security_evidence_ref="ev:security",
            persistence_evidence_ref="ev:persistence",
            usage_evidence_ref="ev:usage",
            reconcile_evidence_ref="ev:reconcile",
            capacity_evidence_ref="ev:capacity",
            deletion_evidence_ref="ev:deletion",
        )
    )

    assert missing.status == ModelReadinessStatus.NOT_READY
    assert missing.missing_evidence == ("security",)
    assert mock_only.status == ModelReadinessStatus.NOT_READY
    assert mock_only.reason == "mock_only_not_ready"
    assert ready.status == ModelReadinessStatus.READY


def test_model_gateway_adapter_experiment_and_shadow_boundaries() -> None:
    gateway = ModelGateway(providers=[MockModelProvider(provider_id="primary", model_id="mock-chat")])

    rollout = gateway.adapter_rollout_plan(
        active_adapter_version="adapter:v1",
        candidate_adapter_version="adapter:v2",
        sdk_api_version="sdk:v2",
        rollback_adapter_version="adapter:v1",
    )
    assert rollout.modes == (
        ModelAdapterRolloutMode.PARALLEL,
        ModelAdapterRolloutMode.CANARY,
        ModelAdapterRolloutMode.DRAIN,
        ModelAdapterRolloutMode.ROLLBACK,
    )
    assert rollout.rollback_adapter_version == "adapter:v1"

    sunset = gateway.provider_api_sunset_plan(
        provider_id="primary",
        retiring_api_version="api:v1",
        replacement_api_version="api:v2",
        migration_evidence_ref="ev:migration",
        rollback_evidence_ref="ev:rollback",
        compatibility_evidence_ref="ev:compatibility",
    )
    assert sunset.migration_evidence_ref == "ev:migration"
    assert sunset.rollback_evidence_ref == "ev:rollback"
    assert sunset.compatibility_evidence_ref == "ev:compatibility"

    blocked_experiment = gateway.experiment_gate_verdict(
        experiment_id="exp:model-routing",
        security_passed=True,
        capability_passed=True,
        budget_passed=False,
        deadline_passed=True,
    )
    allowed_experiment = gateway.experiment_gate_verdict(
        experiment_id="exp:model-routing",
        security_passed=True,
        capability_passed=True,
        budget_passed=True,
        deadline_passed=True,
    )
    first_assignment = gateway.experiment_assignment(
        experiment_id="exp:model-routing",
        sticky_scope="tenant",
        subject_ref="tenant-a",
        variants=("control", "candidate"),
    )
    second_assignment = gateway.experiment_assignment(
        experiment_id="exp:model-routing",
        sticky_scope="tenant",
        subject_ref="tenant-a",
        variants=("control", "candidate"),
    )

    assert blocked_experiment.allowed is False and blocked_experiment.reason == "budget_gate_failed"
    assert allowed_experiment.allowed is True
    assert allowed_experiment.gates == ("security", "capability", "budget", "deadline")
    assert first_assignment == second_assignment
    assert first_assignment.sticky_scope == "tenant"

    shadow = gateway.shadow_call_record(
        shadow_call_id="shadow:1",
        security_ref="security:shadow",
        budget_ref="budget:shadow",
        usage_ref="usage:shadow",
        trace_ref="trace:shadow",
        retention_ref="retention:shadow",
    )
    result = gateway.shadow_result(shadow_call_id=shadow.shadow_call_id, result_ref="result:shadow")

    assert shadow.independent is True
    assert (shadow.security_ref, shadow.budget_ref, shadow.usage_ref, shadow.trace_ref, shadow.retention_ref) == (
        "security:shadow",
        "budget:shadow",
        "usage:shadow",
        "trace:shadow",
        "retention:shadow",
    )
    assert result.enters_business_output is False
