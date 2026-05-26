import json
import tempfile
import asyncio
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]):
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_rag_eval_metrics_compute_retrieval_and_citation_scores():
    from agentchat.evals.rag_eval.metrics import compute_metrics

    local_tmp_root = Path.cwd() / ".test-tmp"
    local_tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=local_tmp_root) as tmp_name:
        tmp_path = Path(tmp_name)
        dataset = tmp_path / "dataset.jsonl"
        retrieval = tmp_path / "retrieval.jsonl"
        answers = tmp_path / "answers.jsonl"
        judges = tmp_path / "judges.jsonl"

        _write_jsonl(
            dataset,
            [
                {
                    "id": "q1",
                    "query": "Python 关键字是什么？",
                    "gold_evidence": [
                        {"file_contains": "Python 关键字.md", "text_contains": "关键字"},
                        {"file_contains": "Python 关键字.md", "text_contains": "标识符"},
                    ],
                    "required_citations": True,
                }
            ],
        )
        _write_jsonl(
            retrieval,
            [
                {
                    "id": "q1",
                    "contexts": [
                        {
                            "content": "Python 关键字是语法保留词，不能作为普通标识符。",
                            "source": "Python 关键字.md",
                        },
                        {
                            "content": "无关内容",
                            "source": "other.md",
                        },
                    ],
                }
            ],
        )
        _write_jsonl(
            answers,
            [
                {
                    "id": "q1",
                    "answer": "关键字不能作为变量名。",
                    "citations": [
                        {
                            "content": "Python 关键字是语法保留词，不能作为普通标识符。",
                            "source": "Python 关键字.md",
                        }
                    ],
                }
            ],
        )
        _write_jsonl(judges, [{"id": "q1", "faithfulness": 1.0, "answer_correctness": 0.9}])

        metrics = compute_metrics(
            dataset_path=dataset,
            retrieval_results_path=retrieval,
            answers_path=answers,
            judge_results_path=judges,
            k=2,
        )

        aggregate = metrics["aggregate"]
        assert aggregate["retrieval_recall_at_k"] == 1.0
        assert aggregate["context_precision_at_k"] == 0.5
        assert aggregate["faithfulness"] == 1.0
        assert aggregate["answer_correctness"] == 0.9
        assert aggregate["citation_accuracy"] == 1.0


def test_rag_eval_metrics_falls_back_to_text_match_when_source_metadata_missing():
    from agentchat.evals.rag_eval.metrics import compute_metrics

    local_tmp_root = Path.cwd() / ".test-tmp"
    local_tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=local_tmp_root) as tmp_name:
        tmp_path = Path(tmp_name)
        dataset = tmp_path / "dataset.jsonl"
        retrieval = tmp_path / "retrieval.jsonl"

        _write_jsonl(
            dataset,
            [
                {
                    "id": "q1",
                    "query": "Python 关键字是什么？",
                    "gold_evidence": [
                        {"file_contains": "Python 关键字.md", "text_contains": "语法保留"}
                    ],
                }
            ],
        )
        _write_jsonl(
            retrieval,
            [
                {
                    "id": "q1",
                    "contexts": [
                        {"content": "关键字是 Python 语法保留的单词，不能作为变量名。"}
                    ],
                }
            ],
        )

        metrics = compute_metrics(dataset_path=dataset, retrieval_results_path=retrieval, k=1)

        assert metrics["aggregate"]["retrieval_recall_at_k"] == 1.0
        assert metrics["aggregate"]["context_precision_at_k"] == 1.0


def test_prepare_python_notes_corpus_deduplicates_file_names():
    from agentchat.evals.rag_eval.prepare_python_notes_corpus import prepare_corpus

    local_tmp_root = Path.cwd() / ".test-tmp"
    local_tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=local_tmp_root) as tmp_name:
        tmp_path = Path(tmp_name)
        source = tmp_path / "source"
        (source / "a").mkdir(parents=True)
        (source / "b").mkdir(parents=True)
        (source / "a" / "collections.md").write_text("first", encoding="utf-8")
        (source / "b" / "collections.md").write_text("duplicate", encoding="utf-8")
        (source / "b" / "contextlib.md").write_text("second", encoding="utf-8")

        manifest = prepare_corpus(source, tmp_path / "out", limit_files=10)

        assert manifest["file_count"] == 2
        assert [item["file_name"] for item in manifest["files"]] == ["collections.md", "contextlib.md"]


def test_run_eval_writes_profile_outputs(monkeypatch):
    from agentchat.evals.rag_eval import run_eval as run_eval_module

    calls = []

    async def fake_retrieve(query, collection_names, index_names=None, **kwargs):
        calls.append(kwargs)
        return {
            "first_mode": kwargs.get("retrieval_mode", "rag"),
            "final_mode": kwargs.get("retrieval_mode", "rag"),
            "round_count": 1,
            "rag_result": {
                "documents": [
                    {
                        "content": "Python 关键字是语法保留词，不能作为普通标识符。",
                        "source": "Python 关键字.md",
                        "score": 0.92,
                    }
                ]
            },
            "graph_result": {"paths": ["Python -> keyword"]},
            "metadata": {"rounds": []},
        }

    monkeypatch.setattr(
        run_eval_module.RagHandler,
        "retrieve_ranked_documents_with_metadata",
        staticmethod(fake_retrieve),
    )

    local_tmp_root = Path.cwd() / ".test-tmp"
    local_tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=local_tmp_root) as tmp_name:
        tmp_path = Path(tmp_name)
        dataset = tmp_path / "dataset.jsonl"
        _write_jsonl(
            dataset,
            [
                {
                    "id": "q1",
                    "query": "Python 关键字是什么？",
                    "reference_answer": "Python 关键字是语法保留词，不能作为普通标识符。",
                    "gold_evidence": [
                        {"file_contains": "Python 关键字.md", "text_contains": "关键字"}
                    ],
                    "required_citations": True,
                }
            ],
        )

        report = asyncio.run(
            run_eval_module.run_eval(
                dataset_path=dataset,
                knowledge_ids=["k_eval"],
                profiles=["baseline_rag", "rag_graph"],
                output_dir=tmp_path / "run",
                trace_langsmith=False,
            )
        )

        assert "baseline_rag" in report["profiles"]
        assert (tmp_path / "run" / "baseline_rag" / "metrics.json").exists()
        assert (tmp_path / "run" / "rag_graph" / "retrieval_results.jsonl").exists()
        assert (tmp_path / "run" / "report.md").exists()
        assert calls[0]["retrieval_mode"] == "rag"
        assert calls[0]["retrieval_options"]["rerank_enabled"] is False
        assert calls[-1]["retrieval_mode"] == "rag_graph"
        assert calls[-1]["retrieval_options"]["graph_hop_limit"] == 2
