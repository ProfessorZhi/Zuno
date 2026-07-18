from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum
import hashlib
import json
from typing import Any

from zuno.platform.security import SandboxAuditEvent, redact_sensitive_payload


class ZunoSpanKind(StrEnum):
    MODEL = "model"
    TOOL = "tool"
    RETRIEVAL = "retrieval"
    EVIDENCE = "evidence"
    CITATION = "citation"
    APPROVAL = "approval"
    SANDBOX = "sandbox"
    MEMORY = "memory"
    EVAL = "eval"
    CHAIN = "chain"


class ObservabilityTraceLifecycleState(StrEnum):
    PREPARED = "PREPARED"
    RUNTIME_OBSERVED = "RUNTIME_OBSERVED"
    MEASURED = "MEASURED"
    BLOCKED = "BLOCKED"
    QUALITY_PROVEN = "QUALITY_PROVEN"


class ObservabilityDeliveryState(StrEnum):
    PREPARED = "PREPARED"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class ObservabilityMetricStatus(StrEnum):
    MEASURED = "MEASURED"
    BLOCKED = "BLOCKED"
    UNAVAILABLE = "UNAVAILABLE"


class RAGCoreFiveMetric(StrEnum):
    CONTEXT_PRECISION = "CONTEXT_PRECISION"
    CONTEXT_RECALL = "CONTEXT_RECALL"
    FAITHFULNESS = "FAITHFULNESS"
    ANSWER_RELEVANCY = "ANSWER_RELEVANCY"
    ANSWER_CORRECTNESS = "ANSWER_CORRECTNESS"


def _canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class ZunoSpan:
    trace_id: str
    session_id: str
    thread_id: str
    task_id: str
    turn_id: str
    run_id: str
    parent_run_id: str | None
    run_type: str
    span_kind: ZunoSpanKind
    name: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    redacted_payload: dict[str, Any] = field(default_factory=dict)
    latency_ms: float | None = None
    cost: float | None = None
    error: str | None = None
    policy_decision: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_otel_span(self) -> dict[str, Any]:
        attributes = {
            "session_id": self.session_id,
            "thread_id": self.thread_id,
            "task_id": self.task_id,
            "turn_id": self.turn_id,
            "run_type": self.run_type,
            "span_kind": self.span_kind.value,
        }
        if self.latency_ms is not None:
            attributes["latency_ms"] = self.latency_ms
        if self.cost is not None:
            attributes["cost"] = self.cost
        if self.error is not None:
            attributes["error"] = self.error
        if self.policy_decision is not None:
            attributes["policy_decision"] = self.policy_decision
        attributes.update(deepcopy(self.metadata))
        for key, value in self.outputs.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                attributes.setdefault(key, value)

        return {
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "parent_run_id": self.parent_run_id,
            "name": self.name,
            "run_type": self.run_type,
            "span_kind": self.span_kind.value,
            "inputs": deepcopy(self.inputs),
            "outputs": deepcopy(self.outputs),
            "redacted_payload": deepcopy(self.redacted_payload),
            "attributes": redact_sensitive_payload(attributes),
        }


