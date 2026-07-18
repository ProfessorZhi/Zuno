from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
from pydantic import ValidationError

from zuno.platform.contracts import ReleaseManifestV1, canonical_sha256

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_release_provenance_manifest.py"
)


def _module():
    spec = spec_from_file_location("verify_phase04_release_provenance", VERIFIER)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_release_provenance_manifest() -> None:
    module = _module()

    assert module.verify_phase04_release_provenance_manifest() == []


def test_release_manifest_rejects_self_rollback_ref() -> None:
    module = _module()
    manifest = module._release_manifest()
    payload = manifest.hash_inputs()
    payload["rollback_release_ref"] = payload["release_id"]
    payload["content_hash"] = canonical_sha256(payload)

    with pytest.raises(ValidationError):
        ReleaseManifestV1(**payload)
