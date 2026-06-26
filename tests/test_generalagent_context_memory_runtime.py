from __future__ import annotations

import asyncio
from types import SimpleNamespace

from langchain_core.messages import AIMessageChunk, HumanMessage


def _agent_config(enable_memory: bool = True):
    from zuno.core.agents.general_agent import AgentConfig

    return AgentConfig(
        user_id="u_1",
        llm_id="",
        mcp_ids=[],
        knowledge_ids=["kb_1"],
        dialog_id="thread_1",
        tool_ids=[],
        agent_skill_ids=[],
        system_prompt="Use available project knowledge.",
        name="contract-agent",
        enable_memory=enable_memory,
    )


def test_general_agent_prepares_context_packet_and_selected_capability_trace() -> None:
    from zuno.core.agents.general_agent import GeneralAgent
    from zuno.services.application.context import ContextSource, ModelContextPacket

    class FakeTool:
        name = "search_knowledge_base"
        description = "Search project knowledge base and GraphRAG evidence."
        args = {"query": {"type": "string"}}

    agent = GeneralAgent(_agent_config())
    agent.tools = [FakeTool()]

    packet = agent.prepare_context(
        [HumanMessage(content="Search the project knowledge base for indemnity evidence")]
    )

    assert isinstance(packet, ModelContextPacket)
    assert packet.execution_context.task == "Search the project knowledge base for indemnity evidence"
    assert any(item.source is ContextSource.CAPABILITY_SCHEMA for item in packet.items)
    assert agent.last_capability_selection is not None
    assert agent.last_capability_selection.trace.selected_names == ("search_knowledge_base",)
    assert "search_knowledge_base" in packet.trace.selected_item_ids


def test_general_agent_astream_passes_context_trace_into_single_loop_and_commits_memory() -> None:
    from zuno.core.agents.general_agent import GeneralAgent
    from zuno.services.memory import MemoryLayer

    captured_input = {}

    class FakeReactAgent:
        async def astream(self, *args, **kwargs):
            captured_input.update(kwargs["input"])
            yield "messages", [AIMessageChunk(content="runtime answer")]

    agent = GeneralAgent(_agent_config(enable_memory=True))
    agent.react_agent = FakeReactAgent()
    agent.conversation_model = SimpleNamespace()

    async def collect():
        return [
            event
            async for event in agent.astream(
                [HumanMessage(content="Search the project knowledge base for indemnity evidence")]
            )
        ]

    events = asyncio.run(collect())

    assert events[-1]["data"]["accumulated"] == "runtime answer"
    assert captured_input["context_trace"]["selected_item_ids"]
    assert captured_input["model_context_packet"]["execution_context"]["thread_id"] == "thread_1"
    assert agent.last_model_context_packet is not None

    scope = agent._memory_scope()
    raw_events = agent.memory_layer_store.raw_events(scope)
    summaries = agent.memory_layer_store.task_summaries(scope)

    assert raw_events[0].layer is MemoryLayer.WORKING
    assert raw_events[0].payload["response"] == "runtime answer"
    assert summaries[0].layer is MemoryLayer.TASK
    assert summaries[0].source_event_ids == (raw_events[0].event_id,)
