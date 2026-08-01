from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_PHASE22 = REPO_ROOT / "tools" / "scripts" / "verify_phase22_cleanup_boundary.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase22_cleanup_boundary", VERIFY_PHASE22)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase22_cleanup_boundary_is_machine_verifiable() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase22_cleanup_boundary() == []
