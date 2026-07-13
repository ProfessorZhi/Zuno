from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/09-security.md"
MIRROR = REPO_ROOT / ".agent/modules/09-security.md"

REQUIRED_SECTIONS = [
    "## 1. 问题、目标与非目标",
    "## 2. Current、Target、Gap、Future、History",
    "## 3. 威胁模型与信任边界",
    "## 4. Ownership 与模块边界",
    "## 6. Principal、身份与组织管理树",
    "## 7. ResourceGrant 与三档权限",
    "## 8. Policy 层级与个性化安全设置",
    "## 9. 完整运行流程",
    "## 11. 输入与输出检测",
    "## 12. DataClassification 与脱敏",
    "## 13. 知识库访问控制",
    "## 14. Tool 访问控制",
    "## 16. Approval Contract",
    "## 17. Revocation、SecurityEpoch 与 TOCTOU",
    "## 20. 全链路审计与 Trace 边界",
    "## 21. Typed Contract",
    "## 22. 状态机",
    "## 23. Failure 分类与传播",
    "## 24. Retry、Recovery、Idempotency 与 Reconcile",
    "## 25. Storage Mapping 与 Migration",
    "## 27. Fault Test Matrix",
    "## 28. Requirement Enforcement Matrix",
    "## 31. Target 转为 Current 的完成证据",
]

REQUIRED_CONTRACTS = [
    "PrincipalAccount",
    "PrincipalContext",
    "SecurityContext",
    "OrgUnit",
    "OrgMembership",
    "DelegatedAdminScope",
    "ResourceGrant",
    "GrantLineage",
    "PolicyVersion",
    "EffectiveSecurityPolicySnapshot",
    "SecurityPreference",
    "DetectionProfile",
    "DetectionFinding",
    "DataClassification",
    "RedactionProfile",
    "RedactionDecision",
    "AuthorizationRequest",
    "AuthorizationDecision",
    "SecurityGateRequest",
    "SecurityGateResult",
    "ApprovalPolicy",
    "ApprovalRequest",
    "SecurityApprovalDecision",
    "RevocationRecord",
    "SecurityEpoch",
    "SecretAccessDecision",
    "CredentialLeaseRef",
    "BreakGlassSession",
    "SecurityViolation",
    "SecurityIncident",
    "SecurityAuditRequirement",
    "SecurityOutboxEvent",
]

REQUIRED_PERMISSION_TERMS = [
    "DENY",
    "USE_ONLY",
    "USE_AND_DELEGATE",
    "显式 `DENY` 高于继承 Allow",
    "默认拒绝",
    "禁止委派放大",
    "source_grant_id",
    "delegation_depth",
    "managed_resource_types",
    "max_permission",
    "include_descendants",
    "管理员不能自我提升",
]

REQUIRED_SECURITY_GATES = [
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
    "ADMIN_GRANT",
    "BREAK_GLASS",
]

REQUIRED_STATE_MACHINES = [
    "### 22.1 PrincipalAccount",
    "### 22.2 PolicyVersion",
    "### 22.3 ResourceGrant",
    "### 22.4 DelegatedAdminScope",
    "### 22.5 ApprovalRequest",
    "### 22.6 Revocation",
    "### 22.7 BreakGlassSession",
    "### 22.8 SecurityIncident",
]

REQUIRED_FAULTS = [
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
]

CROSS_MODULE_TERMS = [
    "DEP-SEC-PS-001",
    "DEP-SEC-KNOW-001",
    "DEP-SEC-MEM-001",
    "DEP-SEC-AG-001",
    "DEP-SEC-TOOL-001",
    "DEP-SEC-MG-001",
    "DEP-SEC-OBS-001",
    "DEP-SEC-INF-001",
    "XMOD-SEC-001",
    "PreparedAction canonical hash",
]

STATUS_TERMS = [
    "design available",
    "implementation available",
    "measurement blocked",
    "quality not yet proven",
    "production ready",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    if not FORMAL.exists():
        return [f"missing formal document: {FORMAL.relative_to(REPO_ROOT)}"]
    if not MIRROR.exists():
        return [f"missing agent mirror: {MIRROR.relative_to(REPO_ROOT)}"]

    formal = _read(FORMAL)
    mirror = _read(MIRROR)
    if formal != mirror:
        errors.append("formal Security document and Agent mirror must be byte-identical")

    phrases = (
        REQUIRED_SECTIONS
        + REQUIRED_CONTRACTS
        + REQUIRED_PERMISSION_TERMS
        + REQUIRED_SECURITY_GATES
        + REQUIRED_STATE_MACHINES
        + REQUIRED_FAULTS
        + CROSS_MODULE_TERMS
        + STATUS_TERMS
    )
    for phrase in phrases:
        if phrase not in formal:
            errors.append(f"missing required Security protocol phrase: {phrase}")

    for number in range(1, 41):
        suffix = f"{number:03d}"
        for token in (
            f"ARCH-SEC-{suffix}",
            f"RC-SEC-{suffix}",
            f"SEC-{suffix}-UT/IT/FT/E2E",
            f"EV-SEC-{suffix}",
        ):
            if token not in formal:
                errors.append(f"missing Security requirement mapping token: {token}")

    requirement_ids = set(re.findall(r"ARCH-SEC-\d{3}", formal))
    if len(requirement_ids) != 40:
        errors.append(f"expected 40 unique ARCH-SEC requirements, got {len(requirement_ids)}")

    for invariant in [
        "前端不得成为 Grant 或 Approval 事实源",
        "用户的行政上级关系不自动等于资源授权",
        "下层只能收紧上层强制规则",
        "Secret 明文不得进入普通 Prompt、长期 Memory、Trace 或 Audit",
        "Mandatory Audit 无法可靠提交时，高风险副作用默认 fail closed",
        "PostgreSQL Security tables：安全领域事实",
        "LangGraph Checkpointer：Agent 图控制状态和 Interrupt 位置",
        "Redaction 失败不向外部导出",
        "接收到 `SecurityDecision` 不会把源领域对象 Ownership 转移给 Security",
    ]:
        if invariant not in formal:
            errors.append(f"missing Security ownership or safety invariant: {invariant}")

    forbidden_claims = [
        "Security is production ready",
        "full CI passed",
        "生产安全已经完成",
    ]
    for phrase in forbidden_claims:
        if phrase in formal:
            errors.append(f"forbidden unsupported Security completion claim: {phrase}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("security target protocol verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
