from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools" / "scripts" / "verify_red_blue_round_v2.py"
SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-WORKFLOW-V2-001"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_red_blue_round_v2", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_round_001_has_exact_v2_contract() -> None:
    verifier = _load_verifier()
    assert verifier.verify_round(SESSION) == []
