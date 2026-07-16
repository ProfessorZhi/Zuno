from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_PHASE01 = REPO_ROOT / "tools" / "scripts" / "verify_phase01_complete_baseline.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase01_complete_baseline", VERIFY_PHASE01)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase01_complete_baseline_verifier_is_fail_closed() -> None:
    verifier = _load_verifier()
    errors = verifier.verify_phase01_complete_baseline()
    assert errors


def test_phase01_current_partial_outputs_do_not_satisfy_closure_gate() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase01_complete_baseline())
    assert "coordinator approval is not approved" in errors
    assert "PHASE02 start gate remains closed" in errors
    assert "P01-T01 is not completed in phase-readiness.yaml" in errors
    assert "P01-T06 is not completed in phase-readiness.yaml" in errors


def test_phase01_requirement_ledger_has_bidirectional_traceability_fields() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase01_complete_baseline())
    assert "requirement ledger missing source ids" not in errors
    assert "requirement ledger has ids not in sources" not in errors
    assert "requirement_count" not in errors
    assert "requirement ledger entries missing" not in errors
    assert "requirement ledger entries with empty test_ids" not in errors
    assert "requirement ledger entries with empty evidence_refs" not in errors
    assert "requirement ledger entries with empty reverse_trace_refs" not in errors
    assert "requirement ledger target_not_current entries missing" not in errors
