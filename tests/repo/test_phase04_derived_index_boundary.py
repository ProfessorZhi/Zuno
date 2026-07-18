from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_derived_index_boundary.py"


def _module():
    spec = spec_from_file_location("verify_phase04_derived_index_boundary", VERIFIER)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_derived_index_boundary() -> None:
    module = _module()

    assert module.verify_phase04_derived_index_boundary() == []


def test_derived_indexes_are_not_required_release_adapters() -> None:
    module = _module()
    release_provenance = module._load_module(
        module.RELEASE_PROVENANCE_VERIFIER,
        "verify_phase04_release_provenance_manifest",
    )
    manifest = release_provenance._release_manifest()
    forbidden = {"milvus", "neo4j", "bm25", "lexical", "search"}

    assert forbidden.isdisjoint(release_provenance.REQUIRED_INFRA_SERVICES)
    assert all(
        not any(service in version.lower() for service in forbidden)
        for version in manifest.adapter_versions
    )
