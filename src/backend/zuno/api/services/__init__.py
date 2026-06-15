from importlib import import_module
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_SUBMODULES = {
    "agent",
    "agent_skill",
    "capability",
    "completion",
    "dialog",
    "history",
    "llm",
    "knowledge",
    "knowledge_file",
    "mcp_agent",
    "mcp_chat",
    "mcp_server",
    "mcp_stdio_server",
    "mcp_user_config",
    "message",
    "mineru",
    "tool",
    "upload",
    "usage_stats",
    "user",
    "wechat",
    "workspace",
    "workspace_session",
}

__all__ = sorted(_SUBMODULES)


def __getattr__(name: str):
    if name in _SUBMODULES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
