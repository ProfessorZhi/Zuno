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


def test_active_program_manifest_preserves_status_boundary() -> None:
    verifier = _load_verifier()
    manifest = verifier.load_manifest()
    assert manifest["state"] == "active"
    assert manifest["current_phase"] == "PHASE03"
    assert manifest["phase_count"] == 22
    assert manifest["atomic_task_count"] == 163
    assert manifest["measurement_status"] == "measurement_blocked"
    assert manifest["quality_gate_status"] == "quality_not_proven"


def test_program_has_all_phase_files_and_atomic_tasks() -> None:
    verifier = _load_verifier()
    assert len(verifier.PHASE_FILES) == 22
    task_count = 0
    for phase_file in verifier.PHASE_FILES:
        text = (verifier.PROGRAM_ROOT / phase_file).read_text(encoding="utf-8")
        import re
        task_count += len(set(re.findall(r"P\d{2}-T\d{2}", text)))
    assert task_count == 163


def test_program_requires_legacy_free_final_source_tree() -> None:
    directory_contract = (REPO_ROOT / ".agent/programs/canonical-directory-contract.md").read_text(
        encoding="utf-8"
    )
    phase22 = (
        REPO_ROOT / ".agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md"
    ).read_text(encoding="utf-8")
    assert "生产源码零 legacy 目录" in directory_contract
    assert "零 legacy alias registry" in directory_contract
    assert "Legacy-free Canonical Directory Cleanup" in phase22
    assert "生产源码树零 Legacy 文件夹" in phase22
