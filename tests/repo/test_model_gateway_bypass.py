from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_model_gateway_bypass.py"


def _load_verifier():
    spec = spec_from_file_location("verify_model_gateway_bypass", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_model_gateway_bypass_inventory_is_locked_until_cutover() -> None:
    verifier = _load_verifier()
    assert verifier.verify_model_gateway_bypass(strict=False) == []


def test_model_gateway_bypass_strict_mode_documents_current_blocker() -> None:
    verifier = _load_verifier()
    errors = verifier.verify_model_gateway_bypass(strict=True)
    assert errors
    assert any("provider SDK bypass remains" in error for error in errors)
