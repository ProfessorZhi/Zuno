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
    # Product submission identity + tenant scope (PHASE22 repair; optional
    # with defaults so the state schema stays backward compatible).
    tenant_id: str = "tenant:default"
    principal_id: str = ""
    submission_id: str = ""
    client_request_id: str = ""
    conversation_id: str = ""
    agent_version: str = ""
    content_fingerprint: str = ""
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
    final_candidate_ref: str | None = None
    publication_ref: str | None = None
    run_outcome_ref: str | None = None
    delivery_ref: str | None = None
    memory_candidate_refs: list[str] = Field(default_factory=list)
    interrupt_refs: list[str] = Field(default_factory=list)
    checkpoint_refs: list[str] = Field(default_factory=list)
    trace_event_ids: list[str] = Field(default_factory=list)
    security_summary: dict[str, Any] = Field(default_factory=dict)
    budget_verdict: dict[str, Any] | None = None

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
    tenant_id: str = "tenant:default"
    principal_id: str = ""
    submission_id: str = ""
    client_request_id: str = ""
    conversation_id: str = ""
    agent_version: str = ""
    content_fingerprint: str = ""
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
    final_candidate_ref: str | None = None
    publication_ref: str | None = None
    run_outcome_ref: str | None = None
    delivery_ref: str | None = None
    memory_candidate_refs: list[str] = field(default_factory=list)
    interrupt_refs: list[str] = field(default_factory=list)
    checkpoint_refs: list[str] = field(default_factory=list)
    trace_event_ids: list[str] = field(default_factory=list)
    # Planning-admission gates: seeded by the product surface (single-controller
    # cutover) so security/budget denials block the plan before any tool
    # execution; consumed by RuntimeStrategySelector.
    security_summary: dict[str, Any] = field(default_factory=dict)
    budget_verdict: dict[str, Any] | None = None

    def to_snapshot(self) -> AgentRuntimeSnapshot:
        return AgentRuntimeSnapshot(
            run_id=self.run_id,
            thread_id=self.thread_id,
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            task_id=self.task_id,
            trace_id=self.trace_id,
            goal=self.goal,
            tenant_id=self.tenant_id,
            principal_id=self.principal_id,
            submission_id=self.submission_id,
            client_request_id=self.client_request_id,
            conversation_id=self.conversation_id,
            agent_version=self.agent_version,
            content_fingerprint=self.content_fingerprint,
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
            final_candidate_ref=self.final_candidate_ref,
            publication_ref=self.publication_ref,
            run_outcome_ref=self.run_outcome_ref,
            delivery_ref=self.delivery_ref,
            memory_candidate_refs=list(self.memory_candidate_refs),
            interrupt_refs=list(self.interrupt_refs),
            checkpoint_refs=list(self.checkpoint_refs),
            trace_event_ids=list(self.trace_event_ids),
            security_summary=dict(self.security_summary),
            budget_verdict=dict(self.budget_verdict) if self.budget_verdict else None,
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
            tenant_id=snapshot.tenant_id,
            principal_id=snapshot.principal_id,
            submission_id=snapshot.submission_id,
            client_request_id=snapshot.client_request_id,
            conversation_id=snapshot.conversation_id,
            agent_version=snapshot.agent_version,
            content_fingerprint=snapshot.content_fingerprint,
            current_node=snapshot.current_node,
            current_step_id=snapshot.current_step_id,
            context_pack=snapshot.context_pack,
            strategy=snapshot.strategy,
            plan_state=snapshot.plan_state,
            retrieval_plan=snapshot.retrieval_plan,
            capability_plan=snapshot.capability_plan,
            observations=list(snapshot.observations),
            node_outcomes=list(snapshot.node_outcomes),
            reflection_decision=(
                ReflectionDecision(snapshot.reflection_decision)
                if snapshot.reflection_decision is not None
                else None
            ),
            finalization_status=FinalizationStatus(snapshot.finalization_status),
            limits=snapshot.limits,
            counters=snapshot.counters,
            evidence_refs=list(snapshot.evidence_refs),
            artifact_refs=list(snapshot.artifact_refs),
            final_candidate_ref=snapshot.final_candidate_ref,
            publication_ref=snapshot.publication_ref,
            run_outcome_ref=snapshot.run_outcome_ref,
            delivery_ref=snapshot.delivery_ref,
            memory_candidate_refs=list(snapshot.memory_candidate_refs),
            interrupt_refs=list(snapshot.interrupt_refs),
            checkpoint_refs=list(snapshot.checkpoint_refs),
            trace_event_ids=list(snapshot.trace_event_ids),
            security_summary=dict(snapshot.security_summary),
            budget_verdict=dict(snapshot.budget_verdict) if snapshot.budget_verdict else None,
        )


__all__ = [
    "AGENT_RUNTIME_STATE_VERSION",
    "AgentRuntimeSnapshot",
    "AgentRuntimeState",
    "UnsupportedRuntimeStateVersion",
]
