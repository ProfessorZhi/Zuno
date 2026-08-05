from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.model_step import ModelStepExecutor
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.platform.model_gateway import (
    MockModelProvider,
    ModelCategory,
    ModelGateway,
    ModelGatewayRequest,
)
from zuno.platform.model_roles import ModelRole, ROLE_DEFAULT_SLOT


class RecordingGateway(ModelGateway):
    def __init__(self) -> None:
        super().__init__(providers=[MockModelProvider()])
        self.calls: list[ModelGatewayRequest] = []

    def invoke(self, request: ModelGatewayRequest):
        self.calls.append(request)
        return super().invoke(request)


def _state() -> AgentRuntimeState:
    return AgentRuntimeState(
        run_id="run:model-roles",
        thread_id="thread-1",
        workspace_id="workspace-1",
        user_id="user-1",
        task_id="task-1",
        trace_id="trace-1",
        goal="answer the question",
    )


def _step(*, action_type: str, model_role: str | None = None) -> PlanStep:
    return PlanStep(
        step_id="step-1",
        goal="answer the question",
        action_type=action_type,
        expected_output="text",
        acceptance_criteria=("complete",),
        model_role=model_role,
    )


def test_canonical_model_step_routes_through_model_gateway_with_executor_role() -> None:
    gateway = RecordingGateway()
    deps = RuntimeDependencies(model_gateway=gateway)
    result = ModelStepExecutor().execute(state=_state(), step=_step(action_type="model_transform"), deps=deps)

    assert result.status.value == "completed"
    assert len(gateway.calls) == 1
    request = gateway.calls[0]
    assert request.category is ModelCategory.CHAT
    assert request.role is ModelRole.EXECUTOR
    assert request.run_id == "run:model-roles"
    assert request.trace_id == "trace-1"
    assert "model_gateway_call" in result.observation.metadata


def test_canonical_model_step_uses_critic_role_for_reflection() -> None:
    gateway = RecordingGateway()
    deps = RuntimeDependencies(model_gateway=gateway)
    ModelStepExecutor().execute(state=_state(), step=_step(action_type="reflect_before_final"), deps=deps)

    assert gateway.calls[0].role is ModelRole.CRITIC


def test_canonical_model_step_uses_synthesis_role_for_answer() -> None:
    gateway = RecordingGateway()
    deps = RuntimeDependencies(model_gateway=gateway)
    ModelStepExecutor().execute(state=_state(), step=_step(action_type="answer_with_evidence"), deps=deps)

    assert gateway.calls[0].role is ModelRole.SYNTHESIS


def test_canonical_model_step_respects_explicit_step_model_role() -> None:
    gateway = RecordingGateway()
    deps = RuntimeDependencies(model_gateway=gateway)
    ModelStepExecutor().execute(
        state=_state(),
        step=_step(action_type="model_transform", model_role="tool_call"),
        deps=deps,
    )

    assert gateway.calls[0].role is ModelRole.TOOL_CALL


def test_model_roles_have_default_slots() -> None:
    assert ROLE_DEFAULT_SLOT[ModelRole.PLANNER] == "reasoning_model"
    assert ROLE_DEFAULT_SLOT[ModelRole.EXECUTOR] == "conversation_model"
    assert ROLE_DEFAULT_SLOT[ModelRole.CRITIC] == "reasoning_model"
    assert ROLE_DEFAULT_SLOT[ModelRole.SYNTHESIS] == "conversation_model"
    assert ROLE_DEFAULT_SLOT[ModelRole.TOOL_CALL] == "tool_call_model"