class ZunoSpanBuilder:
    def build_span(
        self,
        *,
        trace_id: str,
        session_id: str,
        thread_id: str,
        task_id: str,
        turn_id: str,
        run_id: str,
        parent_run_id: str | None,
        run_type: str,
        span_kind: ZunoSpanKind,
        name: str,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        redacted_payload: dict[str, Any] | None = None,
        latency_ms: float | None = None,
        cost: float | None = None,
        error: str | None = None,
        policy_decision: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ZunoSpan:
        return ZunoSpan(
            trace_id=trace_id,
            session_id=session_id,
            thread_id=thread_id,
            task_id=task_id,
            turn_id=turn_id,
            run_id=run_id,
            parent_run_id=parent_run_id,
            run_type=run_type,
            span_kind=span_kind,
            name=name,
            inputs=redact_sensitive_payload(inputs or {}),
            outputs=redact_sensitive_payload(outputs or {}),
            redacted_payload=redact_sensitive_payload(redacted_payload or {}),
            latency_ms=latency_ms,
            cost=cost,
            error=error,
            policy_decision=policy_decision,
            metadata=redact_sensitive_payload(metadata or {}),
        )

    def from_security_audit(
        self,
        audit: SandboxAuditEvent,
        *,
        run_id: str,
        parent_run_id: str | None = None,
    ) -> ZunoSpan:
        return self.build_span(
            trace_id=audit.trace_id,
            session_id=audit.workspace_id,
            thread_id="",
            task_id=audit.task_id,
            turn_id="",
            run_id=run_id,
            parent_run_id=parent_run_id,
            run_type="tool",
            span_kind=ZunoSpanKind.SANDBOX,
            name=f"security.{audit.gate.value}",
            inputs={
                "target": audit.target,
                "model_intent": audit.model_intent,
                "proposed_args": audit.proposed_args_redacted,
            },
            outputs={"final_decision": audit.final_decision},
            policy_decision=audit.policy_decision.value,
            metadata={
                "audit_id": audit.audit_id,
                "actor": audit.actor,
                "gate": audit.gate.value,
                "sandbox_profile": audit.sandbox_profile.value,
                "risk_reasons": list(audit.risk_reasons),
            },
        )


@dataclass(frozen=True, slots=True)
class LangSmithExportAdapter:
    project_name: str

    def to_run_payload(self, span: ZunoSpan) -> dict[str, Any]:
        metadata = {
            "project_name": self.project_name,
            "trace_id": span.trace_id,
            "session_id": span.session_id,
            "thread_id": span.thread_id,
            "task_id": span.task_id,
            "turn_id": span.turn_id,
            "span_kind": span.span_kind.value,
            "run_id": span.run_id,
        }
        if span.parent_run_id is not None:
            metadata["parent_run_id"] = span.parent_run_id
        metadata.update(deepcopy(span.redacted_payload))
        metadata.update(deepcopy(span.metadata))
        return {
            "name": span.name,
            "run_type": span.run_type,
            "id": span.run_id,
            "parent_run_id": span.parent_run_id,
            "inputs": deepcopy(span.inputs),
            "outputs": deepcopy(span.outputs),
            "metadata": redact_sensitive_payload(metadata),
        }


@dataclass(frozen=True, slots=True)
class EvalDatasetCase:
    case_id: str
    scenario: str
    workspace_fixture: str
    input_query: str
    expected_evidence_refs: list[str] = field(default_factory=list)
    expected_behavior: str = ""
    forbidden_tools: list[str] = field(default_factory=list)
    labels: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "scenario": self.scenario,
            "workspace_fixture": self.workspace_fixture,
            "input_query": self.input_query,
            "expected_evidence_refs": list(self.expected_evidence_refs),
            "expected_behavior": self.expected_behavior,
            "forbidden_tools": list(self.forbidden_tools),
            "labels": deepcopy(self.labels),
        }


@dataclass(frozen=True, slots=True)
class MetricThreshold:
    name: str
    operator: str
    value: float | int

    def passed(self, metric_value: float | int) -> bool:
        if self.operator == ">=":
            return metric_value >= self.value
        if self.operator == ">":
            return metric_value > self.value
        if self.operator == "<=":
            return metric_value <= self.value
        if self.operator == "<":
            return metric_value < self.value
        if self.operator == "==":
            return metric_value == self.value
        raise ValueError(f"unsupported metric threshold operator: {self.operator}")


@dataclass(frozen=True, slots=True)
class EvalMetricResult:
    name: str
    value: float | int
    threshold: float | int | None = None


@dataclass(frozen=True, slots=True)
class ReleaseEvalBaselineResult:
    dataset_version: str
    evaluator_version: str
    commit_sha: str
    status: str
    case_count: int
    metric_results: dict[str, dict[str, Any]]
    failure_examples: list[dict[str, Any]]

    def to_release_evidence(self) -> dict[str, Any]:
        return {
            "dataset_version": self.dataset_version,
            "evaluator_version": self.evaluator_version,
            "commit_sha": self.commit_sha,
            "status": self.status,
            "case_count": self.case_count,
            "metric_results": deepcopy(self.metric_results),
            "failure_examples": deepcopy(self.failure_examples),
        }


