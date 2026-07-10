from __future__ import annotations

from zuno.agent.runtime.reflection.deterministic import ReflectionGateResult
from zuno.agent.runtime.state import AgentRuntimeState


class OptionalCritic:
    def evaluate(self, state: AgentRuntimeState, deterministic: ReflectionGateResult) -> ReflectionGateResult:
        del state
        return deterministic


__all__ = ["OptionalCritic"]
