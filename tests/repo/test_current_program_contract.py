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


def test_current_program_baseline_manifest_is_machine_verifiable() -> None:
    verifier = _load_verifier()
    assert verifier.verify_current_program() == []


def test_closure_manifest_does_not_promote_blocked_measurement() -> None:
    verifier = _load_verifier()
    manifest = verifier.load_manifest()

    assert manifest["state"] == "no-active"
    assert manifest["implementation_status"] == "implementation_complete"
    assert manifest["measurement_status"] == "measurement_blocked"
    assert manifest["quality_gate_status"] == "quality_not_proven"
    assert manifest["blocked_reason"] == "enterprise_rag_sample8_external_db_unavailable_and_agentic_profile_incomplete"


def test_closure_archive_is_tracked() -> None:
    verifier = _load_verifier()
    manifest = verifier.load_manifest()

    assert manifest["archive"] == "docs/history/programs/zuno-real-unified-runtime-cutover-v1/"
    assert (REPO_ROOT / manifest["archive"] / "closure-summary.md").exists()
