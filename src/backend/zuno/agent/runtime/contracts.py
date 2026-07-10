from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ObservationKind(StrEnum):
    MODEL = "model"
    RETRIEVAL = "retrieval"
    TOOL = "tool"
    GATE = "gate"
    REFLECTION = "reflection"
    REPLAN = "replan"
    MEMORY = "memory"
    SYSTEM = "system"


class ObservationStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    WAITING = "waiting"


class StrategyMode(StrEnum):
    DIRECT_ANSWER = "direct_answer"
    REACT = "react"
    PLAN_EXECUTE = "plan_execute"
    PLAN_EXECUTE_WITH_REPLAN = "plan_execute_with_replan"
    REFLECTION_ENABLED = "reflection_enabled"
    REFLEXION_ENABLED = "reflexion_enabled"


class ReflectionDecision(StrEnum):
    PASS = "pass"
    REWRITE_ANSWER = "rewrite_answer"
    RETRIEVE_MORE = "retrieve_more"
    USE_TOOL = "use_tool"
    ASK_USER = "ask_user"
    ABSTAIN = "abstain"
    REPLAN = "replan"
    REFUSE = "refuse"


class FinalizationStatus(StrEnum):
    NOT_READY = "not_ready"
    FINALIZED = "finalized"
    ABSTAINED = "abstained"
    INTERRUPTED = "interrupted"
    BLOCKED = "blocked"
    FAILED = "failed"


class RuntimeLimits(BaseModel):
    max_steps: int = 8
    max_replans: int = 2
    max_reflections: int = 3
    max_actions_per_step: int = 4
    timeout_ms: int | None = None
    token_budget: int | None = None
    cost_budget: float | None = None


class RuntimeCounters(BaseModel):
    steps_executed: int = 0
    replans: int = 0
    reflections: int = 0
    retrieval_rounds: int = 0
    tool_calls: int = 0
    model_calls: int = 0
    interrupts: int = 0


class NormalizedObservation(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    observation_id: str
    step_id: str | None = None
    kind: ObservationKind = ObservationKind.SYSTEM
    status: ObservationStatus = ObservationStatus.COMPLETED
    source: str = ""
    summary: str = ""
    payload_ref: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)
    tool_id: str | None = None
    trace_span_id: str | None = None
    failure_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StrategyDecision(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    mode: StrategyMode
    reason: str = ""
    selected_skill_id: str | None = None
    retrieval_profile: str | None = None
    trace_event_ids: list[str] = Field(default_factory=list)


class NodeOutcome(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    node: str
    status: ObservationStatus = ObservationStatus.COMPLETED
    route: str | None = None
    observations: list[NormalizedObservation] = Field(default_factory=list)
    counters_delta: RuntimeCounters = Field(default_factory=RuntimeCounters)
    failure_code: str | None = None
    trace_event_ids: list[str] = Field(default_factory=list)


__all__ = [
    "FinalizationStatus",
    "NodeOutcome",
    "NormalizedObservation",
    "ObservationKind",
    "ObservationStatus",
    "ReflectionDecision",
    "RuntimeCounters",
    "RuntimeLimits",
    "StrategyDecision",
    "StrategyMode",
]
