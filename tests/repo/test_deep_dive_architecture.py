from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load():
    path = REPO_ROOT / "tools/scripts/verify_deep_dive_architecture.py"
    spec = importlib.util.spec_from_file_location("verify_deep_dive_architecture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_four_interview_domains_share_the_unified_target_case() -> None:
    assert _load().verify() == []
