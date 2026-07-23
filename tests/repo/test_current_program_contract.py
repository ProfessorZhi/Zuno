from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_CURRENT_PROGRAM = REPO_ROOT / "tools" / "scripts" / "verify_current_program.py"


def _load_verifier():
    spec = spec_from_file_location("verify_current_program", VERIFY_CURRENT_PROGRAM)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_active_program_is_machine_verifiable() -> None:
    verifier = _load_verifier()
    assert verifier.verify_current_program() == []


def test_active_program_manifest_preserves_current_status_boundary() -> None:
    verifier = _load_verifier()
    manifest = verifier.load_manifest()
    assert manifest["state"] == "active"
    assert manifest["current_phase"] == "PHASE09"
    assert manifest["phase_count"] == 22
    assert manifest["atomic_task_count"] == 163
    assert manifest["measurement_status"] == "measurement_blocked"
    assert manifest["quality_gate_status"] == "quality_not_proven"


def test_phase_states_reflect_goal02_phase11_closure() -> None:
    program_root = REPO_ROOT / ".agent" / "programs"
    expected = {
        "PHASE04_postgres-domain-and-transaction-foundation.md": "status: completed",
        "PHASE05_security-control-plane.md": "status: completed",
        "PHASE06_observability-minimum-black-box.md": "status: completed",
        "PHASE07_model-gateway-runtime.md": "status: completed",
        "PHASE08_deterministic-single-controller-runtime.md": "status: completed",
        "PHASE09_product-surface-backend-runtime.md": "status: ready",
        "PHASE11_durable-ingestion-and-source-lineage.md": "status: completed",
        "PHASE12_knowledge-version-and-standard-rag.md": "status: ready",
    }
    for filename, state in expected.items():
        text = (program_root / filename).read_text(encoding="utf-8")
        assert state in text

    manifest = (program_root / "program-manifest.yaml").read_text(encoding="utf-8")
    assert "minimum_vertical_slice_is_phase_completion: false" in manifest
    assert "id: PHASE08, file: .agent/programs/PHASE08_deterministic-single-controller-runtime.md, state: completed" in manifest
    assert "id: PHASE09, file: .agent/programs/PHASE09_product-surface-backend-runtime.md, state: ready" in manifest
    assert "id: PHASE11, file: .agent/programs/PHASE11_durable-ingestion-and-source-lineage.md, state: completed" in manifest
    assert "id: PHASE12, file: .agent/programs/PHASE12_knowledge-version-and-standard-rag.md, state: ready" in manifest


def test_goal02_repair_reopens_phase08_and_phase11_without_implementing_downstream() -> None:
    readiness = (
        REPO_ROOT / ".agent/programs/work-products/phase11-readiness.yaml"
    ).read_text(encoding="utf-8")
    current = (REPO_ROOT / ".agent/programs/current.md").read_text(encoding="utf-8")
    production = (REPO_ROOT / "docs/status/production-readiness.md").read_text(
        encoding="utf-8"
    )

    assert "current_phase_status: completed" in readiness
    assert "coordinator_approval: approved" in readiness
    assert "target_not_current: 0" in readiness
    assert "PHASE08 completed" in current
    assert "PHASE11 completed" in current
    assert "PHASE09 ready" in current
    assert "PHASE12 ready" in current
    assert "PHASE11 completed" in production


def test_program_has_all_phase_files_and_atomic_tasks() -> None:
    verifier = _load_verifier()
    assert len(verifier.PHASE_FILES) == 22
    task_count = 0
    for phase_file in verifier.PHASE_FILES:
        text = (verifier.PROGRAM_ROOT / phase_file).read_text(encoding="utf-8")
        import re

        task_count += len(set(re.findall(r"P\d{2}-T\d{2}", text)))
    assert task_count == 163
