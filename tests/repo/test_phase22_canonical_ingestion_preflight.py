"""Tests for the PHASE22 canonical ingestion preflight (read-only checker).

Each test builds a synthetic repo tree under ``tmp_path`` and runs the
preflight against it.  The preflight never imports production code, never
touches the network, and never writes outside the supplied repo root.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_REL = "tools/scripts/phase22_canonical_ingestion_preflight.py"


def _load_preflight():
    script_path = REPO_ROOT / SCRIPT_REL
    spec = importlib.util.spec_from_file_location(
        "phase22_canonical_ingestion_preflight", script_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PREFLIGHT = _load_preflight()


def _write(repo_root: Path, rel: str, content: str) -> None:
    path = repo_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


READY_MODULES: dict[str, str] = {
    "src/backend/zuno/knowledge/ingestion/production_runtime.py": (
        "class PackageAProductionIngestionRuntime:\n"
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
    "src/backend/zuno/platform/storage/object_store.py": "class MinioObjectStore:\n    pass\n",
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
    "database:\n"
    "  url: 'postgresql://localhost/zuno'\n"
    "rag:\n"
    "  elasticsearch:\n"
    "    hosts: 'http://127.0.0.1:9200'\n"
    "  vector_db:\n"
    "    host: '127.0.0.1'\n"
    "    port: '19530'\n"
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


def _run(repo_root: Path):
    return PREFLIGHT.run_preflight(repo_root)


def test_ready_case_reports_ready(tmp_path: Path):
    _build_ready_repo(tmp_path)
    result = _run(tmp_path)
    assert result.verdict == "READY_FOR_CANONICAL_INGESTION"
    assert result.gaps == []


def test_missing_adapter_blocks_with_exact_gap(tmp_path: Path):
    _build_ready_repo(tmp_path)
    _write(
        tmp_path,
        "src/backend/zuno/knowledge/indexing/adapters.py",
        "class ElasticsearchBm25IndexClient:\n    pass\n"
        "class Neo4jGraphIndexClient:\n    pass\n",
    )
    result = _run(tmp_path)
    assert result.verdict == "BLOCKED_WITH_EXACT_GAP"
    gap = next(g for g in result.gaps if g.dependency == "milvus adapter")
    assert "MilvusVectorIndexClient" in gap.reason


def test_missing_credential_blocks_with_exact_gap(tmp_path: Path):
    _build_ready_repo(tmp_path)
    _write(
        tmp_path,
        PREFLIGHT.CONFIG_EXAMPLE_REL,
        "database:\n"
        "  url: 'postgresql://localhost/zuno'\n"
        "rag:\n"
        "  elasticsearch:\n"
        "    hosts: 'http://127.0.0.1:9200'\n"
        "neo4j:\n"
        "  uri: 'bolt://localhost:7687'\n",
    )
    result = _run(tmp_path)
    assert result.verdict == "BLOCKED_WITH_EXACT_GAP"
    gap = next(g for g in result.gaps if g.dependency == "milvus adapter")
    assert "credential not declared" in gap.reason
    assert "rag.vector_db" in gap.reason


def test_non_unique_owner_blocks_with_exact_gap(tmp_path: Path):
    _build_ready_repo(tmp_path)
    _write(
        tmp_path,
        "src/backend/zuno/knowledge/storage/local_object_store.py",
        "class LocalObjectStore:\n    pass\n",
    )
    result = _run(tmp_path)
    assert result.verdict == "BLOCKED_WITH_EXACT_GAP"
    gap = next(g for g in result.gaps if g.dependency == "object store")
    assert "non-unique" in gap.reason
    assert "MinioObjectStore" in gap.detail
    assert "LocalObjectStore" in gap.detail


def test_missing_snapshot_activation_entrypoint_blocks(tmp_path: Path):
    _build_ready_repo(tmp_path)
    _write(
        tmp_path,
        "src/backend/zuno/knowledge/ingestion/handoff.py",
        "class SnapshotHandoffRuntime:\n"
        "    def create_snapshot(self, *, document):\n        ...\n",
    )
    result = _run(tmp_path)
    assert result.verdict == "BLOCKED_WITH_EXACT_GAP"
    gap = next(g for g in result.gaps if g.dependency == "snapshot activation owner")
    assert "dispatch_outbox" in gap.reason


def test_real_repo_preflight_is_read_only_and_prints_verdict():
    """Runs against the actual tree: verdict is exactly one of the two strings."""
    result = _run(REPO_ROOT)
    assert result.verdict in ("READY_FOR_CANONICAL_INGESTION", "BLOCKED_WITH_EXACT_GAP")
    checked = {spec.name for spec in PREFLIGHT.DEPENDENCIES}
    gap_deps = {gap.dependency for gap in result.gaps}
    assert gap_deps <= checked
    assert checked - gap_deps
