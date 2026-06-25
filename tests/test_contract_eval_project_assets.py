import asyncio
import importlib
import importlib.util
from pathlib import Path

import pytest


def test_contract_eval_runner_uses_project_assets_without_domain_pack_loader():
    repo_root = Path(__file__).resolve().parents[1]
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.services.domain_pack.loader")

    script = repo_root / "tools/evals/zuno/contract_review_eval/run_contract_eval.py"
    spec = importlib.util.spec_from_file_location("contract_eval_project_assets", script)
    assert spec and spec.loader
    run_contract_eval = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_contract_eval)

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


def test_contract_eval_internal_payload_names_follow_project_mainline():
    repo_root = Path(__file__).resolve().parents[1]
    source = (
        repo_root / "tools/evals/zuno/contract_review_eval/run_contract_eval.py"
    ).read_text(encoding="utf-8")

    assert "project_payload: dict[str, Any]" in source
    assert "sample_project_payload = dict(project_payload)" in source
    assert "domain_pack=project_payload" in source
    assert "domain_pack: dict[str, Any]" not in source
    assert "domain_pack = dict(project_payload)" not in source
    assert '"domain_pack_id"' in source
