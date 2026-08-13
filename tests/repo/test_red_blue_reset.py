from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_red_blue_reset.py"


def _module():
    spec = importlib.util.spec_from_file_location("verify_red_blue_reset", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_red_blue_workspace_is_reset():
    assert _module().verify() == []


def test_round_007_has_not_started():
    status = (ROOT / "project-reconstruction-lab/05-red-blue/workflow-status.md").read_text(encoding="utf-8")
    assert "ACTIVE_PROTOCOL: NONE" in status
    assert "ROUND_007: CANCELLED_BEFORE_START" in status
    assert "FINAL_MODULE_COUNT: NOT_DECIDED" in status


def test_historical_protocols_are_not_active_sources():
    root = ROOT / "project-reconstruction-lab/05-red-blue"
    for path in root.glob("round-protocol-*.md"):
        assert path.read_text(encoding="utf-8").startswith("# Historical compatibility pointer")
