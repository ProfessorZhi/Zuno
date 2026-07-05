import json
import tempfile
import asyncio
from types import SimpleNamespace
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]):
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_rag_eval_metrics_compute_retrieval_and_citation_scores():
    from zuno.evals.rag_eval.metrics import compute_metrics

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
        assert aggregate["source_doc_citation_accuracy"] == 1.0
        assert aggregate["evidence_text_available_at_k"] == 1.0
        assert metrics["per_sample"][0]["evidence_text_available"] == 1.0


def test_rag_eval_metrics_falls_back_to_text_match_when_source_metadata_missing():
    from zuno.evals.rag_eval.metrics import compute_metrics

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


def test_rag_eval_metrics_counts_enterprise_doc_id_hits_for_retrieval_only():
    from zuno.evals.rag_eval.metrics import compute_metrics

    local_tmp_root = Path.cwd() / ".test-tmp"
    local_tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=local_tmp_root) as tmp_name:
        tmp_path = Path(tmp_name)
        dataset = tmp_path / "dataset.jsonl"
        retrieval = tmp_path / "retrieval.jsonl"
        answers = tmp_path / "answers.jsonl"

        _write_jsonl(
            dataset,
            [
                {
                    "id": "enterprise_q1",
                    "query": "When does booking open?",
                    "gold_evidence": [
                        {
                            "doc_id": "dsid_45e2",
                            "file_contains": "dsid_45e2.md",
                            "text_contains": "Booking opens Monday at 09:00 UTC.",
                        }
                    ],
                    "required_citations": True,
                }
            ],
        )
        _write_jsonl(
            retrieval,
            [
                {
                    "id": "enterprise_q1",
                    "contexts": [
                        {
                            "file_name": "dsid_45e2.md",
                            "content": "Reservations open Mon 2026-04-06 09:00 UTC.",
                        }
                    ],
                }
            ],
        )
        _write_jsonl(
            answers,
            [
                {
                    "id": "enterprise_q1",
                    "answer": "Reservations open Monday at 09:00 UTC.",
                    "citations": [
                        {
                            "file_name": "dsid_45e2.md",
                            "content": "Reservations open Mon 2026-04-06 09:00 UTC.",
                        }
                    ],
                }
            ],
        )

        metrics = compute_metrics(
            dataset_path=dataset,
            retrieval_results_path=retrieval,
            answers_path=answers,
            k=1,
        )

        assert metrics["aggregate"]["retrieval_recall_at_k"] == 1.0
        assert metrics["aggregate"]["context_precision_at_k"] == 1.0
        assert metrics["aggregate"]["citation_accuracy"] == 0.0
        assert metrics["aggregate"]["source_doc_citation_accuracy"] == 1.0
        assert metrics["aggregate"]["evidence_text_available_at_k"] == 0.0
        assert metrics["per_sample"][0]["evidence_text_available"] == 0.0


def test_rag_eval_metrics_compute_source_span_and_unsupported_claim_rate():
    from zuno.evals.rag_eval.metrics import compute_metrics

    local_tmp_root = Path.cwd() / ".test-tmp"
    local_tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=local_tmp_root) as tmp_name:
        tmp_path = Path(tmp_name)
        dataset = tmp_path / "dataset.jsonl"
        retrieval = tmp_path / "retrieval.jsonl"
        answers = tmp_path / "answers.jsonl"

        _write_jsonl(
            dataset,
            [
                {
                    "id": "cfqa_1",
                    "query": "研发费用是多少？",
                    "gold_evidence": [
                        {
                            "file_contains": "600000_2023_annual_report.pdf",
                            "page_number": 42,
                            "text_contains": "研发费用",
                        }
                    ],
                    "required_citations": True,
                }
            ],
        )
        _write_jsonl(
            retrieval,
            [
                {
                    "id": "cfqa_1",
                    "contexts": [
                        {
                            "content": "研发费用为 1.23 亿元。",
                            "source": "600000_2023_annual_report.pdf",
                            "page_number": 42,
                        }
                    ],
                }
            ],
        )
        _write_jsonl(
            answers,
            [
                {
                    "id": "cfqa_1",
                    "answer": "研发费用为 1.23 亿元，另有一个未支持判断。",
                    "citations": [
                        {
                            "source": "600000_2023_annual_report.pdf",
                            "page_number": 42,
                            "content": "研发费用为 1.23 亿元。",
                        }
                    ],
                    "claim_count": 2,
                    "unsupported_claims": ["另有一个未支持判断"],
                }
            ],
        )

        metrics = compute_metrics(
            dataset_path=dataset,
            retrieval_results_path=retrieval,
            answers_path=answers,
            k=1,
        )

        aggregate = metrics["aggregate"]
        assert aggregate["citation_accuracy"] == 1.0
        assert aggregate["source_span_accuracy"] == 1.0
        assert aggregate["unsupported_claim_rate"] == 0.5


def test_prepare_python_notes_corpus_deduplicates_file_names():
    from zuno.evals.rag_eval.prepare_python_notes_corpus import prepare_corpus

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
    from zuno.evals.rag_eval import run_eval as run_eval_module

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


def test_run_eval_agentic_profile_fuses_standard_floor_with_deep_contexts(monkeypatch):
    from zuno.evals.rag_eval import run_eval as run_eval_module

    calls = []

    async def fake_retrieve(query, collection_names, index_names=None, **kwargs):
        calls.append(kwargs)
        if kwargs.get("retrieval_mode") == "rag":
            documents = [
                {
                    "content": "Floor evidence from document A.",
                    "file_name": "doc_a.md",
                    "chunk_id": "a1",
                    "score": 0.9,
                },
                {
                    "content": "Another floor chunk from document A.",
                    "file_name": "doc_a.md",
                    "chunk_id": "a2",
                    "score": 0.8,
                },
            ]
        else:
            documents = [
                {
                    "content": "Enhanced evidence from document B.",
                    "file_name": "doc_b.md",
                    "chunk_id": "b1",
                    "score": 0.7,
                }
            ]
        return {
            "first_mode": kwargs.get("retrieval_mode", "rag"),
            "final_mode": kwargs.get("retrieval_mode", "rag"),
            "round_count": 2 if kwargs.get("retrieval_mode") == "rag_graph_deep" else 1,
            "rag_result": {"documents": documents},
            "graph_result": {"documents": [], "paths": []},
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
                    "id": "q_agentic",
                    "query": "Compare document A and B.",
                    "reference_answer": "Document A and document B are both required.",
                    "gold_evidence": [
                        {"file_contains": "doc_a.md", "text_contains": "Floor evidence"},
                        {"file_contains": "doc_b.md", "text_contains": "Enhanced evidence"},
                    ],
                    "required_citations": True,
                }
            ],
        )

        report = asyncio.run(
            run_eval_module.run_eval(
                dataset_path=dataset,
                knowledge_ids=["k_eval"],
                profiles=["agentic_graphrag"],
                output_dir=tmp_path / "run",
                trace_langsmith=False,
            )
        )

        retrieval_rows = [
            json.loads(line)
            for line in (tmp_path / "run" / "agentic_graphrag" / "retrieval_results.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        contexts = retrieval_rows[0]["contexts"]

        assert [call["retrieval_mode"] for call in calls] == ["rag_graph_deep", "rag"]
        assert contexts[0]["file_name"] == "doc_a.md"
        assert contexts[1]["file_name"] == "doc_b.md"
        assert retrieval_rows[0]["metadata"]["agentic_floor_fusion"]["fused_context_count"] == 3
        assert report["profiles"]["agentic_graphrag"]["retrieval_recall_at_k"] == 1.0


def test_run_eval_supports_llm_answer_and_judge_modes(monkeypatch):
    from zuno.core.models import manager as model_manager
    from zuno.evals.rag_eval import run_eval as run_eval_module

    async def fake_retrieve(query, collection_names, index_names=None, **kwargs):
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
            "graph_result": {"paths": []},
            "metadata": {"rounds": []},
        }

    class FakeClient:
        def invoke(self, messages):
            human_content = str(messages[-1].content)
            if "output_schema" in human_content:
                return SimpleNamespace(
                    content='{"faithfulness": 0.8, "answer_correctness": 0.7, "rationale": "ok"}'
                )
            return SimpleNamespace(content="Python 关键字是语法保留词，不能作为变量名。[1]")

    monkeypatch.setattr(
        run_eval_module.RagHandler,
        "retrieve_ranked_documents_with_metadata",
        staticmethod(fake_retrieve),
    )
    monkeypatch.setattr(
        model_manager.ModelManager,
        "get_conversation_model",
        staticmethod(lambda: FakeClient()),
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
                        {"file_contains": "Python 关键字.md", "text_contains": "语法保留"}
                    ],
                    "required_citations": True,
                }
            ],
        )

        report = asyncio.run(
            run_eval_module.run_eval(
                dataset_path=dataset,
                knowledge_ids=["k_eval"],
                profiles=["baseline_rag"],
                output_dir=tmp_path / "run",
                answer_mode="llm",
                judge_mode="llm",
            )
        )

        metrics = report["profiles"]["baseline_rag"]
        assert report["answer_mode"] == "llm"
        assert report["judge_mode"] == "llm"
        assert metrics["faithfulness"] == 0.8
        assert metrics["answer_correctness"] == 0.7


