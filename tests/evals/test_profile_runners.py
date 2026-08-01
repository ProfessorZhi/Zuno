from __future__ import annotations

import pytest
from tools.evals.zuno.rag_eval.profile_runners import (
    AgenticGraphRAGProfileRunner,
    BenchmarkCaseInput,
    DeepGraphRAGProfileRunner,
    LocalGraphRAGProfileRunner,
    StandardRAGProfileRunner,
)


def test_standard_rag_profile_runner() -> None:
    runner = StandardRAGProfileRunner()
    assert runner.is_test_double is True
    case_in = BenchmarkCaseInput(
        case_id="case_pub_001",
        question="Were Scott Derrickson and Ed Wood of the same nationality?",
        question_type="multihop_fact",
        gold_document_refs=("doc_scott", "doc_ed"),
        gold_evidence_refs=("ev_1", "ev_2"),
    )
    res = runner.run_case(case_in)
    assert res.status == "contract_smoke_only"
    assert res.is_test_double is True
    assert res.measurement_state == "BLOCKED"
    assert res.profile_name == "standard_rag"
    assert res.standard_floor_preserved is True
    assert "doc_scott" in res.retrieved_doc_refs


def test_local_graphrag_profile_runner() -> None:
    runner = LocalGraphRAGProfileRunner()
    case_in = BenchmarkCaseInput(
        case_id="case_pub_002",
        question="What government position was held by Kiss and Tell actress?",
        question_type="multihop_fact",
        gold_document_refs=("doc_kiss",),
    )
    res = runner.run_case(case_in)
    assert res.status == "contract_smoke_only"
    assert res.is_test_double is True
    assert res.profile_name == "graphrag_local"
    assert len(res.retrieved_doc_refs) >= 1


def test_deep_graphrag_profile_runner() -> None:
    runner = DeepGraphRAGProfileRunner()
    case_in = BenchmarkCaseInput(
        case_id="case_pub_033",
        question="Who is the individual associated with crypto fraud?",
        question_type="multihop_reasoning",
        gold_document_refs=("doc_crypto",),
    )
    res = runner.run_case(case_in)
    assert res.status == "contract_smoke_only"
    assert res.is_test_double is True
    assert res.profile_name == "graphrag_global"
    assert "subqueries" in res.retrieval_trace


def test_agentic_graphrag_profile_runner_standard_floor() -> None:
    runner = AgenticGraphRAGProfileRunner()
    case_in = BenchmarkCaseInput(
        case_id="case_pub_057",
        question="Explain memory aliasing in C procedure swap.",
        question_type="global_summary",
        gold_document_refs=("doc_swap_c",),
    )
    res = runner.run_case(case_in)
    assert res.status == "contract_smoke_only"
    assert res.is_test_double is True
    assert res.profile_name == "agentic_graphrag"
    assert res.standard_floor_preserved is True
    # Verify standard candidate is preserved in final candidate refs
    assert "doc_swap_c" in res.final_candidate_refs
    assert len(res.graph_added_refs) > 0
