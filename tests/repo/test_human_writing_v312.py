from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load():
    path = ROOT / "tools/scripts/verify_human_writing_v312.py"
    spec = importlib.util.spec_from_file_location("verify_human_writing_v312", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_human_writing_audit_has_no_structural_errors():
    errors, _warnings, rows = _load().verify()
    assert errors == []
    assert len(rows) == 12
