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


def test_legacy_design_material_is_not_canonical() -> None:
    assert (REPO_ROOT / "docs/modules/README.md").exists()
    assert not (REPO_ROOT / "docs/history/superseded-document-taxonomy").exists()
    assert (REPO_ROOT / "docs/history/red-blue/README.md").exists()
    assert (REPO_ROOT / "docs/architecture/architecture.md").exists()
    assert (REPO_ROOT / "docs/architecture/architecture.html").exists()


def test_agent_architecture_and_module_mirrors_are_absent() -> None:
    assert not (REPO_ROOT / ".agent/architecture").exists()
    assert not (REPO_ROOT / ".agent/modules").exists()
