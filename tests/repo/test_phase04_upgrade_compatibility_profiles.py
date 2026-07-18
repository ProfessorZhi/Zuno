from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
from pydantic import ValidationError

from zuno.platform.contracts import UpgradeCompatibilityProfileV1

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_upgrade_compatibility_profiles.py"
)


def _module():
    spec = spec_from_file_location("verify_phase04_upgrade_profiles", VERIFIER)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_upgrade_compatibility_profiles() -> None:
    module = _module()

    assert module.verify_phase04_upgrade_compatibility_profiles() == []


def test_upgrade_profile_rejects_empty_compatibility_window() -> None:
    module = _module()
    capability = module._capabilities(
        module._profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    )["RELATIONAL"]
    profile = module._upgrade_profile(capability)

    with pytest.raises(ValidationError):
        UpgradeCompatibilityProfileV1(
            **{
                **profile.hash_inputs(),
                "read_compatible_adapter_versions": (),
            },
            content_hash=profile.content_hash,
        )
