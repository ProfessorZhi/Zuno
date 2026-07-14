from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_security_target_protocols.py"
FORMAL_PATH = REPO_ROOT / "docs/modules/09-security.md"
MIRROR_PATH = REPO_ROOT / ".agent/modules/09-security.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_security_target_protocols", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _formal() -> str:
    return FORMAL_PATH.read_text(encoding="utf-8")


def test_security_architecture_verifier_passes() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_formal_document_and_agent_mirror_are_byte_identical() -> None:
    assert FORMAL_PATH.read_bytes() == MIRROR_PATH.read_bytes()


def test_single_security_target_document_boundary_is_explicit() -> None:
    content = _formal()
    assert "唯一的正式 Target 架构主设计" in content
    assert "09-security-agentic-security-addendum" not in content


def test_agent_task_session_authorization_is_intersection_based() -> None:
    content = _formal()
    for term in [
        "AgentPrincipal",
        "TaskPrincipal",
        "SessionPrincipal",
        "TaskAuthorizationGrant",
        "用户、Agent、Task、Session 与 Run 权限取交集，不取并集",
    ]:
        assert term in content


def test_three_level_ui_permission_maps_to_fine_grained_actions() -> None:
    content = _formal()
    for term in ["DENY", "USE_ONLY", "USE_AND_DELEGATE", "ActionSet"]:
        assert term in content
    assert "三档 UI 权限必须映射到版本化 ActionSet" in content


def test_policy_plane_has_pap_pdp_pep_pip_and_simulation() -> None:
    content = _formal()
    for term in [
        "PAP — Policy Administration Point",
        "PDP — Policy Decision Point",
        "PEP — Policy Enforcement Point",
        "PIP — Policy Information Point",
        "PolicySimulationReport",
        "SHADOW Evaluation",
    ]:
        assert term in content


def test_agentic_information_flow_controls_are_explicit() -> None:
    content = _formal()
    for term in [
        "InstructionTrustLabel",
        "InfluenceCapability",
        "InformationFlowDecision",
        "ProtectedSinkPolicy",
        "DeclassificationDecision",
        "ActionIntentBinding",
        "不可信内容默认只能影响答案事实",
    ]:
        assert term in content


def test_mcp_credential_and_workload_identity_boundaries_are_explicit() -> None:
    content = _formal()
    for term in [
        "WorkloadIdentity",
        "OnBehalfOfBinding",
        "禁止 Token Passthrough",
        "audience",
        "CredentialVersionRefV1",
        "SecretLeaseV1",
    ]:
        assert term in content


def test_sandbox_network_and_supply_chain_controls_are_explicit() -> None:
    content = _formal()
    for term in [
        "SandboxProfile",
        "NetworkEgressPolicy",
        "SupplyChainArtifact",
        "SupplyChainTrustDecision",
        "SSRF",
        "QUARANTINED",
    ]:
        assert term in content


def test_prepared_tool_action_and_approval_follow_adr_0003() -> None:
    content = _formal()
    for term in [
        "PreparedToolAction",
        "ActionIntentBinding",
        "prepared_action_hash",
        "effective_security_epoch_hash",
        "EffectReceipt or EffectReconciliation",
    ]:
        assert term in content
    assert "XMOD-SEC-001" not in content


def test_security_eval_includes_adaptive_attack_and_benign_utility() -> None:
    content = _formal()
    for term in [
        "Adaptive Defense-aware Attack",
        "Attack Success Rate",
        "Benign Task Success / Utility",
        "Adaptive Attack ASR",
        "Eval Utility Collapse",
    ]:
        assert term in content


def test_requirement_registry_is_complete() -> None:
    content = _formal()
    for number in range(1, 61):
        suffix = f"{number:03d}"
        assert f"ARCH-SEC-{suffix}" in content
        assert f"RC-SEC-{suffix}" in content
        assert f"SEC-{suffix}-UT/IT/FT/E2E" in content
        assert f"EV-SEC-{suffix}" in content


def test_fault_matrix_has_36_unique_cases() -> None:
    content = _formal()
    for number in range(1, 37):
        assert f"FT-SEC-{number:03d}" in content


def test_current_target_and_completion_claims_are_separated() -> None:
    content = _formal()
    for term in [
        "Current",
        "Confirmed Target",
        "Gap",
        "Future Optional",
        "History",
        "design available",
        "implementation available",
        "security quality not yet proven",
        "production ready",
    ]:
        assert term in content
