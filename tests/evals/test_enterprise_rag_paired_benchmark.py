from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_questions(path: Path) -> None:
    rows = [
        {
            "question_id": "qst_basic",
            "question_type": "basic",
            "source_types": ["github"],
            "question": "What are the multipart upload limits?",
            "expected_doc_ids": ["dsid_upload_limits"],
            "gold_answer": "The limits are 10 MiB per file and 50 MiB total.",
            "answer_facts": [
                "The default per file upload size limit is 10 MiB.",
                "The default total request size limit is 50 MiB.",
            ],
        },
        {
            "question_id": "qst_conflict",
            "question_type": "conflicting_info",
            "source_types": ["confluence"],
            "question": "Which rollout checklist is current?",
            "expected_doc_ids": ["dsid_rollout_current"],
            "gold_answer": "The current rollout checklist is console-2026.04.",
            "answer_facts": ["The current rollout checklist is console-2026.04."],
        },
    ]
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _write_documents(path: Path) -> None:
    pq.write_table(
        pa.table(
            {
                "doc_id": ["dsid_upload_limits", "dsid_rollout_current", "dsid_negative_noise"],
                "source_type": ["github", "confluence", "slack"],
                "title": ["Multipart upload support", "Current rollout checklist", "Unrelated launch chatter"],
                "content": [
                    "The default per file upload size limit is 10 MiB. The default total request size limit is 50 MiB.",
                    "The current rollout checklist is console-2026.04.",
                    "This unrelated Slack thread mentions launch snacks and should be a hard negative.",
                ],
            }
        ),
        path,
    )


def test_enterprise_rag_paired_benchmark_blocks_without_documents(tmp_path: Path) -> None:
    from zuno.evals.rag_eval.run_enterprise_rag_paired_benchmark import (
        run_enterprise_rag_paired_benchmark,
    )

    questions = tmp_path / "questions.jsonl"
    _write_questions(questions)
    output_root = tmp_path / "run"

    result = asyncio.run(
        run_enterprise_rag_paired_benchmark(
            questions_file=questions,
            output_root=output_root,
            sample_size=2,
            allow_blocked=True,
            run_profiles=False,
        )
    )

    assert result["status"] == "blocked"
    assert result["metrics_source"] == "blocked_not_measured"

    metrics = _read_json(output_root / "metrics.json")
    assert metrics["status"] == "blocked"
    assert metrics["measurement_status"] == "blocked_not_measured"
    assert metrics["case_set"]["selected_case_count"] == 2
    assert metrics["case_set"]["measured_case_count"] == 0
    assert metrics["corpus"]["external_documents_required"] is True
    assert metrics["corpus"]["blocked_reason"] == "enterprise_rag_bench_documents_required"

    report = (output_root / "report.md").read_text(encoding="utf-8")
    assert "blocked_not_measured" in report
    assert "enterprise_rag_bench_documents_required" in report


