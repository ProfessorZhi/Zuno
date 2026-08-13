from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_normalization_structure_is_canonical() -> None:
    verifier = _load("verify_document_normalization_v311", "tools/scripts/verify_document_normalization_v311.py")
    assert verifier.verify() == []


def test_quality_gate_uses_normalization_and_strict_part_a_threshold() -> None:
    verifier = _load("verify_document_quality_v31", "tools/scripts/verify_document_quality_v31.py")
    assert verifier.verify_quality(ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-003") == []
