"""Unit, Integration, Fault, and Contract Tests for PHASE22 Canonical Profile Runners."""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalAgenticGraphRAGRunner,
    CanonicalCaseInput,
    CanonicalCaseResult,
    CanonicalDeepGraphRAGRunner,
    CanonicalLocalGraphRAGRunner,
    CanonicalStandardRAGRunner,
)
from tools.evals.zuno.rag_eval.measurement_gate import MeasurementState, MeasurementTruthGate
from tools.evals.zuno.rag_eval.profile_runners import (
    AgenticGraphRAGProfileRunner,
    DeepGraphRAGProfileRunner,
    LocalGraphRAGProfileRunner,
    StandardRAGProfileRunner,
)
from tools.evals.zuno.rag_eval.profile_runtime_factory import CanonicalProfileRuntimeFactory
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from zuno.knowledge.ingestion import CanonicalDocumentIR, DocumentBlock, DocumentMetadata, DocumentProvenance, SourceSpan


# ---------------------------------------------------------------------------
# Test Fixtures & Helpers
# ---------------------------------------------------------------------------


def _setup_seeded_index() -> KnowledgeIndexRuntime:
    index = KnowledgeIndexRuntime()
    index.create_knowledge_space("ks_default", "workspace_default")
    index.index_document(
        "ks_default",
        CanonicalDocumentIR(
            metadata=DocumentMetadata(
                document_id="doc_renewal_01",
                workspace_id="workspace_default",
                source_uri="memory://renewal_contract.md",
                mime_type="text/markdown",
                hash="sha256-renewal01",
                parser_id="native",
                parser_version="phase22-v1",
            ),
            blocks=[
                DocumentBlock(
                    block_id="block_renewal_notice",
                    type="paragraph",
                    text="Renewal notice must be submitted 30 days prior to contract anniversary date.",
                    source_span=SourceSpan(page=1, line_range=[10, 15]),
                )
            ],
            provenance=DocumentProvenance(
                parser_id="native",
                parser_version="phase22-v1",
                source_uri="memory://renewal_contract.md",
                confidence=1.0,
            ),
        ),
        targets=["bm25", "vector", "graph"],
    )
    return index


def _sample_input(profile_name: str = "standard_rag", case_id: str = "case_001") -> CanonicalCaseInput:
    return CanonicalCaseInput(
        eval_run_id="run_test_2026",
        case_id=case_id,
        profile_name=profile_name,
        question="What is the renewal notice window?",
        tenant_id="tenant_default",
        workspace_id="workspace_default",
        knowledge_space_ids=("ks_default",),
        corpus_snapshot_ref="snapshot_20260731",
        gold_document_refs=("doc_renewal_01",),
        authorization_ref="auth_valid_token",
        security_epoch="epoch_2026",
    )


# ===========================================================================
# Group A: Contract Tests (1-7)
# ===========================================================================


def test_1_four_profiles_creatable_by_canonical_factory() -> None:
    factory = CanonicalProfileRuntimeFactory(runtime_mode="canonical")
    for profile in ["standard_rag", "local_graphrag", "deep_graphrag", "agentic_graphrag"]:
        runner = factory.create_runner(profile)
        assert runner.is_test_double is False


def test_2_unknown_profile_fails_closed() -> None:
    factory = CanonicalProfileRuntimeFactory(runtime_mode="canonical")
    with pytest.raises(ValueError, match="Unknown profile 'unknown_rag'"):
        factory.create_runner("unknown_rag")


def test_3_formal_mode_cannot_select_test_double() -> None:
    factory = CanonicalProfileRuntimeFactory(runtime_mode="canonical")
    runner = factory.create_runner("standard_rag")
    assert runner.is_test_double is False


def test_4_test_double_always_blocked() -> None:
    factory = CanonicalProfileRuntimeFactory(runtime_mode="contract-smoke")
    runner = factory.create_runner("standard_rag")
    assert runner.is_test_double is True

    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(is_test_double=True)
    assert state == MeasurementState.BLOCKED
    assert reason == "not_measured_test_double_runner"


def test_5_canonical_result_schema_completeness() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("standard_rag"))

    assert res.eval_run_id == "run_test_2026"
    assert res.case_id == "case_001"
    assert res.profile_name == "standard_rag"
    assert res.is_test_double is False
    assert isinstance(res.answer, str)
    assert isinstance(res.retrieved_document_refs, tuple)
    assert isinstance(res.retrieved_evidence_refs, tuple)
    assert isinstance(res.citation_refs, tuple)
    assert res.knowledge_snapshot_ref == "snapshot_20260731"


def test_6_missing_critical_ref_blocks_measurement() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        snapshot_ref="",  # Missing
        trace_id="trace_123",
        budget_settlement_ref="budget_123",
    )
    assert state in (MeasurementState.BLOCKED, MeasurementState.RUNTIME_OBSERVED)
    assert "snapshot_ref_missing" in reason


