from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_observability_eval_target_protocols.py"
FORMAL_PATH = REPO_ROOT / "docs/modules/10-observability-eval.md"
MIRROR_PATH = REPO_ROOT / ".agent/modules/10-observability-eval.md"
RAG_FORMAL_PATH = REPO_ROOT / "docs/modules/10-observability-eval-rag-agent-evaluation.md"
RAG_MIRROR_PATH = REPO_ROOT / ".agent/modules/10-observability-eval-rag-agent-evaluation.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_observability_eval_target_protocols", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _formal() -> str:
    return FORMAL_PATH.read_text(encoding="utf-8")


def _rag_formal() -> str:
    return RAG_FORMAL_PATH.read_text(encoding="utf-8")


def test_observability_eval_protocol_verifier_passes() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_formal_documents_and_agent_mirrors_are_byte_identical() -> None:
    assert FORMAL_PATH.read_bytes() == MIRROR_PATH.read_bytes()
    assert RAG_FORMAL_PATH.read_bytes() == RAG_MIRROR_PATH.read_bytes()


def test_current_quality_claims_remain_blocked() -> None:
    content = _formal() + _rag_formal()
    assert "implementation available" in content
    assert "measurement blocked" in content
    assert "quality not yet proven" in content
    assert "blocked_not_measured" in content
    assert "quality proven" in content
    assert "production ready" in content


