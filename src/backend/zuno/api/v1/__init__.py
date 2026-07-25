from pkgutil import extend_path
from importlib import import_module

__path__ = extend_path(__path__, __name__)

_SUBMODULES = {
    "agent",
    "agent_skill",
    "capability",
    "completion",
    "config",
    "dialog",
    "history",
    "knowledge",
    "knowledge_file",
    "llm",
    "mcp_agent",
    "mcp_chat",
    "mcp_server",
    "mcp_stdio_server",
    "mcp_user_config",
    "message",
    "product",
    "tool",
    "upload",
    "usage_stats",
    "user",
    "wechat",
    "workspace",
}

__all__ = sorted(_SUBMODULES)


def __getattr__(name: str):
    if name in _SUBMODULES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
