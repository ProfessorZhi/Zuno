from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_verifier():
    path = REPO_ROOT / "tools/scripts/verify_markdown_internal_links.py"
    spec = importlib.util.spec_from_file_location("verify_markdown_internal_links_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_tracked_markdown_internal_links_are_resolvable() -> None:
    assert _load_verifier().verify() == []
