import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    runtime_root = str(BACKEND_ROOT)
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)


def test_phase6_agent_runtime_no_longer_binds_domain_pack_graph_runtime() -> None:
    _ensure_runtime_paths()

    general_agent = importlib.import_module("zuno.core.agents.general_agent")
    GeneralAgent = general_agent.GeneralAgent
    AgentConfig = general_agent.AgentConfig

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

    assert not hasattr(agent, "domain_qa_runtime")
    assert "AgentRuntime" not in vars(general_agent)
    assert "RagHandler" not in vars(general_agent)


def test_phase6_domain_pack_defaults_are_retired_surface_evidence() -> None:
    pack_manifest = (
        REPO_ROOT
        / "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml"
    ).read_text(encoding="utf-8")
    retired_doc = (
        REPO_ROOT
        / "docs"
        / "history"
        / "agent-architecture-decision-fragments"
        / "03-retired-surfaces.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "default_retrieval_profile: relation_hybrid",
        "default_eval_profile_id: contract_review_local",
    ]:
        assert phrase in pack_manifest

    for phrase in [
        "Domain Pack",
        "domain_pack_id -> graphrag_project_id",
        "rag_graph_deep -> enhanced mode + query_method",
    ]:
        assert phrase in retired_doc
