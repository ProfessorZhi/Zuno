from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/10-observability-eval.md"
MIRROR = REPO_ROOT / ".agent/modules/10-observability-eval.md"
RAG_FORMAL = REPO_ROOT / "docs/modules/10-observability-eval-rag-agent-evaluation.md"
RAG_MIRROR = REPO_ROOT / ".agent/modules/10-observability-eval-rag-agent-evaluation.md"

REQUIRED_SECTIONS = [
    "## 1. 问题、目标与非目标",
    "## 2. Current、Target、Measurement Blocked",
    "## 3. Ownership 与边界",
    "## 4. 总体运行流程",
    "## 5. Typed Contract",
    "## 8. 状态机",
    "## 10. Eval Dataset / Case / Run / Result",
    "## 11. Judge Policy、Failure Bucket 与 Benchmark Comparison",
    "## 12. Release Gate 与质量门",
    "## 13. Evidence Registry",
    "## 14. Storage Mapping",
    "## 16. Failure、Retry、Recovery、Idempotency",
    "## 17. Fault Test Matrix",
    "## 18. Requirement Enforcement Matrix",
    "## 21. Target 转为 Current 与 quality proven",
]

REQUIRED_CONTRACTS = [
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
]

REQUIRED_STATE_MACHINES = [
    "Trace Lifecycle",
    "ExternalSinkDelivery",
    "EvalRun / EvalCaseExecution",
    "ReleaseGateEvaluation",
    "EvidenceRecord",
    "MeasurementStatus",
]

AGENT_CORE_TERMS = [
    "run_id",
    "trace_id",
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
]

FAULTS = [
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
]

THRESHOLDS = [
    "Agentic Recall@5 >= standard_rag",
    "Evidence Text Available@5 >= 0.60",
    "Source Doc Citation Accuracy >= 0.85",
    "Citation Accuracy >= 0.30",
    "Answer Correctness >= standard_rag",
    "Unsupported Claim Rate 不得恶化",
]

MEASUREMENT_TERMS = [
    "implementation available",
    "measurement blocked",
    "quality not yet proven",
    "blocked_not_measured",
    "unavailable_due_to_missing_trace_fields",
    "PREPARED",
    "RUNTIME_OBSERVED",
    "MEASURED",
    "BLOCKED",
    "UNAVAILABLE",
    "QUALITY_PROVEN",
]

CROSS_MODULE_TERMS = [
    "Server-hosted Product API",
    "CONFIRMED_TARGET",
    "effective_security_epoch_ref",
    "effective_security_epoch_hash",
    "payload_schema_hash",
    "OBS_ENVELOPE_SCHEMA_UNSUPPORTED",
    "OBS_INGEST_GAP",
    "OBS_AUDIT_ACCEPTANCE_FAILED",
    "OBS_EXTERNAL_SINK_DELIVERY_FAILED",
    "AuditPersistenceReceipt != accepted AuditEvent",
    "ExternalSinkDelivery != source-domain success",
    "SecurityAuditRequirement",
    "RedactionDecision",
    "DataClassification",
    "ExternalSinkPolicy",
    "AuditRetentionPolicy",
    "BreakGlassDecision",
    "Trace Store",
    "Append-only Ingest",
    "Outbox-Inbox",
    "Eval Job Queue",
    "Backup/Restore",
    "ModelCallAttempt",
    "RoutingDecision",
    "UsageReceipt",
    "ProviderHealth",
    "StructuredOutputFailure",
]

RAG_REQUIRED_SECTIONS = [
    "## 1. 问题与设计目标",
    "## 2. 指标分层与 Ownership",
    "## 3. Metric Contract",
    "## 4. RAG Core Five 规范",
    "## 6. Agentic GraphRAG 全过程 Trace",
    "## 7. Agentic 循环可观测性",
    "## 8. GraphRAG 与 Agentic Failure Bucket",
    "## 9. Agent 效率 Scorecard",
    "## 11. Release Gate",
    "## 14. Fault Test Matrix",
    "## 15. Requirement Enforcement Matrix",
    "## 17. Current、Target、Future",
]

RAG_CORE_FIVE = [
    "CONTEXT_PRECISION",
    "CONTEXT_RECALL",
    "FAITHFULNESS",
    "ANSWER_RELEVANCY",
    "ANSWER_CORRECTNESS",
]

RAG_CONTRACTS = [
    "MetricDefinition",
    "MetricEvaluationAttempt",
    "RAGMetricResult",
    "RAGCoreFiveInputBundle",
    "AgenticGraphRAGTrace",
    "RetrievalCandidateTrace",
    "GraphTraversalRecord",
    "AgentLoopObservation",
    "AgentEfficiencySnapshot",
]

RAG_PROCESS_TERMS = [
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
]

RAG_FAILURE_BUCKETS = [
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
]

EFFICIENCY_TERMS = [
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
    "quality-first gate",
]

