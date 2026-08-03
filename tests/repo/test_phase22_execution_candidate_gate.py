"""Tests for the controller-owned PHASE22 execution-candidate gate."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_REL = "tools/scripts/phase22_execution_candidate_gate.py"
PREFLIGHT_REL = "tools/scripts/phase22_canonical_ingestion_preflight.py"


def _load_script(rel: str, module_name: str):
    script_path = REPO_ROOT / rel
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GATE = _load_script(SCRIPT_REL, "phase22_execution_candidate_gate")
PREFLIGHT = _load_script(PREFLIGHT_REL, "phase22_canonical_ingestion_preflight_for_gate")


def _write(repo_root: Path, rel: str, content: str) -> None:
    path = repo_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


READY_MODULES: dict[str, str] = {
    "src/backend/zuno/knowledge/ingestion/production_runtime.py": (
        "class PackageAProductionIngestionRuntime:\n"
        "    def __init__(self, *, object_store: DurableMinioObjectStore):\n"
        "        self.object_store = object_store\n"
        "    def accept_workspace_upload(self, command):\n        ...\n"
        "    def confirm_snapshot_handoff_published(self, receipt):\n        ...\n"
    ),
    "src/backend/zuno/knowledge/ingestion/handoff.py": (
        "class SnapshotHandoffRuntime:\n"
        "    def create_snapshot(self, *, document, parse_snapshot):\n        ...\n"
        "    def dispatch_outbox(self, event):\n        ...\n"
    ),
    "src/backend/zuno/platform/database/session.py": "def domain_uow(session):\n    ...\n",
    "src/backend/zuno/platform/database/ingestion/persistence.py": (
        "class IngestionRepository:\n    pass\n"
    ),
    "src/backend/zuno/platform/storage/object_store.py": (
        "class MinioObjectStore:\n    pass\n"
    ),
    "src/backend/zuno/platform/storage/durable.py": (
        "class DurableMinioObjectStore:\n"
        "    def stage(self):\n        ...\n"
        "    def commit(self):\n        ...\n"
        "    def reconcile_committed(self):\n        ...\n"
        "    def read_committed(self):\n        ...\n"
    ),
    "src/backend/zuno/platform/database/foundation.py": (
        "def create_foundation_engine(database_url, **kwargs):\n    ...\n"
    ),
    "src/backend/zuno/knowledge/indexing/adapters.py": (
        "class ElasticsearchBm25IndexClient:\n    pass\n"
        "class MilvusVectorIndexClient:\n    pass\n"
        "class Neo4jGraphIndexClient:\n    pass\n"
    ),
    "src/backend/zuno/platform/model_gateway_adapters.py": (
        "class OpenAIEmbeddingGatewayAdapter:\n    pass\n"
    ),
    "src/backend/zuno/knowledge/indexing/contracts.py": (
        "class IndexQueryResult:\n    pass\n"
        "class IndexJobManifest:\n"
        "    adapter_visibility_receipts: dict = {}\n"
    ),
}

READY_CONFIG = (
    "rag:\n"
    "  elasticsearch:\n"
    "    hosts: 'http://127.0.0.1:9200'\n"
    "  vector_db:\n"
    "    host: '127.0.0.1'\n"
    "neo4j:\n"
    "  uri: 'bolt://localhost:7687'\n"
    "multi_models:\n"
    "  embedding:\n"
    "    api_key: ''\n"
)


def _build_ready_repo(repo_root: Path) -> None:
    for rel, content in READY_MODULES.items():
        _write(repo_root, rel, content)
    _write(repo_root, PREFLIGHT.CONFIG_EXAMPLE_REL, READY_CONFIG)


def test_execution_candidate_requires_pack_and_ready_preflight(tmp_path: Path) -> None:
    _build_ready_repo(tmp_path)

    decision = GATE.evaluate_execution_candidate(repo_root=tmp_path)

    assert decision.status == "execution_candidate"
    assert decision.derivation_pack_status == "legal"
    assert decision.canonical_ingestion_preflight_status == "READY_FOR_CANONICAL_INGESTION"
    assert decision.dependency_status == "DEPENDENCY_COMPATIBLE"


def test_preflight_blocked_fails_closed(tmp_path: Path) -> None:
    _build_ready_repo(tmp_path)
    _write(
        tmp_path,
        "src/backend/zuno/knowledge/indexing/adapters.py",
        "class ElasticsearchBm25IndexClient:\n    pass\n",
    )

    decision = GATE.evaluate_execution_candidate(repo_root=tmp_path)

    assert decision.status == "blocked_with_exact_gap"
    assert decision.derivation_pack_status == "legal"
    assert decision.canonical_ingestion_preflight_status == "BLOCKED_WITH_EXACT_GAP"
    assert decision.dependency_status == "DEPENDENCY_BLOCKED"


def test_invalid_derivation_pack_fails_closed(tmp_path: Path) -> None:
    _build_ready_repo(tmp_path)
    bad_case = dict(GATE.ALL_CASES[0])
    bad_case["expected_answer"] = "Wrong Name"

    decision = GATE.evaluate_execution_candidate(repo_root=tmp_path, cases=(bad_case,))

    assert decision.status == "blocked_with_exact_gap"
    assert decision.derivation_pack_status == "invalid"
    assert decision.canonical_ingestion_preflight_status == "READY_FOR_CANONICAL_INGESTION"


def test_controller_normalizes_worker_preflight_field() -> None:
    decision = GATE.evaluate_execution_candidate(
        preflight_result={"verdict": "READY_FOR_CANONICAL_INGESTION"}
    )

    assert decision.status == "execution_candidate"
    assert decision.canonical_ingestion_preflight_status == "READY_FOR_CANONICAL_INGESTION"
