from __future__ import annotations

from zuno.agent.runtime.reflection.critic import OptionalCritic
from zuno.agent.runtime.reflection.deterministic import DeterministicReflectionGate, ReflectionGateResult
from zuno.agent.runtime.state import AgentRuntimeState


class ReflectionEngine:
    def __init__(
        self,
        *,
        deterministic_gate: DeterministicReflectionGate | None = None,
        critic: OptionalCritic | None = None,
    ) -> None:
        self.deterministic_gate = deterministic_gate or DeterministicReflectionGate()
        self.critic = critic or OptionalCritic()

    def decide(self, state: AgentRuntimeState) -> ReflectionGateResult:
        deterministic = self.deterministic_gate.decide(state)
        return self.critic.evaluate(state, deterministic)


__all__ = ["ReflectionEngine"]
