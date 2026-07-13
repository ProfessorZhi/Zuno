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


def test_security_protocol_verifier_passes() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_formal_document_and_agent_mirror_are_byte_identical() -> None:
    assert FORMAL_PATH.read_bytes() == MIRROR_PATH.read_bytes()


def test_three_level_resource_permission_is_explicit() -> None:
    content = _formal()
    for term in ["DENY", "USE_ONLY", "USE_AND_DELEGATE", "Delegation（委派授权）"]:
        assert term in content


def test_organization_tree_and_admin_scope_are_separate_from_grants() -> None:
    content = _formal()
    for term in [
        "Primary OrgUnit Tree",
        "OrgMembership",
        "DelegatedAdminScope",
        "ResourceGrant",
        "用户的行政上级关系不自动等于资源授权",
    ]:
        assert term in content


def test_delegation_cannot_amplify_privilege() -> None:
    content = _formal()
    for term in [
        "禁止委派放大",
        "source_grant_id",
        "delegation_depth",
        "管理员不能自我提升",
        "父 Grant 被撤销",
    ]:
        assert term in content


def test_personal_security_preferences_only_tighten_mandatory_policy() -> None:
    content = _formal()
    assert "Policy 层级与个性化安全设置" in content
    assert "下层只能收紧上层强制规则" in content
    assert "用户偏好不能把组织禁止项改为允许" in content


def test_end_to_end_security_gates_are_present() -> None:
    content = _formal()
    for gate in [
        "IDENTITY",
        "INPUT",
        "RETRIEVAL",
        "MEMORY_READ",
        "MEMORY_WRITE",
        "MODEL",
        "TOOL_PREPARE",
        "TOOL_EXECUTE",
        "OUTPUT",
        "PUBLICATION",
    ]:
        assert gate in content


def test_approval_revocation_and_epoch_are_bound() -> None:
    content = _formal()
    for term in [
        "prepared_action_hash",
        "canonical_args_hash",
        "security_epoch",
        "Approval Replay",
        "execution-time epoch recheck",
    ]:
        assert term in content


def test_secret_and_redaction_fail_closed_rules_are_explicit() -> None:
    content = _formal()
    assert "Secret 明文不得进入普通 Prompt、长期 Memory、Trace 或 Audit" in content
    assert "Redaction 失败不向外部导出" in content
    assert "Secret in Trace" in content


def test_requirement_registry_is_complete() -> None:
    content = _formal()
    for number in range(1, 41):
        suffix = f"{number:03d}"
        assert f"ARCH-SEC-{suffix}" in content
        assert f"RC-SEC-{suffix}" in content
        assert f"SEC-{suffix}-UT/IT/FT/E2E" in content
        assert f"EV-SEC-{suffix}" in content


def test_fault_matrix_contains_mandatory_faults() -> None:
    content = _formal()
    for fault in [
        "Cross-tenant Retrieval",
        "Client Scope Tamper",
        "Delegation Amplification",
        "Admin Subtree Escape",
        "Grant Cascade Revocation",
        "Stale Security Epoch",
        "Approval Replay",
        "Redaction Failure",
        "Secret in Trace",
        "Policy Store Unavailable",
        "Duplicate Grant Command",
        "Concurrent Policy Activation",
        "Org Tree Cycle",
        "Break-glass Expiry",
        "Audit Outbox Failure",
        "Citation Disclosure",
    ]:
        assert fault in content


def test_current_target_and_completion_claims_are_separated() -> None:
    content = _formal()
    for term in [
        "Current",
        "Target",
        "Gap",
        "Future",
        "History",
        "design available",
        "implementation available",
        "quality not yet proven",
        "production ready",
    ]:
        assert term in content