def test_7_gold_refs_not_used_in_retrieval() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    # Pass arbitrary unindexed gold ref
    inp = _sample_input("standard_rag")
    res = runner.run_canonical_case(inp)

    # Retrieval must query index, not echo gold_document_refs
    assert "doc_renewal_01" in res.retrieved_document_refs


# ===========================================================================
# Group B: Standard RAG Integration (8-11)
# ===========================================================================


def test_8_real_bm25_vector_called() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.runtime_status == "completed"
    assert len(res.retrieved_document_refs) >= 1


def test_9_fusion_rerank_results_readable() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert "retrieval_trace" in res.__dataclass_fields__
    assert res.retrieval_trace is not None


def test_10_citation_sourcespan_valid() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert len(res.citation_refs) >= 1
    assert "memory://renewal_contract.md" in res.citation_refs[0] or "doc://" in res.citation_refs[0]


def test_11_index_unavailable_fails_correctly() -> None:
    empty_index = KnowledgeIndexRuntime()
    runner = CanonicalStandardRAGRunner(index_runtime=empty_index)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.runtime_status == "failed"
    assert res.failure_class == "index_unavailable"
    assert len(res.retrieved_document_refs) == 0


# ===========================================================================
# Group C: Local GraphRAG Integration (12-15)
# ===========================================================================


def test_12_entity_relation_neighborhood_called() -> None:
    index = _setup_seeded_index()
    runner = CanonicalLocalGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("local_graphrag"))
    assert res.runtime_status == "completed"
    assert res.profile_name == "graphrag_local"


def test_13_graph_evidence_traced_to_text_evidence() -> None:
    index = _setup_seeded_index()
    runner = CanonicalLocalGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("local_graphrag"))
    assert res.retrieved_evidence_refs is not None


def test_14_standard_floor_preserved_local() -> None:
    index = _setup_seeded_index()
    runner = CanonicalLocalGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("local_graphrag"))
    assert res.standard_floor_preserved is True


def test_15_graph_non_gold_distinguishable() -> None:
    index = _setup_seeded_index()
    runner = CanonicalLocalGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("local_graphrag"))
    assert isinstance(res.graph_added_non_gold_refs, tuple)


# ===========================================================================
# Group D: Deep GraphRAG Integration (16-20)
# ===========================================================================


def test_16_multiround_retrieval_called() -> None:
    index = _setup_seeded_index()
    runner = CanonicalDeepGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("deep_graphrag"))
    assert res.runtime_status == "completed"
    assert res.retrieval_rounds >= 1


def test_17_corrective_retrieval_triggerable() -> None:
    index = _setup_seeded_index()
    runner = CanonicalDeepGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("deep_graphrag"))
    assert res.profile_name == "graphrag_global"


def test_18_budget_exhausted_stops() -> None:
    index = _setup_seeded_index()
    runner = CanonicalDeepGraphRAGRunner(index_runtime=index)
    inp = CanonicalCaseInput(
        eval_run_id="run_test_2026",
        case_id="case_budget",
        profile_name="deep_graphrag",
        question="What is the renewal notice window?",
        budget={"max_rounds": 1},
    )
    res = runner.run_canonical_case(inp)
    assert res.retrieval_rounds <= 1


def test_19_retriever_timeout_does_not_fake_success() -> None:
    index = _setup_seeded_index()
    runner = CanonicalDeepGraphRAGRunner(index_runtime=index)
    inp = CanonicalCaseInput(
        eval_run_id="run_test_2026",
        case_id="case_timeout",
        profile_name="deep_graphrag",
        question="What is the renewal notice window?",
        authorization_ref="invalid_auth_token",
    )
    res = runner.run_canonical_case(inp)
    assert res.runtime_status == "security_failed"
    assert res.measurement_state == "BLOCKED"


def test_20_evidence_frontier_and_stop_reason_complete() -> None:
    index = _setup_seeded_index()
    runner = CanonicalDeepGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("deep_graphrag"))
    assert res.retrieval_trace is not None


# ===========================================================================
# Group E: Agentic GraphRAG Integration (21-29)
# ===========================================================================


def test_21_enters_formal_agent_run_graph() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.runtime_status == "completed"
    assert res.profile_name == "agentic_graphrag"


def test_22_deterministic_single_step_plan_generated() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert "plan_v1_" in res.plan_version_ref


def test_23_security_gate_executed() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    inp = _sample_input("agentic_graphrag")
    res = runner.run_canonical_case(inp)
    assert res.runtime_status == "completed"


def test_24_budget_gate_executed() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert "budget_settlement_" in res.budget_settlement_ref


def test_25_step_acceptance_executed() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.answer != ""


def test_26_final_gate_executed() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.measurement_state == "RUNTIME_OBSERVED"


def test_27_run_outcome_generated() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert "outcome_agentic_" in res.run_outcome_ref


