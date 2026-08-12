from pathlib import Path

from tools.scripts.verify_canonical_diff_v3 import verify_canonical_diff
from tools.scripts.verify_red_blue_round_v3 import verify_round
from tools.scripts.verify_red_blue_score_v3 import verify_score


ROOT = Path(__file__).resolve().parents[2]
SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-WORKFLOW-V3-ROUND-002"


def test_v3_round_contract_is_complete() -> None:
    assert verify_round(SESSION) == []


def test_v3_scorecard_is_recomputed() -> None:
    assert verify_score(SESSION) == []


def test_v3_canonical_diff_is_traceable() -> None:
    assert verify_canonical_diff(SESSION) == []
