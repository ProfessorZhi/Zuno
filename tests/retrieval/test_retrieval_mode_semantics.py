import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


from tools.evals.zuno.multihop_eval.run_real_runtime_eval import resolve_eval_mode_metadata


def test_standard_retrieval_is_a_public_product_mode():
    payload = resolve_eval_mode_metadata("standard_retrieval")

    assert payload["requested_mode"] == "standard_retrieval"
    assert payload["normalized_mode"] == "standard_retrieval"
    assert payload["runtime_mode"] == "rag"
    assert payload["product_mode"] == "standard_retrieval"
    assert payload["is_product_mode"] is True
    assert payload["is_deprecated_alias"] is False
    assert payload["is_ablation_mode"] is False


def test_enhanced_retrieval_is_a_public_product_mode():
    payload = resolve_eval_mode_metadata("enhanced_retrieval")

    assert payload["requested_mode"] == "enhanced_retrieval"
    assert payload["normalized_mode"] == "enhanced_retrieval"
    assert payload["runtime_mode"] == "rag_graph_deep"
    assert payload["product_mode"] == "enhanced_retrieval"
    assert payload["is_product_mode"] is True
    assert payload["is_deprecated_alias"] is False
    assert payload["is_ablation_mode"] is False


def test_normal_mode_is_phase04_product_alias_for_standard_runtime():
    payload = resolve_eval_mode_metadata("normal")

    assert payload["requested_mode"] == "normal"
    assert payload["normalized_mode"] == "normal"
    assert payload["runtime_mode"] == "rag"
    assert payload["product_mode"] == "normal"
    assert payload["legacy_product_mode"] == "standard_retrieval"
    assert payload["is_product_mode"] is True
    assert payload["default_query_method"] == "basic"


def test_enhanced_mode_is_phase04_product_alias_for_graph_runtime():
    payload = resolve_eval_mode_metadata("enhanced")

    assert payload["requested_mode"] == "enhanced"
    assert payload["normalized_mode"] == "enhanced"
    assert payload["runtime_mode"] == "rag_graph_deep"
    assert payload["product_mode"] == "enhanced"
    assert payload["legacy_product_mode"] == "enhanced_retrieval"
    assert payload["is_product_mode"] is True
    assert payload["default_query_method"] == "auto"


def test_auto_mode_is_router_product_mode_not_query_method():
    payload = resolve_eval_mode_metadata("auto")

    assert payload["requested_mode"] == "auto"
    assert payload["normalized_mode"] == "auto"
    assert payload["runtime_mode"] == "auto"
    assert payload["product_mode"] == "auto"
    assert payload["is_product_mode"] is True
    assert payload["default_query_method"] == "auto"
    assert payload["is_router_mode"] is True


def test_baseline_rag_stays_compatible_but_is_marked_deprecated():
    payload = resolve_eval_mode_metadata("baseline_rag")

    assert payload["normalized_mode"] == "baseline_rag"
    assert payload["runtime_mode"] == "rag"
    assert payload["product_mode"] == "standard_retrieval"
    assert payload["is_product_mode"] is False
    assert payload["is_deprecated_alias"] is True
    assert payload["is_ablation_mode"] is False
    assert "deprecated" in payload["warning"].lower()


def test_graph_modes_are_marked_as_internal_ablations():
    local_payload = resolve_eval_mode_metadata("local_graphrag")
    deep_payload = resolve_eval_mode_metadata("deep_graphrag")

    assert local_payload["product_mode"] == "enhanced_retrieval"
    assert local_payload["is_product_mode"] is False
    assert local_payload["is_deprecated_alias"] is False
    assert local_payload["is_ablation_mode"] is True

    assert deep_payload["product_mode"] == "enhanced_retrieval"
    assert deep_payload["is_product_mode"] is False
    assert deep_payload["is_deprecated_alias"] is False
    assert deep_payload["is_ablation_mode"] is True
