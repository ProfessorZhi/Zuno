from pathlib import Path
import uuid
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api" / "src"))

from tools.evals.zuno.rag_eval.paths import default_runs_root


def test_stackless_compare_matrix_build_dataset_coverage_warns_on_tiny_slice():
    from tools.evals.zuno.rag_eval.run_stackless_compare_matrix import _build_dataset_coverage

    temp_dir = default_runs_root() / f"tmp-test-{uuid.uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    dataset = temp_dir / "dataset.jsonl"
    dataset.write_text(
        "\n".join(
            [
                '{"id":"q1","gold_evidence":[{"file_contains":"a.md"}]}',
                '{"id":"q2","gold_evidence":[{"file_contains":"b.md"}]}',
                '{"id":"q3","gold_evidence":[{"file_contains":"a.md"}]}',
            ]
        ),
        encoding="utf-8",
    )

    coverage = _build_dataset_coverage(dataset_path=dataset, sample_limit=3)
    assert coverage["sampled_question_count"] == 3
    assert coverage["unique_referenced_file_count"] == 2
    assert coverage["warning"] is not None


def test_stackless_compare_matrix_write_markdown():
    from tools.evals.zuno.rag_eval.run_stackless_compare_matrix import write_markdown

    summary = {
        "dataset_path": "dataset.jsonl",
        "manifest_path": "manifest.json",
        "sample_limit": 3,
        "coverage": {
            "sampled_question_count": 3,
            "unique_referenced_file_count": 2,
            "unique_referenced_files": ["a.md", "b.md"],
            "warning": "Low coverage: this matrix run touches too few sampled questions or referenced files to support a strong GraphRAG-vs-RAG conclusion.",
        },
        "runs": {
            "local_compare": {
                "output_root": "runs/local_compare",
                "profiles": ["baseline_rag", "rag_rerank", "rag_graph_chunk_backed"],
                "chunk_count": 2,
                "rerank_score_threshold_override": 0.0,
                "report": {
                    "profiles": {
                        "baseline_rag": {
                            "retrieval_recall_at_k": 0.5,
                            "hit_rate_at_k": 1.0,
                            "context_precision_at_k": 0.2,
                            "mrr_at_k": 0.8,
                            "ndcg_at_k": 0.7,
                            "faithfulness": 1.0,
                            "citation_accuracy": 0.5,
                        }
                    }
                },
            }
        },
        "slices": {
            "local_compare": {
                "profiles": {
                    "baseline_rag": {
                        "graph_relation": {
                            "sample_count": 2,
                            "retrieval_recall": 0.6,
                            "context_precision": 0.3,
                            "mrr": 0.7,
                            "ndcg": 0.65,
                            "citation_accuracy": 0.55,
                        }
                    }
                }
            }
        },
    }
    output_dir = default_runs_root() / f"tmp-test-{uuid.uuid4().hex}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "summary.md"
    write_markdown(output, summary)
    text = output.read_text(encoding="utf-8")
    assert "# Zuno Stackless Compare Matrix" in text
    assert "baseline_rag" in text
    assert "0.5000" in text
    assert "graph_relation" in text
    assert "0.6000" in text
    assert "Low coverage" in text
    assert "Chunk Count" in text


def test_stackless_compare_matrix_help_lists_threshold_args():
    target = Path("tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py")
    content = target.read_text(encoding="utf-8")
    assert "--local-compare-rerank-threshold-override" in content
    assert "--graph-compare-rerank-threshold-override" in content


def test_stackless_compare_matrix_build_acceptance():
    from tools.evals.zuno.rag_eval.run_stackless_compare_matrix import _build_acceptance

    acceptance = _build_acceptance(
        {
            "slices": {
                "local_compare": {
                    "profiles": {
                        "rag_rerank": {"graph_relation": {"retrieval_recall": 0.2, "mrr": 0.3}},
                        "rag_graph_chunk_backed": {"graph_relation": {"retrieval_recall": 0.4, "mrr": 0.5}},
                    }
                },
                "graph_compare": {
                    "profiles": {
                        "baseline_rag": {"graph_relation": {"retrieval_recall": 0.1, "mrr": 0.2, "citation_accuracy": 0.1}},
                        "rag_graph_chunk_backed": {
                            "graph_relation": {
                                "retrieval_recall": 0.4,
                                "mrr": 0.5,
                                "citation_accuracy": 0.2,
                                "context_precision": 0.15,
                            }
                        },
                        "rag_graph_chunk_backed_3hop": {
                            "graph_relation": {
                                "retrieval_recall": 0.45,
                                "mrr": 0.55,
                                "citation_accuracy": 0.2,
                                "context_precision": 0.15,
                            }
                        },
                    }
                },
            }
        }
    )

    assert acceptance["graph_relation_2hop_not_worse_than_baseline"]["passed"] is True
    assert acceptance["graph_relation_citation_not_lower_than_baseline"]["passed"] is True
    assert acceptance["three_hop_only_if_precision_not_hurt"]["passed"] is True
