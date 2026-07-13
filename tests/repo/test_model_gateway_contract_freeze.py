from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_model_gateway_contract_freeze.py"
FORMAL = REPO_ROOT / "docs/modules/04-model-gateway-contract-freeze.md"
MIRROR = REPO_ROOT / ".agent/modules/04-model-gateway-contract-freeze.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_model_gateway_contract_freeze", VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Model Gateway Contract Freeze verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_contract_freeze_verifier_passes() -> None:
    assert _load_verifier().verify() == []


def test_contract_freeze_mirror_is_byte_identical() -> None:
    assert FORMAL.read_bytes() == MIRROR.read_bytes()


def test_role_operation_and_prompt_ownership_are_separate() -> None:
    content = _content()
    for term in [
        "ModelRoleContract",
        "ModelRoleRoutingProfile",
        "ModelOperationKind",
        "PromptExecutionBinding",
        "Role 回答“为什么调用”；Operation 回答“执行何种模型操作”",
    ]:
        assert term in content


def test_non_chat_operations_are_explicit() -> None:
    content = _content()
    for operation in [
        "EMBEDDING",
        "RERANK",
        "VISION_EXTRACTION",
        "AUDIO_TRANSCRIPTION",
        "CLASSIFICATION",
        "JUDGE",
    ]:
        assert operation in content


def test_model_call_aggregate_and_selection_are_defined() -> None:
    content = _content()
    for term in [
        "ModelCallStatus",
        "WAITING_ADMISSION",
        "WAITING_QUOTA",
        "RECONCILING",
        "EXHAUSTED",
        "ModelResponseSelectionDecision",
        "一个 `ModelCall` 最多一个 active selected response",
    ]:
        assert term in content


def test_crash_matrix_and_usage_correction_are_defined() -> None:
    content = _content()
    for term in [
        "崩溃矩阵",
        "Response 已提交，Usage 未提交",
        "Usage Event 重复交付",
        "Usage Correction",
        "RunOutcome 已完成，Usage 后到",
    ]:
        assert term in content


def test_event_streaming_routing_and_validity_protocols_are_defined() -> None:
    content = _content()
    for term in [
        "Canonical Event Catalog",
        "Provider Stream",
        "Gateway Internal Stream",
        "Product Delivery Stream",
        "decision_input_hash",
        "Capability Profile 生命周期",
        "ModelResultValidityChanged",
    ]:
        assert term in content


def test_requirement_registry_is_contiguous_and_mapped() -> None:
    content = _content()
    expected = list(range(1, 21))
    assert sorted(int(v) for v in re.findall(r"ARCH-MODEL-CF-(\d{3})", content)) == expected
    assert sorted(int(v) for v in re.findall(r"RC-MODEL-CF-(\d{3})", content)) == expected
    for requirement_id in expected:
        for suffix in ["UT", "IT", "FT", "E2E"]:
            assert content.count(f"MODEL-CF-{requirement_id:03d}-{suffix}") == 1
        assert content.count(f"EV-MODEL-CF-{requirement_id:03d}") == 1


def test_addendum_does_not_claim_implementation_or_production_readiness() -> None:
    content = _content()
    assert "status: normative-target-module-addendum" in content
    assert "status: production-ready" not in content
    assert "status: implementation_available" not in content
    assert "implementation not established" in content
