import asyncio
import importlib.util
from pathlib import Path


def test_contract_eval_runner_uses_project_assets_without_domain_pack_loader(monkeypatch):
    from zuno.services.domain_pack.loader import DomainPackLoader

    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "tools/evals/zuno/contract_review_eval/run_contract_eval.py"
    spec = importlib.util.spec_from_file_location("contract_eval_project_assets", script)
    assert spec and spec.loader
    run_contract_eval = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_contract_eval)

    def fail_if_loaded(*_args, **_kwargs):
        raise AssertionError("contract eval must load GraphRAG Project assets")

    monkeypatch.setattr(DomainPackLoader, "load", fail_if_loaded)

    payload = asyncio.run(
        run_contract_eval.run("dev_offline", trace_langsmith=False)
    )

    assert payload["status"] == "ok"
    assert payload["asset_source"] == "graphrag_project"
    assert payload["dataset_source"] == "graphrag_project"
    assert payload["graphrag_project_id"] == "contract_review"
    assert payload["results"][0]["id"] == "contract_demo_q1"
    assert payload["results"][0]["path_count"] >= 1


def test_contract_eval_runner_does_not_use_domain_qa_graph():
    repo_root = Path(__file__).resolve().parents[1]
    source = (
        repo_root / "tools/evals/zuno/contract_review_eval/run_contract_eval.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.core.graphs.domain_qa_graph import DomainQAGraph" not in source
    assert "DomainQAGraph(" not in source
