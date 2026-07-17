from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_migration_control.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase04_migration_control", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_lock_and_durable_backfill_control_on_real_postgres() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase04_migration_control() == []
