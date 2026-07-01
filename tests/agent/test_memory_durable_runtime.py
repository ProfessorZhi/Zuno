from __future__ import annotations


def _scope(thread_id: str = "thread_memory"):
    from zuno.memory.contracts import MemoryScope

    return MemoryScope(
        user_id="user_memory",
        agent_id="agent_memory",
        project_id="workspace_memory",
        thread_id=thread_id,
    )


def test_durable_memory_store_snapshot_round_trips_cross_task_memory() -> None:
    from zuno.memory.contracts import MemoryReviewStatus
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy
    from zuno.memory.store import DurableMemoryStore

    scope = _scope()
    engine = MemoryEngine(store=DurableMemoryStore())

    first_event = engine.append_event(
        scope=scope,
        event_id="evt_task_1",
        event_type="agent_turn",
        payload={
            "task": "contract review",
            "durable_facts": ["User wants concise contract risk status."],
        },
        trace_id="trace_task_1",
        task_id="task_1",
    )
    second_event = engine.append_event(
        scope=scope,
        event_id="evt_task_2",
        event_type="agent_turn",
        payload={
            "task": "resume review",
            "durable_facts": ["User wants resume feedback grouped by business scene."],
        },
        trace_id="trace_task_2",
        task_id="task_2",
    )
    engine.summarize_task(
        scope=scope,
        summary_id="summary_task_1",
        content="Task 1 reviewed contract risk status.",
        source_event_ids=(first_event.event_id,),
        token_count=7,
    )
    candidates = (
        *engine.extract_memory_candidates(
            scope=scope,
            source_event=first_event,
            retention_policy=RetentionPolicy(ttl_days=180),
        ),
        *engine.extract_memory_candidates(
            scope=scope,
            source_event=second_event,
            retention_policy=RetentionPolicy(ttl_days=180),
        ),
    )
    for candidate in candidates:
        engine.review_memory_candidate(
            candidate,
            status=MemoryReviewStatus.APPROVED,
            reviewer_id="reviewer_memory",
            reason="explicit durable preference",
        )

    snapshot = engine.store.export_snapshot()
    restored_engine = MemoryEngine(store=DurableMemoryStore.from_snapshot(snapshot))

    restored = restored_engine.retrieve_memory(scope=scope, query="status", limit=5)
    context_pack = restored_engine.render_context_pack(
        scope=scope,
        task_id="task_3",
        trace_id="trace_task_3",
        query="contract status",
        budget_tokens=512,
    )

    assert snapshot.snapshot_version == "phase07-memory-runtime-v1"
    assert {event.metadata["task_id"] for event in restored_engine.store.raw_events(scope)} == {
        "task_1",
        "task_2",
    }
    assert restored[0].source_event_ids == ("evt_task_1",)
    assert context_pack["trace"]["trace_id"] == "trace_task_3"
    assert context_pack["trace"]["source_event_ids_by_item"]["memory:semantic_0"] == [
        "evt_task_1"
    ]
    assert context_pack["context_policy"]["selection_reasons_by_item"]["memory:semantic_0"] == (
        "approved_semantic_memory_query_match"
    )
    assert "memory_candidate_approved" in {
        entry["action"] for entry in restored_engine.store.governance_ledger(scope)
    }


def test_database_memory_store_persists_raw_events_summaries_and_approved_memories_across_engine_instances() -> None:
    from sqlalchemy.pool import StaticPool
    from sqlmodel import SQLModel, Session, create_engine

    from zuno.memory.contracts import MemoryReviewStatus
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy
    from zuno.memory.store import DatabaseMemoryStore
    from zuno.platform.database.models.memory_runtime import (
        MemoryCandidateTable,
        MemoryGovernanceLedgerTable,
        MemoryRawEventTable,
        MemoryReviewDecisionTable,
        MemoryTaskSummaryTable,
    )

    sql_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(sql_engine)

    def session_factory() -> Session:
        return Session(sql_engine)

    scope = _scope("thread_db_memory")
    writer = MemoryEngine(store=DatabaseMemoryStore(session_factory=session_factory))
    event = writer.append_event(
        scope=scope,
        event_id="evt_db_task_1",
        event_type="agent_turn",
        payload={
            "task": "database backed memory",
            "durable_facts": ["User wants DB-backed memory evidence."],
        },
        trace_id="trace_db_1",
        task_id="task_db_1",
    )
    writer.summarize_task(
        scope=scope,
        summary_id="summary_db_task_1",
        content="Stored DB-backed memory evidence.",
        source_event_ids=(event.event_id,),
        token_count=5,
    )
    candidate = writer.extract_memory_candidates(
        scope=scope,
        source_event=event,
        retention_policy=RetentionPolicy(ttl_days=90),
    )[0]
    writer.review_memory_candidate(
        candidate,
        status=MemoryReviewStatus.APPROVED,
        reviewer_id="reviewer_db",
        reason="approved for DB runtime test",
    )

    reader = MemoryEngine(store=DatabaseMemoryStore(session_factory=session_factory))
    retrieved = reader.retrieve_memory(scope=scope, query="DB-backed", limit=5)
    context_pack = reader.render_context_pack(
        scope=scope,
        task_id="task_db_2",
        trace_id="trace_db_2",
        query="memory evidence",
        budget_tokens=256,
    )

    assert {table.__tablename__ for table in [
        MemoryRawEventTable,
        MemoryTaskSummaryTable,
        MemoryCandidateTable,
        MemoryReviewDecisionTable,
        MemoryGovernanceLedgerTable,
    ]}.issubset(SQLModel.metadata.tables)
    assert reader.store.raw_events(scope)[0].metadata["trace_id"] == "trace_db_1"
    assert reader.store.task_summaries(scope)[0].source_event_ids == ("evt_db_task_1",)
    assert retrieved[0].review_status is MemoryReviewStatus.APPROVED
    assert retrieved[0].source_event_ids == ("evt_db_task_1",)
    assert context_pack["trace"]["source_event_ids_by_item"]["memory:semantic_0"] == [
        "evt_db_task_1"
    ]
    assert "memory_candidate_approved" in {
        entry["action"] for entry in reader.store.governance_ledger(scope)
    }


