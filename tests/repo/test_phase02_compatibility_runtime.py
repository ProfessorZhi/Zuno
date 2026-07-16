from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME = REPO_ROOT / "tools" / "scripts" / "phase02_compatibility_runtime.py"


def _load_runtime():
    spec = spec_from_file_location("phase02_compatibility_runtime", RUNTIME)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase02_executable_runtime_controls_pass() -> None:
    runtime = _load_runtime()
    assert runtime.verify_phase02_runtime_controls() == []


def test_feature_flag_state_machine_rejects_illegal_jump() -> None:
    runtime = _load_runtime()
    registry = (
        REPO_ROOT / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
    ).read_text(encoding="utf-8")
    state_machine = runtime.FeatureFlagStateMachine(registry)
    with pytest.raises(ValueError):
        state_machine.decide_transition("product_api_v1_adapter", "DEFAULT_NEW")


def test_temporary_allowlist_guard_fails_new_bypass_by_default() -> None:
    runtime = _load_runtime()
    allowlist = (
        REPO_ROOT / ".agent" / "programs" / "work-products" / "temporary-allowlist.yaml"
    ).read_text(encoding="utf-8")
    legacy = (
        REPO_ROOT / ".agent" / "programs" / "work-products" / "legacy-bypass-inventory.yaml"
    ).read_text(encoding="utf-8")
    guard = runtime.TemporaryAllowlistGuard(allowlist, legacy)
    with pytest.raises(PermissionError):
        guard.assert_allowed("src/backend/zuno/new_unregistered_bypass.py")


def test_data_cutover_controller_produces_stable_owner_hashes() -> None:
    runtime = _load_runtime()
    matrix = (
        REPO_ROOT / ".agent" / "programs" / "work-products" / "data-cutover-matrix.yaml"
    ).read_text(encoding="utf-8")
    hashes = runtime.DataCutoverController(matrix).dry_run_hashes()
    assert len(hashes) >= 6
    assert "06 Agent Core" in hashes
    assert all(len(value) == 64 for value in hashes.values())
