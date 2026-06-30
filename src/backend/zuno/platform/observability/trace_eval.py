from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum
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


__all__ = [
    "EvalDatasetCase",
    "EvalMetricResult",
    "LangSmithExportAdapter",
    "MetricThreshold",
    "ReleaseEvalBaseline",
    "ReleaseEvalBaselineResult",
    "ZunoSpan",
    "ZunoSpanBuilder",
    "ZunoSpanKind",
]
