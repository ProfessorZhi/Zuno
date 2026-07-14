from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_observability_eval_target_protocols.py"
FORMAL_PATH = REPO_ROOT / "docs/modules/10-observability-eval.md"
MIRROR_PATH = REPO_ROOT / ".agent/modules/10-observability-eval.md"
RETIRED_PATHS = [
    REPO_ROOT / "docs/modules/10-observability-eval-rag-agent-evaluation.md",
    REPO_ROOT / ".agent/modules/10-observability-eval-rag-agent-evaluation.md",
    REPO_ROOT / "tools/scripts/align_observability_wave1.py",
]


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_observability_eval_target_protocols", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _formal() -> str:
    return FORMAL_PATH.read_text(encoding="utf-8")


def test_observability_eval_protocol_verifier_passes() -> None:
    assert _load_verifier().verify() == []


def test_single_formal_document_and_agent_mirror_are_byte_identical() -> None:
    assert FORMAL_PATH.read_bytes() == MIRROR_PATH.read_bytes()
    for path in RETIRED_PATHS:
        assert not path.exists()


def test_document_has_agent_core_style_parts_and_single_source_boundary() -> None:
    content = _formal()
    for part in [
        "# Part I：定位与概念架构",
        "# Part II：完整运行流程",
        "# Part III：Telemetry、Trace、Audit 与 Delivery Contract",
        "# Part IV：Eval、RAG Core Five 与质量 Contract",
        "# Part V：Agentic GraphRAG 与 Agent Efficiency Contract",
        "# Part VI：状态机、安全、失败与恢复",
        "# Part VII：存储、代码与 API 规格",
        "# Part VIII：Release Gate、测试与完成证据",
    ]:
        assert part in content
    assert "唯一的正式 Target 架构主设计" in content
    assert "不再维护模块 10 的独立架构附录" in content


def test_current_quality_claims_remain_blocked() -> None:
    content = _formal()
    assert "implementation available" in content
    assert "measurement blocked" in content
    assert "quality not yet proven" in content
    assert "QUALITY_PROVEN" in content
    assert "production ready" in content


def test_platform_contracts_and_ownership_are_complete() -> None:
    content = _formal()
    for term in [
        "CrossModuleEnvelopeV1",
        "TelemetryEnvelopeV1",
        "SecurityAuditRequirementV1",
        "AuditDurabilityRequirement",
        "AuditPersistenceReceiptV1",
        "TraceContext",
        "TraceRecord",
        "SpanRecord",
        "RuntimeEvent",
        "AuditEvent",
        "MetricPoint",
        "StructuredLog",
        "ExternalSinkDelivery",
        "MeasurementStatus",
        "EvidenceRecord",
        "Server-hosted Product API",
        "CONFIRMED_TARGET",
        "AuditPersistenceReceipt != accepted AuditEvent",
        "ExternalSinkDelivery != source-domain success",
    ]:
        assert term in content


def test_agent_core_evidence_mapping_is_explicit() -> None:
    content = _formal()
    for term in [
        "GoalVersion",
        "PlanVersion",
        "StepRun",
        "ActionRun",
        "DispatchGroup",
        "BranchResultRef",
        "ControlDecision",
        "FailureDecision",
        "RunCommand",
        "ResultValidity",
        "FinalCandidate",
        "ArtifactVersion",
        "Publication",
        "RunOutcome",
        "BudgetSettlement",
        "RC-AG/EV-AG",
    ]:
        assert term in content


def test_rag_core_five_are_first_class_and_versioned() -> None:
    content = _formal()
    for metric in [
        "CONTEXT_PRECISION",
        "CONTEXT_RECALL",
        "FAITHFULNESS",
        "ANSWER_RELEVANCY",
        "ANSWER_CORRECTNESS",
    ]:
        assert metric in content
    for contract in [
        "MetricDefinition",
        "MetricEvaluationAttempt",
        "RAGMetricResult",
        "RAGCoreFiveInputBundle",
    ]:
        assert contract in content
    assert "TOP_K_CONTEXT_RELEVANT_RATIO" in content
    assert "Core Five 全部必须是 MEASURED" in content


