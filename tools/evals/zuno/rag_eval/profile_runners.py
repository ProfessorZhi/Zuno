"""Zuno Benchmark Profile Runners and Contract Test Doubles.

NOTE:
- The profile runner implementations in this module (StandardRAGProfileRunner,
  LocalGraphRAGProfileRunner, DeepGraphRAGProfileRunner, AgenticGraphRAGProfileRunner)
  are Deterministic Profile Test Doubles (Contract Doubles) used ONLY for contract
  validation, smoke testing, and data flow verification.
- Canonical runtime integration (real retrievers, AgentRunGraph, planning/security/budget
  gates) is NOT implemented in these test doubles.
- Test doubles MUST output status 'contract_smoke_only' and MUST NOT be used to write
  formal benchmark MEASURED evidence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, List, Optional

from zuno.platform.observability.trace_adapter import ObservabilityTracePort, get_observability_adapter


@dataclass(frozen=True, slots=True)
class BenchmarkCaseInput:
    case_id: str
    question: str
    question_type: str
    gold_document_refs: tuple[str, ...] = ()
    gold_evidence_refs: tuple[str, ...] = ()
    corpus_snapshot_ref: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BenchmarkCaseResult:
    case_id: str
    profile_name: str
    status: str
    answer: str
    retrieved_doc_refs: tuple[str, ...]
    retrieved_evidence_refs: tuple[str, ...]
    standard_floor_preserved: bool
    is_test_double: bool = True
    measurement_state: str = "BLOCKED"
    blocked_reason: str = "not_measured_test_double_runner"
    standard_candidate_refs: tuple[str, ...] = ()
    graph_added_refs: tuple[str, ...] = ()
    graph_added_gold_refs: tuple[str, ...] = ()
    graph_added_non_gold_refs: tuple[str, ...] = ()
    rerank_demoted_standard_gold: tuple[str, ...] = ()
    final_candidate_refs: tuple[str, ...] = ()
    retrieval_trace: dict[str, Any] = field(default_factory=dict)
    cost_latency: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""


class BenchmarkProfileRunner(ABC):
    def __init__(self, trace_adapter: Optional[ObservabilityTracePort] = None) -> None:
        self.trace_adapter = trace_adapter or get_observability_adapter()

    @property
    def is_test_double(self) -> bool:
        return True

    @abstractmethod
    def run_case(self, case_input: BenchmarkCaseInput) -> BenchmarkCaseResult:
        pass


# Base class alias for contract test doubles
DeterministicProfileTestDouble = BenchmarkProfileRunner
BenchmarkProfileContractDouble = BenchmarkProfileRunner


class StandardRAGProfileRunner(BenchmarkProfileRunner):
    """Contract Test Double for Standard RAG profile."""

    def run_case(self, case_input: BenchmarkCaseInput) -> BenchmarkCaseResult:
        span_id = self.trace_adapter.start_span("StandardRAGRun", span_type="RetrievalRound", metadata={"case_id": case_input.case_id})

        # Test Double candidate synthesis for contract verification
        bm25_refs = [f"bm25_{doc}" for doc in case_input.gold_document_refs] or ["doc_std_001"]
        vector_refs = list(case_input.gold_document_refs) or ["doc_std_001"]
        candidates = list(dict.fromkeys(vector_refs + bm25_refs))

        self.trace_adapter.end_span(span_id, outputs={"candidates_count": len(candidates)})
        return BenchmarkCaseResult(
            case_id=case_input.case_id,
            profile_name="standard_rag",
            status="contract_smoke_only",
            answer=f"Standard RAG test double synthesis for {case_input.question[:30]}",
            retrieved_doc_refs=tuple(candidates),
            retrieved_evidence_refs=case_input.gold_evidence_refs,
            standard_floor_preserved=True,
            is_test_double=True,
            measurement_state="BLOCKED",
            blocked_reason="not_measured_test_double_runner",
            standard_candidate_refs=tuple(candidates),
            final_candidate_refs=tuple(candidates),
            retrieval_trace={"bm25": bm25_refs, "vector": vector_refs, "fusion": candidates, "runner_type": "test_double"},
            trace_id=span_id or "trace_std",
        )


class LocalGraphRAGProfileRunner(BenchmarkProfileRunner):
    """Contract Test Double for Local GraphRAG profile."""

    def run_case(self, case_input: BenchmarkCaseInput) -> BenchmarkCaseResult:
        span_id = self.trace_adapter.start_span("LocalGraphRAGRun", span_type="Graph", metadata={"case_id": case_input.case_id})

        local_entity_refs = list(case_input.gold_document_refs) or ["doc_graph_local_001"]
        graph_neighborhood = [f"neighborhood_{ref}" for ref in local_entity_refs]
        all_refs = list(dict.fromkeys(local_entity_refs + graph_neighborhood))

        self.trace_adapter.end_span(span_id, outputs={"neighborhood_nodes": len(all_refs)})
        return BenchmarkCaseResult(
            case_id=case_input.case_id,
            profile_name="graphrag_local",
            status="contract_smoke_only",
            answer=f"Local GraphRAG test double synthesis for {case_input.question[:30]}",
            retrieved_doc_refs=tuple(all_refs),
            retrieved_evidence_refs=case_input.gold_evidence_refs,
            standard_floor_preserved=True,
            is_test_double=True,
            measurement_state="BLOCKED",
            blocked_reason="not_measured_test_double_runner",
            standard_candidate_refs=tuple(local_entity_refs),
            graph_added_refs=tuple(graph_neighborhood),
            final_candidate_refs=tuple(all_refs),
            retrieval_trace={"local_entities": local_entity_refs, "neighborhood": graph_neighborhood, "runner_type": "test_double"},
            trace_id=span_id or "trace_graph_local",
        )


class DeepGraphRAGProfileRunner(BenchmarkProfileRunner):
    """Contract Test Double for Deep GraphRAG profile."""

    def run_case(self, case_input: BenchmarkCaseInput) -> BenchmarkCaseResult:
        span_id = self.trace_adapter.start_span("DeepGraphRAGRun", span_type="Replan", metadata={"case_id": case_input.case_id})

        decomposed_queries = [f"subquery_{i+1}_for_{case_input.case_id}" for i in range(2)]
        deep_refs = list(case_input.gold_document_refs) or ["doc_deep_001"]

        self.trace_adapter.end_span(span_id, outputs={"decomposed_queries": len(decomposed_queries)})
        return BenchmarkCaseResult(
            case_id=case_input.case_id,
            profile_name="graphrag_global",
            status="contract_smoke_only",
            answer=f"Deep GraphRAG test double synthesis for {case_input.question[:30]}",
            retrieved_doc_refs=tuple(deep_refs),
            retrieved_evidence_refs=case_input.gold_evidence_refs,
            standard_floor_preserved=True,
            is_test_double=True,
            measurement_state="BLOCKED",
            blocked_reason="not_measured_test_double_runner",
            standard_candidate_refs=tuple(deep_refs),
            final_candidate_refs=tuple(deep_refs),
            retrieval_trace={"subqueries": decomposed_queries, "deep_candidates": deep_refs, "runner_type": "test_double"},
            trace_id=span_id or "trace_graph_global",
        )


class AgenticGraphRAGProfileRunner(BenchmarkProfileRunner):
    """Contract Test Double for Agentic GraphRAG profile."""

    def run_case(self, case_input: BenchmarkCaseInput) -> BenchmarkCaseResult:
        span_id = self.trace_adapter.start_span("AgentRun", span_type="AgentRun", metadata={"case_id": case_input.case_id})

        # 1. Standard candidates
        std_candidates = list(case_input.gold_document_refs) or ["doc_std_floor"]
        # 2. Graph & Deep additions
        graph_added = [f"graph_node_{doc}" for doc in std_candidates]
        deep_added = [f"deep_node_{doc}" for doc in std_candidates]

        # 3. Standard Floor Fusion
        all_candidates = std_candidates + graph_added + deep_added
        dedup_candidates = list(dict.fromkeys(all_candidates))

        floor_preserved = all(ref in dedup_candidates for ref in std_candidates)

        graph_gold = [g for g in graph_added if any(gold in g for gold in case_input.gold_document_refs)]
        graph_non_gold = [g for g in graph_added if g not in graph_gold]

        self.trace_adapter.end_span(span_id, outputs={
            "agent_plan": "multi_round_search_and_reflect",
            "floor_preserved": floor_preserved,
        })

        return BenchmarkCaseResult(
            case_id=case_input.case_id,
            profile_name="agentic_graphrag",
            status="contract_smoke_only",
            answer=f"Agentic GraphRAG test double plan-reflect synthesis for {case_input.question[:30]}",
            retrieved_doc_refs=tuple(dedup_candidates),
            retrieved_evidence_refs=case_input.gold_evidence_refs,
            standard_floor_preserved=floor_preserved,
            is_test_double=True,
            measurement_state="BLOCKED",
            blocked_reason="not_measured_test_double_runner",
            standard_candidate_refs=tuple(std_candidates),
            graph_added_refs=tuple(graph_added),
            graph_added_gold_refs=tuple(graph_gold),
            graph_added_non_gold_refs=tuple(graph_non_gold),
            rerank_demoted_standard_gold=(),
            final_candidate_refs=tuple(dedup_candidates),
            retrieval_trace={
                "agent_plan": ["step1_standard", "step2_graph_explore", "step3_evidence_acceptance", "step4_synthesis"],
                "standard_floor_candidates": std_candidates,
                "fusion_candidates": dedup_candidates,
                "runner_type": "test_double",
            },
            trace_id=span_id or "trace_agentic",
        )


__all__ = [
    "BenchmarkCaseInput",
    "BenchmarkCaseResult",
    "BenchmarkProfileRunner",
    "DeterministicProfileTestDouble",
    "BenchmarkProfileContractDouble",
    "StandardRAGProfileRunner",
    "LocalGraphRAGProfileRunner",
    "DeepGraphRAGProfileRunner",
    "AgenticGraphRAGProfileRunner",
]
