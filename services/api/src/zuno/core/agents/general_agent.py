from importlib import import_module

# Compatibility-only facade over the legacy `agentchat` implementation.
_AGENTCHAT_MODULE = "agentchat.core.agents.general_agent"
_agentchat_general_agent = import_module(_AGENTCHAT_MODULE)

AgentConfig = _agentchat_general_agent.AgentConfig
EmitEventAgentMiddleware = _agentchat_general_agent.EmitEventAgentMiddleware
GeneralAgent = _agentchat_general_agent.GeneralAgent
StreamAgentState = _agentchat_general_agent.StreamAgentState

__all__ = [
    "AgentConfig",
    "EmitEventAgentMiddleware",
    "GeneralAgent",
    "StreamAgentState",
]
