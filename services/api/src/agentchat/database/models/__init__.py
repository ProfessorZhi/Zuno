from __future__ import annotations

import sys
from importlib import import_module
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_ZUNO_MODELS = import_module("zuno.database.models")

_ALIASES = {
    "agent": "agent",
    "agent_skill": "agent_skill",
    "base": "base",
    "dialog": "dialog",
    "history": "history",
    "knowledge": "knowledge",
    "knowledge_file": "knowledge_file",
    "knowledge_task": "knowledge_task",
    "llm": "llm",
    "mcp_agent": "mcp_agent",
    "mcp_server": "mcp_server",
    "mcp_user_config": "mcp_user_config",
    "memory_history": "memory_history",
    "message": "message",
    "role": "role",
    "tool": "tool",
    "usage_stats": "usage_stats",
    "user": "user",
    "user_role": "user_role",
    "workspace_session": "workspace_session",
}

for alias_name, target_name in _ALIASES.items():
    sys.modules.setdefault(
        f"{__name__}.{alias_name}",
        import_module(f"zuno.database.models.{target_name}"),
    )

__all__ = list(getattr(_ZUNO_MODELS, "__all__", []))


def __getattr__(name: str):
    return getattr(_ZUNO_MODELS, name)
