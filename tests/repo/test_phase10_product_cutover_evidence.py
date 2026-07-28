from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase10_product_cutover_evidence.py"


def test_phase10_product_cutover_evidence_is_machine_verifiable() -> None:
    spec = spec_from_file_location("verify_phase10_product_cutover_evidence", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.verify_phase10_product_cutover_evidence() == []