@dataclass(frozen=True, slots=True)
class ReleaseEvalBaseline:
    dataset_version: str
    evaluator_version: str
    commit_sha: str
    cases: list[EvalDatasetCase] = field(default_factory=list)
    metrics: list[EvalMetricResult] = field(default_factory=list)
    failure_examples: list[dict[str, Any]] = field(default_factory=list)

    def evaluate(self, thresholds: list[MetricThreshold]) -> ReleaseEvalBaselineResult:
        threshold_by_name = {threshold.name: threshold for threshold in thresholds}
        metric_results: dict[str, dict[str, Any]] = {}

        for metric in self.metrics:
            threshold = threshold_by_name.get(metric.name)
            passed = True if threshold is None else threshold.passed(metric.value)
            metric_results[metric.name] = {
                "value": metric.value,
                "configured_threshold": metric.threshold,
                "release_threshold": threshold.value if threshold else None,
                "operator": threshold.operator if threshold else None,
                "passed": passed,
            }

        status = "pass" if all(result["passed"] for result in metric_results.values()) else "fail"
        return ReleaseEvalBaselineResult(
            dataset_version=self.dataset_version,
            evaluator_version=self.evaluator_version,
            commit_sha=self.commit_sha,
            status=status,
            case_count=len(self.cases),
            metric_results=metric_results,
            failure_examples=redact_sensitive_payload(self.failure_examples),
        )


@dataclass(frozen=True, slots=True)
class ObservabilityTraceContext:
    trace_id: str
    tenant_id: str
    workspace_id: str
    correlation_id: str
    causation_id: str | None
    effective_security_epoch_ref: str


@dataclass(frozen=True, slots=True)
class ObservabilityTraceNode:
    span_id: str
    parent_span_id: str | None
    causation_id: str | None
    links: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ObservabilityEnvelope:
    envelope_type: str
    major_version: int
    minor_version: int
    payload_schema_hash: str
    payload_ref: str


@dataclass(frozen=True, slots=True)
class ObservabilityInboxReceipt:
    event_id: str
    payload_hash: str
    accepted: bool
    duplicate: bool


@dataclass(frozen=True, slots=True)
class ObservabilityOrderingWatermark:
    trace_id: str
    last_sequence: int
    gap_detected: bool
    gap_after: int | None


@dataclass(frozen=True, slots=True)
class ObservabilityLifecycleRecord:
    trace_id: str
    state: ObservabilityTraceLifecycleState
    previous_state: ObservabilityTraceLifecycleState | None
    transition_allowed: bool


@dataclass(frozen=True, slots=True)
class ObservabilityDomainTrace:
    domain: str
    required_fields: tuple[str, ...]
    payload: dict[str, Any]
    valid: bool


@dataclass(frozen=True, slots=True)
class ObservabilityAuditRecord:
    audit_id: str
    sequence: int
    previous_hash: str
    payload_hash: str
    audit_hash: str
    immutable: bool = True


@dataclass(frozen=True, slots=True)
class ObservabilitySamplingDecision:
    trace_id: str
    keep: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ObservabilityExternalSinkDelivery:
    delivery_id: str
    sink_id: str
    idempotency_key: str
    state: ObservabilityDeliveryState
    source_success: bool = False


@dataclass(frozen=True, slots=True)
class ObservabilityRetentionDisposition:
    object_ref: str
    retention_policy_ref: str
    legal_hold: bool
    delete_allowed: bool


@dataclass(frozen=True, slots=True)
class ObservabilityEvalDatasetVersion:
    dataset_id: str
    version: str
    case_hashes: tuple[str, ...]
    immutable_hash: str


@dataclass(frozen=True, slots=True)
class ObservabilityEvalCaseAttempt:
    run_id: str
    case_id: str
    attempt: int
    lease_ref: str
    checkpoint_ref: str
    recovered: bool