def test_memory_governance_blocks_sensitive_candidates_and_records_exclusion_reasons() -> None:
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy
    from zuno.memory.store import DurableMemoryStore

    scope = _scope()
    engine = MemoryEngine(store=DurableMemoryStore())
    sensitive_event = engine.append_event(
        scope=scope,
        event_id="evt_sensitive",
        event_type="agent_turn",
        payload={"durable_facts": ["User API key is sk-test-secret."]},
        trace_id="trace_sensitive",
        task_id="task_sensitive",
        sensitivity_tags=("secret",),
    )

    candidates = engine.extract_memory_candidates(
        scope=scope,
        source_event=sensitive_event,
        retention_policy=RetentionPolicy(ttl_days=365),
    )
    context_pack = engine.render_context_pack(
        scope=scope,
        task_id="task_after_sensitive",
        trace_id="trace_after_sensitive",
        query="api key",
        budget_tokens=128,
    )

    assert candidates == ()
    assert context_pack["context_policy"]["excluded_items"][-1] == {
        "item_id": "event:evt_sensitive",
        "reason": "sensitive_candidate_blocked",
        "source_event_ids": ["evt_sensitive"],
    }
    assert engine.store.governance_ledger(scope)[-1]["action"] == "sensitive_candidate_blocked"


def test_memory_runtime_promotes_decays_and_consolidates_with_source_events() -> None:
    from zuno.memory.contracts import ExternalKnowledgeRecord
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy
    from zuno.memory.store import DurableMemoryStore

    scope = _scope()
    engine = MemoryEngine(store=DurableMemoryStore())
    promoted = engine.promote_external_knowledge(
        ExternalKnowledgeRecord(
            record_id="kb_clause_1",
            scope=scope,
            content="Supplier contract renews unless cancelled 30 days before term end.",
            source_uri="graphrag://contracts/doc/1",
            citation_ids=("citation_clause_1",),
        ),
        candidate_id="memory_clause_1",
        retention_policy=RetentionPolicy(ttl_days=30),
        reviewer_id="reviewer_memory",
        reason="user confirmed clause should persist",
        auto_approve=True,
    )
    event = engine.append_event(
        scope=scope,
        event_id="evt_scene_preference",
        event_type="agent_turn",
        payload={"durable_facts": ["User prefers project notes grouped by enterprise scene."]},
        trace_id="trace_scene",
        task_id="task_scene",
    )
    scene_candidate = engine.extract_memory_candidates(
        scope=scope,
        source_event=event,
        retention_policy=RetentionPolicy(ttl_days=180),
    )[0]
    approved_scene = engine.review_memory_candidate(
        scene_candidate,
        status="approved",
        reviewer_id="reviewer_memory",
        reason="explicit preference",
    )
    decayed = engine.apply_decay(scope=scope, current_age_days_by_candidate={"memory_clause_1": 45})
    consolidated = engine.consolidate_memories(
        scope=scope,
        candidate_ids=("memory_clause_1", scene_candidate.candidate_id),
        consolidated_id="memory_consolidated_preferences",
        content="User wants persistent contract clauses and enterprise-scene project notes in future work.",
        reviewer_id="reviewer_memory",
        reason="merge approved durable preferences",
        retention_policy=RetentionPolicy(ttl_days=365),
    )

    assert promoted.review_status.value == "approved"
    assert promoted.source_event_ids == ("kb_clause_1",)
    assert approved_scene.status.value == "approved"
    assert decayed[0].candidate_id == "memory_clause_1"
    assert decayed[0].metadata["memory_state"] == "decayed"
    assert consolidated.review_status.value == "approved"
    assert consolidated.requires_review is False
    assert consolidated.source_event_ids == ("kb_clause_1", "evt_scene_preference")
    assert consolidated.metadata["consolidated_from"] == [
        "memory_clause_1",
        scene_candidate.candidate_id,
    ]
