from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load():
    path = REPO_ROOT / "tools/scripts/verify_architecture_document_set.py"
    spec = importlib.util.spec_from_file_location("verify_architecture_document_set", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_architecture_document_set_is_canonical() -> None:
    assert _load().verify() == []


def test_formal_design_count_is_eleven_plus_two() -> None:
    module_docs = sorted((REPO_ROOT / "docs/modules").glob("[0-9][0-9]-*.md"))
    assert len(module_docs) == 11
    assert (REPO_ROOT / "docs/architecture/architecture.md").exists()
    assert (REPO_ROOT / "docs/architecture/architecture.html").exists()


def test_all_module_mirrors_match() -> None:
    for formal in (REPO_ROOT / "docs/modules").glob("[0-9][0-9]-*.md"):
        mirror = REPO_ROOT / ".agent/modules" / formal.name
        assert formal.read_bytes() == mirror.read_bytes()
