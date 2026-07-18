from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_checkpoint_boundary_version.py"
)


def _load_verifier():
    spec = spec_from_file_location(
        "verify_phase04_checkpoint_boundary_version", VERIFIER
    )
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checkpoint_domain_boundary_and_version_fail_closed_are_explicit() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase04_checkpoint_boundary_version() == []
