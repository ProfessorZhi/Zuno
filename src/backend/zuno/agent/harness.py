from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


RUNTIME_NODE_ORDER = (
    "prepare_context",
    "intent_and_policy_route",
    "plan",
    "act_react_loop",
    "observe",
    "evidence_check",
    "reflect",
    "replan_if_needed",
    "answer_or_artifact",
    "post_turn_commit",
)


@dataclass(frozen=True, slots=True)
class RuntimeNodeContract:
    name: str
    input_keys: tuple[str, ...] = ()
    output_keys: tuple[str, ...] = ()
    trace_span: str = ""
    checkpoint_policy: str = "after"
    failure_policy: str = "surface_error"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "input_keys": list(self.input_keys),
            "output_keys": list(self.output_keys),
            "trace_span": self.trace_span,
            "checkpoint_policy": self.checkpoint_policy,
            "failure_policy": self.failure_policy,
        }


@dataclass(frozen=True, slots=True)
class ControllerRuntimeState:
    thread_id: str
    workspace_id: str
    user_id: str
    task_id: str
    trace_id: str
    goal: str
    context_pack: dict[str, Any] = field(default_factory=dict)
    plan: tuple[str, ...] = ()
    current_step: str = ""
    observations: tuple[dict[str, Any], ...] = ()
    tool_calls: tuple[dict[str, Any], ...] = ()
    retrieval_events: tuple[dict[str, Any], ...] = ()
    approval_interrupts: tuple[dict[str, Any], ...] = ()
    memory_candidates: tuple[str, ...] = ()
    artifact_refs: tuple[str, ...] = ()
    checkpoints: tuple[str, ...] = ()
    stage_order: tuple[str, ...] = RUNTIME_NODE_ORDER

    def to_dict(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "goal": self.goal,
            "context_pack": deepcopy(self.context_pack),
            "plan": list(self.plan),
            "current_step": self.current_step,
            "observations": [dict(item) for item in self.observations],
            "tool_calls": [dict(item) for item in self.tool_calls],
            "retrieval_events": [dict(item) for item in self.retrieval_events],
            "approval_interrupts": [dict(item) for item in self.approval_interrupts],
            "memory_candidates": list(self.memory_candidates),
            "artifact_refs": list(self.artifact_refs),
            "checkpoints": list(self.checkpoints),
            "stage_order": list(self.stage_order),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ControllerRuntimeState":
        return cls(
            thread_id=str(payload.get("thread_id") or ""),
            workspace_id=str(payload.get("workspace_id") or ""),
            user_id=str(payload.get("user_id") or ""),
            task_id=str(payload.get("task_id") or ""),
            trace_id=str(payload.get("trace_id") or ""),
            goal=str(payload.get("goal") or ""),
            context_pack=deepcopy(dict(payload.get("context_pack") or {})),
            plan=tuple(str(item) for item in payload.get("plan") or ()),
            current_step=str(payload.get("current_step") or ""),
            observations=tuple(dict(item) for item in payload.get("observations") or ()),
            tool_calls=tuple(dict(item) for item in payload.get("tool_calls") or ()),
            retrieval_events=tuple(dict(item) for item in payload.get("retrieval_events") or ()),
            approval_interrupts=tuple(dict(item) for item in payload.get("approval_interrupts") or ()),
            memory_candidates=tuple(str(item) for item in payload.get("memory_candidates") or ()),
            artifact_refs=tuple(str(item) for item in payload.get("artifact_refs") or ()),
            checkpoints=tuple(str(item) for item in payload.get("checkpoints") or ()),
            stage_order=tuple(str(item) for item in payload.get("stage_order") or RUNTIME_NODE_ORDER),
        )


@dataclass(frozen=True, slots=True)
class RuntimeCheckpoint:
    checkpoint_id: str
    thread_id: str
    task_id: str
    trace_id: str
    node: str
    state: dict[str, Any]
    payload: dict[str, Any] = field(default_factory=dict)
    state_version: str = "single-controller-v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "thread_id": self.thread_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "node": self.node,
            "state": deepcopy(self.state),
            "payload": deepcopy(self.payload),
            "state_version": self.state_version,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RuntimeCheckpoint":
        return cls(
            checkpoint_id=str(payload.get("checkpoint_id") or ""),
            thread_id=str(payload.get("thread_id") or ""),
            task_id=str(payload.get("task_id") or ""),
            trace_id=str(payload.get("trace_id") or ""),
            node=str(payload.get("node") or ""),
            state=deepcopy(dict(payload.get("state") or {})),
            payload=deepcopy(dict(payload.get("payload") or {})),
            state_version=str(payload.get("state_version") or "single-controller-v1"),
        )


@dataclass(frozen=True, slots=True)
class RuntimeInterrupt:
    interrupt_id: str
    thread_id: str
    task_id: str
    trace_id: str
    node: str
    reason: str
    required_approval: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    resumable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "interrupt_id": self.interrupt_id,
            "thread_id": self.thread_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "node": self.node,
            "reason": self.reason,
            "required_approval": self.required_approval,
            "payload": deepcopy(self.payload),
            "resumable": self.resumable,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RuntimeInterrupt":
        return cls(
            interrupt_id=str(payload.get("interrupt_id") or ""),
            thread_id=str(payload.get("thread_id") or ""),
            task_id=str(payload.get("task_id") or ""),
            trace_id=str(payload.get("trace_id") or ""),
            node=str(payload.get("node") or ""),
            reason=str(payload.get("reason") or ""),
            required_approval=str(payload.get("required_approval") or ""),
            payload=deepcopy(dict(payload.get("payload") or {})),
            resumable=bool(payload.get("resumable", True)),
        )


@dataclass(frozen=True, slots=True)
class SingleControllerRuntimeHarness:
    node_contracts: tuple[RuntimeNodeContract, ...]
    runtime_topology: str = "single_controller"

    def node_names(self) -> list[str]:
        return [contract.name for contract in self.node_contracts]

    def edge_pairs(self) -> list[tuple[str, str]]:
        names = self.node_names()
        return list(zip(names, names[1:]))

    def node_contract(self, name: str) -> RuntimeNodeContract:
        for contract in self.node_contracts:
            if contract.name == name:
                return contract
        raise KeyError(f"unknown runtime node: {name}")

    def checkpoint_state(
        self,
        state: ControllerRuntimeState,
        *,
        node: str,
        payload: dict[str, Any] | None = None,
    ) -> RuntimeCheckpoint:
        self.node_contract(node)
        return RuntimeCheckpoint(
            checkpoint_id=f"{state.trace_id}:{node}:checkpoint",
            thread_id=state.thread_id,
            task_id=state.task_id,
            trace_id=state.trace_id,
            node=node,
            state=state.to_dict(),
            payload=deepcopy(dict(payload or {})),
        )

    def resume_from_checkpoint(self, checkpoint: RuntimeCheckpoint) -> ControllerRuntimeState:
        return ControllerRuntimeState.from_dict(checkpoint.state)

    def request_interrupt(
        self,
        state: ControllerRuntimeState,
        *,
        node: str,
        reason: str,
        required_approval: str = "",
        payload: dict[str, Any] | None = None,
    ) -> RuntimeInterrupt:
        self.node_contract(node)
        return RuntimeInterrupt(
            interrupt_id=f"{state.trace_id}:{node}:interrupt",
            thread_id=state.thread_id,
            task_id=state.task_id,
            trace_id=state.trace_id,
            node=node,
            reason=reason,
            required_approval=required_approval,
            payload=deepcopy(dict(payload or {})),
        )

    def stream_event(
        self,
        state: ControllerRuntimeState,
        *,
        node: str,
        status: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.node_contract(node)
        return {
            "event_type": "runtime_node",
            "runtime_topology": self.runtime_topology,
            "trace_id": state.trace_id,
            "task_id": state.task_id,
            "thread_id": state.thread_id,
            "workspace_id": state.workspace_id,
            "node": node,
            "status": status,
            "payload": deepcopy(dict(payload or {})),
        }


def build_single_controller_runtime_harness() -> SingleControllerRuntimeHarness:
    return SingleControllerRuntimeHarness(
        node_contracts=(
            RuntimeNodeContract(
                name="prepare_context",
                input_keys=("goal", "thread_id", "workspace_id", "user_id"),
                output_keys=("context_pack",),
                trace_span="runtime.prepare_context",
                checkpoint_policy="after",
            ),
            RuntimeNodeContract(
                name="intent_and_policy_route",
                input_keys=("goal", "context_pack"),
                output_keys=("policy_decision",),
                trace_span="runtime.intent_and_policy_route",
                checkpoint_policy="after",
            ),
            RuntimeNodeContract(
                name="plan",
                input_keys=("goal", "context_pack", "policy_decision"),
                output_keys=("plan",),
                trace_span="runtime.plan",
                checkpoint_policy="before_and_after",
            ),
            RuntimeNodeContract(
                name="act_react_loop",
                input_keys=("plan", "current_step", "context_pack"),
                output_keys=("tool_calls", "observations"),
                trace_span="runtime.act_react_loop",
                checkpoint_policy="before_and_after",
                failure_policy="checkpoint_and_resume",
            ),
            RuntimeNodeContract(
                name="observe",
                input_keys=("tool_calls", "retrieval_events"),
                output_keys=("observations",),
                trace_span="runtime.observe",
                checkpoint_policy="after",
            ),
            RuntimeNodeContract(
                name="evidence_check",
                input_keys=("observations", "retrieval_events"),
                output_keys=("evidence_verdict",),
                trace_span="runtime.evidence_check",
                checkpoint_policy="after",
            ),
            RuntimeNodeContract(
                name="reflect",
                input_keys=("plan", "observations", "evidence_verdict"),
                output_keys=("reflection",),
                trace_span="runtime.reflect",
                checkpoint_policy="after",
            ),
            RuntimeNodeContract(
                name="replan_if_needed",
                input_keys=("reflection", "plan"),
                output_keys=("plan", "current_step"),
                trace_span="runtime.replan_if_needed",
                checkpoint_policy="after",
            ),
            RuntimeNodeContract(
                name="answer_or_artifact",
                input_keys=("observations", "artifact_refs", "evidence_verdict"),
                output_keys=("answer", "artifact_refs"),
                trace_span="runtime.answer_or_artifact",
                checkpoint_policy="before_and_after",
            ),
            RuntimeNodeContract(
                name="post_turn_commit",
                input_keys=("answer", "memory_candidates", "artifact_refs"),
                output_keys=("runtime_ledger",),
                trace_span="runtime.post_turn_commit",
                checkpoint_policy="after",
            ),
        )
    )


__all__ = [
    "ControllerRuntimeState",
    "RuntimeCheckpoint",
    "RuntimeInterrupt",
    "RuntimeNodeContract",
    "SingleControllerRuntimeHarness",
    "build_single_controller_runtime_harness",
]
