from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase02_compatibility_boundaries.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase02_compatibility_boundaries", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase02_compatibility_artifacts_are_machine_verifiable() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase02_compatibility_boundaries() == []


def test_temporary_allowlist_covers_phase01_bypass_inventory() -> None:
    verifier = _load_verifier()
    p01 = (verifier.WORK_PRODUCTS / "legacy-bypass-inventory.yaml").read_text(encoding="utf-8")
    p02 = (verifier.WORK_PRODUCTS / "temporary-allowlist.yaml").read_text(encoding="utf-8")
    assert verifier._path_values(p01) <= verifier._path_values(p02)


def test_feature_flags_cannot_be_domain_fact_owner() -> None:
    flags = (REPO_ROOT / ".agent/programs/work-products/feature-flag-registry.yaml").read_text(
        encoding="utf-8"
    )
    assert "domain_fact_owner: \"feature_flag\"" not in flags
    assert "retire_task: \"P22-T03\"" in flags
