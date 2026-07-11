from __future__ import annotations

import hashlib

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import FinalizationStatus, NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.registry import StepExecutionResult
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.capability.runtime import ToolRuntimeRequest


class ToolStepExecutor:
    action_types = frozenset({"select_capability", "observe_tool_result", "tool_call"})

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        if deps.tool_control_plane is None:
            observation = NormalizedObservation(
                observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
                step_id=step.step_id,
                kind=ObservationKind.TOOL,
                status=ObservationStatus.BLOCKED,
                source="ToolStepExecutor",
                summary="tool control plane dependency missing",
                failure_reason="missing_tool_control_plane",
                metadata={
                    "blocked": True,
                    "missing_dependency": "tool_control_plane",
                    "action_type": step.action_type,
                },
            )
            return StepExecutionResult(step_id=step.step_id, status=ObservationStatus.BLOCKED, observation=observation)
        tool_runtime = deps.tool_control_plane
        tool_id = _tool_id_for_step(state, step)
        arguments = _arguments_for_step(state, step, tool_id)
        idempotency_key = _idempotency_key(state, step, tool_id, arguments)
        approved = f"approved:{idempotency_key}" in state.interrupt_refs
        request = ToolRuntimeRequest(
            tool_id=tool_id,
            arguments=arguments,
            workspace_id=state.workspace_id,
            user_id=state.user_id,
            task_id=state.task_id,
            trace_id=state.trace_id,
            model_intent=step.goal,
            approved=approved,
            runtime_state=state,
            execution_id=idempotency_key,
        )
        result = tool_runtime.execute(request)
        if result.status == "approval_required":
            observation = NormalizedObservation(
                observation_id=f"obs:{state.run_id}:{step.step_id}:approval",
                step_id=step.step_id,
                kind=ObservationKind.TOOL,
                status=ObservationStatus.WAITING,
                source="ToolStepExecutor",
                summary=f"approval required for {tool_id}",
                tool_id=tool_id,
                trace_span_id=result.audit_event.audit_id,
                metadata={
                    "tool_runtime_status": result.status,
                    "tool_request_id": result.tool_request_id,
                    "approval_id": result.approval_id,
                    "required_approval": f"tool:{tool_id}",
                    "idempotency_key": idempotency_key,
                    "task_events": [event["type"] for event in result.task_events],
                    "credential_refs": [],
                },
            )
            return StepExecutionResult(
                step_id=step.step_id,
                status=ObservationStatus.WAITING,
                observation=observation,
                interrupt_required=True,
                required_approval=f"tool:{tool_id}",
                idempotency_key=idempotency_key,
            )

        status = ObservationStatus.COMPLETED if result.status == "completed" else ObservationStatus.BLOCKED
        normalized = result.normalized_result
        observation = NormalizedObservation(
            observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
            step_id=step.step_id,
            kind=ObservationKind.TOOL,
            status=status,
            source="ToolStepExecutor",
            summary=(normalized.summary if normalized else result.status),
            tool_id=tool_id,
            trace_span_id=(normalized.trace_span_id if normalized else result.audit_event.audit_id),
            failure_reason=None if status == ObservationStatus.COMPLETED else result.status,
            metadata={
                "tool_runtime_status": result.status,
                "tool_request_id": result.tool_request_id,
                "approval_id": result.approval_id,
                "tool_execution_id": result.tool_execution_id,
                "tool_result_id": result.tool_result_id,
                "idempotency_key": idempotency_key,
                "task_events": [event["type"] for event in result.task_events],
                "credential_refs": list(result.sandbox_context.credential_refs),
                "result": normalized.to_dict() if normalized else None,
            },
        )
        return StepExecutionResult(step_id=step.step_id, status=status, observation=observation)


def _tool_id_for_step(state: AgentRuntimeState, step: PlanStep) -> str:
    if step.action_type == "observe_tool_result":
        return "filesystem.read"
    if step.allowed_capabilities:
        for value in step.allowed_capabilities:
            if value in {"filesystem.read", "filesystem.write", "mail.send"}:
                return value
            if value == "tool.web.search":
                return "filesystem.read"
    if state.capability_plan.allowed_tools:
        return state.capability_plan.allowed_tools[0]
    combined_goal = f"{state.goal} {step.goal}".lower()
    if "send" in combined_goal or "email" in combined_goal or "mail" in combined_goal:
        return "mail.send"
    if "write" in combined_goal:
        return "filesystem.write"
    return "filesystem.read"


def _arguments_for_step(state: AgentRuntimeState, step: PlanStep, tool_id: str) -> dict:
    goal = f"{state.goal} {step.goal}"
    if tool_id == "filesystem.read":
        return {"path": "docs/contract.md"}
    if tool_id == "filesystem.write":
        return {"path": "artifacts/tool-output.md", "content": goal}
    if "mail" in goal.lower() or "email" in goal.lower() or "send" in goal.lower():
        if "https://" in goal.lower() or "http://" in goal.lower():
            return {"to": "review@example.com", "body": goal, "target": "https://example.com"}
        return {"to": "review@example.com", "body": goal, "target": "mailto:review@example.com"}
    return {"path": "docs/contract.md"}


def _idempotency_key(state: AgentRuntimeState, step: PlanStep, tool_id: str, arguments: dict) -> str:
    source = f"{state.run_id}|{step.step_id}|{tool_id}|{sorted(arguments.items())}"
    return f"toolclaim:{hashlib.sha256(source.encode('utf-8')).hexdigest()[:16]}"


__all__ = ["ToolStepExecutor"]
