from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase11_ingestion_source_lineage.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase11_ingestion_source_lineage", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase11_ingestion_source_lineage_schema_is_explicit() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase11_ingestion_source_lineage() == []
