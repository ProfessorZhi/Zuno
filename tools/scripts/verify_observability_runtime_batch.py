from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "backend"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from zuno.platform.observability import (  # noqa: E402
    EvalDatasetCase,
    ObservabilityMetricStatus,
    ObservabilityRuntimeBatch,
    ObservabilityTraceLifecycleState,
    ObservabilityTraceNode,
    RAGCoreFiveMetric,
)


REQUIREMENTS = tuple(f"ARCH-OBS-{index:03d}" for index in range(1, 25)) + tuple(
    f"ARCH-OBS-RAG-{index:03d}" for index in range(1, 21)
)


def verify_observability_runtime_batch() -> list[str]:
    errors: list[str] = []
    runtime = ObservabilityRuntimeBatch()

    context = runtime.trace_context(
        trace_id="trace:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="corr:1",
        causation_id="cause:1",
        effective_security_epoch_ref="security-epoch:1",
    )
    if not all([context.trace_id, context.correlation_id, context.effective_security_epoch_ref]):
        errors.append("trace context lacks scope, propagation, or security epoch")

    if not runtime.trace_tree(
        (
            ObservabilityTraceNode(span_id="root", parent_span_id=None, causation_id=None),
            ObservabilityTraceNode(span_id="child", parent_span_id="root", causation_id="root"),
        )
    ):
        errors.append("trace tree parent/link/causation reducer rejected valid tree")

    envelope = runtime.envelope(envelope_type="TelemetryEnvelopeV1", major_version=1, minor_version=0, payload={"kind": "trace"})
    if envelope.major_version != 1 or not envelope.payload_schema_hash:
        errors.append("envelope versioning lacks schema hash or known major")

    seen: set[str] = set()
    first = runtime.inbox_receipt(event_id="event:1", payload={"sequence": 1}, seen_hashes=seen)
    duplicate = runtime.inbox_receipt(event_id="event:1-dup", payload={"sequence": 1}, seen_hashes=seen)
    if not first.accepted or not duplicate.duplicate or duplicate.accepted:
        errors.append("dedup inbox did not reject duplicate payload hash")

    watermark = runtime.ordering_watermark(trace_id="trace:1", sequences=(1, 2, 4))
    if not watermark.gap_detected or watermark.gap_after != 3:
        errors.append("ordering watermark did not detect sequence gap")

    lifecycle = runtime.lifecycle(
        trace_id="trace:1",
        previous=ObservabilityTraceLifecycleState.RUNTIME_OBSERVED,
        state=ObservabilityTraceLifecycleState.MEASURED,
    )
    if not lifecycle.transition_allowed:
        errors.append("trace lifecycle rejected forward transition")

    for domain, payload, required in [
        ("agent_core", {"task_id": "task:1", "plan_version_ref": "plan:1"}, ("task_id", "plan_version_ref")),
        ("model", {"attempt_ref": "attempt:1", "usage_ref": "usage:1"}, ("attempt_ref", "usage_ref")),
        ("retrieval", {"retrieval_round_ref": "round:1", "evidence_ref": "evidence:1"}, ("retrieval_round_ref", "evidence_ref")),
        ("tool", {"tool_attempt_ref": "tool:1", "effect_ref": "effect:1"}, ("tool_attempt_ref", "effect_ref")),
    ]:
        if not runtime.domain_trace(domain=domain, payload=payload, required_fields=required).valid:
            errors.append(f"{domain} trace lacks required fields")

    redacted = runtime.domain_trace(
        domain="security",
        payload={"api_key": "sk-secret", "decision": "deny"},
        required_fields=("api_key", "decision"),
    )
    if "sk-secret" in repr(redacted.payload):
        errors.append("security redaction did not remove secret")

    audit = runtime.audit_record(audit_id="audit:1", sequence=1, previous_hash="root", payload={"decision": "deny"})
    if not audit.immutable or not audit.audit_hash:
        errors.append("audit record is not immutable append/hash evidence")

    if not runtime.sampling_decision(trace_id="trace:1", high_risk=True, debug=False, sample_rate=0).keep:
        errors.append("sampling did not always keep high-risk trace")
    if runtime.sampling_decision(trace_id="trace:debug", high_risk=False, debug=True, sample_rate=1).keep:
        errors.append("sampling did not honor never-sample debug policy")

    delivery = runtime.external_sink_delivery(
        delivery_id="delivery:1",
        sink_id="sink:langsmith",
        idempotency_key="idem:delivery:1",
        delivered=True,
    )
    if delivery.source_success or not delivery.idempotency_key:
        errors.append("external sink delivery replaced source success or lost idempotency")

    retention = runtime.retention_disposition(
        object_ref="trace-object:1",
        retention_policy_ref="retention:30d",
        legal_hold=True,
    )
    if retention.delete_allowed:
        errors.append("retention/legal hold precedence allowed delete")

    dataset = runtime.eval_dataset_version(
        dataset_id="dataset:rag",
        version="v1",
        cases=(
            EvalDatasetCase(
                case_id="case:1",
                scenario="grounding",
                workspace_fixture="workspace-fixture",
                input_query="Where is the answer?",
            ),
        ),
    )
    if not dataset.immutable_hash or len(dataset.case_hashes) != 1:
        errors.append("eval dataset/case lacks immutable version hash")

    attempt = runtime.eval_case_attempt(
        run_id="eval-run:1",
        case_id="case:1",
        attempt=2,
        lease_ref="lease:1",
        checkpoint_ref="checkpoint:1",
        recovered=True,
    )
    if not (attempt.recovered and attempt.lease_ref and attempt.checkpoint_ref):
        errors.append("eval run/case recovery lacks lease/checkpoint/attempt evidence")

    judge = runtime.judge_policy(policy_id="judge:faithfulness", version="v1", timeout_ms=2500, output_schema={"score": "float"})
    if not judge.output_schema_hash or judge.timeout_ms <= 0:
        errors.append("judge policy lacks version/timeout/schema guard")

    bucket = runtime.failure_bucket(
        bucket="citation_hit_answer_wrong",
        trace_payload={"claim_ref": "claim:1", "citation_ref": "citation:1"},
        required_fields=("claim_ref", "citation_ref"),
    )
    if not bucket.complete:
        errors.append("failure bucket lacks required trace fields")

    comparable = runtime.benchmark_comparison(baseline_input={"dataset": "v1"}, candidate_input={"dataset": "v1"})
    if not comparable.comparable:
        errors.append("benchmark comparison did not pin comparable inputs")

    profile = runtime.profile_completeness(
        profile_id="release-profile",
        required_case_ids=("case:1", "case:2"),
        observed_case_ids=("case:1", "case:2", "case:3"),
    )
    if not profile.complete:
        errors.append("profile completeness guard rejected complete case set")

    release = runtime.release_gate(gate_id="release:1", complete=True, comparable=True, thresholds_passed=True)
    if not release.accepted:
        errors.append("release gate did not require completeness/comparability/thresholds")

    measured = runtime.measurement_record(metric_name="faithfulness", value=0.9)
    blocked = runtime.measurement_record(metric_name="answer_correctness", value=None, blocked_reason="missing_reference")
    if measured.status != ObservabilityMetricStatus.MEASURED or blocked.status != ObservabilityMetricStatus.BLOCKED:
        errors.append("measurement status collapsed measured/blocked states")

    evidence = runtime.evidence_record(evidence_id="ev:1", artifact_ref="artifact:1", artifact={"status": "pass"})
    if not evidence.validated or not evidence.artifact_hash:
        errors.append("evidence registry lacks artifact hash validation")

    projection = runtime.projection_rebuild(projection_id="projection:1", append_log_ref="outbox:obs", replay_watermark=42)
    if projection.source_replaced or projection.replay_watermark != 42:
        errors.append("projection rebuild replaced source or lost replay watermark")

    quality = runtime.quality_verdict(
        measurement_status=ObservabilityMetricStatus.MEASURED,
        comparable=True,
        release_gate_ref="release:1",
        evidence_ref="ev:1",
    )
    if not quality.quality_proven:
        errors.append("quality proven did not require measurement/comparability/gate/evidence")

    definitions = tuple(
        runtime.rag_metric_definition(metric=metric, version="v1", aliases=(metric.value.lower(),), calibration_ref="calibration:v1")
        for metric in RAGCoreFiveMetric
    )
    if {definition.metric for definition in definitions} != set(RAGCoreFiveMetric):
        errors.append("RAG core five metric registry incomplete")
    if not all(definition.metric_hash for definition in definitions):
        errors.append("RAG metric version/calibration hash missing")

    observations = tuple(
        runtime.rag_metric_observation(metric=metric, value=0.8, evidence_refs=(f"evidence:{metric.value}",))
        for metric in RAGCoreFiveMetric
    )
    if not runtime.core_five_release_gate(observations):
        errors.append("RAG core five release gate did not require all metrics")

    if runtime.rag_metric_observation(metric=RAGCoreFiveMetric.CONTEXT_PRECISION, value=None, evidence_refs=()).value == 0:
        errors.append("RAG metric null value was treated as zero")

    route = runtime.rag_route_trace(requested_route="standard_rag", resolved_route="agentic_graphrag")
    if not route.route_changed:
        errors.append("route trace did not record requested/resolved route")

    graph = runtime.rag_graph_trace(
        entity_ids=("entity:1",),
        relation_ids=("relation:1",),
        path_ids=("path:1",),
        community_ids=("community:1",),
    )
    if not (graph.entity_ids and graph.relation_ids and graph.path_ids and graph.community_ids):
        errors.append("graph traversal trace lacks entity/relation/path/community fields")

    if not runtime.rag_source_grounding(graph_ref="graph:1", source_span_refs=("source-span:1",)).grounded:
        errors.append("source grounding did not require graph and source span")

    rerank = runtime.rag_fusion_rerank_trace(candidate_id="candidate:1", original_rank=5, final_rank=1)
    dropped = runtime.rag_fusion_rerank_trace(candidate_id="candidate:2", original_rank=2, final_rank=99, dropped_reason="duplicate")
    if rerank.final_rank >= rerank.original_rank or dropped.dropped_reason != "duplicate":
        errors.append("fusion/rerank trace lacks rank lineage or dropped reason")

    loop = runtime.agentic_loop_trace(
        loop_id="loop:1",
        trigger="retrieval_quality_low",
        outcome="replan",
        replan_ref="plan:2",
    )
    if loop.replan_ref != "plan:2":
        errors.append("agentic loop trace lacks trigger/outcome/replan")

    if not runtime.failure_bucket(
        bucket="fusion_dropped_gold_evidence",
        trace_payload={"candidate_id": "candidate:2", "dropped_reason": "duplicate"},
        required_fields=("candidate_id", "dropped_reason"),
    ).complete:
        errors.append("RAG failure bucket required-field classifier failed")

    if not runtime.evaluation_slice(
        slice_id="slice:graph",
        required_case_ids=("case:1", "case:2"),
        observed_case_ids=("case:1", "case:2"),
    ).complete:
        errors.append("evaluation slice completeness guard failed")

    efficiency = runtime.efficiency_snapshot(
        wall_time_ms=1000.0,
        active_time_ms=800.0,
        queue_wait_ms=200.0,
        critical_path_ms=400.0,
        parallel_branch_time_sum_ms=800.0,
        token_total=1200,
        estimated_cost=0.5,
        settled_cost=0.45,
    )
    if efficiency.parallel_efficiency != 0.5:
        errors.append("agent efficiency snapshot did not compute parallel efficiency")

    if not runtime.quality_constrained_efficiency(quality_gate_passed=True, efficiency=efficiency).accepted:
        errors.append("quality-constrained efficiency ignored quality-first gate")

    attribution = runtime.cost_latency_attribution(
        usage_receipt_refs=("usage:1", "usage:2"),
        critical_path_ms=efficiency.critical_path_ms,
        settled_cost=efficiency.settled_cost,
    )
    if not attribution.reconciled:
        errors.append("cost/latency attribution did not reconcile usage receipts")

    reproducible = runtime.reproducible_evidence(
        bundle_id="bundle:obs",
        artifacts=({"dataset": "v1"}, {"run": "eval-run:1"}),
        result={"status": "pass"},
    )
    if not reproducible.immutable or len(reproducible.artifact_hashes) != 2 or not reproducible.result_hash:
        errors.append("reproducible evidence lacks immutable artifact/result hashes")

    return errors


def main() -> int:
    errors = verify_observability_runtime_batch()
    if errors:
        print("Observability runtime batch verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Observability runtime batch verification passed for {', '.join(REQUIREMENTS)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
