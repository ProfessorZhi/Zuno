from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load():
    path = REPO_ROOT / "tools/scripts/verify_architecture_interview_qa.py"
    spec = importlib.util.spec_from_file_location("verify_architecture_interview_qa", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_architecture_interview_corpus_is_structurally_complete() -> None:
    assert _load().verify() == []
