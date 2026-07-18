from __future__ import annotations

from zuno.platform.observability import (
    EvalDatasetCase,
    ObservabilityMetricStatus,
    ObservabilityRuntimeBatch,
    ObservabilityTraceLifecycleState,
    ObservabilityTraceNode,
    RAGCoreFiveMetric,
)


def test_observability_runtime_batch_platform_boundaries() -> None:
    runtime = ObservabilityRuntimeBatch()

    context = runtime.trace_context(
        trace_id="trace:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="corr:1",
        causation_id="cause:1",
        effective_security_epoch_ref="security-epoch:1",
    )
    assert context.effective_security_epoch_ref == "security-epoch:1"

    assert runtime.trace_tree(
        (
            ObservabilityTraceNode(span_id="root", parent_span_id=None, causation_id=None),
            ObservabilityTraceNode(span_id="child", parent_span_id="root", causation_id="root"),
        )
    )

    envelope = runtime.envelope(envelope_type="TelemetryEnvelopeV1", major_version=1, minor_version=0, payload={"kind": "trace"})
    assert envelope.major_version == 1 and envelope.payload_schema_hash

    seen: set[str] = set()
    first = runtime.inbox_receipt(event_id="event:1", payload={"sequence": 1}, seen_hashes=seen)
    duplicate = runtime.inbox_receipt(event_id="event:1-dup", payload={"sequence": 1}, seen_hashes=seen)
    assert first.accepted is True
    assert duplicate.duplicate is True and duplicate.accepted is False

    watermark = runtime.ordering_watermark(trace_id="trace:1", sequences=(1, 2, 4))
    assert watermark.gap_detected is True and watermark.gap_after == 3

    lifecycle = runtime.lifecycle(
        trace_id="trace:1",
        previous=ObservabilityTraceLifecycleState.RUNTIME_OBSERVED,
        state=ObservabilityTraceLifecycleState.MEASURED,
    )
    assert lifecycle.transition_allowed is True

    agent_trace = runtime.domain_trace(
        domain="agent_core",
        payload={"task_id": "task:1", "plan_version_ref": "plan:1"},
        required_fields=("task_id", "plan_version_ref"),
    )
    model_trace = runtime.domain_trace(
        domain="model",
        payload={"attempt_ref": "attempt:1", "usage_ref": "usage:1"},
        required_fields=("attempt_ref", "usage_ref"),
    )
    redacted = runtime.domain_trace(
        domain="security",
        payload={"api_key": "sk-secret", "decision": "deny"},
        required_fields=("api_key", "decision"),
    )
    assert agent_trace.valid and model_trace.valid and redacted.valid
    assert "sk-secret" not in repr(redacted.payload)

    audit = runtime.audit_record(audit_id="audit:1", sequence=1, previous_hash="root", payload={"decision": "deny"})
    assert audit.immutable is True and audit.audit_hash

    assert runtime.sampling_decision(trace_id="trace:1", high_risk=True, debug=False, sample_rate=0).keep is True
    assert runtime.sampling_decision(trace_id="trace:debug", high_risk=False, debug=True, sample_rate=1).keep is False

    delivery = runtime.external_sink_delivery(
        delivery_id="delivery:1",
        sink_id="sink:langsmith",
        idempotency_key="idem:delivery:1",
        delivered=True,
    )
    assert delivery.state.value == "DELIVERED"
    assert delivery.source_success is False

    retention = runtime.retention_disposition(
        object_ref="trace-object:1",
        retention_policy_ref="retention:30d",
        legal_hold=True,
    )
    assert retention.delete_allowed is False

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
    assert dataset.immutable_hash and len(dataset.case_hashes) == 1

    attempt = runtime.eval_case_attempt(
        run_id="eval-run:1",
        case_id="case:1",
        attempt=2,
        lease_ref="lease:1",
        checkpoint_ref="checkpoint:1",
        recovered=True,
    )
    assert attempt.recovered is True and attempt.lease_ref and attempt.checkpoint_ref

    judge = runtime.judge_policy(policy_id="judge:faithfulness", version="v1", timeout_ms=2500, output_schema={"score": "float"})
    assert judge.output_schema_hash and judge.timeout_ms == 2500

    bucket = runtime.failure_bucket(
        bucket="citation_hit_answer_wrong",
        trace_payload={"claim_ref": "claim:1", "citation_ref": "citation:1"},
        required_fields=("claim_ref", "citation_ref"),
    )
    assert bucket.complete is True

    comparable = runtime.benchmark_comparison(baseline_input={"dataset": "v1"}, candidate_input={"dataset": "v1"})
    assert comparable.comparable is True

    profile = runtime.profile_completeness(
        profile_id="release-profile",
        required_case_ids=("case:1", "case:2"),
        observed_case_ids=("case:1", "case:2", "case:3"),
    )
    assert profile.complete is True

    release = runtime.release_gate(gate_id="release:1", complete=True, comparable=True, thresholds_passed=True)
    assert release.accepted is True

    measured = runtime.measurement_record(metric_name="faithfulness", value=0.9)
    blocked = runtime.measurement_record(metric_name="answer_correctness", value=None, blocked_reason="missing_reference")
    assert measured.status == ObservabilityMetricStatus.MEASURED
    assert blocked.value is None and blocked.status == ObservabilityMetricStatus.BLOCKED

    evidence = runtime.evidence_record(evidence_id="ev:1", artifact_ref="artifact:1", artifact={"status": "pass"})
    assert evidence.validated is True and evidence.artifact_hash

    projection = runtime.projection_rebuild(projection_id="projection:1", append_log_ref="outbox:obs", replay_watermark=42)
    assert projection.source_replaced is False and projection.replay_watermark == 42

    quality = runtime.quality_verdict(
        measurement_status=ObservabilityMetricStatus.MEASURED,
        comparable=True,
        release_gate_ref="release:1",
        evidence_ref="ev:1",
    )
    assert quality.quality_proven is True


