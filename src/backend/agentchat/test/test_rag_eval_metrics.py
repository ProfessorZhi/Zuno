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


def test_run_eval_supports_llm_answer_and_judge_modes(monkeypatch):
    from agentchat.core.models import manager as model_manager
    from agentchat.evals.rag_eval import run_eval as run_eval_module

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
    from agentchat.evals.rag_eval.run_eval import _extract_contexts

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
    from agentchat.evals.rag_eval.run_eval import _extract_contexts

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

    assert contexts[0]["content"].startswith("Runtime architecture > Run execution lifecycle")
    assert contexts[1]["content"].startswith("Example configuration for high reads and high writes")


def test_graph_retriever_resolves_graph_hits_back_to_source_chunks():
    from agentchat.schema.search import SearchModel
    from agentchat.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.graphrag.extractor import GraphExtractor

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
    from agentchat.services.graphrag.extractor import GraphExtractor

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
    from agentchat.services.graphrag.extractor import GraphExtractor

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


def test_graph_retriever_uses_query_seed_entities_from_first_line_only():
    from agentchat.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    assert "transports" in seen_entities
    assert "gateways" in seen_entities
    assert "Milvus" not in seen_entities
    assert "Bob" not in seen_entities


def test_graph_retriever_skips_graph_for_non_relational_single_entity_query():
    from agentchat.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.graphrag.retriever import GraphRetriever

    seen_entities = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.rag.doc_parser.text import TextParser

    path = tmp_path / "demo.txt"
    path.write_text("ProjectAtlas release approvals are handled by Bob.\nBob reports to Carol.", encoding="utf-8")

    parser = TextParser()
    first = asyncio.run(parser.parse_into_chunks("file_demo", str(path), "k_demo"))
    second = asyncio.run(parser.parse_into_chunks("file_demo", str(path), "k_demo"))

    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]


def test_rag_detail_retrieval_preserves_document_metadata_after_rerank(monkeypatch):
    from agentchat.schema.search import SearchModel
    from agentchat.services.rag.handler import RagHandler

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
    monkeypatch.setattr("agentchat.services.rag.handler.Reranker.rerank_documents", fake_rerank_documents)

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
    from agentchat.schema.search import SearchModel
    from agentchat.services.rag.handler import RagHandler

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
    from agentchat.schema.search import SearchModel
    from agentchat.services.rag.handler import RagHandler

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
    from agentchat.services.graphrag.retriever import GraphRetriever

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, hops=1, limit=10):
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
    from agentchat.services.rag.rerank import Reranker

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
    from agentchat.services.graphrag.orchestrator import RetrievalOrchestrator

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
    from agentchat.services.graphrag.orchestrator import RetrievalOrchestrator

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


def test_orchestrator_hybrid_content_uses_query_aware_merged_order():
    from agentchat.services.graphrag.orchestrator import RetrievalOrchestrator

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
    assert merged_content.startswith("Runtime architecture > Run execution lifecycle.")


def test_orchestrator_hybrid_content_can_elevate_graph_doc_when_query_matches_it():
    from agentchat.services.graphrag.orchestrator import RetrievalOrchestrator

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

    assert result["content"].startswith("Persistence. Agent Server persists three types of data")
