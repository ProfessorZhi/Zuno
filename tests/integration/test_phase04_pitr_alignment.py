from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[2]
    verifier_path = repo_root / "tools" / "scripts" / "verify_phase04_pitr_alignment.py"
    spec = spec_from_file_location("verify_phase04_pitr_alignment", verifier_path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase04_pitr_alignment_verifier() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase04_pitr_alignment() == []
