from importlib import import_module

_AGENTCHAT_MODULE = "agentchat.services.workspace.wechat_agent"
_agentchat_wechat_agent = import_module(_AGENTCHAT_MODULE)

MCPConfig = _agentchat_wechat_agent.MCPConfig
WeChatAgent = _agentchat_wechat_agent.WeChatAgent

__all__ = ["MCPConfig", "WeChatAgent"]
