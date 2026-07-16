from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_complete_infrastructure.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase04_complete_infrastructure", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_complete_infrastructure_is_fail_closed_without_real_services() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase04_complete_infrastructure())
    assert "PHASE04 coordinator approval is not approved" in errors
    assert "PHASE05 start gate remains closed" in errors
    assert "PostgreSQL real service is not reachable" in errors
    assert "RabbitMQ real service is not reachable" in errors
    assert "MinIO/S3 real service is not reachable" in errors


def test_phase04_partial_evidence_remains_withdrawn() -> None:
    text = (REPO_ROOT / "docs" / "evidence" / "phase04-postgres-foundation.md").read_text(
        encoding="utf-8"
    )
    assert "partial_implementation_available" in text
    assert "phase_completion: `withdrawn`" in text
