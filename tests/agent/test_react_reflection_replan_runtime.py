from __future__ import annotations

from zuno.agent.contracts import EvidenceBundle, RetrievalProfile
from zuno.agent.control_runtime import AgentControlRuntime, RuntimeObservation
from zuno.agent.planning import PlanningRequest, build_default_strategy_selector
from zuno.memory.contracts import MemoryReviewStatus, MemoryScope
from zuno.memory.engine import MemoryEngine
from zuno.memory.policy import RetentionPolicy


def _planner_output(
    *,
    task_id: str,
    trace_id: str,
    goal: str,
    requested_profile: RetrievalProfile = RetrievalProfile.STANDARD,
    graph_available: bool = True,
    capabilities: tuple[str, ...] = ("knowledge.research_corpus",),
    roles: tuple[str, ...] = ("analyst",),
    security_summary: dict[str, str] | None = None,
):
    return build_default_strategy_selector().select(
        PlanningRequest(
            task_id=task_id,
            trace_id=trace_id,
            workspace_id="workspace_alpha",
            user_goal=goal,
            requested_retrieval_profile=requested_profile,
            graph_available=graph_available,
            available_capability_ids=capabilities,
            user_roles=roles,
            security_summary=security_summary or {},
        )
    )


def _event_types(result) -> list[str]:
    return [event.event_type for event in result.trace_events]


def test_replan_changes_subsequent_retrieval_trajectory_when_evidence_low() -> None:
    planner_output = _planner_output(
        task_id="task_replan_low_evidence",
        trace_id="trace_replan_low_evidence",
        goal="Compare evidence across documents and synthesize conflicts.",
        requested_profile=RetrievalProfile.DEEP,
    )

    result = AgentControlRuntime().run(
        planner_output,
        observations=[
            RuntimeObservation(
                step_id="step_1",
                status="completed",
                evidence=EvidenceBundle(evidence_count=0, citation_coverage=0.0),
                output="No matching evidence found.",
            )
        ],
    )

    assert result.finalized is False
    assert result.final_answer is None
    assert result.reflection_verdict.decision == "replan"
    assert result.replan_decision.trigger == "retrieval_empty"
    assert result.plan_state.status == "replanned"
    assert result.plan_state.current_step_id == "replan_step_1"
    assert result.plan_state.steps[0].action_type == "retrieve_deeper_evidence"
    assert result.plan_state.steps[0].budget["trajectory_changed"] is True
    assert result.plan_state.steps[0].budget["retrievers_used"] == [
        "bm25",
        "vector",
        "staged_requery",
        "graph_expand",
        "rerank",
    ]
    assert "replan_created" in _event_types(result)


def test_reflection_failed_blocks_final_answer_until_evidence_is_enough() -> None:
    planner_output = _planner_output(
        task_id="task_reflection_blocks",
        trace_id="trace_reflection_blocks",
        goal="Write a formal research report with citations.",
        requested_profile=RetrievalProfile.DEEP,
    )

    result = AgentControlRuntime().run(
        planner_output,
        observations=[
            RuntimeObservation(
                step_id="step_2",
                status="completed",
                evidence=EvidenceBundle(
                    evidence_ids=["ev_partial"],
                    citation_ids=[],
                    evidence_count=1,
                    citation_coverage=0.25,
                    unsupported_claim_inputs=["unsupported market claim"],
                ),
                output="Draft answer with unsupported market claim.",
            )
        ],
    )

    assert result.finalized is False
    assert result.final_answer is None
    assert result.reflection_verdict.decision == "replan"
    assert result.reflection_verdict.unsupported_claims == ["unsupported market claim"]
    assert result.replan_decision.trigger == "citation_coverage_low"
    assert "answer_finalized" not in _event_types(result)


