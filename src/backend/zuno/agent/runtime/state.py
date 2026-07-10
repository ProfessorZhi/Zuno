from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from zuno.agent.contracts import CapabilityPlan, ContextPack, PlanState, RetrievalPlan
from zuno.agent.runtime.contracts import (
    FinalizationStatus,
    NormalizedObservation,
    ReflectionDecision,
    RuntimeCounters,
    RuntimeLimits,
    StrategyDecision,
)


AGENT_RUNTIME_STATE_VERSION = "agent-runtime-v1"


class UnsupportedRuntimeStateVersion(ValueError):
    pass


class AgentRuntimeSnapshot(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    state_version: str = AGENT_RUNTIME_STATE_VERSION
    run_id: str
    thread_id: str
    workspace_id: str
    user_id: str
    task_id: str
    trace_id: str
    goal: str
    current_node: str = ""
    current_step_id: str | None = None
    context_pack: ContextPack | None = None
    strategy: StrategyDecision | None = None
    plan_state: PlanState | None = None
    retrieval_plan: RetrievalPlan | None = None
    capability_plan: CapabilityPlan = Field(default_factory=CapabilityPlan)
    observations: list[NormalizedObservation] = Field(default_factory=list)
    node_outcomes: list[dict[str, Any]] = Field(default_factory=list)
    reflection_decision: ReflectionDecision | None = None
    finalization_status: FinalizationStatus = FinalizationStatus.NOT_READY
    limits: RuntimeLimits = Field(default_factory=RuntimeLimits)
    counters: RuntimeCounters = Field(default_factory=RuntimeCounters)
    evidence_refs: list[str] = Field(default_factory=list)
    artifact_refs: list[str] = Field(default_factory=list)
    memory_candidate_refs: list[str] = Field(default_factory=list)
    interrupt_refs: list[str] = Field(default_factory=list)
    checkpoint_refs: list[str] = Field(default_factory=list)
    trace_event_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _reject_unknown_version(cls, data: Any) -> Any:
        if isinstance(data, dict):
            version = data.get("state_version", AGENT_RUNTIME_STATE_VERSION)
            if version != AGENT_RUNTIME_STATE_VERSION:
                raise UnsupportedRuntimeStateVersion(f"unsupported AgentRuntimeState version: {version}")
        return data

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "AgentRuntimeSnapshot":
        version = payload.get("state_version", AGENT_RUNTIME_STATE_VERSION)
        if version != AGENT_RUNTIME_STATE_VERSION:
            raise UnsupportedRuntimeStateVersion(f"unsupported AgentRuntimeState version: {version}")
        return cls.model_validate(payload)


@dataclass(slots=True)
class AgentRuntimeState:
    run_id: str
    thread_id: str
    workspace_id: str
    user_id: str
    task_id: str
    trace_id: str
    goal: str
    current_node: str = ""
    current_step_id: str | None = None
    context_pack: ContextPack | None = None
    strategy: StrategyDecision | None = None
    plan_state: PlanState | None = None
    retrieval_plan: RetrievalPlan | None = None
    capability_plan: CapabilityPlan = field(default_factory=CapabilityPlan)
    observations: list[NormalizedObservation] = field(default_factory=list)
    node_outcomes: list[dict[str, Any]] = field(default_factory=list)
    reflection_decision: ReflectionDecision | None = None
    finalization_status: FinalizationStatus = FinalizationStatus.NOT_READY
    limits: RuntimeLimits = field(default_factory=RuntimeLimits)
    counters: RuntimeCounters = field(default_factory=RuntimeCounters)
    evidence_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    memory_candidate_refs: list[str] = field(default_factory=list)
    interrupt_refs: list[str] = field(default_factory=list)
    checkpoint_refs: list[str] = field(default_factory=list)
    trace_event_ids: list[str] = field(default_factory=list)

    def to_snapshot(self) -> AgentRuntimeSnapshot:
        return AgentRuntimeSnapshot(
            run_id=self.run_id,
            thread_id=self.thread_id,
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            task_id=self.task_id,
            trace_id=self.trace_id,
            goal=self.goal,
            current_node=self.current_node,
            current_step_id=self.current_step_id,
            context_pack=self.context_pack,
            strategy=self.strategy,
            plan_state=self.plan_state,
            retrieval_plan=self.retrieval_plan,
            capability_plan=self.capability_plan,
            observations=list(self.observations),
            node_outcomes=list(self.node_outcomes),
            reflection_decision=self.reflection_decision,
            finalization_status=self.finalization_status,
            limits=self.limits,
            counters=self.counters,
            evidence_refs=list(self.evidence_refs),
            artifact_refs=list(self.artifact_refs),
            memory_candidate_refs=list(self.memory_candidate_refs),
            interrupt_refs=list(self.interrupt_refs),
            checkpoint_refs=list(self.checkpoint_refs),
            trace_event_ids=list(self.trace_event_ids),
        )

    @classmethod
    def from_snapshot(cls, snapshot: AgentRuntimeSnapshot) -> "AgentRuntimeState":
        return cls(
            run_id=snapshot.run_id,
            thread_id=snapshot.thread_id,
            workspace_id=snapshot.workspace_id,
            user_id=snapshot.user_id,
            task_id=snapshot.task_id,
            trace_id=snapshot.trace_id,
            goal=snapshot.goal,
            current_node=snapshot.current_node,
            current_step_id=snapshot.current_step_id,
            context_pack=snapshot.context_pack,
            strategy=snapshot.strategy,
            plan_state=snapshot.plan_state,
            retrieval_plan=snapshot.retrieval_plan,
            capability_plan=snapshot.capability_plan,
            observations=list(snapshot.observations),
            node_outcomes=list(snapshot.node_outcomes),
            reflection_decision=snapshot.reflection_decision,
            finalization_status=snapshot.finalization_status,
            limits=snapshot.limits,
            counters=snapshot.counters,
            evidence_refs=list(snapshot.evidence_refs),
            artifact_refs=list(snapshot.artifact_refs),
            memory_candidate_refs=list(snapshot.memory_candidate_refs),
            interrupt_refs=list(snapshot.interrupt_refs),
            checkpoint_refs=list(snapshot.checkpoint_refs),
            trace_event_ids=list(snapshot.trace_event_ids),
        )


__all__ = [
    "AGENT_RUNTIME_STATE_VERSION",
    "AgentRuntimeSnapshot",
    "AgentRuntimeState",
    "UnsupportedRuntimeStateVersion",
]
