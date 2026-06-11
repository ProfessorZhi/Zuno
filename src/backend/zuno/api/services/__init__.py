from importlib import import_module

_SUBMODULES = {
    "agent",
    "agent_skill",
    "capability",
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
    "tool",
    "usage_stats",
    "user",
    "wechat",
    "workspace_session",
}

__all__ = sorted(_SUBMODULES)


def __getattr__(name: str):
    if name in _SUBMODULES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
