from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.agent.runtime_batch import (
        AgentRuntimeBatchError,
        AgentRuntimeBatchReport,
        validate_agent_runtime_batch,
    )
    from zuno.agent.control_runtime import AgentControlRuntime, AgentRuntimeResult, RuntimeObservation
    from zuno.agent.context import (
        AgentExecutionContext,
        ContextOrchestrator,
        ContextPackPolicy,
        ContextTrace,
        ModelContextPacket,
    )
    from zuno.agent.harness import (
        ControllerRuntimeState,
        RuntimeCheckpoint,
        RuntimeInterrupt,
        RuntimeNodeContract,
        SingleControllerRuntimeHarness,
        build_single_controller_runtime_harness,
    )
    from zuno.agent.durable_runtime import (
        DurableRuntimeEvent,
        DurableRuntimeTaskSnapshot,
        InMemoryDurableRuntimeStore,
        SingleControllerDurableRuntime,
    )
    from zuno.agent.post_turn import RuntimeTurnLedger
    from zuno.agent.planning import PlanningRequest, StrategySelector, build_default_strategy_selector
    from zuno.agent.runtime import AgentConfig, GeneralAgent
    from zuno.agent.state import StreamAgentState


_EXPORT_TO_MODULE = {
    "AgentConfig": "zuno.agent.runtime",
    "AgentControlRuntime": "zuno.agent.control_runtime",
    "AgentRuntimeBatchError": "zuno.agent.runtime_batch",
    "AgentRuntimeBatchReport": "zuno.agent.runtime_batch",
    "AgentRuntimeResult": "zuno.agent.control_runtime",
    "AgentExecutionContext": "zuno.agent.context",
    "ContextOrchestrator": "zuno.agent.context",
    "ContextPackPolicy": "zuno.agent.context",
    "ContextTrace": "zuno.agent.context",
    "ControllerRuntimeState": "zuno.agent.harness",
    "DurableRuntimeEvent": "zuno.agent.durable_runtime",
    "DurableRuntimeTaskSnapshot": "zuno.agent.durable_runtime",
    "GeneralAgent": "zuno.agent.runtime",
    "InMemoryDurableRuntimeStore": "zuno.agent.durable_runtime",
    "ModelContextPacket": "zuno.agent.context",
    "PlanningRequest": "zuno.agent.planning",
    "RuntimeCheckpoint": "zuno.agent.harness",
    "RuntimeInterrupt": "zuno.agent.harness",
    "RuntimeNodeContract": "zuno.agent.harness",
    "RuntimeObservation": "zuno.agent.control_runtime",
    "RuntimeTurnLedger": "zuno.agent.post_turn",
    "SingleControllerRuntimeHarness": "zuno.agent.harness",
    "SingleControllerDurableRuntime": "zuno.agent.durable_runtime",
    "StrategySelector": "zuno.agent.planning",
    "StreamAgentState": "zuno.agent.state",
    "build_default_strategy_selector": "zuno.agent.planning",
    "build_single_controller_runtime_harness": "zuno.agent.harness",
    "validate_agent_runtime_batch": "zuno.agent.runtime_batch",
}

__all__ = [
    "AgentConfig",
    "AgentControlRuntime",
    "AgentRuntimeBatchError",
    "AgentRuntimeBatchReport",
    "AgentRuntimeResult",
    "AgentExecutionContext",
    "ContextOrchestrator",
    "ContextPackPolicy",
    "ContextTrace",
    "ControllerRuntimeState",
    "DurableRuntimeEvent",
    "DurableRuntimeTaskSnapshot",
    "GeneralAgent",
    "InMemoryDurableRuntimeStore",
    "ModelContextPacket",
    "PlanningRequest",
    "RuntimeCheckpoint",
    "RuntimeInterrupt",
    "RuntimeNodeContract",
    "RuntimeObservation",
    "RuntimeTurnLedger",
    "SingleControllerRuntimeHarness",
    "SingleControllerDurableRuntime",
    "StrategySelector",
    "StreamAgentState",
    "build_default_strategy_selector",
    "build_single_controller_runtime_harness",
    "validate_agent_runtime_batch",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
