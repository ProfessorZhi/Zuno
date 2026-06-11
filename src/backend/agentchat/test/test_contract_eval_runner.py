import json
import subprocess
import sys
from pathlib import Path


def test_contract_eval_runner_offline():
    script = Path(__file__).resolve().parents[1] / "evals" / "contract_review_eval" / "run_contract_eval.py"
    output_dir = Path(__file__).resolve().parents[1] / "evals" / "contract_review_eval" / ".tmp_test_reports"
    if output_dir.exists():
        for path in output_dir.glob("*"):
            path.unlink()
    completed = subprocess.run(
        [sys.executable, str(script), "--profile", "dev_offline", "--output-dir", str(output_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout.strip())
    assert payload["profile"] == "dev_offline"
    assert payload["status"] == "ok"
    assert payload["report_count"] == payload["sample_count"]
    assert payload["profile_settings"]["extraction_mode"] == "fixture"
    assert output_dir.joinpath("contract_001_q1.report.md").exists()


def test_contract_eval_runner_demo_uses_real_extraction():
    script = Path(__file__).resolve().parents[1] / "evals" / "contract_review_eval" / "run_contract_eval.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--profile", "demo"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout.strip())
    assert payload["profile"] == "demo"
    assert payload["status"] == "ok"
    assert payload["profile_settings"]["extraction_mode"] == "structured"
    assert payload["trace_langsmith"] is True
    assert payload["results"][0]["path_count"] >= 1
    assert payload["results"][0]["trace_node_count"] >= 4


def test_contract_eval_runner_can_compare_profiles():
    script = Path(__file__).resolve().parents[1] / "evals" / "contract_review_eval" / "run_contract_eval.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--profiles", "dev_offline,dev_local,demo"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout.strip())
    assert payload["status"] == "ok"
    assert payload["profile_order"] == ["dev_offline", "dev_local", "demo"]
    assert payload["profiles"]["dev_offline"]["profile_settings"]["extraction_mode"] == "fixture"
    assert payload["profiles"]["dev_local"]["profile_settings"]["extraction_mode"] == "structured"
    assert payload["profiles"]["demo"]["trace_langsmith"] is True
