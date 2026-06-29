from __future__ import annotations

import asyncio
from types import SimpleNamespace


def test_trace_event_schema_and_artifact_manifest_are_reproducible() -> None:
    from zuno.knowledge.trace import (
        EvidenceChecker,
        HookPoint,
        RuntimeTraceBuilder,
        TraceArtifactManifest,
    )

    builder = RuntimeTraceBuilder(trace_id="trace-phase07", product_mode="enhanced")
    builder.record(
        HookPoint.PRE_RETRIEVAL,
        status="started",
        refs={"input": ["query:contract-risk"]},
        metadata={"query_method": "local"},
    )
    builder.record(
        HookPoint.POST_TOOL,
        status="completed",
        refs={"tool": ["Knowledge:search_knowledge_base"]},
        metadata={"latency_ms": 12},
    )

    verdict = EvidenceChecker().evaluate(
        product_mode="enhanced",
        evidence_bundle={
            "document_count": 1,
            "chunk_ids": ["chunk-1"],
            "citation_chunks": ["chunk-1"],
            "citation_coverage": 1.0,
        },
        citations=["chunk-1"],
        fallback_reason=None,
    )
    manifest = TraceArtifactManifest.from_trace(
        trace_id="trace-phase07",
        query="contract risk",
        answer="supported answer",
        documents=[{"chunk_id": "chunk-1", "file_name": "contract.md"}],
        evidence_bundle={"chunk_ids": ["chunk-1"], "citation_chunks": ["chunk-1"]},
        citations=["chunk-1"],
        events=builder.events,
        evidence_verdict=verdict,
        fallback_reason=None,
    )

    payload = manifest.to_dict()

    assert tuple(event.kind for event in builder.events) == (
        HookPoint.PRE_RETRIEVAL,
        HookPoint.POST_TOOL,
    )
    assert builder.events[0].event_id == "trace-phase07:0001:pre_retrieval"
    assert verdict.status == "pass"
    assert payload["trace_id"] == "trace-phase07"
    assert payload["input_refs"] == ["query:contract-risk"]
    assert payload["retrieval_refs"] == ["chunk-1"]
    assert payload["tool_refs"] == ["Knowledge:search_knowledge_base"]
    assert payload["evidence_refs"] == ["chunk-1"]
    assert payload["output_refs"] == ["answer:trace-phase07"]
    assert payload["event_ids"] == [
        "trace-phase07:0001:pre_retrieval",
        "trace-phase07:0002:post_tool",
    ]


def test_evidence_checker_low_confidence_records_fallback_reason() -> None:
    from zuno.knowledge.trace import EvidenceChecker

    verdict = EvidenceChecker(citation_coverage_threshold=0.75).evaluate(
        product_mode="enhanced",
        evidence_bundle={
            "document_count": 2,
            "chunk_ids": ["chunk-1", "chunk-2"],
            "citation_chunks": ["chunk-1"],
            "citation_coverage": 0.5,
        },
        citations=["chunk-1"],
        fallback_reason=None,
    )

    assert verdict.status == "low_confidence"
    assert verdict.fallback_reason == "citation_coverage_below_threshold"
    assert verdict.citation_coverage == 0.5
    assert verdict.document_count == 2
    assert verdict.details["threshold"] == 0.75


def test_enhanced_query_result_adds_hook_trace_verdict_and_manifest() -> None:
    from zuno.services.graphrag.query_service import (
        GraphRAGProjectSnapshot,
        GraphRAGQueryService,
    )

    class FakeOrchestrator:
        async def run(self, mode, query, knowledge_ids, retrieval_options=None):
            del mode, knowledge_ids, retrieval_options
            return {
                "content": "Answer with weak support.",
                "metadata": {
                    "trace_id": "trace-enhanced-1",
                    "requested_product_mode": "enhanced",
                    "resolved_product_mode": "enhanced",
                    "requested_query_method": "local",
                    "resolved_query_method": "local",
                    "router_decision": "enhanced_local",
                    "fallback_reason": None,
                    "evidence_bundle": {
                        "document_count": 2,
                        "chunk_ids": ["chunk-1", "chunk-2"],
                        "citation_chunks": ["chunk-1"],
                        "citation_coverage": 0.5,
                    },
                    "citation_chunks": ["chunk-1"],
                    "retrievers_used": ["vector", "graph"],
                },
                "final_pass_result": {
                    "documents": [
                        {"chunk_id": "chunk-1", "file_name": "contract-a.md"},
                        {"chunk_id": "chunk-2", "file_name": "contract-b.md"},
                    ]
                },
            }

    service = GraphRAGQueryService(orchestrator=FakeOrchestrator())
    result = asyncio.run(
        service.query(
            query="Explain the contract risk",
            knowledge_ids=["kb-1"],
            snapshot=GraphRAGProjectSnapshot(
                graphrag_project_id="project-1",
                contract={"query_method": "local"},
                index_health={"graph": "ready", "community": "ready"},
                knowledge_capability="rag_graph",
            ),
            product_mode="enhanced",
            query_method="local",
        )
    )

    trace = result.trace_metadata

    assert result.fallback_reason == "citation_coverage_below_threshold"
    assert trace["evidence_verdict"]["status"] == "low_confidence"
    assert trace["evidence_verdict"]["fallback_reason"] == "citation_coverage_below_threshold"
    assert [event["kind"] for event in trace["runtime_trace_events"]] == [
        "pre_retrieval",
        "post_retrieval",
        "post_answer",
    ]
    assert trace["artifact_manifest"]["trace_id"] == "trace-enhanced-1"
    assert trace["artifact_manifest"]["retrieval_refs"] == ["chunk-1", "chunk-2"]
    assert trace["artifact_manifest"]["evidence_refs"] == ["chunk-1"]
    assert trace["artifact_manifest"]["output_refs"] == ["answer:trace-enhanced-1"]
    assert trace["pipeline_trace"]["steps"][-1]["name"] == "artifact_manifest"


def test_tool_middleware_emits_pre_and_post_tool_trace_events(monkeypatch) -> None:
    from langchain_core.messages import ToolMessage

    from zuno.core.agents.general_agent import EmitEventAgentMiddleware

    emitted = []
    monkeypatch.setattr(
        "zuno.core.agents.general_agent.get_stream_writer",
        lambda: emitted.append,
    )
    middleware = EmitEventAgentMiddleware(
        name_resolver_func=lambda _name: ("Tool", "Search Knowledge"),
        mcp_checker=lambda _name: False,
        mcp_id_resolver=lambda _name: None,
        user_id="u_1",
    )
    request = SimpleNamespace(
        tool_call={"id": "call_1", "name": "search_knowledge_base", "args": {}}
    )

    async def handler(_request):
        return ToolMessage(
            content="tool result",
            name="search_knowledge_base",
            tool_call_id="call_1",
        )

    result = asyncio.run(middleware.awrap_tool_call(request, handler))

    assert result.content == "tool result"
    assert [event["status"] for event in emitted] == ["START", "END"]
    assert [event["runtime_trace_event"]["kind"] for event in emitted] == [
        "pre_tool",
        "post_tool",
    ]
    assert emitted[0]["runtime_trace_event"]["event_id"] == "tool-call_1:0001:pre_tool"
    assert emitted[1]["runtime_trace_event"]["event_id"] == "tool-call_1:0002:post_tool"
    assert emitted[1]["runtime_trace_event"]["refs"]["tool"] == ["search_knowledge_base"]
