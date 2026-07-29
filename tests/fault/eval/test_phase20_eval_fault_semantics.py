from __future__ import annotations

from zuno.platform.contracts import canonical_sha256
from zuno.platform.observability.eval_runtime import (
    AgentEfficiencyVector,
    CaseExecutionResult,
    EvalCase,
    EvalDatasetVersion,
    EvalRunConfig,
    EvalRunResultSet,
    EvalRunStatus,
    RAGCoreFiveEvaluator,
    RAGCoreFiveInputBundle,
    ReleaseGateStatus,
    compare_benchmark_runs,
    evaluate_release_gate,
)


def _hash(name: str) -> str:
    return canonical_sha256({"fault": name})


def _config(dataset_hash: str, *, model_profile: str = "model-a") -> EvalRunConfig:
    return EvalRunConfig(
        dataset_hash=dataset_hash,
        corpus_snapshot_hash=_hash("corpus"),
        index_snapshot_hash=_hash("index"),
        model_profile_hash=_hash(model_profile),
        judge_policy_hash=_hash("judge"),
        embedding_profile_hash=_hash("embedding"),
        metric_config_hash=_hash("metric"),
        runtime_profile_hash=_hash("runtime"),
        security_scope_hash=_hash("security"),
    )


def _dataset() -> EvalDatasetVersion:
    return EvalDatasetVersion(
        dataset_id="phase20-fault",
        version="v1",
        cases=(
            EvalCase(
                case_id="case-1",
                question="Which clause governs renewal?",
                reference_claim_refs=("claim-renewal",),
                gold_evidence_refs=("doc-1#renewal",),
                slices=("citation-required",),
                security_scope_ref="scope:tenant-a:workspace-a",
            ),
        ),
    )


def _measured_case() -> CaseExecutionResult:
    return CaseExecutionResult(
        case_id="case-1",
        status=EvalRunStatus.COMPLETED,
        attempt=1,
        lease_ref="lease:case-1",
        checkpoint_ref="checkpoint:case-1",
        metric_results=RAGCoreFiveEvaluator().evaluate(
            RAGCoreFiveInputBundle(
                case_id="case-1",
                retrieved_context_refs=("ctx-1",),
                reference_claim_refs=("claim-renewal",),
                retrieved_context_supported_reference_claim_refs=("claim-renewal",),
                generated_claim_refs=("claim-renewal",),
                supported_generated_claim_refs=("claim-renewal",),
                true_positive_claim_refs=("claim-renewal",),
                false_positive_claim_refs=(),
                false_negative_claim_refs=(),
                answer_relevant=True,
            )
        ),
        failure_buckets=(),
    )


def _efficiency(*, settled: bool = True) -> AgentEfficiencyVector:
    return AgentEfficiencyVector(
        plan_steps=2,
        retry_count=1,
        replan_count=0,
        reflection_count=0,
        tool_call_count=0,
        model_call_count=1,
        retrieval_call_count=1,
        wall_time_ms=1000,
        active_time_ms=900,
        queue_wait_ms=20,
        critical_path_ms=700,
        parallel_branch_time_sum_ms=900,
        token_total=800,
        estimated_cost=0.08,
        settled_cost=0.08 if settled else None,
        evidence_yield=1.0,
    )


def test_phase20_worker_crash_partial_attempt_does_not_publish_measured_claim_until_recovered_attempt() -> None:
    dataset = _dataset()
    config = _config(dataset.dataset_hash)
    partial_attempt = CaseExecutionResult(
        case_id="case-1",
        status=EvalRunStatus.PARTIAL,
        attempt=1,
        lease_ref="lease:attempt-1",
        checkpoint_ref="checkpoint:attempt-1",
        metric_results=_measured_case().metric_results,
        failure_buckets=("worker_crash",),
    )
    partial_run = EvalRunResultSet(
        run_id="run-partial",
        profile_id="agentic_graphrag",
        config=config,
        case_results=(partial_attempt,),
        efficiency=_efficiency(),
    )
    recovered_attempt = _measured_case()
    recovered_attempt = CaseExecutionResult(
        case_id=recovered_attempt.case_id,
        status=recovered_attempt.status,
        attempt=2,
        lease_ref="lease:attempt-2",
        checkpoint_ref="checkpoint:attempt-2",
        metric_results=recovered_attempt.metric_results,
        failure_buckets=(),
        recovered=True,
    )
    recovered_run = EvalRunResultSet(
        run_id="run-recovered",
        profile_id="agentic_graphrag",
        config=config,
        case_results=(recovered_attempt,),
        efficiency=_efficiency(),
    )

    assert partial_run.complete is False
    assert recovered_run.complete is True
    assert compare_benchmark_runs(recovered_run, partial_run).status == ReleaseGateStatus.BLOCKED


def test_phase20_cancelled_case_blocks_release_gate_without_becoming_failed_or_passed() -> None:
    dataset = _dataset()
    cancelled = EvalRunResultSet(
        run_id="run-cancelled",
        profile_id="agentic_graphrag",
        config=_config(dataset.dataset_hash),
        case_results=(
            CaseExecutionResult(
                case_id="case-1",
                status=EvalRunStatus.CANCELLED,
                attempt=1,
                lease_ref="lease:cancelled",
                checkpoint_ref="checkpoint:cancelled",
                metric_results=(),
                failure_buckets=("cancelled",),
            ),
        ),
        efficiency=_efficiency(),
    )
    gate = evaluate_release_gate(
        gate_id="gate:cancelled",
        result_set=cancelled,
        thresholds={"CONTEXT_RECALL": 0.9},
        critical_slices=set(),
        comparison=None,
        evidence_artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
        evidence_artifact_hash=_hash("artifact"),
    )

    assert gate.status == ReleaseGateStatus.BLOCKED
    assert gate.reason == "result_set_not_fully_measured"


def test_phase20_dataset_or_model_mismatch_stays_incomparable_and_gate_replay_hash_is_stable() -> None:
    dataset = _dataset()
    baseline = EvalRunResultSet(
        run_id="run-baseline",
        profile_id="agentic_graphrag",
        config=_config(dataset.dataset_hash),
        case_results=(_measured_case(),),
        efficiency=_efficiency(),
    )
    candidate = EvalRunResultSet(
        run_id="run-candidate",
        profile_id="agentic_graphrag",
        config=_config(dataset.dataset_hash, model_profile="model-b"),
        case_results=(_measured_case(),),
        efficiency=_efficiency(),
    )
    comparison = compare_benchmark_runs(baseline, candidate)
    first = evaluate_release_gate(
        gate_id="gate:replay",
        result_set=candidate,
        thresholds={"CONTEXT_RECALL": 0.9},
        critical_slices=set(),
        comparison=comparison,
        evidence_artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
        evidence_artifact_hash=_hash("artifact"),
    )
    replay = evaluate_release_gate(
        gate_id="gate:replay",
        result_set=candidate,
        thresholds={"CONTEXT_RECALL": 0.9},
        critical_slices=set(),
        comparison=comparison,
        evidence_artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
        evidence_artifact_hash=_hash("artifact"),
    )

    assert comparison.status == ReleaseGateStatus.INCOMPARABLE
    assert first.status == ReleaseGateStatus.INCOMPARABLE
    assert replay.gate_hash == first.gate_hash
    assert replay.evidence_hash == first.evidence_hash
