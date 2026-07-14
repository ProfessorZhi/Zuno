from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/08-tool-runtime.md"
MIRROR = REPO_ROOT / ".agent/modules/08-tool-runtime.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
CAPABILITY_DOC = REPO_ROOT / "docs/modules/07-capability-skill.md"
DOCS_MAP = REPO_ROOT / ".agent/references/docs-map.md"
AGENT_SYSTEM = REPO_ROOT / ".agent/system.yaml"
AGENTS = REPO_ROOT / "AGENTS.md"
DOCS_ENTRYPOINT_VERIFIER = REPO_ROOT / "tools/scripts/verify_docs_entrypoints.py"
AGENT_SYSTEM_VERIFIER = REPO_ROOT / ".agent/scripts/verify_agent_system.py"

REQUIRED_PARTS = [
    "# Part I：定位、术语与边界",
    "# Part II：完整执行流程",
    "# Part III：领域对象与 Contract",
    "# Part IV：状态机与不变量",
    "# Part V：一致性、失败与恢复",
    "# Part VI：安全、输出治理与隔离",
    "# Part VII：Adapter、运维、存储与代码规格",
    "# Part VIII：Current、Target、Gap、Future 与迁移",
    "# Part IX：测试、Requirement 与完成证据",
]

REQUIRED_TERMS = [
    "status: normative-target-module-architecture",
    "唯一的正式 Target 架构主设计",
    "ToolInvocationGateway",
    "ToolProviderDefinition",
    "ToolDefinition",
    "ToolVersion",
    "ToolOperation",
    "ToolInstallation",
    "AdapterConformanceProfile",
    "CanonicalizationProfile",
    "TargetResourceSet",
    "PreparedToolAction",
    "ToolDispatchBinding",
    "ToolAttempt",
    "NativeToolResult",
    "ToolObservation",
    "ToolExecutionReceipt",
    "EffectReceipt",
    "EffectItemReceipt",
    "EffectReconciliation",
    "CancellationReceipt",
    "CompensationAttempt",
    "ManualEffectAssessment",
    "McpCapabilitySnapshot",
    "McpTaskBinding",
    "CrossModuleEnvelopeV1",
    "ALLOWED_LEGACY_TOOL_EXECUTION_PATHS",
    "CLI / HTTP / OpenAPI / SDK / MCP / Browser / Async Job",
    "Zuno 不承诺通用 Exactly Once",
    "UNKNOWN 禁止盲目 Retry",
    "Tool Output 默认不可信",
    "src/backend/zuno/capability/tool_runtime/",
    "design available",
    "implementation-spec-complete",
    "implementation available",
    "production ready",
]

FORBIDDEN_ASSERTIONS = [
    "Tool Runtime owns SecurityApprovalDecision",
    "Tool Runtime owns IdempotencyClaim",
    "Tool Runtime owns ModelCall",
    "HTTP 2xx 表示 Effect 成功",
    "Queue ACK 表示 Tool Effect 成功",
    "通用 Exactly Once 已实现",
    "status: current",
]

CAPABILITY_REQUIRED = [
    "07 只保存 Capability、Skill 和 Planner Projection",
    "08 保存权威 Tool Definition、Version、Prepare、Attempt、Observation、Effect 和 Reconciliation",
    "MCP Tool execution\n    08 Tool Runtime",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []

    required_paths = [
        FORMAL,
        MIRROR,
        DOCS_INDEX,
        AGENT_INDEX,
        CAPABILITY_DOC,
        DOCS_MAP,
        AGENT_SYSTEM,
        AGENTS,
        DOCS_ENTRYPOINT_VERIFIER,
        AGENT_SYSTEM_VERIFIER,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing Tool Runtime architecture path: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal_candidates = sorted(path.name for path in FORMAL.parent.glob("08-*.md"))
    mirror_candidates = sorted(path.name for path in MIRROR.parent.glob("08-*.md"))
    if formal_candidates != ["08-tool-runtime.md"]:
        errors.append(f"Module 08 must keep one formal design document, got: {formal_candidates}")
    if mirror_candidates != ["08-tool-runtime.md"]:
        errors.append(f"Module 08 must keep one Agent mirror, got: {mirror_candidates}")

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Tool Runtime formal document and Agent mirror must be byte-identical")

    positions: list[int] = []
    for part in REQUIRED_PARTS:
        if formal.count(part) != 1:
            errors.append(f"Tool Runtime document must contain part exactly once: {part}")
        else:
            positions.append(formal.index(part))
    if positions and positions != sorted(positions):
        errors.append("Tool Runtime document parts are not in canonical order")

    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Tool Runtime document missing required term: {term}")
    for assertion in FORBIDDEN_ASSERTIONS:
        if assertion in formal:
            errors.append(f"Tool Runtime document contains forbidden assertion: {assertion}")

    requirement_ids = {int(value) for value in re.findall(r"ARCH-TOOL-(\d{3})", formal)}
    if requirement_ids != set(range(1, 81)):
        missing = sorted(set(range(1, 81)) - requirement_ids)
        extra = sorted(requirement_ids - set(range(1, 81)))
        errors.append(
            "Tool Runtime document must define ARCH-TOOL-001 through ARCH-TOOL-080; "
            f"missing={missing}, extra={extra}"
        )

    control_ids = {int(value) for value in re.findall(r"RC-TOOL-(\d{3})", formal)}
    if control_ids != set(range(1, 81)):
        errors.append("Tool Runtime document must map RC-TOOL-001 through RC-TOOL-080")

    docs_index = _read(DOCS_INDEX)
    agent_index = _read(AGENT_INDEX)
    docs_map = _read(DOCS_MAP)
    agent_system = _read(AGENT_SYSTEM)
    agents = _read(AGENTS)
    docs_verifier = _read(DOCS_ENTRYPOINT_VERIFIER)
    system_verifier = _read(AGENT_SYSTEM_VERIFIER)

    if "[08-tool-runtime.md](./08-tool-runtime.md)" not in docs_index:
        errors.append("docs/modules/README.md must link the sole Tool Runtime document")
    if "[08-tool-runtime.md](./08-tool-runtime.md)" not in agent_index:
        errors.append(".agent/modules/README.md must link the Tool Runtime mirror")
    for content_name, content in [
        ("docs/modules/README.md", docs_index),
        (".agent/modules/README.md", agent_index),
    ]:
        if "单一完整 Target 架构" not in content:
            errors.append(f"{content_name} must describe Tool Runtime as a single complete Target architecture")
        if "verify_tool_runtime_target_protocols.py" not in content:
            errors.append(f"{content_name} must route the Tool Runtime verifier")

    for content_name, content in [
        (".agent/references/docs-map.md", docs_map),
        (".agent/system.yaml", agent_system),
        ("AGENTS.md", agents),
        ("tools/scripts/verify_docs_entrypoints.py", docs_verifier),
        (".agent/scripts/verify_agent_system.py", system_verifier),
    ]:
        if "08-tool-runtime.md" not in content:
            errors.append(f"{content_name} must route the Tool Runtime document")

    capability = _read(CAPABILITY_DOC)
    for phrase in CAPABILITY_REQUIRED:
        if phrase not in capability:
            errors.append(f"Capability document missing Tool Runtime ownership alignment: {phrase}")
    for stale in [
        "- Approval：副作用审批。",
        "- CredentialRef：凭据引用",
        "- ExecutionAdapter：工具执行适配器。",
        "- ResultNormalizer：把工具结果归一成 Agent observation。",
    ]:
        if stale in capability:
            errors.append(f"Capability document retains stale Tool Runtime ownership: {stale}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Tool Runtime target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
