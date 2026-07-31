"""Zuno Benchmark Profile Runtime Factory.

Enforces strict separation between Contract Test Doubles ('contract-smoke')
and Production-Grade Canonical Profile Runners ('canonical').
"""

from __future__ import annotations

from typing import Literal

from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalAgenticGraphRAGRunner,
    CanonicalBenchmarkProfileRunner,
    CanonicalDeepGraphRAGRunner,
    CanonicalLocalGraphRAGRunner,
    CanonicalStandardRAGRunner,
)
from tools.evals.zuno.rag_eval.profile_runners import (
    AgenticGraphRAGProfileRunner,
    BenchmarkProfileRunner,
    DeepGraphRAGProfileRunner,
    LocalGraphRAGProfileRunner,
    StandardRAGProfileRunner,
)
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from zuno.platform.observability.trace_adapter import ObservabilityTracePort


VALID_PROFILES = {
    "standard_rag",
    "local_graphrag",
    "deep_graphrag",
    "agentic_graphrag",
}


class CanonicalProfileRuntimeFactory:
    """Factory for creating benchmark profile runners."""

    def __init__(
        self,
        runtime_mode: Literal["contract-smoke", "canonical"] = "canonical",
        index_runtime: KnowledgeIndexRuntime | None = None,
        trace_adapter: ObservabilityTracePort | None = None,
    ) -> None:
        self.runtime_mode = runtime_mode
        self.index_runtime = index_runtime or KnowledgeIndexRuntime()
        self.trace_adapter = trace_adapter

    def create_runner(self, profile_name: str) -> BenchmarkProfileRunner | CanonicalBenchmarkProfileRunner:
        if profile_name not in VALID_PROFILES:
            raise ValueError(
                f"Unknown profile '{profile_name}'. Must be one of {sorted(VALID_PROFILES)}. No fallback permitted."
            )

        if self.runtime_mode == "contract-smoke":
            if profile_name == "standard_rag":
                return StandardRAGProfileRunner(trace_adapter=self.trace_adapter)
            elif profile_name == "local_graphrag":
                return LocalGraphRAGProfileRunner(trace_adapter=self.trace_adapter)
            elif profile_name == "deep_graphrag":
                return DeepGraphRAGProfileRunner(trace_adapter=self.trace_adapter)
            elif profile_name == "agentic_graphrag":
                return AgenticGraphRAGProfileRunner(trace_adapter=self.trace_adapter)

        elif self.runtime_mode == "canonical":
            if profile_name == "standard_rag":
                return CanonicalStandardRAGRunner(
                    index_runtime=self.index_runtime,
                    trace_adapter=self.trace_adapter,
                )
            elif profile_name == "local_graphrag":
                return CanonicalLocalGraphRAGRunner(
                    index_runtime=self.index_runtime,
                    trace_adapter=self.trace_adapter,
                )
            elif profile_name == "deep_graphrag":
                return CanonicalDeepGraphRAGRunner(
                    index_runtime=self.index_runtime,
                    trace_adapter=self.trace_adapter,
                )
            elif profile_name == "agentic_graphrag":
                return CanonicalAgenticGraphRAGRunner(
                    index_runtime=self.index_runtime,
                    trace_adapter=self.trace_adapter,
                )

        raise ValueError(f"Invalid runtime_mode '{self.runtime_mode}' or configuration error.")
