from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_complete_contract_adoption.py"


def _load_verifier():
    spec = spec_from_file_location("verify_complete_contract_adoption", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_complete_contract_adoption_verifier_passes() -> None:
    verifier = _load_verifier()
    assert verifier.verify_complete_contract_adoption() == []


def test_contract_adoption_covers_all_canonical_modules() -> None:
    verifier = _load_verifier()
    contracts = verifier.importlib.import_module("zuno.platform.contracts")
    manifest = contracts.build_wave1_contract_registry().manifest()
    adopted = set()
    for entry in manifest.entries:
        adopted.update(verifier._expand_module(entry.owner_module))
        for producer in entry.producer_modules:
            adopted.update(verifier._expand_module(producer))
        for consumer in entry.consumer_modules:
            adopted.update(verifier._expand_module(consumer))
    assert verifier.CANONICAL_MODULES <= adopted
