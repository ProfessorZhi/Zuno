from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_capability_skill_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/07-capability-skill.md"
MIRROR = REPO_ROOT / ".agent/modules/07-capability-skill.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_capability_skill_target_protocols",
        VERIFIER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Capability / Skill target verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_capability_skill_target_contract() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_capability_skill_mirror_is_byte_identical() -> None:
    assert MIRROR.read_bytes() == FORMAL.read_bytes()


def test_concept_boundaries_are_explicit() -> None:
    content = _content()
    for term in [
        "Skill != Capability",
        "Capability != Tool",
        "MCP != Capability",
        "API / CLI / SDK != Capability",
        "Availability != Authorization",
        "Selection != StepFeasibility",
        "Connector Pack != Runtime Authority",
    ]:
        assert term in content


def test_cross_module_ownership_is_not_mixed() -> None:
    content = _content()
    for term in [
        "ActionProposal",
        "PreparedToolAction",
        "ToolAttempt",
        "EffectReceipt",
        "EffectReconciliation",
        "ActionAuthorizationDecision",
        "SecurityApprovalDecision",
        "IdempotencyClaim",
    ]:
        assert term in content
    assert "ToolRequest：一次工具调用意图" not in content


def test_skill_progressive_loading_and_script_boundary() -> None:
    content = _content()
    for term in [
        "METADATA_ONLY",
        "INSTRUCTION_REQUESTED",
        "RESOURCE_PLAN_CREATED",
        "SkillResourceManifest",
        "Skill Loader 只能返回 Ref",
        "CAP_SKILL_SCRIPT_RUNTIME_BYPASS",
    ]:
        assert term in content


def test_provider_binding_and_conformance_are_first_class() -> None:
    content = _content()
    for term in [
        "CapabilityProviderBinding",
        "CapabilityProviderBindingProposal",
        "ProviderConformanceRecord",
        "coverage_matrix",
        "idempotency_conformance",
        "reconciliation_conformance",
        "模型不能触发 `APPROVED` 或 `ACTIVE`",
    ]:
        assert term in content


def test_version_snapshot_and_preflight_rules_are_closed() -> None:
    content = _content()
    for term in [
        "Requirement 可以声明兼容范围；Plan 与 Action 必须固定精确版本",
        "PlanVersion 必须固定 CapabilityAvailabilitySnapshotRef",
        "每个 Action 执行前必须由 08/09/11 完成最新 Readiness Preflight",
        "ToolInventoryGeneration",
        "Active Plan 不允许静默使用新 Schema",
    ]:
        assert term in content


def test_provider_instance_credential_and_constraint_are_separated() -> None:
    content = _content()
    for term in [
        "ProviderInstance",
        "Credential Scope",
        "CapabilityConstraint",
        "07 选择业务路由；08 只在同一 Tenant/App/Identity/Effect Domain 的 Replica Pool 内负载均衡",
    ]:
        assert term in content


def test_provider_agnostic_connector_architecture_is_present() -> None:
    content = _content()
    for term in [
        'if provider == "feishu"',
        "HttpApiAdapter",
        "CliAdapter",
        "McpAdapter",
        "Connector Extension SPI",
        "Importer 只生成 Draft，不产生 ACTIVE",
        "禁止模型提交任意 Shell 字符串",
    ]:
        assert term in content


def test_domain_objects_have_storage_decisions() -> None:
    content = _content()
    for object_name, table_name in {
        "CapabilityDefinition": "capability_definitions",
        "CapabilityVersion": "capability_versions",
        "SkillDefinition": "skill_definitions",
        "SkillVersion": "skill_versions",
        "CapabilityProviderBinding": "capability_provider_bindings",
        "ProviderConformanceRecord": "provider_conformance_records",
        "CapabilityAvailabilitySnapshot": "capability_availability_snapshots",
        "CapabilitySelectionResult": "capability_selection_results",
    }.items():
        assert object_name in content
        assert table_name in content


def test_requirements_controls_tests_and_evidence_are_closed() -> None:
    content = _content()
    requirements = [int(value) for value in re.findall(r"ARCH-CAP-(\d{3})", content)]
    controls = [int(value) for value in re.findall(r"RC-CAP-(\d{3})", content)]
    assert requirements == list(range(1, 81))
    assert controls == list(range(1, 81))
    for requirement_id in range(1, 81):
        assert f"CAP-{requirement_id:03d}-UT" in content
        assert f"CAP-{requirement_id:03d}-IT" in content
        assert f"EV-CAP-{requirement_id:03d}" in content


def test_target_and_current_are_separated() -> None:
    content = _content()
    assert "唯一的正式 Target 架构主设计" in content
    assert "docs/status/production-readiness.md" in content
    assert ".agent/programs/" in content
    assert "# 当前与短期目标" not in content
    assert "PHASE07 已将" not in content
