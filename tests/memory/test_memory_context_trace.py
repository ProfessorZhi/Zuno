from __future__ import annotations

from zuno.memory.contracts import MemoryCandidate, MemoryLayer, MemoryReviewStatus, MemoryScope
from zuno.memory.engine import MemoryEngine
from zuno.memory.policy import RetentionPolicy


def _scope() -> MemoryScope:
    return MemoryScope(
        user_id="user_trace",
        agent_id="unified_runtime",
        project_id="workspace_trace",
        thread_id="thread_trace",
    )


def test_memory_context_trace_records_include_and_exclude_reasons() -> None:
    engine = MemoryEngine()
    scope = _scope()
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="approved_proc",
            scope=scope,
            layer=MemoryLayer.PROCEDURAL,
            content="Prefer replan when citation support is missing.",
            confidence=0.9,
            source_event_ids=("evt_approved",),
            dedupe_key="proc:approved",
            retention_policy=RetentionPolicy(ttl_days=365),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
            metadata={"memory_category": "procedural_memory"},
        )
    )
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="pending_proc",
            scope=scope,
            layer=MemoryLayer.PROCEDURAL,
            content="Pending lesson should not be included.",
            confidence=0.7,
            source_event_ids=("evt_pending",),
            dedupe_key="proc:pending",
            retention_policy=RetentionPolicy(ttl_days=365),
            review_status=MemoryReviewStatus.PENDING,
            requires_review=True,
            metadata={"memory_category": "reflexion_memory_candidate"},
        )
    )

    result = engine.build_context_pack(
        scope=scope,
        context_pack_id="ctx_trace",
        user_goal="Need citation support",
        task_state={},
        selected_evidence=[{"evidence_id": "ev_trace", "source_event_id": "evt_evidence"}],
        allowed_capabilities=[],
        safety_policy={},
        output_contract={},
        budget_tokens=256,
        task_id="task_trace",
        trace_id="trace_trace",
    )

    trace = result["trace"]
    excluded = result["context_pack"]["safety_policy"]["excluded_items"]

    assert result["context_pack"]["selected_memory_refs"] == ["memory:approved_proc"]
    assert trace["selection_reasons_by_item"]["memory:approved_proc"] in {
        "approved_semantic_memory_query_match",
        "approved_memory_fallback_no_query_match",
    }
    assert trace["source_event_ids_by_item"]["memory:approved_proc"] == ["evt_approved"]
    assert excluded[-1]["item_id"] == "memory:pending_proc"
    assert excluded[-1]["reason"] == "pending_review"
