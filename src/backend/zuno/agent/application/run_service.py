from __future__ import annotations

import json
from typing import Any, Callable

from zuno.agent.runtime import (
    AgentRuntimeService,
    RuntimeStartRequest,
    SQLiteAgentRunStore,
)
from zuno.api.dto.workspace import WorkSpaceSimpleTask
from zuno.api.services.user import UserPayload
from zuno.platform.security import GateRequest, InputSecurityGate, SecurityDecision, SecurityGate


class AgentRunApplicationService:
    """Product application owner for Agent Run admission and projections.

    This service owns the application boundary only: it validates product
    context, applies the input security gate, builds the canonical runtime
    request, and maps durable Agent Run facts to Product projections. Runtime
    execution, checkpointing, approval interrupts and recovery belong to
    ``AgentRuntimeService`` and its injected ``AgentRunStore``.
    """

    _agent_run_store: SQLiteAgentRunStore | None = None
    _product_runtime_submitter_for_tests: Callable[..., Any] | None = None
    _task_projections: dict[str, dict[str, Any]] = {}
    _projection_events: dict[str, list[dict[str, Any]]] = {}
    _input_security_gate = InputSecurityGate()

    @classmethod
    def configure_agent_run_store_for_tests(cls, store: SQLiteAgentRunStore) -> None:
        cls._agent_run_store = store

    @classmethod
    def configure_product_runtime_submitter_for_tests(
        cls, submitter: Callable[..., Any] | None
    ) -> None:
        cls._product_runtime_submitter_for_tests = submitter

    @classmethod
    def reset_runtime_state_for_tests(cls) -> None:
        cls._agent_run_store = None
        cls._product_runtime_submitter_for_tests = None
        cls._task_projections = {}
        cls._projection_events = {}

    @classmethod
    def _store(cls) -> SQLiteAgentRunStore:
        if cls._agent_run_store is None:
            raise RuntimeError("Agent Run durable store is not configured")
        return cls._agent_run_store

    @classmethod
    def _runtime(cls) -> AgentRuntimeService:
        return AgentRuntimeService(store=cls._store())

    @classmethod
    def create_task(
        cls,
        *,
        simple_task: WorkSpaceSimpleTask,
        login_user: UserPayload,
    ) -> dict[str, Any]:
        workspace_id = str(simple_task.workspace_id or "").strip()
        if not workspace_id:
            raise ValueError("workspace_id must come from validated Product context")

        task_id = simple_task.task_id or f"task:{simple_task.session_id}"
        trace_id = simple_task.trace_id or f"trace:{task_id}"
        goal = str(simple_task.goal or simple_task.query or "").strip()
        if not goal:
            raise ValueError("Agent Run goal is required")

        security_result = cls._input_security_gate.evaluate(
            GateRequest(
                gate=SecurityGate.INPUT,
                workspace_id=workspace_id,
                user_id=login_user.user_id,
                content=simple_task.query,
                metadata={"source": "product_agent_run"},
                trace_id=trace_id,
                task_id=task_id,
            )
        )
        task_projection = {
            "task_id": task_id,
            "workspace_id": workspace_id,
            "owner": login_user.user_id,
            "trace_id": trace_id,
            "goal": goal,
            "status": "failed" if security_result.decision is SecurityDecision.BLOCK else "running",
        }
        cls._task_projections[task_id] = task_projection

        if security_result.decision is SecurityDecision.BLOCK:
            cls._append_projection_event(
                task_id,
                event_type="security_gate",
                status="failed",
                payload={
                    "policy_decision": "block",
                    "findings": [finding.to_dict() for finding in security_result.findings],
                    "sanitized_content": security_result.sanitized_content,
                },
            )
            return {"task": dict(task_projection), "agent_run": None}

        if cls._product_runtime_submitter_for_tests is not None:
            cls._product_runtime_submitter_for_tests(
                tenant_id=login_user.tenant_id or login_user.user_id,
                workspace_id=workspace_id,
                conversation_id=simple_task.session_id,
                principal_id=login_user.user_id,
                active_agent_version_id="agent-version:product:default",
                client_request_id=task_id,
                runtime_request_ref=f"runtime-request:{task_id}",
                raw_intent_ref=f"intent:{task_id}",
                payload={"goal": goal},
            )

        request = RuntimeStartRequest(
            run_id=f"run:{task_id}",
            thread_id=simple_task.session_id or f"thread:{task_id}",
            workspace_id=workspace_id,
            user_id=login_user.user_id,
            tenant_id=login_user.tenant_id or login_user.user_id,
            principal_id=login_user.user_id,
            task_id=task_id,
            trace_id=trace_id,
            goal=goal,
            submission_id=f"submission:{task_id}",
            client_request_id=task_id,
            conversation_id=simple_task.session_id or f"conversation:{task_id}",
            agent_version="agent-version:product:default",
            plan_steps=(
                {
                    "step_id": f"step:{task_id}:answer",
                    "goal": goal,
                    "action_type": "draft_answer",
                    "expected_output": "a product answer",
                    "acceptance_criteria": ["answer observation produced"],
                },
            ),
        )
        snapshot = cls._runtime().start(request)
        cls._task_projections[task_id]["status"] = _projection_status(snapshot.finalization_status)
        return {
            "task": dict(cls._task_projections[task_id]),
            "agent_run": snapshot.model_dump(mode="json"),
        }

    @classmethod
    def approve_task(
        cls,
        *,
        task_id: str,
        decision: str,
        approval_id: str | None = None,
        tool_call_id: str | None = None,
        required_approval: str | None = None,
    ) -> dict[str, Any]:
        interrupt = cls._store().pending_interrupt(task_id)
        if interrupt is None:
            raise ValueError(f"Agent Run is not waiting for approval: {task_id}")
        payload = dict(getattr(interrupt, "payload", {}) or {})
        _require_bound_ref(
            supplied=approval_id,
            expected=str(payload.get("approval_id") or ""),
            field="approval_id",
        )
        _require_bound_ref(
            supplied=tool_call_id,
            expected=str(payload.get("tool_call_id") or ""),
            field="tool_call_id",
        )
        _require_bound_ref(
            supplied=required_approval,
            expected=str(getattr(interrupt, "required_approval", "") or payload.get("required_approval") or ""),
            field="required_approval",
        )
        snapshot = cls._runtime().resume(task_id=task_id, approval_decision=decision)
        cls._task_projections.setdefault(task_id, {})["status"] = _projection_status(snapshot.finalization_status)
        return cls.get_task_snapshot(task_id)

    @classmethod
    def cancel_task(cls, *, task_id: str, reason: str | None) -> dict[str, Any]:
        snapshot = cls._runtime().cancel(task_id=task_id, reason=reason or "cancelled by product")
        cls._task_projections.setdefault(task_id, {})["status"] = "cancelled"
        return cls.get_task_snapshot(task_id)

    @staticmethod
    def task_lifecycle_contract() -> dict[str, Any]:
        return {
            "owner": "AgentRunApplicationService",
            "execution_owner": "AgentRuntimeService",
            "terminal_states": ["finalized", "failed", "cancelled", "blocked"],
            "recovery": "AgentRunStore checkpoint and interrupt recovery",
        }

    @classmethod
    def get_task_snapshot(cls, task_id: str, *, principal_id: str = "") -> dict[str, Any]:
        snapshot = cls._runtime().get_snapshot(task_id)
        if snapshot is None:
            raise ValueError(f"Agent Run not found: {task_id}")
        if principal_id and snapshot.user_id != principal_id:
            raise PermissionError(f"Agent Run outside principal scope: {task_id}")
        projection = dict(cls._task_projections.get(task_id) or {})
        projection.setdefault("task_id", task_id)
        projection["status"] = _projection_status(snapshot.finalization_status)
        return {"task": projection, "agent_run": snapshot.model_dump(mode="json")}

    @classmethod
    def list_task_events(cls, task_id: str) -> list[dict[str, Any]]:
        projection_events = list(cls._projection_events.get(task_id) or [])
        runtime_events = [_event_payload(event) for event in cls._store().events(task_id)]
        return [*projection_events, *runtime_events]

    @classmethod
    async def stream_task_events(cls, task_id: str):
        for event in cls.list_task_events(task_id):
            yield f"data: {json.dumps({'data': event}, ensure_ascii=False)}\n\n"

    @classmethod
    def _append_projection_event(
        cls,
        task_id: str,
        *,
        event_type: str,
        status: str,
        payload: dict[str, Any],
    ) -> None:
        cls._projection_events.setdefault(task_id, []).append(
            {
                "event_id": f"projection:{task_id}:{event_type}",
                "task_id": task_id,
                "trace_id": str(cls._task_projections.get(task_id, {}).get("trace_id") or f"trace:{task_id}"),
                "type": event_type,
                "node": "product.application",
                "status": status,
                "payload": payload,
            }
        )


def _projection_status(status: Any) -> str:
    value = str(getattr(status, "value", status) or "").lower()
    return {
        "finalized": "completed",
        "interrupted": "approval_waiting",
        "abstained": "completed",
    }.get(value, value or "running")


def _require_bound_ref(*, supplied: str | None, expected: str, field: str) -> None:
    if supplied is not None and supplied != expected:
        raise PermissionError(f"{field} does not match the durable Agent Run interrupt")


def _event_payload(event: Any) -> dict[str, Any]:
    return {
        "event_id": str(getattr(event, "event_id", "")),
        "task_id": str(getattr(event, "task_id", "")),
        "trace_id": str(getattr(event, "trace_id", "")),
        "type": str(getattr(event, "type", "")),
        "node": str(getattr(event, "node", "")),
        "status": str(getattr(event, "status", "")),
        "payload": dict(getattr(event, "payload", {}) or {}),
    }


__all__ = ["AgentRunApplicationService"]
