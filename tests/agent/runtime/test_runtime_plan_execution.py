from __future__ import annotations

from dataclasses import dataclass

import pytest

from zuno.agent.contracts import PlanState, PlanStep
from zuno.agent.runtime import RuntimeDependencyFactory, RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
from zuno.agent.runtime.planning import PlanExecutor, PlanValidationError, PlanValidator
from zuno.knowledge.agentic import (
    CorrectiveAction,
    CorrectiveRetrievalResult,
    EvidenceLedger,
    EvidenceLedgerRecord,
    QueryStrategy,
    RetrievalQualityVerdict,
)


def _request(task_id: str, goal: str) -> RuntimeStartRequest:
    return RuntimeStartRequest(
        run_id=f"run:{task_id}",
        thread_id="thread_plan",
        workspace_id="workspace_plan",
        user_id="user_plan",
        task_id=task_id,
        trace_id=f"trace:{task_id}",
        goal=goal,
    )


@dataclass
class _EvidenceRuntime:
    calls: int = 0

    def retrieve(self, request):
        self.calls += 1
        ledger = EvidenceLedger()
        ledger.add(
            EvidenceLedgerRecord(
                evidence_id=f"ev:plan:{self.calls}",
                document_id="doc_plan",
                document_version="v1",
                source_span={"page": 1, "line_range": [1, 3]},
                retrieval_round=self.calls,
                query_id=f"{request.trace_id}:q:{self.calls}",
                query_strategy=QueryStrategy.DIRECT,
                retriever="unit",
                raw_score=0.9,
                rerank_score=0.9,
                text="The contract requires cited evidence for renewal conflicts.",
            )
        )
        return CorrectiveRetrievalResult(
            answer="unit answer",
            ledger=ledger,
            rounds=({"round": self.calls, "verdict": RetrievalQualityVerdict.RELEVANT.value},),
            final_verdict=RetrievalQualityVerdict.RELEVANT,
            final_action=CorrectiveAction.CONTINUE,
            trace={"ledger": ledger.to_trace(), "rounds": []},
        )


def test_unified_runtime_executes_multiple_plan_steps_before_reflection(tmp_path) -> None:
    knowledge_runtime = _EvidenceRuntime()
    dependencies = RuntimeDependencyFactory().dependencies()
    dependencies = dependencies.__class__(
        model_gateway=dependencies.model_gateway,
        memory_engine=dependencies.memory_engine,
        knowledge_runtime=knowledge_runtime,
        capability_runtime=dependencies.capability_runtime,
        tool_control_plane=dependencies.tool_control_plane,
        trace_sink=dependencies.trace_sink,
    )
    service = UnifiedAgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        dependencies=dependencies,
    )

    snapshot = service.start(
        _request(
            "task_multistep",
            "Compare evidence across documents and synthesize conflicts with citations.",
        )
    )

    assert snapshot.finalization_status == "finalized"
    assert snapshot.plan_state is not None
    assert snapshot.plan_state.status == "completed"
    assert len(snapshot.plan_state.steps) >= 2
    assert all(step.status == "completed" for step in snapshot.plan_state.steps)
    assert snapshot.counters.steps_executed >= 2
    assert len(snapshot.observations) >= 2
    assert all(step.observation_refs for step in snapshot.plan_state.steps)
    assert knowledge_runtime.calls >= 1


def test_plan_validator_rejects_invalid_dag_and_missing_acceptance() -> None:
    validator = PlanValidator()

    with pytest.raises(PlanValidationError, match="no acceptance"):
        validator.validate(
            PlanState(
                plan_id="plan_invalid",
                steps=[
                    PlanStep(
                        step_id="step_1",
                        goal="missing acceptance",
                        action_type="model_transform",
                    )
                ],
            )
        )

    with pytest.raises(PlanValidationError, match="cycle"):
        validator.validate(
            PlanState(
                plan_id="plan_cycle",
                steps=[
                    PlanStep(
                        step_id="step_1",
                        goal="a",
                        action_type="model_transform",
                        dependencies=["step_2"],
                        acceptance_criteria=["done"],
                    ),
                    PlanStep(
                        step_id="step_2",
                        goal="b",
                        action_type="model_transform",
                        dependencies=["step_1"],
                        acceptance_criteria=["done"],
                    ),
                ],
            )
        )


def test_plan_executor_marks_attempt_status_and_observation_refs() -> None:
    plan = PlanState(
        plan_id="plan_executor",
        steps=[
            PlanStep(
                step_id="step_1",
                goal="retrieve",
                action_type="retrieve_evidence",
                acceptance_criteria=["done"],
            ),
            PlanStep(
                step_id="step_2",
                goal="draft",
                action_type="draft_answer",
                dependencies=["step_1"],
                acceptance_criteria=["done"],
            ),
        ],
    )
    executor = PlanExecutor()

    first = executor.next_ready_step(plan)
    assert first.step_id == "step_1"
    running = executor.mark_running(plan, first)
    assert running.steps[0].status == "running"
    assert running.steps[0].attempt == 1
    completed = executor.mark_completed(running, running.steps[0], observation_ref="obs_1")

    assert completed.steps[0].status == "completed"
    assert completed.steps[0].observation_refs == ["obs_1"]
    assert completed.current_step_id == "step_2"
    assert executor.next_ready_step(completed).step_id == "step_2"


def test_step_budget_limit_forces_finalize_without_fake_completion(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))
    request = _request("task_budget", "Compare evidence across documents and synthesize conflicts.")
    snapshot = service.start(request)

    assert snapshot.counters.steps_executed <= snapshot.limits.max_steps
    assert not any(step.status == "completed" and not step.observation_refs for step in snapshot.plan_state.steps)
