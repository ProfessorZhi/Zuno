from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, relative: str):
    path = REPO_ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_v31_round_contract() -> None:
    verifier = _load("verify_red_blue_round_v31", "tools/scripts/verify_red_blue_round_v31.py")
    errors = verifier.verify_round(REPO_ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-003")
    assert errors == []


def test_v31_document_quality_gate() -> None:
    verifier = _load("verify_document_quality_v31", "tools/scripts/verify_document_quality_v31.py")
    errors = verifier.verify_quality(REPO_ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-003")
    assert errors == []
