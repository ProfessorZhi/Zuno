from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime import RuntimeDependencyFactory, RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.knowledge_step import KnowledgeStepExecutor
from zuno.agent.runtime.execution.model_step import ModelStepExecutor
from zuno.agent.runtime.execution.tool_step import ToolStepExecutor
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.knowledge.indexing.runtime import KnowledgeIndexRuntime


def _state() -> AgentRuntimeState:
    return AgentRuntimeState(
        run_id="run:deps",
        thread_id="thread:deps",
        workspace_id="workspace:deps",
        user_id="user:deps",
        task_id="task:deps",
        trace_id="trace:deps",
        goal="Summarize local evidence.",
    )


def _step(action_type: str) -> PlanStep:
    return PlanStep(
        step_id=f"step:{action_type}",
        goal=action_type,
        action_type=action_type,
        acceptance_criteria=["blocked or completed is explicit"],
    )


def test_runtime_dependency_factory_builds_completion_dependencies(tmp_path) -> None:
    store = SQLiteAgentRunStore(tmp_path / "runtime.db")

    assembly = RuntimeDependencyFactory.for_completion(store=store)

    assert assembly.store is store
    assert assembly.dependencies.model_gateway is not None
    assert assembly.dependencies.memory_engine is not None
    assert assembly.dependencies.tool_control_plane is not None
    assert assembly.dependencies.knowledge_runtime is None


def test_runtime_dependency_factory_builds_workspace_knowledge_runtime(tmp_path) -> None:
    store = SQLiteAgentRunStore(tmp_path / "runtime.db")
    index_runtime = KnowledgeIndexRuntime()

    assembly = RuntimeDependencyFactory.for_workspace_task(
        store=store,
        knowledge_index_runtime=index_runtime,
    )

    assert assembly.store is store
    assert assembly.dependencies.knowledge_runtime is not None
    assert hasattr(assembly.dependencies.knowledge_runtime, "retrieve")


def test_missing_runtime_dependencies_return_blocked_observations() -> None:
    deps = RuntimeDependencies()
    state = _state()

    model = ModelStepExecutor().execute(state=state, step=_step("draft_answer"), deps=deps)
    knowledge = KnowledgeStepExecutor().execute(state=state, step=_step("retrieve_evidence"), deps=deps)
    tool = ToolStepExecutor().execute(state=state, step=_step("tool_call"), deps=deps)

    assert model.observation.status == "blocked"
    assert model.observation.metadata["missing_dependency"] == "model_gateway"
    assert knowledge.observation.status == "blocked"
    assert knowledge.observation.evidence_ids == []
    assert knowledge.observation.citation_ids == []
    assert knowledge.observation.metadata["missing_dependency"] == "knowledge_runtime"
    assert tool.observation.status == "blocked"
    assert tool.observation.metadata["missing_dependency"] == "tool_control_plane"


def test_unified_runtime_service_can_start_from_factory_assembly(tmp_path) -> None:
    assembly = RuntimeDependencyFactory.for_completion(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))
    service = UnifiedAgentRuntimeService(store=assembly.store, dependencies=assembly.dependencies)

    snapshot = service.start(
        RuntimeStartRequest(
            run_id="run:factory",
            thread_id="thread:factory",
            workspace_id="workspace:factory",
            user_id="user:factory",
            task_id="task:factory",
            trace_id="trace:factory",
            goal="Answer with the unified runtime factory.",
        )
    )

    assert snapshot.task_id == "task:factory"
    assert snapshot.finalization_status in {"finalized", "abstained"}
