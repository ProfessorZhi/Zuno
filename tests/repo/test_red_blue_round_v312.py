from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load():
    path = ROOT / "tools/scripts/verify_red_blue_round_v312.py"
    spec = importlib.util.spec_from_file_location("verify_red_blue_round_v312", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_round_004_contract_is_closed():
    assert _load().verify() == []
