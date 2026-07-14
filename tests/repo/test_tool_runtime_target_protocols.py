from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_tool_runtime_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/08-tool-runtime.md"
MIRROR = REPO_ROOT / ".agent/modules/08-tool-runtime.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_tool_runtime_target_protocols", VERIFIER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Tool Runtime verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_tool_runtime_target_verifier() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_tool_runtime_has_one_formal_document_and_one_identical_mirror() -> None:
    assert sorted(path.name for path in FORMAL.parent.glob("08-*.md")) == [
        "08-tool-runtime.md"
    ]
    assert sorted(path.name for path in MIRROR.parent.glob("08-*.md")) == [
        "08-tool-runtime.md"
    ]
    assert FORMAL.read_bytes() == MIRROR.read_bytes()


def test_tool_runtime_parts_are_complete_and_ordered() -> None:
    content = _content()
    parts = [
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
    positions = [content.index(part) for part in parts]
    assert positions == sorted(positions)
    assert all(content.count(part) == 1 for part in parts)


def test_tool_runtime_requirements_and_controls_are_contiguous() -> None:
    content = _content()
    requirement_ids = {
        int(value) for value in re.findall(r"ARCH-TOOL-(\d{3})", content)
    }
    control_ids = {int(value) for value in re.findall(r"RC-TOOL-(\d{3})", content)}
    assert requirement_ids == set(range(1, 81))
    assert control_ids == set(range(1, 81))


def test_tool_runtime_owns_execution_facts_but_not_security_or_infrastructure() -> None:
    content = _content()
    for phrase in [
        "08 Tool Runtime\n    ToolProviderDefinition",
        "PreparedToolAction",
        "ToolAttempt / ToolObservation",
        "ToolExecutionReceipt",
        "EffectReceipt / EffectReconciliation",
        "09 Security\n    Tool Exposure / Prepare / Execute Authorization",
        "11 Infrastructure\n    事务、Outbox / Inbox、Queue、Lease、Fencing",
    ]:
        assert phrase in content
    assert "Tool Runtime owns SecurityApprovalDecision" not in content
    assert "Tool Runtime owns IdempotencyClaim" not in content


def test_all_supported_adapter_families_have_contracts() -> None:
    content = _content()
    for phrase in [
        "## 13. CLI / 本地进程",
        "## 14. HTTP API / OpenAPI",
        "## 15. Provider SDK",
        "## 16. MCP Tool",
        "## 17. Browser / Computer Use",
        "## 18. 异步 Job、Streaming 和 Callback",
        "AdapterConformanceProfile",
    ]:
        assert phrase in content


def test_effect_assurance_does_not_claim_universal_exactly_once() -> None:
    content = _content()
    for phrase in [
        "Zuno 不承诺通用 Exactly Once",
        "UNKNOWN 禁止盲目 Retry",
        "只有 `CONFIRMED_NOT_EXECUTED`",
        "Compensation 是新的受治理副作用",
        "ToolExecutionReceipt != Agent Step accepted",
    ]:
        assert phrase in content


def test_mcp_is_cross_module_and_tool_execution_belongs_to_08() -> None:
    content = _content()
    for phrase in [
        "MCP 是跨模块协议，不是 08 单模块私有 Runtime",
        "MCP Tool execution\n    08 Tool Runtime",
        "MCP Sampling 必须进入 Model Gateway",
        "MCP Elicitation 不能冒充 Security Approval",
        "MCP annotations 默认不可信",
        "McpCapabilitySnapshot",
        "McpTaskBinding",
    ]:
        assert phrase in content


def test_current_target_boundary_and_migration_are_explicit() -> None:
    content = _content()
    for phrase in [
        "Current 证据",
        "GeneralAgent → LangChain Tool handler",
        "MCPManager → tool.coroutine / asyncio.gather",
        "ALLOWED_LEGACY_TOOL_EXECUTION_PATHS",
        "M10 Legacy Removal",
        "implementation available",
        "production ready",
    ]:
        assert phrase in content
    assert "status: current" not in content


def test_target_physical_path_respects_six_layer_repository_contract() -> None:
    content = _content()
    assert "不新增顶层 `zuno/tool_runtime`" in content
    assert "src/backend/zuno/capability/tool_runtime/" in content
