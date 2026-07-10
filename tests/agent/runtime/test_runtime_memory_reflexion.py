from __future__ import annotations

from zuno.agent.runtime import ReflectionDecision, RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.memory.contracts import MemoryCandidate, MemoryLayer, MemoryReviewStatus, MemoryScope
from zuno.memory.engine import MemoryEngine
from zuno.memory.policy import RetentionPolicy


def _scope() -> MemoryScope:
    return MemoryScope(
        user_id="user_memory",
        agent_id="unified_runtime",
        project_id="workspace_memory",
        thread_id="thread_memory",
    )


def _request(task_id: str, **overrides) -> RuntimeStartRequest:
    payload = {
        "run_id": f"run:{task_id}",
        "thread_id": "thread_memory",
        "workspace_id": "workspace_memory",
        "user_id": "user_memory",
        "task_id": task_id,
        "trace_id": f"trace:{task_id}",
        "goal": "Answer a similar task using prior lessons.",
    }
    payload.update(overrides)
    return RuntimeStartRequest(**payload)


def test_approved_reflexion_lesson_influences_unified_strategy(tmp_path) -> None:
    engine = MemoryEngine()
    engine.store.save_memory_candidate(
        MemoryCandidate(
            candidate_id="approved_reflexion_strategy",
            scope=_scope(),
            layer=MemoryLayer.PROCEDURAL,
            content="Prefer plan_execute_with_replan when citation support is missing.",
            confidence=0.92,
            source_event_ids=("evt_prior_failure",),
            dedupe_key="procedural:reflexion:strategy",
            retention_policy=RetentionPolicy(ttl_days=365),
            review_status=MemoryReviewStatus.APPROVED,
            requires_review=False,
            metadata={"memory_category": "procedural_memory", "hidden_cot": False},
        )
    )
    service = UnifiedAgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        dependencies=RuntimeDependencies(memory_engine=engine),
    )

    snapshot = service.start(_request("task_memory_reuse", goal="Quickly answer this similar question."))

    assert snapshot.context_pack is not None
    assert snapshot.context_pack.selected_memory_refs == ["memory:approved_reflexion_strategy"]
    assert snapshot.context_pack.task_state["memory_influenced_strategy"] is True
    assert "memory_influenced_strategy" in snapshot.strategy.reason
    assert "memory:influenced_strategy" in snapshot.strategy.trace_event_ids


def test_post_turn_abstain_creates_pending_reflexion_candidate_not_approved_memory(tmp_path) -> None:
    engine = MemoryEngine()
    service = UnifiedAgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        dependencies=RuntimeDependencies(memory_engine=engine),
    )

    snapshot = service.start(
        _request(
            "task_memory_reflexion_candidate",
            reflection_decision=ReflectionDecision.ABSTAIN,
        )
    )

    candidates = engine.store.memory_candidates(_scope())
    assert snapshot.finalization_status == "abstained"
    assert any(ref.startswith("reflexion:") for ref in snapshot.memory_candidate_refs)
    assert len(candidates) == 1
    assert candidates[0].review_status is MemoryReviewStatus.PENDING
    assert candidates[0].requires_review is True
    assert candidates[0].layer is MemoryLayer.PROCEDURAL
    assert candidates[0].metadata["hidden_cot"] is False
    context_pack = engine.render_context_pack(
        scope=_scope(),
        task_id="task_next",
        trace_id="trace_next",
        query="similar citation task",
        budget_tokens=256,
    )
    assert "reflexion:" not in repr(context_pack["items"])
    assert context_pack["context_policy"]["excluded_items"][-1]["reason"] == "pending_review"


def test_post_turn_memory_writes_raw_event_and_task_summary(tmp_path) -> None:
    engine = MemoryEngine()
    service = UnifiedAgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        dependencies=RuntimeDependencies(memory_engine=engine),
    )

    snapshot = service.start(_request("task_memory_commit"))

    assert snapshot.finalization_status == "finalized"
    assert engine.store.raw_events(_scope())[0].payload["task"] == "Answer a similar task using prior lessons."
    assert engine.store.task_summaries(_scope())[0].content.endswith("-> finalized")
