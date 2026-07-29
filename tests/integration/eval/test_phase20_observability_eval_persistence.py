from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.observability.eval_runtime import (
    AgentEfficiencyVector,
    CaseExecutionResult,
    EvalCase,
    EvalDatasetVersion,
    EvalRunConfig,
    EvalRunResultSet,
    EvalRunStatus,
    EvidenceRecord,
    GraphRAGDiagnosticTrace,
    PostgresEvalRuntimeRepository,
    RAGCoreFiveEvaluator,
    RAGCoreFiveInputBundle,
    ReleaseGateStatus,
    compare_benchmark_runs,
    evaluate_release_gate,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)


def _hash(name: str) -> str:
    return canonical_sha256({"phase20": name})


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    observability_release_gate_evaluations,
                    observability_evidence_records,
                    observability_benchmark_comparisons,
                    observability_failure_buckets,
                    observability_agent_efficiency_snapshots,
                    observability_graphrag_diagnostics,
                    observability_eval_metric_results,
                    observability_eval_case_executions,
                    observability_eval_runs,
                    observability_eval_cases,
                    observability_eval_datasets
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def test_phase20_eval_runtime_persists_dataset_run_metrics_comparison_gate_and_evidence(engine) -> None:
    dataset = EvalDatasetVersion(
        dataset_id="phase20-integration",
        version="v1",
        cases=(
            EvalCase(
                case_id="case-integration",
                question="Which source supports renewal?",
                reference_claim_refs=("claim-renewal",),
                gold_evidence_refs=("doc-1#renewal",),
                slices=("citation-required",),
                security_scope_ref="scope:tenant-a:workspace-a",
            ),
        ),
    )
    config = EvalRunConfig(
        dataset_hash=dataset.dataset_hash,
        corpus_snapshot_hash=_hash("corpus"),
        index_snapshot_hash=_hash("index"),
        model_profile_hash=_hash("model"),
        judge_policy_hash=_hash("judge"),
        embedding_profile_hash=_hash("embedding"),
        metric_config_hash=_hash("metric"),
        runtime_profile_hash=_hash("runtime"),
        security_scope_hash=_hash("security"),
    )
    metrics = RAGCoreFiveEvaluator().evaluate(
        RAGCoreFiveInputBundle(
            case_id="case-integration",
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
    )
    case_result = CaseExecutionResult(
        case_id="case-integration",
        status=EvalRunStatus.COMPLETED,
        attempt=1,
        lease_ref="lease:phase20:case",
        checkpoint_ref="checkpoint:phase20:case",
        metric_results=metrics,
        failure_buckets=(),
    )
    efficiency = AgentEfficiencyVector(
        plan_steps=2,
        retry_count=0,
        replan_count=0,
        reflection_count=0,
        tool_call_count=0,
        model_call_count=1,
        retrieval_call_count=1,
        wall_time_ms=1000,
        active_time_ms=800,
        queue_wait_ms=10,
        critical_path_ms=600,
        parallel_branch_time_sum_ms=800,
        token_total=900,
        estimated_cost=0.09,
        settled_cost=0.09,
        evidence_yield=1.0,
    )
    baseline = EvalRunResultSet(
        run_id="run-phase20-baseline",
        profile_id="agentic_graphrag",
        config=config,
        case_results=(case_result,),
        efficiency=efficiency,
    )
    candidate = EvalRunResultSet(
        run_id="run-phase20-candidate",
        profile_id="agentic_graphrag",
        config=config,
        case_results=(case_result,),
        efficiency=efficiency,
    )
    comparison = compare_benchmark_runs(baseline, candidate)
    gate = evaluate_release_gate(
        gate_id="gate:phase20:integration",
        result_set=candidate,
        thresholds={"CONTEXT_RECALL": 0.9, "FAITHFULNESS": 0.9, "ANSWER_CORRECTNESS": 0.9},
        critical_slices=set(),
        comparison=comparison,
        evidence_artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
        evidence_artifact_hash=_hash("evidence-artifact"),
    )
    evidence = EvidenceRecord(
        evidence_id="evidence:gate:phase20:integration",
        artifact_ref="docs/evidence/goal05-phase20-eval-runtime.md",
        artifact_hash=_hash("evidence-artifact"),
        result_set_hash=gate.result_set_hash,
        gate_hash=gate.gate_hash,
    )
    repo = PostgresEvalRuntimeRepository(engine)
    repo.record_dataset(dataset)
    for run_id in (baseline.run_id, candidate.run_id):
        repo.start_run(run_id=run_id, profile_id="agentic_graphrag", config=config)
        repo.record_case_execution(run_id=run_id, case_hash=dataset.cases[0].case_hash, result=case_result)
        repo.record_efficiency(run_id=run_id, efficiency=efficiency)
    repo.record_graph_diagnostic(
        run_id=candidate.run_id,
        diagnostic=GraphRAGDiagnosticTrace(
            case_id="case-integration",
            route_profile="agentic_graphrag",
            retrieval_round=1,
            entity_refs=("entity-renewal",),
            relation_refs=("relation-governs",),
            path_refs=("path-renewal",),
            community_refs=("community-contract",),
            fusion_kept_evidence_refs=("doc-1#renewal",),
            rerank_top_evidence_refs=("doc-1#renewal",),
            source_grounding_refs=("doc-1#renewal",),
            gold_evidence_refs=("doc-1#renewal",),
        ),
    )
    repo.complete_run(baseline)
    repo.complete_run(candidate)
    repo.record_comparison(comparison)
    repo.record_release_gate(gate, evidence)

    assert gate.status == ReleaseGateStatus.PASSED
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM observability_eval_datasets")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_eval_cases")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_eval_runs")).scalar_one() == 2
        assert conn.execute(text("SELECT count(*) FROM observability_eval_case_executions")).scalar_one() == 2
        assert conn.execute(text("SELECT count(*) FROM observability_eval_metric_results")).scalar_one() == 10
        assert conn.execute(text("SELECT count(*) FROM observability_graphrag_diagnostics")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_agent_efficiency_snapshots")).scalar_one() == 2
        assert conn.execute(text("SELECT count(*) FROM observability_benchmark_comparisons")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM observability_evidence_records")).scalar_one() == 1
        stored_gate = conn.execute(
            text("SELECT status, reason, result_set_hash, evidence_hash FROM observability_release_gate_evaluations")
        ).one()
        assert stored_gate.status == "PASSED"
        assert stored_gate.reason == "passed"
        assert stored_gate.result_set_hash == candidate.result_set_hash
        assert stored_gate.evidence_hash == evidence.evidence_hash
