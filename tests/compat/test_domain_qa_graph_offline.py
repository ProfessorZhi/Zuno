import asyncio

from zuno.core.graphs.domain_qa_graph import DomainQAGraph


def test_domain_qa_graph_builds_initial_state():
    graph = DomainQAGraph()
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review this contract",
        knowledge_ids=["k1"],
        domain_pack_id="contract_review",
    )
    assert state["domain_pack_id"] == "contract_review"
    assert state["rewritten_queries"] == ["review this contract"]
    assert state["status"] == "pending"
    assert state["failure_metadata"] is None


def test_domain_qa_graph_appends_trace():
    graph = DomainQAGraph()
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review this contract",
    )
    updated = graph.append_trace(state, node="resolve_domain_pack", payload={"domain_pack_id": "contract_review"})
    assert updated["trace_metadata"]["nodes"][0]["node"] == "resolve_domain_pack"


def test_domain_qa_graph_ainvoke_runs_retrieval_and_formats_answer():
    async def fake_retrieval_runner(**kwargs):
        return {
            "actual_mode": "graphrag",
            "first_mode": "graphrag",
            "final_mode": "graphrag",
            "round_count": 1,
            "metadata": {
                "round_count": 1,
                "requested_mode": "graphrag",
                "requested_profile": "contract_review_strict",
                "resolved_profile": "contract_review_strict",
                "fallback_triggered": False,
                "scope_policy": {"status": "active", "knowledge_ids": ["kb_1"]},
                "index_version": {"vector": "vector_v2", "graph": "graph_v2"},
                "index_health": {"vector": "ready", "graph": "ready"},
            },
            "final_pass_result": {
                "documents": [
                    {
                        "chunk_id": "chunk_1",
                        "file_name": "contract.md",
                        "knowledge_id": "kb_1",
                        "content": "Termination clause requires 30 days written notice.",
                    }
                ],
                "paths": ["Termination Clause -> Notice Period"],
                "structured_paths": [{"source": "Termination Clause", "target": "Notice Period", "chunk_ids": ["chunk_1"]}],
            },
            "graph_result": {
                "paths": ["Termination Clause -> Notice Period"],
                "structured_paths": [{"source": "Termination Clause", "target": "Notice Period", "chunk_ids": ["chunk_1"]}],
            },
            "content": "Termination clause requires 30 days written notice.",
        }

    graph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review termination risk",
        knowledge_ids=["kb_1"],
        domain_pack_id="contract_review",
        runtime_settings={
            "knowledge_status": "active",
            "knowledge_config": {
                "retrieval_settings": {"default_mode": "graphrag"},
                "index_settings": {"index_version": "vector_v2", "status": "active", "health_status": "ready"},
                "graph_index_settings": {"index_version": "graph_v2", "health_status": "ready"},
            },
        },
        domain_pack={
            "id": "contract_review",
            "answer_template_text": "# Contract Review Answer Template",
            "report_template_text": "# Contract Review Report Template",
            "retrieval_policy_data": {"graph_hop_limit": 2},
        },
    )

    result = asyncio.run(graph.ainvoke(state))

    assert result["domain_pack_id"] == "contract_review"
    assert "Termination clause requires 30 days written notice." in result["final_answer"]
    assert result["citations"][0]["chunk_id"] == "chunk_1"
    assert result["graph_paths"][0]["source"] == "Termination Clause"
    assert result["cost_metadata"]["used_domain_pack"] is True
    assert result["trace_metadata"]["nodes"][-1]["node"] == "finalize"
    assert result["trace_metadata"]["nodes"][4]["node"] == "plan_retrieval"
    assert result["trace_metadata"]["nodes"][4]["payload"]["requested_profile"] == "auto"
    assert result["trace_metadata"]["nodes"][4]["payload"]["resolved_profile"] == "vector_rerank"
    assert result["trace_metadata"]["nodes"][5]["node"] == "retrieve_evidence"
    assert result["trace_metadata"]["nodes"][5]["payload"]["round_count"] == 1
    assert result["trace_metadata"]["nodes"][5]["payload"]["retriever_runs"][0]["mode"] == "graphrag"
    assert result["support_verdict"]["status"] == "supported"
    assert result["evidence_bundle"]["citation_count"] == 1
    assert result["status"] == "completed"
    assert [node["node"] for node in result["trace_metadata"]["nodes"][:7]] == [
        "load_agent_config",
        "resolve_domain_pack",
        "route_intent",
        "rewrite_query",
        "plan_retrieval",
        "retrieve_evidence",
        "fuse_evidence",
    ]


def test_domain_qa_graph_citation_check_deduplicates_citations():
    async def fake_retrieval_runner(**kwargs):
        return {
            "actual_mode": "graphrag",
            "first_mode": "graphrag",
            "final_mode": "graphrag",
            "round_count": 1,
            "metadata": {"round_count": 1},
            "final_pass_result": {
                "documents": [
                    {
                        "chunk_id": "chunk_1",
                        "file_name": "contract.md",
                        "knowledge_id": "kb_1",
                        "content": "Termination clause requires 30 days written notice.",
                    },
                    {
                        "chunk_id": "chunk_1",
                        "file_name": "contract.md",
                        "knowledge_id": "kb_1",
                        "content": "Termination clause requires 30 days written notice.",
                    },
                ],
                "paths": [],
                "structured_paths": [],
            },
            "graph_result": {"paths": [], "structured_paths": []},
            "content": "Termination clause requires 30 days written notice.",
        }

    graph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review termination risk",
        knowledge_ids=["kb_1"],
        domain_pack_id="contract_review",
    )

    result = asyncio.run(graph.ainvoke(state))

    assert len(result["citations"]) == 1
    assert result["trace_metadata"]["nodes"][-2]["node"] == "citation_check"


def test_domain_qa_graph_ainvoke_records_failure_node_and_finalizes():
    async def failing_retrieval_runner(**kwargs):
        raise RuntimeError("retrieval backend unavailable")

    graph = DomainQAGraph(retrieval_runner=failing_retrieval_runner)
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review termination risk",
        knowledge_ids=["kb_1"],
        domain_pack_id="contract_review",
    )

    result = asyncio.run(graph.ainvoke(state))

    assert result["status"] == "failed"
    assert result["failure_metadata"]["node"] == "retrieve_evidence"
    assert "retrieval backend unavailable" in result["failure_metadata"]["error"]
    assert "retrieve_evidence" in result["final_answer"]
    assert result["cost_metadata"]["failed_node"] == "retrieve_evidence"
    assert result["trace_metadata"]["nodes"][-1]["node"] == "finalize"
