from importlib import import_module

# Compatibility-only facade over the legacy `agentchat` workspace agent.
_AGENTCHAT_MODULE = "agentchat.services.workspace.simple_agent"
_agentchat_simple_agent = import_module(_AGENTCHAT_MODULE)

MCPConfig = _agentchat_simple_agent.MCPConfig
WorkSpaceSimpleAgent = _agentchat_simple_agent.WorkSpaceSimpleAgent

__all__ = ["MCPConfig", "WorkSpaceSimpleAgent"]
