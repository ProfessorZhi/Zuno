from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from zuno.evals.rag_eval.run_eval import PROFILE_SETTINGS, resolve_profiles


def test_public_eval_profiles_expose_phase5_compare_surface():
    assert "baseline_rag" in PROFILE_SETTINGS
    assert "local_graphrag" in PROFILE_SETTINGS
    assert "deep_graphrag" in PROFILE_SETTINGS


def test_public_eval_profile_set_resolves_to_phase5_compare_surface():
    assert resolve_profiles(profile_set="deep_graphrag_compare") == [
        "baseline_rag",
        "local_graphrag",
        "deep_graphrag",
    ]
