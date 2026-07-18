from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
from pydantic import ValidationError

from zuno.platform.contracts import AdapterConformanceProfileV1, canonical_sha256

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_adapter_conformance_profiles.py"
)


def _module():
    spec = spec_from_file_location("verify_phase04_adapter_conformance", VERIFIER)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_adapter_conformance_profiles() -> None:
    module = _module()

    assert module.verify_phase04_adapter_conformance_profiles() == []


def test_conformance_profile_rejects_non_fail_fast_unsupported_semantics() -> None:
    module = _module()
    capability = module._capabilities(
        module._profile(deployment_class="DEVELOPER_CI", profile_version="phase04.1")
    )["RELATIONAL"]
    profile = module._conformance_profile(
        deployment_class="DEVELOPER_CI",
        capability=capability,
    )
    payload = profile.hash_inputs()
    payload["fail_fast_on_unsupported"] = False
    payload["content_hash"] = canonical_sha256(payload)

    with pytest.raises(ValidationError):
        AdapterConformanceProfileV1(**payload)
