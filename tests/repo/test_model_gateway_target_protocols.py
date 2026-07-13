from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_model_gateway_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/04-model-gateway.md"
MIRROR = REPO_ROOT / ".agent/modules/04-model-gateway.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_model_gateway_target_protocols", VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Model Gateway target verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_model_gateway_target_contract_is_complete() -> None:
    assert _load_verifier().verify() == []


def test_formal_and_agent_mirror_are_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()


def test_parts_are_complete_and_ordered() -> None:
    content = _content()
    parts = [
        "# Part I：问题、目标与 Ownership",
        "# Part II：概念架构与 Provider-neutral Contract",
        "# Part III：完整调用流程、Routing、Fallback 与 Escalation",
        "# Part IV：规范性状态机",
        "# Part V：Timeout、Cancellation、Usage、Quota、Health 与 Security",
        "# Part VI：Structured Output、Streaming、Failure 与 Observability",
        "# Part VII：Typed Contract、Storage、代码目录与跨模块 Proposal",
        "# Part VIII：Requirement Registry、测试与完成证据",
    ]
    positions = [content.index(part) for part in parts]
    assert positions == sorted(positions)
    assert all(content.count(part) == 1 for part in parts)


def test_role_provider_boundary_and_all_roles_are_defined() -> None:
    content = _content()
    assert "Role 与 Provider / Model 分离" in content
    for role in [
        "TASK_ANALYZER",
        "PLANNER",
        "PLAN_REPAIR",
        "EXECUTOR_FAST",
        "EXECUTOR_REASONING",
        "QUERY_REWRITER",
        "EXTRACTOR",
        "CRITIC",
        "SYNTHESIZER",
        "FINAL_CRITIC",
        "TOOL_CALL",
    ]:
        assert role in content


def test_required_contracts_and_state_machines_exist() -> None:
    content = _content()
    for term in [
        "ModelRoleDefinition",
        "ProviderDefinition",
        "ModelDefinition",
        "ModelCapabilityProfile",
        "ModelAvailabilitySnapshot",
        "ModelCallRequest",
        "ModelRoutingDecision",
        "ModelCallAttempt",
        "ModelResponse",
        "ModelStreamChunk",
        "StructuredOutputResult",
        "UsageReceipt",
        "RateLimitState",
        "QuotaReservation",
        "ProviderHealth",
        "CircuitBreakerState",
        "PromptBinding",
        "ModelFailure",
        "ModelFeasibilityAssessment",
        "## 16. ModelCallAttempt 状态机",
        "## 17. ProviderHealth 状态机",
        "## 18. CircuitBreaker 状态机",
        "## 19. QuotaReservation 状态机",
        "## 20. Streaming Session 状态机",
        "## 21. Structured Output Repair 状态机",
    ]:
        assert term in content


def test_agent_core_security_budget_and_memory_boundaries_are_explicit() -> None:
    content = _content()
    for term in [
        "Agent Core 拥有最终 `StepFeasibilityDecision`",
        "Gateway 不得激活 PlanVersion",
        "Gateway 不直接修改 AgentRun 终态",
        "Gateway 不得自行扩大 Run Budget",
        "模型输出永远是 `Proposal`、`Candidate` 或 `Model Result`",
        "不得直接批准、激活、发布或提交长期事实",
    ]:
        assert term in content


def test_storage_mapping_has_state_and_reconciliation_tables() -> None:
    content = _content()
    for table in [
        "model_role_definitions",
        "model_provider_definitions",
        "model_definitions",
        "model_capability_profiles",
        "model_routing_decisions",
        "model_call_attempts",
        "model_stream_sessions",
        "model_stream_chunks",
        "model_structured_output_results",
        "model_usage_receipts",
        "model_quota_reservations",
        "model_provider_health_snapshots",
        "model_circuit_breaker_states",
        "model_reconciliation_records",
    ]:
        assert table in content


def test_failure_matrix_covers_required_faults() -> None:
    content = _content()
    for fault in [
        "Provider Timeout",
        "Rate Limit",
        "Malformed Structured Output",
        "Stream Disconnect",
        "Usage Receipt Delayed",
        "Provider Success but Response Lost",
        "Circuit Breaker Transition",
        "Fallback Exhausted",
        "Security Revocation",
        "Quota Race",
        "Credential Rotation",
        "Provider SDK Error Mapping",
    ]:
        assert fault in content


def test_requirement_registry_is_contiguous_and_fully_mapped() -> None:
    content = _content()
    expected = list(range(1, 41))
    assert sorted(int(v) for v in re.findall(r"ARCH-MODEL-(\d{3})", content)) == expected
    assert sorted(int(v) for v in re.findall(r"RC-MODEL-(\d{3})", content)) == expected
    for requirement_id in expected:
        for suffix in ["UT", "IT", "FT", "E2E"]:
            assert content.count(f"MODEL-{requirement_id:03d}-{suffix}") == 1
        assert content.count(f"EV-MODEL-{requirement_id:03d}") == 1


def test_target_does_not_claim_implementation_or_production_readiness() -> None:
    content = _content()
    assert "status: normative-target-module-architecture" in content
    assert "所有真实模型调用已经统一进入 Gateway" not in content
    assert "status: production-ready" not in content
    assert "不得仅凭本文声明" in content
