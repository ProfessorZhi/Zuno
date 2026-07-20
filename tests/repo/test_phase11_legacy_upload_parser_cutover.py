from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase11_legacy_upload_parser_cutover.py"
INVENTORY = REPO_ROOT / ".agent/programs/work-products/phase11-legacy-upload-parser-cutover-inventory.md"


def _load_verifier():
    spec = spec_from_file_location("verify_phase11_legacy_upload_parser_cutover", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_phase11_legacy_cutover_inventory_is_machine_verifiable() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase11_legacy_upload_parser_cutover() == []


def test_phase11_legacy_cutover_inventory_keeps_reopen_boundary() -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    assert "status: active_reopen_guard" in text
    assert "PHASE11 仍为 `in_progress`" in text
    assert "legacy_active_default" in text
    assert "不得作为 PHASE11 完成证据" in text