def test_observability_runtime_batch_rag_and_agentic_boundaries() -> None:
    runtime = ObservabilityRuntimeBatch()

    definitions = tuple(
        runtime.rag_metric_definition(metric=metric, version="v1", aliases=(metric.value.lower(),), calibration_ref="calibration:v1")
        for metric in RAGCoreFiveMetric
    )
    assert {definition.metric for definition in definitions} == set(RAGCoreFiveMetric)
    assert all(definition.metric_hash for definition in definitions)

    observations = tuple(
        runtime.rag_metric_observation(metric=metric, value=0.8, evidence_refs=(f"evidence:{metric.value}",))
        for metric in RAGCoreFiveMetric
    )
    assert runtime.core_five_release_gate(observations) is True
    assert all(observation.status == ObservabilityMetricStatus.MEASURED for observation in observations)

    route = runtime.rag_route_trace(requested_route="standard_rag", resolved_route="agentic_graphrag")
    assert route.route_changed is True

    graph = runtime.rag_graph_trace(
        entity_ids=("entity:1",),
        relation_ids=("relation:1",),
        path_ids=("path:1",),
        community_ids=("community:1",),
    )
    assert graph.entity_ids and graph.relation_ids and graph.path_ids and graph.community_ids

    grounding = runtime.rag_source_grounding(graph_ref="graph:1", source_span_refs=("source-span:1",))
    assert grounding.grounded is True

    rerank = runtime.rag_fusion_rerank_trace(candidate_id="candidate:1", original_rank=5, final_rank=1)
    dropped = runtime.rag_fusion_rerank_trace(candidate_id="candidate:2", original_rank=2, final_rank=99, dropped_reason="duplicate")
    assert rerank.final_rank < rerank.original_rank
    assert dropped.dropped_reason == "duplicate"

    loop = runtime.agentic_loop_trace(
        loop_id="loop:1",
        trigger="retrieval_quality_low",
        outcome="replan",
        replan_ref="plan:2",
    )
    assert loop.replan_ref == "plan:2"

    failure_bucket = runtime.failure_bucket(
        bucket="fusion_dropped_gold_evidence",
        trace_payload={"candidate_id": "candidate:2", "dropped_reason": "duplicate"},
        required_fields=("candidate_id", "dropped_reason"),
    )
    assert failure_bucket.complete is True

    evaluation_slice = runtime.evaluation_slice(
        slice_id="slice:graph",
        required_case_ids=("case:1", "case:2"),
        observed_case_ids=("case:1", "case:2"),
    )
    assert evaluation_slice.complete is True

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
    assert efficiency.parallel_efficiency == 0.5

    quality_efficiency = runtime.quality_constrained_efficiency(quality_gate_passed=True, efficiency=efficiency)
    assert quality_efficiency.accepted is True

    attribution = runtime.cost_latency_attribution(
        usage_receipt_refs=("usage:1", "usage:2"),
        critical_path_ms=efficiency.critical_path_ms,
        settled_cost=efficiency.settled_cost,
    )
    assert attribution.reconciled is True

    reproducible = runtime.reproducible_evidence(
        bundle_id="bundle:obs",
        artifacts=({"dataset": "v1"}, {"run": "eval-run:1"}),
        result={"status": "pass"},
    )
    assert reproducible.immutable is True
    assert len(reproducible.artifact_hashes) == 2
