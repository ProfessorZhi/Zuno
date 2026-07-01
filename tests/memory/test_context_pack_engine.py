from __future__ import annotations


def _scope():
    from zuno.memory.contracts import MemoryScope

    return MemoryScope(
        user_id="user_phase05",
        agent_id="agent_phase05",
        project_id="workspace_phase05",
        thread_id="thread_phase05",
    )


def test_context_pack_builder_outputs_contract_and_compression_layers() -> None:
    from zuno.memory.contracts import MemoryCandidate, MemoryLayer, MemoryReviewStatus
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy

    engine = MemoryEngine()
    scope = _scope()
    event = engine.append_event(
        scope=scope,
        event_id="evt_phase05_goal",
        event_type="agent_turn",
        payload={
            "task": "Review renewal policy",
            "decisions": ["Use standard retrieval for single document fact checks."],
            "constraints": ["No external services."],
            "entities": ["ks_contracts", "doc_renewal"],
            "open_issues": ["Need cited renewal evidence."],
            "tool_results": ["retrieval returned cited evidence"],
            "durable_facts": ["User wants contract findings grouped by risk."],
            "safety_notes": ["Do not include secret memory."],
        },
        trace_id="trace_phase05_goal",
        task_id="task_phase05_goal",
    )
    engine.summarize_task(
        scope=scope,
        summary_id="summary_phase05_goal",
        content="Prior task checked renewal policy and left citation follow-up open.",
        source_event_ids=(event.event_id,),
        token_count=12,
    )
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="approved_context",
            scope=scope,
            layer=MemoryLayer.SEMANTIC,
            content="Contract findings should be grouped by risk.",
            confidence=0.91,
            source_event_ids=(event.event_id,),
            dedupe_key="semantic:phase05:risk-grouping",
            retention_policy=RetentionPolicy(ttl_days=180),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
            metadata={"memory_category": "semantic_memory"},
        )
    )

    result = engine.build_context_pack(
        scope=scope,
        context_pack_id="ctx_phase05",
        user_goal="Answer renewal question with citations",
        task_state={"phase": "PHASE05", "status": "active"},
        selected_evidence=[
            {
                "evidence_id": "ev_renewal",
                "content": "Renewal notice is 30 days.",
                "source_event_id": event.event_id,
                "citation_ref": "doc_renewal::block_main",
            }
        ],
        allowed_capabilities=["knowledge_retrieval"],
        safety_policy={"sensitive_exclusion": "enabled"},
        output_contract={"format": "cited_answer"},
        budget_tokens=256,
        task_id="task_phase05_context",
        trace_id="trace_phase05_context",
        high_risk=True,
    )

    context_pack = result["context_pack"]
    compression = result["compression"]

    assert context_pack["context_pack_id"] == "ctx_phase05"
    assert context_pack["user_goal"] == "Answer renewal question with citations"
    assert context_pack["selected_memory_refs"] == ["memory:approved_context"]
    assert context_pack["selected_evidence_refs"] == ["ev_renewal"]
    assert context_pack["allowed_capabilities"] == ["knowledge_retrieval"]
    assert context_pack["safety_policy"]["sensitive_exclusion"] == "enabled"
    assert compression["structured_fields"]["user_goal"] == "Answer renewal question with citations"
    assert "Use standard retrieval" in compression["structured_fields"]["decisions"][0]
    assert compression["hierarchical_summary"]["turn_summary"]
    assert compression["hierarchical_summary"]["task_summary"]
    assert compression["hierarchical_summary"]["session_summary"]
    assert compression["hierarchical_summary"]["workspace_or_project_summary"]
    assert compression["evidence_bound_summary"]["summary"]
    assert compression["evidence_bound_summary"]["evidence_refs"] == ["ev_renewal"]
    assert compression["evidence_bound_summary"]["source_event_ids"] == [event.event_id]
    assert compression["budget_policy"]["budget_tokens"] == 256


def test_high_risk_context_pack_requires_evidence_or_source_binding() -> None:
    from zuno.memory.engine import MemoryEngine

    engine = MemoryEngine()

    try:
        engine.build_context_pack(
            scope=_scope(),
            context_pack_id="ctx_no_evidence",
            user_goal="Produce a high risk compliance conclusion",
            task_state={},
            selected_evidence=[],
            allowed_capabilities=[],
            safety_policy={},
            output_contract={},
            budget_tokens=64,
            task_id="task_no_evidence",
            trace_id="trace_no_evidence",
            high_risk=True,
        )
    except ValueError as err:
        assert "high-risk summary requires source event, artifact, or evidence binding" in str(err)
    else:
        raise AssertionError("high-risk context pack should require evidence binding")


