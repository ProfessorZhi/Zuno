from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_red_blue_round006_closure.py"
ROUND = ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-ROUND-006"


def _module():
    spec = importlib.util.spec_from_file_location("verify_red_blue_round006_closure", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_round006_closure_semantics_pass():
    assert _module().verify_closure(ROUND) == []


def test_round006_architecture_blocker_label_is_rejected(tmp_path: Path):
    import shutil

    directory = tmp_path / "round006"
    shutil.copytree(ROUND, directory)
    manifest_path = directory / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["architecture_blocker"] = "ARCHITECTURE_BLOCKER"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = _module().verify_closure(directory)
    assert any("architecture_blocker must be NONE_ESTABLISHED" in error for error in errors)
