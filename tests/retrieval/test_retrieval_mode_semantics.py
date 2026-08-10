import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


from tools.evals.zuno.multihop_eval.run_real_runtime_eval import resolve_eval_mode_metadata


def test_normal_mode_uses_canonical_vector_runtime():
    payload = resolve_eval_mode_metadata("normal")

    assert payload["requested_mode"] == "normal"
    assert payload["normalized_mode"] == "normal"
    assert payload["runtime_mode"] == "rag"
    assert payload["product_mode"] == "normal"
    assert payload["is_product_mode"] is True
    assert payload["default_query_method"] == "basic"


def test_enhanced_mode_uses_canonical_graph_runtime():
    payload = resolve_eval_mode_metadata("enhanced")

    assert payload["requested_mode"] == "enhanced"
    assert payload["normalized_mode"] == "enhanced"
    assert payload["runtime_mode"] == "rag_graph_deep"
    assert payload["product_mode"] == "enhanced"
    assert payload["is_product_mode"] is True
    assert payload["default_query_method"] == "auto"


def test_auto_mode_is_the_only_router_mode():
    payload = resolve_eval_mode_metadata("auto")

    assert payload["requested_mode"] == "auto"
    assert payload["normalized_mode"] == "auto"
    assert payload["runtime_mode"] == "auto"
    assert payload["product_mode"] == "auto"
    assert payload["is_product_mode"] is True
    assert payload["default_query_method"] == "auto"
    assert payload["is_router_mode"] is True


def test_retired_mode_names_are_rejected():
    for mode in ("standard_retrieval", "enhanced_retrieval", "baseline_rag", "local_graphrag"):
        try:
            resolve_eval_mode_metadata(mode)
        except ValueError:
            continue
        raise AssertionError(f"retired mode was accepted: {mode}")
