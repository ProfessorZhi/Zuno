from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
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
    from zuno.agent.runtime import AgentConfig, GeneralAgent
    from zuno.agent.state import StreamAgentState


_EXPORT_TO_MODULE = {
    "AgentConfig": "zuno.agent.runtime",
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
    "RuntimeCheckpoint": "zuno.agent.harness",
    "RuntimeInterrupt": "zuno.agent.harness",
    "RuntimeNodeContract": "zuno.agent.harness",
    "RuntimeTurnLedger": "zuno.agent.post_turn",
    "SingleControllerRuntimeHarness": "zuno.agent.harness",
    "SingleControllerDurableRuntime": "zuno.agent.durable_runtime",
    "StreamAgentState": "zuno.agent.state",
    "build_single_controller_runtime_harness": "zuno.agent.harness",
}

__all__ = [
    "AgentConfig",
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
    "RuntimeCheckpoint",
    "RuntimeInterrupt",
    "RuntimeNodeContract",
    "RuntimeTurnLedger",
    "SingleControllerRuntimeHarness",
    "SingleControllerDurableRuntime",
    "StreamAgentState",
    "build_single_controller_runtime_harness",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
