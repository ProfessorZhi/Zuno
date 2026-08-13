"""Repository test for the immutable Round-005 record contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/scripts/verify_red_blue_round_v313.py"
SPEC = importlib.util.spec_from_file_location("verify_red_blue_round_v313", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_round_005_has_exact_100_question_chain_and_audit():
    assert MODULE.verify() == []
