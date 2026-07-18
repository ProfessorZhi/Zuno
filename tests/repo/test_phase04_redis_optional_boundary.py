from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_redis_optional_boundary.py"


def _module():
    spec = spec_from_file_location("verify_phase04_redis_optional_boundary", VERIFIER)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_redis_optional_boundary() -> None:
    module = _module()

    assert module.verify_phase04_redis_optional_boundary() == []


def test_redis_is_not_required_release_infrastructure() -> None:
    module = _module()
    release_provenance = module._load_module(
        module.RELEASE_PROVENANCE_VERIFIER,
        "verify_phase04_release_provenance_manifest",
    )
    manifest = release_provenance._release_manifest()

    assert "redis" not in release_provenance.REQUIRED_INFRA_SERVICES
    assert all("redis" not in version.lower() for version in manifest.adapter_versions)
