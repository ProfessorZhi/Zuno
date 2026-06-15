import asyncio
import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_backend_root() -> None:
    backend_root = str(BACKEND_ROOT)
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)


def test_phase1_domain_qa_state_declares_required_runtime_fields() -> None:
    _ensure_backend_root()

    state_module = importlib.import_module("zuno.core.graphs.states")
    domain_state = state_module.DomainQAState
    annotations = domain_state.__annotations__

    required_fields = {
        "retrieval_plan",
        "retrieval_rounds",
        "retriever_runs",
        "evidence_bundle",
        "evidence_quality",
        "fallback_decision",
        "support_verdict",
        "citations",
        "trace_metadata",
        "failure_metadata",
        "status",
    }

    missing = required_fields.difference(annotations)
    assert not missing, missing


def test_phase1_domain_qa_graph_exposes_required_node_boundaries() -> None:
    _ensure_backend_root()

    graph_module = importlib.import_module("zuno.core.graphs.domain_qa_graph")
    content = Path(graph_module.__file__).read_text(encoding="utf-8")

    required_nodes = [
        "load_agent_config",
        "resolve_domain_pack",
        "route_intent",
        "rewrite_query",
        "plan_retrieval",
        "retrieve_evidence",
        "fuse_evidence",
        "verify_evidence",
        "maybe_retry_or_fallback",
        "generate_answer",
        "citation_check",
        "finalize",
    ]

    for node_name in required_nodes:
        assert node_name in content, node_name


def test_phase1_agent_runtime_routes_single_agent_flow_through_domain_qa_graph() -> None:
    _ensure_backend_root()

    AgentRuntime = importlib.import_module("zuno.core.runtime.agent_runtime").AgentRuntime

    events: list[str] = []

    class FakeDomainGraph:
        def build_initial_state(self, **kwargs):
            events.append("build_initial_state")
            return {"built": True, **kwargs}

        async def ainvoke(self, state):
            events.append("ainvoke")
            return {"status": "completed", "state": state}

    runtime = AgentRuntime(graph=FakeDomainGraph(), multi_agent_graph=None)
    result = asyncio.run(
        runtime.run_domain_qa(
            user_id="u1",
            agent_id="a1",
            dialog_id="d1",
            query="合同里甲方什么时候可以解除？",
            knowledge_ids=["kb1"],
            runtime_settings={"knowledge_config": {"retrieval_settings": {}}},
            domain_pack={"id": "contract_review"},
        )
    )

    assert result["status"] == "completed"
    assert events == ["build_initial_state", "ainvoke"]


def test_phase1_domain_qa_graph_failure_always_reaches_finalize() -> None:
    _ensure_backend_root()

    DomainQAGraph = importlib.import_module("zuno.core.graphs.domain_qa_graph").DomainQAGraph

    async def fake_retrieval_runner(**kwargs):
        raise RuntimeError("backend retrieval unavailable")

    graph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="合同里甲方什么时候可以解除？",
        knowledge_ids=["kb1"],
        domain_pack_id="contract_review",
    )

    result = asyncio.run(graph.ainvoke(state))

    assert result["status"] == "failed"
    assert result["trace_metadata"]["nodes"][-1]["node"] == "finalize"
