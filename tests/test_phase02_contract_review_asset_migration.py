from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = REPO_ROOT / "examples" / "graphrag-projects" / "contract_review"


def test_contract_review_assets_have_target_graphrag_project_copy() -> None:
    expected_paths = [
        "settings.yaml",
        "schema.json",
        "retrieval_policy.yaml",
        "prompts/extract_graph.md",
        "prompts/local_query.md",
        "prompts/report_template.md",
        "eval/eval_dataset.jsonl",
    ]

    for relative_path in expected_paths:
        assert (PROJECT_ROOT / relative_path).is_file(), f"missing target asset: {relative_path}"


def test_contract_review_example_project_loads_with_prompt_manifest() -> None:
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader

    loaded = GraphRAGProjectLoader(projects_root=PROJECT_ROOT.parent).load("contract_review")

    assert loaded is not None
    assert loaded.contract.graphrag_project_id == "contract_review"
    assert loaded.contract.status == "ready"
    assert loaded.contract.query_method == "local"
    assert loaded.readiness.ready is True
    assert set(loaded.prompt_texts) == {"extract_graph", "local_query", "report_template"}
    assert loaded.settings["retrieval_policy"]["graph_hop_limit"] == 2
    assert loaded.settings["retrieval_policy"]["risk_relation_preference"] == "CLAUSE_HAS_RISK"
    assert "Contract" in loaded.schema_data["entities"]
    assert loaded.retrieval_policy_data["graph_hop_limit"] == 2
    assert "contract_demo_q1" in loaded.eval_dataset_text
    assert loaded.eval_dataset_rows[0]["id"] == "contract_demo_q1"


def test_contract_review_domain_pack_assets_are_mapped_to_project_assets() -> None:
    settings = yaml.safe_load((PROJECT_ROOT / "settings.yaml").read_text(encoding="utf-8"))
    source_pack = yaml.safe_load(
        (REPO_ROOT / "domain-packs" / "contract_review" / "pack.yaml").read_text(encoding="utf-8")
    )

    assert settings["source_domain_pack"]["id"] == source_pack["id"]
    assert settings["schema_path"] == "schema.json"
    assert settings["retrieval_policy_path"] == "retrieval_policy.yaml"
    assert settings["eval_dataset_path"] == "eval/eval_dataset.jsonl"
    assert settings["prompts"]["extract_graph"] == "prompts/extract_graph.md"
    assert settings["prompts"]["local_query"] == "prompts/local_query.md"
    assert settings["prompts"]["report_template"] == "prompts/report_template.md"
