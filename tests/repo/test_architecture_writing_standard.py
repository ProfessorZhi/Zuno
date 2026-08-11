from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_architecture_writing_standard.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_architecture_writing_standard", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_architecture_writing_standard_is_consistent() -> None:
    assert _load_verifier().verify() == []
