from __future__ import annotations

from zuno.agent.runtime.adapters import (
    normalized_observation_from_controller_payload,
    normalized_observation_from_runtime_observation,
    runtime_state_from_controller_state,
    runtime_state_from_planner_output,
)
from zuno.agent.runtime.contracts import (
    FinalizationStatus,
    NodeOutcome,
    NormalizedObservation,
    ObservationKind,
    ObservationStatus,
    ReflectionDecision,
    RuntimeCounters,
    RuntimeLimits,
    StrategyDecision,
    StrategyMode,
)
from zuno.agent.runtime.graph import build_agent_graph
from zuno.agent.runtime.phase08 import (
    PHASE08_RUN_SCHEMA,
    PHASE08_STEP_SCHEMA,
    Phase08Conflict,
    Phase08RuntimeError,
    Phase08RunService,
    Phase08SignalRecord,
    Phase08StepService,
    append_signal,
    build_phase08_run_graph,
    build_phase08_step_graph,
    reconcile_generations,
)
from zuno.agent.runtime.phase08_cutover import (
    Phase08CutoverController,
    Phase08CutoverError,
    Phase08RuntimeRequest,
    Phase08RuntimeResponse,
    SideEffectLedger,
)
from zuno.agent.runtime.factory import RuntimeAssembly, RuntimeDependencyFactory
from zuno.agent.runtime.planning import (
    PlanExecutor,
    PlanValidationError,
    PlanValidator,
    RuntimePlanner,
    RuntimeStrategySelector,
)
from zuno.agent.runtime.routing import RuntimeNode, route_after_reflection, route_after_strategy
from zuno.agent.runtime.service import RuntimeStartRequest, RuntimeStreamEvent, UnifiedAgentRuntimeService
from zuno.agent.runtime.state import (
    AGENT_RUNTIME_STATE_VERSION,
    AgentRuntimeSnapshot,
    AgentRuntimeState,
    UnsupportedRuntimeStateVersion,
)
from zuno.agent.runtime.store import AgentRunStore
from zuno.agent.runtime.sqlite_store import SQLiteAgentRunStore

__all__ = [
    "AGENT_RUNTIME_STATE_VERSION",
    "AgentRuntimeSnapshot",
    "AgentRuntimeState",
    "AgentRunStore",
    "FinalizationStatus",
    "NodeOutcome",
    "NormalizedObservation",
    "ObservationKind",
    "ObservationStatus",
    "PlanExecutor",
    "PlanValidationError",
    "PlanValidator",
    "PHASE08_RUN_SCHEMA",
    "PHASE08_STEP_SCHEMA",
    "ReflectionDecision",
    "Phase08Conflict",
    "Phase08CutoverController",
    "Phase08CutoverError",
    "Phase08RuntimeError",
    "Phase08RuntimeRequest",
    "Phase08RuntimeResponse",
    "Phase08RunService",
    "Phase08SignalRecord",
    "Phase08StepService",
    "RuntimeCounters",
    "RuntimeLimits",
    "RuntimeAssembly",
    "RuntimeDependencyFactory",
    "RuntimeNode",
    "RuntimePlanner",
    "RuntimeStartRequest",
    "RuntimeStreamEvent",
    "RuntimeStrategySelector",
    "SQLiteAgentRunStore",
    "SideEffectLedger",
    "StrategyDecision",
    "StrategyMode",
    "UnsupportedRuntimeStateVersion",
    "UnifiedAgentRuntimeService",
    "build_agent_graph",
    "build_phase08_run_graph",
    "build_phase08_step_graph",
    "append_signal",
    "reconcile_generations",
    "normalized_observation_from_controller_payload",
    "normalized_observation_from_runtime_observation",
    "runtime_state_from_controller_state",
    "runtime_state_from_planner_output",
    "route_after_reflection",
    "route_after_strategy",
]
