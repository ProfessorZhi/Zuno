from __future__ import annotations

import pytest

from zuno.platform.contracts import canonical_sha256
from zuno.platform.observability.eval_runtime import (
    AgentEfficiencyVector,
    CaseExecutionResult,
    EvalCase,
    EvalDatasetVersion,
    EvalMeasurementStatus,
    EvalRunConfig,
    EvalRunResultSet,
    EvalRunStatus,
    EvalRuntimeError,
    GraphRAGDiagnosticTrace,
    RAGCoreFiveEvaluator,
    RAGCoreFiveInputBundle,
    ReleaseGateStatus,
    compare_benchmark_runs,
    evaluate_release_gate,
)


def _hash(name: str) -> str:
    return canonical_sha256({"fixture": name})


def _dataset() -> EvalDatasetVersion:
    return EvalDatasetVersion(
        dataset_id="goal05-phase20-core",
        version="v1",
        cases=(
            EvalCase(
                case_id="case-1",
                question="Which clause governs renewal?",
                reference_claim_refs=("claim-renewal",),
                gold_evidence_refs=("doc-1#clause-4",),
                slices=("multi-hop", "citation-required"),
                security_scope_ref="scope:tenant-a:workspace-a",
            ),
        ),
    )


def _config(dataset_hash: str, *, model_profile: str = "model-a") -> EvalRunConfig:
    return EvalRunConfig(
        dataset_hash=dataset_hash,
        corpus_snapshot_hash=_hash("corpus"),
        index_snapshot_hash=_hash("index"),
        model_profile_hash=_hash(model_profile),
        judge_policy_hash=_hash("judge-policy"),
        embedding_profile_hash=_hash("embedding"),
        metric_config_hash=_hash("metric-config"),
        runtime_profile_hash=_hash("runtime"),
        security_scope_hash=_hash("security-scope"),
    )


def _measured_case(case_id: str = "case-1", failure_buckets: tuple[str, ...] = ()) -> CaseExecutionResult:
    metrics = RAGCoreFiveEvaluator().evaluate(
        RAGCoreFiveInputBundle(
            case_id=case_id,
            retrieved_context_refs=("ctx-1", "ctx-2"),
            reference_claim_refs=("claim-renewal",),
            retrieved_context_supported_reference_claim_refs=("claim-renewal",),
            generated_claim_refs=("claim-renewal",),
            supported_generated_claim_refs=("claim-renewal",),
            true_positive_claim_refs=("claim-renewal",),
            false_positive_claim_refs=(),
            false_negative_claim_refs=(),
            answer_relevant=True,
        )
    )
    return CaseExecutionResult(
        case_id=case_id,
        status=EvalRunStatus.COMPLETED,
        attempt=1,
        lease_ref=f"lease:{case_id}",
        checkpoint_ref=f"checkpoint:{case_id}",
        metric_results=metrics,
        failure_buckets=failure_buckets,
    )


def _result_set(run_id: str, config: EvalRunConfig, *, failure_buckets: tuple[str, ...] = ()) -> EvalRunResultSet:
    return EvalRunResultSet(
        run_id=run_id,
        profile_id="agentic_graphrag",
        config=config,
        case_results=(_measured_case(failure_buckets=failure_buckets),),
        efficiency=AgentEfficiencyVector(
            plan_steps=3,
            retry_count=0,
            replan_count=0,
            reflection_count=1,
            tool_call_count=1,
            model_call_count=2,
            retrieval_call_count=2,
            wall_time_ms=1200,
            active_time_ms=900,
            queue_wait_ms=50,
            critical_path_ms=700,
            parallel_branch_time_sum_ms=1000,
            token_total=1200,
            estimated_cost=0.12,
            settled_cost=0.12,
            evidence_yield=1.0,
        ),
    )


def test_phase20_eval_dataset_hash_is_immutable_and_scope_checked() -> None:
    dataset = _dataset()
    same = _dataset()
    assert dataset.dataset_hash == same.dataset_hash
    assert len(dataset.case_hashes) == 1
    dataset.require_scope({"scope:tenant-a:workspace-a"})
    with pytest.raises(EvalRuntimeError, match="unauthorized"):
        dataset.require_scope({"scope:other"})
    with pytest.raises(EvalRuntimeError, match="duplicate"):
        EvalDatasetVersion(dataset_id="dup", version="v1", cases=(dataset.cases[0], dataset.cases[0]))


def test_phase20_core_five_metrics_do_not_turn_missing_inputs_into_zero_passes() -> None:
    evaluator = RAGCoreFiveEvaluator()
    blocked = evaluator.evaluate(
        RAGCoreFiveInputBundle(
            case_id="blocked",
            retrieved_context_refs=("ctx-1",),
            reference_claim_refs=(),
            retrieved_context_supported_reference_claim_refs=(),
            generated_claim_refs=("claim-a",),
            supported_generated_claim_refs=(),
            true_positive_claim_refs=(),
            false_positive_claim_refs=(),
            false_negative_claim_refs=("claim-a",),
            answer_relevant=True,
        )
    )
    invalid = evaluator.evaluate(
        RAGCoreFiveInputBundle(
            case_id="invalid",
            retrieved_context_refs=("ctx-1",),
            reference_claim_refs=("claim-a",),
            retrieved_context_supported_reference_claim_refs=("claim-a",),
            generated_claim_refs=("claim-a",),
            supported_generated_claim_refs=("claim-a",),
            true_positive_claim_refs=("claim-a",),
            false_positive_claim_refs=(),
            false_negative_claim_refs=(),
            answer_relevant=True,
            judge_output_valid=False,
        )
    )
    measured = _measured_case().metric_results
    assert {result.status for result in blocked} == {EvalMeasurementStatus.BLOCKED}
    assert {result.status for result in invalid} == {EvalMeasurementStatus.INVALID}
    assert {result.metric_name for result in measured} == {
        "CONTEXT_PRECISION",
        "CONTEXT_RECALL",
        "FAITHFULNESS",
        "ANSWER_RELEVANCY",
        "ANSWER_CORRECTNESS",
    }
    assert all(result.status == EvalMeasurementStatus.MEASURED for result in measured)


