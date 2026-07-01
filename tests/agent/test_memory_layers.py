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


def test_memory_taxonomy_separates_five_agent_memory_layers() -> None:
    from zuno.services.memory.layers import MemoryLayer

    assert MemoryLayer.SHORT_TERM_STATE.value == "short_term_state"
    assert MemoryLayer.WORKING.value == "working_context"
    assert MemoryLayer.SEMANTIC.value == "semantic_memory"
    assert MemoryLayer.EPISODIC.value == "episodic_memory"
    assert MemoryLayer.PROCEDURAL.value == "procedural_memory"
    assert MemoryLayer.EXTERNAL_KNOWLEDGE.value == "external_knowledge"


def test_structured_memory_candidate_requires_review_and_source_events() -> None:
    from zuno.services.memory.layers import (
        MemoryCandidate,
        MemoryLayer,
        MemoryReviewDecision,
        MemoryReviewStatus,
        MemoryScope,
        RetentionPolicy,
    )

    scope = MemoryScope(user_id="u1", agent_id="a1", project_id="p1", thread_id="t1")
    candidate = MemoryCandidate(
        candidate_id="semantic_1",
        scope=scope,
        layer=MemoryLayer.SEMANTIC,
        content="User prefers short status summaries.",
        confidence=0.9,
        source_event_ids=("evt_1",),
        dedupe_key="preference:short-status",
        retention_policy=RetentionPolicy(ttl_days=180),
    )

    assert candidate.review_status is MemoryReviewStatus.PENDING
    assert candidate.requires_review is True

    decision = MemoryReviewDecision.approve(
        candidate=candidate,
        reviewer_id="reviewer_1",
        reason="explicit user preference",
    )

    assert decision.status is MemoryReviewStatus.APPROVED
    assert decision.source_event_ids == ("evt_1",)
    assert decision.to_dict()["candidate_id"] == "semantic_1"


def test_memory_processing_policy_documents_summary_and_extraction_rules() -> None:
    from zuno.services.memory.layers import MemoryProcessingPolicy

    policy = MemoryProcessingPolicy(
        summary_strategy="summary_compression",
        extraction_strategy="structured_extraction",
        review_required=True,
        preserve_raw_event_ids=True,
    )

    payload = policy.to_dict()

    assert payload["summary_strategy"] == "summary_compression"
    assert payload["extraction_strategy"] == "structured_extraction"
    assert payload["review_required"] is True
    assert payload["preserve_raw_event_ids"] is True


def test_semantic_memory_adapter_uses_local_deterministic_fallback_and_scope_filters() -> None:
    from zuno.memory.engine import MemoryEngine
    from zuno.services.memory.layers import (
        MemoryCandidate,
        MemoryLayer,
        MemoryReviewStatus,
        MemoryScope,
        RetentionPolicy,
    )

    engine = MemoryEngine()
    scope = MemoryScope(user_id="u1", agent_id="a1", project_id="p1", thread_id="t1")
    other_scope = MemoryScope(user_id="u2", agent_id="a1", project_id="p1", thread_id="t1")
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="release_memory",
            scope=scope,
            layer=MemoryLayer.SEMANTIC,
            content="Memory release gate evidence must include privacy deletion proof.",
            confidence=0.91,
            source_event_ids=("evt_release",),
            dedupe_key="semantic:release-memory",
            retention_policy=RetentionPolicy(ttl_days=180),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
        )
    )
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="unrelated_memory",
            scope=scope,
            layer=MemoryLayer.SEMANTIC,
            content="The preferred lunch order is noodles.",
            confidence=0.88,
            source_event_ids=("evt_lunch",),
            dedupe_key="semantic:lunch",
            retention_policy=RetentionPolicy(ttl_days=180),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
        )
    )
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="other_user_memory",
            scope=other_scope,
            layer=MemoryLayer.SEMANTIC,
            content="Memory release gate evidence for another user.",
            confidence=0.99,
            source_event_ids=("evt_other_user",),
            dedupe_key="semantic:other-user",
            retention_policy=RetentionPolicy(ttl_days=180),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
        )
    )

    results = engine.search_semantic_memory(
        scope=scope,
        query="release gate privacy evidence",
        limit=5,
    )
    payload = results[0].to_dict()

    assert [result.candidate.candidate_id for result in results] == ["release_memory"]
    assert payload["adapter_id"] == "local_deterministic_semantic_v1"
    assert payload["local_fallback"] is True
    assert payload["vector_ref"].startswith("local-vector:")
    assert payload["score"] > 0


