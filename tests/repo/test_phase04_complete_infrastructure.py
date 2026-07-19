from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_complete_infrastructure.py"
PRE_CLOSURE_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_pre_closure_gate.py"
POST_CLOSURE_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_post_closure_consistency.py"
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


def test_phase04_pre_and_post_closure_gates_pass_after_coordinator_closure() -> None:
    for path, module_name, function_name in [
        (
            PRE_CLOSURE_VERIFIER,
            "verify_phase04_pre_closure_gate",
            "verify_phase04_pre_closure_gate",
        ),
        (
            POST_CLOSURE_VERIFIER,
            "verify_phase04_post_closure_consistency",
            "verify_phase04_post_closure_consistency",
        ),
    ]:
        spec = spec_from_file_location(module_name, path)
        assert spec is not None
        assert spec.loader is not None
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        assert getattr(module, function_name)() == []


def test_phase04_partial_evidence_remains_withdrawn() -> None:
    text = (REPO_ROOT / "docs" / "evidence" / "phase04-postgres-foundation.md").read_text(
        encoding="utf-8"
    )
    assert "partial_implementation_available" in text
    assert "phase_completion: `withdrawn`" in text
