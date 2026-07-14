from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/10-observability-eval.md"
MIRROR = REPO_ROOT / ".agent/modules/10-observability-eval.md"
RETIRED_PATHS = [
    REPO_ROOT / "docs/modules/10-observability-eval-rag-agent-evaluation.md",
    REPO_ROOT / ".agent/modules/10-observability-eval-rag-agent-evaluation.md",
    REPO_ROOT / "tools/scripts/align_observability_wave1.py",
]

REQUIRED_PARTS = [
    "## 0. 文档边界与事实源",
    "# Part I：定位与概念架构",
    "# Part II：完整运行流程",
    "# Part III：Telemetry、Trace、Audit 与 Delivery Contract",
    "# Part IV：Eval、RAG Core Five 与质量 Contract",
    "# Part V：Agentic GraphRAG 与 Agent Efficiency Contract",
    "# Part VI：状态机、安全、失败与恢复",
    "# Part VII：存储、代码与 API 规格",
    "# Part VIII：Release Gate、测试与完成证据",
]

REQUIRED_SECTIONS = [
    "# 1. 为什么需要 Observability & Eval",
    "# 4. 概念架构",
    "# 5. Cross-module Ownership",
    "# 7. Runtime Telemetry 流程",
    "# 8. Agent Run Trace Tree",
    "# 9. Agentic GraphRAG 完整流程",
    "# 11. Eval 与 Release 流程",
    "# 12. CrossModuleEnvelopeV1 与 TelemetryEnvelopeV1",
    "# 14. Audit 三层事实",
    "# 17. Measurement Semantics",
    "# 18. Eval Dataset、Case、Run 与 Result",
    "# 19. MetricDefinition、Attempt 与 RAGMetricResult",
    "# 20. RAG Core Five 输入闭包",
    "# 21. Context Precision",
    "# 22. Context Recall",
    "# 23. Faithfulness",
    "# 24. Answer Relevancy",
    "# 25. Answer Correctness",
    "# 27. JudgePolicy、Calibration 与统计有效性",
    "# 29. AgenticGraphRAGTrace",
    "# 33. GraphRAG 与 Agent Failure Bucket",
    "# 35. AgentEfficiencySnapshot",
    "# 40. ReleaseGateEvaluation",
    "# 44. Retry、Recovery 与 Idempotency",
    "# 46. Storage Mapping",
    "# 47. Target Code Layout",
    "# 50. RAG Core Five Release Gate",
    "# 52. Fault Test Matrix",
    "# 53. Platform Requirement Enforcement Matrix",
    "# 54. RAG 与 Agent Requirement Enforcement Matrix",
    "# 55. Target 转为 Current 与 Quality Proven",
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
    "SamplingPolicy",
    "RetentionPolicy",
    "ExternalSinkDelivery",
    "MeasurementStatus",
    "EvalDataset",
    "EvalCase",
    "EvalRun",
    "EvalResult",
    "MetricDefinition",
    "MetricEvaluationAttempt",
    "RAGMetricResult",
    "RAGCoreFiveInputBundle",
    "JudgePolicy",
    "BenchmarkComparison",
    "AgenticGraphRAGTrace",
    "RetrievalCandidateTrace",
    "GraphTraversalRecord",
    "AgentLoopObservation",
    "AgentEfficiencySnapshot",
    "ReleaseGateEvaluation",
    "EvidenceRecord",
]