def test_context_pack_excludes_stale_conflict_revoked_and_sensitive_memories_with_reasons() -> None:
    from zuno.memory.contracts import MemoryCandidate, MemoryLayer, MemoryReviewStatus
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy

    engine = MemoryEngine()
    scope = _scope()
    for candidate_id, content, metadata in [
        ("safe_memory", "Use cited evidence in renewal answers.", {"memory_category": "semantic_memory"}),
        ("stale_memory", "Old renewal policy used 60 days.", {"memory_state": "stale"}),
        ("conflict_memory", "Conflicting renewal policy says 10 days.", {"memory_state": "conflict"}),
        ("revoked_memory", "Revoked user preference.", {"memory_state": "revoked"}),
        ("secret_memory", "API key is sk-test-secret.", {"sensitivity_tags": ["secret"]}),
    ]:
        engine.store.save_memory_candidate(
            MemoryCandidate(
                candidate_id=candidate_id,
                scope=scope,
                layer=MemoryLayer.SEMANTIC,
                content=content,
                confidence=0.9,
                source_event_ids=(f"evt_{candidate_id}",),
                dedupe_key=f"semantic:{candidate_id}",
                retention_policy=RetentionPolicy(ttl_days=180),
                review_status=MemoryReviewStatus.APPROVED,
                requires_review=False,
                metadata=metadata,
            )
        )

    result = engine.build_context_pack(
        scope=scope,
        context_pack_id="ctx_exclusions",
        user_goal="Answer renewal question",
        task_state={},
        selected_evidence=[{"evidence_id": "ev_safe", "source_event_id": "evt_safe"}],
        allowed_capabilities=[],
        safety_policy={},
        output_contract={},
        budget_tokens=256,
        task_id="task_exclusions",
        trace_id="trace_exclusions",
    )

    item_text = repr(result["items"])
    excluded = {
        item["item_id"]: item["reason"]
        for item in result["context_pack"]["safety_policy"]["excluded_items"]
    }

    assert "Use cited evidence" in item_text
    assert "Old renewal policy" not in item_text
    assert "Conflicting renewal" not in item_text
    assert "Revoked user preference" not in item_text
    assert "sk-test-secret" not in item_text
    assert excluded["memory:stale_memory"] == "stale_memory_excluded"
    assert excluded["memory:conflict_memory"] == "conflict_memory_excluded"
    assert excluded["memory:revoked_memory"] == "revoked_memory_excluded"
    assert excluded["memory:secret_memory"] == "sensitive_memory_excluded"


def test_reflexion_lesson_candidate_enters_review_path_not_long_term_memory() -> None:
    from zuno.agent.contracts import ReflexionLesson
    from zuno.memory.contracts import MemoryReviewStatus
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy

    engine = MemoryEngine()
    scope = _scope()
    lesson = ReflexionLesson(
        lesson_id="lesson_phase05",
        task_type="contract_review",
        failure_type="low_citation_coverage",
        root_cause="Answer finalized before evidence coverage was checked.",
        lesson="Run citation coverage check before final answer.",
        recommended_fix="Trigger replan when citation coverage is below threshold.",
        trigger_condition="citation_coverage < 0.8",
        evidence_refs=["evt_failed_answer"],
    )

    candidate = engine.submit_reflexion_lesson_candidate(
        scope=scope,
        lesson=lesson,
        retention_policy=RetentionPolicy(ttl_days=365),
    )
    context_pack = engine.render_context_pack(
        scope=scope,
        task_id="task_reflexion",
        trace_id="trace_reflexion",
        query="citation coverage lesson",
        budget_tokens=256,
    )

    assert candidate.review_status is MemoryReviewStatus.PENDING
    assert candidate.requires_review is True
    assert candidate.source_event_ids == ("evt_failed_answer",)
    assert engine.store.memory_candidates(scope)[0].candidate_id == "reflexion:lesson_phase05"
    assert "Run citation coverage check" not in repr(context_pack["items"])
    assert context_pack["context_policy"]["excluded_items"][-1] == {
        "item_id": "memory:reflexion:lesson_phase05",
        "reason": "pending_review",
        "source_event_ids": ["evt_failed_answer"],
    }