RAG_FAULTS = [
    "Context Rank Swap",
    "Missing Reference Claims",
    "Partial Claim Judge Failure",
    "Answer Relevancy Judge Timeout",
    "Embedding Policy Drift",
    "Answer Correctness Reference Mismatch",
    "Entity Resolution Miss",
    "Graph Snapshot Missing",
    "Graph-to-Text Mapping Loss",
    "Fusion Drops Gold",
    "Reranker Demotes Gold",
    "DRIFT Follow-up Explosion",
    "Replan Churn",
    "Parallel Partial Failure",
    "Hidden Model Retry",
    "Settled Usage Delayed",
    "Missing Agent Trace",
    "Profile Partial Run",
    "Critical Slice Regression",
    "Quality-Cost Tradeoff",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_phrases(content: str, phrases: list[str], scope: str, errors: list[str]) -> None:
    for phrase in phrases:
        if phrase not in content:
            errors.append(f"missing required {scope} phrase: {phrase}")


def _verify_mirror(formal_path: Path, mirror_path: Path, label: str, errors: list[str]) -> tuple[str, str]:
    if not formal_path.exists():
        errors.append(f"missing {label} formal document: {formal_path.relative_to(REPO_ROOT)}")
        return "", ""
    if not mirror_path.exists():
        errors.append(f"missing {label} agent mirror: {mirror_path.relative_to(REPO_ROOT)}")
        return _read(formal_path), ""
    formal = _read(formal_path)
    mirror = _read(mirror_path)
    if formal != mirror:
        errors.append(f"{label} formal document and agent mirror must be byte-identical")
    return formal, mirror


def verify() -> list[str]:
    errors: list[str] = []
    formal, _ = _verify_mirror(FORMAL, MIRROR, "main", errors)
    rag_formal, _ = _verify_mirror(RAG_FORMAL, RAG_MIRROR, "RAG/agent appendix", errors)
    if not formal or not rag_formal:
        return errors

    _require_phrases(
        formal,
        REQUIRED_SECTIONS
        + REQUIRED_CONTRACTS
        + REQUIRED_STATE_MACHINES
        + AGENT_CORE_TERMS
        + FAULTS
        + THRESHOLDS
        + MEASUREMENT_TERMS
        + CROSS_MODULE_TERMS,
        "observability/eval protocol",
        errors,
    )

    for number in range(1, 25):
        suffix = f"{number:03d}"
        _require_phrases(
            formal,
            [
                f"ARCH-OBS-{suffix}",
                f"RC-OBS-{suffix}",
                f"OBS-{suffix}-UT/IT/FT/E2E",
                f"EV-OBS-{suffix}",
            ],
            "main requirement mapping",
            errors,
        )

    requirement_ids = set(re.findall(r"ARCH-OBS-\d{3}", formal))
    if len(requirement_ids) != 24:
        errors.append(f"expected 24 unique ARCH-OBS requirements, got {len(requirement_ids)}")

    _require_phrases(
        formal,
        [
            "接收到事件不转移领域事实 Ownership",
            "Projection 丢失可从领域事件/Outbox 重建",
            "AuditEvent 一旦按合规合同接收",
            "Redaction 失败不得降级导出",
            "外部 Sink 失败不回滚本地事实",
            "BLOCKED、INCOMPARABLE、ERROR 都不是 FAILED",
            "Measurement Semantics",
            "quality proven",
            "production ready",
            "OpenTelemetry",
            "LangSmith",
        ],
        "ownership or quality invariant",
        errors,
    )

    _require_phrases(
        rag_formal,
        RAG_REQUIRED_SECTIONS
        + RAG_CORE_FIVE
        + RAG_CONTRACTS
        + RAG_PROCESS_TERMS
        + RAG_FAILURE_BUCKETS
        + EFFICIENCY_TERMS
        + RAG_FAULTS,
        "RAG/agent evaluation protocol",
        errors,
    )

    _require_phrases(
        rag_formal,
        [
            "TOP_K_CONTEXT_RELEVANT_RATIO",
            "不得满足 `CONTEXT_PRECISION` Requirement",
            "Context Precision@K",
            "retrieved_context_supported_reference_claims",
            "supported_generated_claims / total_generated_claims",
            "reverse-question",
            "Factual F1",
            "Core Five 全部必须是 MEASURED",
            "缺失字段返回 `unavailable_due_to_missing_trace_fields`",
            "质量、安全、权限和正确性是硬约束",
            "CONFIRMED_TARGET",
            "不保存隐藏思维链",
        ],
        "RAG metric or governance invariant",
        errors,
    )

    for number in range(1, 21):
        suffix = f"{number:03d}"
        _require_phrases(
            rag_formal,
            [
                f"ARCH-OBS-RAG-{suffix}",
                f"RC-OBS-RAG-{suffix}",
                f"OBS-RAG-{suffix}-UT/IT/FT/E2E",
                f"EV-OBS-RAG-{suffix}",
            ],
            "RAG requirement mapping",
            errors,
        )

    rag_requirement_ids = set(re.findall(r"ARCH-OBS-RAG-\d{3}", rag_formal))
    if len(rag_requirement_ids) != 20:
        errors.append(f"expected 20 unique ARCH-OBS-RAG requirements, got {len(rag_requirement_ids)}")

    forbidden_claims = [
        "quality is proven",
        "production ready now",
        "full CI passed",
        "ALIGNED_PENDING_FIELDS",
        "支持本地事实存储，并通过",
    ]
    for phrase in forbidden_claims:
        if phrase in formal or phrase in rag_formal:
            errors.append(f"forbidden unsupported quality claim: {phrase}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("observability/eval target protocol verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