def test_memory_privacy_delete_removes_scoped_content_and_preserves_redacted_audit_report() -> None:
    from zuno.memory.engine import MemoryEngine
    from zuno.services.memory.layers import (
        MemoryCandidate,
        MemoryLayer,
        MemoryReviewStatus,
        MemoryScope,
        RetentionPolicy,
    )

    engine = MemoryEngine()
    scope = MemoryScope(user_id="u1", agent_id="a1", project_id="p1", thread_id="t1")
    event = engine.append_event(
        scope=scope,
        event_id="evt_secret",
        event_type="agent_turn",
        payload={"text": "super-secret token should be deleted"},
        trace_id="trace_secret",
        task_id="task_secret",
        sensitivity_tags=("secret",),
    )
    engine.summarize_task(
        scope=scope,
        summary_id="summary_secret",
        content="super-secret summary should be deleted",
        source_event_ids=(event.event_id,),
        token_count=6,
        metadata={"trace_id": "trace_secret", "task_id": "task_secret"},
    )
    candidate = MemoryCandidate(
        candidate_id="secret_candidate",
        scope=scope,
        layer=MemoryLayer.SEMANTIC,
        content="super-secret durable memory should be deleted",
        confidence=0.9,
        source_event_ids=(event.event_id,),
        dedupe_key="semantic:secret",
        retention_policy=RetentionPolicy(ttl_days=30, allow_privacy_delete=True),
        review_status=MemoryReviewStatus.APPROVED,
        requires_review=False,
    )
    engine.store.save_memory_candidate(candidate)

    report = engine.privacy_delete_scope(
        scope=scope,
        actor_id="privacy_admin",
        reason="delete super-secret token",
    )

    assert report.deleted_counts == {
        "raw_events": 1,
        "task_summaries": 1,
        "memory_candidates": 1,
        "review_decisions": 0,
        "governance_ledger": 2,
    }
    assert engine.store.raw_events(scope) == ()
    assert engine.store.task_summaries(scope) == ()
    assert engine.store.memory_candidates(scope) == ()
    ledger = engine.store.governance_ledger(scope)
    assert len(ledger) == 1
    assert ledger[0]["action"] == "privacy_delete_applied"
    assert ledger[0]["reason"] == "privacy_delete_request"
    assert ledger[0]["metadata"]["deleted_counts"]["raw_events"] == 1
    assert ledger[0]["metadata"]["actor_id"] == "privacy_admin"
    assert report.to_dict()["reason"] == "privacy_delete_request"
    assert "super-secret" not in repr(report.to_dict())
    assert "super-secret" not in repr(ledger)


def test_memory_eval_baseline_reports_release_gate_for_relevance_privacy_and_budget() -> None:
    from zuno.memory.engine import MemoryEngine
    from zuno.services.memory.layers import (
        MemoryCandidate,
        MemoryLayer,
        MemoryReviewStatus,
        MemoryScope,
        RetentionPolicy,
    )

    engine = MemoryEngine()
    scope = MemoryScope(user_id="u1", agent_id="a1", project_id="p1", thread_id="t1")
    event = engine.append_event(
        scope=scope,
        event_id="evt_sensitive",
        event_type="agent_turn",
        payload={"task": "contains raw-secret-token"},
        trace_id="trace_eval",
        task_id="task_eval",
        sensitivity_tags=("secret",),
    )
    engine.summarize_task(
        scope=scope,
        summary_id="summary_sensitive",
        content="raw-secret-token summary must not enter context",
        source_event_ids=(event.event_id,),
        token_count=8,
        metadata={"trace_id": "trace_eval", "task_id": "task_eval"},
    )
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="release_memory",
            scope=scope,
            layer=MemoryLayer.SEMANTIC,
            content="Release gate memory evidence includes privacy-safe context quality.",
            confidence=0.92,
            source_event_ids=("evt_release",),
            dedupe_key="semantic:release-gate",
            retention_policy=RetentionPolicy(ttl_days=180),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
        )
    )
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="pending_secret",
            scope=scope,
            layer=MemoryLayer.SEMANTIC,
            content="raw-secret-token must not enter context",
            confidence=0.95,
            source_event_ids=(event.event_id,),
            dedupe_key="semantic:pending-secret",
            retention_policy=RetentionPolicy(ttl_days=180),
            review_status=MemoryReviewStatus.PENDING,
        )
    )

    result = engine.evaluate_memory_baseline(
        scope=scope,
        query="release gate memory evidence",
        task_id="task_eval",
        trace_id="trace_eval",
        expected_source_event_ids=("evt_release",),
        budget_tokens=256,
    )
    payload = result.to_dict()

    assert result.release_gate_status == "pass"
    assert payload["metrics"]["retrieval_relevance"]["status"] == "pass"
    assert payload["metrics"]["privacy_safety"]["status"] == "pass"
    assert payload["metrics"]["context_compression_quality"]["status"] == "pass"
    assert payload["adapter"]["adapter_id"] == "local_deterministic_semantic_v1"
    assert "raw-secret-token" not in repr(payload["context_pack"]["items"])
    assert payload["context_pack"]["context_policy"]["excluded_items"]
