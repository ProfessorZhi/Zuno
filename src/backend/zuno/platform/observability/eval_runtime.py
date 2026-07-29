from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from sqlalchemy import Engine, text

from zuno.platform.contracts import canonical_json, canonical_sha256


CORE_FIVE_METRICS = (
    "CONTEXT_PRECISION",
    "CONTEXT_RECALL",
    "FAITHFULNESS",
    "ANSWER_RELEVANCY",
    "ANSWER_CORRECTNESS",
)


class EvalRuntimeError(RuntimeError):
    pass


class EvalMeasurementStatus(StrEnum):
    MEASURED = "MEASURED"
    BLOCKED = "BLOCKED"
    UNAVAILABLE = "UNAVAILABLE"
    INVALID = "INVALID"


class EvalRunStatus(StrEnum):
    PREPARED = "PREPARED"
    RUNNING = "RUNNING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class ReleaseGateStatus(StrEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    INCOMPARABLE = "INCOMPARABLE"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class EvalCase:
    case_id: str
    question: str
    reference_claim_refs: tuple[str, ...]
    gold_evidence_refs: tuple[str, ...]
    slices: tuple[str, ...]
    security_scope_ref: str
    expected_answer_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "question": self.question,
            "reference_claim_refs": list(self.reference_claim_refs),
            "gold_evidence_refs": list(self.gold_evidence_refs),
            "slices": list(self.slices),
            "security_scope_ref": self.security_scope_ref,
            "expected_answer_refs": list(self.expected_answer_refs),
            "metadata": self.metadata,
        }

    @property
    def case_hash(self) -> str:
        return canonical_sha256(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class EvalDatasetVersion:
    dataset_id: str
    version: str
    cases: tuple[EvalCase, ...]
    supersedes_dataset_hash: str | None = None

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for case in self.cases:
            if case.case_id in seen:
                raise EvalRuntimeError(f"duplicate eval case_id: {case.case_id}")
            seen.add(case.case_id)
            if not case.reference_claim_refs:
                raise EvalRuntimeError(f"eval case missing reference claims: {case.case_id}")
            if not case.gold_evidence_refs:
                raise EvalRuntimeError(f"eval case missing gold evidence: {case.case_id}")
            if not case.slices:
                raise EvalRuntimeError(f"eval case missing slices: {case.case_id}")
            if not case.security_scope_ref:
                raise EvalRuntimeError(f"eval case missing security scope: {case.case_id}")

    @property
    def case_hashes(self) -> tuple[str, ...]:
        return tuple(case.case_hash for case in self.cases)

    @property
    def dataset_hash(self) -> str:
        return canonical_sha256(
            {
                "dataset_id": self.dataset_id,
                "version": self.version,
                "case_hashes": list(self.case_hashes),
                "supersedes_dataset_hash": self.supersedes_dataset_hash,
            }
        )

    def require_scope(self, authorized_scope_refs: set[str]) -> None:
        unauthorized = sorted({case.security_scope_ref for case in self.cases} - authorized_scope_refs)
        if unauthorized:
            raise EvalRuntimeError(f"unauthorized eval dataset scopes: {', '.join(unauthorized)}")


@dataclass(frozen=True, slots=True)
class EvalRunConfig:
    dataset_hash: str
    corpus_snapshot_hash: str
    index_snapshot_hash: str
    model_profile_hash: str
    judge_policy_hash: str
    embedding_profile_hash: str
    metric_config_hash: str
    runtime_profile_hash: str
    security_scope_hash: str

    def comparable_payload(self) -> dict[str, str]:
        return {
            "dataset_hash": self.dataset_hash,
            "corpus_snapshot_hash": self.corpus_snapshot_hash,
            "index_snapshot_hash": self.index_snapshot_hash,
            "model_profile_hash": self.model_profile_hash,
            "judge_policy_hash": self.judge_policy_hash,
            "embedding_profile_hash": self.embedding_profile_hash,
            "metric_config_hash": self.metric_config_hash,
            "runtime_profile_hash": self.runtime_profile_hash,
            "security_scope_hash": self.security_scope_hash,
        }

    @property
    def config_hash(self) -> str:
        return canonical_sha256(self.comparable_payload())


@dataclass(frozen=True, slots=True)
class RAGCoreFiveInputBundle:
    case_id: str
    retrieved_context_refs: tuple[str, ...]
    reference_claim_refs: tuple[str, ...]
    retrieved_context_supported_reference_claim_refs: tuple[str, ...]
    generated_claim_refs: tuple[str, ...]
    supported_generated_claim_refs: tuple[str, ...]
    true_positive_claim_refs: tuple[str, ...]
    false_positive_claim_refs: tuple[str, ...]
    false_negative_claim_refs: tuple[str, ...]
    answer_relevant: bool | None
    judge_output_valid: bool = True


@dataclass(frozen=True, slots=True)
class MetricResult:
    metric_name: str
    status: EvalMeasurementStatus
    value: float | None
    reason: str
    metric_hash: str


class RAGCoreFiveEvaluator:
    version = "phase20-core-five-v1"

    def evaluate(self, bundle: RAGCoreFiveInputBundle) -> tuple[MetricResult, ...]:
        if not bundle.judge_output_valid:
            return tuple(self._result(metric, EvalMeasurementStatus.INVALID, None, "judge_output_invalid") for metric in CORE_FIVE_METRICS)
        if not bundle.reference_claim_refs:
            return tuple(self._result(metric, EvalMeasurementStatus.BLOCKED, None, "missing_reference_claims") for metric in CORE_FIVE_METRICS)
        if not bundle.retrieved_context_refs:
            return tuple(self._result(metric, EvalMeasurementStatus.UNAVAILABLE, None, "missing_retrieved_context") for metric in CORE_FIVE_METRICS)
        generated_count = len(bundle.generated_claim_refs)
        if generated_count == 0:
            return tuple(self._result(metric, EvalMeasurementStatus.BLOCKED, None, "missing_generated_claims") for metric in CORE_FIVE_METRICS)

        precision = len(set(bundle.retrieved_context_supported_reference_claim_refs)) / max(1, len(bundle.retrieved_context_refs))
        recall = len(set(bundle.retrieved_context_supported_reference_claim_refs)) / len(set(bundle.reference_claim_refs))
        faithfulness = len(set(bundle.supported_generated_claim_refs)) / generated_count
        relevancy = 1.0 if bundle.answer_relevant is True else 0.0 if bundle.answer_relevant is False else None
        correctness = len(set(bundle.true_positive_claim_refs)) / max(
            1,
            len(set(bundle.true_positive_claim_refs)) + len(set(bundle.false_positive_claim_refs)) + len(set(bundle.false_negative_claim_refs)),
        )
        values = {
            "CONTEXT_PRECISION": precision,
            "CONTEXT_RECALL": recall,
            "FAITHFULNESS": faithfulness,
            "ANSWER_RELEVANCY": relevancy,
            "ANSWER_CORRECTNESS": correctness,
        }
        return tuple(
            self._result(
                metric,
                EvalMeasurementStatus.MEASURED if values[metric] is not None else EvalMeasurementStatus.BLOCKED,
                values[metric],
                "measured" if values[metric] is not None else "answer_relevancy_unjudged",
            )
            for metric in CORE_FIVE_METRICS
        )

    def _result(self, metric_name: str, status: EvalMeasurementStatus, value: float | None, reason: str) -> MetricResult:
        return MetricResult(
            metric_name=metric_name,
            status=status,
            value=value,
            reason=reason,
            metric_hash=canonical_sha256(
                {
                    "metric_name": metric_name,
                    "evaluator_version": self.version,
                    "status": status.value,
                    "value": value,
                    "reason": reason,
                }
            ),
        )


@dataclass(frozen=True, slots=True)
class GraphRAGDiagnosticTrace:
    case_id: str
    route_profile: str
    retrieval_round: int
    entity_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    path_refs: tuple[str, ...]
    community_refs: tuple[str, ...]
    fusion_kept_evidence_refs: tuple[str, ...]
    rerank_top_evidence_refs: tuple[str, ...]
    source_grounding_refs: tuple[str, ...]
    gold_evidence_refs: tuple[str, ...]

    def failure_buckets(self) -> tuple[str, ...]:
        buckets: list[str] = []
        gold = set(self.gold_evidence_refs)
        if self.route_profile not in {"standard_rag", "local_graphrag", "deep_graphrag", "agentic_graphrag"}:
            buckets.append("route_mismatch")
        if not self.entity_refs:
            buckets.append("entity_resolution_miss")
        if not self.relation_refs:
            buckets.append("relation_retrieval_miss")
        if not self.path_refs:
            buckets.append("graph_path_miss")
        if not self.community_refs and self.route_profile in {"deep_graphrag", "agentic_graphrag"}:
            buckets.append("community_summary_miss")
        if gold and gold.isdisjoint(self.fusion_kept_evidence_refs):
            buckets.append("fusion_dropped_gold_evidence")
        if gold and gold.isdisjoint(self.rerank_top_evidence_refs):
            buckets.append("rerank_demoted_gold_evidence")
        if not self.source_grounding_refs:
            buckets.append("graph_source_grounding_miss")
        return tuple(buckets)


@dataclass(frozen=True, slots=True)
class AgentEfficiencyVector:
    plan_steps: int
    retry_count: int
    replan_count: int
    reflection_count: int
    tool_call_count: int
    model_call_count: int
    retrieval_call_count: int
    wall_time_ms: int
    active_time_ms: int
    queue_wait_ms: int
    critical_path_ms: int
    parallel_branch_time_sum_ms: int
    token_total: int
    estimated_cost: float
    settled_cost: float | None
    evidence_yield: float
    human_intervention_count: int = 0

    @property
    def settled_cost_available(self) -> bool:
        return self.settled_cost is not None

    @property
    def wasted_work_ratio(self) -> float:
        total = max(1, self.plan_steps + self.retry_count + self.replan_count + self.reflection_count)
        return (self.retry_count + self.replan_count) / total

    @property
    def parallel_efficiency(self) -> float:
        if self.parallel_branch_time_sum_ms <= 0:
            return 1.0
        return min(1.0, self.critical_path_ms / self.parallel_branch_time_sum_ms)


@dataclass(frozen=True, slots=True)
class CaseExecutionResult:
    case_id: str
    status: EvalRunStatus
    attempt: int
    lease_ref: str
    checkpoint_ref: str
    metric_results: tuple[MetricResult, ...]
    failure_buckets: tuple[str, ...]
    recovered: bool = False

    @property
    def measured(self) -> bool:
        return self.status == EvalRunStatus.COMPLETED and all(result.status == EvalMeasurementStatus.MEASURED for result in self.metric_results)


@dataclass(frozen=True, slots=True)
class EvalRunResultSet:
    run_id: str
    profile_id: str
    config: EvalRunConfig
    case_results: tuple[CaseExecutionResult, ...]
    efficiency: AgentEfficiencyVector | None = None

    @property
    def complete(self) -> bool:
        return bool(self.case_results) and all(result.measured for result in self.case_results)

    @property
    def result_set_hash(self) -> str:
        return canonical_sha256(
            {
                "run_id": self.run_id,
                "profile_id": self.profile_id,
                "config_hash": self.config.config_hash,
                "case_results": [
                    {
                        "case_id": result.case_id,
                        "status": result.status.value,
                        "attempt": result.attempt,
                        "metric_hashes": [metric.metric_hash for metric in result.metric_results],
                        "failure_buckets": list(result.failure_buckets),
                    }
                    for result in self.case_results
                ],
                "efficiency": None
                if self.efficiency is None
                else {
                    "settled_cost": self.efficiency.settled_cost,
                    "evidence_yield": self.efficiency.evidence_yield,
                    "parallel_efficiency": self.efficiency.parallel_efficiency,
                    "wasted_work_ratio": self.efficiency.wasted_work_ratio,
                },
            }
        )


@dataclass(frozen=True, slots=True)
class BenchmarkComparison:
    baseline_run_id: str
    candidate_run_id: str
    comparable: bool
    status: ReleaseGateStatus
    reason: str
    comparison_hash: str


def compare_benchmark_runs(baseline: EvalRunResultSet, candidate: EvalRunResultSet) -> BenchmarkComparison:
    if baseline.config.config_hash != candidate.config.config_hash:
        return _comparison(baseline, candidate, False, ReleaseGateStatus.INCOMPARABLE, "config_mismatch")
    if not baseline.complete or not candidate.complete:
        return _comparison(baseline, candidate, False, ReleaseGateStatus.BLOCKED, "partial_profile")
    return _comparison(baseline, candidate, True, ReleaseGateStatus.PASSED, "comparable")


def _comparison(
    baseline: EvalRunResultSet,
    candidate: EvalRunResultSet,
    comparable: bool,
    status: ReleaseGateStatus,
    reason: str,
) -> BenchmarkComparison:
    return BenchmarkComparison(
        baseline_run_id=baseline.run_id,
        candidate_run_id=candidate.run_id,
        comparable=comparable,
        status=status,
        reason=reason,
        comparison_hash=canonical_sha256(
            {
                "baseline_result_set_hash": baseline.result_set_hash,
                "candidate_result_set_hash": candidate.result_set_hash,
                "comparable": comparable,
                "status": status.value,
                "reason": reason,
            }
        ),
    )


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    artifact_ref: str
    artifact_hash: str
    result_set_hash: str
    gate_hash: str
    expires_at: str | None = None

    @property
    def evidence_hash(self) -> str:
        return canonical_sha256(
            {
                "evidence_id": self.evidence_id,
                "artifact_ref": self.artifact_ref,
                "artifact_hash": self.artifact_hash,
                "result_set_hash": self.result_set_hash,
                "gate_hash": self.gate_hash,
                "expires_at": self.expires_at,
            }
        )


@dataclass(frozen=True, slots=True)
class ReleaseGateEvaluation:
    gate_id: str
    status: ReleaseGateStatus
    reason: str
    result_set_hash: str
    comparison_hash: str | None
    evidence_hash: str
    gate_hash: str


def evaluate_release_gate(
    *,
    gate_id: str,
    result_set: EvalRunResultSet,
    thresholds: dict[str, float],
    critical_slices: set[str],
    comparison: BenchmarkComparison | None,
    evidence_artifact_ref: str,
    evidence_artifact_hash: str,
) -> ReleaseGateEvaluation:
    gate_inputs = {
        "gate_id": gate_id,
        "result_set_hash": result_set.result_set_hash,
        "thresholds": thresholds,
        "critical_slices": sorted(critical_slices),
        "comparison_hash": comparison.comparison_hash if comparison else None,
        "evidence_artifact_ref": evidence_artifact_ref,
        "evidence_artifact_hash": evidence_artifact_hash,
    }
    gate_hash = canonical_sha256(gate_inputs)
    evidence = EvidenceRecord(
        evidence_id=f"evidence:{gate_id}",
        artifact_ref=evidence_artifact_ref,
        artifact_hash=evidence_artifact_hash,
        result_set_hash=result_set.result_set_hash,
        gate_hash=gate_hash,
    )
    status = ReleaseGateStatus.PASSED
    reason = "passed"
    if not result_set.complete:
        status, reason = ReleaseGateStatus.BLOCKED, "result_set_not_fully_measured"
    elif comparison is not None and comparison.status == ReleaseGateStatus.INCOMPARABLE:
        status, reason = ReleaseGateStatus.INCOMPARABLE, comparison.reason
    elif comparison is not None and comparison.status == ReleaseGateStatus.BLOCKED:
        status, reason = ReleaseGateStatus.BLOCKED, comparison.reason
    elif result_set.efficiency is not None and not result_set.efficiency.settled_cost_available:
        status, reason = ReleaseGateStatus.BLOCKED, "settled_cost_missing"
    else:
        slice_values: dict[str, list[float]] = {}
        metric_values: dict[str, list[float]] = {}
        for case_result in result_set.case_results:
            for bucket in case_result.failure_buckets:
                if bucket in critical_slices:
                    status, reason = ReleaseGateStatus.FAILED, f"critical_slice_regression:{bucket}"
                    break
            for metric in case_result.metric_results:
                if metric.value is not None:
                    metric_values.setdefault(metric.metric_name, []).append(metric.value)
                    for bucket in case_result.failure_buckets:
                        slice_values.setdefault(bucket, []).append(metric.value)
            if status == ReleaseGateStatus.FAILED:
                break
        if status != ReleaseGateStatus.FAILED:
            for metric_name, threshold in thresholds.items():
                values = metric_values.get(metric_name) or []
                if not values:
                    status, reason = ReleaseGateStatus.BLOCKED, f"metric_missing:{metric_name}"
                    break
                if sum(values) / len(values) < threshold:
                    status, reason = ReleaseGateStatus.FAILED, f"metric_below_threshold:{metric_name}"
                    break
    return ReleaseGateEvaluation(
        gate_id=gate_id,
        status=status,
        reason=reason,
        result_set_hash=result_set.result_set_hash,
        comparison_hash=comparison.comparison_hash if comparison else None,
        evidence_hash=evidence.evidence_hash,
        gate_hash=gate_hash,
    )


class PostgresEvalRuntimeRepository:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def record_dataset(self, dataset: EvalDatasetVersion) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO observability_eval_datasets(
                        dataset_hash, dataset_id, version, case_hashes, supersedes_dataset_hash
                    ) VALUES (
                        :dataset_hash, :dataset_id, :version, CAST(:case_hashes AS jsonb), :supersedes_dataset_hash
                    )
                    ON CONFLICT (dataset_hash) DO NOTHING
                    """
                ),
                {
                    "dataset_hash": dataset.dataset_hash,
                    "dataset_id": dataset.dataset_id,
                    "version": dataset.version,
                    "case_hashes": canonical_json(list(dataset.case_hashes)),
                    "supersedes_dataset_hash": dataset.supersedes_dataset_hash,
                },
            )
            for case in dataset.cases:
                conn.execute(
                    text(
                        """
                        INSERT INTO observability_eval_cases(
                            case_hash, dataset_hash, case_id, question, reference_claim_refs,
                            gold_evidence_refs, slices, security_scope_ref, case_payload
                        ) VALUES (
                            :case_hash, :dataset_hash, :case_id, :question, CAST(:reference_claim_refs AS jsonb),
                            CAST(:gold_evidence_refs AS jsonb), CAST(:slices AS jsonb), :security_scope_ref,
                            CAST(:case_payload AS jsonb)
                        )
                        ON CONFLICT (case_hash) DO NOTHING
                        """
                    ),
                    {
                        "case_hash": case.case_hash,
                        "dataset_hash": dataset.dataset_hash,
                        "case_id": case.case_id,
                        "question": case.question,
                        "reference_claim_refs": canonical_json(list(case.reference_claim_refs)),
                        "gold_evidence_refs": canonical_json(list(case.gold_evidence_refs)),
                        "slices": canonical_json(list(case.slices)),
                        "security_scope_ref": case.security_scope_ref,
                        "case_payload": canonical_json(case.canonical_payload()),
                    },
                )

    def start_run(self, *, run_id: str, profile_id: str, config: EvalRunConfig) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO observability_eval_runs(
                        run_id, profile_id, dataset_hash, config_hash, corpus_snapshot_hash,
                        index_snapshot_hash, model_profile_hash, judge_policy_hash, embedding_profile_hash,
                        metric_config_hash, runtime_profile_hash, security_scope_hash, status, result_set_hash
                    ) VALUES (
                        :run_id, :profile_id, :dataset_hash, :config_hash, :corpus_snapshot_hash,
                        :index_snapshot_hash, :model_profile_hash, :judge_policy_hash, :embedding_profile_hash,
                        :metric_config_hash, :runtime_profile_hash, :security_scope_hash, 'RUNNING', NULL
                    )
                    ON CONFLICT (run_id) DO UPDATE
                    SET status = CASE
                            WHEN observability_eval_runs.status = 'COMPLETED' THEN observability_eval_runs.status
                            ELSE 'RUNNING'
                        END
                    """
                ),
                {"run_id": run_id, "profile_id": profile_id, **config.comparable_payload(), "config_hash": config.config_hash},
            )

    def record_case_execution(self, *, run_id: str, case_hash: str, result: CaseExecutionResult) -> None:
        execution_id = f"case-execution:{run_id}:{result.case_id}:{result.attempt}"
        execution_hash = canonical_sha256(
            {
                "run_id": run_id,
                "case_hash": case_hash,
                "case_id": result.case_id,
                "attempt": result.attempt,
                "status": result.status.value,
                "metric_hashes": [metric.metric_hash for metric in result.metric_results],
                "failure_buckets": list(result.failure_buckets),
                "recovered": result.recovered,
            }
        )
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO observability_eval_case_executions(
                        case_execution_id, run_id, case_hash, case_id, attempt, lease_ref,
                        checkpoint_ref, status, recovered, failure_buckets, execution_hash
                    ) VALUES (
                        :case_execution_id, :run_id, :case_hash, :case_id, :attempt, :lease_ref,
                        :checkpoint_ref, :status, :recovered, CAST(:failure_buckets AS jsonb), :execution_hash
                    )
                    ON CONFLICT (run_id, case_id, attempt) DO UPDATE
                    SET status = EXCLUDED.status,
                        checkpoint_ref = EXCLUDED.checkpoint_ref,
                        recovered = EXCLUDED.recovered,
                        failure_buckets = EXCLUDED.failure_buckets,
                        execution_hash = EXCLUDED.execution_hash
                    """
                ),
                {
                    "case_execution_id": execution_id,
                    "run_id": run_id,
                    "case_hash": case_hash,
                    "case_id": result.case_id,
                    "attempt": result.attempt,
                    "lease_ref": result.lease_ref,
                    "checkpoint_ref": result.checkpoint_ref,
                    "status": result.status.value,
                    "recovered": result.recovered,
                    "failure_buckets": canonical_json(list(result.failure_buckets)),
                    "execution_hash": execution_hash,
                },
            )
            for metric in result.metric_results:
                conn.execute(
                    text(
                        """
                        INSERT INTO observability_eval_metric_results(
                            metric_result_id, case_execution_id, metric_name, measurement_status,
                            metric_value, reason, metric_hash
                        ) VALUES (
                            :metric_result_id, :case_execution_id, :metric_name, :measurement_status,
                            :metric_value, :reason, :metric_hash
                        )
                        ON CONFLICT (case_execution_id, metric_name) DO UPDATE
                        SET measurement_status = EXCLUDED.measurement_status,
                            metric_value = EXCLUDED.metric_value,
                            reason = EXCLUDED.reason,
                            metric_hash = EXCLUDED.metric_hash
                        """
                    ),
                    {
                        "metric_result_id": f"metric:{execution_id}:{metric.metric_name}",
                        "case_execution_id": execution_id,
                        "metric_name": metric.metric_name,
                        "measurement_status": metric.status.value,
                        "metric_value": metric.value,
                        "reason": metric.reason,
                        "metric_hash": metric.metric_hash,
                    },
                )
            for bucket in result.failure_buckets:
                conn.execute(
                    text(
                        """
                        INSERT INTO observability_failure_buckets(bucket_id, run_id, case_id, bucket, bucket_hash)
                        VALUES (:bucket_id, :run_id, :case_id, :bucket, :bucket_hash)
                        ON CONFLICT (run_id, case_id, bucket) DO NOTHING
                        """
                    ),
                    {
                        "bucket_id": f"bucket:{run_id}:{result.case_id}:{bucket}",
                        "run_id": run_id,
                        "case_id": result.case_id,
                        "bucket": bucket,
                        "bucket_hash": canonical_sha256({"run_id": run_id, "case_id": result.case_id, "bucket": bucket}),
                    },
                )

    def record_graph_diagnostic(self, *, run_id: str, diagnostic: GraphRAGDiagnosticTrace) -> None:
        payload = {
            "case_id": diagnostic.case_id,
            "route_profile": diagnostic.route_profile,
            "retrieval_round": diagnostic.retrieval_round,
            "entity_refs": list(diagnostic.entity_refs),
            "relation_refs": list(diagnostic.relation_refs),
            "path_refs": list(diagnostic.path_refs),
            "community_refs": list(diagnostic.community_refs),
            "fusion_kept_evidence_refs": list(diagnostic.fusion_kept_evidence_refs),
            "rerank_top_evidence_refs": list(diagnostic.rerank_top_evidence_refs),
            "source_grounding_refs": list(diagnostic.source_grounding_refs),
            "gold_evidence_refs": list(diagnostic.gold_evidence_refs),
        }
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO observability_graphrag_diagnostics(
                        diagnostic_id, run_id, case_id, route_profile, retrieval_round,
                        diagnostic_payload, failure_buckets, diagnostic_hash
                    ) VALUES (
                        :diagnostic_id, :run_id, :case_id, :route_profile, :retrieval_round,
                        CAST(:diagnostic_payload AS jsonb), CAST(:failure_buckets AS jsonb), :diagnostic_hash
                    )
                    ON CONFLICT (diagnostic_id) DO NOTHING
                    """
                ),
                {
                    "diagnostic_id": f"diagnostic:{run_id}:{diagnostic.case_id}:{diagnostic.retrieval_round}",
                    "run_id": run_id,
                    "case_id": diagnostic.case_id,
                    "route_profile": diagnostic.route_profile,
                    "retrieval_round": diagnostic.retrieval_round,
                    "diagnostic_payload": canonical_json(payload),
                    "failure_buckets": canonical_json(list(diagnostic.failure_buckets())),
                    "diagnostic_hash": canonical_sha256(payload),
                },
            )

    def record_efficiency(self, *, run_id: str, efficiency: AgentEfficiencyVector) -> None:
        payload = {
            "plan_steps": efficiency.plan_steps,
            "retry_count": efficiency.retry_count,
            "replan_count": efficiency.replan_count,
            "reflection_count": efficiency.reflection_count,
            "tool_call_count": efficiency.tool_call_count,
            "model_call_count": efficiency.model_call_count,
            "retrieval_call_count": efficiency.retrieval_call_count,
            "wall_time_ms": efficiency.wall_time_ms,
            "active_time_ms": efficiency.active_time_ms,
            "queue_wait_ms": efficiency.queue_wait_ms,
            "critical_path_ms": efficiency.critical_path_ms,
            "parallel_branch_time_sum_ms": efficiency.parallel_branch_time_sum_ms,
            "token_total": efficiency.token_total,
            "estimated_cost": efficiency.estimated_cost,
            "settled_cost": efficiency.settled_cost,
            "evidence_yield": efficiency.evidence_yield,
            "human_intervention_count": efficiency.human_intervention_count,
        }
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO observability_agent_efficiency_snapshots(
                        snapshot_id, run_id, settled_cost_available, wasted_work_ratio,
                        parallel_efficiency, snapshot_payload, snapshot_hash
                    ) VALUES (
                        :snapshot_id, :run_id, :settled_cost_available, :wasted_work_ratio,
                        :parallel_efficiency, CAST(:snapshot_payload AS jsonb), :snapshot_hash
                    )
                    ON CONFLICT (snapshot_id) DO NOTHING
                    """
                ),
                {
                    "snapshot_id": f"efficiency:{run_id}",
                    "run_id": run_id,
                    "settled_cost_available": efficiency.settled_cost_available,
                    "wasted_work_ratio": efficiency.wasted_work_ratio,
                    "parallel_efficiency": efficiency.parallel_efficiency,
                    "snapshot_payload": canonical_json(payload),
                    "snapshot_hash": canonical_sha256(payload),
                },
            )

    def complete_run(self, result_set: EvalRunResultSet) -> None:
        status = "COMPLETED" if result_set.complete else "PARTIAL"
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE observability_eval_runs
                    SET status = :status,
                        result_set_hash = :result_set_hash,
                        completed_at = now()
                    WHERE run_id = :run_id
                    """
                ),
                {"run_id": result_set.run_id, "status": status, "result_set_hash": result_set.result_set_hash},
            )

    def record_comparison(self, comparison: BenchmarkComparison) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO observability_benchmark_comparisons(
                        comparison_hash, baseline_run_id, candidate_run_id, comparable, status, reason
                    ) VALUES (
                        :comparison_hash, :baseline_run_id, :candidate_run_id, :comparable, :status, :reason
                    )
                    ON CONFLICT (comparison_hash) DO NOTHING
                    """
                ),
                {
                    "comparison_hash": comparison.comparison_hash,
                    "baseline_run_id": comparison.baseline_run_id,
                    "candidate_run_id": comparison.candidate_run_id,
                    "comparable": comparison.comparable,
                    "status": comparison.status.value,
                    "reason": comparison.reason,
                },
            )

    def record_release_gate(self, gate: ReleaseGateEvaluation, evidence: EvidenceRecord) -> None:
        if evidence.evidence_hash != gate.evidence_hash:
            raise EvalRuntimeError("release gate evidence hash mismatch")
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO observability_evidence_records(
                        evidence_hash, evidence_id, artifact_ref, artifact_hash,
                        result_set_hash, gate_hash, expires_at
                    ) VALUES (
                        :evidence_hash, :evidence_id, :artifact_ref, :artifact_hash,
                        :result_set_hash, :gate_hash, NULL
                    )
                    ON CONFLICT (evidence_hash) DO NOTHING
                    """
                ),
                {
                    "evidence_hash": evidence.evidence_hash,
                    "evidence_id": evidence.evidence_id,
                    "artifact_ref": evidence.artifact_ref,
                    "artifact_hash": evidence.artifact_hash,
                    "result_set_hash": evidence.result_set_hash,
                    "gate_hash": evidence.gate_hash,
                },
            )
            conn.execute(
                text(
                    """
                    INSERT INTO observability_release_gate_evaluations(
                        gate_hash, gate_id, status, reason, result_set_hash, comparison_hash, evidence_hash
                    ) VALUES (
                        :gate_hash, :gate_id, :status, :reason, :result_set_hash, :comparison_hash, :evidence_hash
                    )
                    ON CONFLICT (gate_hash) DO NOTHING
                    """
                ),
                {
                    "gate_hash": gate.gate_hash,
                    "gate_id": gate.gate_id,
                    "status": gate.status.value,
                    "reason": gate.reason,
                    "result_set_hash": gate.result_set_hash,
                    "comparison_hash": gate.comparison_hash,
                    "evidence_hash": gate.evidence_hash,
                },
            )
