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


def test_phase4_docs_and_frontend_contract_expose_knowledge_config_v2() -> None:
    phase_doc = (
        REPO_ROOT / "docs" / "architecture" / "history" / "phases" / "phase-04-local-eval-strengthening.md"
    ).read_text(encoding="utf-8")
    api_contract = (REPO_ROOT / "apps" / "web" / "src" / "apis" / "knowledge.ts").read_text(encoding="utf-8")
    utils_contract = (
        REPO_ROOT / "apps" / "web" / "src" / "utils" / "knowledge-config.ts"
    ).read_text(encoding="utf-8")
    backend_schema = (
        REPO_ROOT / "src" / "backend" / "zuno" / "schema" / "knowledge.py"
    ).read_text(encoding="utf-8")

    for phrase in [
        "Knowledge Config V2",
        "Domain Pack binding",
        "eval profile",
        "GraphRAG-vs-RAG proof surfaces",
    ]:
        assert phrase in phase_doc

    for phrase in ["domain_pack_id", "eval_profile_id", "profile", "graph_index_settings"]:
        assert phrase in api_contract
        assert phrase in utils_contract
        assert phrase in backend_schema


def test_phase4_runtime_preserves_domain_pack_id_without_loading_pack(monkeypatch) -> None:
    _ensure_runtime_paths()

    DomainPackLoader = importlib.import_module("zuno.services.domain_pack.loader").DomainPackLoader
    KnowledgeService = importlib.import_module("zuno.api.services.knowledge").KnowledgeService

    def fail_if_loaded(*_args, **_kwargs):
        raise AssertionError("KnowledgeService runtime settings must not load DomainPackLoader")

    monkeypatch.setattr(DomainPackLoader, "load", fail_if_loaded)

    monkeypatch.setattr(
        "zuno.api.services.knowledge.get_local_runtime_settings",
        lambda _knowledge_id: {
            "knowledge_config": {
                "domain_pack_id": "contract_review",
                "retrieval_settings": {"default_mode": "rag_graph", "profile": "auto"},
            },
            "domain_pack_id": "contract_review",
        },
    )

    runtime = asyncio.run(KnowledgeService.get_runtime_settings("kb_phase4"))

    assert runtime["domain_pack_id"] == "contract_review"
    assert runtime["domain_pack"] is None
    assert runtime["knowledge_config"]["graphrag_project_id"] == "contract_review"
    assert runtime["knowledge_config"]["retrieval_settings"]["profile"] == "auto"
    assert runtime["knowledge_config"]["eval_profile_id"] is None

    importlib.import_module("zuno.api.services.knowledge_file")
    importlib.import_module("zuno.services.rag.handler")
    importlib.import_module("zuno.services.graphrag.retriever")
    importlib.import_module("zuno.evals.rag_eval.ingest_prepared_corpus")
