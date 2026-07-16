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


def test_phase01_complete_baseline_verifier_passes_after_coordinator_closure() -> None:
    verifier = _load_verifier()
    errors = verifier.verify_phase01_complete_baseline()
    assert errors == []


def test_phase01_current_outputs_satisfy_closure_gate() -> None:
    verifier = _load_verifier()
    errors = "\n".join(verifier.verify_phase01_complete_baseline())
    assert "coordinator approval is not approved" not in errors
    assert "PHASE02 start gate remains closed" not in errors
    for task_id in ["P01-T01", "P01-T02", "P01-T03", "P01-T04", "P01-T05", "P01-T06"]:
        assert f"{task_id} is not completed in phase-readiness.yaml" not in errors


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


def test_phase01_persistence_inventory_has_required_contract_fields() -> None:
    verifier = _load_verifier()
    inventory = (
        REPO_ROOT / ".agent" / "programs" / "work-products" / "current-persistence-inventory.md"
    ).read_text(encoding="utf-8")
    errors: list[str] = []
    verifier._verify_p01_t02_contract(inventory, errors)
    assert not errors


def test_phase01_persistence_evidence_discloses_not_run_real_dependencies() -> None:
    evidence = (
        REPO_ROOT / "docs" / "evidence" / "phase01-persistence-infrastructure-inventory.md"
    ).read_text(encoding="utf-8")
    for phrase in [
        "Not-Run Real Dependency Checks",
        "RabbitMQ",
        "MinIO/S3",
        "Milvus",
        "Neo4j",
        "Backup / Restore / PITR",
    ]:
        assert phrase in evidence


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
