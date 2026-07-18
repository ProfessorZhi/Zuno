from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_tenant_physical_constraints.py"
)


def _module():
    spec = spec_from_file_location(
        "verify_phase04_tenant_physical_constraints", VERIFIER
    )
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_tenant_physical_constraints() -> None:
    module = _module()

    assert module.verify_phase04_tenant_physical_constraints() == []


def test_target_only_services_are_not_promoted_to_physical_runtime() -> None:
    module = _module()

    for service_kind in {
        "CHECKPOINT",
        "VECTOR",
        "GRAPH",
        "LEXICAL",
        "CACHE",
        "SECRET_KMS",
    }:
        tenant_profile = module._tenant_profile(service_kind)

        assert tenant_profile.current_runtime_status != "PROVEN"