def test_phase20_graphrag_diagnostics_identify_evidence_loss_stage() -> None:
    trace = GraphRAGDiagnosticTrace(
        case_id="case-1",
        route_profile="agentic_graphrag",
        retrieval_round=1,
        entity_refs=(),
        relation_refs=("relation-1",),
        path_refs=("path-1",),
        community_refs=("community-1",),
        fusion_kept_evidence_refs=("wrong-doc",),
        rerank_top_evidence_refs=("wrong-doc",),
        source_grounding_refs=(),
        gold_evidence_refs=("doc-1#clause-4",),
    )
    assert trace.failure_buckets() == (
        "entity_resolution_miss",
        "fusion_dropped_gold_evidence",
        "rerank_demoted_gold_evidence",
        "graph_source_grounding_miss",
    )


def test_phase20_benchmark_comparison_blocks_incomparable_or_partial_runs() -> None:
    dataset = _dataset()
    baseline = _result_set("run-baseline", _config(dataset.dataset_hash))
    mismatch = _result_set("run-mismatch", _config(dataset.dataset_hash, model_profile="model-b"))
    partial = EvalRunResultSet(
        run_id="run-partial",
        profile_id="agentic_graphrag",
        config=baseline.config,
        case_results=(
            CaseExecutionResult(
                case_id="case-1",
                status=EvalRunStatus.PARTIAL,
                attempt=1,
                lease_ref="lease:partial",
                checkpoint_ref="checkpoint:partial",
                metric_results=baseline.case_results[0].metric_results,
                failure_buckets=(),
            ),
        ),
    )
    assert compare_benchmark_runs(baseline, mismatch).status == ReleaseGateStatus.INCOMPARABLE
    assert compare_benchmark_runs(baseline, partial).status == ReleaseGateStatus.BLOCKED
    assert compare_benchmark_runs(baseline, _result_set("run-candidate", baseline.config)).comparable is True


def test_phase20_release_gate_requires_measured_results_comparability_and_settled_cost() -> None:
    dataset = _dataset()
    baseline = _result_set("run-baseline", _config(dataset.dataset_hash))
    candidate = _result_set("run-candidate", baseline.config)
    comparison = compare_benchmark_runs(baseline, candidate)
    passed = evaluate_release_gate(
        gate_id="gate:phase20",
        result_set=candidate,
        thresholds={metric: 0.9 for metric in ("CONTEXT_RECALL", "FAITHFULNESS", "ANSWER_CORRECTNESS")},
        critical_slices={"fusion_dropped_gold_evidence"},
        comparison=comparison,
        evidence_artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
        evidence_artifact_hash=_hash("artifact"),
    )
    regression = evaluate_release_gate(
        gate_id="gate:phase20-regression",
        result_set=_result_set("run-regression", baseline.config, failure_buckets=("fusion_dropped_gold_evidence",)),
        thresholds={metric: 0.9 for metric in ("CONTEXT_RECALL", "FAITHFULNESS", "ANSWER_CORRECTNESS")},
        critical_slices={"fusion_dropped_gold_evidence"},
        comparison=comparison,
        evidence_artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
        evidence_artifact_hash=_hash("artifact"),
    )
    unsettled = EvalRunResultSet(
        run_id="run-unsettled",
        profile_id="agentic_graphrag",
        config=baseline.config,
        case_results=(_measured_case(),),
        efficiency=AgentEfficiencyVector(
            plan_steps=1,
            retry_count=0,
            replan_count=0,
            reflection_count=0,
            tool_call_count=0,
            model_call_count=1,
            retrieval_call_count=1,
            wall_time_ms=100,
            active_time_ms=100,
            queue_wait_ms=0,
            critical_path_ms=100,
            parallel_branch_time_sum_ms=100,
            token_total=10,
            estimated_cost=0.01,
            settled_cost=None,
            evidence_yield=1.0,
        ),
    )
    blocked = evaluate_release_gate(
        gate_id="gate:phase20-blocked",
        result_set=unsettled,
        thresholds={"CONTEXT_RECALL": 0.9},
        critical_slices=set(),
        comparison=None,
        evidence_artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
        evidence_artifact_hash=_hash("artifact"),
    )
    assert passed.status == ReleaseGateStatus.PASSED
    assert passed.result_set_hash == candidate.result_set_hash
    assert passed.evidence_hash
    assert regression.status == ReleaseGateStatus.FAILED
    assert regression.reason == "critical_slice_regression:fusion_dropped_gold_evidence"
    assert blocked.status == ReleaseGateStatus.BLOCKED
    assert blocked.reason == "settled_cost_missing"
