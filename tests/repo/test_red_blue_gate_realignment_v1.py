from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_gate_realignment_record_is_complete_and_user_gated() -> None:
    path = REPO_ROOT / "tools/scripts/verify_red_blue_gate_realignment_v1.py"
    spec = importlib.util.spec_from_file_location("verify_red_blue_gate_realignment_v1", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    session = REPO_ROOT / "project-reconstruction-lab/sessions/RB-GATE-REALIGNMENT-001"
    assert module.verify_session(session) == []
