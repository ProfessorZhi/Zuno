from importlib import import_module

_SUBMODULES = {
    "capability_registry",
    "cli_tool_discovery",
    "convert_files",
    "domain_pack",
    "execution_policy",
    "graphrag",
    "mcp",
    "mcp_openai",
    "memory",
    "pipeline",
    "queue",
    "rag",
    "redis",
    "retrieval",
    "runtime_registry",
    "simple_api_tool",
    "storage",
    "tool_connectivity_service",
    "tool_creation_service",
    "user_defined_tool_runtime",
    "workspace",
}

__all__ = sorted(_SUBMODULES)


def __getattr__(name: str):
    if name in _SUBMODULES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