@dataclass(frozen=True, slots=True)
class ObservabilityJudgePolicy:
    policy_id: str
    version: str
    timeout_ms: int
    output_schema_hash: str


@dataclass(frozen=True, slots=True)
class ObservabilityFailureBucket:
    bucket: str
    required_trace_fields: tuple[str, ...]
    complete: bool


@dataclass(frozen=True, slots=True)
class ObservabilityBenchmarkComparison:
    baseline_input_hash: str
    candidate_input_hash: str
    comparable: bool


@dataclass(frozen=True, slots=True)
class ObservabilityProfileCompleteness:
    profile_id: str
    required_case_ids: tuple[str, ...]
    observed_case_ids: tuple[str, ...]
    complete: bool


@dataclass(frozen=True, slots=True)
class ObservabilityReleaseGateEvaluation:
    gate_id: str
    complete: bool
    comparable: bool
    thresholds_passed: bool
    accepted: bool


@dataclass(frozen=True, slots=True)
class ObservabilityMeasurementRecord:
    metric_name: str
    status: ObservabilityMetricStatus
    value: float | None
    reason: str


@dataclass(frozen=True, slots=True)
class ObservabilityEvidenceRecord:
    evidence_id: str
    artifact_ref: str
    artifact_hash: str
    supersedes: str | None
    validated: bool


@dataclass(frozen=True, slots=True)
class ObservabilityProjectionRebuild:
    projection_id: str
    append_log_ref: str
    replay_watermark: int
    source_replaced: bool = False


@dataclass(frozen=True, slots=True)
class ObservabilityQualityVerdict:
    measurement_status: ObservabilityMetricStatus
    comparable: bool
    release_gate_ref: str
    evidence_ref: str
    quality_proven: bool


@dataclass(frozen=True, slots=True)
class RAGMetricDefinition:
    metric: RAGCoreFiveMetric
    version: str
    aliases: tuple[str, ...]
    calibration_ref: str

    @property
    def metric_hash(self) -> str:
        return _canonical_hash([self.metric.value, self.version, self.aliases, self.calibration_ref])


@dataclass(frozen=True, slots=True)
class RAGMetricObservation:
    metric: RAGCoreFiveMetric
    status: ObservabilityMetricStatus
    value: float | None
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RAGRouteTrace:
    requested_route: str
    resolved_route: str
    route_changed: bool


@dataclass(frozen=True, slots=True)
class RAGGraphTraversalTrace:
    entity_ids: tuple[str, ...]
    relation_ids: tuple[str, ...]
    path_ids: tuple[str, ...]
    community_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RAGSourceGrounding:
    graph_ref: str
    source_span_refs: tuple[str, ...]
    grounded: bool


@dataclass(frozen=True, slots=True)
class RAGFusionRerankTrace:
    candidate_id: str
    original_rank: int
    final_rank: int
    dropped_reason: str | None


@dataclass(frozen=True, slots=True)
class AgenticLoopTrace:
    loop_id: str
    trigger: str
    outcome: str
    replan_ref: str | None


@dataclass(frozen=True, slots=True)
class ObservabilityEvaluationSlice:
    slice_id: str
    required_case_ids: tuple[str, ...]
    observed_case_ids: tuple[str, ...]
    complete: bool


@dataclass(frozen=True, slots=True)
class AgentEfficiencySnapshot:
    wall_time_ms: float
    active_time_ms: float
    queue_wait_ms: float
    critical_path_ms: float
    parallel_branch_time_sum_ms: float
    token_total: int
    estimated_cost: float
    settled_cost: float

    @property
    def parallel_efficiency(self) -> float:
        if self.parallel_branch_time_sum_ms <= 0:
            return 1.0
        return min(1.0, self.critical_path_ms / self.parallel_branch_time_sum_ms)


@dataclass(frozen=True, slots=True)
class QualityConstrainedEfficiency:
    quality_gate_passed: bool
    efficiency: AgentEfficiencySnapshot
    accepted: bool


