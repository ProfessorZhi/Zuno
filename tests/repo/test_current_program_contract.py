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


def test_phase01_manifest_does_not_promote_blocked_measurement() -> None:
    verifier = _load_verifier()
    manifest = verifier.load_manifest()

    assert manifest["measurement_status"] == "baseline_frozen_not_measured"
    assert manifest["phase01_closure"]["benchmark_measured"] is False
    assert manifest["phase01_closure"]["quality_gate_changed"] is False
    assert manifest["benchmark_truth_source"]["status"].endswith("measurement_not_run_in_PHASE01")

    sample_80 = manifest["sample_case_sets"]["sample_80"]
    assert sample_80["status"] == "blocked"
    assert sample_80["case_ids"] == []
    assert "blocked_reason" in sample_80


def test_phase01_sample_8_covers_tracked_regression_dataset() -> None:
    verifier = _load_verifier()
    manifest = verifier.load_manifest()
    sample_8 = manifest["sample_case_sets"]["sample_8"]

    assert sample_8["dataset_path"] == "tools/evals/zuno/rag_eval/datasets/mixed_realistic_v1_eval.jsonl"
    assert len(sample_8["case_ids"]) == 8
    for expected in [
        "exact_lookup",
        "semantic_fact",
        "cross_doc_summary",
        "graph_relation",
        "citation_required",
    ]:
        assert expected in sample_8["coverage"]
