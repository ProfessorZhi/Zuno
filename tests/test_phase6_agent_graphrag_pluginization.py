import asyncio
import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    runtime_root = str(BACKEND_ROOT)
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)


def test_phase6_agent_runtime_can_bind_domain_pack_without_knowledge_runtime_pack(monkeypatch) -> None:
    _ensure_runtime_paths()

    ga = importlib.import_module("zuno.core.agents.general_agent")
    AgentConfig = importlib.import_module("zuno.core.agents.general_agent").AgentConfig
    GeneralAgent = importlib.import_module("zuno.core.agents.general_agent").GeneralAgent

    async def fake_runtime_settings(_knowledge_id):
        return {
            "knowledge_config": {
                "index_capability": "rag_graph",
                "retrieval_settings": {
                    "default_mode": "graphrag",
                    "profile": "auto",
                },
            },
        }

    captured: dict = {}

    async def fake_run_domain_qa(**kwargs):
        captured.update(kwargs)
        return {
            "final_answer": "ok",
            "domain_pack_id": kwargs.get("domain_pack_id"),
            "status": "completed",
        }

    monkeypatch.setattr(ga.KnowledgeService, "get_runtime_settings", fake_runtime_settings)

    agent = GeneralAgent(
        AgentConfig(
            user_id="u_1",
            llm_id="",
            mcp_ids=[],
            knowledge_ids=["kb_contract"],
            domain_pack_id="contract_review",
            retrieval_profile="agent_relation_override",
            eval_profile_id="agent_eval_override",
            graph_capability="rag_graph",
            tool_ids=[],
            agent_skill_ids=[],
            system_prompt="review contract",
            name="contract-agent",
        )
    )
    agent.domain_qa_runtime.run_domain_qa = fake_run_domain_qa

    result = asyncio.run(agent._run_domain_pack_state("这份合同是否约定了违约责任？"))

    assert result["domain_pack_id"] == "contract_review"
    assert captured["domain_pack"]["id"] == "contract_review"
    assert captured["runtime_settings"]["knowledge_config"]["retrieval_settings"]["profile"] == "agent_relation_override"
    assert captured["runtime_settings"]["knowledge_config"]["eval_profile_id"] == "agent_eval_override"
    assert captured["runtime_settings"]["knowledge_config"]["index_capability"] == "rag_graph"


def test_phase6_domain_pack_declares_future_platform_defaults() -> None:
    pack_manifest = (
        REPO_ROOT / "domain-packs" / "contract_review" / "pack.yaml"
    ).read_text(encoding="utf-8")
    phase_doc = (
        REPO_ROOT / "docs" / "architecture" / "phases" / "phase-06-agent-graphrag-pluginization.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "default_retrieval_profile: relation_hybrid",
        "default_eval_profile_id: contract_review_local",
    ]:
        assert phrase in pack_manifest

    for phrase in [
        "Community GraphRAG",
        "DRIFT-like Search",
        "future slots only",
    ]:
        assert phrase in phase_doc