@dataclass(frozen=True, slots=True)
class CostLatencyAttribution:
    usage_receipt_refs: tuple[str, ...]
    critical_path_ms: float
    settled_cost: float
    reconciled: bool


@dataclass(frozen=True, slots=True)
class ReproducibleEvidenceBundle:
    bundle_id: str
    artifact_hashes: tuple[str, ...]
    result_hash: str
    immutable: bool = True


class ObservabilityRuntimeBatch:
    def trace_context(
        self,
        *,
        trace_id: str,
        tenant_id: str,
        workspace_id: str,
        correlation_id: str,
        causation_id: str | None,
        effective_security_epoch_ref: str,
    ) -> ObservabilityTraceContext:
        return ObservabilityTraceContext(
            trace_id=trace_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            effective_security_epoch_ref=effective_security_epoch_ref,
        )

    def trace_tree(self, nodes: tuple[ObservabilityTraceNode, ...]) -> bool:
        span_ids = {node.span_id for node in nodes}
        return all(node.parent_span_id is None or node.parent_span_id in span_ids for node in nodes)

    def envelope(self, *, envelope_type: str, major_version: int, minor_version: int, payload: dict[str, Any]) -> ObservabilityEnvelope:
        if major_version <= 0:
            raise ValueError("unknown major version")
        return ObservabilityEnvelope(
            envelope_type=envelope_type,
            major_version=major_version,
            minor_version=minor_version,
            payload_schema_hash=_canonical_hash(sorted(payload)),
            payload_ref="payload_" + _canonical_hash(payload)[:16],
        )

    def inbox_receipt(self, *, event_id: str, payload: dict[str, Any], seen_hashes: set[str]) -> ObservabilityInboxReceipt:
        payload_hash = _canonical_hash(payload)
        duplicate = payload_hash in seen_hashes
        seen_hashes.add(payload_hash)
        return ObservabilityInboxReceipt(event_id=event_id, payload_hash=payload_hash, accepted=not duplicate, duplicate=duplicate)

    def ordering_watermark(self, *, trace_id: str, sequences: tuple[int, ...]) -> ObservabilityOrderingWatermark:
        ordered = sorted(sequences)
        expected = list(range(ordered[0], ordered[-1] + 1)) if ordered else []
        gap = ordered != expected
        missing = next((value for value in expected if value not in ordered), None)
        return ObservabilityOrderingWatermark(trace_id=trace_id, last_sequence=ordered[-1] if ordered else 0, gap_detected=gap, gap_after=missing)

    def lifecycle(self, *, trace_id: str, previous: ObservabilityTraceLifecycleState | None, state: ObservabilityTraceLifecycleState) -> ObservabilityLifecycleRecord:
        order = {
            ObservabilityTraceLifecycleState.PREPARED: 0,
            ObservabilityTraceLifecycleState.RUNTIME_OBSERVED: 1,
            ObservabilityTraceLifecycleState.MEASURED: 2,
            ObservabilityTraceLifecycleState.QUALITY_PROVEN: 3,
            ObservabilityTraceLifecycleState.BLOCKED: 99,
        }
        allowed = previous is None or state == ObservabilityTraceLifecycleState.BLOCKED or order[state] >= order[previous]
        return ObservabilityLifecycleRecord(trace_id=trace_id, state=state, previous_state=previous, transition_allowed=allowed)

    def domain_trace(self, *, domain: str, payload: dict[str, Any], required_fields: tuple[str, ...]) -> ObservabilityDomainTrace:
        return ObservabilityDomainTrace(domain=domain, required_fields=required_fields, payload=redact_sensitive_payload(payload), valid=all(field in payload for field in required_fields))

    def audit_record(self, *, audit_id: str, sequence: int, previous_hash: str, payload: dict[str, Any]) -> ObservabilityAuditRecord:
        payload_hash = _canonical_hash(redact_sensitive_payload(payload))
        audit_hash = _canonical_hash([audit_id, sequence, previous_hash, payload_hash])
        return ObservabilityAuditRecord(audit_id=audit_id, sequence=sequence, previous_hash=previous_hash, payload_hash=payload_hash, audit_hash=audit_hash)

    def sampling_decision(self, *, trace_id: str, high_risk: bool, debug: bool, sample_rate: float) -> ObservabilitySamplingDecision:
        if high_risk:
            return ObservabilitySamplingDecision(trace_id=trace_id, keep=True, reason="always_keep_high_risk")
        if debug:
            return ObservabilitySamplingDecision(trace_id=trace_id, keep=False, reason="never_sample_debug")
        return ObservabilitySamplingDecision(trace_id=trace_id, keep=sample_rate > 0, reason="sample_rate")

    def external_sink_delivery(self, *, delivery_id: str, sink_id: str, idempotency_key: str, delivered: bool) -> ObservabilityExternalSinkDelivery:
        return ObservabilityExternalSinkDelivery(
            delivery_id=delivery_id,
            sink_id=sink_id,
            idempotency_key=idempotency_key,
            state=ObservabilityDeliveryState.DELIVERED if delivered else ObservabilityDeliveryState.FAILED,
        )

    def retention_disposition(self, *, object_ref: str, retention_policy_ref: str, legal_hold: bool) -> ObservabilityRetentionDisposition:
        return ObservabilityRetentionDisposition(object_ref=object_ref, retention_policy_ref=retention_policy_ref, legal_hold=legal_hold, delete_allowed=not legal_hold)

    def eval_dataset_version(self, *, dataset_id: str, version: str, cases: tuple[EvalDatasetCase, ...]) -> ObservabilityEvalDatasetVersion:
        hashes = tuple(_canonical_hash(case.to_dict()) for case in cases)
        return ObservabilityEvalDatasetVersion(dataset_id=dataset_id, version=version, case_hashes=hashes, immutable_hash=_canonical_hash([dataset_id, version, hashes]))

    def eval_case_attempt(self, *, run_id: str, case_id: str, attempt: int, lease_ref: str, checkpoint_ref: str, recovered: bool) -> ObservabilityEvalCaseAttempt:
        return ObservabilityEvalCaseAttempt(run_id=run_id, case_id=case_id, attempt=attempt, lease_ref=lease_ref, checkpoint_ref=checkpoint_ref, recovered=recovered)

    def judge_policy(self, *, policy_id: str, version: str, timeout_ms: int, output_schema: dict[str, Any]) -> ObservabilityJudgePolicy:
        return ObservabilityJudgePolicy(policy_id=policy_id, version=version, timeout_ms=timeout_ms, output_schema_hash=_canonical_hash(output_schema))

    def failure_bucket(self, *, bucket: str, trace_payload: dict[str, Any], required_fields: tuple[str, ...]) -> ObservabilityFailureBucket:
        return ObservabilityFailureBucket(bucket=bucket, required_trace_fields=required_fields, complete=all(field in trace_payload for field in required_fields))

    def benchmark_comparison(self, *, baseline_input: dict[str, Any], candidate_input: dict[str, Any]) -> ObservabilityBenchmarkComparison:
        baseline_hash = _canonical_hash(baseline_input)
        candidate_hash = _canonical_hash(candidate_input)
        return ObservabilityBenchmarkComparison(baseline_input_hash=baseline_hash, candidate_input_hash=candidate_hash, comparable=baseline_hash == candidate_hash)

    def profile_completeness(self, *, profile_id: str, required_case_ids: tuple[str, ...], observed_case_ids: tuple[str, ...]) -> ObservabilityProfileCompleteness:
        return ObservabilityProfileCompleteness(profile_id=profile_id, required_case_ids=required_case_ids, observed_case_ids=observed_case_ids, complete=set(required_case_ids) <= set(observed_case_ids))

    def release_gate(self, *, gate_id: str, complete: bool, comparable: bool, thresholds_passed: bool) -> ObservabilityReleaseGateEvaluation:
        return ObservabilityReleaseGateEvaluation(gate_id=gate_id, complete=complete, comparable=comparable, thresholds_passed=thresholds_passed, accepted=complete and comparable and thresholds_passed)

    def measurement_record(self, *, metric_name: str, value: float | None, blocked_reason: str | None = None) -> ObservabilityMeasurementRecord:
        if blocked_reason:
            return ObservabilityMeasurementRecord(metric_name=metric_name, status=ObservabilityMetricStatus.BLOCKED, value=None, reason=blocked_reason)
        if value is None:
            return ObservabilityMeasurementRecord(metric_name=metric_name, status=ObservabilityMetricStatus.UNAVAILABLE, value=None, reason="missing_value")
        return ObservabilityMeasurementRecord(metric_name=metric_name, status=ObservabilityMetricStatus.MEASURED, value=value, reason="measured")

    def evidence_record(self, *, evidence_id: str, artifact_ref: str, artifact: dict[str, Any], supersedes: str | None = None) -> ObservabilityEvidenceRecord:
        return ObservabilityEvidenceRecord(evidence_id=evidence_id, artifact_ref=artifact_ref, artifact_hash=_canonical_hash(artifact), supersedes=supersedes, validated=True)

    def projection_rebuild(self, *, projection_id: str, append_log_ref: str, replay_watermark: int) -> ObservabilityProjectionRebuild:
        return ObservabilityProjectionRebuild(projection_id=projection_id, append_log_ref=append_log_ref, replay_watermark=replay_watermark)

    def quality_verdict(
        self,
        *,
        measurement_status: ObservabilityMetricStatus,
        comparable: bool,
        release_gate_ref: str,
        evidence_ref: str,
    ) -> ObservabilityQualityVerdict:
        return ObservabilityQualityVerdict(
            measurement_status=measurement_status,
            comparable=comparable,
            release_gate_ref=release_gate_ref,
            evidence_ref=evidence_ref,
            quality_proven=measurement_status == ObservabilityMetricStatus.MEASURED and comparable and bool(release_gate_ref and evidence_ref),
        )

    def rag_metric_definition(self, *, metric: RAGCoreFiveMetric, version: str, aliases: tuple[str, ...], calibration_ref: str) -> RAGMetricDefinition:
        return RAGMetricDefinition(metric=metric, version=version, aliases=aliases, calibration_ref=calibration_ref)

    def rag_metric_observation(self, *, metric: RAGCoreFiveMetric, value: float | None, evidence_refs: tuple[str, ...]) -> RAGMetricObservation:
        status = ObservabilityMetricStatus.MEASURED if value is not None else ObservabilityMetricStatus.UNAVAILABLE
        return RAGMetricObservation(metric=metric, status=status, value=value, evidence_refs=evidence_refs)

    def rag_route_trace(self, *, requested_route: str, resolved_route: str) -> RAGRouteTrace:
        return RAGRouteTrace(requested_route=requested_route, resolved_route=resolved_route, route_changed=requested_route != resolved_route)

    def rag_graph_trace(self, *, entity_ids: tuple[str, ...], relation_ids: tuple[str, ...], path_ids: tuple[str, ...], community_ids: tuple[str, ...]) -> RAGGraphTraversalTrace:
        return RAGGraphTraversalTrace(entity_ids=entity_ids, relation_ids=relation_ids, path_ids=path_ids, community_ids=community_ids)

    def rag_source_grounding(self, *, graph_ref: str, source_span_refs: tuple[str, ...]) -> RAGSourceGrounding:
        return RAGSourceGrounding(graph_ref=graph_ref, source_span_refs=source_span_refs, grounded=bool(graph_ref and source_span_refs))

    def rag_fusion_rerank_trace(self, *, candidate_id: str, original_rank: int, final_rank: int, dropped_reason: str | None = None) -> RAGFusionRerankTrace:
        return RAGFusionRerankTrace(candidate_id=candidate_id, original_rank=original_rank, final_rank=final_rank, dropped_reason=dropped_reason)

    def agentic_loop_trace(self, *, loop_id: str, trigger: str, outcome: str, replan_ref: str | None) -> AgenticLoopTrace:
        return AgenticLoopTrace(loop_id=loop_id, trigger=trigger, outcome=outcome, replan_ref=replan_ref)

    def evaluation_slice(self, *, slice_id: str, required_case_ids: tuple[str, ...], observed_case_ids: tuple[str, ...]) -> ObservabilityEvaluationSlice:
        return ObservabilityEvaluationSlice(slice_id=slice_id, required_case_ids=required_case_ids, observed_case_ids=observed_case_ids, complete=set(required_case_ids) <= set(observed_case_ids))

    def efficiency_snapshot(self, **values: Any) -> AgentEfficiencySnapshot:
        return AgentEfficiencySnapshot(**values)

    def quality_constrained_efficiency(self, *, quality_gate_passed: bool, efficiency: AgentEfficiencySnapshot) -> QualityConstrainedEfficiency:
        return QualityConstrainedEfficiency(quality_gate_passed=quality_gate_passed, efficiency=efficiency, accepted=quality_gate_passed)

    def cost_latency_attribution(self, *, usage_receipt_refs: tuple[str, ...], critical_path_ms: float, settled_cost: float) -> CostLatencyAttribution:
        return CostLatencyAttribution(usage_receipt_refs=usage_receipt_refs, critical_path_ms=critical_path_ms, settled_cost=settled_cost, reconciled=bool(usage_receipt_refs))

    def core_five_release_gate(self, observations: tuple[RAGMetricObservation, ...]) -> bool:
        measured = {observation.metric for observation in observations if observation.status == ObservabilityMetricStatus.MEASURED}
        return set(RAGCoreFiveMetric) <= measured

    def reproducible_evidence(self, *, bundle_id: str, artifacts: tuple[dict[str, Any], ...], result: dict[str, Any]) -> ReproducibleEvidenceBundle:
        artifact_hashes = tuple(_canonical_hash(artifact) for artifact in artifacts)
        return ReproducibleEvidenceBundle(bundle_id=bundle_id, artifact_hashes=artifact_hashes, result_hash=_canonical_hash(result))


