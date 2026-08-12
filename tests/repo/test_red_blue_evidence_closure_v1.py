from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_verifier():
    path = REPO_ROOT / "tools/scripts/verify_red_blue_evidence_closure_v1.py"
    spec = importlib.util.spec_from_file_location("verify_red_blue_evidence_closure_v1", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_evidence_closure_campaign_is_complete_and_open() -> None:
    verifier = _load_verifier()
    session = REPO_ROOT / "project-reconstruction-lab/sessions/RB-EVIDENCE-CLOSURE-001"
    assert verifier.verify_session(session) == []
