from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase03_contract_bundle.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase03_contract_bundle", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase03_contract_bundle_verifier_passes() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase03_contract_bundle() == []
