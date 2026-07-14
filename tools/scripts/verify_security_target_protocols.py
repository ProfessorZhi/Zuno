from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/09-security.md"
MIRROR = REPO_ROOT / ".agent/modules/09-security.md"


REQUIRED_PARTS = [
    "# Part I：定位、事实状态与威胁模型",
    "# Part II：身份、组织、授权与策略",
    "# Part III：Agent 专属结构性安全",
    "# Part IV：Tool、MCP、Credential、Sandbox 与供应链",
    "# Part V：Gate 与完整运行流程",
    "# Part VI：Contract、状态、故障与持久化",
    "# Part VII：跨模块请求",
    "# Part VIII：测试、评测、Requirement 与完成证据",
]

REQUIRED_SECTIONS = [
    "## 0. 文档边界与规范层级",
    "# 2. Current、Target、Gap、Future 与 History",
    "# 4. 威胁模型",
    "# 5. Security Ownership",
    "# 6. 强制安全不变量",
    "# 7. Principal 模型",
    "# 10. 资源模型、动作模型与三档 UI 权限",
    "# 12. Agent、Task、Session 与用户权限交集",
    "# 13. Policy 架构：PAP、PDP、PEP、PIP",
    "# 17. Instruction Trust 模型",
    "# 18. Information Flow、Taint 与 Capability",
    "# 19. Protected Sink 与 Declassification",
    "# 20. ActionIntentBinding",
    "# 21. Prompt Injection 与 Memory Poisoning 防御",
    "# 29. PreparedToolAction 与 Approval",
    "# 30. MCP、OAuth 与 Token 安全",
    "# 32. SandboxProfile",
    "# 34. Supply Chain Trust",
    "# 36. Security Gate Catalog",
    "# 46. CrossModuleEnvelope",
    "# 48. 状态机",
    "# 49. Failure 分类与传播",
    "# 50. Retry、Recovery、Idempotency 与 Reconcile",
    "# 52. Storage Mapping 与 Migration",
    "# 60. Fault Test Matrix",
    "# 61. Security Eval 与 Release Gate",
    "# 62. Requirement Enforcement Matrix",
    "# 63. Target 转为 Current 的完成证据",
    "# 64. 研究与成熟工程参考",
]

REQUIRED_CONTRACTS = [
    "PrincipalAccount",
    "PrincipalContext",
    "SecurityContext",
    "AgentPrincipal",
    "TaskPrincipal",
    "SessionPrincipal",
    "WorkloadIdentity",
    "OnBehalfOfBinding",
    "OrgUnit",
    "OrgMembership",
    "DelegatedAdminScope",
    "ResourceRef",
    "ActionSet",
    "ResourceGrant",
    "GrantLineage",
    "TaskAuthorizationGrant",
    "PolicySchemaRef",
    "PolicyVersion",
    "PolicyValidationReport",
    "PolicySimulationReport",
    "EffectiveSecurityPolicySnapshot",
    "AuthorizationRequest",
    "AuthorizationDecision",
    "DecisionExplanation",
    "InstructionTrustLabel",
    "InfluenceCapability",
    "InformationFlowDecision",
    "ProtectedSinkPolicy",
    "DeclassificationDecision",
    "ActionIntentBinding",
    "DetectionProfile",
    "DetectionFinding",
    "DataClassification",
    "RedactionProfile",
    "RedactionDecision",
    "ModelSecurityDecision",
    "ActionAuthorizationDecision",
    "SecurityApprovalDecision",
    "EffectiveSecurityEpochRefV1",
    "CredentialVersionRefV1",
    "SecretLeaseV1",
    "SandboxProfile",
    "NetworkEgressPolicy",
    "SupplyChainArtifact",
    "SupplyChainTrustDecision",
    "SecurityAuditRequirementV1",
    "SecurityEvalProfile",
    "SecurityEvalRun",
    "SecurityReleaseGateEvaluation",
]