__all__ = [
    "AgentEfficiencySnapshot",
    "AgenticLoopTrace",
    "CostLatencyAttribution",
    "EvalDatasetCase",
    "EvalMetricResult",
    "LangSmithExportAdapter",
    "MetricThreshold",
    "ObservabilityAuditRecord",
    "ObservabilityBenchmarkComparison",
    "ObservabilityDeliveryState",
    "ObservabilityDomainTrace",
    "ObservabilityEnvelope",
    "ObservabilityEvaluationSlice",
    "ObservabilityEvalCaseAttempt",
    "ObservabilityEvalDatasetVersion",
    "ObservabilityEvidenceRecord",
    "ObservabilityExternalSinkDelivery",
    "ObservabilityFailureBucket",
    "ObservabilityInboxReceipt",
    "ObservabilityJudgePolicy",
    "ObservabilityLifecycleRecord",
    "ObservabilityMeasurementRecord",
    "ObservabilityMetricStatus",
    "ObservabilityOrderingWatermark",
    "ObservabilityProfileCompleteness",
    "ObservabilityProjectionRebuild",
    "ObservabilityQualityVerdict",
    "ObservabilityReleaseGateEvaluation",
    "ObservabilityRetentionDisposition",
    "ObservabilityRuntimeBatch",
    "ObservabilitySamplingDecision",
    "ObservabilityTraceContext",
    "ObservabilityTraceLifecycleState",
    "ObservabilityTraceNode",
    "QualityConstrainedEfficiency",
    "RAGCoreFiveMetric",
    "RAGFusionRerankTrace",
    "RAGGraphTraversalTrace",
    "RAGMetricDefinition",
    "RAGMetricObservation",
    "RAGRouteTrace",
    "RAGSourceGrounding",
    "ReproducibleEvidenceBundle",
    "ReleaseEvalBaseline",
    "ReleaseEvalBaselineResult",
    "ZunoSpan",
    "ZunoSpanBuilder",
    "ZunoSpanKind",
]
