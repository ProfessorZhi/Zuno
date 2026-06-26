from dataclasses import replace


def test_model_context_packet_serializes_without_mutating_graphrag_snapshot() -> None:
    from zuno.services.application.context.contracts import (
        AgentExecutionContext,
        ContextItem,
        ContextSelectionReason,
        ContextSource,
        ContextTrace,
        ModelContextPacket,
        TokenBudgetPolicy,
    )
    from zuno.services.graphrag.query_service import GraphRAGProjectSnapshot

    snapshot = GraphRAGProjectSnapshot(
        graphrag_project_id="contract_review",
        contract={"query_method": "local"},
        query_policy={"default_method": "local"},
        prompt_categories=["local"],
        index_version={"graph": "graph-v1"},
        readiness={"local": True},
    )
    original_snapshot = replace(snapshot)

    execution_context = AgentExecutionContext(
        trace_id="trace_1",
        user_id="u1",
        agent_id="agent_1",
        thread_id="thread_1",
        project_id="project_1",
        task="answer contract question",
        graphrag_project=snapshot,
    )
    item = ContextItem(
        item_id="msg_1",
        source=ContextSource.RECENT_MESSAGE,
        content="What termination clause applies?",
        token_estimate=5,
        priority=100,
        reason=ContextSelectionReason.RECENT_USER_TURN,
        source_event_ids=("event_1",),
    )
    policy = TokenBudgetPolicy(max_tokens=32, reserved_response_tokens=8)
    trace = ContextTrace.from_items(
        trace_id="trace_1",
        policy=policy,
        selected_items=(item,),
        dropped_items=(),
    )

    packet = ModelContextPacket(
        execution_context=execution_context,
        items=(item,),
        token_budget=policy,
        trace=trace,
    )

    payload = packet.to_dict()

    assert snapshot == original_snapshot
    assert payload["execution_context"]["trace_id"] == "trace_1"
    assert payload["execution_context"]["graphrag_project_id"] == "contract_review"
    assert "graphrag_project" not in payload["items"][0]
    assert payload["items"][0]["source"] == "recent_message"
    assert payload["trace"]["selected_item_ids"] == ["msg_1"]
    assert payload["trace"]["token_budget"]["remaining_tokens"] == 19


def test_token_budget_trace_records_dropped_items_and_reasons() -> None:
    from zuno.services.application.context.contracts import (
        ContextItem,
        ContextSelectionReason,
        ContextSource,
        ContextTrace,
        TokenBudgetPolicy,
    )

    selected = ContextItem(
        item_id="memory_1",
        source=ContextSource.MEMORY,
        content="User prefers concise answers.",
        token_estimate=4,
        priority=80,
        reason=ContextSelectionReason.RELEVANT_MEMORY,
    )
    dropped = ContextItem(
        item_id="tool_1",
        source=ContextSource.TOOL_RESULT,
        content="Long tool output",
        token_estimate=100,
        priority=10,
        reason=ContextSelectionReason.LOW_PRIORITY_EVICTED,
    )
    policy = TokenBudgetPolicy(max_tokens=20, reserved_response_tokens=6)

    trace = ContextTrace.from_items(
        trace_id="trace_budget",
        policy=policy,
        selected_items=(selected,),
        dropped_items=(dropped,),
    )

    assert trace.used_tokens == 4
    assert trace.remaining_tokens == 10
    assert trace.dropped_item_ids == ("tool_1",)
    assert trace.selection_reasons["memory_1"] == "relevant_memory"
    assert trace.selection_reasons["tool_1"] == "low_priority_evicted"


def test_context_contract_exports_are_explicit_and_do_not_create_query_runtime() -> None:
    import zuno.services.application.context.contracts as contracts

    assert "GraphRAGQueryService" not in contracts.__all__
    assert "GraphRAGProjectSnapshot" not in contracts.__all__
    assert {
        "AgentExecutionContext",
        "ModelContextPacket",
        "TokenBudgetPolicy",
        "ContextTrace",
        "ContextItem",
        "ContextSource",
        "ContextSelectionReason",
    }.issubset(set(contracts.__all__))
