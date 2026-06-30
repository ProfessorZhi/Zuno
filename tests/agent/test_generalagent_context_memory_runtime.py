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
    capability_item = next(item for item in packet.items if item.item_id == "search_knowledge_base")
    selection_trace = capability_item.metadata["capability_selection_trace"]
    assert selection_trace["selected_tool_card_ids"] == ["Knowledge:search_knowledge_base"]
    assert selection_trace["candidate_tool_card_ids"] == ["Knowledge:search_knowledge_base"]
    assert selection_trace["injected_schema_ids"] == []


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
    assert captured_input["context_trace"]["source_event_ids_by_item"]["message_0"] == ["message:0"]
    assert captured_input["model_context_packet"]["context_policy"]["compression_strategy"] == "summary_compression"
    assert captured_input["model_context_packet"]["execution_context"]["thread_id"] == "thread_1"
    assert agent.last_model_context_packet is not None

    scope = agent._memory_scope()
    raw_events = agent.memory_layer_store.raw_events(scope)
    summaries = agent.memory_layer_store.task_summaries(scope)

    assert raw_events[0].layer is MemoryLayer.WORKING
    assert raw_events[0].payload["response"] == "runtime answer"
    assert raw_events[0].payload["context_policy"]["extraction_strategy"] == "structured_extraction"
    assert summaries[0].layer is MemoryLayer.TASK
    assert summaries[0].source_event_ids == (raw_events[0].event_id,)
    assert summaries[0].metadata["compression_strategy"] == "summary_compression"


def test_general_agent_runtime_turn_ledger_links_runtime_contracts() -> None:
    from zuno.core.agents.general_agent import GeneralAgent

    captured_input = {}

    class FakeTool:
        name = "search_knowledge_base"
        description = "Search project knowledge base and GraphRAG evidence."
        args = {"query": {"type": "string"}}

    class FakeReactAgent:
        async def astream(self, *args, **kwargs):
            captured_input.update(kwargs["input"])
            agent.record_knowledge_trace_metadata(
                {
                    "trace_id": "retrieval-trace-1",
                    "runtime_trace_events": [
                        {"event_id": "retrieval-trace-1:0001:pre_retrieval", "kind": "pre_retrieval"},
                        {"event_id": "retrieval-trace-1:0003:post_answer", "kind": "post_answer"},
                    ],
                    "evidence_verdict": {
                        "status": "pass",
                        "citation_coverage": 1.0,
                    },
                    "artifact_manifest": {
                        "trace_id": "retrieval-trace-1",
                        "retrieval_refs": ["chunk-1"],
                        "evidence_refs": ["chunk-1"],
                    },
                    "query_method_contract": {
                        "resolved_query_method": "local",
                        "internal_route": "local_graphrag",
                    },
                }
            )
            agent.record_tool_trace_event(
                {
                    "event_id": "tool-call_1:0001:pre_tool",
                    "kind": "pre_tool",
                    "refs": {"tool": ["search_knowledge_base"]},
                }
            )
            yield "messages", [AIMessageChunk(content="integrated runtime answer")]

    agent = GeneralAgent(_agent_config(enable_memory=True))
    agent.tools = [FakeTool()]
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

    assert events[-1]["data"]["accumulated"] == "integrated runtime answer"
    assert captured_input["context_trace"]["selected_item_ids"]
    assert agent.last_runtime_turn_ledger is not None
    ledger = agent.last_runtime_turn_ledger.to_dict()

    assert ledger["stage_order"] == [
        "prepare_context",
        "capability_selection",
        "agent_loop",
        "knowledge_retrieval_trace",
        "tool_trace",
        "post_turn_commit",
    ]
    assert ledger["layers_touched"] == [
        "agent",
        "context",
        "capability",
        "knowledge",
        "trace",
        "memory",
    ]
    assert ledger["context_trace"]["selected_item_ids"]
    assert ledger["capability_trace"]["selected_names"] == ["search_knowledge_base"]
    assert ledger["knowledge_trace"]["query_method_contract"]["resolved_query_method"] == "local"
    assert ledger["tool_trace_events"][0]["kind"] == "pre_tool"
    assert ledger["post_turn_memory_event_ids"][0].endswith(":turn")
    assert ledger["response_present"] is True