def test_enterprise_rag_paired_benchmark_runs_same_cases_with_deltas_and_negatives(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from zuno.evals.rag_eval import run_enterprise_rag_paired_benchmark as paired

    questions = tmp_path / "questions.jsonl"
    documents = tmp_path / "documents.parquet"
    _write_questions(questions)
    _write_documents(documents)
    output_root = tmp_path / "run"

    async def fake_run_stackless_local_eval(**kwargs):
        assert kwargs["profile_set"] == "deep_graphrag_compare"
        assert kwargs["sample_limit"] == 2
        run_root = Path(kwargs["output_root"])
        run_root.mkdir(parents=True, exist_ok=True)
        profiles = {
            "baseline_rag": {
                "retrieval_recall_at_k": 0.5,
                "context_precision_at_k": 0.25,
                "mrr_at_k": 0.5,
                "ndcg_at_k": 0.5,
                "answer_correctness": 0.4,
                "citation_accuracy": 0.5,
            },
            "local_graphrag": {
                "retrieval_recall_at_k": 0.75,
                "context_precision_at_k": 0.3,
                "mrr_at_k": 0.6,
                "ndcg_at_k": 0.65,
                "answer_correctness": 0.55,
                "citation_accuracy": 0.6,
            },
            "deep_graphrag": {
                "retrieval_recall_at_k": 1.0,
                "context_precision_at_k": 0.35,
                "mrr_at_k": 0.8,
                "ndcg_at_k": 0.9,
                "answer_correctness": 0.7,
                "citation_accuracy": 0.8,
            },
        }
        for profile, aggregate in profiles.items():
            profile_dir = run_root / profile
            profile_dir.mkdir()
            per_sample = [
                {
                    "id": "qst_basic",
                    "retrieval_recall": aggregate["retrieval_recall_at_k"],
                    "context_precision": aggregate["context_precision_at_k"],
                    "mrr": aggregate["mrr_at_k"],
                    "ndcg": aggregate["ndcg_at_k"],
                    "answer_correctness": aggregate["answer_correctness"],
                    "citation_accuracy": aggregate["citation_accuracy"],
                    "unsupported_claim_rate": 0.0,
                },
                {
                    "id": "qst_conflict",
                    "retrieval_recall": 0.0 if profile == "baseline_rag" else 1.0,
                    "context_precision": aggregate["context_precision_at_k"],
                    "mrr": aggregate["mrr_at_k"],
                    "ndcg": aggregate["ndcg_at_k"],
                    "answer_correctness": aggregate["answer_correctness"],
                    "citation_accuracy": aggregate["citation_accuracy"],
                    "unsupported_claim_rate": 0.25 if profile == "baseline_rag" else 0.0,
                },
            ]
            (profile_dir / "metrics.json").write_text(
                json.dumps({"aggregate": aggregate, "per_sample": per_sample}, ensure_ascii=False),
                encoding="utf-8",
            )
            retrieval_rows = [
                {
                    "id": "qst_basic",
                    "contexts": [{"file_name": "dsid_upload_limits.md", "content": "10 MiB"}],
                    "metadata": {"latency_ms": 10 if profile == "baseline_rag" else 18, "cost_usd": 0.001},
                    "raw_result": {"final_mode": "rag_graph_deep" if "graph" in profile else "rag"},
                },
                {
                    "id": "qst_conflict",
                    "contexts": [{"kind": "graph_path", "content": "rollout -> console-2026.04"}]
                    if profile == "deep_graphrag"
                    else [],
                    "metadata": {"latency_ms": 12 if profile == "baseline_rag" else 24, "cost_usd": 0.002},
                    "raw_result": {"final_mode": "rag_graph_deep" if "graph" in profile else "rag"},
                },
            ]
            (profile_dir / "retrieval_results.jsonl").write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in retrieval_rows) + "\n",
                encoding="utf-8",
            )
        return {
            "chunk_count": 3,
            "profiles": list(profiles),
            "output_root": str(run_root),
            "report": {"profiles": profiles},
        }

    monkeypatch.setattr(paired, "run_stackless_local_eval", fake_run_stackless_local_eval)

    result = asyncio.run(
        paired.run_enterprise_rag_paired_benchmark(
            questions_file=questions,
            documents_file=documents,
            output_root=output_root,
            sample_size=2,
            hard_negative_count=1,
            allow_blocked=True,
        )
    )

    assert result["status"] == "measured"

    corpus_manifest = _read_json(output_root / "corpus_manifest.json")
    assert corpus_manifest["file_count"] == 3
    assert corpus_manifest["hard_negative_count"] == 1

    metrics = _read_json(output_root / "metrics.json")
    assert metrics["case_set"]["common_case_ids"] == ["qst_basic", "qst_conflict"]
    assert metrics["profiles"]["standard_rag"]["underlying_profile"] == "baseline_rag"
    assert metrics["profiles"]["deep_graphrag"]["underlying_profile"] == "deep_graphrag"
    assert metrics["profiles"]["agentic_graphrag"]["measured"] is False
    assert metrics["profiles"]["agentic_graphrag"]["blocked_reason"] == "agentic_runtime_runner_not_wired"
    assert metrics["deltas"]["deep_vs_standard"]["retrieval_recall_at_k"] == 0.5
    assert metrics["deltas"]["deep_vs_standard"]["answer_correctness"] == 0.3
    assert metrics["agentic_metrics"]["graph_usage_gain"] == 0.5
    assert metrics["agentic_metrics"]["replan_success_rate"] is None
    assert metrics["cost_latency"]["deep_graphrag"]["latency_p95_ms"] == 24

    failure_text = (output_root / "failure_cases.md").read_text(encoding="utf-8")
    assert "retrieval_miss" in failure_text
    assert "unsupported_claim" in failure_text
