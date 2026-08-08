import asyncio
import pytest


def test_mcp_chat_agent_ainvoke_fails_closed(monkeypatch):
    """PHASE22: MCP Chat execution fails closed with
    MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND — zero provider calls, zero model
    calls. The legacy MCPManager.process_query / deep_anthropic direct
    execution loop is retired."""
    from zuno.api.services.mcp_chat import (
        MCPChatAgent,
        MCPChatCanonicalRuntimeNotBound,
    )

    agent = MCPChatAgent(
        mcp_servers_id=[],
        llm_id="llm_1",
        enable_memory=False,
        knowledges_id=["kb_1"],
    )

    with pytest.raises(MCPChatCanonicalRuntimeNotBound) as excinfo:
        asyncio.run(agent.ainvoke("解释一下这套 Python 课程结构", "dialog_1"))
    assert "MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND" in str(excinfo.value)

    # init_MCP_Server fails closed too: no MCP server connection is made.
    with pytest.raises(MCPChatCanonicalRuntimeNotBound):
        asyncio.run(agent.init_MCP_Server())

    # The agent never holds a provider model or an MCP execution manager.
    assert not hasattr(agent, "deep_anthropic")
    assert not hasattr(agent, "mcp_manager")


def test_mcp_chat_agent_memory_history_falls_back_to_direct_history(monkeypatch):
    from zuno.api.services.mcp_chat import MCPChatAgent

    async def fake_direct_history(self, dialog_id, top_k):
        assert dialog_id == "dialog_2"
        assert top_k == 3
        return [{"role": "assistant", "content": "最近历史"}]

    monkeypatch.setattr(MCPChatAgent, "_direct_history", fake_direct_history)

    agent = MCPChatAgent(
        mcp_servers_id=[],
        llm_id="llm_1",
        enable_memory=True,
        knowledges_id=[],
    )

    result = asyncio.run(agent._retrieval_history("查询问题", "dialog_2", 3))

    assert result == [{"role": "assistant", "content": "最近历史"}]


def test_mcp_chat_agent_direct_history_awaits_history_service(monkeypatch):
    from zuno.api.services.mcp_chat import MCPChatAgent

    async def fake_select_history(dialog_id, top_k):
        assert dialog_id == "dialog_3"
        assert top_k == 2
        return ["history-message"]

    monkeypatch.setattr(
        "zuno.api.services.mcp_chat.HistoryService.select_history",
        fake_select_history,
    )

    agent = MCPChatAgent(
        mcp_servers_id=[],
        llm_id="llm_1",
        enable_memory=False,
        knowledges_id=[],
    )

    result = asyncio.run(agent._direct_history("dialog_3", 2))

    assert result == ["history-message"]
