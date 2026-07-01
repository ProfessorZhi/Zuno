from __future__ import annotations


def test_database_memory_store_privacy_delete_removes_content_and_keeps_redacted_ledger() -> None:
    from sqlalchemy.pool import StaticPool
    from sqlmodel import SQLModel, Session, create_engine

    from zuno.memory.engine import MemoryEngine
    from zuno.memory.store import DatabaseMemoryStore
    from zuno.services.memory.layers import (
        MemoryCandidate,
        MemoryLayer,
        MemoryReviewStatus,
        MemoryScope,
        RetentionPolicy,
    )

    sql_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(sql_engine)

    def session_factory() -> Session:
        return Session(sql_engine)

    scope = MemoryScope(user_id="u1", agent_id="a1", project_id="p1", thread_id="t1")
    engine = MemoryEngine(store=DatabaseMemoryStore(session_factory=session_factory))
    event = engine.append_event(
        scope=scope,
        event_id="evt_db_secret",
        event_type="agent_turn",
        payload={"text": "database-secret should be erased"},
        trace_id="trace_db_secret",
        task_id="task_db_secret",
        sensitivity_tags=("secret",),
    )
    engine.summarize_task(
        scope=scope,
        summary_id="summary_db_secret",
        content="database-secret summary should be erased",
        source_event_ids=(event.event_id,),
        token_count=7,
        metadata={"trace_id": "trace_db_secret", "task_id": "task_db_secret"},
    )
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="db_secret_candidate",
            scope=scope,
            layer=MemoryLayer.SEMANTIC,
            content="database-secret durable memory should be erased",
            confidence=0.91,
            source_event_ids=(event.event_id,),
            dedupe_key="semantic:db-secret",
            retention_policy=RetentionPolicy(ttl_days=30),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
        )
    )

    report = engine.privacy_delete_scope(
        scope=scope,
        actor_id="privacy_admin",
        reason="delete database-secret",
    )
    reader = DatabaseMemoryStore(session_factory=session_factory)

    assert report.deleted_counts["raw_events"] == 1
    assert report.deleted_counts["task_summaries"] == 1
    assert report.deleted_counts["memory_candidates"] == 1
    assert reader.raw_events(scope) == ()
    assert reader.task_summaries(scope) == ()
    assert reader.memory_candidates(scope) == ()
    ledger = reader.governance_ledger(scope)
    assert len(ledger) == 1
    assert ledger[0]["action"] == "privacy_delete_applied"
    assert ledger[0]["reason"] == "privacy_delete_request"
    assert ledger[0]["metadata"]["deleted_counts"]["raw_events"] == 1
    assert report.to_dict()["reason"] == "privacy_delete_request"
    assert "database-secret" not in repr(report.to_dict())
    assert "database-secret" not in repr(ledger)