def test_main_typed_contracts_and_agent_core_mapping_are_present() -> None:
    content = _formal()
    for contract in [
        "TraceContext",
        "TraceRecord",
        "SpanRecord",
        "RuntimeEvent",
        "AuditEvent",
        "MetricPoint",
        "StructuredLog",
        "TelemetryEnvelope",
        "EvidenceRecord",
        "EvalDataset",
        "EvalCase",
        "EvalRun",
        "EvalResult",
        "JudgePolicy",
        "FailureBucket",
        "BenchmarkComparison",
        "ReleaseGateEvaluation",
        "ExternalSinkDelivery",
        "SamplingPolicy",
        "RetentionPolicy",
        "MeasurementStatus",
    ]:
        assert contract in content
    for term in [
        "PlanVersion",
        "StepRun",
        "ActionRun",
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


def test_main_faults_thresholds_and_requirement_registry_are_preserved() -> None:
    content = _formal()
    for fault in [
        "Duplicate Event",
        "Out-of-order Event",
        "Trace Store Unavailable",
        "External Sink Failure",
        "Redaction Failure",
        "Audit Event Loss",
        "Eval Worker Crash",
        "Partial Eval Run",
        "Judge Timeout",
        "Dataset Version Mismatch",
        "Missing Trace Fields",
        "Blocked Profile",
        "Release Gate with Incomparable Runs",
        "Retention / Legal Hold Conflict",
    ]:
        assert fault in content
    for threshold in [
        "Agentic Recall@5 >= standard_rag",
        "Evidence Text Available@5 >= 0.60",
        "Source Doc Citation Accuracy >= 0.85",
        "Citation Accuracy >= 0.30",
        "Answer Correctness >= standard_rag",
        "Unsupported Claim Rate 不得恶化",
    ]:
        assert threshold in content
    for number in range(1, 25):
        suffix = f"{number:03d}"
        assert f"ARCH-OBS-{suffix}" in content
        assert f"RC-OBS-{suffix}" in content
        assert f"OBS-{suffix}-UT/IT/FT/E2E" in content
        assert f"EV-OBS-{suffix}" in content


def test_projection_audit_and_redaction_ownership_remain_separate() -> None:
    content = _formal()
    assert "接收到事件不转移领域事实 Ownership" in content
    assert "Projection 丢失可从领域事件/Outbox 重建" in content
    assert "AuditEvent 一旦按合规合同接收" in content
    assert "Redaction 失败不得降级导出" in content
    assert "外部 Sink 失败不回滚本地事实" in content


def test_rag_core_five_are_canonical_first_class_metrics() -> None:
    content = _rag_formal()
    for metric in [
        "CONTEXT_PRECISION",
        "CONTEXT_RECALL",
        "FAITHFULNESS",
        "ANSWER_RELEVANCY",
        "ANSWER_CORRECTNESS",
    ]:
        assert metric in content
    assert "TOP_K_CONTEXT_RELEVANT_RATIO" in content
    assert "不得满足 `CONTEXT_PRECISION` Requirement" in content
    assert "Core Five 全部必须是 MEASURED" in content


def test_rag_metric_contracts_expose_claim_context_and_attempt_diagnostics() -> None:
    content = _rag_formal()
    for contract in [
        "MetricDefinition",
        "MetricEvaluationAttempt",
        "RAGMetricResult",
        "RAGCoreFiveInputBundle",
    ]:
        assert contract in content
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


def test_core_five_scoring_semantics_are_explicit() -> None:
    content = _rag_formal()
    assert "Context Precision@K" in content
    assert "retrieved_context_supported_reference_claims" in content
    assert "supported_generated_claims / total_generated_claims" in content
    assert "reverse-question" in content
    assert "Factual F1" in content
    assert "Semantic Similarity" in content
    assert "Judge 超时、Embedding 缺失、Reference 缺失或 Trace 字段缺失不能记为 0" in content


def test_agentic_graphrag_full_process_is_traceable() -> None:
    content = _rag_formal()
    for term in [
        "Query Normalize / Rewrite / Decompose",
        "Route and Profile Decision",
        "Retrieval Plan + Budget + Security Scope",
        "Vector / Dense",
        "Lexical / BM25",
        "Local Graph Search",
        "Global Community Search",
        "DRIFT / Follow-up Expansion",
        "Entity / Relation / Path / Community Expansion",
        "Graph-to-Text Source Grounding",
        "Fusion / Dedup",
        "Rerank",
        "Evidence Assembly / Compression",
        "Claim Extraction / Citation Binding",
        "Reflection / Replan Barrier",
        "basic | local | global | drift",
        "standard_rag | local_graphrag | deep_graphrag | agentic_graphrag",
    ]:
        assert term in content
    for contract in [
        "AgenticGraphRAGTrace",
        "RetrievalCandidateTrace",
        "GraphTraversalRecord",
        "AgentLoopObservation",
    ]:
        assert contract in content


def test_graph_and_agent_failure_buckets_support_root_cause_drill_down() -> None:
    content = _rag_formal()
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
    assert "缺失字段返回 `unavailable_due_to_missing_trace_fields`" in content


def test_agent_efficiency_is_quality_constrained_and_multidimensional() -> None:
    content = _rag_formal()
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
        "quality-first gate",
    ]:
        assert term in content


def test_rag_requirement_registry_is_complete() -> None:
    content = _rag_formal()
    for number in range(1, 21):
        suffix = f"{number:03d}"
        assert f"ARCH-OBS-RAG-{suffix}" in content
        assert f"RC-OBS-RAG-{suffix}" in content
        assert f"OBS-RAG-{suffix}-UT/IT/FT/E2E" in content
        assert f"EV-OBS-RAG-{suffix}" in content


def test_wave1_contracts_are_confirmed_target() -> None:
    content = _rag_formal()
    assert "CONFIRMED_TARGET" in content
    assert "ALIGNED_PENDING_FIELDS" not in content


def test_server_authoritative_observability_contract_alignment() -> None:
    content = _formal()
    for term in [
        "Server-hosted Product API",
        "CrossModuleEnvelopeV1",
        "TelemetryEnvelopeV1",
        "SecurityAuditRequirementV1",
        "AuditDurabilityRequirement",
        "AuditPersistenceReceiptV1",
        "effective_security_epoch_ref",
        "payload_schema_hash",
        "OBS_AUDIT_ACCEPTANCE_FAILED",
        "AuditPersistenceReceipt != accepted AuditEvent",
        "ExternalSinkDelivery != source-domain success",
    ]:
        assert term in content