def test_extract_contexts_uses_query_aware_priority_to_put_graph_evidence_first():
    from zuno.evals.rag_eval.run_eval import _extract_contexts

    contexts = _extract_contexts(
        {
            "rag_result": {
                "documents": [
                    {
                        "chunk_id": "rag_chunk_1",
                        "content": "General Agent Server overview.",
                        "file_name": "rag.md",
                        "score": 0.9,
                    }
                ]
            },
            "graph_result": {
                "documents": [
                    {
                        "chunk_id": "graph_chunk_1",
                        "content": "Persistence. Agent Server persists three types of data and stores them in PostgreSQL by default.",
                        "file_name": "graph.md",
                        "graph_seed_hit_count": 2,
                        "score": 0.0,
                    }
                ],
                "paths": ["ProjectAtlas -> Bob"],
            },
        },
        query="Agent Server 持久化哪三类数据？默认后端分别是什么？",
    )

    assert contexts[0]["content"].startswith("Persistence.")
    assert contexts[1]["content"] == "General Agent Server overview."
    assert contexts[2]["kind"] == "graph_path"


def test_extract_contexts_keeps_rag_first_when_graph_docs_are_query_noise():
    from zuno.evals.rag_eval.run_eval import _extract_contexts

    contexts = _extract_contexts(
        {
            "rag_result": {
                "documents": [
                    {
                        "chunk_id": "rag_chunk_1",
                        "content": "Runtime architecture > Run execution lifecycle. A client sends a request to an API server and the queue worker picks up the run.",
                        "file_name": "rag.md",
                        "score": 5.0,
                    }
                ]
            },
            "graph_result": {
                "documents": [
                    {
                        "chunk_id": "graph_chunk_1",
                        "content": "Example configuration for high reads and high writes > Autoscaling.",
                        "file_name": "graph.md",
                        "graph_seed_hit_count": 5,
                        "score": 0.0,
                    }
                ],
                "paths": [
                    "Milvus -> Limits",
                    "Milvus -> Naming",
                    "Milvus -> Length",
                    "Milvus -> AI",
                    "Milvus -> Cost",
                    "Milvus -> Feature",
                    "Milvus -> Scaling",
                    "Milvus -> Segment",
                    "Milvus -> Cluster",
                ],
            },
        },
        query="一次 Agent Server run 从 API server 到 queue worker 再到客户端流式返回的执行路径是什么？",
    )

    top_documents = contexts[:2]
    assert {item["file_name"] for item in top_documents} == {"rag.md", "graph.md"}
    assert any(
        item["content"].startswith("Runtime architecture > Run execution lifecycle")
        for item in top_documents
    )
    assert all(item.get("kind") != "graph_path" for item in top_documents)


def test_extract_contexts_does_not_promote_weak_compact_graph_docs_ahead_of_rag():
    from zuno.evals.rag_eval.run_eval import _extract_contexts

    contexts = _extract_contexts(
        {
            "rag_result": {
                "documents": [
                    {
                        "chunk_id": "rag_chunk_1",
                        "content": "Python namespace maps names to objects and assignment binds a name to an object.",
                        "file_name": "namespace.md",
                        "score": 5.0,
                    }
                ]
            },
            "graph_result": {
                "documents": [
                    {
                        "chunk_id": "graph_chunk_1",
                        "content": "Python -> Agent",
                        "file_name": "graph.md",
                        "graph_seed_hit_count": 1,
                        "graph_support_count": 1,
                        "score": 0.0,
                    },
                    {
                        "chunk_id": "graph_chunk_2",
                        "content": "Python -> Infra",
                        "file_name": "graph.md",
                        "graph_seed_hit_count": 1,
                        "graph_support_count": 1,
                        "score": 0.0,
                    },
                ],
                "paths": ["Python -> Agent", "Python -> Infra"],
            },
        },
        query="Python 閲屽彉閲忋€佸懡鍚嶇┖闂村拰瀵硅薄缁戝畾涔嬮棿鏄粈涔堝叧绯伙紵",
    )

    assert contexts[0]["content"].startswith("Python namespace maps names to objects")


