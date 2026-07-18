from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_complete_infrastructure.py"
SMOKE_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_real_services_smoke.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase04_complete_infrastructure", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_real_services_smoke_passes_against_running_docker_services() -> None:
    spec = spec_from_file_location("verify_phase04_real_services_smoke", SMOKE_VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.verify_phase04_real_services_smoke() == []


def test_phase04_complete_infrastructure_is_fail_closed_until_full_proof() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase04_complete_infrastructure())
    assert "PHASE04 coordinator approval is not approved" in errors
    assert "PHASE05 start gate remains closed" in errors
    assert "PHASE04 evidence missing completion proof marker: backup_restore_replay: proven" in errors
    assert "PHASE04 evidence missing completion proof marker: combined_dependency_fault: proven" in errors


def test_phase04_partial_evidence_remains_withdrawn() -> None:
    text = (REPO_ROOT / "docs" / "evidence" / "phase04-postgres-foundation.md").read_text(
        encoding="utf-8"
    )
    assert "partial_implementation_available" in text
    assert "phase_completion: `withdrawn`" in text
