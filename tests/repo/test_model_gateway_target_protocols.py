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


def test_unified_model_gateway_contract_is_complete() -> None:
    assert _load_verifier().verify() == []


def test_formal_and_agent_mirror_are_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()


def test_split_architecture_documents_and_validators_are_removed() -> None:
    for path in [
        REPO_ROOT / "docs/modules/04-model-gateway-contract-freeze.md",
        REPO_ROOT / ".agent/modules/04-model-gateway-contract-freeze.md",
        REPO_ROOT / "docs/modules/04-model-gateway-operations-conformance.md",
        REPO_ROOT / ".agent/modules/04-model-gateway-operations-conformance.md",
        REPO_ROOT / "tools/scripts/verify_model_gateway_contract_freeze.py",
        REPO_ROOT / "tools/scripts/verify_model_gateway_operations_conformance.py",
        REPO_ROOT / "tests/repo/test_model_gateway_contract_freeze.py",
        REPO_ROOT / "tests/repo/test_model_gateway_operations_conformance.py",
    ]:
        assert not path.exists()


def test_parts_are_complete_and_ordered() -> None:
    content = _content()
    parts = [
        "# Part I：定位、问题与跨模块模型使用地图",
        "# Part II：概念架构、Role、Operation 与配置模型",
        "# Part III：完整运行流程与 Operation 协议",
        "# Part IV：聚合、状态机与生命周期",
        "# Part V：故障、恢复、幂等、安全与事件",
        "# Part VI：多租户、缓存、运维、SLO 与兼容",
        "# Part VII：目标实现规格",
        "# Part VIII：Requirement、测试与完成证据",
    ]
    positions = [content.index(part) for part in parts]
    assert positions == sorted(positions)
    assert all(content.count(part) == 1 for part in parts)


def test_wave1_adr_and_physical_ownership_are_aligned() -> None:
    content = _content()
    for term in [
        "dependency_baseline_sha: `140128fa7352094cac5a7a58f247090d0b451753`",
        "confirmed_wave1_contract_sha: `849820d2c52d36abebee8c3d4a974bf035524e0a`",
        "docs/decisions/0003-wave1-cross-module-contract-freeze.md",
        "accepted-target",
        "CrossModuleEnvelopeV1",
        "EffectiveSecurityEpochRefV1",
        "CredentialVersionRefV1",
        "ProviderConnectionRequestV1",
        "ModelQuotaReservationV1",
        "ModelUsageReceiptV1",
        "ModelCancellationReceiptV1",
        "src/backend/zuno/platform/model_gateway/",
        "不得新增 `src/backend/zuno/model_gateway/`",
    ]:
        assert term in content


def test_all_model_roles_and_operations_are_defined() -> None:
    content = _content()
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
    for operation in [
        "TEXT_GENERATION",
        "STRUCTURED_GENERATION",
        "EMBEDDING",
        "RERANK",
        "VISION_EXTRACTION",
        "TRANSCRIPTION",
        "CLASSIFICATION",
        "JUDGE",
    ]:
        assert operation in content


def test_cross_module_model_usage_map_is_explicit() -> None:
    content = _content()
    for term in [
        "十一个模块的模型使用地图",
        "VLM / 多模态模型 OCR",
        "Chunk/Query Embedding",
        "Context Compression",
        "Memory Extraction",
        "Prompt Injection",
        "Judge 调用也必须经过 Gateway",
        "Shadow Result 永远不能进入业务输出",
    ]:
        assert term in content


def test_required_contracts_and_state_machines_exist() -> None:
    content = _content()
    for term in [
        "ModelRoleDefinition",
        "ModelOperationKind",
        "ProviderAdapterContract",
        "ProviderAdapterResult",
        "ModelGatewayConfigSnapshot",
        "ModelCallRequest",
        "ModelRoutingDecision",
        "ModelCallAttempt",
        "ModelResponseSelection",
        "StructuredOutputResult",
        "EmbeddingResult",
        "RerankResult",
        "VisionExtractionResult",
        "JudgeResult",
        "AdapterConformanceProfile",
        "TenantAdmissionPolicy",
        "GatewayResultCachePolicy",
        "ModelGatewayOperationalCommand",
        "ModelDataRetentionBinding",
        "GatewayReadinessSnapshot",
        "ModelGatewayCompatibilityEntry",
        "ModelRoutingExperimentAssignment",
        "# 29. ModelCallAttempt 状态机",
        "# 36. Adapter Conformance 生命周期",
        "# 37. Config Activation 状态机",
        "# 39. Admission Queue 状态机",
        "# 40. Overload 状态机",
        "# 41. Result Cache 状态机",
        "# 42. Deletion 状态机",
    ]:
        assert term in content


def test_agent_core_security_memory_knowledge_and_tool_boundaries_are_explicit() -> None:
    content = _content()
    for term in [
        "Agent Core 拥有最终 `StepFeasibilityDecision`",
        "Gateway 不得激活 PlanVersion",
        "Gateway 不直接修改 AgentRun 终态",
        "不得自行扩大 Run Budget",
        "模型输出永远是 `Proposal`、`Candidate`、`Score` 或 `Model Result`",
        "模型不能直接写长期 Memory",
        "最终 Security Decision 必须由 Security 模块",
        "Gateway 不执行外部副作用",
    ]:
        assert term in content


def test_storage_mapping_covers_runtime_operations_and_governance() -> None:
    content = _content()
    for table in [
        "model_role_definitions",
        "model_operation_definitions",
        "model_gateway_config_snapshots",
        "model_adapter_conformance_profiles",
        "model_calls",
        "model_routing_decisions",
        "model_call_attempts",
        "model_response_selections",
        "model_embedding_batches",
        "model_rerank_batches",
        "model_vision_results",
        "model_stream_sessions",
        "model_usage_receipts",
        "model_quota_reservations",
        "model_admission_queue_items",
        "model_provider_health_snapshots",
        "model_circuit_breaker_states",
        "model_reconciliation_records",
        "model_result_validity_records",
        "model_cache_reuse_receipts",
        "model_operational_commands",
        "model_data_deletion_records",
        "model_readiness_snapshots",
        "model_routing_experiment_assignments",
    ]:
        assert table in content


def test_failure_matrix_covers_execution_operations_and_lifecycle() -> None:
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
        "Config Activation Failure",
        "Cache Isolation Mismatch",
        "Deletion Partial Failure",
        "Judge Unavailable",
        "Overload",
    ]:
        assert fault in content


def test_requirement_registry_is_contiguous_and_fully_mapped() -> None:
    content = _content()
    expected = list(range(1, 89))
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
    assert "Mock-only、单次成功调用或文档完成不能证明生产 Readiness" in content
