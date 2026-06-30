from __future__ import annotations


def test_memory_taxonomy_defines_read_write_manage_boundaries() -> None:
    from zuno.memory.engine import MEMORY_TAXONOMY

    assert set(MEMORY_TAXONOMY) == {
        "raw_event_log",
        "working_memory",
        "recent_window",
        "task_summary",
        "episodic_memory",
        "semantic_memory",
        "procedural_memory",
        "graph_memory_candidate",
        "model_context_pack",
    }

    assert MEMORY_TAXONOMY["raw_event_log"].storage_target == "event_log"
    assert MEMORY_TAXONOMY["raw_event_log"].can_enter_context is False
    assert MEMORY_TAXONOMY["task_summary"].can_enter_context is True
    assert MEMORY_TAXONOMY["semantic_memory"].requires_review is True
    assert MEMORY_TAXONOMY["graph_memory_candidate"].storage_target == "review_queue"
    assert MEMORY_TAXONOMY["model_context_pack"].storage_target == "rendered_context"

    for entry in MEMORY_TAXONOMY.values():
        payload = entry.to_dict()
        assert payload["category"] == entry.category
        assert payload["source_binding"] == "trace_id/task_id/source_event_ids"


def test_memory_engine_runs_append_summarize_review_retrieve_and_render_flow() -> None:
    from zuno.memory.contracts import MemoryReviewStatus, MemoryScope
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy

    scope = MemoryScope(user_id="u_1", agent_id="agent_1", project_id="workspace_1", thread_id="thread_1")
    engine = MemoryEngine()

    event = engine.append_event(
        scope=scope,
        event_id="trace_1:turn",
        event_type="agent_turn",
        payload={"task": "review contract", "durable_facts": ["User prefers concise status updates."]},
        trace_id="trace_1",
        task_id="task_1",
    )
    summary = engine.summarize_task(
        scope=scope,
        summary_id="summary_1",
        content="Reviewed the supplier contract payment terms.",
        source_event_ids=(event.event_id,),
        token_count=9,
    )
    candidates = engine.extract_memory_candidates(
        scope=scope,
        source_event=event,
        retention_policy=RetentionPolicy(ttl_days=180),
    )
    decision = engine.review_memory_candidate(
        candidates[0],
        status=MemoryReviewStatus.APPROVED,
        reviewer_id="reviewer_1",
        reason="explicit durable user preference",
    )
    retrieved = engine.retrieve_memory(scope=scope, query="concise", limit=5)
    context_pack = engine.render_context_pack(
        scope=scope,
        task_id="task_1",
        trace_id="trace_1",
        query="concise contract status",
        budget_tokens=256,
    )

    assert event.metadata["trace_id"] == "trace_1"
    assert event.metadata["task_id"] == "task_1"
    assert engine.build_recent_window(scope=scope, limit=1) == (event,)
    assert summary.source_event_ids == (event.event_id,)
    assert candidates[0].requires_review is True
    assert decision.status is MemoryReviewStatus.APPROVED
    assert retrieved[0].review_status is MemoryReviewStatus.APPROVED
    assert retrieved[0].source_event_ids == (event.event_id,)

    item_sources = {item["source"] for item in context_pack["items"]}
    assert {"recent_window", "task_summary", "semantic_memory"}.issubset(item_sources)
    assert context_pack["trace"]["trace_id"] == "trace_1"
    assert context_pack["trace"]["task_id"] == "task_1"
    assert context_pack["trace"]["source_event_ids_by_item"]["memory:semantic_0"] == [event.event_id]
    assert context_pack["context_policy"]["budget_tokens"] == 256


def test_memory_engine_blocks_sensitive_candidates_and_exposes_eval_policy() -> None:
    from zuno.memory.contracts import MemoryScope
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy

    scope = MemoryScope(user_id="u_1", agent_id="agent_1", project_id="workspace_1", thread_id="thread_1")
    engine = MemoryEngine()
    event = engine.append_event(
        scope=scope,
        event_id="trace_sensitive:turn",
        event_type="agent_turn",
        payload={"durable_facts": ["User passport number is 123456789."]},
        trace_id="trace_sensitive",
        task_id="task_sensitive",
        sensitivity_tags=("pii",),
    )

    candidates = engine.extract_memory_candidates(
        scope=scope,
        source_event=event,
        retention_policy=RetentionPolicy(ttl_days=365),
    )
    eval_policy = engine.memory_eval_policy.to_dict()

    assert candidates == ()
    assert eval_policy["metrics"] == [
        "relevance",
        "over_retention",
        "redaction",
        "stale_suppression",
        "conflict_detection",
    ]
    assert eval_policy["sensitive_tags_blocked"] == ["credential", "pii", "secret"]
