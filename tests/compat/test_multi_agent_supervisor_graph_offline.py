import asyncio

from agentchat.core.graphs.multi_agent_supervisor_graph import MultiAgentSupervisorGraph


def test_multi_agent_supervisor_graph_builds_initial_state():
    graph = MultiAgentSupervisorGraph()
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review termination risk",
        knowledge_ids=["kb_1"],
        domain_pack_id="contract_review",
    )
    assert state["domain_pack_id"] == "contract_review"
    assert state["planned_agents"] == []
    assert state["specialist_outputs"] == []
    assert state["status"] == "pending"


def test_multi_agent_supervisor_graph_ainvoke_runs_two_specialists():
    async def fake_domain_qa_runner(state):
        return {
            "status": "completed",
            "vector_contexts": [
                {
                    "chunk_id": "chunk_1",
                    "file_name": "contract.md",
                    "knowledge_id": "kb_1",
                    "content": "Termination clause requires 30 days written notice.",
                }
            ],
            "graph_paths": [
                {
                    "source": "Termination Clause",
                    "target": "Notice Period",
                    "chunk_ids": ["chunk_1"],
                }
            ],
            "citations": [
                {
                    "chunk_id": "chunk_1",
                    "file_name": "contract.md",
                    "knowledge_id": "kb_1",
                },
                {
                    "chunk_id": "chunk_1",
                    "file_name": "contract.md",
                    "knowledge_id": "kb_1",
                },
            ],
            "draft_answer": "Termination clause requires 30 days written notice.",
            "report_markdown": "# Contract Review Report",
            "final_answer": "Termination clause requires 30 days written notice.",
            "evidence_bundle": {
                "items": [
                    {
                        "chunk_id": "chunk_1",
                        "file_name": "contract.md",
                        "knowledge_id": "kb_1",
                        "excerpt": "Termination clause requires 30 days written notice.",
                        "is_cited": True,
                    }
                ],
                "document_count": 1,
                "citation_count": 2,
            },
            "support_verdict": {"status": "supported", "reason": "cited_documents_present"},
        }

    async def fake_citation_verifier_runner(state):
        return {
            "verified_citations": [
                {
                    "chunk_id": "chunk_1",
                    "file_name": "contract.md",
                    "knowledge_id": "kb_1",
                }
            ],
            "verdict": "verified",
        }

    graph = MultiAgentSupervisorGraph(
        domain_qa_runner=fake_domain_qa_runner,
        citation_verifier_runner=fake_citation_verifier_runner,
    )
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review termination risk",
        knowledge_ids=["kb_1"],
        domain_pack_id="contract_review",
    )

    result = asyncio.run(graph.ainvoke(state))

    assert result["status"] == "completed"
    assert result["planned_agents"] == ["domain_qa_specialist", "citation_verifier_specialist"]
    assert len(result["specialist_outputs"]) == 2
    assert result["specialist_outputs"][0]["agent"] == "domain_qa_specialist"
    assert result["specialist_outputs"][1]["agent"] == "citation_verifier_specialist"
    assert len(result["citations"]) == 1
    assert result["support_verdict"]["status"] == "supported"
    assert result["evidence_bundle"]["document_count"] == 1
    assert result["graph_paths"][0]["source"] == "Termination Clause"
    assert result["final_answer"] == "Termination clause requires 30 days written notice."
    assert [node["node"] for node in result["trace_metadata"]["nodes"]] == [
        "plan_specialists",
        "domain_qa_specialist",
        "citation_verifier_specialist",
        "finalize",
    ]
    assert result["cost_metadata"]["planned_agent_count"] == 2
    assert result["cost_metadata"]["specialist_count"] == 2


def test_multi_agent_supervisor_graph_records_failure_and_finalizes():
    async def failing_domain_qa_runner(state):
        raise RuntimeError("domain specialist unavailable")

    graph = MultiAgentSupervisorGraph(domain_qa_runner=failing_domain_qa_runner)
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review termination risk",
    )

    result = asyncio.run(graph.ainvoke(state))

    assert result["status"] == "failed"
    assert result["failure_metadata"]["node"] == "domain_qa_specialist"
    assert "domain specialist unavailable" in result["failure_metadata"]["error"]
    assert "domain_qa_specialist" in result["final_answer"]
    assert result["trace_metadata"]["nodes"][-1]["node"] == "finalize"
