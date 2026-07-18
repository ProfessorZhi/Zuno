from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_infrastructure_docs_governance.py"
)


def _module():
    spec = spec_from_file_location(
        "verify_phase04_infrastructure_docs_governance", VERIFIER
    )
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_infrastructure_docs_governance() -> None:
    module = _module()

    assert module.verify_phase04_infrastructure_docs_governance() == []


def test_architecture_file_sets_are_canonical() -> None:
    module = _module()

    assert module._architecture_file_set_errors() == []