def test_build_extractive_answer_prefers_relevant_clause_snippets():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_contract",
        "query": "数据处理附录终止后，乙方需要在多久内返还数据，并在多久内删除备份？",
    }
    contexts = [
        {
            "content": (
                "数据处理附录\n"
                "第四条 事件通知\n"
                "发生个人信息泄露时，乙方应在12小时内通知甲方。\n"
                "第五条 删除与返还\n"
                "合同终止时，乙方应在20个工作日内返还相关数据，并在30日内删除全部备份数据。\n"
                "第六条 法律依据\n"
                "双方应遵守个人信息保护法和数据安全法。"
            ),
            "file_name": "contract_006_data_processing_addendum.md",
        },
        {
            "content": (
                "主服务合同\n"
                "第五条 付款安排\n"
                "甲方应在收到发票后10个工作日内支付首期服务费。"
            ),
            "file_name": "contract_001_master_service_agreement.md",
        },
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "20个工作日内返还相关数据" in answer["answer"]
    assert "30日内删除全部备份数据" in answer["answer"]
    assert "10个工作日内支付首期服务费" not in answer["answer"]
    assert answer["citations"][0]["file_name"] == "contract_006_data_processing_addendum.md"


def test_build_extractive_answer_prefers_law_basis_snippet():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_law_basis",
        "query": "数据处理附录的履行需要遵守哪两部法律？",
    }
    contexts = [
        {
            "content": (
                "数据处理附录\n"
                "第五条 删除与返还\n"
                "合同终止时，乙方应在20个工作日内返还相关数据，并在30日内删除全部备份数据。\n"
                "第六条 法律依据\n"
                "双方确认本附件的履行应遵守《中华人民共和国个人信息保护法》《中华人民共和国数据安全法》。"
            ),
            "file_name": "contract_006_data_processing_addendum.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "个人信息保护法" in answer["answer"]
    assert "数据安全法" in answer["answer"]
    assert "20个工作日内返还相关数据" not in answer["answer"]


def test_build_extractive_answer_prefers_compact_limit_snippet_over_long_intro():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_upload_limits",
        "query": (
            "What are the default size limits for file uploads and total request size "
            "for the new multipart upload support on the OpenAI-compatible API endpoints?"
        ),
    }
    contexts = [
        {
            "content": (
                "add multipart/form-data handling, strict content-type validation, and payload limit enforcement "
                "for API tool/file inputs\n\n"
                "description:\n"
                "Motivation: users integrating tool/function calling and file uploads via the "
                "OpenAI-compatibility endpoints were sending a wide variety of content-types and very large "
                "multipart requests which caused inconsistent runtime behavior, high memory pressure, and "
                "unexpected acceptance of unsupported payloads. This PR introduces a focused, backwards-compatible "
                "implementation for multipart/form-data parsing on the OpenAI-compatibility path, strict "
                "Content-Type validation for tool/file inputs, and deterministic payload limits both per-file "
                "and per-request. Summary of changes: 1) Add a streaming-safe multipart parser that yields parts "
                "rather than buffering entire requests; 2) Validate Content-Type of each part; "
                "3) Enforce configurable limits: max_file_size (default 10MiB), "
                "max_total_request_size (default 50MiB), max_parts_count (default 20)."
            ),
            "file_name": "dsid_ae068ee4aa9640159427cd941bef0238.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts)

    assert "max_file_size" in answer["answer"]
    assert "10MiB" in answer["answer"]
    assert "max_total_request_size" in answer["answer"]
    assert "50MiB" in answer["answer"]
    assert "streaming-safe multipart parser" not in answer["answer"]


def test_build_extractive_answer_contract_review_handles_guarantee_scope():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_guarantee",
        "query": "借款合同中，谁承担连带保证责任？其责任覆盖什么范围？",
    }
    contexts = [
        {
            "content": (
                "流动资金借款合同\n"
                "甲方：海岳银行股份有限公司\n"
                "乙方：远航制造有限公司\n"
                "丙方：远航控股有限公司\n"
                "第三条 保证担保\n"
                "丙方作为保证人，应对乙方在本合同项下的全部债务承担连带保证责任。"
            ),
            "file_name": "contract_003_loan_agreement.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "丙方远航控股有限公司" in answer["answer"]
    assert "全部债务" in answer["answer"]


def test_build_answer_strict_grounded_returns_no_evidence_when_citations_do_not_support_answer():
    from zuno.evals.rag_eval.run_eval import NO_EVIDENCE_ANSWER, _build_answer

    sample = {
        "id": "q_strict_grounded",
        "query": "合同终止后多久删除备份？",
    }
    contexts = [
        {
            "content": "主服务合同约定甲方应在收到发票后10个工作日内付款。",
            "file_name": "contract_001_master_service_agreement.md",
            "chunk_id": "chunk_pay",
            "knowledge_id": "kb_1",
        }
    ]

    answer = asyncio.run(
        _build_answer(
            sample,
            contexts,
            answer_mode="strict_grounded",
            domain_pack_id="contract_review",
        )
    )

    assert answer["answer"] == NO_EVIDENCE_ANSWER
    assert answer["citations"] == []
    assert answer["support_verdict"]["status"] == "insufficient_evidence"
    assert answer["evidence_bundle"]["document_count"] == 1


def test_build_answer_strict_grounded_keeps_supported_answer_and_bundle():
    from zuno.evals.rag_eval.run_eval import _build_answer

    sample = {
        "id": "q_strict_supported",
        "query": "合同终止后多久删除备份？",
    }
    contexts = [
        {
            "content": "合同终止后，乙方应在30日内删除全部备份数据。",
            "file_name": "contract_006_data_processing_addendum.md",
            "chunk_id": "chunk_delete",
            "knowledge_id": "kb_1",
        }
    ]

    answer = asyncio.run(
        _build_answer(
            sample,
            contexts,
            answer_mode="strict_grounded",
            domain_pack_id="contract_review",
        )
    )

    assert "30日内删除全部备份数据" in answer["answer"]
    assert answer["support_verdict"]["status"] == "supported"
    assert answer["evidence_bundle"]["citation_count"] == 1
    assert answer["evidence_bundle"]["items"][0]["is_cited"] is True


def test_build_extractive_answer_contract_review_handles_saas_data_deletion():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_saas_delete",
        "query": "SaaS订阅服务合同终止后，乙方对甲方数据承担哪两步义务？对应的时间要求分别是什么？",
    }
    contexts = [
        {
            "content": (
                "SaaS订阅服务合同\n"
                "第三条 账号与数据\n"
                "甲方拥有其业务数据的所有权。合同终止后30日内，乙方应协助甲方导出数据，"
                "并在导出完成后15日内删除甲方生产环境中的全部个人信息副本。\n"
                "第四条 保密与合规\n"
                "乙方对甲方上传的订单数据和会员信息负有保密义务。"
            ),
            "file_name": "contract_002_saas_subscription.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "导出数据" in answer["answer"]
    assert "30日内" in answer["answer"]
    assert "15日内" in answer["answer"]
    assert "保密义务" not in answer["answer"]


def test_build_extractive_answer_contract_review_handles_payment_trigger():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_payment_trigger",
        "query": "采购框架协议中，甲方付款的两个前置条件是什么？",
    }
    contexts = [
        {
            "content": (
                "采购框架协议\n"
                "第四条 交付与付款\n"
                "甲方在完成验收且收到增值税专用发票后30日内支付对应货款。\n"
                "第五条 违约责任\n"
                "乙方逾期交付的，应承担违约责任。"
            ),
            "file_name": "contract_005_procurement_framework.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "甲方付款以完成验收并收到增值税专用发票为前置条件" in answer["answer"]
    assert "违约责任" not in answer["answer"]


def test_build_extractive_answer_contract_review_handles_distribution_return():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_distribution_return",
        "query": "区域经销协议里，乙方在哪种情况下可以申请退货？是否所有库存都能回购？",
    }
    contexts = [
        {
            "content": (
                "区域经销协议\n"
                "第三条 库存与退货\n"
                "甲方对乙方在授权区域内形成的正常周转库存不承担回购义务。"
                "对于甲方书面确认存在质量缺陷的产品，乙方可在发现后15日内申请退货。"
            ),
            "file_name": "contract_007_distribution_agreement.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "只有甲方书面确认存在质量缺陷的产品" in answer["answer"]
    assert "15日内申请退货" in answer["answer"]
    assert "甲方不承担回购义务" in answer["answer"]


def test_build_extractive_answer_contract_review_handles_guarantee_with_reference_style():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_guarantee_style",
        "query": "借款合同中，谁承担连带保证责任？其责任覆盖什么范围？",
    }
    contexts = [
        {
            "content": (
                "流动资金借款合同\n"
                "甲方：海岳银行股份有限公司\n"
                "乙方：远航制造有限公司\n"
                "丙方：远航控股有限公司\n"
                "第三条 保证担保\n"
                "丙方作为保证人，应对乙方在本合同项下的全部债务承担连带保证责任。"
            ),
            "file_name": "contract_003_loan_agreement.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "在借款合同中，丙方远航控股有限公司作为保证人承担连带保证责任" in answer["answer"]
    assert "其责任覆盖乙方在合同项下的全部债务" in answer["answer"]


def test_build_extractive_answer_contract_review_handles_ip_risk_with_reference_style():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_ip_risk_style",
        "query": "采购框架协议里，如果货物或工艺侵犯第三方知识产权，由谁处理并承担赔偿？",
    }
    contexts = [
        {
            "content": (
                "采购框架协议\n"
                "第五条 知识产权与合规\n"
                "乙方保证所供货物及其制造工艺不侵犯第三方知识产权。"
                "如因侵权引发索赔，乙方应负责处理并赔偿甲方损失。"
            ),
            "file_name": "contract_005_procurement_framework.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "采购框架协议约定，如因侵权引发索赔，由乙方负责处理并赔偿甲方损失。" in answer["answer"]


def test_build_extractive_answer_contract_review_handles_incident_response_with_reference_style():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_incident_style",
        "query": "外包运维服务合同中，高危安全事件发生后，乙方在时间线上要完成哪三件事？",
    }
    contexts = [
        {
            "content": (
                "外包运维服务合同\n"
                "第三条 安全事件与协助\n"
                "发生影响甲方业务连续性的高危安全事件时，乙方应在1小时内启动应急响应，"
                "在4小时内提交初步事件报告，并配合甲方完成取证、隔离和修复。"
            ),
            "file_name": "contract_008_outsourcing_service_agreement.md",
        }
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert "高危安全事件发生后，乙方应在1小时内启动应急响应，在4小时内提交初步事件报告，并配合甲方完成取证、隔离和修复。" in answer["answer"]


def test_build_extractive_answer_contract_review_selects_relevant_citations():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_citation_focus",
        "query": "借款合同中，谁承担连带保证责任？其责任覆盖什么范围？",
    }
    contexts = [
        {
            "content": "主服务合同 第二条 验收安排 甲方应在收到乙方交付通知后5个工作日内完成验收。",
            "file_name": "contract_001_master_service_agreement.md",
        },
        {
            "content": (
                "流动资金借款合同\n"
                "丙方：远航控股有限公司\n"
                "第三条 保证担保\n"
                "丙方作为保证人，应对乙方在本合同项下的全部债务承担连带保证责任。"
            ),
            "file_name": "contract_003_loan_agreement.md",
        },
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert answer["citations"][0]["file_name"] == "contract_003_loan_agreement.md"


def test_build_extractive_answer_contract_review_prefers_canonical_citation_over_variant():
    from zuno.evals.rag_eval.run_eval import _build_extractive_answer

    sample = {
        "id": "q_canonical_citation",
        "query": "区域经销协议里，乙方在哪种情况下可以申请退货？是否所有库存都能回购？",
    }
    contexts = [
        {
            "content": (
                "区域经销协议\n"
                "第三条 库存与退货\n"
                "甲方对乙方在授权区域内形成的正常周转库存不承担回购义务。"
                "对于甲方书面确认存在质量缺陷的产品，乙方可在发现后15日内申请退货。"
            ),
            "file_name": "contract_007_distribution_agreement__variant_1.md",
        },
        {
            "content": (
                "区域经销协议\n"
                "第三条 库存与退货\n"
                "甲方对乙方在授权区域内形成的正常周转库存不承担回购义务。"
                "对于甲方书面确认存在质量缺陷的产品，乙方可在发现后15日内申请退货。"
            ),
            "file_name": "contract_007_distribution_agreement.md",
        },
    ]

    answer = _build_extractive_answer(sample, contexts, domain_pack_id="contract_review")

    assert len(answer["citations"]) == 1
    assert answer["citations"][0]["file_name"] == "contract_007_distribution_agreement.md"


def test_overlap_score_handles_semantically_equivalent_contract_answers():
    from zuno.evals.rag_eval.run_eval import _overlap_score

    answer = "甲方应在收到交付通知后5个工作日内完成验收，逾期未提出实质性异议的视为该阶段交付物已经验收通过。"
    reference = "在主服务合同中，甲方应在收到交付通知后5个工作日内完成验收；若逾期未提出实质性异议，则视为该阶段交付物已经验收通过。"

    assert _overlap_score(answer, reference) >= 0.45


def test_judge_answer_heuristic_supports_semantic_contract_fragments():
    from zuno.evals.rag_eval.run_eval import _judge_answer_heuristic

    sample = {
        "id": "q_faithful_contract",
        "reference_answer": "甲方应在收到交付通知后5个工作日内完成验收；逾期未提出实质性异议的，视为交付物验收通过。",
    }
    answer_row = {
        "answer": "甲方应在收到交付通知后5个工作日内完成验收；逾期未提出实质性异议的，视为该阶段交付物已经验收通过。"
    }
    contexts = [
        {
            "content": (
                "主服务合同\n"
                "第二条 验收安排\n"
                "甲方应在收到乙方交付通知后5个工作日内完成验收并书面反馈。"
                "甲方逾期未提出实质性异议的，视为该阶段交付物已经验收通过。"
            )
        }
    ]

    judged = _judge_answer_heuristic(sample, answer_row, contexts)

    assert judged["faithfulness"] >= 0.9


def test_judge_answer_heuristic_supports_multiline_extracts():
    from zuno.evals.rag_eval.run_eval import _judge_answer_heuristic

    sample = {
        "id": "q_judge",
        "reference_answer": "应在20个工作日内返还数据，并在30日内删除备份。",
    }
    answer_row = {
        "answer": "应在20个工作日内返还数据。\n并在30日内删除备份。",
    }
    contexts = [
        {
            "content": (
                "数据处理附录\n"
                "第五条 删除与返还\n"
                "应在20个工作日内返还数据。\n"
                "并在30日内删除备份。"
            )
        }
    ]

    judge = _judge_answer_heuristic(sample, answer_row, contexts)

    assert judge["faithfulness"] == 1.0
    assert judge["answer_correctness"] > 0.0


def test_graph_retriever_resolves_graph_hits_back_to_source_chunks():
    from zuno.schema.search import SearchModel
    from zuno.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            assert knowledge_id == "k_graph"
            return [
                {
                    "source": "ProjectAtlas",
                    "target": "Bob",
                    "chunk_ids": ["chunk_1"],
                },
                {
                    "source": "Bob",
                    "target": "Carol",
                    "chunk_ids": ["chunk_2"],
                },
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            assert collection_name == "k_graph"
            assert chunk_ids == ["chunk_1", "chunk_2"]
            return [
                SearchModel(
                    chunk_id="chunk_1",
                    content="ProjectAtlas approvals are handled by Bob.",
                    score=0.0,
                    file_id="file_1",
                    file_name="atlas.md",
                    update_time="2026-05-27T00:00:00",
                    knowledge_id="k_graph",
                    summary="",
                ),
                SearchModel(
                    chunk_id="chunk_2",
                    content="Bob reports to Carol.",
                    score=0.0,
                    file_id="file_2",
                    file_name="org.md",
                    update_time="2026-05-27T00:00:00",
                    knowledge_id="k_graph",
                    summary="",
                ),
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "ProjectAtlas 的发布审批最后归谁负责？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert [doc["chunk_id"] for doc in result["documents"]] == ["chunk_1", "chunk_2"]
    assert result["paths"] == ["ProjectAtlas -> Bob", "Bob -> Carol"]
    assert "Bob reports to Carol." in result["content"]


def test_graph_extractor_connects_anchor_to_structure_lists():
    from zuno.services.graphrag.extractor import GraphExtractor

    chunk = {
        "chunk_id": "chunk_milvus",
        "content": (
            "## How is Milvus designed?\n\n"
            "The system breaks down into four levels:\n\n"
            "- Access layer: The access layer is composed of a group of stateless proxies.\n"
            "- Coordinator service: The coordinator service assigns tasks to the worker nodes.\n"
            "- Worker nodes: The worker nodes execute DML/DDL commands.\n"
            "- Storage: Storage is the bone of the system.\n"
        ),
    }

    result = asyncio.run(GraphExtractor().extract_from_chunk(chunk, "k_graph"))
    relation_pairs = {(item["source"], item["target"]) for item in result["relations"]}

    assert ("Milvus", "Access layer") in relation_pairs
    assert ("Milvus", "Coordinator service") in relation_pairs
    assert ("Milvus", "Worker nodes") in relation_pairs
    assert ("Milvus", "Storage") in relation_pairs


def test_graph_extractor_filters_noise_and_keeps_rabbitmq_list_labels():
    from zuno.services.graphrag.extractor import GraphExtractor

    chunk = {
        "chunk_id": "chunk_rabbitmq",
        "content": (
            "RabbitMQ server overview.\n"
            "An example should not become a graph entity.\n"
            "- transports - extensions of the RabbitMQ server that expose the AMQP protocol.\n"
            "- gateways - extensions of the RabbitMQ server that bridge between AMQP and other networks.\n"
            "For operators, this section is a reference only.\n"
        ),
    }

    result = asyncio.run(GraphExtractor().extract_from_chunk(chunk, "k_graph"))
    entity_names = {item["name"] for item in result["entities"]}
    relation_pairs = {(item["source"], item["target"]) for item in result["relations"]}

    assert "An" not in entity_names
    assert "For" not in entity_names
    assert "RabbitMQ" in entity_names
    assert "transports" in entity_names
    assert "gateways" in entity_names
    assert ("RabbitMQ", "transports") in relation_pairs
    assert ("RabbitMQ", "gateways") in relation_pairs


def test_graph_extractor_captures_agent_server_deployment_and_persistence_lists():
    from zuno.services.graphrag.extractor import GraphExtractor

    chunk = {
        "chunk_id": "chunk_agent_server",
        "content": (
            "## Parts of a deployment\n\n"
            "When you deploy Agent Server, you are deploying one or more graphs, a database for persistence, and a task queue.\n\n"
            "### Persistence\n\n"
            "Agent Server persists three types of data, all backed by PostgreSQL by default:\n"
            "- **Core resource data**: assistants, threads, runs, and cron jobs.\n"
            "- **Checkpoints (short-term memory)**: snapshots of graph execution state written at each step.\n"
            "- **Store (long-term memory)**: memory that persists across threads.\n"
            "### Task queue\n"
            "Redis handles the signaling, cancellation, and streaming pub/sub between API servers and queue workers. "
            "Run data itself is always read from and written to PostgreSQL.\n"
        ),
    }

    result = asyncio.run(GraphExtractor().extract_from_chunk(chunk, "k_graph"))
    relation_pairs = {(item["source"], item["target"]) for item in result["relations"]}

    assert ("Agent Server", "graphs") in relation_pairs
    assert ("Agent Server", "persistence") in relation_pairs
    assert ("Agent Server", "task queue") in relation_pairs
    assert ("Agent Server", "Core resource data") in relation_pairs
    assert ("Agent Server", "Checkpoints (short-term memory)") in relation_pairs
    assert ("Agent Server", "Store (long-term memory)") in relation_pairs


def test_graph_retriever_uses_query_seed_entities_from_query_text():
    from zuno.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            seen_entities.append(entity_name)
            return []

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return []

    asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "RabbitMQ Universe 中 transports 和 gateways 分别是什么？\nMilvus Storage Bob",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert "RabbitMQ" in seen_entities
    assert "RabbitMQ Universe" in seen_entities
    assert "Milvus" in seen_entities
    assert "Milvus Storage Bob" in seen_entities


def test_graph_retriever_skips_graph_for_non_relational_single_entity_query():
    from zuno.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            seen_entities.append(entity_name)
            return [{"source": "Milvus", "target": "Introduction", "chunk_ids": ["chunk_1"]}]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return []

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "Milvus 最初创建的核心目标是什么？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert seen_entities == []
    assert result["documents"] == []
    assert result["paths"] == []


def test_graph_retriever_keeps_graph_for_relational_structure_query_and_filters_generic_targets():
    from zuno.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            seen_entities.append(entity_name)
            return [
                {"source": "Milvus", "target": "Introduction", "chunk_ids": ["chunk_noise"]},
                {"source": "Milvus", "target": "Storage", "chunk_ids": ["chunk_good"]},
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            assert chunk_ids == ["chunk_good"]
            return []

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "Milvus 的系统设计被拆成哪四个层次？各自承担什么角色？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert "Milvus" in seen_entities
    assert result["paths"] == ["Milvus -> Storage"]


def test_graph_retriever_filters_scale_template_targets_for_agent_server_queries():
    from zuno.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            return [
                {"source": "Agent Server", "target": "Example", "chunk_ids": ["chunk_noise"]},
                {"source": "Agent Server", "target": "High", "chunk_ids": ["chunk_noise_2"]},
                {"source": "Agent Server", "target": "Persistence", "chunk_ids": ["chunk_good"]},
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            assert chunk_ids == ["chunk_good"]
            return []

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "Agent Server 持久化哪三类数据？默认后端分别是什么？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert result["paths"] == ["Agent Server -> Persistence"]


def test_graph_retriever_adds_alias_seed_for_chinese_persistence_query():
    from zuno.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            seen_entities.append(entity_name)
            if entity_name == "Persistence":
                return [{"source": "Agent Server", "target": "Persistence", "chunk_ids": ["chunk_good"]}]
            return []

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return [
                {
                    "chunk_id": "chunk_good",
                    "file_name": "md_001_agent-server.mdx",
                    "content": "Persistence. Agent Server persists three types of data backed by PostgreSQL by default.",
                    "summary": "",
                }
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "Agent Server 持久化哪三类数据？默认后端分别是什么？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert "Persistence" in seen_entities
    assert result["paths"] == ["Agent Server -> Persistence"]


def test_graph_retriever_does_not_enable_graph_only_because_query_has_many_ascii_terms():
    from zuno.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            seen_entities.append(entity_name)
            return [{"source": "LangSmith", "target": "Assistants", "chunk_ids": ["chunk_1"]}]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return []

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "LangSmith Agent Server API 主要用于创建和管理哪些资源？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert seen_entities == []
    assert result["paths"] == []


def test_graph_retriever_skips_graph_for_non_relational_type_listing_query():
    from zuno.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            seen_entities.append(entity_name)
            return [{"source": "Milvus", "target": "RabbitMQ", "chunk_ids": ["chunk_1"]}]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return []

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "Milvus 支持的向量索引类型里，哪些属于近似最近邻搜索，且 HNSW 适合什么场景？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert seen_entities == []
    assert result["paths"] == []


def test_graph_retriever_downranks_agent_server_scale_chunks_for_non_scaling_queries():
    from zuno.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            return [
                {"source": "Agent Server", "target": "Persistence", "chunk_ids": ["chunk_scale", "chunk_good"]},
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return [
                {
                    "chunk_id": "chunk_scale",
                    "file_name": "md_001_agent-server-scale.mdx",
                    "content": "Example self-hosted Agent Server configurations for high reads and writes.",
                    "summary": "",
                },
                {
                    "chunk_id": "chunk_good",
                    "file_name": "md_001_agent-server.mdx",
                    "content": "Parts of a deployment. When you deploy Agent Server, you are deploying graphs, persistence, and a task queue.",
                    "summary": "",
                },
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "部署 Agent Server 时会部署哪些核心组成部分？它们分别对应什么用途？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert result["documents"][0]["chunk_id"] == "chunk_good"


def test_graph_retriever_downranks_docs_navigation_chunks_when_question_is_not_about_tests():
    from zuno.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            return [
                {"source": "GraphRAG", "target": "Python", "chunk_ids": ["chunk_nav", "chunk_intro"]},
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return [
                {
                    "chunk_id": "chunk_nav",
                    "file_name": "tmp4m02o8w9.md",
                    "content": "Development > Run tests\nRun the tests using uv.",
                    "summary": "",
                },
                {
                    "chunk_id": "chunk_intro",
                    "file_name": "tmp4m02o8w9.md",
                    "content": "GraphRAG for Python. This package is a renamed continuation of neo4j-genai.",
                    "summary": "",
                },
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "Neo4j GraphRAG for Python 文档如何说明这个包的定位和 neo4j-genai 的关系？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert result["documents"][0]["chunk_id"] == "chunk_intro"


def test_text_parser_chunk_ids_are_stable_for_repeated_parses(tmp_path):
    from zuno.services.rag.doc_parser.text import TextParser

    path = tmp_path / "demo.txt"
    path.write_text("ProjectAtlas release approvals are handled by Bob.\nBob reports to Carol.", encoding="utf-8")

    parser = TextParser()
    parser.chunk_size = 100
    first = asyncio.run(parser.parse_into_chunks("file_demo", str(path), "k_demo"))
    second = asyncio.run(parser.parse_into_chunks("file_demo", str(path), "k_demo"))

    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]


def test_rag_detail_retrieval_preserves_document_metadata_after_rerank(monkeypatch):
    from zuno.schema.search import SearchModel
    from zuno.services.rag.handler import RagHandler

    async def fake_mix_retrieval(*args, **kwargs):
        return [
            SearchModel(
                chunk_id="chunk_1",
                content="ProjectAtlas release approvals are handled by Bob.",
                score=0.3,
                file_id="file_1",
                file_name="project_atlas_release.md",
                update_time="2026-05-27T00:00:00",
                knowledge_id="k_demo",
                summary="",
            ),
            SearchModel(
                chunk_id="chunk_2",
                content="Bob reports to Carol.",
                score=0.2,
                file_id="file_2",
                file_name="bob_manager.md",
                update_time="2026-05-27T00:00:00",
                knowledge_id="k_demo",
                summary="",
            ),
        ]

    class FakeRerankResult:
        def __init__(self, index, score):
            self.index = index
            self.score = score

    async def fake_rerank_documents(query, documents, **kwargs):
        return [FakeRerankResult(index=1, score=0.91), FakeRerankResult(index=0, score=0.82)]

    async def fake_runtime_settings(*args, **kwargs):
        return {
            "knowledge_config": {
                "retrieval_settings": {
                    "top_k": 5,
                    "rerank_enabled": True,
                    "rerank_top_k": 5,
                    "score_threshold": None,
                }
            },
            "rerank_config": None,
        }

    monkeypatch.setattr(RagHandler, "_resolve_runtime_settings", classmethod(lambda cls, ids: fake_runtime_settings()))
    monkeypatch.setattr(RagHandler, "mix_retrival_documents", classmethod(lambda cls, *args, **kwargs: fake_mix_retrieval()))
    monkeypatch.setattr("zuno.services.rag.handler.Reranker.rerank_documents", fake_rerank_documents)

    result = asyncio.run(
        RagHandler._retrieve_ranked_documents_rag_detail(
            "ProjectAtlas 的发布审批最终属于哪个团队？",
            ["k_demo"],
            ["k_demo"],
            needs_query_rewrite=False,
            retrieval_options={"rerank_enabled": True, "rerank_top_k": 5, "score_threshold": None, "top_k": 5},
        )
    )

    assert result["documents"][0]["file_name"] == "bob_manager.md"
    assert result["documents"][0]["chunk_id"] == "chunk_2"


def test_rag_detail_without_external_rerank_uses_local_priority_for_agent_server_query(monkeypatch):
    from zuno.schema.search import SearchModel
    from zuno.services.rag.handler import RagHandler

    async def fake_mix_retrieval(*args, **kwargs):
        return [
            SearchModel(
                chunk_id="chunk_scale",
                content="Example self-hosted Agent Server configurations for high reads and writes.",
                score=0.95,
                file_id="file_1",
                file_name="md_001_agent-server-scale.mdx",
                update_time="2026-05-28T00:00:00",
                knowledge_id="k_demo",
                summary="",
            ),
            SearchModel(
                chunk_id="chunk_good",
                content="Parts of a deployment. When you deploy Agent Server, you are deploying graphs, a database for persistence, and a task queue.",
                score=0.70,
                file_id="file_2",
                file_name="md_001_agent-server.mdx",
                update_time="2026-05-28T00:00:00",
                knowledge_id="k_demo",
                summary="",
            ),
        ]

    async def fake_runtime_settings(*args, **kwargs):
        return {
            "knowledge_config": {
                "retrieval_settings": {
                    "top_k": 5,
                    "rerank_enabled": False,
                    "rerank_top_k": 5,
                    "score_threshold": None,
                }
            },
            "rerank_config": None,
        }

    monkeypatch.setattr(RagHandler, "_resolve_runtime_settings", classmethod(lambda cls, ids: fake_runtime_settings()))
    monkeypatch.setattr(RagHandler, "mix_retrival_documents", classmethod(lambda cls, *args, **kwargs: fake_mix_retrieval()))

    result = asyncio.run(
        RagHandler._retrieve_ranked_documents_rag_detail(
            "部署 Agent Server 时会部署哪些核心组成部分？它们分别对应什么用途？",
            ["k_demo"],
            ["k_demo"],
            needs_query_rewrite=False,
            retrieval_options={"rerank_enabled": False, "score_threshold": None, "top_k": 5},
        )
    )

    assert result["documents"][0]["file_name"] == "md_001_agent-server.mdx"
    assert result["documents"][0]["chunk_id"] == "chunk_good"


def test_rag_detail_local_priority_bridges_chinese_persistence_query_to_english_section(monkeypatch):
    from zuno.schema.search import SearchModel
    from zuno.services.rag.handler import RagHandler

    async def fake_mix_retrieval(*args, **kwargs):
        return [
            SearchModel(
                chunk_id="chunk_scale",
                content="Example self-hosted Agent Server configurations for high reads and writes.",
                score=0.95,
                file_id="file_1",
                file_name="md_001_agent-server-scale.mdx",
                update_time="2026-05-28T00:00:00",
                knowledge_id="k_demo",
                summary="",
            ),
            SearchModel(
                chunk_id="chunk_deployment",
                content="Parts of a deployment. When you deploy Agent Server, you are deploying graphs, a database for persistence, and a task queue.",
                score=0.85,
                file_id="file_2",
                file_name="md_001_agent-server.mdx",
                update_time="2026-05-28T00:00:00",
                knowledge_id="k_demo",
                summary="",
            ),
            SearchModel(
                chunk_id="chunk_persistence",
                content=(
                    "Persistence. Agent Server persists three types of data. "
                    "Core resource data is always stored in PostgreSQL. "
                    "Checkpoints are stored in PostgreSQL by default."
                ),
                score=0.70,
                file_id="file_3",
                file_name="md_001_agent-server.mdx",
                update_time="2026-05-28T00:00:00",
                knowledge_id="k_demo",
                summary="",
            ),
        ]

    async def fake_runtime_settings(*args, **kwargs):
        return {
            "knowledge_config": {
                "retrieval_settings": {
                    "top_k": 5,
                    "rerank_enabled": False,
                    "rerank_top_k": 5,
                    "score_threshold": None,
                }
            },
            "rerank_config": None,
        }

    monkeypatch.setattr(RagHandler, "_resolve_runtime_settings", classmethod(lambda cls, ids: fake_runtime_settings()))
    monkeypatch.setattr(RagHandler, "mix_retrival_documents", classmethod(lambda cls, *args, **kwargs: fake_mix_retrieval()))

    result = asyncio.run(
        RagHandler._retrieve_ranked_documents_rag_detail(
            "Agent Server 持久化哪三类数据？默认后端分别是什么？",
            ["k_demo"],
            ["k_demo"],
            needs_query_rewrite=False,
            retrieval_options={"rerank_enabled": False, "score_threshold": None, "top_k": 5},
        )
    )

    assert result["documents"][0]["chunk_id"] == "chunk_persistence"


def test_graph_retriever_prefers_task_queue_section_for_redis_postgres_question():
    from zuno.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10, domain_pack_id=None):
            return [
                {"source": "Agent Server", "target": "Task queue", "chunk_ids": ["chunk_diagram", "chunk_task_queue"]},
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return [
                {
                    "chunk_id": "chunk_diagram",
                    "file_name": "md_001_agent-server.mdx",
                    "content": "Runtime architecture > Container architecture. API writes to Postgres and notifies Redis.",
                    "summary": "",
                },
                {
                    "chunk_id": "chunk_task_queue",
                    "file_name": "md_001_agent-server.mdx",
                    "content": (
                        "Parts of a deployment > Task queue. Redis handles the signaling, cancellation, "
                        "and streaming pub/sub between API servers and queue workers. "
                        "Run data itself is always read from and written to PostgreSQL."
                    ),
                    "summary": "",
                },
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "在 Agent Server 的 task queue 设计中，Redis 和 PostgreSQL 分别保存什么？",
            "k_graph",
            graph_hop_limit=2,
            max_paths_per_entity=5,
        )
    )

    assert result["documents"][0]["chunk_id"] == "chunk_task_queue"


def test_reranker_falls_back_when_request_errors(monkeypatch):
    from zuno.services.rag.rerank import Reranker

    monkeypatch.setattr(Reranker, "_is_configured", classmethod(lambda cls, config_override=None: True))

    async def fake_request_rerank(*args, **kwargs):
        raise RuntimeError("rerank service disconnected")

    monkeypatch.setattr(Reranker, "request_rerank", classmethod(lambda cls, *args, **kwargs: fake_request_rerank()))

    results = asyncio.run(
        Reranker.rerank_documents(
            "Agent Server 持久化哪三类数据？",
            [
                "scale config chunk",
                "persistence chunk",
            ],
        )
    )

    assert len(results) == 2
    assert results[0].content == "scale config chunk"


def test_orchestrator_skips_rag_entry_chunk_for_already_graph_worthy_query():
    from zuno.services.graphrag.orchestrator import RetrievalOrchestrator

    captured = {}

    class FakeRagRetriever:
        async def retrieve(self, query, knowledge_ids, options=None):
            return {
                "content": "rag content",
                "raw_content": "rag content",
                "documents": [
                    {"content": "Runtime architecture > Run execution lifecycle. A client sends a request to an API server."}
                ],
                "document_count": 1,
                "requested_top_k": 5,
                "top_score": 1.0,
                "score_threshold": None,
            }

    class FakeGraphRetriever:
        def _extract_query_seeds(self, query):
            return ["Agent Server", "API"]

        def _is_graph_worthy_query(self, query, seed_entities):
            return True

        async def retrieve(self, query, knowledge_id, graph_hop_limit=2, max_paths_per_entity=10):
            captured["query"] = query
            return {"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}

    orchestrator = RetrievalOrchestrator(
        rag_retriever=FakeRagRetriever(),
        graph_retriever=FakeGraphRetriever(),
    )

    asyncio.run(
        orchestrator._run_single_pass(
            "hybrid",
            "一次 Agent Server run 从 API server 到 queue worker 再到客户端流式返回的执行路径是什么？",
            ["k_demo"],
            {"use_rag_entry_chunk": True},
        )
    )

    assert captured["query"] == "一次 Agent Server run 从 API server 到 queue worker 再到客户端流式返回的执行路径是什么？"


def test_orchestrator_keeps_rag_entry_chunk_for_weak_graph_query():
    from zuno.services.graphrag.orchestrator import RetrievalOrchestrator

    captured = {}

    class FakeRagRetriever:
        async def retrieve(self, query, knowledge_ids, options=None):
            return {
                "content": "rag content",
                "raw_content": "rag content",
                "documents": [
                    {"content": "Entry chunk about ProjectAtlas release approvals handled by Bob."}
                ],
                "document_count": 1,
                "requested_top_k": 5,
                "top_score": 1.0,
                "score_threshold": None,
            }

    class FakeGraphRetriever:
        def _extract_query_seeds(self, query):
            return ["ProjectAtlas"]

        def _is_graph_worthy_query(self, query, seed_entities):
            return False

        async def retrieve(self, query, knowledge_id, graph_hop_limit=2, max_paths_per_entity=10):
            captured["query"] = query
            return {"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}

    orchestrator = RetrievalOrchestrator(
        rag_retriever=FakeRagRetriever(),
        graph_retriever=FakeGraphRetriever(),
    )

    asyncio.run(
        orchestrator._run_single_pass(
            "hybrid",
            "ProjectAtlas 最终由谁审批？",
            ["k_demo"],
            {"use_rag_entry_chunk": True},
        )
    )

    assert "Entry chunk about ProjectAtlas release approvals handled by Bob." in captured["query"]


def test_graph_retriever_extracts_additional_multiline_seeds_from_entry_chunk():
    from zuno.services.graphrag.retriever import GraphRetriever

    seeds = GraphRetriever._extract_query_seeds(
        "Python 閲屽彉閲忋€佸懡鍚嶇┖闂村拰瀵硅薄缁戝畾涔嬮棿鏄粈涔堝叧绯伙紵\n"
        "Python namespace maps names to objects and assignment binds a name to an object."
    )

    lowered = {seed.lower() for seed in seeds}
    assert "python" in lowered
    assert any("namespace" in seed for seed in lowered) or any("命名空间" in seed for seed in seeds)


def test_graph_retriever_needs_entry_chunk_for_generic_relation_seed():
    from zuno.services.graphrag.retriever import GraphRetriever

    assert GraphRetriever._needs_entry_chunk(
        "Python 閲屽彉閲忋€佸懡鍚嶇┖闂村拰瀵硅薄缁戝畾涔嬮棿鏄粈涔堝叧绯伙紵",
        ["Python"],
    ) is True


def test_graph_retriever_augments_focus_file_with_sibling_chunks():
    from zuno.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=2, limit=10, domain_pack_id=None):
            return [
                {
                    "source": "Python",
                    "target": "namespace",
                    "chunk_ids": ["focus_chunk"],
                }
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, knowledge_id, chunk_ids):
            return [
                {
                    "chunk_id": "focus_chunk",
                    "file_id": "file_002",
                    "file_name": "002_Python 变量、命名空间与对象绑定.md",
                    "content": "命名空间 = 名字到对象的映射表",
                    "summary": "",
                }
            ]

        async def get_documents_by_file_id(self, knowledge_id, file_id, limit=None):
            return [
                {
                    "chunk_id": "focus_chunk",
                    "file_id": "file_002",
                    "file_name": "002_Python 变量、命名空间与对象绑定.md",
                    "content": "命名空间 = 名字到对象的映射表",
                    "summary": "",
                },
                {
                    "chunk_id": "sibling_chunk",
                    "file_id": "file_002",
                    "file_name": "002_Python 变量、命名空间与对象绑定.md",
                    "content": "变量只是名字，赋值是把名字绑定到对象。",
                    "summary": "",
                },
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "Python 里变量、命名空间和对象绑定之间是什么关系？",
            "k_demo",
            graph_hop_limit=2,
        )
    )

    chunk_ids = [doc.get("chunk_id") for doc in result["documents"]]
    assert "focus_chunk" in chunk_ids
    assert "sibling_chunk" in chunk_ids
    sibling_doc = next(doc for doc in result["documents"] if doc.get("chunk_id") == "sibling_chunk")
    assert sibling_doc.get("graph_file_focus", 0) >= 1


def test_graph_retriever_score_demotes_metadata_heavy_graph_chunk():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = "Python 里变量、命名空间和对象绑定之间是什么关系？"
    query_terms = GraphRetriever._expanded_query_terms(query, ["Python", "命名空间", "对象绑定"])
    metadata_chunk = {
        "file_name": "001_Python 关键字.md",
        "content": "title: Python 关键字\n"
        "tags: #Python #命名空间 #Agent #Infra\n"
        "aliases: 关键字\n"
        "路径语境：[[Python 本体]]",
        "summary": "",
        "graph_seed_hit_count": 2,
        "graph_support_count": 2,
    }
    explanatory_chunk = {
        "file_name": "002_Python 变量、命名空间与对象绑定.md",
        "content": "变量只是名字，命名空间是名字到对象的映射表，赋值是把名字绑定到对象。",
        "summary": "",
        "graph_seed_hit_count": 2,
        "graph_support_count": 1,
    }

    metadata_score = GraphRetriever._score_document(query, query_terms, metadata_chunk)
    explanatory_score = GraphRetriever._score_document(query, query_terms, explanatory_chunk)

    assert explanatory_score > metadata_score


def test_orchestrator_hybrid_content_preserves_merged_retriever_order():
    from zuno.services.graphrag.orchestrator import RetrievalOrchestrator

    class FakeRagRetriever:
        async def retrieve(self, query, knowledge_ids, options=None):
            return {
                "content": "General Agent Server overview.\nRuntime architecture > Run execution lifecycle.",
                "raw_content": "General Agent Server overview.\nRuntime architecture > Run execution lifecycle.",
                "documents": [
                    {
                        "chunk_id": "rag_noise",
                        "content": "General Agent Server overview.",
                        "file_name": "agent.md",
                        "score": 0.9,
                    },
                    {
                        "chunk_id": "rag_good",
                        "content": "Runtime architecture > Run execution lifecycle. A client sends a request to an API server.",
                        "file_name": "agent.md",
                        "score": 0.8,
                    },
                ],
                "document_count": 2,
                "requested_top_k": 5,
                "top_score": 0.9,
                "score_threshold": None,
            }

    class FakeGraphRetriever:
        async def retrieve(self, query, knowledge_id, graph_hop_limit=2, max_paths_per_entity=10):
            return {
                "content": "Example configuration for high reads and high writes > Autoscaling.",
                "raw_content": "Example configuration for high reads and high writes > Autoscaling.",
                "documents": [
                    {
                        "chunk_id": "graph_noise",
                        "content": "Example configuration for high reads and high writes > Autoscaling.",
                        "file_name": "scale.mdx",
                        "graph_seed_hit_count": 5,
                        "graph_support_count": 1,
                        "score": 0.0,
                    }
                ],
                "entities": ["API"],
                "paths": ["API -> Configure"],
            }

    orchestrator = RetrievalOrchestrator(
        rag_retriever=FakeRagRetriever(),
        graph_retriever=FakeGraphRetriever(),
    )

    result = asyncio.run(
        orchestrator._run_single_pass(
            "hybrid",
            "一次 Agent Server run 从 API server 到 queue worker 再到客户端流式返回的执行路径是什么？",
            ["k_demo"],
            {"top_k": 5, "use_rag_entry_chunk": False},
        )
    )

    merged_content = result["content"]
    assert merged_content.startswith("General Agent Server overview.")
    assert "Runtime architecture > Run execution lifecycle." in merged_content


def test_orchestrator_hybrid_content_keeps_vector_result_before_graph_result():
    from zuno.services.graphrag.orchestrator import RetrievalOrchestrator

    class FakeRagRetriever:
        async def retrieve(self, query, knowledge_ids, options=None):
            return {
                "content": "General Agent Server overview.",
                "raw_content": "General Agent Server overview.",
                "documents": [
                    {
                        "chunk_id": "rag_noise",
                        "content": "General Agent Server overview.",
                        "file_name": "agent.md",
                        "score": 0.9,
                    }
                ],
                "document_count": 1,
                "requested_top_k": 5,
                "top_score": 0.9,
                "score_threshold": None,
            }

    class FakeGraphRetriever:
        async def retrieve(self, query, knowledge_id, graph_hop_limit=2, max_paths_per_entity=10):
            return {
                "content": "Persistence. Agent Server persists three types of data backed by PostgreSQL by default.",
                "raw_content": "Persistence. Agent Server persists three types of data backed by PostgreSQL by default.",
                "documents": [
                    {
                        "chunk_id": "graph_good",
                        "content": "Persistence. Agent Server persists three types of data backed by PostgreSQL by default.",
                        "file_name": "agent.md",
                        "graph_seed_hit_count": 3,
                        "graph_support_count": 2,
                        "score": 0.0,
                    }
                ],
                "entities": ["Persistence"],
                "paths": ["Agent Server -> Persistence"],
            }

    orchestrator = RetrievalOrchestrator(
        rag_retriever=FakeRagRetriever(),
        graph_retriever=FakeGraphRetriever(),
    )

    result = asyncio.run(
        orchestrator._run_single_pass(
            "hybrid",
            "Agent Server 持久化哪三类数据？默认后端分别是什么？",
            ["k_demo"],
            {"top_k": 5, "use_rag_entry_chunk": False},
        )
    )

    assert result["content"].startswith("General Agent Server overview.")
    assert "Persistence. Agent Server persists three types of data" in result["content"]

