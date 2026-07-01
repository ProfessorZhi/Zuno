from __future__ import annotations


PHASE02_CONTRACT_NAMES = {
    "AgentRun",
    "ContextPack",
    "RetrievalProfile",
    "RetrievalDecision",
    "EvidenceBundle",
    "CitationLineage",
    "FileInputFormat",
    "SourceObject",
    "BinarySourceObject",
    "ObjectStoreRef",
    "ObjectStoreResult",
    "ParserCapabilityStatus",
    "ParserDependencyProbe",
    "ParserWorkerSpec",
    "ParserWorkerResult",
    "ParseJobStatus",
    "ParseAttempt",
    "IndexWorkerSpec",
    "IndexWorkerResult",
    "QueueMessage",
    "QueueBackendResult",
    "OutboxEvent",
    "DeadLetterRecord",
    "ReconcilerFinding",
    "OCRVLMEnrichmentResult",
    "KnowledgeSpaceConfig",
    "FileIngestionStatus",
    "ChangeImpactPreview",
    "CapabilityCard",
    "CapabilityPolicy",
    "CapabilityRiskProfile",
    "CapabilityAuditEvent",
    "SkillCard",
    "ToolCard",
    "PlanStep",
    "PlanState",
    "StrategySelectorOutput",
    "SelectedSkill",
    "CapabilityPlan",
    "RetrievalPlan",
    "ReflectionVerdict",
    "ReplanDecision",
    "ReflexionLesson",
    "PlannerOutput",
    "TraceRecord",
    "TraceMetric",
    "CostMetric",
    "ConversationRunMetrics",
    "StageMetrics",
    "IngestionMetrics",
    "RetrievalMetrics",
    "PlanningMetrics",
    "SecurityMetrics",
    "EvalComparisonReport",
    "ScenarioSummary",
    "TraceSummary",
}


def _dump(model):
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model.dict()


def test_phase02_shared_contract_index_has_unique_owners_and_consumers() -> None:
    from zuno.agent.contracts import PHASE02_SHARED_CONTRACTS

    assert set(PHASE02_SHARED_CONTRACTS) == PHASE02_CONTRACT_NAMES
    for name, entry in PHASE02_SHARED_CONTRACTS.items():
        assert entry.owner
        assert entry.path == "src/backend/zuno/agent/contracts.py"
        assert entry.fields
        assert entry.consuming_phases
        assert entry.serialization in {"pydantic", "enum", "dataclass-facade"}

    assert PHASE02_SHARED_CONTRACTS["QueueMessage"].owner == "Workstream A"
    assert "PHASE03" in PHASE02_SHARED_CONTRACTS["QueueMessage"].consuming_phases
    assert PHASE02_SHARED_CONTRACTS["KnowledgeSpaceConfig"].owner == "Coordinator"
    assert "PHASE11" in PHASE02_SHARED_CONTRACTS["KnowledgeSpaceConfig"].consuming_phases
    assert PHASE02_SHARED_CONTRACTS["PlanStep"].owner == "Workstream F"
    assert "PHASE10" in PHASE02_SHARED_CONTRACTS["PlanStep"].consuming_phases