def test_general_agent_runtime_turn_ledger_uses_current_knowledge_tool_trace(monkeypatch) -> None:
    from zuno.core.agents import general_agent as ga
    from zuno.core.agents.general_agent import GeneralAgent
    from zuno.knowledge.query_service import KnowledgeQueryResult

    captured_input = {}

    async def fake_query(self, *, user_id, knowledge_ids, query, product_mode="auto", query_method=None, top_k=None):
        del self, user_id, knowledge_ids, query, product_mode, query_method, top_k
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="fresh knowledge answer",
            requested_query_method="local",
            resolved_query_method="local",
            fallback_reason=None,
            documents=[{"chunk_id": "chunk-1"}],
            evidence={"document_count": 1, "citation_coverage": 1.0},
            citations=["chunk-1"],
            retrievers_used=["vector", "graph"],
            graph_paths=[],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={},
            community_version=None,
            trace_metadata={
                "trace_id": "fresh-retrieval-trace",
                "runtime_trace_events": [
                    {"event_id": "fresh-retrieval-trace:0001:pre_retrieval", "kind": "pre_retrieval"},
                    {"event_id": "fresh-retrieval-trace:0003:post_answer", "kind": "post_answer"},
                ],
                "evidence_verdict": {"status": "pass", "citation_coverage": 1.0},
                "artifact_manifest": {
                    "trace_id": "fresh-retrieval-trace",
                    "retrieval_refs": ["chunk-1"],
                    "evidence_refs": ["chunk-1"],
                },
                "query_method_contract": {
                    "resolved_query_method": "local",
                    "internal_route": "local_graphrag",
                },
            },
        )

    monkeypatch.setattr(ga.KnowledgeQueryService, "query", fake_query)

    agent = GeneralAgent(_agent_config(enable_memory=True))
    asyncio.run(agent.setup_knowledge_tool())
    agent.last_knowledge_trace_metadata = {"trace_id": "stale-trace"}
    agent.runtime_tool_trace_events = [{"kind": "stale_tool"}]

    class FakeReactAgent:
        async def astream(self, *args, **kwargs):
            captured_input.update(kwargs["input"])
            agent.record_tool_trace_event(
                {
                    "event_id": "tool-call_1:0001:pre_tool",
                    "kind": "pre_tool",
                    "refs": {"tool": ["search_knowledge_base"]},
                }
            )
            result = await agent.tools[0].ainvoke({"query": "use current knowledge trace"})
            yield "messages", [AIMessageChunk(content=result)]

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

    assert "fresh knowledge answer" in events[-1]["data"]["accumulated"]
    assert captured_input["context_trace"]["selected_item_ids"]
    assert agent.last_runtime_turn_ledger is not None
    ledger = agent.last_runtime_turn_ledger.to_dict()
    assert ledger["knowledge_trace"]["trace_id"] == "fresh-retrieval-trace"
    assert ledger["tool_trace_events"] == [
        {
            "event_id": "tool-call_1:0001:pre_tool",
            "kind": "pre_tool",
            "refs": {"tool": ["search_knowledge_base"]},
        }
    ]
    assert ledger["post_turn_memory_event_ids"][0].endswith(":turn")
    assert "stale" not in str(ledger)

    raw_event = agent.memory_layer_store.raw_events(agent._memory_scope())[0]
    assert raw_event.payload["knowledge_trace"]["trace_id"] == "fresh-retrieval-trace"
    assert raw_event.payload["tool_trace_events"][0]["kind"] == "pre_tool"
    assert raw_event.payload["capability_trace"]["selected_names"] == ["search_knowledge_base"]


def test_general_agent_reads_task_summary_and_approved_memory_into_context() -> None:
    from zuno.core.agents.general_agent import GeneralAgent
    from zuno.services.application.context import ContextSource
    from zuno.services.memory import (
        MemoryCandidate,
        MemoryLayer,
        MemoryReviewStatus,
        RawMemoryEvent,
        RetentionPolicy,
        TaskMemorySummary,
    )

    agent = GeneralAgent(_agent_config(enable_memory=True))
    scope = agent._memory_scope()
    raw_event = RawMemoryEvent(
        event_id="evt_summary_source",
        scope=scope,
        event_type="agent_turn",
        payload={"task": "summarize contract", "response": "short summary"},
    )
    agent.memory_layer_store.append_raw_event(raw_event)
    agent.memory_layer_store.save_task_summary(
        TaskMemorySummary(
            summary_id="summary_1",
            scope=scope,
            layer=MemoryLayer.TASK,
            content="Prior task summary with open question.",
            source_event_ids=(raw_event.event_id,),
            token_count=8,
        )
    )
    agent.memory_layer_store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="semantic_1",
            scope=scope,
            layer=MemoryLayer.SEMANTIC,
            content="User prefers concise architecture status.",
            confidence=0.91,
            source_event_ids=("evt_preference",),
            dedupe_key="preference:concise-architecture-status",
            retention_policy=RetentionPolicy(ttl_days=180),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
        )
    )

    packet = agent.prepare_context([HumanMessage(content="Continue the review")])
    sources = {item.item_id: item for item in packet.items}

    assert sources["task_summary_0"].source is ContextSource.TASK_SUMMARY
    assert sources["task_summary_0"].source_event_ids == ("evt_summary_source",)
    assert sources["memory_candidate_0"].source is ContextSource.MEMORY
    assert sources["memory_candidate_0"].metadata["review_status"] == "approved"
    assert packet.trace.source_event_ids_by_item["memory_candidate_0"] == ("evt_preference",)
