from __future__ import annotations

from enum import Enum
from typing import Any


class ExecutionMode(str, Enum):
    TOOL = "tool"
    TERMINAL = "terminal"


class AccessScope(str, Enum):
    WORKSPACE = "workspace"
    UNRESTRICTED = "unrestricted"


EXECUTION_MODE_DEFINITIONS: dict[ExecutionMode, dict[str, Any]] = {
    ExecutionMode.TOOL: {
        "id": ExecutionMode.TOOL.value,
        "label": "工具模式",
        "summary": "默认文件能力加可选工具，适合大多数稳定任务。",
        "capabilities": [
            "文件浏览",
            "文件读取",
            "文件写入",
            "文件搜索",
            "基础文本编辑",
            "可选白名单工具",
        ],
        "restrictions": [
            "不提供通用终端",
            "工具需要显式选择",
        ],
        "supports_tools": True,
        "supports_terminal": False,
    },
    ExecutionMode.TERMINAL: {
        "id": ExecutionMode.TERMINAL.value,
        "label": "终端模式",
        "summary": "为后续内置终端执行预留的高能力模式。",
        "capabilities": [
            "默认文件能力",
            "内置终端执行",
            "脚本与命令调试",
        ],
        "restrictions": [
            "高风险操作应审计",
            "建议显式确认后开启",
        ],
        "supports_tools": False,
        "supports_terminal": True,
    },
}


ACCESS_SCOPE_DEFINITIONS: dict[AccessScope, dict[str, Any]] = {
    AccessScope.WORKSPACE: {
        "id": AccessScope.WORKSPACE.value,
        "label": "工作区限制",
        "summary": "只允许访问当前工作区内容。",
        "capabilities": [
            "访问工作区内文件与目录",
        ],
        "restrictions": [
            "不允许访问工作区外路径",
        ],
        "risk_level": "low",
    },
    AccessScope.UNRESTRICTED: {
        "id": AccessScope.UNRESTRICTED.value,
        "label": "任意访问",
        "summary": "允许访问工作区外路径，应谨慎开启。",
        "capabilities": [
            "允许访问工作区外路径",
        ],
        "restrictions": [
            "建议保留审计日志",
            "建议二次确认危险操作",
        ],
        "risk_level": "high",
    },
}


LEGACY_EXECUTION_MODE_MAP = {
    "default": ExecutionMode.TOOL.value,
    "tool": ExecutionMode.TOOL.value,
    "high_privilege": ExecutionMode.TERMINAL.value,
    "terminal": ExecutionMode.TERMINAL.value,
}

LEGACY_ACCESS_SCOPE_MAP = {
    "default": AccessScope.WORKSPACE.value,
    "workspace": AccessScope.WORKSPACE.value,
    "high_privilege": AccessScope.UNRESTRICTED.value,
    "unrestricted": AccessScope.UNRESTRICTED.value,
}


def normalize_execution_mode(mode: str | None) -> ExecutionMode:
    normalized = (mode or "").strip().lower()
    if not normalized:
        return ExecutionMode.TOOL
    normalized = LEGACY_EXECUTION_MODE_MAP.get(normalized, normalized)
    try:
        return ExecutionMode(normalized)
    except ValueError:
        return ExecutionMode.TOOL


def normalize_access_scope(scope: str | None) -> AccessScope:
    normalized = (scope or "").strip().lower()
    if not normalized:
        return AccessScope.WORKSPACE
    normalized = LEGACY_ACCESS_SCOPE_MAP.get(normalized, normalized)
    try:
        return AccessScope(normalized)
    except ValueError:
        return AccessScope.WORKSPACE


def get_execution_config_payload() -> dict[str, list[dict[str, Any]]]:
    return {
        "execution_modes": [EXECUTION_MODE_DEFINITIONS[mode] for mode in ExecutionMode],
        "access_scopes": [ACCESS_SCOPE_DEFINITIONS[scope] for scope in AccessScope],
    }


def get_tool_runtime_type(tool: dict[str, Any]) -> str:
    auth_config = tool.get("auth_config") or {}
    if tool.get("is_user_defined"):
        runtime_type = (auth_config.get("mode") or "remote_api").strip()
        return runtime_type if runtime_type in {"cli", "remote_api"} else "remote_api"
    return "system"


def annotate_tool_execution_metadata(tool: dict[str, Any]) -> dict[str, Any]:
    runtime_type = get_tool_runtime_type(tool)
    annotated = dict(tool)
    annotated["runtime_type"] = runtime_type
    annotated["execution_mode_min"] = ExecutionMode.TOOL.value
    return annotated


def filter_tools_for_mode(tools: list[dict[str, Any]], mode: str | None) -> list[dict[str, Any]]:
    normalized_mode = normalize_execution_mode(mode)
    if normalized_mode == ExecutionMode.TERMINAL:
        return []

    return [annotate_tool_execution_metadata(tool) for tool in tools]


def validate_tools_for_mode(tools: list[dict[str, Any]], mode: str | None):
    normalized_mode = normalize_execution_mode(mode)
    if normalized_mode == ExecutionMode.TOOL:
        return

    selected_tools = [
        tool.get("display_name") or tool.get("name") or tool.get("tool_id")
        for tool in tools
    ]
    if selected_tools:
        raise ValueError("终端模式下不应再选择工具: " + "、".join(selected_tools))