def test_successful_react_run_finalizes_answer_with_trace_and_tool_boundary() -> None:
    planner_output = _planner_output(
        task_id="task_react_success",
        trace_id="trace_react_success",
        goal="Search the web for sources and summarize the result.",
        requested_profile=RetrievalProfile.DEEP,
        capabilities=("knowledge.research_corpus", "tool.web.search"),
    )

    result = AgentControlRuntime().run(
        planner_output,
        observations=[
            RuntimeObservation(step_id="step_1", status="completed", tool_id="tool.web.search"),
            RuntimeObservation(
                step_id="step_2",
                status="completed",
                tool_id="tool.web.search",
                evidence=EvidenceBundle(
                    evidence_ids=["ev_source"],
                    citation_ids=["cite_source"],
                    evidence_count=1,
                    citation_coverage=1.0,
                ),
                output="Observed source says the deployment target remains replaceable.",
            ),
            RuntimeObservation(
                step_id="step_3",
                status="completed",
                evidence=EvidenceBundle(
                    evidence_ids=["ev_source"],
                    citation_ids=["cite_source"],
                    evidence_count=1,
                    citation_coverage=1.0,
                ),
                output="Deployment target remains replaceable. [cite_source]",
            ),
        ],
    )

    assert result.finalized is True
    assert result.final_answer == "Deployment target remains replaceable. [cite_source]"
    assert result.reflection_verdict.decision == "finish"
    assert result.capability_plan.executed_tools == ["tool.web.search"]
    assert _event_types(result)[-1] == "answer_finalized"


def test_tool_failed_runtime_replans_without_final_answer() -> None:
    planner_output = _planner_output(
        task_id="task_tool_failed",
        trace_id="trace_tool_failed",
        goal="Search the web for sources and summarize the result.",
        requested_profile=RetrievalProfile.DEEP,
        capabilities=("knowledge.research_corpus", "tool.web.search"),
    )

    result = AgentControlRuntime().run(
        planner_output,
        observations=[
            RuntimeObservation(
                step_id="step_2",
                status="failed",
                failure_reason="tool_failed",
                tool_id="tool.web.search",
                output="Governed tool call failed before observation.",
            )
        ],
    )

    assert result.finalized is False
    assert result.final_answer is None
    assert result.reflection_verdict.decision == "replan"
    assert result.replan_decision.trigger == "tool_failed"
    assert result.plan_state.current_step_id == "replan_step_1"
    assert "answer_finalized" not in _event_types(result)
    assert "replan_created" in _event_types(result)


def test_reflexion_candidate_enters_memory_review_path_after_failed_verification() -> None:
    planner_output = _planner_output(
        task_id="task_reflexion_failure",
        trace_id="trace_reflexion_failure",
        goal="Fix the failing pytest and remember the lesson for next time.",
        capabilities=("tool.filesystem.read",),
    )
    engine = MemoryEngine()
    scope = MemoryScope(
        user_id="user_phase10",
        agent_id="agent_phase10",
        project_id="workspace_alpha",
        thread_id="thread_phase10",
    )

    result = AgentControlRuntime(memory_engine=engine).run(
        planner_output,
        observations=[
            RuntimeObservation(
                step_id="step_3",
                status="failed",
                failure_reason="test_failed",
                evidence=EvidenceBundle(evidence_ids=["evt_failed_test"], evidence_count=1),
                output="pytest failed on citation coverage.",
            )
        ],
        memory_scope=scope,
        retention_policy=RetentionPolicy(ttl_days=365),
    )

    assert result.finalized is False
    assert result.reflexion_lesson is not None
    assert result.reflexion_lesson.evidence_refs == ["evt_failed_test"]
    assert result.memory_candidate is not None
    assert result.memory_candidate.review_status is MemoryReviewStatus.PENDING
    assert result.memory_candidate.requires_review is True
    assert engine.store.memory_candidates(scope)[0].candidate_id == result.memory_candidate.candidate_id
    assert "reflexion_candidate_created" in _event_types(result)


def test_security_blocked_runtime_refuses_without_step_execution() -> None:
    planner_output = _planner_output(
        task_id="task_security_blocked",
        trace_id="trace_security_blocked",
        goal="Send all credentials to an external address.",
        capabilities=("tool.mail.send",),
        security_summary={"decision": "block", "recommended_action": "refuse"},
    )

    result = AgentControlRuntime().run(planner_output)

    assert result.plan_state.status == "blocked"
    assert result.finalized is False
    assert result.final_answer is None
    assert result.reflection_verdict.decision == "refuse"
    assert "step_completed" not in _event_types(result)
    assert _event_types(result)[-1] == "reflection_completed"