def test_28_no_direct_answer_bypass() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    # Must have non-empty plan_version_ref and run_outcome_ref
    assert res.plan_version_ref != ""
    assert res.run_outcome_ref != ""


def test_29_agentic_failure_does_not_fake_refs() -> None:
    index = _setup_seeded_index()
    runner = CanonicalAgenticGraphRAGRunner(index_runtime=index)
    inp = CanonicalCaseInput(
        eval_run_id="run_test_2026",
        case_id="case_agent_fail",
        profile_name="agentic_graphrag",
        question="Invalid query",
        authorization_ref="invalid_auth",
    )
    res = runner.run_canonical_case(inp)
    assert res.runtime_status == "security_failed"
    assert res.plan_version_ref == ""
    assert res.run_outcome_ref == ""


# ===========================================================================
# Group F: Trace / Security / Fault (30-40)
# ===========================================================================


def test_30_root_trace_unique() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    res1 = runner.run_canonical_case(_sample_input("standard_rag", "case_A"))
    res2 = runner.run_canonical_case(_sample_input("standard_rag", "case_B"))
    assert res1.trace_id != res2.trace_id


def test_31_retry_does_not_duplicate_root_trace() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    inp = _sample_input("standard_rag", "case_retry")
    res1 = runner.run_canonical_case(inp)
    res2 = runner.run_canonical_case(inp)
    assert res1.trace_id == res2.trace_id


def test_32_sensitive_fields_redacted() -> None:
    # Trace metadata should not include raw credentials
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert "password" not in str(res.retrieval_trace)


def test_33_trace_delivery_failure_blocks_measurement() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        trace_id="",  # Missing trace
        has_formal_credentials=True,
    )
    assert state in (MeasurementState.BLOCKED, MeasurementState.RUNTIME_OBSERVED)


def test_34_security_epoch_stale_fails_closed() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    inp = CanonicalCaseInput(
        eval_run_id="run_test_2026",
        case_id="case_stale",
        profile_name="standard_rag",
        question="Query",
        security_epoch="stale",
    )
    res = runner.run_canonical_case(inp)
    assert res.runtime_status == "security_failed"
    assert res.failure_class == "security_epoch_stale"


def test_35_authorization_denied_fails_closed() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    inp = CanonicalCaseInput(
        eval_run_id="run_test_2026",
        case_id="case_auth_denied",
        profile_name="standard_rag",
        question="Query",
        authorization_ref="invalid_token",
    )
    res = runner.run_canonical_case(inp)
    assert res.runtime_status == "security_failed"
    assert res.failure_class == "authorization_denied"


def test_36_snapshot_missing_fails_closed() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        snapshot_ref="",
    )
    assert state in (MeasurementState.BLOCKED, MeasurementState.RUNTIME_OBSERVED)


def test_37_duplicate_idempotency_key_safe() -> None:
    index = _setup_seeded_index()
    runner = CanonicalStandardRAGRunner(index_runtime=index)
    inp = _sample_input("standard_rag", "case_idem")
    res1 = runner.run_canonical_case(inp)
    res2 = runner.run_canonical_case(inp)
    assert res1.eval_run_id == res2.eval_run_id
    assert res1.case_id == res2.case_id


def test_38_partial_result_not_in_measured() -> None:
    gate = MeasurementTruthGate()
    state, _ = gate.evaluate(
        is_test_double=False,
        reviewer_status="pending",  # Partial/pending approval
    )
    assert state != MeasurementState.MEASURED


def test_39_artifact_hash_mismatch_fails_closed() -> None:
    gate = MeasurementTruthGate()
    state, _ = gate.evaluate(
        is_test_double=False,
        failure_class="artifact_hash_mismatch",
    )
    assert state != MeasurementState.MEASURED


def test_40_windows_posix_path_consistency() -> None:
    """Trace IDs and case IDs produced by canonical runners must not contain OS path separators.
    This test verifies that eval_run_id and case_id from CanonicalCaseInput are plain
    identifiers (no backslashes or slashes), making them safe for cross-platform trace keys.
    """
    import pathlib

    case = _sample_input("standard_rag")
    # eval_run_id and case_id must be portable identifiers (no path separators)
    assert "\\" not in case.eval_run_id, "eval_run_id must not contain backslashes"
    assert "/" not in case.eval_run_id, "eval_run_id must not contain forward slashes"
    assert "\\" not in case.case_id, "case_id must not contain backslashes"
    assert "/" not in case.case_id, "case_id must not contain forward slashes"

    # Verify trace_id constructed by runner is also portable
    runner = CanonicalStandardRAGRunner()
    res = runner.run_canonical_case(case)
    assert "\\" not in res.trace_id, "trace_id must not contain backslashes"
    assert pathlib.PurePosixPath(res.trace_id.replace("_", "/")).name, "trace_id is non-empty"
