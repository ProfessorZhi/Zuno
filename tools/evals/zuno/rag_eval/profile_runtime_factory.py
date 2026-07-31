"""Zuno Benchmark Profile Runtime Factory.

Enforces strict separation between Contract Test Doubles ('contract-smoke')
and Production-Grade Canonical Profile Runners ('canonical').

canonical mode rules:
- Requires an explicit CanonicalRuntimeDependencies bundle from Composition Root.
- MUST NOT create KnowledgeIndexRuntime, AgentControlRuntime, or any other
  infrastructure object internally.
- Missing required dependency -> raises RuntimeError (fail closed). No fallback.

contract-smoke mode rules:
- Uses local Test Double runners (BenchmarkProfileRunner subclasses).
- May use in-memory adapters.
- Must NOT be used for formal measurement.
"""

from __future__ import annotations

from typing import Literal, Optional

from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalAgenticGraphRAGRunner,
    CanonicalBenchmarkProfileRunner,
    CanonicalDeepGraphRAGRunner,
    CanonicalLocalGraphRAGRunner,
    CanonicalRuntimeDependencies,
    CanonicalStandardRAGRunner,
)
from tools.evals.zuno.rag_eval.profile_runners import (
    AgenticGraphRAGProfileRunner,
    BenchmarkProfileRunner,
    DeepGraphRAGProfileRunner,
    LocalGraphRAGProfileRunner,
    StandardRAGProfileRunner,
)
from zuno.platform.observability.trace_adapter import ObservabilityTracePort


VALID_PROFILES = frozenset({
    "standard_rag",
    "local_graphrag",
    "deep_graphrag",
    "agentic_graphrag",
})


class CanonicalProfileRuntimeFactory:
    """Factory for creating benchmark profile runners.

    In canonical mode the factory requires an explicit CanonicalRuntimeDependencies
    bundle. It will never create KnowledgeIndexRuntime or other infrastructure itself.
    Missing deps -> RuntimeError (fail closed, no silent downgrade).
    """

    def __init__(
        self,
        runtime_mode: Literal["contract-smoke", "canonical"] = "canonical",
        canonical_deps: Optional[CanonicalRuntimeDependencies] = None,
        trace_adapter: Optional[ObservabilityTracePort] = None,
    ) -> None:
        if runtime_mode not in ("contract-smoke", "canonical"):
            raise ValueError(
                f"Invalid runtime_mode '{runtime_mode}'. Must be 'contract-smoke' or 'canonical'."
            )
        self.runtime_mode = runtime_mode
        self._canonical_deps = canonical_deps
        self._trace_adapter = trace_adapter

        if runtime_mode == "canonical" and canonical_deps is None:
            raise RuntimeError(
                "canonical mode requires an explicit CanonicalRuntimeDependencies bundle. "
                "No auto-creation of infrastructure is permitted. "
                "Provide deps from a Composition Root."
            )

    def create_runner(self, profile_name: str) -> BenchmarkProfileRunner | CanonicalBenchmarkProfileRunner:
        if profile_name not in VALID_PROFILES:
            raise ValueError(
                f"Unknown profile '{profile_name}'. "
                f"Must be one of {sorted(VALID_PROFILES)}. No fallback permitted."
            )

        if self.runtime_mode == "contract-smoke":
            return self._create_smoke_runner(profile_name)

        return self._create_canonical_runner(profile_name)

    def _create_smoke_runner(self, profile_name: str) -> BenchmarkProfileRunner:
        runners = {
            "standard_rag": StandardRAGProfileRunner,
            "local_graphrag": LocalGraphRAGProfileRunner,
            "deep_graphrag": DeepGraphRAGProfileRunner,
            "agentic_graphrag": AgenticGraphRAGProfileRunner,
        }
        cls = runners[profile_name]
        if self._trace_adapter is not None:
            return cls(trace_adapter=self._trace_adapter)
        return cls()

    def _create_canonical_runner(self, profile_name: str) -> CanonicalBenchmarkProfileRunner:
        # deps was validated non-None in __init__; assert for type checker
        assert self._canonical_deps is not None
        # Inject trace_adapter override into deps if provided
        deps = self._canonical_deps
        if self._trace_adapter is not None and deps.trace_adapter is None:
            deps = CanonicalRuntimeDependencies(
                knowledge_runtime=deps.knowledge_runtime,
                index_runtime=deps.index_runtime,
                trace_adapter=self._trace_adapter,
            )

        runners = {
            "standard_rag": CanonicalStandardRAGRunner,
            "local_graphrag": CanonicalLocalGraphRAGRunner,
            "deep_graphrag": CanonicalDeepGraphRAGRunner,
            "agentic_graphrag": CanonicalAgenticGraphRAGRunner,
        }
        cls = runners[profile_name]
        return cls(deps)
