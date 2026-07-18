from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "backend"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from zuno.platform.model_gateway import (  # noqa: E402
    BudgetPolicy,
    ModelAttemptState,
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
from zuno.platform.model_roles import ModelRole  # noqa: E402


REQUIREMENTS = tuple(f"ARCH-MODEL-{index:03d}" for index in range(1, 32))


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