REQUIRED_INVARIANTS = [
    "前端不得成为 Grant 或 Approval 事实源",
    "用户的行政上级关系不自动等于资源授权",
    "用户、Agent、Task、Session 与 Run 权限取交集，不取并集",
    "三档 UI 权限必须映射到版本化 ActionSet",
    "不可信内容默认只能影响答案事实",
    "Protected Sink 只能接受满足 Information Flow Policy 的值",
    "Token 必须验证 issuer、audience、authorized party、subject、purpose、scope 和 expiry",
    "禁止 Token Passthrough",
    "Mandatory Audit 无法可靠提交时，高风险副作用 fail closed",
    "Tool Effect 未知时进入 Reconcile，禁止盲目 Retry",
    "PostgreSQL 保存安全领域事实；LangGraph Checkpointer 只保存图控制状态和事实引用",
    "接收到 `SecurityDecision` 不会把源领域对象 Ownership 转移给 Security",
    "Redaction 失败不向外部导出",
    "安全 Release Gate 必须同时评估攻击成功率和正常任务效用",
]

REQUIRED_GATES = [
    "IDENTITY",
    "INPUT",
    "CONTEXT_BUILD",
    "RETRIEVAL",
    "MEMORY_READ",
    "MEMORY_WRITE",
    "MODEL",
    "INFORMATION_FLOW",
    "ACTION_INTENT",
    "TOOL_PREPARE",
    "TOOL_EXECUTE",
    "OUTPUT",
    "CITATION",
    "ARTIFACT",
    "PUBLICATION",
    "ADMIN_GRANT",
    "POLICY_ACTIVATION",
    "CREDENTIAL",
    "SUPPLY_CHAIN",
    "BREAK_GLASS",
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
    "Instruction Trust Escalation",
    "Tool Output Injection",
    "Memory Poisoning",
    "Action Intent Unbound",
    "Protected Sink Violation",
    "Token Audience Mismatch",
    "Token Passthrough",
    "SSRF Redirect",
    "Sandbox Requirement Missing",
    "Supply Chain Digest Change",
    "Adaptive Prompt Injection",
    "Multimodal Hidden Instruction",
    "Credential Lease Wrong Task",
    "Effect Unknown",
    "Eval Utility Collapse",
]

FORBIDDEN_STALE_TEXT = [
    "并行 Wave 1 的 04 Model Gateway",
    "XMOD-SEC-001",
    "PreparedAction 冲突请求",
    "Draft PR",
]

FORBIDDEN_CLAIMS = [
    "Security is production ready",
    "full CI passed",
    "生产安全已经完成",
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

    for phrase in (
        REQUIRED_PARTS
        + REQUIRED_SECTIONS
        + REQUIRED_CONTRACTS
        + REQUIRED_INVARIANTS
        + REQUIRED_GATES
        + REQUIRED_FAULTS
    ):
        if phrase not in formal:
            errors.append(f"missing required Security architecture phrase: {phrase}")

    for number in range(1, 61):
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
    if len(requirement_ids) != 60:
        errors.append(f"expected 60 unique ARCH-SEC requirements, got {len(requirement_ids)}")

    fault_ids = set(re.findall(r"FT-SEC-\d{3}", formal))
    if len(fault_ids) != 36:
        errors.append(f"expected 36 unique FT-SEC faults, got {len(fault_ids)}")

    for phrase in FORBIDDEN_STALE_TEXT:
        if phrase in formal:
            errors.append(f"stale Security architecture text must be removed: {phrase}")

    for phrase in FORBIDDEN_CLAIMS:
        if phrase in formal:
            errors.append(f"forbidden unsupported Security completion claim: {phrase}")

    if "status: normative-target-module-architecture" not in formal:
        errors.append("Security document must declare normative-target-module-architecture")

    if "唯一的正式 Target 架构主设计" not in formal:
        errors.append("Security document must declare itself the single target architecture document")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("security target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
