from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_model_gateway_operations_conformance.py"
FORMAL = REPO_ROOT / "docs/modules/04-model-gateway-operations-conformance.md"
MIRROR = REPO_ROOT / ".agent/modules/04-model-gateway-operations-conformance.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_model_gateway_operations_conformance",
        VERIFIER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Model Gateway Operations verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_operations_verifier_passes() -> None:
    assert _load_verifier().verify() == []


def test_operations_mirror_is_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()


def test_adapter_conformance_and_config_lifecycle_are_explicit() -> None:
    content = _content()
    for term in [
        "ProviderAdapterContract",
        "AdapterConformanceProfile",
        "ModelGatewayConfigSnapshot",
        "GatewayConfigActivation",
        "CONFORMANT_WITH_LIMITATIONS",
        "Activation CAS",
    ]:
        assert term in content


def test_tenant_fairness_overload_and_queue_are_defined() -> None:
    content = _content()
    for term in [
        "TenantAdmissionPolicy",
        "AdmissionQueueItem",
        "LoadSheddingDecision",
        "noisy neighbor",
        "age boost",
        "REJECT_OVERLOADED",
    ]:
        assert term in content


def test_cache_operations_and_retention_boundaries_are_defined() -> None:
    content = _content()
    for term in [
        "Provider-managed Prompt Cache",
        "Gateway Result Cache",
        "跨租户 cache sharing 默认禁止",
        "ModelGatewayOperationalCommand",
        "ModelDataRetentionBinding",
        "ModelDataDeletionRecord",
        "BLOCKED_BY_HOLD",
    ]:
        assert term in content


def test_readiness_compatibility_and_eval_governance_are_defined() -> None:
    content = _content()
    for term in [
        "ModelGatewayServiceLevelProfile",
        "GatewayReadinessSnapshot",
        "无证据不得默认 READY",
        "ModelGatewayCompatibilityEntry",
        "Judge 调用仍走 Model Gateway",
        "模型 A 判断模型 A 很好",
        "ModelRoutingExperimentAssignment",
    ]:
        assert term in content


def test_operations_storage_mapping_is_complete() -> None:
    content = _content()
    for table in [
        "model_provider_adapters",
        "model_adapter_conformance_profiles",
        "model_gateway_config_snapshots",
        "model_gateway_config_activations",
        "model_lifecycle_records",
        "model_tenant_admission_policies",
        "model_admission_queue_items",
        "model_operational_commands",
        "model_data_retention_bindings",
        "model_data_deletion_records",
        "model_service_level_profiles",
        "model_readiness_snapshots",
        "model_compatibility_entries",
        "model_routing_experiment_assignments",
    ]:
        assert table in content


def test_requirement_registry_is_contiguous_and_mapped() -> None:
    content = _content()
    expected = list(range(1, 29))
    assert sorted(int(v) for v in re.findall(r"ARCH-MODEL-OPS-(\d{3})", content)) == expected
    assert sorted(int(v) for v in re.findall(r"RC-MODEL-OPS-(\d{3})", content)) == expected
    for requirement_id in expected:
        for suffix in ["UT", "IT", "FT", "E2E"]:
            assert content.count(f"MODEL-OPS-{requirement_id:03d}-{suffix}") == 1
        assert content.count(f"EV-MODEL-OPS-{requirement_id:03d}") == 1


def test_operations_addendum_contains_no_program_or_readiness_claim() -> None:
    content = _content()
    assert "不包含实施 Program" in content
    assert "status: normative-target-module-addendum" in content
    assert "status: production-ready" not in content
    assert "status: implementation_available" not in content
    assert "implementation not established" in content
