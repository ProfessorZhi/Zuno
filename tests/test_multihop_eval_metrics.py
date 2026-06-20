import math
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_question_metrics_use_fixed_precision_denominator_and_mrr():
    from tools.evals.zuno.multihop_eval.metrics import compute_question_metrics

    metrics = compute_question_metrics(
        question_id="q1",
        gold_doc_ids=["doc-a", "doc-b"],
        retrieved_doc_ids=["doc-x", "doc-a", "doc-a", "doc-b"],
        latency_ms=120.0,
    )

    assert metrics["gold_count"] == 2
    assert metrics["retrieved_count"] == 3
    assert metrics["hits_at_2"] == 1
    assert metrics["hits_at_5"] == 2
    assert math.isclose(metrics["recall_at_2"], 0.5)
    assert math.isclose(metrics["recall_at_5"], 1.0)
    assert math.isclose(metrics["precision_at_5"], 0.4)
    assert math.isclose(metrics["precision_at_10"], 0.2)
    assert math.isclose(metrics["mrr_at_10"], 0.5)


def test_question_metrics_expose_chain_and_full_chain_fields():
    from tools.evals.zuno.multihop_eval.metrics import compute_question_metrics

    partial = compute_question_metrics(
        question_id="q-partial",
        gold_doc_ids=["doc-a", "doc-b", "doc-c"],
        retrieved_doc_ids=["doc-a", "doc-z", "doc-y", "doc-x", "doc-b"],
    )
    full = compute_question_metrics(
        question_id="q-full",
        gold_doc_ids=["doc-a", "doc-b"],
        retrieved_doc_ids=["doc-x", "doc-a", "doc-b"],
    )

    assert math.isclose(partial["chain_recall_at_5"], 2 / 3)
    assert partial["full_chain_hit_at_5"] == 0.0
    assert full["full_chain_hit_at_5"] == 1.0
    assert full["full_chain_hit_at_10"] == 1.0


def test_aggregate_metrics_exclude_invalid_gold_but_keep_runtime_health_counts():
    from tools.evals.zuno.multihop_eval.metrics import aggregate_question_metrics, compute_question_metrics

    valid = compute_question_metrics(
        question_id="q-valid",
        gold_doc_ids=["doc-a", "doc-b"],
        retrieved_doc_ids=["doc-a"],
        latency_ms=100.0,
    )
    failure = compute_question_metrics(
        question_id="q-failure",
        gold_doc_ids=["doc-c"],
        retrieved_doc_ids=[],
        latency_ms=400.0,
        fallback=True,
        failure=True,
    )
    invalid = compute_question_metrics(
        question_id="q-invalid",
        gold_doc_ids=[],
        retrieved_doc_ids=["noise"],
        latency_ms=200.0,
    )

    aggregate = aggregate_question_metrics([valid, failure, invalid])

    assert aggregate["question_count"] == 3
    assert aggregate["valid_question_count"] == 2
    assert math.isclose(aggregate["Recall@5"], 0.25)
    assert math.isclose(aggregate["Precision@5"], 0.1)
    assert math.isclose(aggregate["MRR@10"], 0.5)
    assert aggregate["failure_count"] == 1
    assert math.isclose(aggregate["failure_rate"], 1 / 3)
    assert aggregate["fallback_count"] == 1
    assert math.isclose(aggregate["fallback_rate"], 1 / 3)
    assert aggregate["empty_result_count"] == 1


def test_aggregate_metrics_report_latency_percentiles():
    from tools.evals.zuno.multihop_eval.metrics import aggregate_question_metrics, compute_question_metrics

    rows = [
        compute_question_metrics(question_id="q1", gold_doc_ids=["a"], retrieved_doc_ids=["a"], latency_ms=100.0),
        compute_question_metrics(question_id="q2", gold_doc_ids=["a"], retrieved_doc_ids=["a"], latency_ms=200.0),
        compute_question_metrics(question_id="q3", gold_doc_ids=["a"], retrieved_doc_ids=["a"], latency_ms=300.0),
        compute_question_metrics(question_id="q4", gold_doc_ids=["a"], retrieved_doc_ids=["a"], latency_ms=400.0),
        compute_question_metrics(question_id="q5", gold_doc_ids=["a"], retrieved_doc_ids=["a"], latency_ms=500.0),
    ]

    aggregate = aggregate_question_metrics(rows)

    assert math.isclose(aggregate["avg_latency_ms"], 300.0)
    assert math.isclose(aggregate["p50_latency_ms"], 300.0)
    assert math.isclose(aggregate["p95_latency_ms"], 480.0)