def test_phase02_shared_contracts_serialize_defaults_and_boundaries() -> None:
    from zuno.agent.contracts import (
        CapabilityPolicy,
        CapabilityPlan,
        ConversationRunMetrics,
        EvalComparisonReport,
        KnowledgeSpaceConfig,
        ParserDependencyProbe,
        PlannerOutput,
        PlanState,
        PlanStep,
        QueueMessage,
        RetrievalDecision,
        RetrievalPlan,
        RetrievalProfile,
        ScenarioSummary,
        SelectedSkill,
        SkillCard,
        StageMetrics,
        StrategySelectorOutput,
        TraceRecord,
    )

    assert {item.value for item in RetrievalProfile} == {
        "standard",
        "deep",
        "deep_without_graph",
    }

    message = QueueMessage(
        message_id="msg_parse_1",
        topic="parse_requested",
        payload={"parse_job_id": "parse_1"},
        idempotency_key="parse:workspace:sha",
    )
    assert _dump(message)["status"] == "queued"
    assert _dump(message)["attempt"] == 0

    probe = ParserDependencyProbe(
        provider_id="rabbitmq",
        capability="queue",
        status="target_blocked",
        blocked_reason="RabbitMQ is not configured for local baseline.",
    )
    assert _dump(probe)["status"] == "target_blocked"

    decision = RetrievalDecision(
        requested_profile=RetrievalProfile.DEEP,
        effective_profile=RetrievalProfile.DEEP_WITHOUT_GRAPH,
        fallback_reason="graph_index_missing",
        retrievers_used=["bm25", "vector", "light_fusion"],
        evidence_count=2,
        citation_coverage=0.5,
    )
    assert _dump(decision)["requested_profile"] == "deep"
    assert _dump(decision)["effective_profile"] == "deep_without_graph"

    knowledge_config = KnowledgeSpaceConfig(
        name="Contracts",
        workspace_id="workspace_contracts",
        index_capabilities={"basic_index": True, "graph_index": False},
        retrieval_defaults={"default_profile": "standard"},
    )
    assert _dump(knowledge_config)["retrieval_defaults"] == {"default_profile": "standard"}
    assert "basic" not in str(_dump(knowledge_config)["retrieval_defaults"])

    skill = SkillCard(
        skill_id="contract_review",
        skill_version="v1",
        when_to_use="Review contract obligations.",
        task_type="contract_review",
        recommended_retrieval_profile=RetrievalProfile.DEEP,
        required_evidence=["citation_lineage"],
        allowed_tools=["knowledge.search"],
        memory_scopes=["session"],
        output_contract={"artifact": "contract_review_report"},
        safety_policy="citation_required",
        eval_rubric={"citation_coverage": 1.0},
        max_steps=4,
        reflection_policy="required",
    )
    assert _dump(skill)["recommended_retrieval_profile"] == "deep"
    assert _dump(skill)["allowed_tools"] == ["knowledge.search"]

    policy = CapabilityPolicy(
        capability_id="knowledge.contracts",
        capability_type="knowledge",
        workspace_scope="workspace_contracts",
        required_roles=["member"],
        approval_required=False,
        side_effect_level="read",
        network_policy="deny",
        credential_policy="none",
        data_access_policy="workspace_acl",
        audit_policy="trace",
    )
    assert _dump(policy)["data_access_policy"] == "workspace_acl"

    stage = StageMetrics(stage_name="retrieval", latency_ms=12.5, trace_event_ids=["evt_1"])
    assert _dump(stage)["stage_name"] == "retrieval"
    assert _dump(stage)["error_count"] == 0

    selected = SelectedSkill(
        skill_id="contract_review",
        selection_mode="automatic",
        allowed_tools=["knowledge.contracts"],
        required_evidence=["citation_lineage"],
        retrieval_profile=RetrievalProfile.DEEP,
    )
    capability_plan = CapabilityPlan(
        allowed_capabilities=["knowledge.contracts"],
        allowed_tools=[],
        executed_tools=[],
    )
    retrieval_plan = RetrievalPlan(
        requested_profile=RetrievalProfile.DEEP,
        effective_profile=RetrievalProfile.DEEP_WITHOUT_GRAPH,
        retrievers_used=["bm25", "vector"],
        fallback_reason="graph_index_missing",
        evidence_requirements=["citation_lineage"],
    )
    planner_output = PlannerOutput(
        task_id="task_plan",
        trace_id="trace_plan",
        strategy=StrategySelectorOutput(
            strategy="plan_execute_with_replan",
            reason="multi_hop_evidence_needed",
            selected_skill="contract_review",
            retrieval_profile=RetrievalProfile.DEEP,
        ),
        selected_skill=selected,
        capability_plan=capability_plan,
        retrieval_plan=retrieval_plan,
        plan_state=PlanState(
            plan_id="plan_1",
            status="planned",
            steps=[PlanStep(step_id="step_1", goal="Retrieve evidence.", action_type="retrieval")],
            current_step_id="step_1",
        ),
        trace_events=[
            TraceRecord(
                event_id="evt_strategy",
                task_id="task_plan",
                trace_id="trace_plan",
                event_type="strategy_selected",
                payload={"strategy": "plan_execute_with_replan"},
            )
        ],
    )
    assert _dump(planner_output)["retrieval_plan"]["effective_profile"] == "deep_without_graph"
    assert _dump(planner_output)["capability_plan"]["executed_tools"] == []

    run = ConversationRunMetrics(
        task_id="task_1",
        session_id="session_1",
        workspace_id="workspace_contracts",
        user_id="user_1",
        selected_knowledge_spaces=["contracts"],
        retrieval_profiles={"contracts": "deep"},
        selected_skill="contract_review",
        strategy="plan_execute_with_replan",
        model_config={"chat": "local-mock"},
    )
    assert _dump(run)["retrieval_profiles"] == {"contracts": "deep"}

    report = EvalComparisonReport(
        baseline_label="agentic_graphrag",
        quality_delta=0.12,
        latency_delta=18.0,
        cost_delta=0.01,
        citation_delta=0.2,
        security_delta=0.0,
    )
    assert _dump(report)["baseline_label"] == "agentic_graphrag"

    scenario = ScenarioSummary(
        user_question="Which renewal notice applies?",
        selected_knowledge_spaces=["contracts"],
        retrieval_profiles={"contracts": "deep"},
        selected_skill="contract_review",
        plan_summary="Retrieve contract clauses and verify citations.",
        retrieval_decision=decision,
        reflection_verdict={"decision": "continue"},
        replan_event={"trigger": "citation_coverage_low"},
        artifact_content_excerpt="Renewal notice requires 30 days...",
        citations=[{"citation_id": "c1", "document_id": "doc1"}],
        metrics_summary={"latency_ms": 50},
        feedback_result={"stored": True},
        restart_rehydrate_result={"artifact": "available"},
        file_status_timeline=["uploaded", "queued", "parsing", "parsed", "indexing", "indexed"],
        parser_dependency_probe=probe,
        blocked_reason=None,
        worker_event={"topic": "parse_requested", "ack": True},
        index_status="indexed",
        citation_lineage=[{"document_version_id": "docv1", "block_id": "b1"}],
    )
    assert _dump(scenario)["retrieval_decision"]["effective_profile"] == "deep_without_graph"
    assert _dump(scenario)["file_status_timeline"][-1] == "indexed"
