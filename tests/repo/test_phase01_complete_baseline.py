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
    assert "P01-T02 is not completed in phase-readiness.yaml" in errors
    assert "P01-T06 is not completed in phase-readiness.yaml" in errors
    assert "P01-T05 is not completed in phase-readiness.yaml" not in errors


def test_phase01_requirement_ledger_still_lacks_bidirectional_evidence() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase01_complete_baseline())
    assert "requirement ledger entries missing reviewer" in errors
    assert "requirement ledger entries missing reverse_trace_refs" in errors
    assert "requirement ledger entries with empty test_ids" in errors
    assert "requirement ledger entries with empty evidence_refs" in errors

def test_p01_t05_legacy_bypass_inventory_and_evidence_are_registered() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase01_complete_baseline())
    assert "P01-T05 legacy paths missing from PHASE02 temporary allowlist" not in errors
    assert "PHASE02 temporary allowlist has paths not in P01-T05 inventory" not in errors
    assert "P01-T05 legacy inventory missing bypass categories" not in errors
    assert "P01-T05 legacy inventory still has placeholder current_callers" not in errors
    assert "P01-T05 evidence missing" not in errors
    assert "P01-T05 evidence missing reproducibility field" not in errors


def test_p01_t01_runtime_inventory_has_required_contract_fields() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase01_complete_baseline())
    assert "P01-T01 runtime inventory missing required field row" not in errors
    assert "P01-T01 runtime inventory missing required coverage" not in errors
    assert "P01-T01 evidence file missing" not in errors
    assert "P01-T01 evidence missing required field" not in errors
