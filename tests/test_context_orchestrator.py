import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from zuno.services.application.context import (
    AgentExecutionContext,
    ContextItem,
    ContextOrchestrator,
    ContextSelectionReason,
    ContextSource,
    TokenBudgetPolicy,
)
from zuno.services.graphrag.query_service import GraphRAGProjectSnapshot


def _execution_context(
    *,
    snapshot: GraphRAGProjectSnapshot | None = None,
) -> AgentExecutionContext:
    return AgentExecutionContext(
        trace_id="trace-context-test",
        user_id="user-1",
        agent_id="general-agent",
        thread_id="thread-1",
        project_id="project-1",
        task="answer with citations",
        graphrag_project=snapshot,
    )


def _prepare(**kwargs):
    from zuno.services.application.context import ContextPreparationInput

    return ContextOrchestrator().prepare(
        ContextPreparationInput(
            execution_context=kwargs.get("execution_context", _execution_context()),
            messages=tuple(kwargs.get("messages", ())),
            system_instruction=kwargs.get("system_instruction", ""),
            token_budget=kwargs.get(
                "token_budget",
                TokenBudgetPolicy(max_tokens=4000, reserved_response_tokens=800),
            ),
            memory_items=tuple(kwargs.get("memory_items", ())),
            knowledge_evidence_items=tuple(kwargs.get("knowledge_evidence_items", ())),
            capability_items=tuple(kwargs.get("capability_items", ())),
        )
    )


def test_context_orchestrator_preserves_system_instruction_and_latest_user_query():
    result = _prepare(
        system_instruction="Use concise Chinese.",
        messages=(
            SystemMessage(content="framework system message"),
            HumanMessage(content="old question"),
            AIMessage(content="old answer"),
            HumanMessage(content="latest question with evidence"),
        ),
    )

    packet = result.packet.to_dict()
    contents = [item["content"] for item in packet["items"]]
    reasons = packet["trace"]["selection_reasons"]

    assert "Use concise Chinese." in contents
    assert "latest question with evidence" in contents
    assert reasons["system_prompt"] == ContextSelectionReason.PINNED_INSTRUCTION.value
    assert reasons["message_3"] == ContextSelectionReason.RECENT_USER_TURN.value


def test_recent_window_keeps_coherent_recent_messages():
    result = _prepare(
        messages=(
            HumanMessage(content="what is the design"),
            AIMessage(content="the design uses one GeneralAgent"),
            HumanMessage(content="summarize the boundary"),
        ),
    )

    items = result.packet.to_dict()["items"]
    assert [item["item_id"] for item in items] == ["message_0", "message_1", "message_2"]
    assert any(
        item["reason"] == ContextSelectionReason.RECENT_ASSISTANT_TURN.value
        for item in items
    )


def test_tool_call_and_result_group_is_not_split():
    result = _prepare(
        token_budget=TokenBudgetPolicy(max_tokens=12, reserved_response_tokens=0),
        messages=(
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "search_knowledge_base",
                        "args": {"query": "runtime architecture"},
                        "id": "call_1",
                    }
                ],
            ),
            ToolMessage(content="retrieved architecture evidence", tool_call_id="call_1"),
            HumanMessage(content="latest"),
        ),
    )

    selected_tool_items = [
        item
        for item in result.selected_items
        if item.metadata.get("group_id") == "tool_group_0"
    ]
    dropped_tool_items = [
        item
        for item in result.dropped_items
        if item.metadata.get("group_id") == "tool_group_0"
    ]

    assert len(selected_tool_items) in {0, 2}
    assert len(dropped_tool_items) in {0, 2}


def test_low_priority_context_is_evicted_under_budget():
    memory_item = ContextItem(
        item_id="memory-low",
        source=ContextSource.MEMORY,
        content="low value memory",
        token_estimate=120,
        priority=10,
        reason=ContextSelectionReason.RELEVANT_MEMORY,
    )

    result = _prepare(
        token_budget=TokenBudgetPolicy(max_tokens=24, reserved_response_tokens=0),
        system_instruction="Pinned instruction",
        messages=(HumanMessage(content="latest"),),
        memory_items=(memory_item,),
    )

    assert "memory-low" in result.packet.trace.dropped_item_ids
    assert (
        result.packet.trace.selection_reasons["memory-low"]
        == ContextSelectionReason.LOW_PRIORITY_EVICTED.value
    )


def test_explicit_user_constraints_are_preserved():
    result = _prepare(
        token_budget=TokenBudgetPolicy(max_tokens=4, reserved_response_tokens=0),
        messages=(
            AIMessage(content="background answer that can go away"),
            HumanMessage(content="必须 keep the final answer in Chinese"),
        ),
    )

    selected = {item.item_id: item for item in result.selected_items}
    assert selected["message_1"].reason == ContextSelectionReason.EXPLICIT_USER_CONSTRAINT


def test_trace_and_result_are_serializable():
    result = _prepare(
        messages=(HumanMessage(content="serialize context trace"),),
        knowledge_evidence_items=(
            ContextItem(
                item_id="evidence-1",
                source=ContextSource.KNOWLEDGE_EVIDENCE,
                content="citation bundle",
                token_estimate=8,
                priority=70,
                reason=ContextSelectionReason.KNOWLEDGE_RESULT,
            ),
        ),
    )

    json.dumps(result.to_dict(), ensure_ascii=False)
    assert result.packet.trace.trace_id == "trace-context-test"


def test_graphrag_project_snapshot_is_execution_metadata_not_agent_context():
    snapshot = GraphRAGProjectSnapshot(
        graphrag_project_id="graphrag-project-1",
        contract={"query_method": "global"},
        retrieval_settings={"top_k": 8},
    )

    result = _prepare(
        execution_context=_execution_context(snapshot=snapshot),
        messages=(HumanMessage(content="use project knowledge"),),
    )

    packet = result.packet.to_dict()
    assert packet["execution_context"]["graphrag_project_id"] == "graphrag-project-1"
    assert all(
        "graphrag-project-1" not in item["content"]
        and "query_method" not in item["content"]
        for item in packet["items"]
    )


def test_memory_and_knowledge_context_are_separate_and_optional():
    empty_result = _prepare()
    assert empty_result.selected_items == ()
    assert empty_result.packet.items == ()

    memory_item = ContextItem(
        item_id="memory-1",
        source=ContextSource.MEMORY,
        content="remember user preference",
        token_estimate=6,
        priority=65,
        reason=ContextSelectionReason.RELEVANT_MEMORY,
    )
    evidence_item = ContextItem(
        item_id="evidence-1",
        source=ContextSource.KNOWLEDGE_EVIDENCE,
        content="retrieval evidence",
        token_estimate=6,
        priority=70,
        reason=ContextSelectionReason.KNOWLEDGE_RESULT,
    )

    result = _prepare(
        memory_items=(memory_item,),
        knowledge_evidence_items=(evidence_item,),
    )

    sources = {item.item_id: item.source for item in result.selected_items}
    assert sources["memory-1"] == ContextSource.MEMORY
    assert sources["evidence-1"] == ContextSource.KNOWLEDGE_EVIDENCE
