from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RETIRED_DIRECT_CALLER_FILES = (
    REPO_ROOT / "src/backend/zuno/agent/core/agents/react_agent.py",
    REPO_ROOT / "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
    REPO_ROOT / "src/backend/zuno/agent/core/agents/codeact_agent.py",
)
CURRENT_MCP_MANAGER = REPO_ROOT / "src/backend/zuno/platform/services/mcp/manager.py"


def test_phase16_legacy_direct_tool_callers_use_bypass_guard() -> None:
    for path in RETIRED_DIRECT_CALLER_FILES:
        assert not path.exists()
    text = CURRENT_MCP_MANAGER.read_text(encoding="utf-8")
    assert "ensure_legacy_direct_tool_allowed" in text
    assert "PHASE16_DIRECT_TOOL_BYPASS_BLOCKED" not in text


def test_phase16_no_known_production_user_defined_tool_adapter_direct_execute_bypass() -> None:
    text = (REPO_ROOT / "src/backend/zuno/platform/services/user_defined_tool_runtime.py").read_text(encoding="utf-8")
    assert "ToolInvocationGateway" in text
    assert "gateway.invoke_readonly" in text
    assert "adapter.execute(_tool_name=tool_name" in text
