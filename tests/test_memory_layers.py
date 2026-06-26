def test_memory_layer_store_preserves_raw_events_when_summary_is_written() -> None:
    from zuno.services.memory.layers import (
        InMemoryLayerStore,
        MemoryLayer,
        MemoryScope,
        RawMemoryEvent,
        TaskMemorySummary,
    )

    store = InMemoryLayerStore()
    scope = MemoryScope(user_id="u1", agent_id="a1", project_id="p1", thread_id="t1")
    event = RawMemoryEvent(
        event_id="evt_1",
        scope=scope,
        event_type="user_message",
        payload={"text": "Remember the cancellation clause."},
    )

    store.append_raw_event(event)
    store.save_task_summary(
        TaskMemorySummary(
            summary_id="sum_1",
            scope=scope,
            layer=MemoryLayer.TASK,
            content="User asked about the cancellation clause.",
            source_event_ids=("evt_1",),
            token_count=8,
        )
    )

    assert store.raw_events(scope) == (event,)
    assert store.task_summaries(scope)[0].source_event_ids == ("evt_1",)


def test_memory_candidate_requires_scope_confidence_and_source_events() -> None:
    from zuno.services.memory.layers import (
        MemoryCandidate,
        MemoryLayer,
        MemoryScope,
        RetentionPolicy,
    )

    scope = MemoryScope(user_id="u1", agent_id="a1", project_id="p1", thread_id="t1")
    candidate = MemoryCandidate(
        candidate_id="cand_1",
        scope=scope,
        layer=MemoryLayer.LONG_TERM,
        content="User prefers concise architecture status updates.",
        confidence=0.84,
        source_event_ids=("evt_1", "evt_2"),
        dedupe_key="pref:concise-status",
        retention_policy=RetentionPolicy(ttl_days=180, allow_privacy_delete=True),
    )

    payload = candidate.to_dict()

    assert payload["scope"] == {
        "user_id": "u1",
        "agent_id": "a1",
        "project_id": "p1",
        "thread_id": "t1",
    }
    assert payload["confidence"] == 0.84
    assert payload["source_event_ids"] == ["evt_1", "evt_2"]
    assert payload["retention_policy"]["ttl_days"] == 180
    assert payload["retention_policy"]["allow_privacy_delete"] is True


def test_external_knowledge_requires_explicit_promotion_before_memory_candidate() -> None:
    from zuno.services.memory.layers import (
        ExternalKnowledgeRecord,
        MemoryCandidate,
        MemoryLayer,
        MemoryScope,
        RetentionPolicy,
    )

    scope = MemoryScope(user_id="u1", agent_id="a1", project_id="p1", thread_id="t1")
    knowledge = ExternalKnowledgeRecord(
        record_id="kb_1",
        scope=scope,
        content="Contract clause evidence",
        source_uri="graphrag://contract_review/doc/1",
        citation_ids=("citation_1",),
    )

    assert knowledge.can_promote_to_memory is False

    try:
        MemoryCandidate.from_external_knowledge(
            candidate_id="cand_kb",
            knowledge=knowledge,
            retention_policy=RetentionPolicy(ttl_days=30),
        )
    except ValueError as err:
        assert "explicit promotion" in str(err)
    else:
        raise AssertionError("external knowledge should require explicit promotion")

    promoted = MemoryCandidate.from_external_knowledge(
        candidate_id="cand_kb",
        knowledge=knowledge.mark_for_promotion(reason="user confirmed durable preference"),
        retention_policy=RetentionPolicy(ttl_days=30),
    )

    assert promoted.layer is MemoryLayer.LONG_TERM
    assert promoted.source_event_ids == ("kb_1",)
    assert promoted.metadata["promotion_reason"] == "user confirmed durable preference"


def test_memory_layer_exports_do_not_import_live_memory_client() -> None:
    import zuno.services.memory.layers as layers

    assert "memory_client" not in layers.__dict__
    assert {
        "MemoryLayer",
        "MemoryScope",
        "RawMemoryEvent",
        "TaskMemorySummary",
        "MemoryCandidate",
        "ExternalKnowledgeRecord",
        "RetentionPolicy",
        "InMemoryLayerStore",
    }.issubset(set(layers.__all__))
