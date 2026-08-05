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

    # The retired GeneralAgent module (which used to bind the domain pack
    # graph runtime) is gone; the runtime must not be importable.
    try:
        importlib.import_module("zuno.agent.core.agents.general_agent")
    except ModuleNotFoundError:
        pass
    else:
        raise AssertionError("retired GeneralAgent module is importable")

    core_module = importlib.import_module("zuno.agent.core")
    assert "AgentRuntime" not in getattr(core_module, "__all__", [])


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
