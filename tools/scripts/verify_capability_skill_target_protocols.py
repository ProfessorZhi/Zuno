from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/07-capability-skill.md"
MIRROR = REPO_ROOT / ".agent/modules/07-capability-skill.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"

REQUIRED_PARTS = [
    "# Part I：定位、术语与概念架构",
    "# Part II：完整运行流程",
    "# Part III：状态、失败、恢复与一致性",
    "# Part IV：领域对象与 Typed Contract",
    "# Part V：Policy、版本、安全与 Provider 治理",
    "# Part VI：目标实现表面",
    "# Part VII：规范性矩阵与控制闭环",
    "# Part VIII：测试、Requirement 与完成证据",
]

REQUIRED_TERMS = [
    "唯一的正式 Target 架构主设计",
    "CapabilityDefinition",
    "CapabilityVersion",
    "CapabilityRequirement",
    "CapabilityAvailabilitySnapshot",
    "CapabilitySelectionResult",
    "SkillDefinition",
    "SkillVersion",
    "SkillMetadata",
    "SkillInstruction",
    "SkillResourceManifest",
    "ToolCapabilityDescriptor",
    "ToolDefinitionRef",
    "CapabilityProviderBinding",
    "ProviderConformanceRecord",
    "ProviderInstanceRef",
    "RuntimeEndpointReplicaRef",
    "Connector Pack",
    "Function Calling",
    "MCP != Capability",
    "Availability != Authorization",
    "Selection != StepFeasibility",
    "ActionProposal",
    "PreparedToolAction",
    "ToolAttempt",
    "EffectReceipt",
    "EffectReconciliation",
    "ActionAuthorizationDecision",
    "SecurityApprovalDecision",
    "EffectiveSecurityEpoch",
    "IdempotencyClaim",
    "CrossModuleEnvelopeV1",
    "ToolInventoryGeneration",
    "CAP_UNKNOWN_EFFECT_FALLBACK_FORBIDDEN",
    "HttpApiAdapter",
    "CliAdapter",
    "McpAdapter",
    "CapabilityProviderBindingProposal",
    "Portable Capability",
    "Provider-native Capability",
    "ProviderFailureDomain",
    "PostgreSQL",
    ".agent/programs/",
    "docs/status/production-readiness.md",
]

REQUIRED_TABLES = [
    "capability_definitions",
    "capability_versions",
    "capability_active_versions",
    "capability_requirements",
    "capability_revocations",
    "skill_definitions",
    "skill_versions",
    "skill_resource_manifests",
    "skill_resources",
    "skill_publication_decisions",
    "skill_quarantines",
    "skill_discovery_results",
    "skill_load_results",
    "capability_provider_bindings",
    "provider_conformance_records",
    "capability_availability_snapshots",
    "capability_availability_entries",
    "capability_selection_results",
    "capability_result_validity_records",
    "capability_transition_records",
    "capability_domain_events",
    "capability_outbox_events",
    "capability_reconciliation_records",
]

REQUIRED_STATE_HEADINGS = [
    "# 21. CapabilityVersion 状态机",
    "# 22. SkillVersion 状态机",
    "# 23. CapabilityProviderBinding 状态机",
    "# 24. ProviderConformanceRecord 状态机",
    "# 25. SkillLoad 状态机",
    "# 26. CapabilityAvailabilitySnapshot 状态机",
    "# 27. CapabilitySelectionResult Validity",
]

FORBIDDEN_TERMS = [
    "# 当前与短期目标",
    "ToolRequest：一次工具调用意图",
    "- Approval：副作用审批",
    "- CredentialRef：凭据引用",
    "- ExecutionAdapter：工具执行适配器",
    "- ResultNormalizer：把工具结果归一成 Agent observation",
    "- ToolTrace：审批、执行、timeout、错误和结果摘要",
    "Tool Runtime     = 宿主代码的审批、凭据、执行",
    "模型直接激活 Binding",
    "Skill Loader 直接执行脚本",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []

    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX]:
        if not path.exists():
            errors.append(f"missing Capability / Skill target path: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)

    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Capability / Skill formal document and Agent mirror must be byte-identical")

    if "status: normative-target-module-architecture" not in formal:
        errors.append("Capability / Skill document must declare normative-target-module-architecture")

    positions: list[int] = []
    for part in REQUIRED_PARTS:
        if formal.count(part) != 1:
            errors.append(f"Capability / Skill document must contain part exactly once: {part}")
        else:
            positions.append(formal.index(part))
    if positions and positions != sorted(positions):
        errors.append("Capability / Skill document parts are not in canonical order I through VIII")

    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Capability / Skill document missing required term: {term}")

    for table in REQUIRED_TABLES:
        if table not in formal:
            errors.append(f"Capability / Skill document missing target table: {table}")

    for heading in REQUIRED_STATE_HEADINGS:
        if heading not in formal:
            errors.append(f"Capability / Skill document missing state machine: {heading}")

    for term in FORBIDDEN_TERMS:
        if term in formal:
            errors.append(f"Capability / Skill document contains obsolete or conflicting contract: {term}")

    requirement_ids = [int(value) for value in re.findall(r"ARCH-CAP-(\d{3})", formal)]
    if requirement_ids != list(range(1, 81)):
        errors.append(
            "Capability / Skill document must define ARCH-CAP-001 through ARCH-CAP-080 "
            "exactly once and in order"
        )

    control_ids = [int(value) for value in re.findall(r"RC-CAP-(\d{3})", formal)]
    if control_ids != list(range(1, 81)):
        errors.append(
            "Capability / Skill document must map RC-CAP-001 through RC-CAP-080 "
            "exactly once and in order"
        )

    for requirement_id in range(1, 81):
        for token in [
            f"CAP-{requirement_id:03d}-UT",
            f"CAP-{requirement_id:03d}-IT",
            f"EV-CAP-{requirement_id:03d}",
        ]:
            if token not in formal:
                errors.append(f"Capability / Skill requirement mapping missing: {token}")

    for index_name, content in {
        "docs/modules/README.md": _read(DOCS_INDEX),
        ".agent/modules/README.md": _read(AGENT_INDEX),
    }.items():
        for term in [
            "07-capability-skill.md",
            "verify_capability_skill_target_protocols.py",
        ]:
            if term not in content:
                errors.append(
                    f"{index_name} does not route to Capability / Skill target artifact: {term}"
                )

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Capability / Skill target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
