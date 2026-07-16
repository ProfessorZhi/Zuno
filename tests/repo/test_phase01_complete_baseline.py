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
    assert "P01-T04 is not completed in phase-readiness.yaml" in errors


def test_phase01_requirement_ledger_still_lacks_bidirectional_evidence() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase01_complete_baseline())
    assert "requirement ledger entries missing reviewer" in errors
    assert "requirement ledger entries missing reverse_trace_refs" in errors
    assert "requirement ledger entries with empty test_ids" in errors
    assert "requirement ledger entries with empty evidence_refs" in errors


def test_phase01_frontend_desktop_inventory_has_required_contract_matrix() -> None:
    inventory = (
        REPO_ROOT / ".agent/programs/work-products/frontend-current-inventory.md"
    ).read_text(encoding="utf-8")
    evidence = (
        REPO_ROOT / "docs/evidence/phase01-frontend-desktop-inventory.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "page/component exists",
        "contract adopted",
        "generated or machine-checked type",
        "authorized projection",
        "available action",
        "real E2E/smoke evidence",
        "gap/blocker",
        "target phase",
        "SSE resume",
        "reauthorization",
        "multiple Interrupt",
        "UNKNOWN",
        "PHASE10",
        "PHASE21",
    ]:
        assert phrase in inventory

    for phrase in [
        "task_id: P01-T04",
        "artifact hash",
        "Browser E2E",
        "Desktop Smoke",
        "not run",
        "node_modules",
        "AvailableAction",
        "UNKNOWN",
    ]:
        assert phrase in evidence
