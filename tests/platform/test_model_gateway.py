from __future__ import annotations

from types import SimpleNamespace

from zuno.platform.model_gateway import (
    BudgetPolicy,
    ModelAttemptState,
    ModelCallRequest,
    ModelCallState,
    ModelCategory,
    ModelControlActionType,
    ModelDomainWrite,
    ModelGateway,
    ModelGatewayProviderError,
    ModelGatewayRequest,
    ModelOperation,
    ModelRepairRecord,
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
