from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_backup_service_boundaries.py"
)


def _load_verifier():
    spec = spec_from_file_location("verify_phase04_backup_service_boundaries", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_backup_scope_and_service_boundaries_are_explicit() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase04_backup_service_boundaries() == []
