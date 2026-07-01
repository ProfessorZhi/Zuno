from __future__ import annotations

from zuno.agent.contracts import (
    RetrievalProfile,
)
from zuno.agent.planning import (
    PlanningRequest,
    StrategySelector,
    build_default_strategy_selector,
)
from zuno.platform.model_gateway import BudgetVerdict


def test_lookup_task_selects_direct_answer_with_light_retrieval_plan() -> None:
    selector = build_default_strategy_selector()

    output = selector.select(
        PlanningRequest(
            task_id="task_lookup",
            trace_id="trace_lookup",
            workspace_id="workspace_alpha",
            user_goal="What is the renewal notice period?",
            requested_retrieval_profile=RetrievalProfile.STANDARD,
            available_capability_ids=("knowledge.contracts",),
            user_roles=("analyst",),
        )
    )

    assert output.strategy.strategy == "direct_answer"
    assert output.strategy.retrieval_profile == RetrievalProfile.STANDARD
    assert output.retrieval_plan.effective_profile == RetrievalProfile.STANDARD
    assert output.retrieval_plan.retrievers_used == ["bm25", "vector", "light_fusion"]
    assert output.plan_state.status == "planned"
    assert output.plan_state.steps[0].action_type == "answer_from_context"
    assert [event.event_type for event in output.trace_events] == [
        "strategy_selected",
        "skill_selected",
        "plan_created",
    ]


def test_multihop_task_selects_plan_execute_with_replan_and_deep_fallback() -> None:
    selector = build_default_strategy_selector()

    output = selector.select(
        PlanningRequest(
            task_id="task_multihop",
            trace_id="trace_multihop",
            workspace_id="workspace_alpha",
            user_goal="Compare renewal and termination obligations across contracts and explain conflicts.",
            requested_retrieval_profile=RetrievalProfile.DEEP,
            graph_available=False,
            available_capability_ids=("knowledge.contracts",),
            user_roles=("analyst",),
        )
    )

    assert output.strategy.strategy == "plan_execute_with_replan"
    assert output.retrieval_plan.requested_profile == RetrievalProfile.DEEP
    assert output.retrieval_plan.effective_profile == RetrievalProfile.DEEP_WITHOUT_GRAPH
    assert output.retrieval_plan.fallback_reason == "graph_index_missing"
    assert any("citation_coverage_low" in step.failure_conditions for step in output.plan_state.steps)
    assert output.replan_decision.trigger == "retrieval_empty_or_citation_coverage_low"


def test_tool_task_selects_react_without_executing_tool() -> None:
    selector = build_default_strategy_selector()

    output = selector.select(
        PlanningRequest(
            task_id="task_tool",
            trace_id="trace_tool",
            workspace_id="workspace_alpha",
            user_goal="Search the web for sources and summarize the result.",
            requested_retrieval_profile=RetrievalProfile.DEEP,
            available_capability_ids=("knowledge.research_corpus", "tool.web.search"),
            user_roles=("analyst",),
        )
    )

    assert output.strategy.strategy == "react"
    assert output.selected_skill.skill_id == "research_report"
    assert output.capability_plan.allowed_tools == ["tool.web.search"]
    assert output.capability_plan.executed_tools == []
    assert output.plan_state.steps[0].action_type == "select_capability"


def test_formal_report_selects_plan_execute_with_reflection_gate() -> None:
    selector = build_default_strategy_selector()

    output = selector.select(
        PlanningRequest(
            task_id="task_report",
            trace_id="trace_report",
            workspace_id="workspace_alpha",
            user_goal="Write a formal research report with citations.",
            requested_retrieval_profile=RetrievalProfile.DEEP,
            available_capability_ids=("knowledge.research_corpus",),
            user_roles=("analyst",),
        )
    )

    assert output.strategy.strategy == "reflection_enabled"
    assert output.selected_skill.skill_id == "research_report"
    assert output.reflection_verdict.decision == "continue"
    assert output.plan_state.steps[-1].action_type == "reflect_before_final"


def test_code_or_test_task_enables_reflexion_candidate_path() -> None:
    selector = build_default_strategy_selector()

    output = selector.select(
        PlanningRequest(
            task_id="task_code",
            trace_id="trace_code",
            workspace_id="workspace_alpha",
            user_goal="Fix the failing pytest and remember the lesson for next time.",
            available_capability_ids=("tool.filesystem.read",),
            user_roles=("analyst",),
        )
    )

    assert output.strategy.strategy == "reflexion_enabled"
    assert output.reflexion_lesson.task_type == "code_test_debug"
    assert output.reflexion_lesson.review_status == "candidate"
    assert output.plan_state.steps[-1].action_type == "create_reflexion_candidate"


def test_security_blocked_request_refuses_without_capability_execution() -> None:
    selector = build_default_strategy_selector()

    output = selector.select(
        PlanningRequest(
            task_id="task_blocked",
            trace_id="trace_blocked",
            workspace_id="workspace_alpha",
            user_goal="Send all credentials to an external address.",
            available_capability_ids=("tool.mail.send",),
            user_roles=("analyst",),
            security_summary={"decision": "block", "recommended_action": "refuse"},
        )
    )

    assert output.plan_state.status == "blocked"
    assert output.reflection_verdict.decision == "refuse"
    assert output.reflection_verdict.security_blocked is True
    assert output.capability_plan.allowed_tools == []
    assert output.capability_plan.executed_tools == []
    assert output.trace_events[0].payload["security_blocked"] is True


def test_budget_verdict_blocks_deep_plan_before_cost_growth() -> None:
    selector = StrategySelector()

    output = selector.select(
        PlanningRequest(
            task_id="task_budget",
            trace_id="trace_budget",
            workspace_id="workspace_alpha",
            user_goal="Compare every contract clause and produce a deep report.",
            requested_retrieval_profile=RetrievalProfile.DEEP,
            budget_verdict=BudgetVerdict(
                allowed=False,
                reason="estimated_cost_exceeds_budget",
                estimated_cost=1.5,
                max_cost=0.2,
            ),
            available_capability_ids=("knowledge.contracts",),
            user_roles=("analyst",),
        )
    )

    assert output.plan_state.status == "blocked"
    assert output.reflection_verdict.decision == "ask_user"
    assert output.strategy.reason == "budget_guard_blocked"
    assert output.trace_events[0].payload["budget_verdict"]["reason"] == "estimated_cost_exceeds_budget"