RAG_CORE_FIVE = [
    "CONTEXT_PRECISION",
    "CONTEXT_RECALL",
    "FAITHFULNESS",
    "ANSWER_RELEVANCY",
    "ANSWER_CORRECTNESS",
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

FAILURE_BUCKETS = [
    "doc_miss",
    "doc_hit_text_miss",
    "text_hit_citation_miss",
    "citation_hit_answer_wrong",
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

MEASUREMENT_TERMS = [
    "design available",
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
    "ModelCallAttempt",
    "RoutingDecision",
    "UsageReceipt",
    "ProviderHealth",
    "StructuredOutputFailure",
    "Outbox",
    "Inbox Dedup",
    "Backup/Restore",
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

THRESHOLDS = [
    "Agentic Recall@5 >= standard_rag",
    "Evidence Text Available@5 >= 0.60",
    "Source Doc Citation Accuracy >= 0.85",
    "Citation Accuracy >= 0.30",
    "Answer Correctness >= standard_rag",
    "Unsupported Claim Rate 不得恶化",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require(content: str, phrases: list[str], scope: str, errors: list[str]) -> None:
    for phrase in phrases:
        if phrase not in content:
            errors.append(f"missing required {scope} phrase: {phrase}")


def verify() -> list[str]:
    errors: list[str] = []
    if not FORMAL.exists():
        return [f"missing formal document: {FORMAL.relative_to(REPO_ROOT)}"]
    if not MIRROR.exists():
        return [f"missing agent mirror: {MIRROR.relative_to(REPO_ROOT)}"]

    formal = _read(FORMAL)
    mirror = _read(MIRROR)
    if formal != mirror:
        errors.append("formal document and agent mirror must be byte-identical")

    for retired in RETIRED_PATHS:
        if retired.exists():
            errors.append(f"retired Observability architecture artifact must not exist: {retired.relative_to(REPO_ROOT)}")

    _require(
        formal,
        REQUIRED_PARTS
        + REQUIRED_SECTIONS
        + REQUIRED_CONTRACTS
        + RAG_CORE_FIVE
        + RAG_PROCESS_TERMS
        + FAILURE_BUCKETS
        + EFFICIENCY_TERMS
        + MEASUREMENT_TERMS
        + CROSS_MODULE_TERMS
        + FAULTS
        + THRESHOLDS,
        "Observability/Eval architecture",
        errors,
    )

    _require(
        formal,
        [
            "唯一的正式 Target 架构主设计",
            "不再维护模块 10 的独立架构附录",
            "接收到事件不转移领域事实 Ownership",
            "Projection 丢失可从领域事件/Outbox 重建",
            "AuditEvent 一旦按合规合同接收",
            "Redaction 失败不得降级导出",
            "外部 Sink 失败不回滚本地事实",
            "BLOCKED、INCOMPARABLE、ERROR 都不是 FAILED",
            "TOP_K_CONTEXT_RELEVANT_RATIO",
            "不得满足 `CONTEXT_PRECISION` Requirement",
            "retrieved_context_supported_reference_claims",
            "supported_generated_claims / total_generated_claims",
            "reverse-question",
            "Factual F1",
            "Core Five 全部必须是 MEASURED",
            "质量、安全、权限和正确性是硬约束",
            "不保存隐藏思维链",
            "OpenTelemetry",
            "LangSmith",
            "Ragas",
            "Microsoft GraphRAG",
        ],
        "architecture invariant",
        errors,
    )

    platform_ids = set(re.findall(r"ARCH-OBS-\d{3}", formal))
    if len(platform_ids) != 24:
        errors.append(f"expected 24 unique ARCH-OBS requirements, got {len(platform_ids)}")
    rag_ids = set(re.findall(r"ARCH-OBS-RAG-\d{3}", formal))
    if len(rag_ids) != 20:
        errors.append(f"expected 20 unique ARCH-OBS-RAG requirements, got {len(rag_ids)}")

    for number in range(1, 25):
        suffix = f"{number:03d}"
        _require(
            formal,
            [
                f"ARCH-OBS-{suffix}",
                f"RC-OBS-{suffix}",
                f"OBS-{suffix}-UT/IT/FT/E2E",
                f"EV-OBS-{suffix}",
            ],
            "platform requirement mapping",
            errors,
        )

    for number in range(1, 21):
        suffix = f"{number:03d}"
        _require(
            formal,
            [
                f"ARCH-OBS-RAG-{suffix}",
                f"RC-OBS-RAG-{suffix}",
                f"OBS-RAG-{suffix}-UT/IT/FT/E2E",
                f"EV-OBS-RAG-{suffix}",
            ],
            "RAG requirement mapping",
            errors,
        )

    for phrase in ["quality is proven", "production ready now", "full CI passed"]:
        if phrase in formal:
            errors.append(f"forbidden unsupported quality claim: {phrase}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("observability/eval single-document target protocol verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