def test_core_five_scoring_and_claim_diagnostics_are_explicit() -> None:
    content = _formal()
    assert "Context Precision@K" in content
    assert "retrieved_context_supported_reference_claims" in content
    assert "supported_generated_claims / total_generated_claims" in content
    assert "reverse-question" in content
    assert "Factual F1" in content
    for term in [
        "reference_claim_refs",
        "generated_claim_refs",
        "supported_claim_refs",
        "unsupported_claim_refs",
        "missing_reference_claim_refs",
        "true_positive_claim_refs",
        "false_positive_claim_refs",
        "false_negative_claim_refs",
        "metric_hash",
        "calibration_dataset_ref",
    ]:
        assert term in content


def test_agentic_graphrag_full_process_is_traceable() -> None:
    content = _formal()
    for term in [
        "Agent Core Task Analysis",
        "RetrievalNeedDecision / EvidenceRequirement",
        "KnowledgeQueryRequest + Budget + Authorized Scope",
        "Fixed KnowledgeRetrievalGraph",
        "RetrievalPlan / RetrievalRound",
        "Parallel BM25 / Vector / Graph / Structured Retrievers",
        "Normalize / Ground / Fusion / Rerank",
        "EvidenceLedger / EvidenceFrontier",
        "RetrievalQualityVerdict",
        "CorrectiveRetrievalDecision + new RetrievalRound",
        "SelectedEvidenceBundle / KnowledgeRetrievalOutcome",
        "KnowledgeControlProposal",
        "Agent Core Step Acceptance",
        "Agent Core ControlDecision",
        "Replan Barrier + new PlanVersion",
        "Interrupt or terminal control",
        "Final Synthesis / Claim and Citation Binding / Final Gate",
        "Publication / RunOutcome / BudgetSettlement / Eval",
        "AgenticGraphRAGTrace",
        "RetrievalCandidateTrace",
        "GraphTraversalRecord",
        "AgentLoopObservation",
    ]:
        assert term in content


def test_failure_buckets_support_root_cause_drill_down() -> None:
    content = _formal()
    for bucket in [
        "query_rewrite_drift",
        "route_mismatch",
        "entity_resolution_miss",
        "relation_retrieval_miss",
        "graph_path_miss",
        "community_summary_miss",
        "graph_source_grounding_miss",
        "fusion_dropped_gold_evidence",
        "rerank_demoted_gold_evidence",
        "context_noise_excess",
        "context_coverage_gap",
        "answer_unfaithful",
        "answer_irrelevant",
        "answer_incorrect",
        "retry_churn",
        "replan_churn",
        "parallel_join_waste",
    ]:
        assert bucket in content
    assert "unavailable_due_to_missing_trace_fields" in content


def test_agent_efficiency_is_quality_constrained_and_multidimensional() -> None:
    content = _formal()
    assert "AgentEfficiencySnapshot" in content
    for term in [
        "Agent Goal Accuracy",
        "Tool Call Accuracy",
        "Tool Call F1",
        "wall_time_ms",
        "active_time_ms",
        "queue_wait_ms",
        "critical_path_ms",
        "parallel_branch_time_sum_ms",
        "token_total",
        "estimated_cost",
        "settled_cost",
        "Evidence Yield",
        "Candidate Yield",
        "Wasted Work Ratio",
        "Parallel Efficiency",
        "Quality per Cost",
        "质量、安全、权限和正确性是硬约束",
    ]:
        assert term in content


def test_release_gate_preserves_existing_thresholds_and_core_five_guards() -> None:
    content = _formal()
    for threshold in [
        "Agentic Recall@5 >= standard_rag",
        "Evidence Text Available@5 >= 0.60",
        "Source Doc Citation Accuracy >= 0.85",
        "Citation Accuracy >= 0.30",
        "Answer Correctness >= standard_rag",
        "Unsupported Claim Rate 不得恶化",
    ]:
        assert threshold in content
    assert "BLOCKED、INCOMPARABLE、ERROR 都不是 FAILED" in content


def test_requirement_registries_are_complete() -> None:
    content = _formal()
    for number in range(1, 25):
        suffix = f"{number:03d}"
        assert f"ARCH-OBS-{suffix}" in content
        assert f"RC-OBS-{suffix}" in content
        assert f"OBS-{suffix}-UT/IT/FT/E2E" in content
        assert f"EV-OBS-{suffix}" in content
    for number in range(1, 21):
        suffix = f"{number:03d}"
        assert f"ARCH-OBS-RAG-{suffix}" in content
        assert f"RC-OBS-RAG-{suffix}" in content
        assert f"OBS-RAG-{suffix}-UT/IT/FT/E2E" in content
        assert f"EV-OBS-RAG-{suffix}" in content
