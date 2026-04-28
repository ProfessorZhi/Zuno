import asyncio
from types import SimpleNamespace


def test_mcp_chat_agent_ainvoke_uses_ranked_retrieval(monkeypatch):
    from agentchat.api.services.mcp_chat import MCPChatAgent

    async def fake_ainvoke(messages):
        return {"messages": messages}

    monkeypatch.setattr(
        MCPChatAgent,
        "_init_Anthropic",
        lambda self: SimpleNamespace(ainvoke=fake_ainvoke),
    )

    class FakeMCPManager:
        async def process_query(self, messages):
            return list(messages)

    monkeypatch.setattr(MCPChatAgent, "_init_MCP_Manager", lambda self: FakeMCPManager())

    async def fake_history(self, user_input, dialog_id, top_k=5):
        assert user_input == "解释一下这套 Python 课程结构"
        assert dialog_id == "dialog_1"
        assert top_k == 5
        return [{"role": "user", "content": "历史消息"}]

    async def fake_retrieve(query, collection_names, index_names=None, **kwargs):
        assert query == "解释一下这套 Python 课程结构"
        assert collection_names == ["kb_1"]
        assert index_names == ["kb_1"]
        return "知识库召回结果"

    monkeypatch.setattr(MCPChatAgent, "get_history_message", fake_history)
    monkeypatch.setattr(
        "agentchat.api.services.mcp_chat.RagHandler.retrieve_ranked_documents",
        fake_retrieve,
    )

    agent = MCPChatAgent(
        mcp_servers_id=[],
        llm_id="llm_1",
        enable_memory=False,
        knowledges_id=["kb_1"],
    )

    result = asyncio.run(agent.ainvoke("解释一下这套 Python 课程结构", "dialog_1"))

    assert result["messages"][-1] == {"role": "user", "content": "知识库召回结果"}


def test_mcp_chat_agent_memory_history_falls_back_to_direct_history(monkeypatch):
    from agentchat.api.services.mcp_chat import MCPChatAgent

    monkeypatch.setattr(MCPChatAgent, "_init_Anthropic", lambda self: SimpleNamespace())
    monkeypatch.setattr(MCPChatAgent, "_init_MCP_Manager", lambda self: SimpleNamespace())

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
    from agentchat.api.services.mcp_chat import MCPChatAgent

    monkeypatch.setattr(MCPChatAgent, "_init_Anthropic", lambda self: SimpleNamespace())
    monkeypatch.setattr(MCPChatAgent, "_init_MCP_Manager", lambda self: SimpleNamespace())

    async def fake_select_history(dialog_id, top_k):
        assert dialog_id == "dialog_3"
        assert top_k == 2
        return ["history-message"]

    monkeypatch.setattr(
        "agentchat.api.services.mcp_chat.HistoryService.select_history",
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
