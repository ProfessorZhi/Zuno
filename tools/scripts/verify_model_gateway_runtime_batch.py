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
    ModelGateway,
    ModelGatewayRequest,
    ModelOperation,
    ModelUsageKind,
    MockModelProvider,
)
from zuno.platform.model_roles import ModelRole  # noqa: E402


REQUIREMENTS = tuple(f"ARCH-MODEL-{index:03d}" for index in range(1, 17)) + ("ARCH-MODEL-020",)


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
