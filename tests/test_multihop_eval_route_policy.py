import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_route_policy_defaults_to_auto():
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import resolve_route_policy

    assert resolve_route_policy(None) == "auto"
    assert resolve_route_policy("") == "auto"
    assert resolve_route_policy("auto") == "auto"


def test_route_policy_accepts_force_graph_and_force_deep():
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import resolve_route_policy

    assert resolve_route_policy("force_graph") == "force_graph"
    assert resolve_route_policy("force_deep") == "force_deep"


def test_route_policy_rejects_unsupported_values():
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import resolve_route_policy

    with pytest.raises(ValueError, match="Unsupported route policy"):
        resolve_route_policy("force_everything")


def test_runtime_retrieval_options_mark_eval_only_force_graph():
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import build_runtime_retrieval_options

    options = build_runtime_retrieval_options(
        top_k=5,
        profile_name="retrieval_only_text_multihop",
        route_policy="force_graph",
    )

    assert options["top_k"] == 5
    assert options["requested_profile"] == "retrieval_only_text_multihop"
    assert options["route_policy"] == "force_graph"
    assert options["eval_only_route_override"] == "force_graph"
    assert options["trace_policy"]["enabled"] is True
