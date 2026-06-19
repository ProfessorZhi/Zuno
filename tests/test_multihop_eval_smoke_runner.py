import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

SAMPLE_ROOT = REPO_ROOT / "tools" / "evals" / "zuno" / "multihop_eval" / "sample_data"


def test_multihop_runner_supports_three_public_modes_and_writes_compare_matrix(tmp_path):
    from tools.evals.zuno.multihop_eval.run_multihop_eval import run_multihop_eval

    output_root = tmp_path / "reports"
    input_path = SAMPLE_ROOT / "hotpotqa_sample.jsonl"

    baseline = run_multihop_eval(
        dataset="hotpotqa",
        mode="baseline_rag",
        split="dev",
        limit=10,
        input_path=input_path,
        output_root=output_root,
    )
    local = run_multihop_eval(
        dataset="hotpotqa",
        mode="local_graphrag",
        split="dev",
        limit=10,
        input_path=input_path,
        output_root=output_root,
    )
    deep = run_multihop_eval(
        dataset="hotpotqa",
        mode="deep_graphrag",
        split="dev",
        limit=10,
        input_path=input_path,
        output_root=output_root,
    )

    assert baseline["execution_mode"] == "mocked"
    assert local["mode"] == "local_graphrag"
    assert deep["mode"] == "deep_graphrag"

    for result in [baseline, local, deep]:
        assert Path(result["report_path"]).exists()
        assert "Recall@5" in result["metrics"]
        assert "Supporting Evidence Recall" in result["metrics"]

    compare_matrix = output_root / "compare_matrix.json"
    assert compare_matrix.exists()
    payload = json.loads(compare_matrix.read_text(encoding="utf-8"))
    assert payload["dataset"] == "hotpotqa"
    assert set(payload["modes"]) >= {"baseline_rag", "local_graphrag", "deep_graphrag"}
    assert payload["execution_mode"] == "mocked"


def test_multihop_runner_reads_default_sample_input_when_path_is_omitted(tmp_path):
    from tools.evals.zuno.multihop_eval.run_multihop_eval import resolve_input_path

    path = resolve_input_path(dataset="twowiki", split="dev", input_path=None)
    assert path.name == "twowiki_sample.jsonl"
    assert path.exists()


def test_multihop_runner_rejects_unknown_mode():
    from tools.evals.zuno.multihop_eval.run_multihop_eval import run_multihop_eval

    try:
        run_multihop_eval(
            dataset="hotpotqa",
            mode="unknown_mode",
            split="dev",
            limit=10,
            input_path=SAMPLE_ROOT / "hotpotqa_sample.jsonl",
            output_root=Path(".test-tmp") / "multihop-invalid",
        )
    except ValueError as error:
        assert "Unsupported mode" in str(error)
    else:
        raise AssertionError("unknown mode should be rejected")

